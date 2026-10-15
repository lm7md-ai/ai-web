"""CareerVerse - a sprint delivery simulator.

Stdlib only: this file is copied verbatim into the execution sandbox.

The learner acts as the engineer planning a sprint: choose the order of tasks,
how much capacity goes to review, and when to ask for help.  The world then
simulates the days honestly - dependencies block, unreviewed work loses
quality, and asking for help costs a day but removes a blocker.

Learner contract::

    def program(sprint):
        sprint.plan(["schema", "api", "tests"])
        sprint.set_review_ratio(0.3)
        sprint.run()
"""

from __future__ import annotations

import json


class BudgetExceeded(Exception):
    """Raised when the sprint runs past its deadline."""


class Sprint:
    def __init__(self, tasks: list[dict], days: int, capacity: float, objectives: list[dict]) -> None:
        self.tasks = tasks
        self.days = days
        self.capacity = capacity
        self.objectives = objectives
        self.order: list[str] = []
        self.review_ratio = 0.0
        self.help_requests: list[str] = []
        self.day = 0
        self.events: list[dict] = []
        self.done: list[str] = []
        self.quality: dict[str, float] = {}
        self.stop_reason = ""
        self.finished = False

    # ------------------------------------------------------------------ senses
    def task_ids(self) -> list[str]:
        return [task["id"] for task in self.tasks]

    def task(self, task_id: str) -> dict:
        for task in self.tasks:
            if task["id"] == task_id:
                return {k: v for k, v in task.items() if k != "depends_on_explain"}
        raise KeyError(task_id)

    def estimate(self, task_id: str) -> float:
        return float(self.task(task_id).get("estimate", 1.0))

    def dependencies(self, task_id: str) -> list[str]:
        return list(self.task(task_id).get("depends_on", []))

    def remaining_days(self) -> int:
        return max(0, self.days - self.day)

    # ------------------------------------------------------------------ action
    def plan(self, order: list[str]) -> None:
        unknown = [task for task in order if task not in self.task_ids()]
        if unknown:
            raise KeyError(f"unknown tasks in plan: {unknown}")
        missing = [task for task in self.task_ids() if task not in order]
        if missing:
            raise ValueError(f"plan is missing tasks: {missing}")
        self.order = list(order)

    def set_review_ratio(self, ratio: float) -> None:
        if not 0.0 <= ratio <= 0.6:
            raise ValueError("review ratio must be between 0.0 and 0.6")
        self.review_ratio = float(ratio)

    def ask_for_help(self, task_id: str) -> None:
        """Costs a day, but clears the blocker on that task."""
        self.help_requests.append(task_id)
        self.events.append({"tick": self.day, "type": "help", "task": task_id})
        self.day += 1
        self._check_deadline()

    def _check_deadline(self) -> None:
        if self.day > self.days:
            self.stop_reason = "sprint deadline passed"
            raise BudgetExceeded(f"day {self.day} is past the {self.days}-day sprint")

    def run(self) -> dict:
        """Simulate the planned sprint day by day."""
        if not self.order:
            self.order = self.task_ids()
        build_capacity = self.capacity * (1.0 - self.review_ratio)
        review_capacity = self.capacity * self.review_ratio
        todo = list(self.order)
        awaiting_review: dict[str, float] = {}
        self.day = 0
        try:
            self._simulate(todo, awaiting_review, build_capacity, review_capacity)
        except BudgetExceeded:
            self.stop_reason = self.stop_reason or "sprint deadline passed"
        self.finished = True
        return {"day": self.day, "done": list(self.done), "quality": self.quality}

    def _simulate(self, todo: list[str], awaiting_review: dict[str, float],
                  build_capacity: float, review_capacity: float) -> None:
        while todo or awaiting_review:
            self.day += 1
            self._check_deadline()
            day_build = build_capacity
            day_review = review_capacity

            for task_id in list(todo):
                if day_build <= 0:
                    break
                deps = self.dependencies(task_id)
                if any(dep not in self.done for dep in deps):
                    self.events.append({"tick": self.day, "type": "blocked", "task": task_id,
                                        "waiting_on": [d for d in deps if d not in self.done]})
                    continue
                need = self.estimate(task_id)
                if need <= day_build:
                    day_build -= need
                    awaiting_review[task_id] = max(0.2, self.task(task_id).get("review", 0.5))
                    todo.remove(task_id)
                    self.events.append({"tick": self.day, "type": "built", "task": task_id})
                else:
                    # Spend the rest of the day's build capacity on this task
                    # and keep going: a partial day is still real progress.
                    remaining = need - day_build
                    self.tasks[self.task_ids().index(task_id)]["estimate"] = round(remaining, 4)
                    self.events.append({"tick": self.day, "type": "progress", "task": task_id,
                                        "left": round(remaining, 2)})
                    day_build = 0.0

            for task_id in list(awaiting_review):
                if day_review <= 0:
                    break
                review_need = awaiting_review[task_id]
                if review_need <= day_review:
                    day_review -= review_need
                    self.done.append(task_id)
                    self.quality[task_id] = round(min(1.0, 0.45 + self.review_ratio * 1.6), 3)
                    awaiting_review.pop(task_id)
                    self.events.append({"tick": self.day, "type": "shipped", "task": task_id,
                                        "quality": self.quality[task_id]})
                else:
                    awaiting_review[task_id] = review_need - day_review
                    day_review = 0.0
                    self.events.append({"tick": self.day, "type": "reviewing", "task": task_id,
                                        "left": round(awaiting_review[task_id], 2)})

            if not todo and not awaiting_review:
                break
            if self.day > self.days * 4:  # safety valve against pathological plans
                self.stop_reason = "sprint never converged"
                break


