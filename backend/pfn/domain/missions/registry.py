"""Mission registry service: catalogues missions and keeps the DB in sync."""

from __future__ import annotations

from datetime import datetime, timezone

from pfn.db.connection import Database
from pfn.domain.missions.content import MISSIONS, by_id
from pfn.domain.missions.models import Mission

WORLD_ORDER = {"roboverse": 0, "automation_city": 1, "neural_civilization": 2}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class MissionRegistry:
    def __init__(self, db: Database) -> None:
        self.db = db

    def sync(self) -> int:
        now = _now()
        with self.db.transaction() as conn:
            for mission in MISSIONS:
                conn.execute(
                    """INSERT INTO missions (id, world, order_index, difficulty, title_ar, title_en,
                                             brief_ar, brief_en, skills_json, synced_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(id) DO UPDATE SET
                         world=excluded.world, order_index=excluded.order_index,
                         difficulty=excluded.difficulty, title_ar=excluded.title_ar,
                         title_en=excluded.title_en, brief_ar=excluded.brief_ar,
                         brief_en=excluded.brief_en, skills_json=excluded.skills_json,
                         synced_at=excluded.synced_at""",
                    (
                        mission.id,
                        mission.world,
                        mission.order_index,
                        mission.difficulty,
                        mission.title_ar,
                        mission.title_en,
                        mission.brief_ar,
                        mission.brief_en,
                        __import__("json").dumps(list(mission.skills)),
                        now,
                    ),
                )
        return len(MISSIONS)

    def all(self, locale: str = "en") -> list[Mission]:
        return sorted(
            MISSIONS, key=lambda m: (WORLD_ORDER.get(m.world, 9), m.order_index, m.id)
        )

    def for_world(self, world: str, locale: str = "en") -> list[Mission]:
        return sorted(
            (m for m in MISSIONS if m.world == world), key=lambda m: (m.order_index, m.id)
        )

    def get(self, mission_id: str) -> Mission:
        return by_id(mission_id)

    def to_dict(self, locale: str = "en", world: str | None = None) -> list[dict]:
        missions = self.for_world(world) if world else self.all()
        return [m.to_dict(locale) for m in missions]
