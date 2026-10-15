"""Curriculum endpoints: browse, run, submit (graded by real pytest)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from pfn.api.deps import Services, learner_dep, locale_dep, mode_dep, services_dep

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

SPEC_NAMES = ("task", "assessment", "transfer_task")
STATUSES = ("not_started", "in_progress", "completed", "skipped")


class CodePayload(BaseModel):
    code: str | None = None


class ExperimentPayload(BaseModel):
    code: str = Field(min_length=1)


class SubmitPayload(BaseModel):
    code: str = Field(min_length=1)
    spec: str = Field(default="task", pattern="^(task|assessment|transfer_task)$")
    public_only: bool = False
    hints_used: int = Field(default=0, ge=0, le=99)
    assistance_level: str = Field(default="independent", pattern="^(independent|hints|solution)$")


class StatusPayload(BaseModel):
    status: str = Field(pattern="^(not_started|in_progress|completed|skipped)$")


@router.get("")
def list_modules(locale: str = Depends(locale_dep), level: int | None = Query(None, ge=0, le=11),
                 services: Services = Depends(services_dep)) -> dict:
    modules = services.curriculum.to_dict(locale, level)
    return {"locale": locale, "level": level, "count": len(modules), "modules": modules}


@router.get("/levels")
def levels(services: Services = Depends(services_dep)) -> dict:
    counts: dict[int, int] = {}
    for module in services.curriculum.all():
        counts[module.level] = counts.get(module.level, 0) + 1
    return {"levels": [{"level": k, "modules": v} for k, v in sorted(counts.items())]}


@router.get("/progress")
def progress(learner_id: str = Depends(learner_dep),
             services: Services = Depends(services_dep)) -> dict:
    return {"learner_id": learner_id, "progress": services.curriculum.progress(learner_id)}


@router.get("/{module_id}")
def get_module(module_id: str, locale: str = Depends(locale_dep),
               learner_id: str = Depends(learner_dep),
               services: Services = Depends(services_dep)) -> dict:
    module = services.curriculum.get(module_id).to_dict(locale)
    module["progress"] = services.curriculum.progress(learner_id).get(module_id, {})
    return module


@router.get("/{module_id}/task")
def get_task(module_id: str, spec: str = Query("task"), locale: str = Depends(locale_dep),
             services: Services = Depends(services_dep)) -> dict:
    if spec not in SPEC_NAMES:
        raise ValueError(f"spec must be one of {SPEC_NAMES}")
    module = services.curriculum.get(module_id)
    task = getattr(module, spec)
    if task is None:
        raise KeyError(f"{module_id} has no {spec}")
    return {
        "module_id": module_id,
        "spec": spec,
        "brief": task.brief(locale),
        "starter_code": task.starter_code,
        "entry_filename": task.entry_filename,
        "independent": task.independent,
        "hints_available": len(task.hints),
        "extra_files": sorted(task.extra_files),
        "public_tests": sorted(task.public_tests),
    }


@router.post("/{module_id}/example")
def run_example(module_id: str, payload: CodePayload | None = None, mode: str = Depends(mode_dep),
                learner_id: str = Depends(learner_dep),
                services: Services = Depends(services_dep)) -> dict:
    code = payload.code if payload else None
    return services.curriculum.run_example(learner_id, module_id, code, mode)


@router.post("/{module_id}/experiment")
def run_experiment(module_id: str, payload: ExperimentPayload, mode: str = Depends(mode_dep),
                   learner_id: str = Depends(learner_dep),
                   services: Services = Depends(services_dep)) -> dict:
    return services.curriculum.run_experiment(learner_id, module_id, payload.code, mode)


@router.post("/{module_id}/submit")
def submit(module_id: str, payload: SubmitPayload, mode: str = Depends(mode_dep),
           learner_id: str = Depends(learner_dep),
           services: Services = Depends(services_dep)) -> dict:
    """Grade with real pytest. Hidden tests stay on the server."""
    return services.curriculum.submit_task(
        learner_id=learner_id,
        module_id=module_id,
        spec_name=payload.spec,
        code=payload.code,
        mode=mode,
        assistance_level=payload.assistance_level,
        hints_used=payload.hints_used,
        public_only=payload.public_only,
    )


@router.post("/{module_id}/status")
def set_status(module_id: str, payload: StatusPayload, learner_id: str = Depends(learner_dep),
               services: Services = Depends(services_dep)) -> dict:
    services.curriculum.mark_status(learner_id, module_id, payload.status)
    return {"module_id": module_id, "status": payload.status}
