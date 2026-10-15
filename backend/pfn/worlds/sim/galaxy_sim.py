"""Knowledge Galaxy - a spaced-repetition scheduling arena.

Stdlib only: this file is copied verbatim into the execution sandbox.

Every node in the galaxy is a skill with a difficulty and a retention level that
decays a little each day.  The learner writes the scheduler: pick which nodes to
review today, and the world honestly simulates the forgetting curve.  Reviewing
a node raises its retention by an amount that shrinks with how well it was
already remembered, so cramming one node while ignoring others is punished.

Learner contract::

    def program(galaxy):
        while galaxy.days_left() > 0:
            due = sorted(galaxy.candidates(), key=lambda n: n["retention"])[: galaxy.daily_budget()]
            for node in due:
                galaxy.review(node["id"])
            galaxy.sleep()
"""

from __future__ import annotations

import json
import random


class BudgetExceeded(Exception):
    """Raised when the learner reviews more nodes than the daily budget allows."""


class Galaxy:
    def __init__(self, nodes: list[dict], days: int, budget: int, objectives: list[dict]) -> None:
        self.nodes = {node["id"]: dict(node, retention=float(node.get("retention", 0.6)),
                                       last_review=0, reviews=0)
                      for node in nodes}
        self.days = days
        self.budget = budget
        self.objectives = objectives
        self.day = 0
        self.reviews_today = 0
        self.events: list[dict] = []
        self.history: list[dict] = []
        self.stop_reason = ""

    # ------------------------------------------------------------------ senses
    def candidates(self) -> list[dict]:
        return [{"id": node["id"], "retention": round(node["retention"], 4),
                 "difficulty": node["difficulty"], "last_review": node["last_review"],
                 "critical": bool(node.get("critical"))}
                for node in self.nodes.values()]

    def retention(self, node_id: str) -> float:
        return round(self.nodes[node_id]["retention"], 4)

    def days_left(self) -> int:
        return max(0, self.days - self.day)

    def daily_budget(self) -> int:
        """How many reviews today's session allows."""
        return self.budget

    def reviews_left(self) -> int:
        return max(0, self.budget - self.reviews_today)

    # ------------------------------------------------------------------ action
    def review(self, node_id: str) -> dict:
        if node_id not in self.nodes:
            raise KeyError(f"unknown node: {node_id}")
        if self.reviews_today >= self.budget:
            self.stop_reason = "daily review budget exceeded"
            raise BudgetExceeded(f"{self.budget} reviews per day, {self.reviews_today} used")
        node = self.nodes[node_id]
        gain = 0.70 * (1.0 - node["retention"]) * (1.0 - 0.30 * node["difficulty"])
        before = node["retention"]
        node["retention"] = min(0.99, node["retention"] + gain)
        node["last_review"] = self.day
        node["reviews"] += 1
        self.reviews_today += 1
        self.events.append({"tick": self.day, "type": "review", "node": node_id,
                            "before": round(before, 3), "after": round(node["retention"], 3)})
        return {"node": node_id, "before": round(before, 4), "after": round(node["retention"], 4)}

    def sleep(self, days: int = 1) -> None:
        """Advance the clock: every node forgets a bit, harder nodes faster."""
        for _ in range(days):
            self.day += 1
            for node in self.nodes.values():
                decay = 0.02 + 0.06 * node["difficulty"]
                node["retention"] = max(0.0, node["retention"] - decay)
            self.history.append({
                "day": self.day,
                "average_retention": round(self.average_retention(), 4),
                "reviews": self.reviews_today,
            })
            self.reviews_today = 0
            if self.day >= self.days:
                self.stop_reason = self.stop_reason or "horizon reached"
                return

    # ------------------------------------------------------------------ report
    def average_retention(self) -> float:
        values = [node["retention"] for node in self.nodes.values()]
        return sum(values) / len(values) if values else 0.0

    def weakest(self, count: int = 5) -> list[dict]:
        ordered = sorted(self.nodes.values(), key=lambda n: n["retention"])
        return [{"id": n["id"], "retention": round(n["retention"], 4)} for n in ordered[:count]]

    def forgotten(self, threshold: float = 0.35) -> list[str]:
        return [n["id"] for n in self.nodes.values() if n["retention"] < threshold]


