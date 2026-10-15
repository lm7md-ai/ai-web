"""Neural Civilization - a self-contained multi-agent society simulation.

Standard library only, so it can be copied into the execution sandbox.  The
learner writes ``program(society)`` and controls a population of agents that
gather resources, share them and try to keep everybody alive.  Deterministic
by seed: the same policy and seed always produce the same trace.

Learner contract::

    def program(society):
        def policy(s):
            for agent in s.agents():
                if agent.energy < 30 and agent.store().get("food", 0) > 0:
                    agent.eat(1)
                else:
                    node = s.nearest_node(agent, "food")
                    if node:
                        agent.move_to(node.x, node.y)
                        agent.gather(node)
        society.on_tick(policy)
        society.run()
"""

from __future__ import annotations

import random
from typing import Any, Callable


class SimulationStopped(Exception):
    pass


class Event:
    __slots__ = ("tick", "type", "payload", "actor")

    def __init__(self, tick: int, type_: str, payload: dict | None = None, actor: str = "") -> None:
        self.tick = tick
        self.type = type_
        self.payload = payload or {}
        self.actor = actor

    def to_dict(self) -> dict:
        return {"tick": self.tick, "type": self.type, "actor": self.actor, **self.payload}


class Node:
    def __init__(self, spec: dict, index: int) -> None:
        self.index = index
        self.x = int(spec.get("x", 0))
        self.y = int(spec.get("y", 0))
        self.item = str(spec.get("item", "food"))
        self.amount = int(spec.get("amount", 20))
        self.initial = self.amount
        self.regen = float(spec.get("regen", 0.0))

    def to_dict(self) -> dict:
        return {"index": self.index, "x": self.x, "y": self.y, "item": self.item, "amount": self.amount}


class Agent:
    def __init__(self, spec: dict) -> None:
        self.name = str(spec.get("name", "a1"))
        self.x = int(spec.get("x", 0))
        self.y = int(spec.get("y", 0))
        self.energy = float(spec.get("energy", 100))
        self.store: dict[str, int] = dict(spec.get("store", {}))
        self.gathered: dict[str, int] = {}
        self.alive = True
        self.idle_ticks = 0
        self.acted_this_tick = False

    def gathered_total(self) -> int:
        return sum(self.gathered.values())

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "energy": round(self.energy, 2),
            "store": dict(self.store),
            "gathered": dict(self.gathered),
            "alive": self.alive,
            "idle_ticks": self.idle_ticks,
        }


