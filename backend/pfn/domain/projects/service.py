"""Project workbench: multi-file projects with real execution and versioning."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone

from pfn.db.connection import Database
from pfn.domain.projects.models import TEMPLATES, TEMPLATE_NOTES, ProjectRecord
from pfn.runtime.policy import PRESETS
from pfn.runtime.service import ExecutionService, RunRequest

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
MAX_FILE_BYTES = 256 * 1024


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ProjectService:
    """CRUD, versioning and execution for learner projects."""

    def __init__(self, db: Database, executions: ExecutionService) -> None:
        self.db = db
        self.executions = executions

    # ------------------------------------------------------------------ list
    def templates(self) -> list[dict]:
        return [
            {
                "id": name,
                "files": sorted(files),
                "notes": TEMPLATE_NOTES.get(name, {}),
            }
            for name, files in sorted(TEMPLATES.items())
        ]

    def list_projects(self, learner_id: str) -> list[dict]:
        rows = self.db.query_all(
            "SELECT * FROM projects WHERE learner_id = ? ORDER BY updated_at DESC", (learner_id,)
        )
        return [self._record(row).to_dict() for row in rows]

    def _record(self, row) -> ProjectRecord:
        return ProjectRecord(
            id=row["id"],
            learner_id=row["learner_id"],
            slug=row["slug"],
            title=row["title"],
            template=row["template"],
            description=row["description"],
            current_version=row["current_version"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    # ---------------------------------------------------------------- create
    def create(self, learner_id: str, slug: str, title: str | None = None,
               template: str = "blank", description: str = "") -> dict:
        if not SLUG_RE.match(slug):
            raise ValueError("slug must match ^[a-z0-9][a-z0-9_-]{0,63}$")
        if template not in TEMPLATES:
            raise ValueError(f"unknown template: {template}")
        existing = self.db.query_one(
            "SELECT id FROM projects WHERE learner_id = ? AND slug = ?", (learner_id, slug)
        )
        if existing:
            raise ValueError(f"slug '{slug}' already exists")

        project_id = _id("prj")
        now = _now()
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT INTO projects (id, learner_id, slug, title, template, description,"
                " current_version, created_at, updated_at) VALUES (?,?,?,?,?,?,1,?,?)",
                (project_id, learner_id, slug, title or slug, template, description, now, now),
            )
            for path, content in TEMPLATES[template].items():
                conn.execute(
                    "INSERT INTO project_files (project_id, path, content, updated_at) VALUES (?,?,?,?)",
                    (project_id, path, content, now),
                )
            conn.execute(
                "INSERT INTO project_versions (id, project_id, version, message, snapshot_json, created_at)"
                " VALUES (?,?,1,'initial scaffold',?,?)",
                (project_id + "_v1", project_id, json.dumps(TEMPLATES[template]), now),
            )
        return self.get(learner_id, project_id)

    # ------------------------------------------------------------------ read
    def get(self, learner_id: str, project_id: str) -> dict:
        row = self.db.query_one(
            "SELECT * FROM projects WHERE id = ? AND learner_id = ?", (project_id, learner_id)
        )
        if row is None:
            raise KeyError(project_id)
        record = self._record(row).to_dict()
        record["files"] = self.files(project_id)
        record["versions"] = self.versions(project_id)
        return record

    def files(self, project_id: str) -> dict[str, str]:
        rows = self.db.query_all(
            "SELECT path, content FROM project_files WHERE project_id = ? ORDER BY path", (project_id,)
        )
        return {row["path"]: row["content"] for row in rows}

    def versions(self, project_id: str) -> list[dict]:
        rows = self.db.query_all(
            "SELECT version, message, created_at FROM project_versions"
            " WHERE project_id = ? ORDER BY version DESC LIMIT 50",
            (project_id,),
        )
        return [dict(row) for row in rows]

    # ---------------------------------------------------------------- update
    def save_files(self, learner_id: str, project_id: str, files: dict[str, str],
                   commit: bool = False, message: str = "") -> dict:
        self._owned(learner_id, project_id)
        for path, content in files.items():
            if path.startswith("/") or ".." in path.split("/"):
                raise ValueError(f"illegal path: {path}")
            if len(content.encode("utf-8")) > MAX_FILE_BYTES:
                raise ValueError(f"{path} is larger than {MAX_FILE_BYTES} bytes")
        now = _now()
        with self.db.transaction() as conn:
            for path, content in files.items():
                conn.execute(
                    "INSERT INTO project_files (project_id, path, content, updated_at) VALUES (?,?,?,?)"
                    " ON CONFLICT(project_id, path) DO UPDATE SET content=excluded.content,"
                    " updated_at=excluded.updated_at",
                    (project_id, path, content, now),
                )
            conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        if commit:
            self.commit(learner_id, project_id, message or "work saved")
        return self.get(learner_id, project_id)

    def delete_file(self, learner_id: str, project_id: str, path: str) -> dict:
        self._owned(learner_id, project_id)
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM project_files WHERE project_id = ? AND path = ?", (project_id, path))
            conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (_now(), project_id))
        return self.get(learner_id, project_id)

    def commit(self, learner_id: str, project_id: str, message: str) -> int:
        self._owned(learner_id, project_id)
        snapshot = self.files(project_id)
        row = self.db.query_one(
            "SELECT current_version FROM projects WHERE id = ?", (project_id,)
        )
        version = int(row["current_version"]) + 1
        now = _now()
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT INTO project_versions (id, project_id, version, message, snapshot_json, created_at)"
                " VALUES (?,?,?,?,?,?)",
                (_id("ver"), project_id, version, message, json.dumps(snapshot), now),
            )
            conn.execute(
                "UPDATE projects SET current_version = ?, updated_at = ? WHERE id = ?",
                (version, now, project_id),
            )
        return version

    def rollback(self, learner_id: str, project_id: str, version: int) -> dict:
        self._owned(learner_id, project_id)
        row = self.db.query_one(
            "SELECT snapshot_json FROM project_versions WHERE project_id = ? AND version = ?",
            (project_id, version),
        )
        if row is None:
            raise KeyError(f"version {version} not found")
        snapshot = json.loads(row["snapshot_json"])
        now = _now()
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM project_files WHERE project_id = ?", (project_id,))
            for path, content in snapshot.items():
                conn.execute(
                    "INSERT INTO project_files (project_id, path, content, updated_at) VALUES (?,?,?,?)",
                    (project_id, path, content, now),
                )
            conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        return self.get(learner_id, project_id)

    # ------------------------------------------------------------------- run
    def run(self, learner_id: str, project_id: str, entry: str = "main.py",
            mode: str = "native", trace: bool = False) -> dict:
        self._owned(learner_id, project_id)
        files = self.files(project_id)
        if entry not in files:
            raise KeyError(f"{entry} is not part of this project")
        result = self.executions.run(
            RunRequest(files=files, kind="script", entry=entry, mode=mode, trace=trace)
        )
        return result.to_dict()

    def test(self, learner_id: str, project_id: str, tests: dict[str, str] | None = None,
             mode: str = "native") -> dict:
        self._owned(learner_id, project_id)
        files = self.files(project_id)
        suite = tests or {path: content for path, content in files.items() if path.startswith("tests/")}
        if not suite:
            raise ValueError("this project has no tests/ directory and no inline tests were supplied")
        report = self.executions.run_tests(files, suite, mode=mode)
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT INTO events (id, learner_id, type, payload_json, created_at) VALUES (?,?,?,?,?)",
                (
                    _id("evt"),
                    learner_id,
                    "project.test",
                    json.dumps({"project_id": project_id, "ok": report["ok"],
                                "passed": report["passed"], "total": report["total"]}),
                    _now(),
                ),
            )
        return report

    # --------------------------------------------------------------- helpers
    def _owned(self, learner_id: str, project_id: str) -> None:
        row = self.db.query_one(
            "SELECT id FROM projects WHERE id = ? AND learner_id = ?", (project_id, learner_id)
        )
        if row is None:
            raise KeyError(project_id)
