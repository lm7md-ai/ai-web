"""Execution service: prepares sandboxes, launches workers, enforces wall limits.

This is the single entry point used by every feature that runs Python
(lessons, missions, worlds, projects, library examples, hidden tests,
career tasks and research runs).
"""

from __future__ import annotations

import contextlib
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pfn.config import Settings, get_settings
from pfn.runtime.policy import PRESETS, Limits, Mode, policy_for
from pfn.security.paths import write_files

WORKER = Path(__file__).with_name("worker.py")


@dataclass(slots=True)
class RunRequest:
    files: dict[str, str]
    kind: str = "script"  # script | function | program
    entry: str = "main.py"
    module: str = "main"
    target: str = "program"
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    world: dict | None = None
    mode: Mode = "native"
    trace: bool = False
    limits: Limits | None = None

    def job(self) -> dict:
        limits = self.limits or PRESETS.get(self.mode, PRESETS["native"])
        return {
            "kind": self.kind,
            "entry": self.entry,
            "module": self.module,
            "target": self.target,
            "args": self.args,
            "kwargs": self.kwargs,
            "world": self.world,
            "mode": self.mode,
            "trace": self.trace,
            "limits": limits.to_dict(),
        }


@dataclass(slots=True)
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    result: Any
    error: dict | None
    trace: dict | None
    world: dict | None
    metrics: dict
    mode: str
    kind: str
    run_id: str = ""

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "result": self.result,
            "error": self.error,
            "trace": self.trace,
            "world": self.world,
            "metrics": self.metrics,
            "mode": self.mode,
            "kind": self.kind,
            "run_id": self.run_id,
        }