def build(config: dict):
    tasks = list(config.get("tasks") or DEFAULT_TASKS)
    sprint = Sprint(
        tasks,
        days=int(config.get("days", 10)),
        capacity=float(config.get("capacity", 1.0)),
        objectives=list(config.get("objectives") or [{"type": "delivered"}, {"type": "deadline"},
                                                     {"type": "quality", "min": 0.8}]),
    )
    sprint.events.append({"tick": 0, "type": "init", "tasks": len(tasks), "days": sprint.days})
    return sprint, sprint


DEFAULT_TASKS = [
    {"id": "schema", "estimate": 1.5, "review": 0.4, "depends_on": []},
    {"id": "api", "estimate": 2.5, "review": 0.6, "depends_on": ["schema"]},
    {"id": "ui", "estimate": 2.0, "review": 0.5, "depends_on": ["api"]},
    {"id": "tests", "estimate": 1.5, "review": 0.3, "depends_on": ["api"]},
    {"id": "docs", "estimate": 1.0, "review": 0.2, "depends_on": ["ui", "tests"]},
]


def evaluate(sprint: Sprint, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "delivered")
        if kind == "delivered":
            required = [t["id"] for t in sprint.tasks if t.get("must")]
            needed = required or sprint.task_ids()
            ok = all(task in sprint.done for task in needed)
            missing = [t for t in needed if t not in sprint.done]
            results.append({"type": kind, "ok": ok,
                            "detail": f"{len(needed) - len(missing)}/{len(needed)} tasks shipped"
                                      + (f", missing {missing}" if missing else "")})
        elif kind == "deadline":
            ok = sprint.day <= sprint.days
            results.append({"type": kind, "ok": ok,
                            "detail": f"finished on day {sprint.day} of {sprint.days}"})
        elif kind == "quality":
            minimum = float(objective.get("min", 0.8))
            values = list(sprint.quality.values())
            average = sum(values) / len(values) if values else 0.0
            ok = bool(values) and average >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"average quality {average:.2f} (min {minimum})"})
        elif kind == "reviewed":
            ok = sprint.review_ratio > 0
            results.append({"type": kind, "ok": ok,
                            "detail": f"review ratio {sprint.review_ratio:.2f}"})
        elif kind == "no_help":
            ok = not sprint.help_requests
            results.append({"type": kind, "ok": ok,
                            "detail": f"{len(sprint.help_requests)} help requests"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Sprint, state: Sprint) -> dict:
    if not state.finished:
        state.run()
    evaluated, score = evaluate(state, state.objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "careerverse",
        "ok": ok,
        "score": score,
        "tick": state.day,
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": state.events[-300:],
        "state": {"day": state.day, "done": state.done, "quality": state.quality},
        "stats": {
            "tasks": len(state.tasks),
            "shipped": len(state.done),
            "days_used": state.day,
            "days_budget": state.days,
            "review_ratio": round(state.review_ratio, 3),
            "blocked_events": sum(1 for e in state.events if e["type"] == "blocked"),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({"days": 14, "capacity": 1.5,
                        "objectives": [{"type": "delivered"}, {"type": "deadline"},
                                       {"type": "quality", "min": 0.8}]})

    def program(sprint):
        sprint.plan(["schema", "api", "tests", "ui", "docs"])
        sprint.set_review_ratio(0.3)
        sprint.run()

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
