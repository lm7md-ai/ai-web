"""Adaptive learning engine.

The engine turns three signals into a recommendation:

1. **what the learner demonstrated** (skill graph states and evidence),
2. **what they did inside the curriculum** (module_progress rows),
3. **what decayed** (skills whose review date has passed).

It never invents mastery: a module is only "ready" when every prerequisite
module is at least started and the skills it teaches are not in a negative
state that blocks it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from pfn.db.connection import Database
from pfn.domain.curriculum.registry import CurriculumService
from pfn.domain.skills.graph import SkillGraphService
from pfn.domain.skills.states import SkillState

BLOCKING_STATES = frozenset(
    {
        SkillState.CURRENTLY_UNCERTAIN.value,
        SkillState.RECOVERY_RECOMMENDED.value,
    }
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Recommendation:
    module_id: str
    level: int
    title: str
    reason: str
    reason_ar: str
    score: float
    skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "level": self.level,
            "title": self.title,
            "reason": self.reason,
            "reason_ar": self.reason_ar,
            "score": round(self.score, 3),
            "skills": list(self.skills),
        }


class LearningEngine:
    """Decides what to study next, and why."""

    def __init__(
        self,
        db: Database,
        curriculum: CurriculumService,
        skills: SkillGraphService,
    ) -> None:
        self.db = db
        self.curriculum = curriculum
        self.skills = skills

    # ------------------------------------------------------------------ reads
    def _progress_rows(self, learner_id: str) -> dict[str, dict]:
        return self.curriculum.progress(learner_id)

    def _skill_states(self, learner_id: str) -> dict[str, dict]:
        return self.skills.states(learner_id)

    # ------------------------------------------------------------ diagnosis
    def diagnose(self, learner_id: str, locale: str = "en") -> dict:
        """Aggregate view: levels, weak skills, stalled modules, due reviews."""
        states = self._skill_states(learner_id)
        progress = self._progress_rows(learner_id)
        modules = self.curriculum.all(locale)

        by_level: dict[int, dict[str, int]] = {}
        for module in modules:
            bucket = by_level.setdefault(module.level, {"modules": 0, "started": 0, "passed": 0})
            bucket["modules"] += 1
            row = progress.get(module.id) or {}
            if row.get("status", "not_started") != "not_started":
                bucket["started"] += 1
            if row.get("task_passed"):
                bucket["passed"] += 1

        weak = [
            entry
            for entry in states.values()
            if entry.get("state") in BLOCKING_STATES or (entry.get("confidence", 0.0) < 0.4 and entry.get("evidence_count"))
        ]
        weak.sort(key=lambda entry: (entry.get("confidence", 0.0), entry.get("skill_id", "")))

        stalled = []
        for module in modules:
            row = progress.get(module.id) or {}
            if row.get("status") == "in_progress" and not row.get("task_passed"):
                stalled.append({"id": module.id, "title": module.title(locale), "level": module.level})

        due = self.skills.due_reviews(learner_id, now=_now())

        return {
            "learner_id": learner_id,
            "levels": [
                {"level": level, **counts, "completion": round(counts["passed"] / max(1, counts["modules"]), 3)}
                for level, counts in sorted(by_level.items())
            ],
            "weak_skills": [
                {
                    "skill_id": entry.get("skill_id"),
                    "state": entry.get("state"),
                    "confidence": entry.get("confidence"),
                }
                for entry in weak[:15]
            ],
            "stalled_modules": stalled[:10],
            "due_reviews": due[:10],
            "generated_at": _now().isoformat(timespec="seconds"),
        }

    # -------------------------------------------------------- recommend
    def recommend(self, learner_id: str, locale: str = "en", limit: int = 5) -> list[Recommendation]:
        states = self._skill_states(learner_id)
        progress = self._progress_rows(learner_id)
        recommendations: list[Recommendation] = []

        for module in self.curriculum.all(locale):
            row = progress.get(module.id) or {}
            if row.get("assessment_passed"):
                continue  # already mastered, no need to push it again

            missing = [p for p in module.prerequisites if not (progress.get(p) or {}).get("task_passed")]
            if missing:
                continue

            score = 0.0
            reasons_en: list[str] = []
            reasons_ar: list[str] = []

            module_skills = list(module.skills)
            blocking = [s for s in module_skills if (states.get(s) or {}).get("state") in BLOCKING_STATES]
            unassessed = [s for s in module_skills if (states.get(s) or {}).get("state") == SkillState.NOT_ASSESSED.value]
            weak = [
                s
                for s in module_skills
                if (states.get(s) or {}).get("state") not in BLOCKING_STATES
                and (states.get(s) or {}).get("confidence", 0.0) < 0.5
            ]

            if blocking:
                score += 3.0
                reasons_en.append(f"repairs {len(blocking)} skill(s) currently marked uncertain")
                reasons_ar.append(f"يعالج {len(blocking)} مهارة موسومة بعدم التأكد حالياً")
            if unassessed:
                score += 1.5
                reasons_en.append(f"assesses {len(unassessed)} unmeasured skill(s)")
                reasons_ar.append(f"يقيس {len(unassessed)} مهارة لم تُقَيَّم بعد")
            if weak:
                score += 1.0
                reasons_en.append(f"practises {len(weak)} low-confidence skill(s)")
                reasons_ar.append(f"يتدرب على {len(weak)} مهارة منخفضة الثقة")

            if row.get("task_passed") and not row.get("assessment_passed"):
                score += 2.0
                reasons_en.append("the task passed but the independent assessment is still open")
                reasons_ar.append("المهمة نجحت لكن التقييم المستقل ما زال مفتوحاً")
            if row.get("status") == "in_progress":
                score += 1.5
                reasons_en.append("already in progress")
                reasons_ar.append("قيد التقدم بالفعل")
            if row.get("status", "not_started") == "not_started":
                score += 0.8

            # keep the learner moving forward, but never skip a whole level
            score += max(0, 6 - module.level) * 0.15

            recommendations.append(
                Recommendation(
                    module_id=module.id,
                    level=module.level,
                    title=module.title(locale),
                    reason="; ".join(reasons_en) or "next unvisited module in your path",
                    reason_ar="؛ ".join(reasons_ar) or "الوحدة التالية غير المزارة في مسارك",
                    score=score,
                    skills=module_skills,
                )
            )

        recommendations.sort(key=lambda item: (-item.score, item.level, item.module_id))
        return recommendations[: max(1, limit)]

    def path(self, learner_id: str, locale: str = "en") -> list[dict]:
        """The full curriculum annotated with readiness and progress."""
        progress = self._progress_rows(learner_id)
        states = self._skill_states(learner_id)
        out = []
        for module in self.curriculum.all(locale):
            row = progress.get(module.id) or {}
            missing = [p for p in module.prerequisites if not (progress.get(p) or {}).get("task_passed")]
            blocking = [s for s in module.skills if (states.get(s) or {}).get("state") in BLOCKING_STATES]
            out.append(
                {
                    "id": module.id,
                    "level": module.level,
                    "order_index": module.order_index,
                    "domain": module.domain,
                    "title": module.title(locale),
                    "summary": module.summary(locale),
                    "status": row.get("status", "not_started"),
                    "task_passed": bool(row.get("task_passed")),
                    "assessment_passed": bool(row.get("assessment_passed")),
                    "prerequisites": list(module.prerequisites),
                    "missing_prerequisites": missing,
                    "blocking_skills": blocking,
                    "ready": not missing,
                    "skills": list(module.skills),
                }
            )
        return out

    # ------------------------------------------------------------ reviews
    def review_queue(self, learner_id: str, limit: int = 10) -> list[dict]:
        return self.skills.due_reviews(learner_id, now=_now())[: max(1, limit)]
