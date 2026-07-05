"""UK statutory staff:child ratios for wraparound care (EYFS-based)."""

from collections import defaultdict
from dataclasses import dataclass


@dataclass
class RatioRequirement:
    age_min: int
    age_max: int
    children_per_staff: int
    label: str


# Statutory ratios for early years / wraparound (UK)
RATIO_TABLE = [
    RatioRequirement(0, 2, 3, "Under 2s (1:3)"),
    RatioRequirement(2, 3, 4, "Aged 2 (1:4)"),
    RatioRequirement(3, 5, 8, "Aged 3–4 (1:8)"),
    RatioRequirement(5, 8, 8, "Reception / Y1–Y2 (1:8)"),
    RatioRequirement(8, 12, 10, "Aged 8+ (1:10)"),
]


def required_staff_for_age(age: int) -> int:
    for ratio in RATIO_TABLE:
        if ratio.age_min <= age < ratio.age_max:
            return ratio.children_per_staff
    return 10


def required_staff_count(children_ages: list[int]) -> int:
    """Minimum staff needed based on youngest age group present (strictest ratio)."""
    if not children_ages:
        return 0
    min_ratio = min(required_staff_for_age(age) for age in children_ages)
    return max(1, -(-len(children_ages) // min_ratio))  # ceiling division


def analyse_session_ratio(children_ages: list[int], staff_count: int) -> dict:
    groups: dict[str, int] = defaultdict(int)
    for age in children_ages:
        for ratio in RATIO_TABLE:
            if ratio.age_min <= age < ratio.age_max:
                groups[ratio.label] += 1
                break

    required = required_staff_count(children_ages)
    compliant = staff_count >= required if children_ages else True

    return {
        "child_count": len(children_ages),
        "staff_count": staff_count,
        "required_staff": required,
        "compliant": compliant,
        "age_groups": dict(groups),
        "ratio_display": f"1:{max(required_staff_for_age(a) for a in children_ages) if children_ages else '—'}",
    }
