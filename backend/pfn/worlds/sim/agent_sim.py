"""Agent Planet - a tool-calling agent environment.

Stdlib only: this file is copied verbatim into the execution sandbox.

The learner writes an agent loop: read the goal, call tools, submit an answer.
The world charges for every tool call and every tick, so a wasteful loop is
visible in the score.  Tool results are computed here from real state.

Learner contract::

    def program(agent):
        goal = agent.goal()
        for _ in range(agent.max_steps()):
            if agent.done():
                break
            agent.think()                    # costs one tick
            found = agent.search(goal["term"])
            agent.answer(found["value"])
"""

from __future__ import annotations

import json
import random

TOOL_COST = {"search": 2, "lookup": 1, "calculate": 1, "translate": 2, "fetch": 3}


class BudgetExceeded(Exception):
    """Raised when the agent spends more than its tool or step budget."""


class Agent:
    def __init__(self, tasks: list[dict], knowledge: dict, max_steps: int, budget: int,
                 objectives: list[dict]) -> None:
        self.tasks = tasks
        self.knowledge = knowledge
        self.max_steps = max_steps
        self.budget = budget
        self.objectives = objectives
        self.index = 0
        self.steps = 0
        self.spend = 0
        self.answers: list[dict] = []
        self.trace: list[dict] = []
        self.stop_reason = ""

    # ------------------------------------------------------------------ senses
    def goal(self) -> dict | None:
        if self.index >= len(self.tasks):
            return None
        task = dict(self.tasks[self.index])
        task.pop("expected", None)
        return task

    def done(self) -> bool:
        return self.index >= len(self.tasks)

    def tasks_left(self) -> int:
        return max(0, len(self.tasks) - self.index)

    def steps_left(self) -> int:
        return max(0, self.max_steps - self.steps)

    def budget_left(self) -> int:
        return max(0, self.budget - self.spend)

    # ------------------------------------------------------------------- tools
    def _charge(self, tool: str) -> None:
        cost = TOOL_COST.get(tool, 1)
        if self.spend + cost > self.budget:
            self.stop_reason = "tool budget exhausted"
            raise BudgetExceeded(f"{tool} costs {cost}, only {self.budget_left()} left")
        self.spend += cost
        self.steps += 1
        if self.steps > self.max_steps:
            self.stop_reason = "step budget exhausted"
            raise BudgetExceeded(f"used {self.steps} steps, budget is {self.max_steps}")
        self.trace.append({"tick": self.steps, "type": "tool", "tool": tool})

    def think(self) -> None:
        """One reasoning step: cheap, but it still costs a tick."""
        self._charge("think")

    def search(self, term: str) -> dict:
        self._charge("search")
        hits = {key: value for key, value in self.knowledge.items() if term.lower() in key.lower()}
        self.trace[-1]["hits"] = len(hits)
        return {"hits": hits, "count": len(hits)}

    def lookup(self, key: str):
        self._charge("lookup")
        self.trace[-1]["key"] = key
        return self.knowledge.get(key)

    def calculate(self, expression: str, allowed: str = "0123456789+-*/(). ") -> float:
        self._charge("calculate")
        if any(char not in allowed for char in expression):
            raise ValueError(f"expression contains a character outside the safe set: {expression!r}")
        self.trace[-1]["expression"] = expression
        return float(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307 - safe set enforced

    def translate(self, text: str) -> str:
        self._charge("translate")
        table = dict(self.knowledge.get("__glossary__", {}))
        self.trace[-1]["length"] = len(text)
        return " ".join(table.get(word, word) for word in text.split())

    def fetch(self, key: str) -> str:
        self._charge("fetch")
        notes = self.knowledge.get("__notes__", {})
        return str(notes.get(key, ""))

    # ------------------------------------------------------------------ action
    def answer(self, value) -> dict:
        """Submit an answer for the current task; the world grades it."""
        task = self.tasks[self.index] if self.index < len(self.tasks) else {}
        expected = task.get("expected")
        correct = _matches(value, expected)
        record = {
            "task": task.get("prompt", f"task {self.index}"),
            "submitted": value,
            "expected": expected,
            "correct": correct,
        }
        self.answers.append(record)
        self.trace.append({"tick": self.steps, "type": "answer", "correct": correct})
        self.index += 1
        return {"correct": correct, "remaining": self.tasks_left(), "expected": expected}

    # ------------------------------------------------------------------ report
    def log(self, kind: str, **payload) -> None:
        self.trace.append({"tick": self.steps, "type": kind, **payload})


def _matches(value, expected) -> bool:
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        try:
            return abs(float(value) - float(expected)) < 1e-6
        except (TypeError, ValueError):
            return False
    if isinstance(expected, str):
        return str(value).strip().lower() == expected.strip().lower()
    return value == expected


def build(config: dict):
    seed = int(config.get("seed", 4))
    rng = random.Random(seed)
    knowledge: dict = dict(config.get("knowledge") or {})
    if not knowledge:
        words = ["gravity", "orbit", "thrust", "pressure", "voltage", "entropy"]
        knowledge = {word: round(rng.uniform(1, 100), 2) for word in words}
        knowledge["python"] = 1991
        knowledge["pi"] = 3.14159
    tasks = list(config.get("tasks") or [])
    if not tasks:
        keys = [k for k in knowledge if not k.startswith("__")]
        tasks = [
            {"prompt": f"look up {keys[0]}", "term": keys[0], "expected": knowledge[keys[0]]},
            {"prompt": "compute 12 * (3 + 4)", "expression": "12 * (3 + 4)", "expected": 84.0},
        ]
    agent = Agent(
        tasks,
        knowledge,
        max_steps=int(config.get("max_steps", 200)),
        budget=int(config.get("budget", 120)),
        objectives=list(config.get("objectives") or [{"type": "solved"}, {"type": "budget"}]),
    )
    agent.log("init", tasks=len(tasks), budget=agent.budget)
    return agent, agent


def evaluate(agent: Agent, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "solved")
        if kind == "solved":
            needed = int(objective.get("count", len(agent.tasks)))
            solved = sum(1 for a in agent.answers if a["correct"])
            ok = solved >= needed and agent.tasks_left() == 0
            results.append({"type": kind, "ok": ok,
                            "detail": f"{solved} correct answers out of {len(agent.tasks)}"})
        elif kind == "budget":
            limit = int(objective.get("max", agent.budget))
            ok = agent.spend <= limit
            results.append({"type": kind, "ok": ok,
                            "detail": f"spent {agent.spend} of {limit} tool credits"})
        elif kind == "steps":
            limit = int(objective.get("max", agent.max_steps))
            ok = agent.steps <= limit
            results.append({"type": kind, "ok": ok, "detail": f"used {agent.steps} steps (max {limit})"})
        elif kind == "no_wasted_calls":
            limit = int(objective.get("max_per_task", 4))
            per_task: dict[int, int] = {}
            for entry in agent.trace:
                if entry["type"] == "tool":
                    per_task[entry["tick"] // 1000] = per_task.get(entry["tick"] // 1000, 0) + 1
            ok = len(agent.trace) <= limit * max(1, len(agent.tasks))
            results.append({"type": kind, "ok": ok,
                            "detail": f"{len(agent.trace)} trace entries for {len(agent.tasks)} tasks"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Agent, state: Agent) -> dict:
    evaluated, score = evaluate(state, state.objectives)
    solved = sum(1 for a in state.answers if a["correct"])
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "agent_planet",
        "ok": ok,
        "score": score,
        "tick": state.steps,
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": state.trace[-300:],
        "answers": state.answers[-20:],
        "stats": {
            "tasks": len(state.tasks),
            "solved": solved,
            "remaining": state.tasks_left(),
            "credits_spent": state.spend,
            "credits_left": state.budget_left(),
            "steps": state.steps,
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({
        "knowledge": {"gravity": 9.81, "orbit": 7.66, "python": 1991},
        "tasks": [
            {"prompt": "what is gravity?", "expected": 9.81},
            {"prompt": "what year is python?", "expected": 1991},
        ],
        "objectives": [{"type": "solved"}, {"type": "budget", "max": 40}],
    })

    def program(agent):
        while not agent.done():
            task = agent.goal()
            agent.think()
            value = agent.lookup(task["prompt"].split()[-1].strip("?"))
            if value is None:
                for key in agent.knowledge:
                    if key in task["prompt"]:
                        value = agent.lookup(key)
                        break
            agent.answer(value)

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
