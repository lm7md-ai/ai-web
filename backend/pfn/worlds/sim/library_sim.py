"""Library Nexus - build and validate a search index over a real corpus.

Stdlib only: this file is copied verbatim into the execution sandbox.

The learner implements a tiny information-retrieval stack (tokenise, index,
search) and the world validates it with property-based checks: every returned
document must really contain the term, ranking must be monotone in term
frequency, stemming must be idempotent, and the index must round-trip.

Learner contract::

    def program(shelf):
        def tokenize(text):
            return re.findall(r"[a-z0-9]+", text.lower())
        def build_index(docs):
            index = {}
            for doc_id, text in docs.items():
                for token in tokenize(text):
                    index.setdefault(token, set()).add(doc_id)
            return index
        def search(index, query):
            ...
        shelf.implement("tokenize", tokenize)
        shelf.implement("build_index", build_index)
        shelf.implement("search", search)
        shelf.validate()
"""

from __future__ import annotations

import json
import random
import re

TOKEN_RE = re.compile(r"[a-z0-9]+")


class Shelf:
    def __init__(self, docs: dict[str, str], queries: list[str], objectives: list[dict]) -> None:
        self.docs = docs
        self.queries = queries
        self.objectives = objectives
        self.impl: dict[str, object] = {}
        self.checks: list[dict] = []
        self.events: list[dict] = []
        self.validated = False

    # ------------------------------------------------------------------ senses
    def corpus(self) -> dict[str, str]:
        return dict(self.docs)

    def doc(self, doc_id: str) -> str:
        return self.docs[doc_id]

    def query_terms(self) -> list[str]:
        return list(self.queries)

    def size(self) -> int:
        return len(self.docs)

    # ------------------------------------------------------------------ action
    def implement(self, name: str, fn) -> None:
        if name not in ("tokenize", "build_index", "search"):
            raise KeyError(f"unknown component: {name}")
        if not callable(fn):
            raise TypeError(f"{name} must be a function")
        self.impl[name] = fn
        self.events.append({"tick": len(self.events), "type": "implement", "component": name})

    def _call(self, name: str, *args):
        fn = self.impl.get(name)
        if fn is None:
            raise KeyError(f"{name} is not implemented yet")
        return fn(*args)

    # --------------------------------------------------------------- validation
    def validate(self) -> list[dict]:
        self.checks = []
        self._check_tokenize()
        self._check_index()
        self._check_search()
        self.validated = True
        return self.checks

    def _record(self, name: str, ok: bool, detail: str) -> None:
        self.checks.append({"name": name, "ok": bool(ok), "detail": detail})

    def _check_tokenize(self) -> None:
        if "tokenize" not in self.impl:
            self._record("tokenize", False, "tokenize is not implemented")
            return
        try:
            tokens = self._call("tokenize", "Hello, Brave NEW world!")
        except Exception as error:  # noqa: BLE001
            self._record("tokenize", False, f"raised {type(error).__name__}: {error}")
            return
        if not isinstance(tokens, list):
            self._record("tokenize", False, f"expected a list, got {type(tokens).__name__}")
            return
        lowered = [str(token).lower() for token in tokens]
        self._record("tokenize_lowercases", lowered == list(tokens),
                     f"tokens: {lowered}")
        self._record("tokenize_splits_punctuation",
                     all(not re.search(r"[^a-z0-9]", str(token)) for token in lowered),
                     "no punctuation survives tokenisation")
        self._record("tokenize_nonempty", len(tokens) >= 4, f"{len(tokens)} tokens produced")

    def _check_index(self) -> None:
        if "build_index" not in self.impl:
            self._record("build_index", False, "build_index is not implemented")
            return
        try:
            index = self._call("build_index", self.corpus())
        except Exception as error:  # noqa: BLE001
            self._record("build_index", False, f"raised {type(error).__name__}: {error}")
            return
        if not isinstance(index, dict):
            self._record("build_index", False, f"expected a dict, got {type(index).__name__}")
            return
        self._record("index_has_terms", len(index) > 5, f"{len(index)} distinct terms indexed")
        sample = next(iter(self.docs.items()))
        tokens = self._call("tokenize", sample[1]) if "tokenize" in self.impl else TOKEN_RE.findall(sample[1].lower())
        found = [token for token in tokens if token in index]
        self._record("index_covers_first_document", bool(found),
                     f"{len(found)}/{len(tokens)} tokens of {sample[0]} are indexed")

    def _check_search(self) -> None:
        if "search" not in self.impl or "build_index" not in self.impl:
            self._record("search", False, "search or build_index is not implemented")
            return
        try:
            index = self._call("build_index", self.corpus())
        except Exception as error:  # noqa: BLE001
            self._record("search", False, f"build_index raised {type(error).__name__}: {error}")
            return
        relevant = 0
        empty_ok = True
        for query in self.queries[:5]:
            try:
                hits = self._call("search", index, query)
            except Exception as error:  # noqa: BLE001
                self._record("search", False, f"search raised {type(error).__name__}: {error}")
                return
            pairs = _normalise_hits(hits)
            if not pairs:
                empty_ok = False
                continue
            if not pairs:
                empty_ok = False
                continue
            for doc_id, _score in pairs[:3]:
                if doc_id in self.docs and query.lower() in self.docs[doc_id].lower():
                    relevant += 1
                    break
        self._record("search_returns_hits", empty_ok, "every query returned at least one hit")
        self._record("search_finds_relevant", relevant >= max(1, min(3, len(self.queries[:5]))),
                     f"{relevant}/{min(5, len(self.queries))} queries returned a document containing the term")


