"""AI Mentor Council.

Every mentor has two brains:

1. a **deterministic** brain that always works - it reads the real runtime
   report, the AST of the learner's code and the failing assertions;
2. an optional **provider** brain (OpenAI-compatible or local Ollama) that is
   used only when the learner has configured one.

The response always says which brain answered. It never invents a result: if
the deterministic brain has nothing to add, it says so.
"""

from __future__ import annotations

import ast
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from pfn.ai.providers.base import Completion, Message, Provider, build_provider
from pfn.db.connection import Database
from pfn.runtime.service import ExecutionService, RunRequest


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _id() -> str:
    return f"ai_{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True, slots=True)
class Mentor:
    id: str
    name_ar: str
    name_en: str
    focus_ar: str
    focus_en: str
    persona: str

    def name(self, locale: str) -> str:
        return self.name_ar if locale == "ar" else self.name_en

    def focus(self, locale: str) -> str:
        return self.focus_ar if locale == "ar" else self.focus_en

    def to_dict(self, locale: str = "en") -> dict:
        return {
            "id": self.id,
            "name": self.name(locale),
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "focus": self.focus(locale),
            "focus_ar": self.focus_ar,
            "focus_en": self.focus_en,
        }


MENTORS: tuple[Mentor, ...] = (
    Mentor("architect", "المِعماري", "The Architect", "البنية والتصميم",
           "Structure and design", "You review structure, decomposition and naming."),
    Mentor("debugger", "المُنقّح", "The Debugger", "تشخيص الأخطاء",
           "Failure diagnosis", "You explain why code fails, using evidence only."),
    Mentor("reviewer", "المُراجع", "The Reviewer", "جودة الكود",
           "Code quality", "You review style, typing, tests and maintainability."),
    Mentor("coach", "المدرّب", "The Coach", "طريقة التعلم",
           "Learning process", "You ask guiding questions instead of giving answers."),
    Mentor("researcher", "الباحث", "The Researcher", "الخوارزميات والأدلة",
           "Algorithms and evidence", "You connect the problem to algorithms and complexity."),
)

_BY_ID = {mentor.id: mentor for mentor in MENTORS}


class _StaticReview(ast.NodeVisitor):
    """Cheap, honest static checks - no guessing at intent."""

    def __init__(self) -> None:
        self.findings: list[dict] = []
        self.imported: dict[str, int] = {}
        self.used: set[str] = set()
        self.functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname or alias.name.split(".")[0]
            self.imported[name] = node.lineno
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name != "*":
                self.imported[alias.asname or alias.name] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        self.used.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        cursor = node
        while isinstance(cursor, ast.Attribute):
            cursor = cursor.value
        if isinstance(cursor, ast.Name):
            self.used.add(cursor.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node) -> None:
        self.functions.append(node)
        if ast.get_docstring(node) is None and not node.name.startswith("_"):
            self._add("missing_docstring", node.lineno, node.name, "info")
        defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
        for default in defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self._add("mutable_default", node.lineno, node.name, "warning")
        body_lines = (node.end_lineno or node.lineno) - node.lineno
        if body_lines > 60:
            self._add("long_function", node.lineno, node.name, "info", detail=f"{body_lines} lines")

    def visit_Try(self, node: ast.Try) -> None:
        for handler in node.handlers:
            if handler.type is None:
                self._add("bare_except", handler.lineno, "", "warning")
            elif isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                    self._add("silent_except", handler.lineno, "", "warning")
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        for op in node.ops:
            if isinstance(op, (ast.Eq, ast.NotEq)):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value is None:
                        self._add("none_comparison", node.lineno, "", "warning")
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        self._add("global_state", node.lineno, ",".join(node.names), "info")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            self._add("dynamic_exec", node.lineno, node.func.id, "warning")
        self.generic_visit(node)

    def _add(self, kind: str, lineno: int, symbol: str, severity: str, detail: str = "") -> None:
        self.findings.append({
            "kind": kind, "line": lineno, "symbol": symbol,
            "severity": severity, "detail": detail,
        })

    def finish(self) -> list[dict]:
        for name, lineno in self.imported.items():
            if name not in self.used and name not in {"annotations"}:
                self.findings.append({
                    "kind": "unused_import", "line": lineno, "symbol": name,
                    "severity": "info", "detail": "",
                })
        self.findings.sort(key=lambda item: (item["line"], item["kind"]))
        return self.findings


