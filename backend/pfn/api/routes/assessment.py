"""Adaptive learning, mastery and the learner passport."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse

from pfn.api.deps import Services, learner_dep, locale_dep, services_dep

router = APIRouter(prefix="/api", tags=["assessment"])


@router.get("/learning/diagnose")
def diagnose(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
             services: Services = Depends(services_dep)) -> dict:
    return services.learning.diagnose(learner_id, locale)


@router.get("/learning/recommendations")
def recommendations(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
                    limit: int = Query(5, ge=1, le=25),
                    services: Services = Depends(services_dep)) -> dict:
    items = services.learning.recommend(learner_id, locale, limit)
    return {"locale": locale, "count": len(items), "recommendations": [item.to_dict() for item in items]}


@router.get("/learning/path")
def path(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
         services: Services = Depends(services_dep)) -> dict:
    return {"locale": locale, "path": services.learning.path(learner_id, locale)}


@router.get("/learning/reviews")
def reviews(learner_id: str = Depends(learner_dep),
            services: Services = Depends(services_dep)) -> dict:
    return {"queue": services.learning.review_queue(learner_id)}


@router.get("/assessment/mastery")
def mastery(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
            services: Services = Depends(services_dep)) -> dict:
    return services.mastery.mastery(learner_id, locale)


@router.get("/assessment/milestones")
def milestones(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
               services: Services = Depends(services_dep)) -> dict:
    return {"locale": locale, "milestones": services.mastery.milestones(learner_id, locale)}


@router.get("/assessment/passport")
def passport(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
             services: Services = Depends(services_dep)) -> dict:
    return services.mastery.passport(learner_id, locale)


@router.get("/assessment/passport.md", response_class=PlainTextResponse)
def passport_markdown(learner_id: str = Depends(learner_dep), locale: str = Depends(locale_dep),
                      services: Services = Depends(services_dep)) -> str:
    return services.mastery.passport_markdown(learner_id, locale)