class Society:
    def __init__(self, config: dict) -> None:
        cfg = dict(config or {})
        self.width = int(cfg.get("width", 12))
        self.height = int(cfg.get("height", 10))
        self.max_ticks = int(cfg.get("max_ticks", 120))
        self.energy_per_tick = float(cfg.get("energy_per_tick", 1.0))
        self.energy_per_move = float(cfg.get("energy_per_move", 0.5))
        self.energy_per_food = float(cfg.get("energy_per_food", 25.0))
        self.gather_rate = int(cfg.get("gather_rate", 2))
        self.tick = 0
        self.events: list[Event] = []
        self.nodes = [Node(spec, i) for i, spec in enumerate(cfg.get("nodes", []))]
        self.agents: dict[str, Agent] = {}
        for spec in cfg.get("agents", [{"name": "a1"}]):
            agent = Agent(spec)
            self.agents[agent.name] = agent
        self.treasury: dict[str, int] = {}
        self.handlers: list[Callable[[Any], None]] = []
        self.objectives = cfg.get("objectives", [])
        self.stop_reason: str | None = None
        self.rng = random.Random(cfg.get("seed", 3))

    # ---------------------------------------------------------------- utils
    def log(self, type_: str, actor: str = "", **payload) -> None:
        self.events.append(Event(self.tick, type_, payload, actor))

    def agent(self, name: str) -> Agent:
        if name not in self.agents:
            raise KeyError(f"unknown agent {name!r}; available: {sorted(self.agents)}")
        return self.agents[name]

    def nearest_node(self, agent: Agent, item: str | None = None) -> Node | None:
        candidates = [n for n in self.nodes if n.amount > 0 and (item is None or n.item == item)]
        if not candidates:
            return None
        return min(candidates, key=lambda n: abs(n.x - agent.x) + abs(n.y - agent.y))

    def node_at(self, x: int, y: int) -> Node | None:
        for node in self.nodes:
            if node.x == x and node.y == y:
                return node
        return None

    # -------------------------------------------------------------- actions
    def move_towards(self, agent: Agent, x: int, y: int, max_steps: int = 4) -> int:
        steps = 0
        while (agent.x, agent.y) != (x, y) and steps < max_steps:
            dx = x - agent.x
            dy = y - agent.y
            if abs(dx) >= abs(dy):
                agent.x += 1 if dx > 0 else -1
            else:
                agent.y += 1 if dy > 0 else -1
            agent.energy -= self.energy_per_move
            steps += 1
            agent.acted_this_tick = True
            self.log("move", agent.name, x=agent.x, y=agent.y, energy=round(agent.energy, 1))
            if agent.energy <= 0:
                self._kill(agent)
                return steps
        return steps

    def gather(self, agent: Agent, node: Node, qty: int | None = None) -> int:
        if node.amount <= 0:
            self.log("gather_failed", agent.name, reason="empty node", node=node.index)
            return 0
        if (agent.x, agent.y) != (node.x, node.y):
            self.log("gather_failed", agent.name, reason="not at node", node=node.index)
            return 0
        amount = min(self.gather_rate if qty is None else int(qty), node.amount)
        node.amount -= amount
        agent.store[node.item] = agent.store.get(node.item, 0) + amount
        agent.gathered[node.item] = agent.gathered.get(node.item, 0) + amount
        self.treasury[node.item] = self.treasury.get(node.item, 0) + amount
        agent.acted_this_tick = True
        self.log("gather", agent.name, item=node.item, qty=amount, node=node.index)
        return amount

    def share(self, agent: Agent, other: Agent, item: str, qty: int) -> int:
        have = agent.store.get(item, 0)
        moved = max(0, min(int(qty), have))
        if moved == 0:
            self.log("share_failed", agent.name, to=other.name, item=item)
            return 0
        agent.store[item] = have - moved
        other.store[item] = other.store.get(item, 0) + moved
        agent.acted_this_tick = True
        self.log("share", agent.name, to=other.name, item=item, qty=moved)
        return moved

    def eat(self, agent: Agent, qty: int = 1) -> int:
        have = agent.store.get("food", 0)
        eaten = max(0, min(int(qty), have))
        if eaten == 0:
            self.log("eat_failed", agent.name, reason="no food")
            return 0
        agent.store["food"] = have - eaten
        agent.energy += self.energy_per_food * eaten
        agent.acted_this_tick = True
        self.log("eat", agent.name, qty=eaten, energy=round(agent.energy, 1))
        return eaten

    def deposit(self, agent: Agent, item: str, qty: int | None = None) -> int:
        have = agent.store.get(item, 0)
        moved = have if qty is None else min(have, int(qty))
        if moved <= 0:
            return 0
        agent.store[item] = have - moved
        self.log("deposit", agent.name, item=item, qty=moved)
        return moved

    def _kill(self, agent: Agent) -> None:
        agent.energy = 0
        agent.alive = False
        self.log("died", agent.name, tick=self.tick)

    # --------------------------------------------------------------- clock
    def on_tick(self, handler: Callable[[Any], None]) -> None:
        if not callable(handler):
            raise TypeError("society.on_tick expects a function taking the society API")
        self.handlers.append(handler)

    def advance(self) -> None:
        for agent in self.agents.values():
            if agent.alive:
                agent.energy -= self.energy_per_tick
                if agent.energy <= 0:
                    self._kill(agent)
        for node in self.nodes:
            if node.regen and node.amount < node.initial:
                node.amount = min(node.initial, int(node.amount + node.regen))
        self.tick += 1
        for agent in self.agents.values():
            if not agent.acted_this_tick and agent.alive:
                agent.idle_ticks += 1
            agent.acted_this_tick = False
        if self.tick >= self.max_ticks:
            self.stop_reason = "tick_limit"
            self.log("tick_limit", tick=self.tick)
            raise SimulationStopped(f"reached the tick limit ({self.max_ticks})")
        if not any(a.alive for a in self.agents.values()):
            self.stop_reason = "population_lost"
            self.log("population_lost", tick=self.tick)
            raise SimulationStopped("every agent ran out of energy")


