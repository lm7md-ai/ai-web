"""SQLite connection management (WAL, foreign keys, row factory)."""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from pfn.config import Settings, get_settings

_local = threading.local()


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=15.0, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


class Database:
    """Thin wrapper around :mod:`sqlite3` with per-thread connections."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.path = Path(self.settings.db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._connections: list[sqlite3.Connection] = []

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn: sqlite3.Connection | None = getattr(_local, "conn", None)
        if conn is None:
            conn = _connect(self.path)
            with self._lock:
                self._connections.append(conn)
            _local.conn = conn
        yield conn

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.connection() as conn:
            conn.execute("BEGIN")
            try:
                yield conn
            except Exception:
                conn.execute("ROLLBACK")
                raise
            else:
                conn.execute("COMMIT")

    def execute(self, sql: str, params: tuple | dict = ()) -> sqlite3.Cursor:
        with self.connection() as conn:
            return conn.execute(sql, params)

    def query_all(self, sql: str, params: tuple | dict = ()) -> list[sqlite3.Row]:
        return list(self.execute(sql, params).fetchall())

    def query_one(self, sql: str, params: tuple | dict = ()) -> sqlite3.Row | None:
        return self.execute(sql, params).fetchone()

    def close(self) -> None:
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                except sqlite3.Error:  # pragma: no cover - defensive
                    pass
            self._connections.clear()
        if hasattr(_local, "conn"):
            delattr(_local, "conn")


_db: Database | None = None


def get_db(settings: Settings | None = None) -> Database:
    global _db
    if _db is None or (settings is not None and settings is not _db.settings):
        _db = Database(settings)
    return _db
