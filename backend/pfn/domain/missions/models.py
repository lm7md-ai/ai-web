"""Mission data model shared by every world."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Mission:
    id: str
    world: str
    title_ar: str
    title_en: str
    brief_ar: str
    brief_en: str
    order_index: int
    difficulty: int = 1
    skills: tuple[str, ...] = ()
    config: dict = field(default_factory=dict)
    starter_code: str = ""
    reference_solution: str = ""
    hints: tuple[str, ...] = ()
    concepts_ar: str = ""
    concepts_en: str = ""

    def title(self, locale: str = "en") -> str:
        return self.title_ar if locale == "ar" else self.title_en

    def brief(self, locale: str = "en") -> str:
        return self.brief_ar if locale == "ar" else self.brief_en

    def concepts(self, locale: str = "en") -> str:
        return self.concepts_ar if locale == "ar" else self.concepts_en

    def to_dict(self, locale: str = "en", include_solution: bool = False) -> dict:
        payload = {
            "id": self.id,
            "world": self.world,
            "title": self.title(locale),
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "brief": self.brief(locale),
            "brief_ar": self.brief_ar,
            "brief_en": self.brief_en,
            "concepts": self.concepts(locale),
            "difficulty": self.difficulty,
            "order_index": self.order_index,
            "skills": list(self.skills),
            "config": self.config,
            "starter_code": self.starter_code,
            "hints_available": len(self.hints),
            "concepts_ar": self.concepts_ar,
            "concepts_en": self.concepts_en,
        }
        if include_solution:
            payload["reference_solution"] = self.reference_solution
            payload["hints"] = list(self.hints)
        return payload
