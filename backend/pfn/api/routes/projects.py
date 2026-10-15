"""Multi-file project workbench."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from pfn.api.deps import Services, learner_dep, mode_dep, services_dep

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreatePayload(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")
    title: str | None = Field(default=None, max_length=120)
    template: str = Field(default="blank")
    description: str = Field(default="", max_length=2000)


class FilesPayload(BaseModel):
    files: dict[str, str]
    commit: bool = False
    message: str = Field(default="work saved", max_length=200)


class RunPayload(BaseModel):
    entry: str = Field(default="main.py")
    trace: bool = False


class TestPayload(BaseModel):
    tests: dict[str, str] | None = None


class RollbackPayload(BaseModel):
    version: int = Field(ge=1)


@router.get("/templates")
def templates(services: Services = Depends(services_dep)) -> dict:
    return {"templates": services.projects.templates()}


@router.get("")
def list_projects(learner_id: str = Depends(learner_dep),
                  services: Services = Depends(services_dep)) -> dict:
    projects = services.projects.list_projects(learner_id)
    return {"count": len(projects), "projects": projects}


@router.post("")
def create(payload: CreatePayload, learner_id: str = Depends(learner_dep),
           services: Services = Depends(services_dep)) -> dict:
    return services.projects.create(
        learner_id=learner_id,
        slug=payload.slug,
        title=payload.title,
        template=payload.template,
        description=payload.description,
    )


@router.get("/{project_id}")
def get_project(project_id: str, learner_id: str = Depends(learner_dep),
                services: Services = Depends(services_dep)) -> dict:
    return services.projects.get(learner_id, project_id)


@router.put("/{project_id}/files")
def save_files(project_id: str, payload: FilesPayload, learner_id: str = Depends(learner_dep),
               services: Services = Depends(services_dep)) -> dict:
    return services.projects.save_files(
        learner_id, project_id, payload.files, commit=payload.commit, message=payload.message
    )


@router.delete("/{project_id}/files/{path:path}")
def delete_file(project_id: str, path: str, learner_id: str = Depends(learner_dep),
                services: Services = Depends(services_dep)) -> dict:
    return services.projects.delete_file(learner_id, project_id, path)


@router.post("/{project_id}/run")
def run_project(project_id: str, payload: RunPayload, mode: str = Depends(mode_dep),
                learner_id: str = Depends(learner_dep),
                services: Services = Depends(services_dep)) -> dict:
    return services.projects.run(learner_id, project_id, payload.entry, mode, payload.trace)


@router.post("/{project_id}/test")
def test_project(project_id: str, payload: TestPayload | None = None, mode: str = Depends(mode_dep),
                 learner_id: str = Depends(learner_dep),
                 services: Services = Depends(services_dep)) -> dict:
    tests = payload.tests if payload else None
    return services.projects.test(learner_id, project_id, tests, mode)


@router.get("/{project_id}/versions")
def versions(project_id: str, learner_id: str = Depends(learner_dep),
             services: Services = Depends(services_dep)) -> dict:
    services.projects.get(learner_id, project_id)
    return {"project_id": project_id, "versions": services.projects.versions(project_id)}


@router.post("/{project_id}/commit")
def commit(project_id: str, message: str = Query("work saved", max_length=200),
           learner_id: str = Depends(learner_dep),
           services: Services = Depends(services_dep)) -> dict:
    version = services.projects.commit(learner_id, project_id, message)
    return {"project_id": project_id, "version": version}


@router.post("/{project_id}/rollback")
def rollback(project_id: str, payload: RollbackPayload, learner_id: str = Depends(learner_dep),
             services: Services = Depends(services_dep)) -> dict:
    return services.projects.rollback(learner_id, project_id, payload.version)
