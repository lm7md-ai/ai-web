"""Mission runner: executes learner code against a world and records evidence.

Flow (matching the platform's execution contract)::

    learner source -> python runtime -> validated program -> structured commands
    -> simulation state transition -> event recording -> rendering payload
    -> objective evaluation -> learning evidence
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone

from pfn.db.connection import Database
from pfn.domain.missions.content import by_id
from pfn.domain.missions.models import Mission
from pfn.domain.skills.graph import SkillGraphService
from pfn.runtime.policy import PRESETS
from pfn.runtime.service import ExecutionService, RunRequest
from pfn.worlds.engine.registry import sandbox_files


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class MissionRunner:
    def __init__(
        self,
        db: Database,
        executions: ExecutionService,
        skills: SkillGraphService,
    ) -> None:
        self.db = db
        self.executions = executions
        self.skills = skills

    def run(
        self,
        *,
        learner_id: str,
        mission_id: str,
        code: str,
        mode: str = "native",
        hints_used: int = 0,
        assistance_level: str = "independent",
        trace: bool = False,
    ) -> dict:
        mission: Mission = by_id(mission_id)
        files, world_spec = sandbox_files(mission.world, mission.config)
        files["main.py"] = code
        started = time.perf_counter()
        run = self.executions.run(
            RunRequest(
                files=files,
                kind="program",
                module="main",
                target="program",
                world=world_spec,
                mode=mode,  # type: ignore[arg-type]
                trace=trace,
                limits=PRESETS["lesson"] if mode == "isolated" else PRESETS["native"],
            )
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        world_result = run.world or {}
        ok = bool(world_result.get("ok")) and run.ok is not False and run.error is None
        score = float(world_result.get("score", 0.0))
        if run.error is not None:
            ok = False
            score = 0.0

        attempt_id = "att_" + uuid.uuid4().hex[:12]
        payload = {
            "id": attempt_id,
            "mission_id": mission.id,
            "world": mission.world,
            "ok": ok,
            "score": score,
            "mode": mode,
            "hints_used": hints_used,
            "assistance_level": assistance_level,
            "duration_ms": duration_ms,
            "run": run.to_dict(),
        }
        with self.db.transaction() as conn:
            conn.execute(
                """INSERT INTO mission_attempts (id, learner_id, mission_id, world, code, mode, ok,
                                                 score, hints_used, assistance_level, duration_ms,
                                                 result_json, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    attempt_id,
                    learner_id,
                    mission.id,
                    mission.world,
                    code,
                    mode,
                    1 if ok else 0,
                    score,
                    int(hints_used),
                    assistance_level,
                    duration_ms,
                    json.dumps(
                        {
                            "objectives": world_result.get("objectives", []),
                            "stats": world_result.get("stats") or world_result.get("metrics", {}),
                            "tick": world_result.get("tick"),
                            "stop_reason": world_result.get("stop_reason"),
                            "error": run.error,
                        }
                    ),
                    _now(),
                ),
            )
            conn.execute(
                """INSERT INTO simulation_runs (id, learner_id, world, mission_id, config_json,
                                                events_json, final_state_json, ok, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    "sim_" + uuid.uuid4().hex[:12],
                    learner_id,
                    mission.world,
                    mission.id,
                    json.dumps(mission.config),
                    json.dumps(world_result.get("events", [])),
                    json.dumps(
                        {
                            k: v
                            for k, v in world_result.items()
                            if k not in ("events",)
                        }
                    ),
                    1 if ok else 0,
                    _now(),
                ),
            )

        # ---- evidence: only real outcomes count, and transfer is not claimed here
        for skill_id in mission.skills:
            self.skills.record_evidence(
                learner_id=learner_id,
                skill_id=skill_id,
                kind="mission_attempt",
                source_type="mission",
                source_id=mission.id,
                outcome="success" if ok else ("partial" if score > 0 else "failure"),
                independence=assistance_level if assistance_level in ("independent", "hinted", "guided", "assisted") else "independent",
                weight=1.0 if ok else 0.5,
                details={
                    "mission_id": mission.id,
                    "world": mission.world,
                    "score": score,
                    "hints_used": hints_used,
                    "duration_ms": duration_ms,
                    "stop_reason": world_result.get("stop_reason"),
                },
            )

        payload["objectives"] = world_result.get("objectives", [])
        payload["events"] = world_result.get("events", [])
        payload["state"] = {k: v for k, v in world_result.items() if k != "events"}
        payload["feedback"] = self._feedback(mission, run, world_result, ok)
        return payload

    # --------------------------------------------------------------- helpers
    def _feedback(self, mission: Mission, run, world_result: dict, ok: bool) -> dict:
        """Concrete, evidence-based feedback - never generic praise."""
        notes_ar: list[str] = []
        notes_en: list[str] = []
        if run.error:
            error = run.error or {}
            notes_en.append(
                f"The program stopped with {error.get('type', 'an error')}: {error.get('message', '')}"
            )
            notes_ar.append(
                f"توقف البرنامج بخطأ {error.get('type', 'غير معروف')}: {error.get('message', '')}"
            )
            learner_frames = [f for f in error.get("frames", []) if f.get("is_learner_code")]
            if learner_frames:
                frame = learner_frames[-1]
                notes_en.append(f"Look at line {frame.get('line')} in {frame.get('file')}: {frame.get('code')}")
                notes_ar.append(f"راجع السطر {frame.get('line')} في {frame.get('file')}: {frame.get('code')}")
        elif world_result:
            for objective in world_result.get("objectives", []):
                if not objective.get("ok"):
                    notes_en.append(f"Objective not met [{objective.get('type')}]: {objective.get('detail')}")
                    notes_ar.append(f"هدف غير محقق [{objective.get('type')}]: {objective.get('detail')}")
            stop = world_result.get("stop_reason")
            if stop and stop not in ("completed", None):
                notes_en.append(f"Run ended because: {stop}")
                notes_ar.append(f"انتهت المحاولة بسبب: {stop}")
        if ok:
            notes_en.append(
                f"Mission complete in {world_result.get('tick')} ticks "
                f"(score {world_result.get('score')})."
            )
            notes_ar.append(
                f"اكتملت المهمة في {world_result.get('tick')} نبضة (النتيجة {world_result.get('score')})."
            )
        else:
            notes_en.append("The mission is not complete yet - the evidence above shows what is missing.")
            notes_ar.append("المهمة لم تكتمل بعد - الأدلة أعلاه توضح ما ينقص.")
        return {"notes_en": notes_en, "notes_ar": notes_ar, "ok": ok}

    def history(self, learner_id: str, mission_id: str | None = None, limit: int = 20) -> list[dict]:
        sql = "SELECT * FROM mission_attempts WHERE learner_id = ?"
        params: list = [learner_id]
        if mission_id:
            sql += " AND mission_id = ?"
            params.append(mission_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = self.db.query_all(sql, tuple(params))
        return [
            {
                "id": row["id"],
                "mission_id": row["mission_id"],
                "world": row["world"],
                "ok": bool(row["ok"]),
                "score": row["score"],
                "mode": row["mode"],
                "hints_used": row["hints_used"],
                "assistance_level": row["assistance_level"],
                "duration_ms": row["duration_ms"],
                "result": json.loads(row["result_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]
