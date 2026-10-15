"""Curriculum registry: catalogue, persistence, execution and grading.

Grading is done by *real pytest runs* inside the sandbox.  Hidden tests never
leave the server: the frontend receives pass/fail counts and the names of
failing cases, never the hidden source.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone

from pfn.db.connection import Database
from pfn.domain.curriculum.content.level0 import MODULES as LEVEL0
from pfn.domain.curriculum.content.level1 import MODULES as LEVEL1
from pfn.domain.curriculum.content.level2 import MODULES as LEVEL2
from pfn.domain.curriculum.content.level3 import MODULES as LEVEL3
from pfn.domain.curriculum.content.level4 import MODULES as LEVEL4
from pfn.domain.curriculum.content.level5 import MODULES as LEVEL5
from pfn.domain.curriculum.content.level6 import MODULES as LEVEL6
from pfn.domain.curriculum.content.level7 import MODULES as LEVEL7
from pfn.domain.curriculum.content.level8 import MODULES as LEVEL8
from pfn.domain.curriculum.content.level9 import MODULES as LEVEL9
from pfn.domain.curriculum.content.level10 import MODULES as LEVEL10
from pfn.domain.curriculum.content.level11 import MODULES as LEVEL11
from pfn.domain.curriculum.models import CurriculumModule, TaskSpec
from pfn.domain.skills.graph import SkillGraphService
from pfn.runtime.policy import PRESETS
from pfn.runtime.service import ExecutionService, RunRequest

MODULES: list[CurriculumModule] = (
    list(LEVEL0)
    + list(LEVEL1)
    + list(LEVEL2)
    + list(LEVEL3)
    + list(LEVEL4)
    + list(LEVEL5)
    + list(LEVEL6)
    + list(LEVEL7)
    + list(LEVEL8)
    + list(LEVEL9)
    + list(LEVEL10)
    + list(LEVEL11)
)

_BY_ID: dict[str, CurriculumModule] = {module.id: module for module in MODULES}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _junit_file(classname: str, name: str = "") -> str:
    """Resolve the test file that owns a JUnit case.

    pytest writes ``classname="tests.test_public"`` for executed cases, but
    leaves it empty for collection errors, where the module path lands in
    ``name`` instead. Both shapes are handled so a public failure is never
    mislabelled as hidden.
    """
    parts = [part for part in (classname or name or "").split(".") if part]
    if not parts:
        return ""
    stem = parts[1] if len(parts) > 1 and parts[0] == "tests" else parts[-1]
    return f"{stem}.py"


def validate_curriculum() -> list[str]:
    """Structural checks used by the test suite (skills exist, ids unique...)."""
    problems: list[str] = []
    seen: set[str] = set()
    for module in MODULES:
        if module.id in seen:
            problems.append(f"duplicate module id: {module.id}")
        seen.add(module.id)
        for spec_name in ("task", "assessment", "transfer_task"):
            spec: TaskSpec | None = getattr(module, spec_name)
            if spec is None:
                continue
            if not spec.reference_solution.strip():
                problems.append(f"{module.id}.{spec_name}: missing reference solution")
            if not spec.hidden_tests:
                problems.append(f"{module.id}.{spec_name}: missing hidden tests")
            for name in spec.hidden_tests:
                if not name.startswith("test_"):
                    problems.append(f"{module.id}.{spec_name}: hidden test file must be test_*.py ({name})")
    return problems


class CurriculumService:
    def __init__(self, db: Database, executions: ExecutionService, skills: SkillGraphService) -> None:
        self.db = db
        self.executions = executions
        self.skills = skills

    # ------------------------------------------------------------------ sync
    def sync(self) -> int:
        now = _now()
        with self.db.transaction() as conn:
            for module in MODULES:
                conn.execute(
                    """INSERT INTO curriculum_modules (id, level, order_index, domain, title_ar, title_en,
                                                      summary_ar, summary_en, skills_json, synced_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(id) DO UPDATE SET
                         level=excluded.level, order_index=excluded.order_index, domain=excluded.domain,
                         title_ar=excluded.title_ar, title_en=excluded.title_en,
                         summary_ar=excluded.summary_ar, summary_en=excluded.summary_en,
                         skills_json=excluded.skills_json, synced_at=excluded.synced_at""",
                    (
                        module.id,
                        module.level,
                        module.order_index,
                        module.domain,
                        module.title_ar,
                        module.title_en,
                        module.summary_ar,
                        module.summary_en,
                        json.dumps(list(module.skills)),
                        now,
                    ),
                )
        problems = validate_curriculum()
        if problems:
            raise RuntimeError(f"curriculum is invalid: {problems}")
        return len(MODULES)

    # ------------------------------------------------------------------ read
    def all(self, locale: str = "en") -> list[CurriculumModule]:
        return sorted(MODULES, key=lambda m: (m.level, m.order_index, m.id))

    def by_level(self, level: int) -> list[CurriculumModule]:
        return sorted((m for m in MODULES if m.level == level), key=lambda m: (m.order_index, m.id))

    def get(self, module_id: str) -> CurriculumModule:
        if module_id not in _BY_ID:
            raise KeyError(f"unknown curriculum module: {module_id}")
        return _BY_ID[module_id]

    def to_dict(self, locale: str = "en", level: int | None = None) -> list[dict]:
        modules = self.by_level(level) if level is not None else self.all()
        return [m.to_dict(locale) for m in modules]

    def progress(self, learner_id: str) -> dict[str, dict]:
        rows = self.db.query_all(
            "SELECT * FROM module_progress WHERE learner_id = ?", (learner_id,)
        )
        return {row["module_id"]: dict(row) for row in rows}

    # ------------------------------------------------------------- execution
    def run_example(self, learner_id: str, module_id: str, code: str | None = None, mode: str = "native") -> dict:
        module = self.get(module_id)
        source = code if code is not None else module.example_code
        started = time.perf_counter()
        run = self.executions.run(
            RunRequest(files={"main.py": source}, kind="script", mode=mode, trace=False,
                       limits=PRESETS["lesson"] if mode == "isolated" else PRESETS["native"])
        )
        self._bump(learner_id, module_id, example_runs=1 if run.ok else 0)
        return {
            "module_id": module_id,
            "ok": run.ok,
            "stdout": run.stdout,
            "stderr": run.stderr,
            "error": run.error,
            "duration_ms": int((time.perf_counter() - started) * 1000),
            "notes": module.notes("ar"),
            "notes_en": module.notes("en"),
        }

    def run_experiment(self, learner_id: str, module_id: str, code: str, mode: str = "native") -> dict:
        module = self.get(module_id)
        started = time.perf_counter()
        run = self.executions.run(
            RunRequest(files={"main.py": code}, kind="script", mode=mode, trace=True,
                       limits=PRESETS["lesson"] if mode == "isolated" else PRESETS["native"])
        )
        self._bump(learner_id, module_id, experiment_runs=1 if run.ok else 0)
        return {
            "module_id": module_id,
            "ok": run.ok,
            "stdout": run.stdout,
            "stderr": run.stderr,
            "error": run.error,
            "trace": run.trace,
            "duration_ms": int((time.perf_counter() - started) * 1000),
        }

    # --------------------------------------------------------------- grading
    def submit_task(
        self,
        *,
        learner_id: str,
        module_id: str,
        spec_name: str,
        code: str,
        mode: str = "native",
        assistance_level: str = "independent",
        hints_used: int = 0,
        public_only: bool = False,
    ) -> dict:
        module = self.get(module_id)
        spec: TaskSpec | None = getattr(module, spec_name, None)
        if spec is None:
            raise KeyError(f"module {module_id} has no {spec_name}")
        files: dict[str, str] = dict(spec.extra_files)
        files[spec.entry_filename] = code
        tests = dict(spec.public_tests)
        if not public_only:
            tests.update(spec.hidden_tests)
        started = time.perf_counter()
        report = self.executions.run_tests(files, tests, mode=mode)
        duration_ms = int((time.perf_counter() - started) * 1000)

        passed, total = report["passed"], report["total"]
        ok = report["ok"]
        # Visible cases are safe to show; hidden failures are summarised only.
        # JUnit reports the module as ``tests.<file_stem>``, so the file that
        # owns a case is derived from the classname, never from the case name.
        public_files = {name for name in spec.public_tests}
        cases: list[dict] = []
        failed_public: list[str] = []
        failed_hidden: list[str] = []
        for case in report["cases"]:
            file_name = _junit_file(case["classname"], case["name"])
            is_public = file_name in public_files
            cases.append(
                {
                    "file": file_name,
                    "name": case["name"],
                    "outcome": case["outcome"],
                    "message": case["message"] if is_public else "",
                    "detail": case["detail"][:400] if is_public else "",
                    "visible": is_public,
                }
            )
            if case["outcome"] in ("failed", "error"):
                (failed_public if is_public else failed_hidden).append(
                    case["name"] if is_public else file_name
                )

        field_map = {"task": "task_passed", "assessment": "assessment_passed", "transfer_task": "transfer_passed"}
        self._bump(learner_id, module_id, **{field_map[spec_name]: 1 if ok else 0})

        for skill_id in module.skills:
            self.skills.record_evidence(
                learner_id=learner_id,
                skill_id=skill_id,
                kind=f"curriculum_{spec_name}",
                source_type="curriculum",
                source_id=module.id,
                outcome="success" if ok else ("partial" if passed else "failure"),
                independence=assistance_level,
                weight=1.2 if spec_name == "assessment" else 1.0,
                transfer=spec_name == "transfer_task",
                details={
                    "module_id": module.id,
                    "passed": passed,
                    "total": total,
                    "hints_used": hints_used,
                    "mode": mode,
                    "duration_ms": duration_ms,
                },
            )

        return {
            "module_id": module_id,
            "spec": spec_name,
            "ok": ok,
            "passed": passed,
            "total": total,
            "cases": cases,
            "failed_hidden": failed_hidden,
            "output": report["output"] if not ok else "",
            "timed_out": report["timed_out"],
            "duration_ms": duration_ms,
            "feedback": self._feedback(ok, passed, total, failed_hidden, duration_ms, failed_public),
        }

    def _feedback(self, ok: bool, passed: int, total: int, failed_hidden: list[str], duration_ms: int,
                  failed_public: list[str] | None = None) -> dict:
        if ok:
            return {
                "notes_en": [f"All {total} checks passed in {duration_ms} ms."],
                "notes_ar": [f"نجحت كل الفحوص ({total}) في {duration_ms} مللي ثانية."],
            }
        notes_en = [f"{passed}/{total} checks passed."]
        notes_ar = [f"نجح {passed} من {total} فحصاً."]
        for name in (failed_public or [])[:5]:
            notes_en.append(f"Visible check failed: {name} - read the case output for the exact difference.")
            notes_ar.append(f"فحص ظاهر فاشل: {name} - راجع مخرجات الفحص لمعرفة الفرق بالضبط.")
        for name in failed_hidden[:5]:
            notes_en.append(f"Hidden check failed: {name}")
            notes_ar.append(f"فحص مخفي فاشل: {name}")
        return {"notes_en": notes_en, "notes_ar": notes_ar}

    # -------------------------------------------------------------- progress
    def _bump(self, learner_id: str, module_id: str, **counters: int) -> None:
        now = _now()
        with self.db.transaction() as conn:
            conn.execute(
                """INSERT INTO module_progress (learner_id, module_id, status, updated_at)
                   VALUES (?, ?, 'in_progress', ?)
                   ON CONFLICT(learner_id, module_id) DO NOTHING""",
                (learner_id, module_id, now),
            )
            sets, values = [], []
            for key, value in counters.items():
                if value:
                    sets.append(f"{key} = {key} + ?")
                    values.append(int(value))
            sets.append("updated_at = ?")
            values.append(now)
            values.extend([learner_id, module_id])
            conn.execute(
                f"UPDATE module_progress SET {', '.join(sets)} WHERE learner_id = ? AND module_id = ?",
                tuple(values),
            )

    def mark_status(self, learner_id: str, module_id: str, status: str) -> None:
        now = _now()
        with self.db.transaction() as conn:
            conn.execute(
                """INSERT INTO module_progress (learner_id, module_id, status, updated_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(learner_id, module_id)
                   DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at""",
                (learner_id, module_id, status, now),
            )
