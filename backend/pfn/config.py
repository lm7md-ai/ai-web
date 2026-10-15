"""Application configuration.

Values are read from environment variables (``PFN_`` prefix) or a local ``.env``
file.  Nothing here is developer-machine specific: every path is resolved
relative to the repository root.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _repo_root() -> Path:
    """Repository root (the directory that contains ``backend/``)."""
    return Path(__file__).resolve().parents[2]


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser().resolve() if raw else default


@dataclass(slots=True)
class Settings:
    app_name: str = "Python Forge Nexus"
    version: str = "0.1.0"
    root: Path = field(default_factory=_repo_root)

    # --- storage -----------------------------------------------------------
    data_dir: Path = field(default_factory=lambda: _repo_root() / "var")
    db_path: Path | None = None
    projects_dir: Path | None = None
    runs_dir: Path | None = None
    career_dir: Path | None = None
    export_dir: Path | None = None

    # --- server ------------------------------------------------------------
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    api_prefix: str = "/api"

    # --- execution ---------------------------------------------------------
    execution_mode_default: str = "native"  # native | isolated
    allow_untrusted_isolated: bool = True
    max_wall_seconds: int = 20
    max_cpu_seconds: int = 10
    max_memory_mb: int = 768
    max_output_bytes: int = 128_000
    max_trace_steps: int = 25_000

    # --- ai providers ------------------------------------------------------
    ai_provider: str = "local"  # local | openai_compatible
    ai_base_url: str | None = None
    ai_model: str | None = None
    ai_timeout_seconds: int = 30

    # --- misc --------------------------------------------------------------
    default_locale: str = "ar"
    supported_locales: tuple[str, ...] = ("ar", "en")

    def __post_init__(self) -> None:
        self.data_dir = _env_path("PFN_DATA_DIR", self.data_dir)
        self.db_path = _env_path("PFN_DB_PATH", self.data_dir / "pfn.db")
        self.projects_dir = _env_path("PFN_PROJECTS_DIR", self.data_dir / "projects")
        self.runs_dir = _env_path("PFN_RUNS_DIR", self.data_dir / "runs")
        self.career_dir = _env_path("PFN_CAREER_DIR", self.data_dir / "career")
        self.export_dir = _env_path("PFN_EXPORT_DIR", self.data_dir / "exports")
        self.host = os.environ.get("PFN_HOST", self.host)
        self.port = int(os.environ.get("PFN_PORT", str(self.port)))
        self.execution_mode_default = os.environ.get("PFN_EXECUTION_MODE", self.execution_mode_default)
        self.ai_provider = os.environ.get("PFN_AI_PROVIDER", self.ai_provider)
        self.ai_base_url = os.environ.get("PFN_AI_BASE_URL", None)
        self.ai_model = os.environ.get("PFN_AI_MODEL", None)
        self.default_locale = os.environ.get("PFN_LOCALE", self.default_locale)
        origins = os.environ.get("PFN_CORS_ORIGINS")
        if origins:
            self.cors_origins = [o.strip() for o in origins.split(",") if o.strip()]

    def ensure_dirs(self) -> None:
        for path in (
            self.data_dir,
            self.projects_dir,
            self.runs_dir,
            self.career_dir,
            self.export_dir,
            self.db_path.parent,
        ):
            if path is not None:
                path.mkdir(parents=True, exist_ok=True)


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
