"""Skill graph service: seeding, evidence recording, state queries and reviews."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone

from pfn.db.connection import Database
from pfn.domain.skills import nodes as node_data
from pfn.domain.skills.states import (
    Independence,
    Outcome,
    SkillState,
    Transition,
    apply_evidence,
    rank,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


class SkillGraphService:
    """Owns every read/write against the shared skill graph."""

    def __init__(self, db: Database) -> None:
        self.db = db

    # ------------------------------------------------------------------ seed
    def sync_graph(self) -> int:
        """Upsert the canonical graph into the database. Returns the node count."""
        now = _iso(_now())
        with self.db.transaction() as conn:
            for node in node_data.NODES.values():
                conn.execute(
                    """INSERT INTO skills (id, domain, level, title_ar, title_en, description_ar,
                                          description_en, prerequisites_json, related_json,
                                          evidence_required, updated_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(id) DO UPDATE SET
                         domain=excluded.domain, level=excluded.level, title_ar=excluded.title_ar,
                         title_en=excluded.title_en, description_ar=excluded.description_ar,
                         description_en=excluded.description_en,
                         prerequisites_json=excluded.prerequisites_json,
                         related_json=excluded.related_json,
                         evidence_required=excluded.evidence_required, updated_at=excluded.updated_at""",
                    (
                        node.id,
                        node.domain,
                        node.level,
                        node.title_ar,
                        node.title_en,
                        node.description_ar,
                        node.description_en,
                        json.dumps(list(node.prerequisites)),
                        json.dumps(list(node.related)),
                        node.evidence_required,
                        now,
                    ),
                )
        problems = node_data.validate_graph()
        if problems:
            raise RuntimeError(f"skill graph is invalid: {problems}")
        return len(node_data.NODES)

    # ------------------------------------------------------------------ read
    def list_skills(self, locale: str = "en", domain: str | None = None, level: int | None = None):
        sql = "SELECT * FROM skills"
        clauses, params = [], []
        if domain:
            clauses.append("domain = ?")
            params.append(domain)
        if level is not None:
            clauses.append("level = ?")
            params.append(level)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY level, id"
        rows = self.db.query_all(sql, tuple(params))
        return [self._skill_row(row, locale) for row in rows]

    def _skill_row(self, row, locale: str) -> dict:
        return {
            "id": row["id"],
            "domain": row["domain"],
            "level": row["level"],
            "title": row["title_ar"] if locale == "ar" else row["title_en"],
            "title_ar": row["title_ar"],
            "title_en": row["title_en"],
            "description": row["description_ar"] if locale == "ar" else row["description_en"],
            "description_ar": row["description_ar"],
            "description_en": row["description_en"],
            "prerequisites": json.loads(row["prerequisites_json"]),
            "related": json.loads(row["related_json"]),
            "evidence_required": row["evidence_required"],
        }

    def get_skill(self, skill_id: str, locale: str = "en") -> dict | None:
        row = self.db.query_one("SELECT * FROM skills WHERE id = ?", (skill_id,))
        return self._skill_row(row, locale) if row else None

    def states(self, learner_id: str, locale: str = "en") -> dict[str, dict]:
        rows = self.db.query_all("SELECT * FROM skill_state WHERE learner_id = ?", (learner_id,))
        by_id = {row["skill_id"]: dict(row) for row in rows}
        out: dict[str, dict] = {}
        for skill_id, node in node_data.NODES.items():
            state = by_id.get(skill_id)
            out[skill_id] = {
                "skill_id": skill_id,
                "title": node.title(locale),
                "domain": node.domain,
                "level": node.level,
                "state": state["state"] if state else SkillState.NOT_ASSESSED.value,
                "confidence": state["confidence"] if state else 0.0,
                "evidence_count": state["evidence_count"] if state else 0,
                "independent_count": state["independent_count"] if state else 0,
                "assisted_count": state["assisted_count"] if state else 0,
                "last_evidence_at": state["last_evidence_at"] if state else None,
                "last_verified_at": state["last_verified_at"] if state else None,
                "next_review_at": state["next_review_at"] if state else None,
                "review_interval_days": state["review_interval_days"] if state else 1.0,
            }
        return out

    def summary(self, learner_id: str, locale: str = "en") -> dict:
        states = self.states(learner_id, locale)
        counts: dict[str, int] = {}
        for entry in states.values():
            counts[entry["state"]] = counts.get(entry["state"], 0) + 1
        total = len(states)
        mastered = sum(
            1
            for e in states.values()
            if e["state"]
            in (
                SkillState.DEMONSTRATED.value,
                SkillState.INDEPENDENTLY_PRACTICED.value,
                SkillState.TRANSFER_DEMONSTRATED.value,
            )
        )
        independent = sum(
            1
            for e in states.values()
            if e["state"]
            in (SkillState.INDEPENDENTLY_PRACTICED.value, SkillState.TRANSFER_DEMONSTRATED.value)
        )
        return {
            "total_skills": total,
            "mastered": mastered,
            "independent": independent,
            "coverage": round(mastered / total, 4) if total else 0.0,
            "state_counts": counts,
            "due_reviews": len(self.due_reviews(learner_id)),
            "gaps": self.gaps(learner_id, locale)[:5],
        }

    # ------------------------------------------------------------- evidence
    def _ensure_state_row(self, conn, learner_id: str, skill_id: str) -> dict:
        row = conn.execute(
            "SELECT * FROM skill_state WHERE learner_id = ? AND skill_id = ?", (learner_id, skill_id)
        ).fetchone()
        if row is None:
            conn.execute(
                """INSERT INTO skill_state (learner_id, skill_id, state, confidence, updated_at)
                   VALUES (?, ?, 'not_assessed', 0.0, ?)""",
                (learner_id, skill_id, _iso(_now())),
            )
            row = conn.execute(
                "SELECT * FROM skill_state WHERE learner_id = ? AND skill_id = ?",
                (learner_id, skill_id),
            ).fetchone()
        return dict(row)

    def record_evidence(
        self,
        *,
        learner_id: str,
        skill_id: str | None,
        kind: str,
        source_type: str,
        source_id: str | None = None,
        outcome: str = "success",
        independence: str = "independent",
        weight: float = 1.0,
        details: dict | None = None,
        transfer: bool = False,
        prior_knowledge: bool = False,
    ) -> dict:
        """Persist evidence and fold it into the skill state (atomic in one tx)."""
        if skill_id is not None and skill_id not in node_data.NODES:
            raise KeyError(f"unknown skill id: {skill_id}")
        now = _now()
        evidence_id = "ev_" + uuid.uuid4().hex[:16]
        transition: Transition | None = None
        with self.db.transaction() as conn:
            conn.execute(
                """INSERT INTO evidence (id, learner_id, skill_id, kind, source_type, source_id,
                                         outcome, independence, weight, details_json, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    evidence_id,
                    learner_id,
                    skill_id,
                    kind,
                    source_type,
                    source_id,
                    Outcome(outcome).value,
                    Independence(independence).value,
                    weight,
                    json.dumps(details or {}),
                    _iso(now),
                ),
            )
            if skill_id is not None:
                state = self._ensure_state_row(conn, learner_id, skill_id)
                independent_count = state["independent_count"] + (
                    1 if independence in ("independent", "hinted") else 0
                )
                assisted_count = state["assisted_count"] + (1 if independence == "assisted" else 0)
                transition = apply_evidence(
                    state=state["state"],
                    confidence=state["confidence"],
                    outcome=outcome,
                    independence=independence,
                    evidence_count=state["evidence_count"],
                    independent_count=independent_count,
                    transfer=transfer,
                    review_interval_days=state["review_interval_days"],
                    prior_knowledge=prior_knowledge,
                )
                next_review = now + timedelta(days=transition.review_interval_days)
                conn.execute(
                    """UPDATE skill_state
                          SET state = ?, confidence = ?,
                              evidence_count = evidence_count + 1,
                              independent_count = ?, assisted_count = ?,
                              last_evidence_at = ?,
                              last_verified_at = CASE WHEN ? THEN ? ELSE last_verified_at END,
                              next_review_at = ?, review_interval_days = ?, updated_at = ?
                        WHERE learner_id = ? AND skill_id = ?""",
                    (
                        transition.state.value,
                        transition.confidence,
                        independent_count,
                        assisted_count,
                        _iso(now),
                        1 if Outcome(outcome) is Outcome.SUCCESS else 0,
                        _iso(now),
                        _iso(next_review),
                        transition.review_interval_days,
                        _iso(now),
                        learner_id,
                        skill_id,
                    ),
                )
        payload = {
            "evidence_id": evidence_id,
            "skill_id": skill_id,
            "outcome": outcome,
            "independence": independence,
            "recorded_at": _iso(now),
        }
        if transition is not None:
            payload.update(
                {
                    "state": transition.state.value,
                    "confidence": transition.confidence,
                    "review_interval_days": transition.review_interval_days,
                    "note_ar": transition.note_ar,
                    "note_en": transition.note_en,
                }
            )
        return payload

    def evidence_history(self, learner_id: str, skill_id: str | None = None, limit: int = 50) -> list[dict]:
        sql = "SELECT * FROM evidence WHERE learner_id = ?"
        params: list = [learner_id]
        if skill_id:
            sql += " AND skill_id = ?"
            params.append(skill_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self.db.query_all(sql, tuple(params))
        return [
            {
                "id": row["id"],
                "skill_id": row["skill_id"],
                "kind": row["kind"],
                "source_type": row["source_type"],
                "source_id": row["source_id"],
                "outcome": row["outcome"],
                "independence": row["independence"],
                "weight": row["weight"],
                "details": json.loads(row["details_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    # -------------------------------------------------------------- planning
    def due_reviews(self, learner_id: str, now: datetime | None = None) -> list[dict]:
        now = now or _now()
        rows = self.db.query_all(
            """SELECT * FROM skill_state
                WHERE learner_id = ? AND next_review_at IS NOT NULL AND next_review_at <= ?
                ORDER BY next_review_at""",
            (learner_id, _iso(now)),
        )
        return [dict(row) for row in rows]

    def gaps(self, learner_id: str, locale: str = "en", limit: int = 10) -> list[dict]:
        """Skills whose state is weak or negative, weakest and lowest-level first."""
        states = self.states(learner_id, locale)
        weak = {
            SkillState.RECOVERY_RECOMMENDED.value,
            SkillState.CURRENTLY_UNCERTAIN.value,
            SkillState.PARTIALLY_DEMONSTRATED.value,
            SkillState.NOT_ASSESSED.value,
        }
        candidates = [
            entry for entry in states.values() if entry["state"] in weak
        ]
        # Prefer skills whose prerequisites are already solid: teach the frontier.
        def score(entry: dict) -> tuple:
            prereq_ids = node_data.NODES[entry["skill_id"]].prerequisites
            prereq_ready = 0
            if prereq_ids:
                prereq_ready = sum(
                    1
                    for p in prereq_ids
                    if states.get(p, {}).get("state")
                    in (
                        SkillState.DEMONSTRATED.value,
                        SkillState.INDEPENDENTLY_PRACTICED.value,
                        SkillState.TRANSFER_DEMONSTRATED.value,
                    )
                )
                prereq_ready = prereq_ready / len(prereq_ids)
            else:
                prereq_ready = 1.0
            severity = {
                SkillState.RECOVERY_RECOMMENDED.value: 0,
                SkillState.CURRENTLY_UNCERTAIN.value: 1,
                SkillState.PARTIALLY_DEMONSTRATED.value: 2,
                SkillState.NOT_ASSESSED.value: 3,
            }[entry["state"]]
            return (-prereq_ready, severity, entry["level"], entry["skill_id"])

        candidates.sort(key=score)
        return candidates[:limit]

    def readiness(self, learner_id: str, skill_id: str, locale: str = "en") -> dict:
        """How prepared is the learner for this skill, based on prerequisites?"""
        node = node_data.NODES.get(skill_id)
        if node is None:
            raise KeyError(skill_id)
        states = self.states(learner_id, locale)
        missing = []
        ready = []
        positive = {
            SkillState.DEMONSTRATED.value,
            SkillState.INDEPENDENTLY_PRACTICED.value,
            SkillState.TRANSFER_DEMONSTRATED.value,
        }
        for prereq in node.prerequisites:
            state = states.get(prereq, {}).get("state", SkillState.NOT_ASSESSED.value)
            if state in positive:
                ready.append(prereq)
            else:
                missing.append(
                    {
                        "skill_id": prereq,
                        "title": node_data.NODES[prereq].title(locale),
                        "state": state,
                    }
                )
        total = len(node.prerequisites) or 1
        return {
            "skill_id": skill_id,
            "title": node.title(locale),
            "level": node.level,
            "prerequisite_count": len(node.prerequisites),
            "ready_prerequisites": ready,
            "missing_prerequisites": missing,
            "readiness": round(len(ready) / total, 3),
            "current_state": states.get(skill_id, {}).get("state", SkillState.NOT_ASSESSED.value),
        }

    def cross_domain_links(self, learner_id: str, skill_id: str, locale: str = "en") -> list[dict]:
        node = node_data.NODES.get(skill_id)
        if node is None:
            return []
        states = self.states(learner_id, locale)
        return [
            {
                "skill_id": rel,
                "title": node_data.NODES[rel].title(locale),
                "domain": node_data.NODES[rel].domain,
                "level": node_data.NODES[rel].level,
                "state": states.get(rel, {}).get("state", SkillState.NOT_ASSESSED.value),
            }
            for rel in node.related
            if rel in node_data.NODES
        ]

    def next_recommended(self, learner_id: str, locale: str = "en", limit: int = 5) -> list[dict]:
        """Frontier skills: not yet mastered, but whose prerequisites are ready."""
        states = self.states(learner_id, locale)
        positive = {
            SkillState.DEMONSTRATED.value,
            SkillState.INDEPENDENTLY_PRACTICED.value,
            SkillState.TRANSFER_DEMONSTRATED.value,
        }
        out = []
        for skill_id, node in node_data.NODES.items():
            state = states[skill_id]["state"]
            if state in positive:
                continue
            prereqs = node.prerequisites
            if prereqs and not all(states.get(p, {}).get("state") in positive for p in prereqs):
                continue
            out.append(
                {
                    "skill_id": skill_id,
                    "title": node.title(locale),
                    "domain": node.domain,
                    "level": node.level,
                    "state": state,
                    "confidence": states[skill_id]["confidence"],
                }
            )
        out.sort(key=lambda item: (item["level"], item["skill_id"]))
        return out[:limit]

    def set_state(
        self, learner_id: str, skill_id: str, state: str, confidence: float | None = None
    ) -> dict:
        """Explicit override (used by onboarding self-assessment, clearly flagged)."""
        if skill_id not in node_data.NODES:
            raise KeyError(skill_id)
        target = SkillState(state)
        with self.db.transaction() as conn:
            self._ensure_state_row(conn, learner_id, skill_id)
            if confidence is None:
                conn.execute(
                    "UPDATE skill_state SET state = ?, updated_at = ? WHERE learner_id = ? AND skill_id = ?",
                    (target.value, _iso(_now()), learner_id, skill_id),
                )
            else:
                conn.execute(
                    """UPDATE skill_state SET state = ?, confidence = ?, updated_at = ?
                        WHERE learner_id = ? AND skill_id = ?""",
                    (target.value, confidence, _iso(_now()), learner_id, skill_id),
                )
            row = conn.execute(
                "SELECT * FROM skill_state WHERE learner_id = ? AND skill_id = ?",
                (learner_id, skill_id),
            ).fetchone()
        return dict(row)

    def weakest_prerequisite_chain(self, learner_id: str, skill_id: str, locale: str = "en") -> list[dict]:
        """Walk prerequisites to find the earliest weak link (for recovery)."""
        states = self.states(learner_id, locale)
        positive = {
            SkillState.DEMONSTRATED.value,
            SkillState.INDEPENDENTLY_PRACTICED.value,
            SkillState.TRANSFER_DEMONSTRATED.value,
        }
        chain: list[dict] = []
        seen: set[str] = set()
        stack = list(node_data.NODES[skill_id].prerequisites) if skill_id in node_data.NODES else []
        while stack:
            current = stack.pop(0)
            if current in seen:
                continue
            seen.add(current)
            node = node_data.NODES.get(current)
            if node is None:
                continue
            state = states.get(current, {}).get("state", SkillState.NOT_ASSESSED.value)
            if state not in positive:
                chain.append(
                    {
                        "skill_id": current,
                        "title": node.title(locale),
                        "state": state,
                        "level": node.level,
                    }
                )
                stack = list(node.prerequisites) + stack
        chain.sort(key=lambda item: (item["level"], item["skill_id"]))
        return chain
