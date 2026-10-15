"""Real execution tracing for Python X-Ray and the Code Time Machine.

This uses :func:`sys.settrace` on the *actual* interpreter, so every snapshot
in the UI comes from a genuine run.  Nothing here invents interpreter state:
if the tracer cannot observe something (for example C-level frames), it simply
does not report it.
"""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass, field
from typing import Any

MAX_REPR = 120
MAX_LOCALS = 24
MAX_STRINGS = 600


class StepLimitExceeded(RuntimeError):
    """Raised when the traced program exceeds its step budget.

    This is the mechanism that stops accidental infinite loops; the limit is a
    *step* limit (traced events), which is deterministic, unlike wall-clock time.
    """


def _safe_repr(value: Any, depth: int = 0) -> str:
    if depth > 2:
        return "…"
    try:
        text = repr(value)
    except Exception as exc:  # pragma: no cover - exotic __repr__ failures
        return f"<unrepresentable {type(value).__name__}: {exc.__class__.__name__}>"
    if len(text) > MAX_REPR:
        text = text[: MAX_REPR - 1] + "…"
    return text


_SCALAR = (int, float, bool, complex, str, bytes, type(None))


def describe(value: Any, depth: int = 0) -> dict:
    """Summarise a runtime value without trusting user ``__repr__`` too much."""
    info: dict[str, Any] = {
        "type": type(value).__name__,
        "repr": _safe_repr(value, depth),
        "id": id(value),
    }
    if isinstance(value, _SCALAR):
        info["kind"] = "scalar"
        if isinstance(value, str):
            info["length"] = len(value)
    elif isinstance(value, (list, tuple, set, frozenset)):
        info["kind"] = "sequence"
        info["length"] = len(value)
        if depth < 2 and len(value) <= 8:
            info["items"] = [describe(item, depth + 1) for item in list(value)[:8]]
    elif isinstance(value, dict):
        info["kind"] = "mapping"
        info["length"] = len(value)
        if depth < 2 and len(value) <= 8:
            info["items"] = [
                {"key": _safe_repr(k, depth), "value": describe(v, depth + 1)}
                for k, v in list(value.items())[:8]
            ]
    elif isinstance(value, types.GeneratorType):
        info["kind"] = "generator"
    elif callable(value):
        info["kind"] = "callable"
        info["qualname"] = getattr(value, "__qualname__", type(value).__name__)
    else:
        info["kind"] = "object"
    return info


@dataclass(slots=True)
class Frame:
    index: int
    event: str
    function: str
    filename: str
    line: int
    depth: int
    locals: dict = field(default_factory=dict)
    stack: list = field(default_factory=list)
    value: dict | None = None
    note: str | None = None


class Tracer:
    """Collects a bounded, replayable trace of a Python run."""

    def __init__(
        self,
        max_steps: int = 25_000,
        capture_locals: bool = True,
        max_frames: int = 4_000,
        root: str | None = None,
    ):
        self.root = root
        self.max_steps = max_steps
        self.capture_locals = capture_locals
        self.max_frames = max_frames
        self.frames: list[Frame] = []
        self.steps = 0
        self.calls: list[dict] = []
        self.returns: list[dict] = []
        self.exceptions: list[dict] = []
        self._depth = 0
        self.truncated = False
        self._seen_ids: dict[int, str] = {}

    # ------------------------------------------------------------------ API
    def __call__(self, frame, event, arg):  # noqa: ANN001
        return self._trace(frame, event, arg)

    def _trace(self, frame, event, arg):  # noqa: ANN001
        self.steps += 1
        if self.steps > self.max_steps:
            self.truncated = True
            raise StepLimitExceeded(
                f"execution stopped after {self.max_steps} traced steps "
                "(possible infinite loop or very heavy computation)"
            )
        if len(self.frames) >= self.max_frames:
            self.truncated = True
            return None
        code = frame.f_code
        filename = code.co_filename
        if "pfn/runtime" in filename or filename.endswith("worker.py"):
            return None
        if self.root is not None and not filename.startswith(str(self.root)):
            # Only learner code is traced: interpreter and library internals are
            # not part of the educational picture and would flood the timeline.
            return None
        if event == "call":
            self._depth += 1
            if self._depth > 40:
                self._depth -= 1
                return None
        elif event == "return":
            args = frame.f_locals
            self.returns.append(
                {
                    "function": code.co_name,
                    "line": frame.f_lineno,
                    "value": _safe_repr(arg),
                }
            )
            self._depth = max(0, self._depth - 1)
        elif event == "exception":
            exc_type, exc_value, _tb = arg
            self.exceptions.append(
                {
                    "type": getattr(exc_type, "__name__", str(exc_type)),
                    "message": str(exc_value)[:400],
                    "line": frame.f_lineno,
                    "function": code.co_name,
                }
            )

        if event in ("line", "call", "return", "exception"):
            snapshot: dict[str, dict] = {}
            if self.capture_locals:
                for name, value in list(frame.f_locals.items())[:MAX_LOCALS]:
                    if name.startswith("__"):
                        continue
                    try:
                        snapshot[name] = describe(value)
                    except Exception:  # pragma: no cover - defensive
                        snapshot[name] = {"type": "unknown", "repr": "<?>", "kind": "unknown"}
            stack = []
            f = frame
            while f is not None and len(stack) < 12:
                stack.append({"function": f.f_code.co_name, "line": f.f_lineno})
                f = f.f_back
            self.frames.append(
                Frame(
                    index=len(self.frames),
                    event=event,
                    function=code.co_name,
                    filename=filename.split("/")[-1],
                    line=frame.f_lineno,
                    depth=self._depth,
                    locals=snapshot,
                    stack=stack,
                    value=describe(arg) if event == "return" and arg is not None else None,
                )
            )
        return self._trace if event == "call" else self

    # ------------------------------------------------------------- context
    def __enter__(self) -> "Tracer":
        sys.settrace(self._trace)
        return self

    def __exit__(self, *_exc) -> None:
        sys.settrace(None)

    # -------------------------------------------------------------- export
    def to_dict(self) -> dict:
        return {
            "frames": [
                {
                    "index": f.index,
                    "event": f.event,
                    "function": f.function,
                    "filename": f.filename,
                    "line": f.line,
                    "depth": f.depth,
                    "locals": f.locals,
                    "stack": f.stack,
                    "value": f.value,
                }
                for f in self.frames
            ],
            "calls": self.calls,
            "returns": self.returns[-200:],
            "exceptions": self.exceptions[-50:],
            "steps": self.steps,
            "truncated": self.truncated,
            "limitations": [
                "C-level frames (builtins, numpy internals) are not traced.",
                "Snapshots store reprs and ids, not live objects; identity is "
                "recorded as the CPython id() at trace time.",
                "The trace is bounded by the step limit, so long runs are truncated.",
            ],
        }
