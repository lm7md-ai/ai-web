"""Crisis Simulator - an incident-response reliability arena.

Stdlib only: this file is copied verbatim into the execution sandbox.

A seeded incident schedule hits a small fleet of services.  The learner writes
``program(ops)``: read the alerts, choose an action per service, and advance the
clock.  Restarting is fast but costs availability; rollback is safe only while
no writes were accepted since the deploy; scaling costs money.  The world
computes uptime, MTTR and spend from the learner's decisions.

Learner contract::

    def program(ops):
        while ops.running():
            for alert in ops.alerts():
                if alert["kind"] == "latency":
                    ops.act(alert["service"], "scale", by=2)
                else:
                    ops.investigate(alert["service"])
            ops.wait()
"""

from __future__ import annotations

import copy
import json
import random

ACTIONS = {
    "restart": {"cost": 2, "downtime": 1, "fixes": ["crash", "leak"]},
    "scale": {"cost": 4, "downtime": 0, "fixes": ["latency", "overload"]},
    "rollback": {"cost": 6, "downtime": 2, "fixes": ["bad_deploy"], "data_loss_if_writes": True},
    # patch is the expensive, loss-free way to undo a bad deploy; rollback is
    # cheaper but destroys writes accepted since the deploy.
    "patch": {"cost": 8, "downtime": 0, "fixes": ["bug", "bad_deploy"]},
    "noop": {"cost": 0, "downtime": 0, "fixes": []},
}


class BudgetExceeded(Exception):
    """Raised when the incident window closes or the money runs out."""


