"""Skill mastery states and the rules that govern transitions between them.

The state machine deliberately distinguishes *durability* from *recency* and
*independence* from *assisted success*, because the primary learner is someone
who previously knew Python and may have partially forgotten it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class SkillState(str, Enum):
    NOT_ASSESSED = "not_assessed"
    PREVIOUSLY_FAMILIAR = "previously_familiar"
    RECOVERY_RECOMMENDED = "recovery_recommended"
    CURRENTLY_UNCERTAIN = "currently_uncertain"
    PARTIALLY_DEMONSTRATED = "partially_demonstrated"
    DEMONSTRATED = "demonstrated"
    INDEPENDENTLY_PRACTICED = "independently_practiced"
    TRANSFER_DEMONSTRATED = "transfer_demonstrated"

    @property
    def is_positive(self) -> bool:
        return self in _POSITIVE

    def label(self, locale: str = "en") -> str:
        return _LABELS[self.value][locale]


_POSITIVE: Final = frozenset(
    {
        SkillState.DEMONSTRATED,
        SkillState.INDEPENDENTLY_PRACTICED,
        SkillState.TRANSFER_DEMONSTRATED,
    }
)

_LABELS: Final[dict[str, dict[str, str]]] = {
    "not_assessed": {"en": "Not assessed", "ar": "لم يُقيَّم بعد"},
    "previously_familiar": {"en": "Previously familiar", "ar": "معرفة سابقة"},
    "recovery_recommended": {"en": "Recovery recommended", "ar": "يُنصح بالمراجعة"},
    "currently_uncertain": {"en": "Currently uncertain", "ar": "غير متأكد حالياً"},
    "partially_demonstrated": {"en": "Partially demonstrated", "ar": "مُثبت جزئياً"},
    "demonstrated": {"en": "Demonstrated", "ar": "مُثبت"},
    "independently_practiced": {"en": "Independently practiced", "ar": "مُطبَق باستقلالية"},
    "transfer_demonstrated": {"en": "Transfer demonstrated", "ar": "مُثبت بالتحويل"},
}

# Mastery ordering used to decide whether new evidence may raise a state.
_ORDER: Final[list[SkillState]] = [
    SkillState.NOT_ASSESSED,
    SkillState.PREVIOUSLY_FAMILIAR,
    SkillState.RECOVERY_RECOMMENDED,
    SkillState.CURRENTLY_UNCERTAIN,
    SkillState.PARTIALLY_DEMONSTRATED,
    SkillState.DEMONSTRATED,
    SkillState.INDEPENDENTLY_PRACTICED,
    SkillState.TRANSFER_DEMONSTRATED,
]

_RANK: Final[dict[SkillState, int]] = {state: i for i, state in enumerate(_ORDER)}


def rank(state: SkillState | str) -> int:
    return _RANK[SkillState(state)]


class Outcome(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    ERROR = "error"


class Independence(str, Enum):
    """How much of the work was done without mentor/model assistance."""

    INDEPENDENT = "independent"
    HINTED = "hinted"
    GUIDED = "guided"
    ASSISTED = "assisted"  # mentor supplied substantial code or a full solution


_INDEPENDENCE_RANK: Final[dict[Independence, int]] = {
    Independence.ASSISTED: 0,
    Independence.GUIDED: 1,
    Independence.HINTED: 2,
    Independence.INDEPENDENT: 3,
}


def independence_rank(value: Independence | str) -> int:
    return _INDEPENDENCE_RANK[Independence(value)]


@dataclass(frozen=True, slots=True)
class Transition:
    """Result of folding one piece of evidence into an existing skill state."""

    state: SkillState
    confidence: float
    review_interval_days: float
    note_ar: str
    note_en: str


def _interval(state: SkillState, current: float) -> float:
    """Spaced-repetition style review interval with honest, modest growth."""
    base = {
        SkillState.NOT_ASSESSED: 0.5,
        SkillState.PREVIOUSLY_FAMILIAR: 1.0,
        SkillState.RECOVERY_RECOMMENDED: 0.5,
        SkillState.CURRENTLY_UNCERTAIN: 1.0,
        SkillState.PARTIALLY_DEMONSTRATED: 2.0,
        SkillState.DEMONSTRATED: 4.0,
        SkillState.INDEPENDENTLY_PRACTICED: 8.0,
        SkillState.TRANSFER_DEMONSTRATED: 16.0,
    }[state]
    return max(base, min(current * 1.8, 45.0) if current >= base else base)


def apply_evidence(
    *,
    state: SkillState | str,
    confidence: float,
    outcome: Outcome | str,
    independence: Independence | str,
    evidence_count: int,
    independent_count: int,
    transfer: bool = False,
    review_interval_days: float = 1.0,
    prior_knowledge: bool = False,
) -> Transition:
    """Fold a single evidence record into a skill state.

    Rules (deliberately conservative - mastery must be earned):
      * failure only ever lowers or holds a state;
      * assisted success can raise a skill no higher than ``demonstrated``;
      * ``independently_practiced`` requires repeated independent successes;
      * ``transfer_demonstrated`` requires success in a *new context*.
    """
    current = SkillState(state)
    out = Outcome(outcome)
    indep = Independence(independence)

    if out in (Outcome.FAILURE, Outcome.ERROR):
        lowered = {
            SkillState.TRANSFER_DEMONSTRATED: SkillState.INDEPENDENTLY_PRACTICED,
            SkillState.INDEPENDENTLY_PRACTICED: SkillState.DEMONSTRATED,
            SkillState.DEMONSTRATED: SkillState.CURRENTLY_UNCERTAIN,
            SkillState.PARTIALLY_DEMONSTRATED: SkillState.CURRENTLY_UNCERTAIN,
            SkillState.CURRENTLY_UNCERTAIN: SkillState.RECOVERY_RECOMMENDED,
            SkillState.PREVIOUSLY_FAMILIAR: SkillState.RECOVERY_RECOMMENDED,
            SkillState.RECOVERY_RECOMMENDED: SkillState.RECOVERY_RECOMMENDED,
            SkillState.NOT_ASSESSED: SkillState.RECOVERY_RECOMMENDED,
        }[current]
        return Transition(
            state=lowered,
            confidence=max(0.0, round(confidence * 0.6, 3)),
            review_interval_days=max(0.5, review_interval_days * 0.5),
            note_ar="نتيجة غير ناجحة: تم تخفيض حالة المهارة وستتم مراجعتها قريباً.",
            note_en="Unsuccessful attempt: the skill state was lowered and will be reviewed soon.",
        )

    gain = {
        Outcome.SUCCESS: 0.34,
        Outcome.PARTIAL: 0.16,
        Outcome.FAILURE: 0.0,
        Outcome.ERROR: 0.0,
    }[out]
    gain *= 1.0 if independence_rank(indep) >= 2 else 0.6
    confidence = round(min(1.0, confidence + gain), 3)

    if transfer and independence_rank(indep) >= 2 and out is Outcome.SUCCESS and independent_count >= 2:
        new_state = SkillState.TRANSFER_DEMONSTRATED
    elif out is Outcome.SUCCESS and independence_rank(indep) == 3 and independent_count >= 3 and confidence >= 0.7:
        new_state = SkillState.INDEPENDENTLY_PRACTICED
    elif out is Outcome.SUCCESS and independence_rank(indep) >= 2 and confidence >= 0.5:
        new_state = SkillState.DEMONSTRATED
    elif out is Outcome.SUCCESS:
        new_state = SkillState.DEMONSTRATED if independence_rank(indep) >= 1 else SkillState.PARTIALLY_DEMONSTRATED
    else:  # partial
        new_state = (
            SkillState.PARTIALLY_DEMONSTRATED
            if rank(current) < rank(SkillState.PARTIALLY_DEMONSTRATED)
            else current
        )

    # Assisted work can never be certified as independent practice.
    if independence_rank(indep) < 2 and rank(new_state) > rank(SkillState.DEMONSTRATED):
        new_state = SkillState.DEMONSTRATED

    new_state = new_state if rank(new_state) > rank(current) else current

    if (
        prior_knowledge
        and new_state in (SkillState.NOT_ASSESSED,)
        and out is Outcome.SUCCESS
    ):
        new_state = SkillState.PREVIOUSLY_FAMILIAR

    note_ar = {
        SkillState.PARTIALLY_DEMONSTRATED: "أداء جزئي: المهارة قيد التكوين وتحتاج تطبيقاً إضافياً.",
        SkillState.DEMONSTRATED: "أُثبتت المهارة في هذا السياق؛ ولم يُتحقق بعد من نقلها إلى سياقات أخرى.",
        SkillState.INDEPENDENTLY_PRACTICED: "تم تطبيق المهارة باستقلالية متكررة.",
        SkillState.TRANSFER_DEMONSTRATED: "تم نقل المهارة إلى سياق جديد بنجاح.",
    }.get(new_state, "تم تحديث حالة المهارة.")
    note_en = {
        SkillState.PARTIALLY_DEMONSTRATED: "Partial performance: the skill is still forming.",
        SkillState.DEMONSTRATED: "Demonstrated in this context; transfer to new contexts is not yet verified.",
        SkillState.INDEPENDENTLY_PRACTICED: "Applied independently and repeatedly.",
        SkillState.TRANSFER_DEMONSTRATED: "Skill transferred successfully into a new context.",
    }.get(new_state, "Skill state updated.")

    return Transition(
        state=new_state,
        confidence=confidence,
        review_interval_days=_interval(new_state, review_interval_days),
        note_ar=note_ar,
        note_en=note_en,
    )
