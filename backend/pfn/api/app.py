"""FastAPI application factory."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pfn.api.deps import Services, get_services, init_services
from pfn.api.routes import assessment, curriculum, learners, library, mentor, missions, projects
from pfn.api.routes import runtime, skills, system, worlds
from pfn.config import Settings

log = logging.getLogger("pfn.api")

ROUTERS = (
    system.router,
    learners.router,
    curriculum.router,
    missions.router,
    worlds.router,
    projects.router,
    library.router,
    mentor.router,
    skills.router,
    assessment.router,
    runtime.router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    services = init_services(getattr(app.state, "settings", None))
    app.state.services = services
    log.info("python-forge-nexus ready: %s", services.settings.version)
    yield
    services.db.close()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="An executable Python learning platform: real execution, real tests, real evidence.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(KeyError)
    async def _not_found(request: Request, exc: KeyError):
        return JSONResponse(status_code=404, content={"detail": f"not found: {exc.args[0]}"})

    @app.exception_handler(ValueError)
    async def _bad_request(request: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(PermissionError)
    async def _forbidden(request: Request, exc: PermissionError):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(FileNotFoundError)
    async def _missing(request: Request, exc: FileNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    for router in ROUTERS:
        app.include_router(router)

    @app.get("/", include_in_schema=False)
    def root() -> dict:
        services: Services = get_services()
        return {
            "app": services.settings.app_name,
            "version": services.settings.version,
            "docs": "/docs",
            "api": services.settings.api_prefix,
        }

    return app


app = create_app()
