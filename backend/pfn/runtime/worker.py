"""Sandbox worker: executes one learner job in a separate, limited process.

Invoked as::

    python -I worker.py <job.json> <result.json>

Design notes
------------
* The parent process writes all source files into a private run directory and
  passes only paths; the worker never trusts user input beyond JSON parsing.
* Resource limits are applied *before* any learner code is imported.
* Every failure path writes a result file, so the parent never hangs.
* ``-I`` (isolated) removes the script directory and user site-packages from
  ``sys.path``; we deliberately re-add the run directory so the learner's own
  modules are importable, and nothing else.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import signal
import sys
import time
import traceback
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from pfn.runtime.serde import jsonable  # noqa: E402


class JobError(Exception):
    pass


class _CappedWriter:
    """Write to a file, silently dropping output beyond the byte budget."""

    def __init__(self, stream, limit: int, sink: io.StringIO) -> None:
        self._stream = stream
        self._limit = limit
        self._written = 0
        self._sink = sink
        self.truncated = False

    def write(self, text: str) -> int:
        encoded = text.encode("utf-8", errors="replace")
        if self._written + len(encoded) > self._limit:
            remaining = max(0, self._limit - self._written)
            if remaining:
                self._stream.write(encoded[:remaining].decode("utf-8", errors="replace"))
                self._sink.write(encoded[:remaining].decode("utf-8", errors="replace"))
                self._written += remaining
            self.truncated = True
            return len(text)
        self._stream.write(text)
        self._sink.write(text)
        self._written += len(encoded)
        return len(text)

    def flush(self) -> None:
        with contextlib.suppress(Exception):
            self._stream.flush()


def _apply_limits(limits: dict) -> None:
    try:
        import resource
    except ImportError:  # pragma: no cover - non-POSIX
        return
    cpu = int(limits.get("cpu_seconds", 5))

    def _handler(signum, frame):  # noqa: ANN001
        raise TimeoutError(f"CPU time limit exceeded ({cpu}s)")

    signal.signal(signal.SIGXCPU, _handler)
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 1))
        mem = int(limits.get("memory_mb", 512)) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024 * 1024, 32 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
        nproc = int(limits.get("max_processes", 64))
        resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
    except (ValueError, OSError) as exc:  # pragma: no cover - platform dependent
        sys.stderr.write(f"[worker] could not apply every limit: {exc}\n")


def _friendly_frames(exc: BaseException, run_dir: Path) -> list[dict]:
    frames = []
    for tb in traceback.extract_tb(exc.__traceback__):
        filename = str(tb.filename)
        if "pfn/runtime/worker.py" in filename:
            continue
        in_run = str(run_dir) in filename or not filename.startswith("/")
        frames.append(
            {
                "file": Path(filename).name if in_run else filename,
                "line": tb.lineno,
                "function": tb.name,
                "code": (tb.line or "").strip()[:200],
                "is_learner_code": in_run,
            }
        )
    return frames


def _run_module(entry: str, run_dir: Path):
    """Execute a script as ``__main__`` (equivalent to ``python entry.py``)."""
    import runpy

    path = (run_dir / entry).resolve()
    if run_dir not in path.parents and path != run_dir:
        raise JobError(f"entry point escapes the run directory: {entry}")
    if not path.exists():
        raise JobError(f"entry point not found: {entry}")
    runpy.run_path(str(path), run_name="__main__")


def _import_module(module_name: str, run_dir: Path):
    if str(run_dir) not in sys.path:
        sys.path.insert(0, str(run_dir))
    return importlib.import_module(module_name)


def _jsonify_result(value) -> dict:
    return {"value": jsonable(value), "type": type(value).__name__}


def main() -> int:  # noqa: C901 - a single controlled entry point
    job_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    run_dir = Path(job_path).parent
    started = time.perf_counter()

    job = json.loads(job_path.read_text(encoding="utf-8"))
    limits = job.get("limits", {})
    mode = job.get("mode", "native")
    result: dict = {
        "ok": False,
        "stdout": "",
        "stderr": "",
        "result": None,
        "error": None,
        "trace": None,
        "world": None,
        "metrics": {"duration_ms": 0, "steps": 0, "truncated": False, "output_truncated": False},
        "mode": mode,
        "kind": job.get("kind", "script"),
    }

    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    out_sink, err_sink = io.StringIO(), io.StringIO()
    try:
        _apply_limits(limits)
        if mode == "isolated":
            from pfn.runtime import guards
            from pfn.runtime.policy import BLOCKED_IMPORTS

            guards.install_import_guard(BLOCKED_IMPORTS)
            guards.install_network_guard()
            guards.install_builtin_guard()
            guards.install_pickle_guard()
            guards.install_process_guard()
            guards.install_native_loading_guard()
            import builtins

            builtins.open = guards.sandbox_open(str(run_dir))  # type: ignore[misc]

        with open(stdout_path, "w", encoding="utf-8", errors="replace") as so, open(
            stderr_path, "w", encoding="utf-8", errors="replace"
        ) as se:
            out_writer = _CappedWriter(so, int(limits.get("max_output_bytes", 128_000)), out_sink)
            err_writer = _CappedWriter(se, int(limits.get("max_output_bytes", 128_000)), err_sink)

            tracer = None
            trace_requested = bool(job.get("trace"))
            if trace_requested:
                from pfn.runtime.tracer import Tracer

                tracer = Tracer(
                    max_steps=int(limits.get("max_steps", 25_000)),
                    root=str(run_dir) + os.sep,
                )

            try:
                with contextlib.redirect_stdout(out_writer), contextlib.redirect_stderr(err_writer):  # type: ignore[arg-type]
                    if tracer is not None:
                        sys.settrace(tracer)
                    try:
                        kind = job.get("kind", "script")
                        if kind == "script":
                            _run_module(job.get("entry", "main.py"), run_dir)
                            result["result"] = None
                        elif kind == "function":
                            module = _import_module(job.get("module", "main"), run_dir)
                            target = job.get("target")
                            func = getattr(module, target, None)
                            if func is None:
                                raise JobError(
                                    f"function '{target}' was not found in {job.get('module')}.py. "
                                    f"Available names: "
                                    + ", ".join(sorted(n for n in vars(module) if not n.startswith("_"))[:20])
                                )
                            if not callable(func):
                                raise JobError(f"'{target}' exists but is not callable")
                            value = func(*job.get("args", []), **job.get("kwargs", {}))
                            result["result"] = _jsonify_result(value)
                        elif kind == "program":
                            world_spec = job.get("world") or {}
                            world_module = _import_module(world_spec.get("module", "pfnworld"), run_dir)
                            api, state = world_module.build(world_spec.get("config", {}))
                            module = _import_module(job.get("module", "main"), run_dir)
                            func = getattr(module, job.get("target", "program"), None)
                            if func is None:
                                raise JobError(
                                    f"define a function named '{job.get('target', 'program')}' "
                                    "that accepts the world API object"
                                )
                            func(api)
                            result["world"] = world_module.result(api, state)
                        else:
                            raise JobError(f"unknown job kind: {kind}")
                        result["ok"] = True
                    finally:
                        sys.settrace(None)
                        if tracer is not None:
                            result["trace"] = tracer.to_dict()
                            result["metrics"]["steps"] = tracer.steps
                            result["metrics"]["truncated"] = tracer.truncated
            except BaseException as exc:  # noqa: BLE001 - every failure must be reported
                result["ok"] = False
                tb_text = "".join(
                    traceback.format_exception(type(exc), exc, exc.__traceback__, limit=12)
                )
                result["error"] = {
                    "type": type(exc).__name__,
                    "message": str(exc)[:2000],
                    "frames": _friendly_frames(exc, run_dir),
                    "traceback": tb_text[-6000:],
                }
                err_writer.write(tb_text)
            result["metrics"]["output_truncated"] = out_writer.truncated or err_writer.truncated

        result["stdout"] = out_sink.getvalue()[-int(limits.get("max_output_bytes", 128_000)) :]
        result["stderr"] = err_sink.getvalue()[-int(limits.get("max_output_bytes", 128_000)) :]
    except BaseException as exc:  # noqa: BLE001 - worker must always report
        result["ok"] = False
        result["error"] = {
            "type": type(exc).__name__,
            "message": str(exc)[:2000],
            "frames": [],
            "traceback": traceback.format_exc()[-4000:],
        }
    finally:
        result["metrics"]["duration_ms"] = int((time.perf_counter() - started) * 1000)
        try:
            out_path.write_text(json.dumps(result, ensure_ascii=False, default=str), encoding="utf-8")
        except Exception as exc:  # pragma: no cover - last resort
            out_path.write_text(
                json.dumps({"ok": False, "error": {"type": "SerializationError", "message": str(exc)}}),
                encoding="utf-8",
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