class Ops:
    def __init__(self, services: list[dict], incidents: list[dict], horizon: int,
                 budget: int, objectives: list[dict]) -> None:
        self.services = {s["name"]: dict(s, healthy=True, load=0.4, writes_since_deploy=0)
                         for s in services}
        self.incidents = incidents
        self.horizon = horizon
        self.budget = budget
        self.objectives = objectives
        self.minute = 0
        self.spend = 0
        self.downtime_minutes = 0
        self.data_loss_events = 0
        self.mttr_samples: list[int] = []
        self.open: list[dict] = []
        self.actions: list[dict] = []
        self.stop_reason = ""
        self._fired: set[int] = set()

    # ------------------------------------------------------------------ senses
    def names(self) -> list[str]:
        return sorted(self.services)

    def running(self) -> bool:
        return self.minute < self.horizon

    def alerts(self) -> list[dict]:
        return [dict(incident) for incident in self.open]

    def health(self, name: str) -> dict:
        service = self.services[name]
        return {"healthy": service["healthy"], "load": round(service["load"], 3),
                "writes_since_deploy": service["writes_since_deploy"]}

    def money_left(self) -> int:
        return self.budget - self.spend

    # ------------------------------------------------------------------ action
    def investigate(self, name: str) -> dict:
        """Free but slow: reveals the root cause of an incident on that service."""
        for incident in self.open:
            if incident["service"] == name:
                incident["diagnosed"] = True
                self.actions.append({"tick": self.minute, "type": "investigate", "service": name,
                                     "cause": incident["kind"]})
                return {"service": name, "cause": incident["kind"]}
        return {"service": name, "cause": None}

    def act(self, name: str, action: str, **kwargs) -> dict:
        if name not in self.services:
            raise KeyError(f"unknown service: {name}")
        if action not in ACTIONS:
            raise ValueError(f"unknown action: {action}")
        spec = ACTIONS[action]
        if self.spend + spec["cost"] > self.budget:
            self.stop_reason = "budget exhausted"
            raise BudgetExceeded(f"{action} costs {spec['cost']}, only {self.money_left()} left")
        service = self.services[name]
        self.spend += spec["cost"]
        resolved = None
        for incident in list(self.open):
            if incident["service"] != name or incident["kind"] not in spec["fixes"]:
                continue
            if action == "rollback" and service["writes_since_deploy"] > 0:
                self.data_loss_events += 1
                self.actions.append({"tick": self.minute, "type": "data_loss", "service": name,
                                     "writes": service["writes_since_deploy"]})
            self.open.remove(incident)
            incident["resolved_at"] = self.minute
            self.mttr_samples.append(self.minute - incident["started_at"])
            resolved = incident["kind"]
            break
        downtime = spec["downtime"] if resolved else max(0, spec["downtime"] // 2)
        self.downtime_minutes += downtime
        if action == "scale":
            service["load"] = max(0.05, service["load"] - 0.25 * float(kwargs.get("by", 1)))
        if action == "restart":
            service["writes_since_deploy"] = 0
        service["healthy"] = not self.open or all(
            incident["service"] != name for incident in self.open
        )
        self.actions.append({"tick": self.minute, "type": action, "service": name,
                             "resolved": resolved, "downtime": downtime, "cost": spec["cost"]})
        return {"resolved": resolved, "downtime": downtime, "spend": self.spend}

    def wait(self, minutes: int = 1) -> None:
        """Advance the clock: new incidents may arrive and load drifts upward."""
        for _ in range(minutes):
            self.minute += 1
            for index, incident in enumerate(self.incidents):
                if incident["at"] == self.minute and index not in self._fired:
                    self._fired.add(index)
                    entry = dict(incident)
                    entry.setdefault("started_at", self.minute)
                    entry["diagnosed"] = False
                    self.open.append(entry)
                    self.services[entry["service"]]["healthy"] = False
            # An unresolved incident keeps the service unavailable: doing
            # nothing is the most expensive strategy.
            self.downtime_minutes += len(self.open)
            for service in self.services.values():
                service["load"] = min(1.0, service["load"] + 0.02)
                if service["healthy"]:
                    service["writes_since_deploy"] += 1
            if self.minute >= self.horizon:
                self.stop_reason = self.stop_reason or "incident window closed"
                return


def build(config: dict):
    seed = int(config.get("seed", 21))
    rng = random.Random(seed)
    services = list(config.get("services") or [{"name": "api"}, {"name": "db"}, {"name": "worker"}])
    horizon = int(config.get("horizon", 60))
    incidents = copy.deepcopy(list(config.get("incidents") or []))
    if not incidents:
        kinds = ["crash", "latency", "bad_deploy", "leak", "bug"]
        for i in range(4):
            incidents.append({
                "at": rng.randint(3, horizon - 5),
                "service": rng.choice([s["name"] for s in services]),
                "kind": rng.choice(kinds),
                "severity": rng.choice(["low", "high"]),
            })
    ops = Ops(
        services,
        incidents,
        horizon=horizon,
        budget=int(config.get("budget", 60)),
        objectives=list(config.get("objectives") or [
            {"type": "uptime", "min": 0.9},
            {"type": "mttr", "max": 12},
            {"type": "budget", "max": 60},
        ]),
    )
    ops.actions.append({"tick": 0, "type": "init", "services": len(services), "horizon": horizon})
    return ops, ops


def evaluate(ops: Ops, objectives: list[dict]) -> tuple[list[dict], float]:
    total = max(1, ops.horizon * len(ops.services))
    uptime = max(0.0, 1.0 - (ops.downtime_minutes / total))
    mttr = round(sum(ops.mttr_samples) / len(ops.mttr_samples), 2) if ops.mttr_samples else None
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "uptime")
        if kind == "uptime":
            minimum = float(objective.get("min", 0.9))
            ok = uptime >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"uptime {uptime:.3f} (min {minimum})"})
        elif kind == "mttr":
            limit = float(objective.get("max", 15))
            ok = mttr is not None and mttr <= limit
            results.append({"type": kind, "ok": ok,
                            "detail": f"MTTR {mttr} minutes (max {limit})" if mttr is not None
                                      else "no incident was resolved"})
        elif kind == "resolved":
            needed = int(objective.get("count", len(ops.incidents)))
            ok = len(ops.mttr_samples) >= needed
            results.append({"type": kind, "ok": ok,
                            "detail": f"resolved {len(ops.mttr_samples)}/{needed} incidents"})
        elif kind == "budget":
            limit = int(objective.get("max", ops.budget))
            ok = ops.spend <= limit
            results.append({"type": kind, "ok": ok,
                            "detail": f"spent {ops.spend} of {limit}"})
        elif kind == "no_data_loss":
            ok = ops.data_loss_events == 0
            results.append({"type": kind, "ok": ok,
                            "detail": f"{ops.data_loss_events} rollbacks destroyed committed writes"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Ops, state: Ops) -> dict:
    evaluated, score = evaluate(state, state.objectives)
    ok = all(item["ok"] for item in evaluated)
    total = max(1, state.horizon * len(state.services))
    return {
        "world": "crisis_simulator",
        "ok": ok,
        "score": score,
        "tick": state.minute,
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": state.actions[-300:],
        "state": {name: state.health(name) for name in state.names()},
        "stats": {
            "minute": state.minute,
            "horizon": state.horizon,
            "open_incidents": len(state.open),
            "resolved": len(state.mttr_samples),
            "downtime_minutes": state.downtime_minutes,
            "uptime": round(max(0.0, 1.0 - state.downtime_minutes / total), 4),
            "spend": state.spend,
            "data_loss_events": state.data_loss_events,
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({
        "seed": 5,
        "horizon": 40,
        "budget": 100,
        "services": [{"name": "api"}, {"name": "db"}],
        "incidents": [
            {"at": 5, "service": "api", "kind": "latency"},
            {"at": 12, "service": "db", "kind": "crash"},
            {"at": 25, "service": "api", "kind": "bad_deploy"},
        ],
        "objectives": [{"type": "resolved", "count": 3}, {"type": "uptime", "min": 0.9},
                       {"type": "no_data_loss"}],
    })

    def program(ops):
        while ops.running():
            for alert in ops.alerts():
                cause = ops.investigate(alert["service"])["cause"]
                if cause in ("latency", "overload"):
                    ops.act(alert["service"], "scale", by=2)
                elif cause == "bad_deploy":
                    if ops.health(alert["service"])["writes_since_deploy"] == 0:
                        ops.act(alert["service"], "rollback")
                    else:
                        ops.act(alert["service"], "patch")
                else:
                    ops.act(alert["service"], "restart")
            ops.wait()

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
