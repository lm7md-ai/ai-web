"""Automation City - a self-contained factory simulation (standard library only).

The learner writes ``program(city)`` and drives haulers between machines,
sources and sinks so that a production target is met within a tick budget.
Nothing about the outcome is pre-computed: the machines only advance when the
learner's code feeds them, and the score comes from the recorded state.

Learner contract::

    def program(city):
        h = city.hauler("h1")
        for _ in range(20):
            h.load("mine", "ore", 2)
            h.move_to(2, 2)
            h.unload("smelter")
            city.tick(3)
"""

from __future__ import annotations

import random
from typing import Any, Callable


class MissionStopped(Exception):
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


class Machine:
    def __init__(self, spec: dict) -> None:
        self.name = spec["name"]
        self.x = int(spec.get("x", 0))
        self.y = int(spec.get("y", 0))
        self.recipe: dict[str, int] = dict(spec.get("recipe", {}))
        self.output: dict[str, int] = dict(spec.get("output", {}))
        self.duration = int(spec.get("duration", 1))
        self.capacity = int(spec.get("capacity", 20))
        self.infinite = bool(spec.get("infinite", False))
        self.is_sink = bool(spec.get("sink", False))
        self.buffer_in: dict[str, int] = dict(spec.get("buffer_in", {}))
        self.buffer_out: dict[str, int] = dict(spec.get("buffer_out", {}))
        self.progress = 0
        self.status = "idle"
        self.produced = 0

    def stock(self) -> dict[str, int]:
        return dict(self.buffer_out)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "status": self.status,
            "progress": self.progress,
            "duration": self.duration,
            "buffer_in": dict(self.buffer_in),
            "buffer_out": dict(self.buffer_out),
            "produced": self.produced,
            "infinite": self.infinite,
        }


class Hauler:
    def __init__(self, spec: dict) -> None:
        self.name = spec.get("name", "h1")
        self.x = int(spec.get("x", 0))
        self.y = int(spec.get("y", 0))
        self.capacity = int(spec.get("capacity", 4))
        self.battery = int(spec.get("battery", 400))
        self.cargo: dict[str, int] = {}
        self.idle_ticks = 0

    @property
    def load(self) -> int:
        return sum(self.cargo.values())

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "cargo": dict(self.cargo),
            "load": self.load,
            "capacity": self.capacity,
            "battery": self.battery,
            "idle_ticks": self.idle_ticks,
        }


