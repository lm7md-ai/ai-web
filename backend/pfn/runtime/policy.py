"""Execution policies and resource limits.

Three modes are supported and are *never* silently substituted for one another:

``native``
    Trusted, developer-owned code executed with the same interpreter as the
    backend.  Resource limits still apply, but no import restriction is added.
``isolated``
    Untrusted / imported code.  Adds import + network guards on top of the
    resource limits.  This is defence in depth, **not** a true sandbox: see
    ``SECURITY.md`` for the residual risks of this deployment model.
``browser``
    Pyodide in the learner's browser (frontend side).  The backend exposes the
    contract only; no code is executed server-side for this mode.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal

Mode = Literal["native", "isolated", "browser"]


@dataclass(frozen=True, slots=True)
class Limits:
    cpu_seconds: int = 8
    wall_seconds: int = 20
    memory_mb: int = 768
    max_steps: int = 250_000
    max_output_bytes: int = 128_000
    max_file_bytes: int = 400_000  # per source file written into the sandbox
    max_files: int = 120
    max_processes: int = 64
    allow_network: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


PRESETS: dict[str, Limits] = {
    "native": Limits(cpu_seconds=6, wall_seconds=15, memory_mb=1024, max_steps=500_000),
    "isolated": Limits(
        cpu_seconds=5,
        wall_seconds=12,
        memory_mb=768,
        max_steps=200_000,
        allow_network=False,
    ),
    "lesson": Limits(cpu_seconds=4, wall_seconds=10, memory_mb=384, max_steps=100_000),
    "test": Limits(cpu_seconds=20, wall_seconds=60, memory_mb=1024, max_steps=1_000_000),
}


@dataclass(frozen=True, slots=True)
class Policy:
    mode: Mode = "native"
    limits: Limits = field(default_factory=lambda: PRESETS["native"])
    trace: bool = False
    allow_imports: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        data = asdict(self)
        data["limits"] = self.limits.to_dict()
        return data


# Modules refused outright.  ``subprocess`` and ``ctypes`` are NOT in this list
# because pandas/scipy/sklearn import them at import time; their dangerous
# capabilities are disabled separately by guards.install_process_guard() and
# guards.install_native_loading_guard().
# Modules refused outright.  The science stack (numpy/pandas/scipy/sklearn)
# imports ``socket`` and ``subprocess`` at import time, so those two stay
# importable and their dangerous *capabilities* are disabled at runtime by
# ``guards.install_network_guard`` / ``install_process_guard`` instead.
BLOCKED_IMPORTS: tuple[str, ...] = (
    "webbrowser",
    "http.client",
    "urllib.request",
    "ftplib",
    "smtplib",
    "telnetlib",
    "pty",
    "resource",
    "ssl",
)

DANGEROUS_BUILTINS: tuple[str, ...] = ("exit", "quit", "help", "input")


def policy_for(mode: str, *, trace: bool = False) -> Policy:
    if mode not in ("native", "isolated"):
        raise ValueError(f"unknown execution mode: {mode}")
    return Policy(mode=mode, limits=PRESETS.get(mode, PRESETS["native"]), trace=trace)
