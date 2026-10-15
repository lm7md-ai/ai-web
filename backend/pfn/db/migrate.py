"""Versioned SQL migrations with forward-only application and checksum logging."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from pfn.db.connection import Database

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_meta(db: Database) -> None:
    db.execute(
        """CREATE TABLE IF NOT EXISTS schema_migrations (
            version     TEXT PRIMARY KEY,
            checksum    TEXT NOT NULL,
            applied_at  TEXT NOT NULL
        )"""
    )


def discover() -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        match = re.match(r"^(\d+)_", path.name)
        if not match:
            raise ValueError(f"migration file must start with a number: {path.name}")
        found.append((match.group(1).zfill(4), path))
    return found


def migrate(db: Database) -> list[str]:
    """Apply pending migrations, returning the versions applied in this call."""
    _ensure_meta(db)
    applied_rows = db.query_all("SELECT version, checksum FROM schema_migrations")
    applied = {row["version"]: row["checksum"] for row in applied_rows}
    pending: list[str] = []
    for version, path in discover():
        sql = path.read_text(encoding="utf-8")
        checksum = hashlib.sha256(sql.encode("utf-8")).hexdigest()
        if version in applied:
            if applied[version] != checksum:
                raise RuntimeError(
                    f"migration {version} ({path.name}) changed after being applied; "
                    "restore the original file or add a new migration"
                )
            continue
        with db.transaction() as conn:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version, checksum, applied_at) VALUES (?, ?, ?)",
                (version, checksum, _utcnow()),
            )
        pending.append(version)
    return pending


def current_version(db: Database) -> str:
    _ensure_meta(db)
    row = db.query_one("SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1")
    return row["version"] if row else "0000"
