"""Learner + preferences repositories."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from pfn.db.connection import Database


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class LearnerRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def ensure_default(self, learner_id: str = "local", name: str = "Learner", locale: str = "ar") -> dict:
        row = self.db.query_one("SELECT * FROM learners WHERE id = ?", (learner_id,))
        if row is None:
            now = _now()
            self.db.execute(
                """INSERT INTO learners (id, display_name, locale, theme, goals_json, onboarded,
                                         created_at, updated_at)
                   VALUES (?, ?, ?, 'dark', '[]', 0, ?, ?)""",
                (learner_id, name, locale, now, now),
            )
            self.db.execute(
                """INSERT OR IGNORE INTO preferences (learner_id, updated_at) VALUES (?, ?)""",
                (learner_id, now),
            )
            row = self.db.query_one("SELECT * FROM learners WHERE id = ?", (learner_id,))
        return dict(row)

    def get(self, learner_id: str) -> dict | None:
        row = self.db.query_one("SELECT * FROM learners WHERE id = ?", (learner_id,))
        return dict(row) if row else None

    def update(self, learner_id: str, **fields) -> dict:
        allowed = {"display_name", "locale", "theme", "goals_json", "onboarded"}
        sets, values = [], []
        for key, value in fields.items():
            if key in allowed:
                sets.append(f"{key} = ?")
                values.append(value)
        if not sets:
            return self.get(learner_id) or {}
        sets.append("updated_at = ?")
        values.append(_now())
        values.append(learner_id)
        self.db.execute(f"UPDATE learners SET {', '.join(sets)} WHERE id = ?", tuple(values))
        return self.get(learner_id) or {}

    def set_goals(self, learner_id: str, goals: list[str]) -> dict:
        return self.update(learner_id, goals_json=json.dumps(goals))

    def get_preferences(self, learner_id: str) -> dict:
        row = self.db.query_one("SELECT * FROM preferences WHERE learner_id = ?", (learner_id,))
        return dict(row) if row else {}

    def update_preferences(self, learner_id: str, **fields) -> dict:
        allowed = {
            "assistance_mode",
            "hints_enabled",
            "trace_enabled",
            "execution_mode",
            "mentor_role",
            "daily_goal_minutes",
        }
        sets, values = [], []
        for key, value in fields.items():
            if key in allowed:
                sets.append(f"{key} = ?")
                values.append(int(value) if isinstance(value, bool) else value)
        if not sets:
            return self.get_preferences(learner_id)
        sets.append("updated_at = ?")
        values.append(_now())
        values.append(learner_id)
        self.db.execute(f"UPDATE preferences SET {', '.join(sets)} WHERE learner_id = ?", tuple(values))
        return self.get_preferences(learner_id)