def build(config: dict):
    seed = int(config.get("seed", 8))
    rng = random.Random(seed)
    nodes = list(config.get("nodes") or [])
    if not nodes:
        names = ["variables", "loops", "functions", "lists", "dicts", "files",
                 "exceptions", "classes", "testing", "recursion"]
        nodes = [{"id": name, "difficulty": round(rng.uniform(0.1, 0.9), 2),
                  "retention": round(rng.uniform(0.35, 0.75), 2),
                  "critical": i < 3} for i, name in enumerate(names)]
    galaxy = Galaxy(
        nodes,
        days=int(config.get("days", 30)),
        budget=int(config.get("budget", 3)),
        objectives=list(config.get("objectives") or [
            {"type": "retention", "min": 0.75},
            {"type": "critical", "min": 0.8},
            {"type": "budget"},
        ]),
    )
    galaxy.events.append({"tick": 0, "type": "init", "nodes": len(nodes), "days": galaxy.days})
    return galaxy, galaxy


def evaluate(galaxy: Galaxy, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "retention")
        if kind == "retention":
            minimum = float(objective.get("min", 0.75))
            average = galaxy.average_retention()
            ok = average >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"average retention {average:.3f} (min {minimum})"})
        elif kind == "critical":
            minimum = float(objective.get("min", 0.8))
            criticals = [n for n in galaxy.nodes.values() if n.get("critical")]
            if criticals:
                average = sum(n["retention"] for n in criticals) / len(criticals)
                ok = average >= minimum
                results.append({"type": kind, "ok": ok,
                                "detail": f"critical nodes at {average:.3f} (min {minimum})"})
            else:
                results.append({"type": kind, "ok": True, "detail": "no critical nodes"})
        elif kind == "no_forgotten":
            threshold = float(objective.get("threshold", 0.3))
            forgotten = galaxy.forgotten(threshold)
            ok = not forgotten
            results.append({"type": kind, "ok": ok,
                            "detail": f"{len(forgotten)} nodes below {threshold}"
                                      + (f": {forgotten[:5]}" if forgotten else "")})
        elif kind == "coverage":
            minimum = float(objective.get("min", 0.8))
            reviewed = sum(1 for n in galaxy.nodes.values() if n["reviews"] > 0)
            ratio = reviewed / len(galaxy.nodes)
            ok = ratio >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"{reviewed}/{len(galaxy.nodes)} nodes reviewed (min {minimum})"})
        elif kind == "budget":
            ok = galaxy.stop_reason != "daily review budget exceeded"
            results.append({"type": kind, "ok": ok, "detail": galaxy.stop_reason or "within budget"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Galaxy, state: Galaxy) -> dict:
    evaluated, score = evaluate(state, state.objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "knowledge_galaxy",
        "ok": ok,
        "score": score,
        "tick": state.day,
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": state.events[-200:],
        "history": state.history[-60:],
        "state": {"day": state.day, "average_retention": round(state.average_retention(), 4),
                  "weakest": state.weakest(5)},
        "stats": {
            "nodes": len(state.nodes),
            "days": state.days,
            "reviews": sum(n["reviews"] for n in state.nodes.values()),
            "reviewed_nodes": sum(1 for n in state.nodes.values() if n["reviews"] > 0),
            "average_retention": round(state.average_retention(), 4),
            "forgotten": len(state.forgotten(0.3)),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({"days": 30, "budget": 4,
                        "objectives": [{"type": "retention", "min": 0.75},
                                       {"type": "critical", "min": 0.8},
                                       {"type": "coverage", "min": 0.9}]})

    def program(galaxy):
        while galaxy.days_left() > 0:
            due = sorted(galaxy.candidates(), key=lambda n: (n["retention"], -n["difficulty"]))
            for node in due[:galaxy.daily_budget()]:
                galaxy.review(node["id"])
            galaxy.sleep()

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