class AgentAPI:
    def __init__(self, society: Society, agent: Agent, api: "SocietyAPI") -> None:
        self._society = society
        self._agent = agent
        self._api = api

    @property
    def name(self) -> str:
        return self._agent.name

    @property
    def energy(self) -> float:
        return round(self._agent.energy, 2)

    @property
    def alive(self) -> bool:
        return self._agent.alive

    def position(self) -> tuple[int, int]:
        return (self._agent.x, self._agent.y)

    def store(self) -> dict[str, int]:
        return dict(self._agent.store)

    def gathered(self) -> dict[str, int]:
        return dict(self._agent.gathered)

    def move_to(self, x: int, y: int, max_steps: int = 4) -> int:
        return self._society.move_towards(self._agent, int(x), int(y), int(max_steps))

    def move_towards(self, x: int, y: int, max_steps: int = 4) -> int:
        return self._society.move_towards(self._agent, int(x), int(y), int(max_steps))

    def gather(self, node: "NodeAPI | None" = None, qty: int | None = None) -> int:
        target = node._node if isinstance(node, NodeAPI) else self._society.node_at(self._agent.x, self._agent.y)
        if target is None:
            self._society.log("gather_failed", self._agent.name, reason="no node here")
            return 0
        return self._society.gather(self._agent, target, qty)

    def share(self, other: "AgentAPI | str", item: str, qty: int = 1) -> int:
        target = other._agent if isinstance(other, AgentAPI) else self._society.agent(str(other))
        return self._society.share(self._agent, target, item, qty)

    def eat(self, qty: int = 1) -> int:
        return self._society.eat(self._agent, qty)

    def deposit(self, item: str, qty: int | None = None) -> int:
        return self._society.deposit(self._agent, item, qty)

    def __repr__(self) -> str:
        return f"<Agent {self._agent.name} energy={self.energy} store={self._agent.store}>"


class NodeAPI:
    def __init__(self, node: Node) -> None:
        self._node = node

    @property
    def x(self) -> int:
        return self._node.x

    @property
    def y(self) -> int:
        return self._node.y

    @property
    def item(self) -> str:
        return self._node.item

    @property
    def amount(self) -> int:
        return self._node.amount

    def __repr__(self) -> str:
        return f"<Node {self._node.item} ({self._node.x},{self._node.y}) amount={self._node.amount}>"


class SocietyAPI:
    def __init__(self, society: Society) -> None:
        self._society = society

    @property
    def tick(self) -> int:
        return self._society.tick

    def agent(self, name: str) -> AgentAPI:
        return AgentAPI(self._society, self._society.agent(name), self)

    def agents(self) -> list[AgentAPI]:
        return [AgentAPI(self._society, a, self) for a in self._society.agents.values()]

    def alive_agents(self) -> list[AgentAPI]:
        return [a for a in self.agents() if a.alive]

    def nodes(self, item: str | None = None) -> list[NodeAPI]:
        return [
            NodeAPI(n)
            for n in self._society.nodes
            if (item is None or n.item == item) and n.amount > 0
        ]

    def nearest_node(self, agent: AgentAPI, item: str | None = None) -> NodeAPI | None:
        node = self._society.nearest_node(agent._agent, item)
        return NodeAPI(node) if node else None

    def treasury(self) -> dict[str, int]:
        return dict(self._society.treasury)

    def on_tick(self, handler: Callable[[Any], None]) -> None:
        self._society.on_tick(handler)

    def run(self, ticks: int | None = None) -> None:
        """Advance the society until the tick budget is spent.

        Reaching the limit is a normal end condition, not an error, so the
        stop signal is absorbed here and recorded as ``stop_reason``.
        """
        limit = int(ticks) if ticks else self._society.max_ticks
        deadline = self._society.tick + limit
        try:
            while self._society.tick < deadline:
                for handler in list(self._society.handlers):
                    handler(self)
                self._society.advance()
        except SimulationStopped:
            pass
        self._society.stop_reason = self._society.stop_reason or "completed"

    def say(self, message: str) -> None:
        self._society.log("say", "society", message=str(message)[:160])


def gini(values: list[float]) -> float:
    """Gini coefficient: 0 = perfectly equal, 1 = one agent holds everything."""
    positive = [v for v in values if v > 0]
    n = len(positive)
    if n <= 1:
        return 0.0
    ordered = sorted(positive)
    total = sum(ordered)
    if total == 0:
        return 0.0
    cumulative = sum((i + 1) * value for i, value in enumerate(ordered))
    return round((2 * cumulative) / (n * total) - (n + 1) / n, 4)


def build(config: dict) -> tuple[SocietyAPI, Society]:
    society = Society(config)
    society.log("start", tick=0, agents=len(society.agents), nodes=len(society.nodes))
    return SocietyAPI(society), society


