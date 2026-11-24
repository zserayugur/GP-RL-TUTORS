"""Resolve a displayed LLM choice against an approved teaching item (FR-40)."""
from dataclasses import dataclass
import sqlite3


@dataclass(frozen=True)
class Choice:
    item_id: int
    canonical_label: str | None
    correct: bool | None
    misconception_id: int | None


def resolve_choice(db: sqlite3.Connection, item_id: int, order: str, reply: str) -> Choice:
    """order[i] is the original label shown in display position i; no DB writes."""
    if sorted(order) != list("ABCD"):
        raise ValueError("order must be a permutation of ABCD")
    rows = db.execute("""
        SELECT o.option_label, o.is_correct, o.misconception_id, i.correct_answer
        FROM usable_items i JOIN item_options o USING(item_id)
        WHERE i.item_id=? AND i.pool='teaching' AND i.item_format='multiple_choice'
    """, (item_id,)).fetchall()
    if (sorted(r[0] for r in rows) != list("ABCD")
            or sum(r[1] for r in rows) != 1
            or any(bool(flag) != (label == key) for label, flag, _, key in rows)):
        raise ValueError("ineligible item or inconsistent options")
    letter = reply.strip().upper()
    if letter not in tuple("ABCD"):
        return Choice(item_id, None, None, None)
    original = order["ABCD".index(letter)]
    _, correct, code, _ = next(r for r in rows if r[0] == original)
    return Choice(item_id, original, bool(correct), None if correct else code)
