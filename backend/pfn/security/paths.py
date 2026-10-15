"""Path safety helpers used before writing learner files into the sandbox."""

from __future__ import annotations

from pathlib import Path

MAX_PATH_PARTS = 12
ALLOWED_SUFFIXES = {".py", ".txt", ".json", ".csv", ".md", ".toml", ".cfg", ".ini", ".yaml", ".yml", ".sql"}


class UnsafePathError(ValueError):
    pass


def safe_relative_path(raw: str) -> Path:
    """Validate a learner-supplied project path and return it as a relative Path."""
    text = str(raw).strip().replace("\\", "/")
    if not text or text.startswith("/") or ":" in text.split("/")[0]:
        raise UnsafePathError(f"path must be relative: {raw!r}")
    parts = [p for p in text.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        raise UnsafePathError(f"path may not contain '..': {raw!r}")
    if len(parts) > MAX_PATH_PARTS:
        raise UnsafePathError(f"path is too deep: {raw!r}")
    candidate = Path(*parts)
    suffix = candidate.suffix.lower()
    if suffix and suffix not in ALLOWED_SUFFIXES:
        raise UnsafePathError(f"file type not allowed in the sandbox: {suffix}")
    return candidate


def write_files(root: Path, files: dict[str, str], max_bytes: int = 400_000, max_files: int = 120) -> list[str]:
    """Write a mapping of relative paths into *root*, returning written paths."""
    root = Path(root)
    if len(files) > max_files:
        raise UnsafePathError(f"too many files (limit {max_files})")
    written: list[str] = []
    for raw, content in files.items():
        rel = safe_relative_path(raw)
        data = content if isinstance(content, str) else str(content)
        if len(data.encode("utf-8")) > max_bytes:
            raise UnsafePathError(f"file too large: {rel} (limit {max_bytes} bytes)")
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data, encoding="utf-8")
        written.append(str(rel))
    return written
