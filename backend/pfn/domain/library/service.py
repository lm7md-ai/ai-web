"""Library Nexus: searchable reference whose examples are always runnable."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from pfn.db.connection import Database
from pfn.domain.library.content import ENTRIES, LibraryEntry, get_entry
from pfn.runtime.service import ExecutionService, RunRequest


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _id() -> str:
    return f"lib_{uuid.uuid4().hex[:12]}"


def _tokens(entry: LibraryEntry) -> str:
    return " ".join(
        [entry.id, entry.domain, entry.title_en, entry.title_ar, entry.summary_en, entry.summary_ar,
         entry.body_en, entry.body_ar, " ".join(entry.skills)]
    ).lower()


class LibraryService:
    def __init__(self, db: Database, executions: ExecutionService) -> None:
        self.db = db
        self.executions = executions

    # -------------------------------------------------------------- browsing
    def list_entries(self, locale: str = "en", domain: str | None = None) -> list[dict]:
        entries = [e for e in ENTRIES if domain is None or e.domain == domain]
        return [entry.to_dict(locale) for entry in entries]

    def domains(self) -> list[str]:
        return sorted({entry.domain for entry in ENTRIES})

    def get(self, entry_id: str, locale: str = "en") -> dict:
        return get_entry(entry_id).to_dict(locale)

    def search(self, query: str, locale: str = "en", limit: int = 20) -> list[dict]:
        needle = query.strip().lower()
        scored = []
        for entry in ENTRIES:
            haystack = _tokens(entry)
            if not needle or needle in haystack:
                score = haystack.count(needle) if needle else 0
                scored.append((score, entry))
        scored.sort(key=lambda pair: (-pair[0], pair[1].id))
        return [entry.to_dict(locale) for _, entry in scored[:limit]]

    # -------------------------------------------------------------- examples
    def examples(self, entry_id: str) -> list[dict]:
        entry = get_entry(entry_id)
        return [{"index": i, "label": label, "code": code} for i, (label, code) in enumerate(entry.examples)]

    def run_example(self, learner_id: str, entry_id: str, index: int | None = None) -> dict:
        entry = get_entry(entry_id)
        if index is None:
            index = 0
        if not 0 <= index < len(entry.examples):
            raise IndexError(f"{entry_id} has {len(entry.examples)} examples; got index {index}")
        label, code = entry.examples[index]
        result = self.executions.run(
            RunRequest(files={"main.py": code}, kind="script", entry="main.py")
        ).to_dict()
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT INTO library_runs (id, learner_id, library_id, example_index, ok, output, created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (
                    _id(),
                    learner_id,
                    entry_id,
                    index,
                    int(bool(result.get("ok"))),
                    (result.get("stdout") or "")[:2000],
                    _now(),
                ),
            )
        result["entry_id"] = entry_id
        result["example_index"] = index
        result["label"] = label
        return result

    def run_all_examples(self, learner_id: str, entry_id: str) -> dict:
        entry = get_entry(entry_id)
        reports = [self.run_example(learner_id, entry_id, i) for i in range(len(entry.examples))]
        return {
            "entry_id": entry_id,
            "total": len(reports),
            "ok": sum(1 for r in reports if r.get("ok")),
            "reports": reports,
        }

    def history(self, learner_id: str, limit: int = 30) -> list[dict]:
        rows = self.db.query_all(
            "SELECT library_id AS entry_id, example_index, ok, created_at FROM library_runs"
            " WHERE learner_id = ? ORDER BY created_at DESC LIMIT ?",
            (learner_id, limit),
        )
        return [dict(row) for row in rows]

    def stats(self) -> dict:
        rows = self.db.query_all(
            "SELECT library_id AS entry_id, COUNT(*) AS runs, SUM(ok) AS successful FROM library_runs"
            " GROUP BY library_id ORDER BY runs DESC"
        )
        return {"entries": len(ENTRIES), "by_entry": [dict(row) for row in rows]}