def evaluate(society: Society) -> tuple[list[dict], float]:
    results: list[dict] = []
    gathered = [a.gathered_total() for a in society.agents.values()]
    fairness = gini([float(v) for v in gathered])
    alive = sum(1 for a in society.agents.values() if a.alive)
    for objective in society.objectives:
        kind = objective.get("type", "collect")
        if kind == "collect":
            item = objective.get("item", "food")
            needed = int(objective.get("quantity", 1))
            have = society.treasury.get(item, 0)
            results.append({"type": kind, "ok": have >= needed, "detail": f"gathered {have}/{needed} {item}"})
        elif kind == "survive":
            needed = int(objective.get("min_alive", 1))
            results.append({"type": kind, "ok": alive >= needed, "detail": f"alive {alive}/{needed}"})
        elif kind == "fairness":
            limit = float(objective.get("max_gini", 0.5))
            results.append({"type": kind, "ok": fairness <= limit, "detail": f"gini {fairness} <= {limit}"})
        elif kind == "ticks":
            limit = int(objective.get("max", society.max_ticks))
            results.append({"type": kind, "ok": society.tick <= limit, "detail": f"used {society.tick}/{limit}"})
        elif kind == "idle":
            limit = int(objective.get("max", 10 ** 6))
            idle = sum(a.idle_ticks for a in society.agents.values())
            results.append({"type": kind, "ok": idle <= limit, "detail": f"idle ticks {idle}/{limit}"})
        elif kind == "consumption":
            limit = int(objective.get("max_eaten", 10 ** 6))
            eaten = sum(int(e.payload.get("qty", 0)) for e in society.events if e.type == "eat")
            results.append({"type": kind, "ok": eaten <= limit, "detail": f"eaten {eaten}/{limit}"})
        elif kind == "energy":
            floor = float(objective.get("min", 1))
            results.append(
                {
                    "type": kind,
                    "ok": all(a.energy >= floor for a in society.agents.values() if a.alive),
                    "detail": ", ".join(f"{a.name}={round(a.energy,1)}" for a in society.agents.values()),
                }
            )
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    passed = sum(1 for r in results if r["ok"])
    return results, round(passed / len(results), 3) if results else 0.0


def result(api: SocietyAPI, society: Society) -> dict:
    objectives, score = evaluate(society)
    ok = all(o["ok"] for o in objectives)
    if ok or society.stop_reason == "tick_limit":
        society.stop_reason = "completed" if ok else society.stop_reason
    gathered = [float(a.gathered_total()) for a in society.agents.values()]
    return {
        "world": "neural_civilization",
        "ok": ok,
        "score": score,
        "tick": society.tick,
        "stop_reason": society.stop_reason or "completed",
        "agents": {name: a.to_dict() for name, a in society.agents.items()},
        "nodes": [n.to_dict() for n in society.nodes],
        "treasury": dict(society.treasury),
        "objectives": objectives,
        "events": [e.to_dict() for e in society.events][-2000:],
        "metrics": {
            "gini": gini(gathered),
            "alive": sum(1 for a in society.agents.values() if a.alive),
            "idle_ticks": sum(a.idle_ticks for a in society.agents.values()),
            "deaths": sum(1 for e in society.events if e.type == "died"),
            "gather_events": sum(1 for e in society.events if e.type == "gather"),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    import json

    demo = {
        "width": 10,
        "height": 8,
        "agents": [
            {"name": "a1", "x": 0, "y": 0, "energy": 60},
            {"name": "a2", "x": 9, "y": 7, "energy": 60},
        ],
        "nodes": [
            {"x": 3, "y": 2, "item": "food", "amount": 30, "regen": 1},
            {"x": 7, "y": 6, "item": "food", "amount": 30, "regen": 1},
        ],
        "objectives": [
            {"type": "collect", "item": "food", "quantity": 25},
            {"type": "survive", "min_alive": 2},
            {"type": "fairness", "max_gini": 0.5},
        ],
        "max_ticks": 60,
    }
    api, society = build(demo)

    def policy(s):
        for agent in s.alive_agents():
            if agent.energy < 35 and agent.store().get("food", 0) > 0:
                agent.eat(1)
                continue
            node = s.nearest_node(agent, "food")
            if node:
                agent.move_to(node.x, node.y)
                agent.gather(node)

    api.on_tick(policy)
    api.run()
    out = result(api, society)
    print(json.dumps({k: out[k] for k in ("ok", "score", "tick", "objectives", "treasury", "metrics")}, indent=2))