class ExecutionService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.settings.ensure_dirs()
        self.runs_dir = Path(self.settings.runs_dir)

    # -------------------------------------------------------------- execute
    def run(self, request: RunRequest, keep_dir: bool = False) -> RunResult:
        mode = request.mode
        if mode == "isolated" and not self.settings.allow_untrusted_isolated:
            raise PermissionError("isolated execution is disabled by configuration")
        policy = policy_for(mode, trace=request.trace)
        limits = request.limits or policy.limits
        run_id = "run_" + uuid.uuid4().hex[:12]
        run_dir = Path(tempfile.mkdtemp(prefix=run_id + "_", dir=str(self.runs_dir)))
        started = time.perf_counter()
        try:
            write_files(
                run_dir,
                request.files,
                max_bytes=limits.max_file_bytes,
                max_files=limits.max_files,
            )
            job = request.job()
            job_path = run_dir / "job.json"
            out_path = run_dir / "result.json"
            job_path.write_text(json.dumps(job, ensure_ascii=False), encoding="utf-8")

            cmd = [sys.executable, "-I", str(WORKER), str(job_path), str(out_path)]
            env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": str(run_dir),
                "TMPDIR": str(run_dir),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "MPLBACKEND": "Agg",
                "MPLCONFIGDIR": str(run_dir),
            }
            if platform.system() == "Windows":  # pragma: no cover
                env.update({"SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "TEMP": str(run_dir)})

            timed_out = False
            returncode = -1
            proc = subprocess.Popen(
                cmd,
                cwd=str(run_dir),
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            try:
                proc.communicate(timeout=limits.wall_seconds)
                returncode = proc.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                self._kill_tree(proc)
                with contextlib.suppress(Exception):
                    proc.communicate(timeout=5)

            payload: dict | None = None
            if out_path.exists():
                with contextlib.suppress(Exception):
                    payload = json.loads(out_path.read_text(encoding="utf-8"))
            if payload is None:
                payload = {
                    "ok": False,
                    "stdout": "",
                    "stderr": "",
                    "result": None,
                    "error": {
                        "type": "TimeoutError" if timed_out else "WorkerCrash",
                        "message": (
                            f"execution exceeded the wall-clock limit of {limits.wall_seconds}s "
                            "and was terminated"
                            if timed_out
                            else f"the sandbox worker exited with code {returncode} "
                            "without producing a report (killed by the OS, out of memory, "
                            "or crashed at interpreter start)"
                        ),
                        "frames": [],
                        "traceback": "",
                    },
                    "trace": None,
                    "world": None,
                    "metrics": {"duration_ms": int((time.perf_counter() - started) * 1000)},
                    "mode": mode,
                    "kind": request.kind,
                }
            payload.setdefault("metrics", {})["wall_ms"] = int((time.perf_counter() - started) * 1000)
            payload["metrics"]["returncode"] = returncode
            payload["metrics"]["timed_out"] = timed_out
            payload["run_id"] = run_id
            return RunResult(**{k: payload.get(k) for k in RunResult.__slots__ if k != "run_id"}, run_id=run_id)
        finally:
            if not keep_dir:
                shutil.rmtree(run_dir, ignore_errors=True)

    # ----------------------------------------------------------- test suite
    def run_tests(
        self,
        files: dict[str, str],
        test_files: dict[str, str],
        mode: Mode = "native",
        timeout: int | None = None,
        keep_dir: bool = False,
    ) -> dict:
        """Run real pytest against learner code and parse the JUnit XML report."""
        run_id = "tst_" + uuid.uuid4().hex[:12]
        run_dir = Path(tempfile.mkdtemp(prefix=run_id + "_", dir=str(self.runs_dir)))
        report_path = run_dir / "report.xml"
        started = time.perf_counter()
        try:
            write_files(run_dir, files)
            write_files(run_dir, {f"tests/{name}": src for name, src in test_files.items()})
            (run_dir / "tests" / "__init__.py").write_text("", encoding="utf-8")
            cmd = [
                sys.executable,
                "-I",
                "-m",
                "pytest",
                "tests",
                "-q",
                "--no-header",
                "-p",
                "no:cacheprovider",
                f"--junitxml={report_path}",
            ]
            env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": str(run_dir),
                "TMPDIR": str(run_dir),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "MPLBACKEND": "Agg",
            }
            wall = timeout or PRESETS["test"].wall_seconds
            try:
                completed = subprocess.run(
                    cmd,
                    cwd=str(run_dir),
                    env=env,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    timeout=wall,
                    start_new_session=True,
                )
                output, returncode = completed.stdout + completed.stderr, completed.returncode
                timed_out = False
            except subprocess.TimeoutExpired as exc:
                output = (exc.stdout or "") + (exc.stderr or "")
                returncode = -1
                timed_out = True

            cases = parse_junit(report_path) if report_path.exists() else []
            passed = sum(1 for c in cases if c["outcome"] == "passed")
            failed = sum(1 for c in cases if c["outcome"] in ("failed", "error"))
            return {
                "run_id": run_id,
                "ok": returncode == 0 and failed == 0 and passed > 0,
                "passed": passed,
                "failed": failed,
                "total": len(cases),
                "cases": cases,
                "output": output[-8000:],
                "timed_out": timed_out,
                "returncode": returncode,
                "duration_ms": int((time.perf_counter() - started) * 1000),
            }
        finally:
            if not keep_dir:
                shutil.rmtree(run_dir, ignore_errors=True)

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _kill_tree(proc: subprocess.Popen) -> None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            with contextlib_suppress():
                proc.kill()

    def python_info(self) -> dict:
        import importlib.metadata as md

        wanted = [
            "numpy",
            "pandas",
            "polars",
            "scikit-learn",
            "scipy",
            "sympy",
            "matplotlib",
            "fastapi",
            "pydantic",
            "pytest",
            "duckdb",
            "torch",
        ]
        installed = {}
        for name in wanted:
            try:
                installed[name] = md.version(name)
            except Exception:
                installed[name] = None
        return {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "executable": sys.executable,
            "packages": installed,
        }

    def cleanup_old_runs(self, max_age_hours: int = 24) -> int:
        cutoff = time.time() - max_age_hours * 3600
        removed = 0
        for entry in self.runs_dir.iterdir() if self.runs_dir.exists() else []:
            try:
                if entry.is_dir() and entry.stat().st_mtime < cutoff:
                    shutil.rmtree(entry, ignore_errors=True)
                    removed += 1
            except OSError:  # pragma: no cover
                continue
        return removed


def parse_junit(path: Path) -> list[dict]:
    """Parse a JUnit XML report into a compact list of test cases."""
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError):
        return []
    cases: list[dict] = []
    for case in tree.iter("testcase"):
        outcome = "passed"
        message = ""
        detail = ""
        for child in case:
            if child.tag in ("failure", "error"):
                outcome = "failed" if child.tag == "failure" else "error"
                message = (child.get("message") or "")[:800]
                detail = (child.text or "")[:1200]
                break
            if child.tag == "skipped":
                outcome = "skipped"
        cases.append(
            {
                "name": case.get("name", "?"),
                "classname": case.get("classname", ""),
                "outcome": outcome,
                "message": message,
                "detail": detail,
                "time": float(case.get("time") or 0.0),
            }
        )
    return cases
