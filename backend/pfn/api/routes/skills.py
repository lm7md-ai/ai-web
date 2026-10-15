"""Skill graph endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from pfn.api.deps import Services, learner_dep, locale_dep, services_dep

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("")
def list_skills(locale: str = Depends(locale_dep), domain: str | None = None,
                level: int | None = Query(None, ge=0, le=11),
                services: Services = Depends(services_dep)) -> dict:
    skills = services.skills.list_skills(locale, domain, level)
    return {"locale": locale, "domain": domain, "level": level, "count": len(skills), "skills": skills}


@router.get("/summary")
def summary(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
            services: Services = Depends(services_dep)) -> dict:
    return services.skills.summary(learner_id, locale)


@router.get("/states")
def states(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
           services: Services = Depends(services_dep)) -> dict:
    return {"learner_id": learner_id, "states": services.skills.states(learner_id, locale)}


@router.get("/gaps")
def gaps(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
         limit: int = Query(10, ge=1, le=50), services: Services = Depends(services_dep)) -> dict:
    return {"gaps": services.skills.gaps(learner_id, locale, limit)}


@router.get("/due")
def due(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
        services: Services = Depends(services_dep)) -> dict:
    return {"due": services.skills.due_reviews(learner_id)}


@router.get("/next")
def next_skills(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
                limit: int = Query(5, ge=1, le=25),
                services: Services = Depends(services_dep)) -> dict:
    return {"skills": services.skills.next_recommended(learner_id, locale, limit)}


@router.get("/evidence")
def evidence(learner_id: str = Depends(learner_dep), skill_id: str | None = None,
             limit: int = Query(50, ge=1, le=500),
             services: Services = Depends(services_dep)) -> dict:
    return {"evidence": services.skills.evidence_history(learner_id, skill_id, limit)}


@router.get("/{skill_id}")
def get_skill(skill_id: str, locale: str = Depends(locale_dep),
              learner_id: str = Depends(learner_dep),
              services: Services = Depends(services_dep)) -> dict:
    skill = services.skills.get_skill(skill_id, locale)
    if skill is None:
        raise KeyError(skill_id)
    states = services.skills.states(learner_id, locale)
    skill["state"] = states.get(skill_id)
    return skill


@router.get("/{skill_id}/readiness")
def readiness(skill_id: str, locale: str = Depends(locale_dep),
              learner_id: str = Depends(learner_dep),
              services: Services = Depends(services_dep)) -> dict:
    return services.skills.readiness(learner_id, skill_id, locale)


@router.get("/{skill_id}/links")
def links(skill_id: str, locale: str = Depends(locale_dep), learner_id: str = Depends(learner_dep),
          services: Services = Depends(services_dep)) -> dict:
    return {"skill_id": skill_id, "links": services.skills.cross_domain_links(learner_id, skill_id, locale)}


@router.get("/{skill_id}/chain")
def chain(skill_id: str, locale: str = Depends(locale_dep), learner_id: str = Depends(learner_dep),
          services: Services = Depends(services_dep)) -> dict:
    """The weakest prerequisite chain that is holding this skill back."""
    return {"skill_id": skill_id, "chain": services.skills.weakest_prerequisite_chain(learner_id, skill_id, locale)}