class City:
    def __init__(self, config: dict) -> None:
        cfg = dict(config or {})
        self.width = int(cfg.get("width", 12))
        self.height = int(cfg.get("height", 8))
        self.max_ticks = int(cfg.get("max_ticks", 200))
        self.move_cost = int(cfg.get("move_cost", 1))
        self.load_cost = int(cfg.get("load_cost", 1))
        self.tick = 0
        self.events: list[Event] = []
        self.machines: dict[str, Machine] = {}
        self.haulers: dict[str, Hauler] = {}
        self.storage: dict[str, int] = {}
        self.objectives = cfg.get("objectives", [])
        self.stop_reason: str | None = None
        self.conflicts = 0
        self.rng = random.Random(cfg.get("seed", 11))
        for spec in cfg.get("machines", []):
            machine = Machine(spec)
            self.machines[machine.name] = machine
            if machine.is_sink:
                self.storage.setdefault("_sink", 0)
        for spec in cfg.get("haulers", [{"name": "h1"}]):
            hauler = Hauler(spec)
            self.haulers[hauler.name] = hauler

    # -------------------------------------------------------------- helpers
    def log(self, type_: str, actor: str = "", **payload) -> None:
        self.events.append(Event(self.tick, type_, payload, actor))

    def machine(self, name: str) -> Machine:
        if name not in self.machines:
            raise KeyError(f"unknown machine {name!r}; available: {sorted(self.machines)}")
        return self.machines[name]

    def hauler(self, name: str) -> Hauler:
        if name not in self.haulers:
            raise KeyError(f"unknown hauler {name!r}; available: {sorted(self.haulers)}")
        return self.haulers[name]

    # -------------------------------------------------------------- actions
    def move_hauler(self, hauler: Hauler, x: int, y: int) -> int:
        steps = 0
        while hauler.x != x or hauler.y != y:
            if hauler.battery <= 0:
                self.log("out_of_energy", hauler.name)
                raise MissionStopped(f"{hauler.name} is out of battery")
            if abs(hauler.x - x) >= abs(hauler.y - y):
                hauler.x += 1 if hauler.x < x else -1
            else:
                hauler.y += 1 if hauler.y < y else -1
            hauler.battery -= self.move_cost
            steps += 1
            self.log("move", hauler.name, x=hauler.x, y=hauler.y, battery=hauler.battery)
            self.advance_time(1)
        return steps

    def load_from(self, hauler: Hauler, machine: Machine, item: str, qty: int) -> int:
        if machine.is_sink:
            raise ValueError(f"{machine.name} is a sink: you cannot load from it")
        room = hauler.capacity - hauler.load
        available = 10**6 if machine.infinite else machine.buffer_out.get(item, 0)
        moved = max(0, min(int(qty), room, available))
        if moved == 0:
            self.log("load_failed", hauler.name, machine=machine.name, item=item, requested=int(qty))
            return 0
        if not machine.infinite:
            machine.buffer_out[item] -= moved
            if machine.buffer_out[item] == 0:
                del machine.buffer_out[item]
        hauler.cargo[item] = hauler.cargo.get(item, 0) + moved
        self.log("load", hauler.name, machine=machine.name, item=item, qty=moved)
        self.advance_time(self.load_cost)
        return moved

    def unload_to(self, hauler: Hauler, machine: Machine, item: str | None = None, qty: int | None = None) -> int:
        moved_total = 0
        items = [item] if item else list(hauler.cargo.keys())
        for name in items:
            have = hauler.cargo.get(name, 0)
            if have <= 0:
                continue
            want = have if qty is None else min(have, int(qty))
            if machine.is_sink:
                accepted = want
                self.storage[name] = self.storage.get(name, 0) + accepted
                self.storage["_sink"] = self.storage.get("_sink", 0) + accepted
                self.log("deliver", hauler.name, machine=machine.name, item=name, qty=accepted)
            else:
                accepted = want
                machine.buffer_in[name] = machine.buffer_in.get(name, 0) + accepted
                self.log("unload", hauler.name, machine=machine.name, item=name, qty=accepted)
            hauler.cargo[name] = have - accepted
            if hauler.cargo[name] == 0:
                del hauler.cargo[name]
            moved_total += accepted
            self.advance_time(self.load_cost)
        return moved_total

    # ---------------------------------------------------------------- clock
    def advance_time(self, ticks: int = 1) -> None:
        for _ in range(int(ticks)):
            self.tick += 1
            self._run_machines()
            if self.tick >= self.max_ticks:
                self.stop_reason = "tick_limit"
                self.log("tick_limit", tick=self.tick)
                raise MissionStopped(f"reached the tick limit ({self.max_ticks})")

    def _run_machines(self) -> None:
        for machine in self.machines.values():
            if machine.is_sink or machine.infinite:
                continue
            if machine.status == "running":
                machine.progress += 1
                if machine.progress >= machine.duration:
                    if sum(machine.buffer_out.values()) + sum(machine.output.values()) > machine.capacity:
                        machine.status = "blocked"
                        self.log("machine_blocked", machine.name, reason="output full")
                        continue
                    for item, qty in machine.output.items():
                        machine.buffer_out[item] = machine.buffer_out.get(item, 0) + qty
                    machine.produced += sum(machine.output.values())
                    machine.progress = 0
                    machine.status = "idle"
                    self.log("machine_done", machine.name, output=dict(machine.output))
                continue
            if machine.status in ("idle", "blocked"):
                if all(machine.buffer_in.get(item, 0) >= qty for item, qty in machine.recipe.items()):
                    if sum(machine.buffer_out.values()) + sum(machine.output.values()) > machine.capacity:
                        machine.status = "blocked"
                        continue
                    for item, qty in machine.recipe.items():
                        machine.buffer_in[item] -= qty
                        if machine.buffer_in[item] == 0:
                            del machine.buffer_in[item]
                    machine.status = "running"
                    machine.progress = 0
                    self.log("machine_start", machine.name, recipe=dict(machine.recipe))


