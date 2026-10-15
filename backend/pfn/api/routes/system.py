"""Health, diagnostics and static platform information."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from pfn.api.deps import MODES, Services, services_dep
from pfn.domain.curriculum.registry import MODULES, validate_curriculum
from pfn.domain.library.content import ENTRIES
from pfn.domain.missions.content import MISSIONS
from pfn.domain.skills.nodes import NODES
from pfn.worlds.engine.registry import WORLDS

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health")
def health(services: Services = Depends(services_dep)) -> dict:
    info = services.executions.python_info()
    return {
        "status": "ok",
        "app": services.settings.app_name,
        "version": services.settings.version,
        "python": info["python"],
        "platform": info["platform"],
        "providers": services.mentor.status(),
    }


@router.get("/info")
def info(services: Services = Depends(services_dep)) -> dict:
    """Static catalogue sizes - the numbers the UI shows on the dashboard."""
    return {
        "app": services.settings.app_name,
        "version": services.settings.version,
        "locales": list(services.settings.supported_locales),
        "default_locale": services.settings.default_locale,
        "execution_modes": list(MODES),
        "counts": {
            "modules": len(MODULES),
            "levels": len({m.level for m in MODULES}),
            "missions": len(MISSIONS),
            "worlds": len(WORLDS),
            "skills": len(NODES),
            "library_entries": len(ENTRIES),
        },
        "python": services.executions.python_info(),
    }


@router.get("/integrity")
def integrity() -> dict:
    """Self-check: content graphs and catalogue consistency."""
    problems = validate_curriculum()
    levels = sorted({m.level for m in MODULES})
    return {
        "modules": len(MODULES),
        "levels": levels,
        "problems": problems,
        "ok": not problems,
    }


@router.post("/admin/cleanup")
def cleanup(max_age_hours: int = Query(24, ge=1, le=720),
            services: Services = Depends(services_dep)) -> dict:
    return {"removed": services.executions.cleanup_old_runs(max_age_hours)}


@router.get("/events")
def events(limit: int = Query(50, ge=1, le=500), services: Services = Depends(services_dep)) -> dict:
    rows = services.db.query_all(
        "SELECT id, learner_id, type, payload_json, created_at FROM events"
        " ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    return {"events": [dict(row) for row in rows]}
