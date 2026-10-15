"""STEM Cosmos - a deterministic physics laboratory.

Stdlib only: this file is copied verbatim into the execution sandbox.

The learner flies a craft by writing ``program(lab)`` and calling
``lab.thrust(dx, dy)`` each step.  The world integrates Newtonian motion with
Euler steps at a fixed ``dt``, so the trajectory is fully determined by the
learner's control law - nothing is scripted.

Learner contract::

    def program(lab):
        while lab.altitude() < 120:
            lab.thrust(0, 3.0)
            lab.step()
"""

from __future__ import annotations

import json
import math

G = 9.80665


class StepLimit(Exception):
    """Raised when the simulation horizon is reached."""


class OutOfFuel(Exception):
    """Raised when the craft spends more delta-v than its tank holds."""


class Lab:
    def __init__(self, config: dict) -> None:
        self.dt = float(config.get("dt", 0.05))
        self.max_steps = int(config.get("max_steps", 4000))
        self.gravity = float(config.get("gravity", G))
        self.planet_radius = float(config.get("planet_radius", 6371.0))
        self.drag = float(config.get("drag", 0.0))
        self.fuel = float(config.get("fuel", 300.0))

        self.x = float(config.get("x", 0.0))
        self.y = float(config.get("y", 0.0))
        self.vx = float(config.get("vx", 0.0))
        self.vy = float(config.get("vy", 0.0))
        self.step_index = 0
        self.max_altitude = self.y
        self.max_speed = math.hypot(self.vx, self.vy)
        self.orbit_ticks = 0
        self.stop_reason = ""
        self.events: list[dict] = []
        self.objectives: list[dict] = list(config.get("objectives") or [{"type": "altitude", "min": 100}])

    # ------------------------------------------------------------------ senses
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    def velocity(self) -> tuple[float, float]:
        return (self.vx, self.vy)

    def altitude(self) -> float:
        return self.y

    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    def fuel_left(self) -> float:
        return self.fuel

    def steps(self) -> int:
        return self.step_index

    # --------------------------------------------------------------- actuators
    def thrust(self, ax: float, ay: float) -> None:
        """Spend fuel to accelerate. Cost is proportional to |a| * dt."""
        cost = math.hypot(ax, ay) * self.dt
        if cost > self.fuel:
            self.stop_reason = "out of fuel"
            raise OutOfFuel(f"needed {cost:.3f}, only {self.fuel:.3f} left")
        self.fuel -= cost
        self._pending_ax = ax
        self._pending_ay = ay

    def step(self, steps: int = 1) -> None:
        for _ in range(steps):
            if self.step_index >= self.max_steps:
                self.stop_reason = self.stop_reason or "simulation horizon reached"
                raise StepLimit(f"reached {self.max_steps} steps")
            ax = getattr(self, "_pending_ax", 0.0)
            ay = getattr(self, "_pending_ay", 0.0)
            self._pending_ax = 0.0
            self._pending_ay = 0.0

            speed = self.speed()
            drag_x = -self.drag * speed * self.vx if self.drag else 0.0
            drag_y = -self.drag * speed * self.vy if self.drag else 0.0

            self.vx += (ax + drag_x) * self.dt
            self.vy += (ay + drag_y - self.gravity) * self.dt
            self.x += self.vx * self.dt
            self.y += self.vy * self.dt
            self.step_index += 1

            if self.y <= 0.0:  # ground contact
                self.y = 0.0
                self.vy = max(0.0, self.vy)
                self.vx *= 0.4
                self.events.append({"tick": self.step_index, "type": "ground_contact"})

            self.max_altitude = max(self.max_altitude, self.y)
            self.max_speed = max(self.max_speed, self.speed())
            if self.orbital():
                self.orbit_ticks += 1

    def orbital(self) -> bool:
        """A crude but honest circular-orbit test: vertical speed near zero while high."""
        return self.y > 50.0 and abs(self.vy) < 1.0 and self.speed() > 20.0

    # ------------------------------------------------------------------ report
    def log(self, kind: str, **payload) -> None:
        self.events.append({"tick": self.step_index, "type": kind, **payload})

    def trajectory(self, every: int = 20) -> list[dict]:
        return [{"tick": e["tick"], "type": e["type"]} for e in self.events[::every]][:60]


def build(config: dict):
    lab = Lab(config)
    lab.log("init", altitude=round(lab.y, 3), fuel=lab.fuel, dt=lab.dt)
    return lab, lab


def evaluate(lab: Lab, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "altitude")
        if kind == "altitude":
            minimum = float(objective.get("min", 100))
            ok = lab.max_altitude >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"max altitude {lab.max_altitude:.2f} m (need {minimum})"})
        elif kind == "land":
            tolerance = float(objective.get("max_speed", 2.0))
            ok = lab.y <= 0.01 and lab.speed() <= tolerance
            results.append({"type": kind, "ok": ok,
                            "detail": f"touchdown speed {lab.speed():.2f} m/s (max {tolerance})"})
        elif kind == "orbit":
            ticks = int(objective.get("ticks", 50))
            ok = lab.orbit_ticks >= ticks
            results.append({"type": kind, "ok": ok,
                            "detail": f"{lab.orbit_ticks} orbital steps (need {ticks})"})
        elif kind == "fuel":
            minimum = float(objective.get("min", 0.0))
            ok = lab.fuel >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"{lab.fuel:.2f} fuel left (need >= {minimum})"})
        elif kind == "steps":
            limit = int(objective.get("max", lab.max_steps))
            ok = lab.step_index <= limit
            results.append({"type": kind, "ok": ok,
                            "detail": f"{lab.step_index} steps (budget {limit})"})
        elif kind == "range":
            target = float(objective.get("x", 0.0))
            tolerance = float(objective.get("tolerance", 5.0))
            ok = abs(lab.x - target) <= tolerance
            results.append({"type": kind, "ok": ok,
                            "detail": f"downrange {lab.x:.2f} m (target {target} ±{tolerance})"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Lab, state: Lab) -> dict:
    objectives = list(state.objectives or [{"type": "altitude", "min": 100}])
    evaluated, score = evaluate(state, objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "stem_cosmos",
        "ok": ok,
        "score": score,
        "tick": state.step_index,
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": state.events[-200:],
        "state": {
            "x": round(state.x, 3),
            "y": round(state.y, 3),
            "vx": round(state.vx, 3),
            "vy": round(state.vy, 3),
        },
        "stats": {
            "max_altitude": round(state.max_altitude, 3),
            "max_speed": round(state.max_speed, 3),
            "fuel_left": round(state.fuel, 3),
            "orbit_steps": state.orbit_ticks,
            "steps": state.step_index,
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({"fuel": 400.0, "max_steps": 3000,
                        "objectives": [{"type": "altitude", "min": 120}, {"type": "fuel", "min": 0}]})

    def program(lab):
        while lab.altitude() < 130 and lab.steps() < 2500:
            lab.thrust(0.0, 22.0)
            lab.step()

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