class CityAPI:
    """The object handed to the learner's ``program(city)`` function."""

    def __init__(self, city: City) -> None:
        self._city = city

    # inspection ---------------------------------------------------------
    def machine(self, name: str) -> MachineAPI:
        return MachineAPI(self._city, self._city.machine(name))

    def machines(self) -> list[str]:
        return sorted(self._city.machines)

    def hauler(self, name: str) -> "HaulerAPI":
        return HaulerAPI(self._city, self._city.hauler(name))

    def haulers(self) -> list[str]:
        return sorted(self._city.haulers)

    def storage(self) -> dict[str, int]:
        return {k: v for k, v in self._city.storage.items() if k != "_sink"}

    @property
    def tick(self) -> int:
        return self._city.tick

    def map(self) -> list[str]:
        grid = [["." for _ in range(self._city.width)] for _ in range(self._city.height)]
        for machine in self._city.machines.values():
            if 0 <= machine.x < self._city.width and 0 <= machine.y < self._city.height:
                grid[machine.y][machine.x] = "S" if machine.is_sink else "M"
        for hauler in self._city.haulers.values():
            if 0 <= hauler.x < self._city.width and 0 <= hauler.y < self._city.height:
                grid[hauler.y][hauler.x] = "H"
        return ["".join(row) for row in grid]

    # control -------------------------------------------------------------
    def tick(self, n: int = 1) -> None:  # noqa: F811 - shadowing the property on purpose
        raise TypeError("city.tick is a read-only counter; use city.wait(n) to advance time")

    def wait(self, n: int = 1) -> None:
        self._city.advance_time(int(n))

    def say(self, message: str) -> None:
        self._city.log("say", "city", message=str(message)[:160])


class MachineAPI:
    def __init__(self, city: City, machine: Machine) -> None:
        self._city = city
        self._machine = machine

    @property
    def status(self) -> str:
        return self._machine.status

    @property
    def progress(self) -> int:
        return self._machine.progress

    def input(self) -> dict[str, int]:
        return dict(self._machine.buffer_in)

    def output(self) -> dict[str, int]:
        return dict(self._machine.buffer_out)

    def produced(self) -> int:
        return self._machine.produced

    def position(self) -> tuple[int, int]:
        return (self._machine.x, self._machine.y)

    def recipe(self) -> dict[str, int]:
        return dict(self._machine.recipe)

    def can_start(self) -> bool:
        return all(
            self._machine.buffer_in.get(item, 0) >= qty for item, qty in self._machine.recipe.items()
        )

    def __repr__(self) -> str:
        return f"<Machine {self._machine.name} {self._machine.status} in={self._machine.buffer_in} out={self._machine.buffer_out}>"


class HaulerAPI:
    def __init__(self, city: City, hauler: Hauler) -> None:
        self._city = city
        self._hauler = hauler

    def move_to(self, x: int, y: int) -> int:
        return self._city.move_hauler(self._hauler, int(x), int(y))

    def load(self, machine: str, item: str, qty: int = 1) -> int:
        return self._city.load_from(self._hauler, self._city.machine(machine), item, int(qty))

    def unload(self, machine: str, item: str | None = None, qty: int | None = None) -> int:
        return self._city.unload_to(self._hauler, self._city.machine(machine), item, qty)

    def position(self) -> tuple[int, int]:
        return (self._hauler.x, self._hauler.y)

    def cargo(self) -> dict[str, int]:
        return dict(self._hauler.cargo)

    @property
    def battery(self) -> int:
        return self._hauler.battery

    def wait(self, n: int = 1) -> None:
        self._city.advance_time(int(n))

    def __repr__(self) -> str:
        return f"<Hauler {self._hauler.name} at=({self._hauler.x},{self._hauler.y}) cargo={self._hauler.cargo}>"


