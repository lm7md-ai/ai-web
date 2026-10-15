"""Library Nexus: bilingual reference with runnable examples."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from pfn.api.deps import Services, learner_dep, locale_dep, services_dep

router = APIRouter(prefix="/api/library", tags=["library"])


class RunPayload(BaseModel):
    index: int | None = Field(default=None, ge=0, le=50)


@router.get("")
def list_entries(locale: str = Depends(locale_dep), domain: str | None = None,
                 q: str | None = Query(None, min_length=1, max_length=120),
                 services: Services = Depends(services_dep)) -> dict:
    if q:
        entries = services.library.search(q, locale)
    else:
        entries = services.library.list_entries(locale, domain)
    return {"locale": locale, "domain": domain, "query": q, "count": len(entries), "entries": entries}


@router.get("/domains")
def domains(services: Services = Depends(services_dep)) -> dict:
    return {"domains": services.library.domains()}


@router.get("/history")
def history(limit: int = Query(30, ge=1, le=200), learner_id: str = Depends(learner_dep),
            services: Services = Depends(services_dep)) -> dict:
    return {"runs": services.library.history(learner_id, limit)}


@router.get("/stats")
def stats(services: Services = Depends(services_dep)) -> dict:
    return services.library.stats()


@router.get("/{entry_id}")
def get_entry(entry_id: str, locale: str = Depends(locale_dep),
              services: Services = Depends(services_dep)) -> dict:
    return services.library.get(entry_id, locale)


@router.get("/{entry_id}/examples")
def examples(entry_id: str, services: Services = Depends(services_dep)) -> dict:
    entries = services.library.examples(entry_id)
    return {"entry_id": entry_id, "count": len(entries), "examples": entries}


@router.post("/{entry_id}/run")
def run_example(entry_id: str, payload: RunPayload | None = None,
                learner_id: str = Depends(learner_dep),
                services: Services = Depends(services_dep)) -> dict:
    index = payload.index if payload else None
    if index is None:
        return services.library.run_all_examples(learner_id, entry_id)
    return services.library.run_example(learner_id, entry_id, index)
