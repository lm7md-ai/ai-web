"""Learner profile and preferences (single-user friendly)."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from pfn.api.deps import DEFAULT_LEARNER, Services, learner_dep, services_dep

router = APIRouter(prefix="/api", tags=["learner"])

ASSISTANCE_MODES = "^(full_support|hints_only|exam_mode|independent)$"
MENTOR_ROLES = "^(architect|debugger|reviewer|coach|researcher|teacher)$"


class LearnerUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    locale: str | None = Field(default=None, pattern="^(ar|en)$")
    theme: str | None = Field(default=None, pattern="^(dark|light)$")
    goals: list[str] | None = None
    onboarded: bool | None = None


class PreferencesUpdate(BaseModel):
    assistance_mode: str | None = Field(default=None, pattern=ASSISTANCE_MODES)
    hints_enabled: bool | None = None
    trace_enabled: bool | None = None
    execution_mode: str | None = Field(default=None, pattern="^(native|isolated)$")
    mentor_role: str | None = Field(default=None, pattern=MENTOR_ROLES)
    daily_goal_minutes: int | None = Field(default=None, ge=5, le=600)


def _public(learner: dict) -> dict:
    if not learner:
        return {}
    data = dict(learner)
    try:
        data["goals"] = json.loads(data.get("goals_json") or "[]")
    except ValueError:
        data["goals"] = []
    return data


@router.get("/learner")
def get_learner(learner_id: str = Depends(learner_dep),
                services: Services = Depends(services_dep)) -> dict:
    services.learners.ensure_default(learner_id)
    return {
        "learner": _public(services.learners.get(learner_id) or {}),
        "preferences": services.learners.get_preferences(learner_id),
        "default_learner_id": DEFAULT_LEARNER,
    }


@router.patch("/learner")
def update_learner(payload: LearnerUpdate, learner_id: str = Depends(learner_dep),
                   services: Services = Depends(services_dep)) -> dict:
    services.learners.ensure_default(learner_id)
    fields = payload.model_dump(exclude_none=True)
    goals = fields.pop("goals", None)
    if fields:
        services.learners.update(learner_id, **fields)
    if goals is not None:
        services.learners.set_goals(learner_id, goals)
    return {
        "learner": _public(services.learners.get(learner_id) or {}),
        "preferences": services.learners.get_preferences(learner_id),
    }


@router.get("/learner/preferences")
def preferences(learner_id: str = Depends(learner_dep),
                services: Services = Depends(services_dep)) -> dict:
    services.learners.ensure_default(learner_id)
    return services.learners.get_preferences(learner_id)


@router.put("/learner/preferences")
def update_preferences(payload: PreferencesUpdate, learner_id: str = Depends(learner_dep),
                       services: Services = Depends(services_dep)) -> dict:
    services.learners.ensure_default(learner_id)
    return services.learners.update_preferences(learner_id, **payload.model_dump(exclude_none=True))