def build(config: dict) -> tuple[CityAPI, City]:
    city = City(config)
    city.log("start", tick=0, machines=len(city.machines), haulers=len(city.haulers))
    return CityAPI(city), city


def evaluate(city: City) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in city.objectives:
        kind = objective.get("type", "produce")
        if kind == "produce":
            item = objective.get("item", "widget")
            needed = int(objective.get("quantity", 1))
            have = city.storage.get(item, 0)
            results.append({"type": kind, "ok": have >= needed, "detail": f"delivered {have}/{needed} {item}"})
        elif kind == "ticks":
            limit = int(objective.get("max", city.max_ticks))
            results.append({"type": kind, "ok": city.tick <= limit, "detail": f"used {city.tick}/{limit} ticks"})
        elif kind == "battery":
            minimum = int(objective.get("min", 0))
            results.append(
                {
                    "type": kind,
                    "ok": all(h.battery >= minimum for h in city.haulers.values()),
                    "detail": ", ".join(f"{h.name}={h.battery}" for h in city.haulers.values()),
                }
            )
        elif kind == "throughput":
            needed = int(objective.get("min", 1))
            produced = sum(m.produced for m in city.machines.values())
            results.append({"type": kind, "ok": produced >= needed, "detail": f"produced {produced}/{needed}"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    passed = sum(1 for r in results if r["ok"])
    return results, round(passed / len(results), 3) if results else 0.0


def result(api: CityAPI, city: City) -> dict:
    objectives, score = evaluate(city)
    ok = all(o["ok"] for o in objectives)
    city.stop_reason = "completed" if ok else (city.stop_reason or "objectives_unmet")
    return {
        "world": "automation_city",
        "ok": ok,
        "score": score,
        "tick": city.tick,
        "stop_reason": city.stop_reason or ("completed" if ok else "objectives_unmet"),
        "machines": {name: m.to_dict() for name, m in city.machines.items()},
        "haulers": {name: h.to_dict() for name, h in city.haulers.items()},
        "storage": {k: v for k, v in city.storage.items() if k != "_sink"},
        "objectives": objectives,
        "events": [e.to_dict() for e in city.events][-2000:],
        "grid": api.map(),
        "stats": {
            "deliveries": sum(1 for e in city.events if e.type == "deliver"),
            "machine_runs": sum(1 for e in city.events if e.type == "machine_done"),
            "moves": sum(1 for e in city.events if e.type == "move"),
            "battery_left": sum(h.battery for h in city.haulers.values()),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    demo = {
        "width": 8,
        "height": 6,
        "machines": [
            {"name": "mine", "x": 0, "y": 0, "output": {"ore": 1}, "duration": 1, "infinite": True},
            {"name": "smelter", "x": 4, "y": 0, "recipe": {"ore": 2}, "output": {"plate": 1}, "duration": 2},
            {"name": "export", "x": 7, "y": 5, "sink": True},
        ],
        "haulers": [{"name": "h1", "x": 1, "y": 0, "capacity": 4, "battery": 300}],
        "objectives": [{"type": "produce", "item": "plate", "quantity": 3}, {"type": "ticks", "max": 80}],
        "max_ticks": 120,
    }
    api, city = build(demo)
    try:
        h = api.hauler("h1")
        for _ in range(4):
            h.load("mine", "ore", 2)
            h.move_to(4, 0)
            h.unload("smelter")
            api.wait(2)
            h.load("smelter", "plate", 4)
            h.move_to(7, 5)
            h.unload("export")
    except MissionStopped as exc:
        print("stopped:", exc)
    import json

    print(json.dumps(result(api, city), indent=2)[:900])
