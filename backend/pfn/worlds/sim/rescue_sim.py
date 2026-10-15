"""Project Rescue - repair a broken codebase.

Stdlib only: this file is copied verbatim into the execution sandbox.

The world ships a small, deliberately broken codebase as *text* plus a suite of
checks per function.  The learner reads the broken source with
``repo.source(name)``, then registers a working replacement with
``repo.fix(name, fn)``.  The world runs the real checks against the learner's
callables - it never inspects the source text of the answer.

Learner contract::

    def program(repo):
        def cart_total(items):
            return sum(qty * price for qty, price in items)
        repo.fix("cart_total", cart_total)
        repo.verify()
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable


class BudgetExceeded(Exception):
    """Raised when verification exceeds the time budget."""


class Repo:
    def __init__(self, modules: list[dict], objectives: list[dict], max_seconds: float) -> None:
        self.modules = modules
        self.objectives = objectives
        self.max_seconds = max_seconds
        self.fixes: dict[str, Callable] = {}
        self.results: list[dict] = []
        self.events: list[dict] = []
        self.started = time.perf_counter()
        self.stop_reason = ""
        self.verified = False

    # ------------------------------------------------------------------ senses
    def names(self) -> list[str]:
        return [module["name"] for module in self.modules]

    def source(self, name: str) -> str:
        for module in self.modules:
            if module["name"] == name:
                return module["source"]
        raise KeyError(f"unknown module: {name}")

    def bug_hint(self, name: str) -> str:
        for module in self.modules:
            if module["name"] == name:
                return module.get("hint", "")
        raise KeyError(f"unknown module: {name}")

    def checks(self, name: str) -> list[dict]:
        for module in self.modules:
            if module["name"] == name:
                return [{"args": case["args"], "expected": case["expected"]}
                        for case in module.get("cases", [])]
        raise KeyError(f"unknown module: {name}")

    def elapsed(self) -> float:
        return time.perf_counter() - self.started

    # ------------------------------------------------------------------ action
    def fix(self, name: str, fn: Callable) -> None:
        if not callable(fn):
            raise TypeError(f"{name}: expected a function, got {type(fn).__name__}")
        if name not in self.names():
            raise KeyError(f"there is no module named {name}")
        self.fixes[name] = fn
        self.events.append({"tick": len(self.events), "type": "fix", "module": name})

    def run(self, name: str, *args: Any):
        """Call a registered fix (or, if absent, the original broken function)."""
        fn = self.fixes.get(name)
        if fn is None:
            raise KeyError(f"{name} has no registered fix yet")
        if self.elapsed() > self.max_seconds:
            self.stop_reason = "time budget exhausted"
            raise BudgetExceeded(f"used {self.elapsed():.2f}s, budget is {self.max_seconds}s")
        return fn(*args)

    def verify(self) -> list[dict]:
        """Run every check against the registered fixes and record the outcome."""
        self.results = []
        for module in self.modules:
            name = module["name"]
            fn = self.fixes.get(name)
            for index, case in enumerate(module.get("cases", [])):
                args = list(case["args"])
                expected = case["expected"]
                entry = {"module": name, "case": index, "args": _safe(args), "expected": _safe(expected)}
                if fn is None:
                    entry.update(outcome="missing", ok=False, detail="no fix registered")
                else:
                    started = time.perf_counter()
                    try:
                        actual = fn(*args)
                    except Exception as error:  # noqa: BLE001 - a failing check is data
                        entry.update(outcome="error", ok=False,
                                     detail=f"{type(error).__name__}: {error}")
                    else:
                        elapsed_ms = (time.perf_counter() - started) * 1000
                        ok = _same(actual, expected)
                        entry.update(outcome="passed" if ok else "failed", ok=ok,
                                     actual=_safe(actual),
                                     detail=f"returned {_safe(actual)!r}, expected {_safe(expected)!r}",
                                     ms=round(elapsed_ms, 3))
                self.results.append(entry)
        self.verified = True
        return self.results


def _safe(value: Any) -> Any:
    """Keep report payloads JSON-serialisable."""
    try:
        json.dumps(value)
        return value
    except TypeError:
        return repr(value)


def _same(actual: Any, expected: Any) -> bool:
    if isinstance(expected, float) or isinstance(actual, float):
        try:
            return abs(float(actual) - float(expected)) < 1e-6
        except (TypeError, ValueError):
            return False
    return actual == expected


def build(config: dict):
    modules = list(config.get("modules") or DEFAULT_MODULES)
    repo = Repo(
        modules,
        objectives=list(config.get("objectives") or [{"type": "all_checks"}, {"type": "no_regressions"}]),
        max_seconds=float(config.get("max_seconds", 20.0)),
    )
    repo.events.append({"tick": 0, "type": "init", "modules": len(modules)})
    return repo, repo


DEFAULT_MODULES = [
    {
        "name": "cart_total",
        "hint": "The loop multiplies instead of accumulating.",
        "source": 'def cart_total(items):\n    total = 0\n    for qty, price in items:\n        total = qty * price   # BUG: overwrites instead of adding\n    return total\n',
        "cases": [
            {"args": [[(2, 3.0), (1, 4.5)]], "expected": 10.5},
            {"args": [[]], "expected": 0},
            {"args": [[(3, 1.5)]], "expected": 4.5},
        ],
    },
    {
        "name": "count_words",
        "hint": "Splitting on a single space misses tabs and repeated spaces.",
        "source": 'def count_words(text):\n    return len(text.split(" "))   # BUG: counts empty tokens\n',
        "cases": [
            {"args": ["hello brave new world"], "expected": 4},
            {"args": ["  hello   world  "], "expected": 2},
            {"args": [""], "expected": 0},
        ],
    },
]


def evaluate(repo: Repo, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "all_checks")
        if kind == "all_checks":
            failed = [r for r in repo.results if not r["ok"]]
            ok = bool(repo.results) and not failed
            results.append({"type": kind, "ok": ok,
                            "detail": f"{len(repo.results) - len(failed)}/{len(repo.results)} checks passed"})
        elif kind == "module":
            name = objective.get("name", "")
            entries = [r for r in repo.results if r["module"] == name]
            ok = bool(entries) and all(r["ok"] for r in entries)
            results.append({"type": kind, "ok": ok,
                            "detail": f"{name}: {sum(1 for r in entries if r['ok'])}/{len(entries)} passed"})
        elif kind == "no_regressions":
            ok = not any(r["outcome"] == "error" for r in repo.results)
            errors = [r for r in repo.results if r["outcome"] == "error"]
            results.append({"type": kind, "ok": ok,
                            "detail": "no check raised" if ok else f"{errors[0]['detail']}"})
        elif kind == "time":
            limit = float(objective.get("max", repo.max_seconds))
            ok = repo.elapsed() <= limit
            results.append({"type": kind, "ok": ok,
                            "detail": f"{repo.elapsed():.3f}s (budget {limit}s)"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Repo, state: Repo) -> dict:
    if not state.verified:
        state.verify()
    evaluated, score = evaluate(state, state.objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "project_rescue",
        "ok": ok,
        "score": score,
        "tick": len(state.events),
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": state.events[-200:],
        "results": state.results[-60:],
        "stats": {
            "modules": len(state.modules),
            "fixed": len(state.fixes),
            "checks": len(state.results),
            "passed": sum(1 for r in state.results if r["ok"]),
            "elapsed_s": round(state.elapsed(), 3),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({"modules": DEFAULT_MODULES,
                        "objectives": [{"type": "all_checks"}, {"type": "time", "max": 5}]})

    def program(repo):
        def cart_total(items):
            return sum(qty * price for qty, price in items)
        def count_words(text):
            return len(text.split())
        repo.fix("cart_total", cart_total)
        repo.fix("count_words", count_words)
        repo.verify()

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:1000])
