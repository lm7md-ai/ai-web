"""Model Olympics - a training and evaluation arena.

Stdlib only: this file is copied verbatim into the execution sandbox.

The learner trains a classifier in pure Python and submits predictions for a
held-out set.  The world generates the data from a seeded process, computes the
real metrics (accuracy, precision, recall, F1) and compares them with two honest
baselines: majority class and a linear rule with the true weights.

Learner contract::

    def program(arena):
        rows = arena.train_set()
        weights, bias = train(rows, epochs=200, lr=0.1)
        arena.submit([1 if dot(x, weights) + bias > 0 else 0 for x in arena.test_features()])
"""

from __future__ import annotations

import json
import random
import time


class BudgetExceeded(Exception):
    """Raised when training exceeds the compute budget."""


class Arena:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.seed = int(config.get("seed", 9))
        self.features = int(config.get("features", 3))
        self.train_n = int(config.get("train_n", 400))
        self.test_n = int(config.get("test_n", 150))
        self.noise = float(config.get("noise", 0.12))
        self.max_seconds = float(config.get("max_seconds", 10.0))
        self.started = time.perf_counter()
        self.stop_reason = ""
        self.predictions: list[int] | None = None
        self.events: list[dict] = []
        self.objectives: list[dict] = list(config.get("objectives") or [
            {"type": "accuracy", "min": 0.8}, {"type": "beat_baseline"}, {"type": "complete"},
        ])
        self._train, self._test = self._make_data()

    # ------------------------------------------------------------------- data
    def _make_data(self):
        rng = random.Random(self.seed)
        weights = [round(rng.uniform(-1.5, 1.5), 3) for _ in range(self.features)]
        bias = round(rng.uniform(-0.4, 0.4), 3)

        def row():
            x = [round(rng.uniform(-2.0, 2.0), 4) for _ in range(self.features)]
            score = sum(w * v for w, v in zip(weights, x)) + bias
            noisy = score + rng.gauss(0.0, self.noise)
            return x, (1 if noisy > 0 else 0)

        train = [row() for _ in range(self.train_n)]
        test = [row() for _ in range(self.test_n)]
        self._truth = weights, bias
        return train, test

    def train_set(self) -> list[tuple[list[float], int]]:
        return [(list(x), y) for x, y in self._train]

    def test_features(self) -> list[list[float]]:
        return [list(x) for x, _ in self._test]

    def peek_baseline(self) -> float:
        """Majority-class accuracy - the number a real model must beat."""
        labels = [y for _, y in self._train]
        majority = max(set(labels), key=labels.count)
        return round(sum(1 for y in labels if y == majority) / len(labels), 4)

    # ------------------------------------------------------------------ budget
    def tick(self, count: int = 1) -> None:
        """Declare compute work (used for the budget and for honest profiling)."""
        if time.perf_counter() - self.started > self.max_seconds:
            self.stop_reason = "compute budget exhausted"
            raise BudgetExceeded(f"training ran longer than {self.max_seconds}s")

    def elapsed(self) -> float:
        return round(time.perf_counter() - self.started, 4)

    # ------------------------------------------------------------------ submit
    def submit(self, predictions) -> dict:
        values = [int(p) for p in predictions]
        if len(values) != len(self._test):
            raise ValueError(f"expected {len(self._test)} predictions, got {len(values)}")
        if any(v not in (0, 1) for v in values):
            raise ValueError("predictions must be 0 or 1")
        self.predictions = values
        self.events.append({"tick": 0, "type": "submit", "count": len(values)})
        return self.score()

    # ------------------------------------------------------------------ metrics
    def score(self) -> dict:
        if self.predictions is None:
            return {"error": "no predictions submitted yet"}
        truth = [y for _, y in self._test]
        preds = self.predictions
        tp = sum(1 for p, t in zip(preds, truth) if p == 1 and t == 1)
        fp = sum(1 for p, t in zip(preds, truth) if p == 1 and t == 0)
        fn = sum(1 for p, t in zip(preds, truth) if p == 0 and t == 1)
        tn = sum(1 for p, t in zip(preds, truth) if p == 0 and t == 0)
        accuracy = (tp + tn) / len(truth)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        weights, bias = self._truth
        oracle = [1 if sum(w * v for w, v in zip(weights, x)) + bias > 0 else 0 for x, _ in self._test]
        ceiling = sum(1 for o, t in zip(oracle, truth) if o == t) / len(truth)
        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "majority_baseline": self.peek_baseline(),
            "bayes_ceiling": round(ceiling, 4),
        }

    def log(self, kind: str, **payload) -> None:
        self.events.append({"tick": 0, "type": kind, **payload})


def build(config: dict):
    arena = Arena(config)
    arena.events.append({"tick": 0, "type": "init", "train": arena.train_n, "test": arena.test_n})
    return arena, arena


def evaluate(arena: Arena, objectives: list[dict]) -> tuple[list[dict], float]:
    metrics = arena.score()
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "accuracy")
        if kind == "accuracy":
            minimum = float(objective.get("min", 0.8))
            actual = metrics.get("accuracy", 0.0)
            ok = actual >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"accuracy {actual} (min {minimum})"})
        elif kind == "f1":
            minimum = float(objective.get("min", 0.7))
            ok = metrics.get("f1", 0.0) >= minimum
            results.append({"type": kind, "ok": ok, "detail": f"F1 {metrics.get('f1')} (min {minimum})"})
        elif kind == "beat_baseline":
            margin = float(objective.get("margin", 0.05))
            ok = metrics.get("accuracy", 0.0) >= metrics.get("majority_baseline", 1.0) + margin
            results.append({"type": kind, "ok": ok,
                            "detail": f"accuracy {metrics.get('accuracy')} vs majority "
                                      f"{metrics.get('majority_baseline')} (+{margin} required)"})
        elif kind == "complete":
            ok = arena.predictions is not None
            results.append({"type": kind, "ok": ok,
                            "detail": "predictions submitted" if ok else "nothing was submitted"})
        elif kind == "budget":
            ok = arena.stop_reason == "" and arena.elapsed() <= arena.max_seconds
            results.append({"type": kind, "ok": ok,
                            "detail": f"{arena.elapsed()}s (budget {arena.max_seconds}s)"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Arena, state: Arena) -> dict:
    evaluated, score = evaluate(state, state.objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "model_olympics",
        "ok": ok,
        "score": score,
        "tick": int(state.elapsed() * 1000),
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": state.events[-100:],
        "metrics": state.score(),
        "stats": {
            "train_rows": state.train_n,
            "test_rows": state.test_n,
            "features": state.features,
            "seconds": state.elapsed(),
            "seconds_budget": state.max_seconds,
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({"seed": 4, "train_n": 600, "test_n": 200,
                        "objectives": [{"type": "accuracy", "min": 0.85},
                                       {"type": "beat_baseline", "margin": 0.05},
                                       {"type": "complete"}]})

    def program(arena):
        rows = arena.train_set()
        size = len(rows[0][0])
        weights = [0.0] * size
        bias = 0.0
        lr = 0.25
        for epoch in range(300):
            arena.tick()
            for x, y in rows:
                z = sum(w * v for w, v in zip(weights, x)) + bias
                p = 1.0 / (1.0 + 2.718281828459045 ** (-max(-30.0, min(30.0, z))))
                err = (y - p)
                for i in range(size):
                    weights[i] += lr * err * x[i]
                bias += lr * err
        preds = []
        for x in arena.test_features():
            z = sum(w * v for w, v in zip(weights, x)) + bias
            preds.append(1 if z > 0 else 0)
        arena.submit(preds)

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
