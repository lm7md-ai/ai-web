"""Mission endpoints: run learner code inside a simulation world."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from pfn.api.deps import Services, learner_dep, locale_dep, mode_dep, services_dep
from pfn.domain.missions.content import MISSIONS, by_id

router = APIRouter(prefix="/api/missions", tags=["missions"])


class RunPayload(BaseModel):
    code: str = Field(min_length=1)
    hints_used: int = Field(default=0, ge=0, le=99)
    assistance_level: str = Field(default="independent", pattern="^(independent|hints|solution)$")
    trace: bool = False


@router.get("")
def list_missions(locale: str = Depends(locale_dep), world: str | None = None,
                  services: Services = Depends(services_dep)) -> dict:
    missions = [m for m in MISSIONS if world is None or m.world == world]
    missions.sort(key=lambda m: (m.world, m.order_index, m.id))
    return {
        "locale": locale,
        "world": world,
        "count": len(missions),
        "missions": [m.to_dict(locale) for m in missions],
    }


@router.get("/{mission_id}")
def get_mission(mission_id: str, locale: str = Depends(locale_dep)) -> dict:
    mission = by_id(mission_id)
    payload = mission.to_dict(locale)
    payload["world_config"] = mission.config
    return payload


@router.get("/{mission_id}/hint")
def hint(mission_id: str, index: int = Query(0, ge=0, le=20)) -> dict:
    """Progressive hints, one at a time. The reference solution is never served."""
    mission = by_id(mission_id)
    hints = list(mission.hints)
    if index >= len(hints):
        return {"mission_id": mission_id, "index": index, "hint": None, "total": len(hints)}
    return {"mission_id": mission_id, "index": index, "hint": hints[index], "total": len(hints)}


@router.post("/{mission_id}/run")
def run(mission_id: str, payload: RunPayload, mode: str = Depends(mode_dep),
        learner_id: str = Depends(learner_dep),
        services: Services = Depends(services_dep)) -> dict:
    return services.missions.run(
        learner_id=learner_id,
        mission_id=mission_id,
        code=payload.code,
        mode=mode,
        hints_used=payload.hints_used,
        assistance_level=payload.assistance_level,
        trace=payload.trace,
    )


@router.get("/{mission_id}/history")
def history(mission_id: str, limit: int = Query(20, ge=1, le=200),
            learner_id: str = Depends(learner_dep),
            services: Services = Depends(services_dep)) -> dict:
    return {"mission_id": mission_id, "attempts": services.missions.history(learner_id, mission_id, limit)}
