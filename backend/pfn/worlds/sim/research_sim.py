"""Research Reactor - an experiment-design laboratory.

Stdlib only: this file is copied verbatim into the execution sandbox.

The learner designs and analyses an A/B test.  The world generates the data from
a seeded process with a *true* effect that the learner cannot read.  The learner
chooses a sample size, pulls samples, computes the statistic themselves and
submits a decision.  The world recomputes the statistic independently, so a
claimed p-value that does not match the data is caught.

Learner contract::

    def program(lab):
        a = lab.sample("A", 400)
        b = lab.sample("B", 400)
        effect = mean(b) - mean(a)
        p = welch_p(a, b)          # written by the learner
        lab.report(decision=abs(effect) > 0.02 and p < 0.05,
                   effect=effect, p_value=p)
"""

from __future__ import annotations

import json
import math
import random
import statistics


class BudgetExceeded(Exception):
    """Raised when the lab exceeds its sampling or compute budget."""


class Lab:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.seed = int(config.get("seed", 17))
        self.true_effect = float(config.get("true_effect", 0.0))
        self.baseline = float(config.get("baseline", 0.20))
        self.noise = float(config.get("noise", 1.0))
        self.max_samples = int(config.get("max_samples", 20_000))
        self.max_ticks = int(config.get("max_ticks", 200_000))
        self.ticks = 0
        self.drawn = 0
        self.peeks = 0
        self.draws: list[dict] = []
        self.arms: dict[str, list[float]] = {}
        self.report_data: dict | None = None
        self.stop_reason = ""
        self.objectives: list[dict] = list(config.get("objectives") or [
            {"type": "decision"}, {"type": "power", "min_n": 300}, {"type": "no_peeking"},
        ])

    # ---------------------------------------------------------------- sampling
    def sample(self, arm: str, count: int) -> list[float]:
        """Draw ``count`` observations for ``arm`` ('A' or 'B') from the process."""
        if arm not in ("A", "B"):
            raise ValueError("arm must be 'A' or 'B'")
        count = int(count)
        if count <= 0:
            raise ValueError("count must be positive")
        if self.drawn + count > self.max_samples:
            self.stop_reason = "sample budget exhausted"
            raise BudgetExceeded(f"asked for {count}, only {self.max_samples - self.drawn} left")
        self.ticks += count
        if self.ticks > self.max_ticks:
            self.stop_reason = "compute budget exhausted"
            raise BudgetExceeded(f"used {self.ticks} ticks, budget is {self.max_ticks}")
        rng = random.Random(f"{self.seed}-{arm}-{self.drawn}-{count}")
        shift = self.true_effect if arm == "B" else 0.0
        values = []
        for _ in range(count):
            uniform = rng.random()
            bernoulli = 1.0 if uniform < (self.baseline + shift) else 0.0
            values.append(bernoulli + rng.gauss(0.0, 0.05 * self.noise))
        self.drawn += count
        self.arms.setdefault(arm, []).extend(values)
        self.draws.append({"arm": arm, "count": count, "total": self.drawn})
        if len(self.draws) > 2:
            self.peeks += 1
        return values

    # ----------------------------------------------------------------- helpers
    def mean(self, values: list[float]) -> float:
        return statistics.fmean(values)

    def welch_p(self, a: list[float], b: list[float]) -> float:
        """Welch's t-test two-sided p-value, computed with the normal approximation."""
        if len(a) < 2 or len(b) < 2:
            return 1.0
        ma, mb = statistics.fmean(a), statistics.fmean(b)
        va, vb = statistics.variance(a), statistics.variance(b)
        se = math.sqrt(va / len(a) + vb / len(b))
        if se == 0:
            return 1.0
        t = (mb - ma) / se
        return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t) / math.sqrt(2.0))))

    # ------------------------------------------------------------------ submit
    def report(self, decision: bool, effect: float, p_value: float,
               n_per_arm: int | None = None) -> dict:
        self.report_data = {
            "decision": bool(decision),
            "effect": float(effect),
            "p_value": float(p_value),
            "n_per_arm": int(n_per_arm or (self.drawn // 2)),
        }
        return dict(self.report_data)

    # ------------------------------------------------------------------ truths
    def truth(self) -> dict:
        return {"true_effect": self.true_effect, "baseline": self.baseline}


def build(config: dict):
    lab = Lab(config)
    return lab, lab


def evaluate(lab: Lab, objectives: list[dict]) -> tuple[list[dict], float]:
    report = lab.report_data or {}
    results: list[dict] = []
    truth_effect = lab.true_effect
    for objective in objectives:
        kind = objective.get("type", "decision")
        if kind == "decision":
            expected = abs(truth_effect) > 1e-9
            ok = bool(report.get("decision")) == expected
            results.append({"type": kind, "ok": ok,
                            "detail": f"reported {report.get('decision')}, truth is {expected} "
                                      f"(true effect {truth_effect})"})
        elif kind == "effect":
            tolerance = float(objective.get("tolerance", 0.05))
            actual = float(report.get("effect", 0.0))
            ok = abs(actual - truth_effect) <= tolerance
            results.append({"type": kind, "ok": ok,
                            "detail": f"reported effect {actual:.4f}, true {truth_effect:.4f} (±{tolerance})"})
        elif kind == "p_value":
            # Honesty check: recompute the statistic from the data the learner
            # actually drew and compare it with the claimed p-value.
            tolerance = float(objective.get("tolerance", 0.03))
            claimed = float(report.get("p_value", -1.0))
            recomputed = lab.welch_p(lab.arms.get("A", []), lab.arms.get("B", []))
            ok = 0.0 <= claimed <= 1.0 and abs(claimed - recomputed) <= tolerance
            results.append({"type": kind, "ok": ok,
                            "detail": f"claimed p={claimed:.4f}, recomputed from your samples "
                                      f"p={recomputed:.4f} (±{tolerance})"})
        elif kind == "power":
            minimum = int(objective.get("min_n", 300))
            ok = int(report.get("n_per_arm", 0)) >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"n={report.get('n_per_arm', 0)} per arm (min {minimum})"})
        elif kind == "no_peeking":
            limit = int(objective.get("max_draws", 2))
            ok = len(lab.draws) <= limit
            results.append({"type": kind, "ok": ok,
                            "detail": f"{len(lab.draws)} sampling calls (max {limit})"})
        elif kind == "budget":
            ok = lab.stop_reason == ""
            results.append({"type": kind, "ok": ok, "detail": lab.stop_reason or "within budget"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Lab, state: Lab) -> dict:
    evaluated, score = evaluate(state, state.objectives)
    ok = all(item["ok"] for item in evaluated)
    report = state.report_data or {}
    return {
        "world": "research_reactor",
        "ok": ok,
        "score": score,
        "tick": state.ticks,
        "stop_reason": state.stop_reason or ("completed" if ok else "objectives_unmet"),
        "objectives": evaluated,
        "events": [{"tick": i, "type": "sample", **draw} for i, draw in enumerate(state.draws)],
        "state": {
            "report": report,
            "draws": state.draws,
            "samples_used": state.drawn,
        },
        "stats": {
            "samples": state.drawn,
            "sample_budget": state.max_samples,
            "draw_calls": len(state.draws),
            "peeks": state.peeks,
            "true_effect": state.true_effect,
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({
        "seed": 3,
        "true_effect": 0.08,
        "max_samples": 5000,
        "objectives": [{"type": "decision"}, {"type": "effect", "tolerance": 0.05},
                       {"type": "power", "min_n": 300}, {"type": "no_peeking", "max_draws": 2}],
    })

    def program(lab):
        a = lab.sample("A", 900)
        b = lab.sample("B", 900)
        effect = lab.mean(b) - lab.mean(a)
        p = lab.welch_p(a, b)
        lab.report(decision=p < 0.05 and effect > 0, effect=effect, p_value=p, n_per_arm=900)

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
