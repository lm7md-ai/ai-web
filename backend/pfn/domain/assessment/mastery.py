"""Mastery computation and the learner passport.

Mastery is derived from *evidence rows only*. Nothing here is inferred from
time spent, pages visited or self-reported confidence.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from pfn.db.connection import Database
from pfn.domain.curriculum.registry import CurriculumService
from pfn.domain.skills.graph import SkillGraphService
from pfn.domain.skills.states import SkillState

POSITIVE = frozenset(
    {
        SkillState.DEMONSTRATED.value,
        SkillState.INDEPENDENTLY_PRACTICED.value,
        SkillState.TRANSFER_DEMONSTRATED.value,
    }
)

LEVEL_NAMES = {
    0: {"en": "Recovery", "ar": "الاستعادة"},
    1: {"en": "Foundations", "ar": "الأساسيات"},
    2: {"en": "Idiomatic Python", "ar": "الأسلوب البايثوني"},
    3: {"en": "Professional practice", "ar": "الممارسة المهنية"},
    4: {"en": "Advanced Python", "ar": "بايثون المتقدمة"},
    5: {"en": "Data engineering", "ar": "هندسة البيانات"},
    6: {"en": "Algorithms", "ar": "الخوارزميات"},
    7: {"en": "Machine learning", "ar": "تعلّم الآلة"},
    8: {"en": "Deep learning", "ar": "التعلّم العميق"},
    9: {"en": "LLM engineering", "ar": "هندسة النماذج اللغوية"},
    10: {"en": "Systems", "ar": "الأنظمة"},
    11: {"en": "Capstone", "ar": "مشروع التخرّج"},
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class MasteryService:
    """Turns skill states and curriculum progress into mastery figures."""

    def __init__(
        self,
        db: Database,
        skills: SkillGraphService,
        curriculum: CurriculumService,
    ) -> None:
        self.db = db
        self.skills = skills
        self.curriculum = curriculum

    # ------------------------------------------------------------------ core
    def mastery(self, learner_id: str, locale: str = "en") -> dict:
        states = self.skills.states(learner_id, locale)
        progress = self.curriculum.progress(learner_id)
        modules = self.curriculum.all(locale)

        per_domain: dict[str, dict[str, float]] = {}
        counted = 0
        demonstrated = 0
        for entry in states.values():
            domain = (entry.get("domain") or "core").split(".")[0]
            bucket = per_domain.setdefault(domain, {"total": 0, "positive": 0, "confidence": 0.0})
            bucket["total"] += 1
            bucket["confidence"] += float(entry.get("confidence") or 0.0)
            counted += 1
            if entry.get("state") in POSITIVE:
                bucket["positive"] += 1
                demonstrated += 1

        domains = sorted(
            (
                {
                    "domain": domain,
                    "skills": int(values["total"]),
                    "demonstrated": int(values["positive"]),
                    "average_confidence": round(values["confidence"] / max(1, values["total"]), 3),
                    "mastery": round(values["positive"] / max(1, values["total"]), 3),
                }
                for domain, values in per_domain.items()
            ),
            key=lambda item: -item["mastery"],
        )

        levels = []
        per_level: dict[int, dict[str, int]] = {}
        for module in modules:
            bucket = per_level.setdefault(module.level, {"modules": 0, "task": 0, "assessment": 0})
            bucket["modules"] += 1
            row = progress.get(module.id) or {}
            if row.get("task_passed"):
                bucket["task"] += 1
            if row.get("assessment_passed"):
                bucket["assessment"] += 1
        for level, values in sorted(per_level.items()):
            levels.append(
                {
                    "level": level,
                    "name": LEVEL_NAMES.get(level, {"en": str(level), "ar": str(level)})[locale],
                    "modules": values["modules"],
                    "tasks_passed": values["task"],
                    "assessments_passed": values["assessment"],
                    "completion": round(values["assessment"] / max(1, values["modules"]), 3),
                }
            )

        return {
            "learner_id": learner_id,
            "skills_tracked": counted,
            "skills_demonstrated": demonstrated,
            "overall_mastery": round(demonstrated / max(1, counted), 3),
            "domains": domains,
            "levels": levels,
            "generated_at": _now_iso(),
        }

    # --------------------------------------------------------------- passport
    def passport(self, learner_id: str, locale: str = "en") -> dict:
        """The exportable record: what was demonstrated, with evidence."""
        mastery = self.mastery(learner_id, locale)
        states = self.skills.states(learner_id, locale)
        progress = self.curriculum.progress(learner_id)

        demonstrated = []
        for skill_id, entry in sorted(states.items()):
            if entry.get("state") in POSITIVE:
                demonstrated.append(
                    {
                        "skill_id": skill_id,
                        "title": entry.get("title"),
                        "state": entry.get("state"),
                        "confidence": entry.get("confidence"),
                        "evidence_count": entry.get("evidence_count"),
                        "independent_count": entry.get("independent_count"),
                        "last_verified_at": entry.get("last_verified_at"),
                    }
                )

        modules = []
        for module in self.curriculum.all(locale):
            row = progress.get(module.id) or {}
            if row.get("assessment_passed") or row.get("task_passed"):
                modules.append(
                    {
                        "id": module.id,
                        "level": module.level,
                        "title": module.title(locale),
                        "task_passed": bool(row.get("task_passed")),
                        "assessment_passed": bool(row.get("assessment_passed")),
                    }
                )

        attempts = self.db.query_all(
            "SELECT mission_id, world, ok, score, assistance_level, created_at FROM mission_attempts"
            " WHERE learner_id = ? ORDER BY created_at DESC LIMIT 20",
            (learner_id,),
        )
        artifacts = self.db.query_all(
            "SELECT id, kind, title, summary, independence, created_at FROM portfolio_artifacts"
            " WHERE learner_id = ? ORDER BY created_at DESC LIMIT 50",
            (learner_id,),
        )

        independence_ratio = 0.0
        if attempts:
            independent = sum(1 for row in attempts if row["assistance_level"] == "independent")
            independence_ratio = round(independent / len(attempts), 3)

        return {
            "learner_id": learner_id,
            "generated_at": _now_iso(),
            "mastery": mastery,
            "skills": demonstrated,
            "modules": modules,
            "missions": [
                {
                    "mission_id": row["mission_id"],
                    "world": row["world"],
                    "ok": bool(row["ok"]),
                    "score": row["score"],
                    "assistance_level": row["assistance_level"],
                    "created_at": row["created_at"],
                }
                for row in attempts
            ],
            "artifacts": [
                {
                    "id": row["id"],
                    "kind": row["kind"],
                    "title": row["title"],
                    "summary": row["summary"],
                    "independence": row["independence"],
                    "created_at": row["created_at"],
                }
                for row in artifacts
            ],
            "independence_ratio": independence_ratio,
        }

    def passport_markdown(self, learner_id: str, locale: str = "en") -> str:
        data = self.passport(learner_id, locale)
        lines = [
            "# Python Forge Nexus - learner passport",
            "",
            f"learner: {data['learner_id']}",
            f"generated: {data['generated_at']}",
            f"overall mastery: {data['mastery']['overall_mastery']:.0%}"
            f" ({data['mastery']['skills_demonstrated']}/{data['mastery']['skills_tracked']} skills)",
            "",
            "## skills demonstrated",
        ]
        for skill in data["skills"]:
            lines.append(
                f"- {skill['skill_id']} - {skill['title']} ({skill['state']}, "
                f"confidence {skill['confidence']}, evidence {skill['evidence_count']})"
            )
        lines += ["", "## curriculum", ]
        for module in data["modules"]:
            marker = "assessment passed" if module["assessment_passed"] else "task passed"
            lines.append(f"- L{module['level']} {module['id']} - {module['title']} ({marker})")
        lines += ["", "## missions", ]
        for mission in data["missions"]:
            lines.append(
                f"- {mission['mission_id']} ({mission['world']}): ok={mission['ok']} "
                f"score={mission['score']} assistance={mission['assistance_level']}"
            )
        if data["artifacts"]:
            lines += ["", "## portfolio artifacts"]
            for artifact in data["artifacts"]:
                lines.append(f"- [{artifact['kind']}] {artifact['title']} - {artifact['summary']}")
        return "\n".join(lines) + "\n"

    # --------------------------------------------------------------- awards
    def milestones(self, learner_id: str, locale: str = "en") -> list[dict]:
        """Completed when every module of a level has passed its assessment."""
        mastery = self.mastery(learner_id, locale)
        earned = []
        for entry in mastery["levels"]:
            if entry["modules"] and entry["assessments_passed"] == entry["modules"]:
                earned.append(
                    {
                        "level": entry["level"],
                        "name": entry["name"],
                        "completion": entry["completion"],
                        "done": True,
                    }
                )
        return earned
