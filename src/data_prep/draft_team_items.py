"""WBS 5.2: draft team-written teaching items for skills with too few Eedi items.

Decision 25 Nov 2026 (risk 10): the missing teaching items are written by the team;
each wrong option is mapped to an Eedi misconception (MisconceptionId from the Kaggle
"Eedi - Mining Misconceptions in Mathematics" mapping). Items are generated from
templates and every answer is checked with exact fraction arithmetic (`fractions`).

These are DRAFTS: status 'pending', created_by 'claude-draft'. A team member must
read each one and set it to 'approved' (FR-11: the author cannot approve their own items).

Output: data/processed/team_items_draft.json (our own content, so it can be in Git).
Usage: python src/data_prep/draft_team_items.py
"""
from __future__ import annotations

import json
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "data", "processed", "team_items_draft.json")

# Eedi MisconceptionIds used (names from misconception_mapping.csv)
M_NOT_UNDERSTAND_EQUIV = 120  # Does not understand equivalent fractions
M_ADDITIVE = 1429  # Believes equivalent fractions are formed with addition not multiplication
M_MULTIPLIER_AS_NUMERATOR = 6  # Can identify the multiplier ... but does not apply to the numerator


def frac(n, d) -> str:
    return rf"\( \frac{{{n}}}{{{d}}} \)"


def s1_missing_numerator(a: int, b: int, k: int) -> dict:
    """a/b = ?/(k*b). Correct: k*a."""
    c = k * b
    correct = k * a
    wrong = [
        (a + (c - b), M_ADDITIVE),  # adds the same number to top and bottom
        (k, M_MULTIPLIER_AS_NUMERATOR),  # writes the multiplier as the numerator
        (a, M_NOT_UNDERSTAND_EQUIV),  # keeps the numerator unchanged
    ]
    assert Fraction(correct, c) == Fraction(a, b)
    return _mc_item(
        "S1",
        rf"Complete the statement \( \frac{{{a}}}{{{b}}}=\frac{{?}}{{{c}}} \)",
        correct, wrong, fmt=lambda v: rf"\( {v} \)",
        check=lambda v: Fraction(v, c) == Fraction(a, b),
        difficulty="easy" if k <= 3 else "hard",
        template="s1_missing_numerator",
    )


def s1_missing_denominator(a: int, b: int, k: int) -> dict:
    """a/b = (k*a)/?. Correct: k*b."""
    n = k * a
    correct = k * b
    wrong = [
        (b + (n - a), M_ADDITIVE),  # adds the same number to top and bottom
        (b, M_NOT_UNDERSTAND_EQUIV),  # keeps the denominator unchanged
        (n, M_NOT_UNDERSTAND_EQUIV),  # copies the numerator (gives n/n = 1)
    ]
    assert Fraction(n, correct) == Fraction(a, b)
    item = _mc_item(
        "S1",
        rf"Complete the statement \( \frac{{{a}}}{{{b}}}=\frac{{{n}}}{{?}} \)",
        correct, wrong, fmt=lambda v: rf"\( {v} \)",
        check=lambda v: Fraction(n, v) == Fraction(a, b),
        difficulty="easy" if k <= 3 else "hard",
        template="s1_missing_denominator",
    )
    return item


def _mc_item(skill, text, correct, wrong: list, fmt, check, difficulty, template) -> dict:
    """wrong: list of (value, misconception_id); every wrong option must have a label (FR-07)."""
    values = [correct, *(v for v, _ in wrong)]
    if len(set(values)) != len(values):
        raise ValueError(f"duplicate options in {text}: {values}")
    for v in values[1:]:
        if check(v):
            raise ValueError(f"distractor {v} is also correct in {text}")
    if not check(correct):
        raise ValueError(f"correct answer wrong in {text}")
    if any(m is None for _, m in wrong):
        raise ValueError(f"unlabelled distractor in {text}")
    opts = [(correct, None)] + list(wrong)
    if len(opts) != 4:
        raise ValueError(f"need 4 options, got {len(opts)} in {text}")
    # deterministic but varied position of the correct answer
    shift = sum(map(ord, text)) % 4
    opts = opts[shift:] + opts[:shift]
    labels = "ABCD"
    return {
        "skill_id": skill,
        "pool": "teaching",
        "item_format": "multiple_choice",
        "difficulty": difficulty,
        "question_text": text,
        "correct_answer": labels[[i for i, (v, _) in enumerate(opts) if v == correct][0]],
        "options": [
            {"label": labels[i], "text": fmt(v), "misconception_id": m} for i, (v, m) in enumerate(opts)
        ],
        "source": "team",
        "license": "project (team-written)",
        "status": "pending",
        "created_by": "claude-draft",
        "template": template,
    }


def draft_s1() -> list[dict]:
    items = []
    # (a, b, k): proper fractions in lowest terms, small multipliers; for missing numerator a must differ from 1 and k
    # (otherwise the correct answer k*a equals the "multiplier as numerator" distractor k)
    for a, b, k in [(5, 8, 3), (2, 3, 4), (3, 4, 2), (2, 5, 3), (3, 7, 2), (4, 5, 3), (5, 6, 3), (3, 8, 5), (7, 9, 2)]:
        items.append(s1_missing_numerator(a, b, k))
    for a, b, k in [(1, 3, 4), (2, 7, 3), (3, 5, 2), (4, 9, 3), (5, 8, 2), (2, 9, 5), (5, 7, 4), (1, 6, 5)]:
        items.append(s1_missing_denominator(a, b, k))
    return items


def main() -> None:
    items = draft_s1()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"{len(items)} draft items written to {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
