"""Interactive worlds: metadata, API contract and the sim source itself."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from pfn.api.deps import Services, locale_dep, services_dep
from pfn.domain.missions.content import MISSIONS
from pfn.worlds.engine.registry import WORLDS, get_world, world_summary

router = APIRouter(prefix="/api/worlds", tags=["worlds"])


@router.get("")
def list_worlds(locale: str = Depends(locale_dep)) -> dict:
    return {"locale": locale, "count": len(WORLDS), "worlds": world_summary(locale)}


@router.get("/{world_id}")
def get_world_detail(world_id: str, locale: str = Depends(locale_dep)) -> dict:
    world = get_world(world_id)
    missions = [m for m in MISSIONS if m.world == world_id]
    return {
        "id": world.id,
        "title": world.title(locale),
        "title_ar": world.title_ar,
        "title_en": world.title_en,
        "description": world.description(locale),
        "description_ar": world.description_ar,
        "description_en": world.description_en,
        "entrypoint": world.entrypoint,
        "module_name": world.module_name,
        "api": [{"signature": sig, "doc": doc} for sig, doc in world.api_docs],
        "missions": [
            {"id": m.id, "title": m.title(locale), "order_index": m.order_index,
             "difficulty": m.difficulty}
            for m in sorted(missions, key=lambda m: (m.order_index, m.id))
        ],
    }


@router.get("/{world_id}/source")
def world_source(world_id: str) -> dict:
    """The simulation is open source and readable - learners can inspect the rules."""
    world = get_world(world_id)
    return {
        "id": world.id,
        "module_name": world.module_name,
        "entrypoint": world.entrypoint,
        "source": world.source(),
    }
