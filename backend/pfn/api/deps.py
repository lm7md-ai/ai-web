"""Service container for the HTTP layer.

Services are built once per process (they hold a SQLite connection pool and
the migration state) and injected into routes through FastAPI dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header, Query

from pfn.ai.mentor import MentorService
from pfn.ai.providers.base import Provider, build_provider
from pfn.config import Settings, get_settings
from pfn.db.connection import Database
from pfn.db.migrate import current_version, migrate
from pfn.db.repositories.learners import LearnerRepository
from pfn.domain.assessment.mastery import MasteryService
from pfn.domain.curriculum.registry import CurriculumService, MODULES
from pfn.domain.learning.engine import LearningEngine
from pfn.domain.library.service import LibraryService
from pfn.domain.missions.content import MISSIONS
from pfn.domain.missions.runner import MissionRunner
from pfn.domain.projects.service import ProjectService
from pfn.domain.skills.graph import SkillGraphService
from pfn.runtime.service import ExecutionService
from pfn.worlds.engine.registry import WORLDS

DEFAULT_LEARNER = "local"
MODES = ("native", "isolated")


@dataclass(slots=True)
class Services:
    settings: Settings
    db: Database
    learners: LearnerRepository
    executions: ExecutionService
    skills: SkillGraphService
    curriculum: CurriculumService
    missions: MissionRunner
    learning: LearningEngine
    mastery: MasteryService
    projects: ProjectService
    library: LibraryService
    mentor: MentorService

    def bootstrap(self) -> dict:
        """Apply migrations, sync static catalogues and create the learner."""
        applied = migrate(self.db)
        skills = self.skills.sync_graph()
        modules = self.curriculum.sync()
        self.learners.ensure_default(DEFAULT_LEARNER, locale=self.settings.default_locale)
        return {
            "migrations_applied": applied,
            "schema_version": current_version(self.db),
            "skills": skills,
            "modules": modules,
            "missions": len(MISSIONS),
            "worlds": len(WORLDS),
        }


_services: Services | None = None


def build_services(settings: Settings | None = None, provider: Provider | None = None) -> Services:
    settings = settings or get_settings()
    settings.ensure_dirs()
    db = Database(settings)
    executions = ExecutionService(settings)
    skills = SkillGraphService(db)
    curriculum = CurriculumService(db, executions, skills)
    missions = MissionRunner(db, executions, skills)
    learning = LearningEngine(db, curriculum, skills)
    mastery = MasteryService(db, skills, curriculum)
    projects = ProjectService(db, executions)
    library = LibraryService(db, executions)
    mentor = MentorService(db, executions, provider=provider or build_provider())
    return Services(
        settings=settings,
        db=db,
        learners=LearnerRepository(db),
        executions=executions,
        skills=skills,
        curriculum=curriculum,
        missions=missions,
        learning=learning,
        mastery=mastery,
        projects=projects,
        library=library,
        mentor=mentor,
    )


def init_services(settings: Settings | None = None, provider: Provider | None = None) -> Services:
    global _services
    _services = build_services(settings, provider)
    _services.bootstrap()
    return _services


def get_services() -> Services:
    """Return the process-wide container, building it on first use.

    Lazy construction keeps short-lived callers (tests, scripts, the ASGI
    server) working without an explicit bootstrap step; ``init_services``
    remains the explicit entry point used by the app lifespan.
    """
    global _services
    if _services is None:
        _services = build_services()
        _services.bootstrap()
    return _services


def services_dep() -> Services:
    """FastAPI dependency."""
    return get_services()


def locale_dep(locale: str = Query("en", pattern="^(ar|en)$")) -> str:
    return locale


def learner_dep(
    x_learner_id: str | None = Header(default=None, alias="X-Learner-Id"),
    learner_id: str = Query(DEFAULT_LEARNER),
) -> str:
    """Single-user by default; the header lets tests isolate a learner."""
    return (x_learner_id or learner_id or DEFAULT_LEARNER).strip() or DEFAULT_LEARNER


def mode_dep(mode: str = Query("native")) -> str:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    return mode


__all__ = [
    "DEFAULT_LEARNER",
    "MODES",
    "MODULES",
    "Services",
    "build_services",
    "get_services",
    "init_services",
    "learner_dep",
    "locale_dep",
    "mode_dep",
    "services_dep",
]
