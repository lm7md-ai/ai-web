"""JSON-safe conversion of arbitrary Python results produced inside the runner."""

from __future__ import annotations

import dataclasses
import datetime as dt
import decimal
from pathlib import Path
from typing import Any

MAX_ITEMS = 400
MAX_ROWS = 200
MAX_STRING = 20_000


def _clip(text: str) -> str:
    return text if len(text) <= MAX_STRING else text[:MAX_STRING] + "…[truncated]"


def jsonable(value: Any, depth: int = 0) -> Any:
    """Best-effort conversion to JSON-compatible data, never raising."""
    if depth > 6:
        return "<max depth>"
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return str(value)
        return value
    if isinstance(value, str):
        return _clip(value)
    if isinstance(value, (decimal.Decimal,)):
        return float(value)
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: jsonable(getattr(value, f.name), depth + 1) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {
            str(jsonable(k, depth + 1)): jsonable(v, depth + 1)
            for k, v in list(value.items())[:MAX_ITEMS]
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        return [jsonable(v, depth + 1) for v in list(value)[:MAX_ITEMS]]
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, bytes):
        return value[:MAX_STRING].decode("utf-8", errors="replace")

    module = type(value).__module__
    name = type(value).__name__

    # numpy / pandas / polars are optional at runtime.
    if module.startswith("numpy"):
        return _numpy(value, depth)
    if module.startswith("pandas"):
        return _pandas(value, depth)
    if module.startswith("polars"):
        return _polars(value, depth)
    if name == "ndarray":
        return _numpy(value, depth)
    if hasattr(value, "tolist") and module.split(".")[0] in {"numpy", "torch"}:
        try:
            return jsonable(value.tolist(), depth + 1)
        except Exception:
            pass
    if hasattr(value, "item") and callable(value.item):
        try:
            return jsonable(value.item(), depth + 1)
        except Exception:
            pass
    if hasattr(value, "to_dict") and name in {"Series", "DataFrame"}:
        return _pandas(value, depth)
    if hasattr(value, "__dict__"):
        return {
            "__type__": f"{module}.{name}",
            **{
                k: jsonable(v, depth + 1)
                for k, v in list(vars(value).items())[:MAX_ITEMS]
                if not k.startswith("_")
            },
        }
    return _clip(repr(value))


def _numpy(value, depth: int):
    try:
        arr = value
        if getattr(arr, "ndim", 0) == 0:
            return jsonable(arr.item(), depth + 1)
        return {
            "__type__": "numpy.ndarray",
            "shape": list(arr.shape),
            "dtype": str(arr.dtype),
            "data": jsonable(arr.tolist(), depth + 1),
        }
    except Exception:  # pragma: no cover - defensive
        return _clip(repr(value))


def _pandas(value, depth: int):
    try:
        if type(value).__name__ == "DataFrame":
            return {
                "__type__": "pandas.DataFrame",
                "shape": list(value.shape),
                "columns": [str(c) for c in value.columns],
                "head": jsonable(value.head(MAX_ROWS).to_dict(orient="records"), depth + 1),
            }
        return {
            "__type__": "pandas.Series",
            "name": str(getattr(value, "name", "")),
            "dtype": str(value.dtype),
            "data": jsonable(value.head(MAX_ROWS).tolist(), depth + 1),
        }
    except Exception:  # pragma: no cover - defensive
        return _clip(repr(value))


def _polars(value, depth: int):
    try:
        if type(value).__name__ == "DataFrame":
            return {
                "__type__": "polars.DataFrame",
                "shape": list(value.shape),
                "columns": list(value.columns),
                "head": jsonable(value.head(MAX_ROWS).to_dicts(), depth + 1),
            }
        return _clip(repr(value))
    except Exception:  # pragma: no cover - defensive
        return _clip(repr(value))
