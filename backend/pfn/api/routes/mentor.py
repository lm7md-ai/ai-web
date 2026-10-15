"""AI Mentor Council endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from pfn.api.deps import Services, learner_dep, locale_dep, services_dep

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


class AskPayload(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    mentor_id: str = Field(default="coach")
    files: dict[str, str] | None = None
    run_report: dict | None = None


class ReviewPayload(BaseModel):
    files: dict[str, str]
    entry: str = Field(default="main.py")


class HintPayload(BaseModel):
    goal: str = Field(min_length=1, max_length=1000)
    failures: list[dict] | None = None
    code: str | None = None
    level: int = Field(default=1, ge=1, le=4)


@router.get("/mentors")
def mentors(locale: str = Depends(locale_dep), services: Services = Depends(services_dep)) -> dict:
    return {"locale": locale, "mentors": services.mentor.mentors(locale)}


@router.get("/status")
def status(services: Services = Depends(services_dep)) -> dict:
    """Honest status: tells the UI whether a real model answered."""
    return services.mentor.status()


@router.post("/ask")
def ask(payload: AskPayload, locale: str = Depends(locale_dep),
        learner_id: str = Depends(learner_dep),
        services: Services = Depends(services_dep)) -> dict:
    return services.mentor.ask(
        learner_id=learner_id,
        question=payload.question,
        locale=locale,
        mentor_id=payload.mentor_id,
        files=payload.files,
        run_report=payload.run_report,
    )


@router.post("/council")
def council(payload: AskPayload, locale: str = Depends(locale_dep),
            learner_id: str = Depends(learner_dep),
            services: Services = Depends(services_dep)) -> dict:
    return services.mentor.council(
        learner_id=learner_id,
        question=payload.question,
        locale=locale,
        files=payload.files,
        run_report=payload.run_report,
    )


@router.post("/review")
def review(payload: ReviewPayload, locale: str = Depends(locale_dep),
           learner_id: str = Depends(learner_dep),
           services: Services = Depends(services_dep)) -> dict:
    return services.mentor.review(learner_id, payload.files, locale, payload.entry)


@router.post("/hint")
def hint(payload: HintPayload, locale: str = Depends(locale_dep),
         learner_id: str = Depends(learner_dep),
         services: Services = Depends(services_dep)) -> dict:
    return services.mentor.hint(
        learner_id=learner_id,
        goal=payload.goal,
        failures=payload.failures,
        code=payload.code,
        level=payload.level,
        locale=locale,
    )


@router.get("/history")
def history(limit: int = Query(30, ge=1, le=200), learner_id: str = Depends(learner_dep),
            services: Services = Depends(services_dep)) -> dict:
    return {"items": services.mentor.history(learner_id, limit)}