FINDING_TEXT = {
    "bare_except": {
        "en": "`except:` catches everything, including KeyboardInterrupt. Catch a specific exception.",
        "ar": "`except:` يمسك كل شيء حتى KeyboardInterrupt. حدّد نوع الاستثناء.",
    },
    "silent_except": {
        "en": "`except Exception: pass` hides the failure you are trying to find.",
        "ar": "`except Exception: pass` يخفي الخطأ الذي تبحث عنه.",
    },
    "mutable_default": {
        "en": "A mutable default argument is shared between calls; use `None` and build inside.",
        "ar": "القيمة الافتراضية القابلة للتغيير تُشارك بين الاستدعاءات؛ استخدم `None` ثم أنشئها داخل الدالة.",
    },
    "long_function": {
        "en": "This function is long; consider extracting a helper with a clear name.",
        "ar": "هذه الدالة طويلة؛ فكّر في استخراج دالة مساعدة باسم واضح.",
    },
    "unused_import": {
        "en": "This import is never used.",
        "ar": "هذا الاستيراد غير مستخدم.",
    },
    "missing_docstring": {
        "en": "Public function without a docstring - say what it promises.",
        "ar": "دالة عامة بلا توثيق؛ اذكر ما تعد به.",
    },
    "none_comparison": {
        "en": "Compare with `is None` / `is not None` instead of `== None`.",
        "ar": "استخدم `is None` أو `is not None` بدل `== None`.",
    },
    "global_state": {
        "en": "Mutating global state makes functions hard to test; prefer passing values in.",
        "ar": "تعديل الحالة العامة يجعل الاختبار صعباً؛ مرّر القيم كمعاملات أفضل.",
    },
    "dynamic_exec": {
        "en": "`eval`/`exec` on arbitrary text is a security risk - avoid it in your own code too.",
        "ar": "`eval` و`exec` على نصوص عشوائية خطر أمني؛ تجنّبهما حتى في كودك.",
    },
}


def _finding_text(kind: str, locale: str) -> str:
    entry = FINDING_TEXT.get(kind, {})
    return entry.get(locale) or entry.get("en") or kind