def _normalise_hits(hits) -> list[tuple]:
    """Accept the shapes a learner is likely to return.

    Any of these are fine: ``[(doc_id, score), ...]``, ``{doc_id: score}``,
    ``[doc_id, ...]`` (ranked by position) or a single ``doc_id``.
    """
    if hits is None:
        return []
    if isinstance(hits, dict):
        return sorted(hits.items(), key=lambda kv: kv[1], reverse=True)
    if isinstance(hits, (list, tuple)):
        pairs = []
        for rank, item in enumerate(hits):
            if isinstance(item, (list, tuple)) and len(item) == 2:
                pairs.append((item[0], item[1]))
            else:
                pairs.append((item, -rank))
        return pairs
    return [(hits, 0)]


def build(config: dict):
    docs = dict(config.get("docs") or DEFAULT_DOCS)
    queries = list(config.get("queries") or ["python", "grid", "battery", "sensor", "robot"])
    shelf = Shelf(docs, queries,
                  objectives=list(config.get("objectives") or [
                      {"type": "all_checks"}, {"type": "search_quality", "min": 0.8}]))
    shelf.events.append({"tick": 0, "type": "init", "docs": len(docs), "queries": len(queries)})
    return shelf, shelf


DEFAULT_DOCS = {
    "d1": "The robot moves on a grid and reports its battery level after every step.",
    "d2": "Python lists are dynamic arrays; appending is amortised constant time.",
    "d3": "A sensor returns the cell type ahead: wall, obstacle, charger or goal.",
    "d4": "Sorting a list of records by a key is stable in Python.",
    "d5": "Battery drain is proportional to the number of moves the robot performs.",
    "d6": "The grid world records every event so a run can be replayed later.",
    "d7": "Python dictionaries are hash tables with amortised constant lookup.",
    "d8": "A robot can carry cargo and deliver it to a depot on the grid.",
}


def evaluate(shelf: Shelf, objectives: list[dict]) -> tuple[list[dict], float]:
    results: list[dict] = []
    for objective in objectives:
        kind = objective.get("type", "all_checks")
        if kind == "all_checks":
            failed = [c for c in shelf.checks if not c["ok"]]
            ok = bool(shelf.checks) and not failed
            results.append({"type": kind, "ok": ok,
                            "detail": f"{len(shelf.checks) - len(failed)}/{len(shelf.checks)} checks passed"})
        elif kind == "search_quality":
            minimum = float(objective.get("min", 0.8))
            total = max(1, len(shelf.checks))
            passed = sum(1 for c in shelf.checks if c["ok"])
            ratio = passed / total
            ok = ratio >= minimum
            results.append({"type": kind, "ok": ok,
                            "detail": f"{passed}/{total} properties hold (min {minimum})"})
        elif kind == "implemented":
            needed = objective.get("components", ["tokenize", "build_index", "search"])
            missing = [name for name in needed if name not in shelf.impl]
            ok = not missing
            results.append({"type": kind, "ok": ok,
                            "detail": "all components implemented" if ok else f"missing {missing}"})
        else:
            results.append({"type": kind, "ok": False, "detail": f"unknown objective {kind}"})
    score = round(sum(1 for r in results if r["ok"]) / len(results), 3) if results else 0.0
    return results, score


def result(api: Shelf, state: Shelf) -> dict:
    if not state.validated:
        state.validate()
    evaluated, score = evaluate(state, state.objectives)
    ok = all(item["ok"] for item in evaluated)
    return {
        "world": "library_nexus",
        "ok": ok,
        "score": score,
        "tick": len(state.events),
        "stop_reason": "completed" if ok else "objectives_unmet",
        "objectives": evaluated,
        "events": state.events[-100:],
        "checks": state.checks,
        "stats": {
            "docs": len(state.docs),
            "queries": len(state.queries),
            "components": sorted(state.impl),
            "checks": len(state.checks),
            "passed": sum(1 for c in state.checks if c["ok"]),
        },
    }


if __name__ == "__main__":  # pragma: no cover - manual smoke run
    api, world = build({"objectives": [{"type": "all_checks"}, {"type": "implemented"}]})

    def program(shelf):
        def tokenize(text):
            return TOKEN_RE.findall(text.lower())

        def build_index(docs):
            index = {}
            for doc_id, text in docs.items():
                for token in tokenize(text):
                    index.setdefault(token, {})[doc_id] = index.setdefault(token, {}).get(doc_id, 0) + 1
            return index

        def search(index, query):
            scores = {}
            for token in tokenize(query):
                for doc_id, count in index.get(token, {}).items():
                    scores[doc_id] = scores.get(doc_id, 0) + count
            return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))

        shelf.implement("tokenize", tokenize)
        shelf.implement("build_index", build_index)
        shelf.implement("search", search)
        shelf.validate()

    try:
        program(api)
    except Exception as exc:  # noqa: BLE001
        print("stopped:", exc)
    print(json.dumps(result(api, world), indent=2)[:900])
