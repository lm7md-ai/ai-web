"""Algorithm Gladiators - a comparison-budget sorting/search arena.

Stdlib only: this file is copied verbatim into the execution sandbox.

The learner is given an array they may not index-compare directly: every
comparison must go through ``arena.compare(i, j)`` and every mutation through
``arena.swap(i, j)``.  Both are counted, so the score reflects the real cost of
the algorithm, not a keyword match.

Learner contract::

    def program(arena):
        n = arena.size()
        for i in range(1, n):
            j = i
            while j > 0 and arena.compare(j - 1, j) > 0:
                arena.swap(j - 1, j)
                j -= 1
"""

from __future__ import annotations

import json
import random

MAX_OPS = 4_000_000


class BudgetExceeded(Exception):
    """Raised when the algorithm spends more operations than the arena allows."""


class StepLimit(Exception):
    """Raised when the tick budget of the arena is exhausted."""


class Arena:
    def __init__(self, values: list[int], max_ops: int, max_ticks: int, seed: int) -> None:
        self._values = list(values)
        self.max_ops = max_ops
        self.max_ticks = max_ticks
        self.seed = seed
        self.comparisons = 0
        self.swaps = 0
        self.ticks = 0
        self.events: list[dict] = []
        self.stop_reason = ""
        self.objectives: list[dict] = []
        self.original: list[int] = []

    # ------------------------------------------------------------- inspection
    def size(self) -> int:
        return len(self._values)

    def get(self, index: int) -> int:
        """Read a cell. Reading is free, but it does not tell you the order."""
        return self._values[index]

    def snapshot(self) -> list[int]:
        return list(self._values)

    # -------------------------------------------------------------- mutations
    def compare(self, i: int, j: int) -> int:
        """Return -1/0/1 comparing cells i and j. This is the counted operation."""
        self._spend()
        self.comparisons += 1
        a, b = self._values[i], self._values[j]
        return (a > b) - (a < b)

    def swap(self, i: int, j: int) -> None:
        self._spend()
        if i == j:
            return
        self._values[i], self._values[j] = self._values[j], self._values[i]
        self.swaps += 1

    def write(self, index: int, value: int) -> None:
        self._spend()
        self._values[index] = value

    # ------------------------------------------------------------------ clock
    def tick(self, steps: int = 1) -> None:
        for _ in range(steps):
            self._spend()
            self.ticks += 1

    def _spend(self) -> None:
        if self.comparisons + self.swaps >= self.max_ops:
            self.stop_reason = "operation budget exhausted"
            raise BudgetExceeded(
                f"used {self.comparisons + self.swaps} operations, budget is {self.max_ops}"
            )
        if self.ticks >= self.max_ticks:
            self.stop_reason = "tick budget exhausted"
            raise StepLimit(f"used {self.ticks} ticks, budget is {self.max_ticks}")

    # ------------------------------------------------------------------ state
    def is_sorted(self) -> bool:
        return all(a <= b for a, b in zip(self._values, self._values[1:]))

    def sorted_positions(self) -> int:
        return sum(1 for a, b in zip(self._values, self._values[1:]) if a <= b)

    def inversions(self) -> int:
        total = 0
        for i, a in enumerate(self._values):
            for b in self._values[i + 1:]:
                if a > b:
                    total += 1
        return total

    def log(self, kind: str, **payload) -> None:
        self.events.append({"tick": self.ticks, "type": kind, **payload})


def build(config: dict):
    seed = int(config.get("seed", 7))
    size = int(config.get("size", 40))
    rng = random.Random(seed)

    shape = config.get("shape", "random")
    if shape == "random":
        values = [rng.randint(0, 999) for _ in range(size)]
    elif shape == "sorted":
        values = sorted(rng.randint(0, 999) for _ in range(size))
    elif shape == "reversed":
        values = sorted((rng.randint(0, 999) for _ in range(size)), reverse=True)
    elif shape == "nearly":
        values = sorted(rng.randint(0, 999) for _ in range(size))
        for _ in range(max(1, size // 10)):
            i, j = rng.randrange(size), rng.randrange(size)
            values[i], values[j] = values[j], values[i]
    elif shape == "few_unique":
        pool = [rng.randint(0, 99) for _ in range(max(2, size // 8))]
        values = [rng.choice(pool) for _ in range(size)]
    else:
        values = list(config.get("values") or [rng.randint(0, 999) for _ in range(size)])

    arena = Arena(
        values,
        max_ops=int(config.get("max_ops", min(MAX_OPS, max(10_000, size * size * 4)))),
        max_ticks=int(config.get("max_ticks", 200_000)),
        seed=seed,
    )
    arena.original = list(values)
    arena.objectives = list(config.get("objectives") or [{"type": "sorted"}, {"type": "no_budget_breach"}])
    arena.log("init", size=len(values), shape=shape, ops_budget=arena.max_ops)
    return arena, arena


def evaluate(arena: Arena, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "sorted")
        if kind == "sorted":
            ok = arena.is_sorted()
            results.append({
                "type": kind,
                "ok": ok,
                "detail": f"{arena.sorted_positions()}/{max(1, arena.size() - 1)} adjacent pairs ordered",
            })
        elif kind == "comparisons":
            limit = int(objective.get("max", arena.max_ops))
            ok = arena.comparisons <= limit
            results.append({"type": kind, "ok": ok,
                            "detail": f"{arena.comparisons} comparisons (budget {limit})"})
        elif kind == "ops":
            limit = int(objective.get("max", arena.max_ops))
            used = arena.comparisons + arena.swaps
            ok = used <= limit
            results.append({"type": kind, "ok": ok, "detail": f"{used} operations (budget {limit})"})
        elif kind == "swaps":
            limit = int(objective.get("max", arena.max_ops))
            ok = arena.swaps <= limit
            results.append({"type": kind, "ok": ok, "detail": f"{arena.swaps} swaps (budget {limit})"})
        elif kind == "preserves_values":
            ok = sorted(arena.snapshot()) == sorted(arena.original)
            results.append({"type": kind, "ok": ok,
                            "detail": "multiset of values unchanged" if ok else "values were lost or invented"})
        elif kind == "no_budget_breach":
            ok = arena.stop_reason == ""
            results.append({"type": kind, "ok": ok, "detail": arena.stop_reason or "within budget"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Arena, state: Arena) -> dict:
    arena = state
    objectives = list(arena.objectives or [{"type": "sorted"}, {"type": "no_budget_breach"}])
    evaluated, score = evaluate(arena, objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "algorithm_gladiators",
        "ok": ok,
        "score": score,
        "tick": arena.ticks,
        "stop_reason": arena.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": arena.events[-400:],
        "head": arena.snapshot()[:24],
        "stats": {
            "size": arena.size(),
            "comparisons": arena.comparisons,
            "swaps": arena.swaps,
            "ops": arena.comparisons + arena.swaps,
            "inversions_left": arena.inversions(),
            "ops_budget": arena.max_ops,
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    demo = {
        "seed": 3,
        "size": 30,
        "shape": "random",
        "max_ops": 20_000,
        "objectives": [{"type": "sorted"}, {"type": "ops", "max": 5000}],
    }
    api, world = build(demo)

    def insertion(arena):
        for i in range(1, arena.size()):
            j = i
            while j > 0 and arena.compare(j - 1, j) > 0:
                arena.swap(j - 1, j)
                j -= 1

    try:
        insertion(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