class MentorService:
    def __init__(self, db: Database, executions: ExecutionService,
                 provider: Provider | None = None) -> None:
        self.db = db
        self.executions = executions
        self.provider = provider if provider is not None else build_provider()
        self._last_error: str | None = None

    # ------------------------------------------------------------------ meta
    def mentors(self, locale: str = "en") -> list[dict]:
        return [mentor.to_dict(locale) for mentor in MENTORS]

    def status(self) -> dict:
        return {
            "provider": self.provider.name,
            "model": self.provider.model,
            "enabled": self.provider.is_enabled(),
            "mode": "provider" if self.provider.is_enabled() else "heuristic",
            "last_error": self._last_error,
        }

    # ------------------------------------------------------------------ ask
    def ask(self, learner_id: str, question: str, locale: str = "en",
            mentor_id: str = "coach", files: dict[str, str] | None = None,
            run_report: dict | None = None) -> dict:
        mentor = _BY_ID.get(mentor_id, _BY_ID["coach"])
        facts = self._facts(files, run_report)
        answer = None
        source = "heuristic"
        if self.provider.is_enabled():
            completion = self.provider.complete(self._messages(mentor, question, locale, facts))
            if completion.ok and completion.text.strip():
                answer = completion.text.strip()
                source = "provider"
            else:
                facts.append(f"(provider unavailable: {completion.error})")
        if answer is None:
            answer = self._heuristic_answer(mentor, question, locale, facts)

        response = {
            "mentor": mentor.to_dict(locale),
            "question": question,
            "answer": answer,
            "source": source,
            "facts": facts,
            "follow_ups": self._follow_ups(mentor, locale, question),
            "at": _now(),
        }
        self._log(learner_id, "ask", {"mentor": mentor.id, "locale": locale,
                                      "question": question[:400]}, role=mentor.id, mode=source)
        return response

    def council(self, learner_id: str, question: str, locale: str = "en",
                files: dict[str, str] | None = None, run_report: dict | None = None) -> dict:
        facts = self._facts(files, run_report)
        opinions = []
        for mentor in MENTORS:
            answer = None
            source = "heuristic"
            if self.provider.is_enabled():
                completion = self.provider.complete(self._messages(mentor, question, locale, facts))
                if completion.ok and completion.text.strip():
                    answer, source = completion.text.strip(), "provider"
            if answer is None:
                answer = self._heuristic_answer(mentor, question, locale, facts)
            opinions.append({
                "mentor": mentor.to_dict(locale),
                "answer": answer,
                "source": source,
            })
        self._log(learner_id, "council", {"locale": locale, "question": question[:400]},
                  role="council", mode=opinions[0]["source"])
        return {
            "question": question,
            "facts": facts,
            "opinions": opinions,
            "synthesis": self._synthesise(opinions, locale),
            "at": _now(),
        }

    # ---------------------------------------------------------------- review
    def review(self, learner_id: str, files: dict[str, str], locale: str = "en",
               entry: str = "main.py") -> dict:
        findings: list[dict] = []
        parsed = 0
        syntax_errors = 0
        for path, source in sorted(files.items()):
            if not path.endswith(".py"):
                continue
            try:
                tree = ast.parse(source)
            except SyntaxError as error:
                syntax_errors += 1
                findings.append({
                    "file": path, "kind": "syntax_error", "line": error.lineno or 0,
                    "symbol": "", "severity": "error", "detail": error.msg,
                    "message": f"SyntaxError: {error.msg}",
                })
                continue
            parsed += 1
            visitor = _StaticReview()
            visitor.visit(tree)
            for finding in visitor.finish():
                finding["file"] = path
                finding["message"] = _finding_text(finding["kind"], locale)
                findings.append(finding)

        report: dict | None = None
        if entry in files and not syntax_errors:
            report = self.executions.run(RunRequest(files=files, kind="script", entry=entry)).to_dict()
            if not report.get("ok"):
                findings.insert(0, {
                    "file": entry, "kind": "runtime_failure", "line": 0, "symbol": "",
                    "severity": "error", "detail": (report.get("error") or {}).get("type", ""),
                    "message": self._explain_failure(report, locale),
                })

        severity_order = {"error": 0, "warning": 1, "info": 2}
        findings.sort(key=lambda item: (severity_order.get(item["severity"], 3), item["file"], item["line"]))

        llm_notes = None
        if self.provider.is_enabled():
            completion = self.provider.complete([
                Message("system", "You are a senior Python reviewer. Answer with short, numbered, actionable notes."),
                Message("user", self._code_dump(files) + "\n\nStatic findings:\n"
                        + json.dumps([{k: v for k, v in f.items() if k != "message"} for f in findings],
                                     ensure_ascii=False)),
            ])
            if completion.ok:
                llm_notes = completion.text.strip()

        result = {
            "files_reviewed": parsed,
            "findings": findings,
            "counts": {
                "error": sum(1 for f in findings if f["severity"] == "error"),
                "warning": sum(1 for f in findings if f["severity"] == "warning"),
                "info": sum(1 for f in findings if f["severity"] == "info"),
            },
            "runtime": report,
            "provider_notes": llm_notes,
            "mode": "provider" if llm_notes else "static",
            "at": _now(),
        }
        self._log(learner_id, "review", {"files": sorted(files), "findings": len(findings)},
                  role="reviewer", mode=result["mode"])
        return result

    # ----------------------------------------------------------------- hints
    def hint(self, learner_id: str, goal: str, failures: list[dict] | None = None,
             code: str | None = None, level: int = 1, locale: str = "en") -> dict:
        """Progressive hints grounded in the real failure list.

        Level 1 restates the goal, level 2 names the first failing assertion,
        level 3 points at the shape of the fix, level 4 sketches the structure.
        The reference solution is never emitted here.
        """
        level = max(1, min(4, int(level)))
        failures = failures or []
        lines = []
        if locale == "ar":
            lines.append(f"الهدف: {goal}")
            if failures:
                first = failures[0]
                lines.append(f"أول فحص فاشل: {first.get('name') or 'assertion'} - {first.get('message') or ''}")
            if level == 1:
                lines.append("اقرأ رسالة الفشل كلمة بكلمة: القيمة المتوقعة والقيمة الفعلية تخبرك أين الخطأ.")
            elif level == 2:
                lines.append("حدّد أي سطر في كودك ينتج القيمة الفعلية، وتحقّق منه بـ print واحدة قبل الإصلاح.")
            elif level == 3:
                lines.append("فكّك المسألة: ما نوع المُدخل (قائمة/نص/قاموس)؟ وما القيمة الحدية (فارغ، سالب، مكرّر)؟")
            else:
                lines.append("اكتب هيكلاً: دالة تستقبل المُدخل، حلقة/تراكم، إرجاع النتيجة - ثم املأ الفراغات.")
        else:
            lines.append(f"Goal: {goal}")
            if failures:
                first = failures[0]
                lines.append(f"First failing check: {first.get('name') or 'assertion'} - {first.get('message') or ''}")
            if level == 1:
                lines.append("Read the failure message word by word: expected vs actual tells you where to look.")
            elif level == 2:
                lines.append("Find the line that produces the actual value and confirm it with one print before fixing.")
            elif level == 3:
                lines.append("Break it down: what is the input type (list/str/dict)? What are the edge cases "
                             "(empty, negative, duplicate)?")
            else:
                lines.append("Sketch the shape: a function that takes the input, a loop or accumulator, then a return - "
                             "then fill the blanks.")

        if code and level >= 2:
            try:
                tree = ast.parse(code)
            except SyntaxError as error:
                lines.append(f"SyntaxError on line {error.lineno}: {error.msg}")
            else:
                visitor = _StaticReview()
                visitor.visit(tree)
                for finding in visitor.finish()[:3]:
                    lines.append(f"- line {finding['line']}: {_finding_text(finding['kind'], locale)}")

        payload = {"goal": goal, "level": level, "failures": failures[:5], "hints": lines, "locale": locale}
        self._log(learner_id, "hint", {"goal": goal[:200], "level": level, "locale": locale},
                  role="coach", mode="heuristic")
        return payload

    # ------------------------------------------------------------- internals
    def _facts(self, files: dict[str, str] | None, run_report: dict | None) -> list[str]:
        facts: list[str] = []
        if files:
            for path, source in sorted(files.items()):
                facts.append(f"{path} ({len(source.splitlines())} lines)")
        if run_report:
            facts.append(f"run ok={run_report.get('ok')}")
            for item in (run_report.get("failures") or [])[:3]:
                facts.append(f"failed: {item.get('name')} - {item.get('message')}")
            error = run_report.get("error")
            if error:
                facts.append(f"error: {error}")
        return facts

    def _code_dump(self, files: dict[str, str]) -> str:
        chunks = []
        for path, source in sorted(files.items()):
            chunks.append(f"# {path}\n{source}")
        return "\n\n".join(chunks)[:12000]

    def _messages(self, mentor: Mentor, question: str, locale: str, facts: list[str]) -> list[Message]:
        language = "Arabic" if locale == "ar" else "English"
        system = (
            f"You are '{mentor.name_en}', a Python mentor. {mentor.persona} "
            f"Answer in {language}, in at most 6 short numbered points. "
            "Never write the full solution unless the learner explicitly asks for it; prefer guiding questions. "
            "Only use the provided facts; if something is unknown, say so."
        )
        user = question
        if facts:
            user += "\n\nFacts:\n- " + "\n- ".join(facts)
        return [Message("system", system), Message("user", user)]

    def _heuristic_answer(self, mentor: Mentor, question: str, locale: str, facts: list[str]) -> str:
        ar = locale == "ar"
        lines: list[str] = []
        if ar:
            lines.append(f"أنا {mentor.name_ar}. أعمل بالتحليل المحلي (لا يوجد مزوّد ذكاء اصطناعي مضبوط).")
        else:
            lines.append(f"I am {mentor.name_en}. I am running on local analysis (no AI provider configured).")
        if facts:
            lines.append("ما أعرفه عن حالتك:" if ar else "What I can see about your situation:")
            lines += [f"- {fact}" for fact in facts]
        else:
            lines.append("لا توجد نتائج تشغيل مرفقة." if ar else "No run results were attached.")
        if mentor.id == "debugger":
            lines.append("أرسل تقرير التنفيذ (رسالة الخطأ أو الفحص الفاشل) لأشخّص بدقة."
                         if ar else "Send me the execution report (error message or failing check) and I will diagnose precisely.")
        elif mentor.id == "architect":
            lines.append("قسّم المشكلة إلى دوال صغيرة ذات أسماء واضحة قبل كتابة التفاصيل."
                         if ar else "Split the problem into small, clearly named functions before writing details.")
        elif mentor.id == "reviewer":
            lines.append("أضف اختباراً واحداً يفشل الآن؛ سيكون دليلك عند الإصلاح."
                         if ar else "Add one test that fails now - it becomes your proof when you fix it.")
        elif mentor.id == "researcher":
            lines.append("اسأل نفسك: ما حجم المُدخل؟ هل O(n²) مقبول هنا؟"
                         if ar else "Ask yourself: how large is the input? Is O(n^2) acceptable here?")
        else:
            lines.append("ما الذي جرّبته حتى الآن؟ ابدأ بأصغر مُدخل يُظهر المشكلة."
                         if ar else "What have you tried so far? Start from the smallest input that shows the problem.")
        return "\n".join(lines)

    def _follow_ups(self, mentor: Mentor, locale: str, question: str) -> list[str]:
        ar = locale == "ar"
        generic = [
            "ما أصغر مُدخل يُظهر الخطأ؟" if ar else "What is the smallest input that reproduces the failure?",
            "ما النتيجة التي تتوقعها بالضبط؟" if ar else "What exactly do you expect the result to be?",
            "كيف ستختبر هذا الحالة الحدية؟" if ar else "How will you test the edge case?",
        ]
        return generic

    def _synthesise(self, opinions: list[dict], locale: str) -> str:
        names = ", ".join(item["mentor"]["name" if locale == "en" else "name_ar"] for item in opinions)
        sources = {item["source"] for item in opinions}
        mode = "provider" if "provider" in sources else "heuristic"
        if locale == "ar":
            return f"شارك في الإجابة: {names}. طريقة التوليد: {mode}."
        return f"Contributors: {names}. Generation mode: {mode}."

    def _explain_failure(self, report: dict, locale: str) -> str:
        error = report.get("error") or {}
        error_type = error.get("type") or "Error"
        message = error.get("message") or ""
        if locale == "ar":
            return f"التنفيذ فشل: {error_type}: {message}"
        return f"Execution failed: {error_type}: {message}"

    def _log(self, learner_id: str, kind: str, payload: dict, role: str = "council",
             mode: str = "heuristic") -> None:
        """Record the assistance request.

        Logging must never break the run loop, so failures are swallowed - but
        they are reported through :meth:`status` rather than silently ignored.
        """
        try:
            with self.db.transaction() as conn:
                conn.execute(
                    "INSERT INTO ai_assistance (id, learner_id, context_type, context_id, role, mode,"
                    " request_json, response_json, provider, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        _id(),
                        learner_id,
                        kind,
                        payload.get("mentor") or payload.get("goal") or "",
                        role,
                        mode,
                        json.dumps(payload, ensure_ascii=False),
                        json.dumps({"logged": True}, ensure_ascii=False),
                        self.provider.name,
                        _now(),
                    ),
                )
        except Exception as error:  # noqa: BLE001 - mentoring must never break the run loop
            self._last_error = str(error)

    def history(self, learner_id: str, limit: int = 30) -> list[dict]:
        rows = self.db.query_all(
            "SELECT id, context_type AS kind, role, mode, provider, request_json, created_at"
            " FROM ai_assistance WHERE learner_id = ? ORDER BY created_at DESC LIMIT ?",
            (learner_id, limit),
        )
        out = []
        for row in rows:
            item = dict(row)
            try:
                item["request"] = json.loads(item.pop("request_json"))
            except ValueError:
                item["request"] = {}
            out.append(item)
        return out


__all__ = ["MentorService", "MENTORS", "Mentor", "Completion"]
