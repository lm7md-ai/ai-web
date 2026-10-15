"""Curriculum data model.

A published module must contain, per the product rules:

1. a verified explanation, 2. prerequisites, 3. an executable example,
4. an interactive experiment, 5. a practical task, 6. an assessment,
7. feedback, 8. a transfer activity, 9. source references,
10. progress persistence (handled by the registry + database).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TaskSpec:
    """A graded coding task: real pytest, hidden tests kept server-side."""

    brief_ar: str
    brief_en: str
    starter_code: str
    public_tests: dict[str, str]
    hidden_tests: dict[str, str]
    reference_solution: str
    hints: tuple[str, ...] = ()
    independent: bool = False  # assessment mode: no mentor help by default
    entry_filename: str = "main.py"
    extra_files: dict[str, str] = field(default_factory=dict)  # project context files

    def brief(self, locale: str = "en") -> str:
        return self.brief_ar if locale == "ar" else self.brief_en


@dataclass(frozen=True, slots=True)
class CurriculumModule:
    id: str
    level: int
    order_index: int
    domain: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    explanation_ar: str
    explanation_en: str
    skills: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    example_code: str = ""
    example_notes_ar: str = ""
    example_notes_en: str = ""
    experiment_code: str = ""
    experiment_brief_ar: str = ""
    experiment_brief_en: str = ""
    task: TaskSpec | None = None
    assessment: TaskSpec | None = None
    transfer_ar: str = ""
    transfer_en: str = ""
    transfer_task: TaskSpec | None = None
    references: tuple[tuple[str, str], ...] = ()

    # ------------------------------------------------------------ localised
    def title(self, locale: str = "en") -> str:
        return self.title_ar if locale == "ar" else self.title_en

    def summary(self, locale: str = "en") -> str:
        return self.summary_ar if locale == "ar" else self.summary_en

    def explanation(self, locale: str = "en") -> str:
        return self.explanation_ar if locale == "ar" else self.explanation_en

    def notes(self, locale: str = "en") -> str:
        return self.example_notes_ar if locale == "ar" else self.example_notes_en

    def experiment_brief(self, locale: str = "en") -> str:
        return self.experiment_brief_ar if locale == "ar" else self.experiment_brief_en

    def transfer(self, locale: str = "en") -> str:
        return self.transfer_ar if locale == "ar" else self.transfer_en

    # ------------------------------------------------------------ serialise
    def to_dict(self, locale: str = "en", include_hidden: bool = False) -> dict:
        payload = {
            "id": self.id,
            "level": self.level,
            "order_index": self.order_index,
            "domain": self.domain,
            "title": self.title(locale),
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "summary": self.summary(locale),
            "summary_ar": self.summary_ar,
            "summary_en": self.summary_en,
            "explanation": self.explanation(locale),
            "explanation_ar": self.explanation_ar,
            "explanation_en": self.explanation_en,
            "skills": list(self.skills),
            "prerequisites": list(self.prerequisites),
            "example_code": self.example_code,
            "example_notes": self.notes(locale),
            "experiment_code": self.experiment_code,
            "experiment_brief": self.experiment_brief(locale),
            "transfer": self.transfer(locale),
            "transfer_ar": self.transfer_ar,
            "transfer_en": self.transfer_en,
            "references": [{"title": t, "url": u} for t, u in self.references],
            "has_task": self.task is not None,
            "has_assessment": self.assessment is not None,
            "has_transfer_task": self.transfer_task is not None,
        }
        for name, spec in (("task", self.task), ("assessment", self.assessment), ("transfer_task", self.transfer_task)):
            if spec is None:
                payload[name] = None
                continue
            payload[name] = {
                "entry_filename": spec.entry_filename,
                "extra_files": dict(spec.extra_files),
                "brief": spec.brief(locale),
                "brief_ar": spec.brief_ar,
                "brief_en": spec.brief_en,
                "starter_code": spec.starter_code,
                "public_tests": spec.public_tests,
                "hints_available": len(spec.hints),
                "independent": spec.independent,
            }
            if include_hidden:
                payload[name]["hidden_tests"] = spec.hidden_tests
                payload[name]["reference_solution"] = spec.reference_solution
                payload[name]["hints"] = list(spec.hints)
        return payload
