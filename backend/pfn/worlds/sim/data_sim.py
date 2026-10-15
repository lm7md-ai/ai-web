"""Data Empire - a streaming data pipeline arena.

Stdlib only: this file is copied verbatim into the execution sandbox.

A generator pushes records through the learner's pipeline.  The learner writes
``program(pipeline)`` and registers a ``transform`` (and optionally a
``filter`` and an ``aggregate``).  Nothing about the result is pre-baked: the
world computes the real aggregates from the records the learner emitted.

Learner contract::

    def program(pipeline):
        def transform(record):
            record["total"] = record["qty"] * record["price"]
            return record
        pipeline.set_transform(transform)
        pipeline.run()
"""

from __future__ import annotations

import json
import random

MAX_ROWS = 200_000


class BudgetExceeded(Exception):
    """Raised when the pipeline exceeds its row or tick budget."""


class Pipeline:
    def __init__(self, rows: list[dict], max_ticks: int, max_rows: int) -> None:
        self.rows = rows
        self.max_ticks = max_ticks
        self.max_rows = max_rows
        self.ticks = 0
        self.emitted: list[dict] = []
        self.errors: list[dict] = []
        self.dropped: list[dict] = []
        self.transform_fn = None
        self.filter_fn = None
        self.stop_reason = ""
        self.objectives: list[dict] = []
        self.events: list[dict] = []

    # ------------------------------------------------------------ registration
    def set_transform(self, fn) -> None:
        self.transform_fn = fn

    def set_filter(self, fn) -> None:
        self.filter_fn = fn

    # -------------------------------------------------------------------- view
    def source(self) -> list[dict]:
        """A defensive copy of the raw records (the learner may inspect them)."""
        return [dict(row) for row in self.rows]

    def head(self, count: int = 5) -> list[dict]:
        return [dict(row) for row in self.rows[:count]]

    def size(self) -> int:
        return len(self.rows)

    # -------------------------------------------------------------------- run
    def run(self, limit: int | None = None) -> int:
        """Push every source row through filter -> transform, recording failures."""
        count = 0
        for index, row in enumerate(self.rows):
            if limit is not None and count >= limit:
                break
            self.tick()
            record = dict(row)
            try:
                if self.filter_fn is not None and not bool(self.filter_fn(record)):
                    self.dropped.append({"index": index, "id": record.get("id")})
                    continue
                if self.transform_fn is not None:
                    record = self.transform_fn(record)
                    if record is None:
                        raise ValueError("transform returned None")
            except Exception as error:  # noqa: BLE001 - a bad row is data, not a crash
                self.errors.append({"index": index, "error": f"{type(error).__name__}: {error}"})
                continue
            self.emitted.append(record)
            count += 1
        return count

    def tick(self, steps: int = 1) -> None:
        self.ticks += steps
        if self.ticks > self.max_ticks:
            self.stop_reason = "tick budget exhausted"
            raise BudgetExceeded(f"used {self.ticks} ticks, budget is {self.max_ticks}")

    # ------------------------------------------------------------------ report
    def sum(self, field: str) -> float:
        return float(sum(float(row.get(field, 0) or 0) for row in self.emitted))

    def count(self) -> int:
        return len(self.emitted)

    def groups(self, field: str) -> dict:
        out: dict = {}
        for row in self.emitted:
            out.setdefault(row.get(field), 0)
            out[row.get(field)] += 1
        return out

    def log(self, kind: str, **payload) -> None:
        self.events.append({"tick": self.ticks, "type": kind, **payload})


def build(config: dict):
    seed = int(config.get("seed", 11))
    count = min(int(config.get("rows", 200)), MAX_ROWS)
    rng = random.Random(seed)
    regions = list(config.get("regions") or ["north", "south", "east", "west"])
    rows = []
    for i in range(count):
        qty = rng.randint(0, 12)
        rows.append({
            "id": i + 1,
            "region": rng.choice(regions),
            "qty": qty,
            "price": round(rng.uniform(1.0, 40.0), 2),
            "discount": rng.choice([0.0, 0.0, 0.1, 0.25]),
            "note": "" if rng.random() < 0.8 else rng.choice(["damaged", "gift", None]),
        })
    pipeline = Pipeline(rows, max_ticks=int(config.get("max_ticks", 100_000)), max_rows=MAX_ROWS)
    pipeline.events = [{"tick": 0, "type": "init", "rows": len(rows)}]
    pipeline.objectives = list(config.get("objectives") or [{"type": "no_errors"}])
    return pipeline, pipeline


def evaluate(pipe: Pipeline, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "rows")
        if kind == "rows":
            expected = objective.get("count")
            if expected is None:
                expected = objective.get("min", len(pipe.rows))
            ok = pipe.count() >= int(expected)
            results.append({"type": kind, "ok": ok,
                            "detail": f"emitted {pipe.count()} rows, expected >= {expected}"})
        elif kind == "no_errors":
            ok = not pipe.errors
            results.append({"type": kind, "ok": ok,
                            "detail": "no row failed" if ok else f"{len(pipe.errors)} rows failed: "
                                                                 f"{pipe.errors[0]}"})
        elif kind == "sum":
            field = objective.get("field", "total")
            target = float(objective.get("equals", 0))
            tolerance = float(objective.get("tolerance", 0.01))
            actual = pipe.sum(field)
            ok = abs(actual - target) <= tolerance
            results.append({"type": kind, "ok": ok,
                            "detail": f"sum({field}) = {round(actual, 3)}, expected {target} ±{tolerance}"})
        elif kind == "field_exists":
            field = objective.get("field", "")
            ok = bool(pipe.emitted) and all(field in row for row in pipe.emitted)
            missing = sum(1 for row in pipe.emitted if field not in row)
            results.append({"type": kind, "ok": ok, "detail": f"missing '{field}' in {missing} rows"})
        elif kind == "filtered":
            ok = bool(pipe.dropped)
            results.append({"type": kind, "ok": ok,
                            "detail": f"filtered out {len(pipe.dropped)} rows"})
        elif kind == "budget":
            ok = pipe.stop_reason == ""
            results.append({"type": kind, "ok": ok, "detail": pipe.stop_reason or "within budget"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Pipeline, state: Pipeline) -> dict:
    pipe = state
    objectives = list(pipe.objectives or [{"type": "no_errors"}])
    evaluated, score = evaluate(pipe, objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "data_empire",
        "ok": ok,
        "score": score,
        "tick": pipe.ticks,
        "stop_reason": pipe.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": pipe.events[-200:],
        "sample": pipe.emitted[:5],
        "stats": {
            "source_rows": len(pipe.rows),
            "emitted": pipe.count(),
            "dropped": len(pipe.dropped),
            "errors": len(pipe.errors),
            "regions": pipe.groups("region"),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({
        "seed": 5,
        "rows": 60,
        "objectives": [
            {"type": "rows", "min": 60},
            {"type": "no_errors"},
            {"type": "field_exists", "field": "total"},
        ],
    })

    def program(pipeline):
        def transform(record):
            record["total"] = round(record["qty"] * record["price"] * (1 - record["discount"]), 2)
            return record
        pipeline.set_transform(transform)
        pipeline.run()

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
