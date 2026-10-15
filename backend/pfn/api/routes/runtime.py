"""Direct execution endpoints (used by the scratch console and by tests)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from pfn.api.deps import Services, learner_dep, mode_dep, services_dep
from pfn.runtime.service import RunRequest

router = APIRouter(prefix="/api/runtime", tags=["runtime"])


class RunPayload(BaseModel):
    files: dict[str, str]
    entry: str = Field(default="main.py")
    trace: bool = False


class TestPayload(BaseModel):
    files: dict[str, str]
    tests: dict[str, str]


@router.get("/python")
def python_info(services: Services = Depends(services_dep)) -> dict:
    return services.executions.python_info()


@router.post("/run")
def run(payload: RunPayload, mode: str = Depends(mode_dep),
        services: Services = Depends(services_dep)) -> dict:
    return services.executions.run(
        RunRequest(files=payload.files, kind="script", entry=payload.entry, mode=mode,
                   trace=payload.trace)
    ).to_dict()


@router.post("/test")
def run_tests(payload: TestPayload, mode: str = Depends(mode_dep),
              learner_id: str = Depends(learner_dep),
              services: Services = Depends(services_dep)) -> dict:
    return services.executions.run_tests(payload.files, payload.tests, mode=mode)
