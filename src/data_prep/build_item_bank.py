"""WBS 5.2: build the SQLite item bank and load the Eedi (Kaggle) fraction questions.

Usage:
    python src/data_prep/build_item_bank.py <Kaggle Eedi folder with train.csv> [db_path]

db_path defaults to data/interim/item_bank.sqlite (git-ignored: it contains Eedi
question text, CC BY-NC 4.0, which must not be redistributed).

What is loaded now:
  - The 6 skills and the prerequisite graph (S1 -> S2, S3, S6; S4 -> S5).
  - Eedi misconceptions used by the selected questions.
  - Eedi fraction questions as 'teaching' / 'multiple_choice' items with their four
    options and option-level misconceptions. Visual items are loaded with
    visual_flag = 1 (kept, but excluded from `usable_items`).
What is still empty (to be filled by the team): difficulty, hint, worked_example,
explanation, and the short-answer 'test' pool (pre/post tests).
"""
from __future__ import annotations

import os
import sqlite3
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eedi_kaggle_fractions import SKILL_SUBJECTS, VISUAL_PATTERN  # noqa: E402

SKILLS = [
    ("S1", "Equivalent Fractions", ""),
    ("S2", "Ordering Fractions", "S1"),
    ("S3", "Addition and Subtraction Fractions", "S1"),
    ("S4", "Multiplication Fractions", ""),
    ("S5", "Division Fractions", "S4"),
    ("S6", "Conversion of Fraction Decimals Percents", "S1"),
]
MIN_TEACHING_ITEMS = 20  # IP1 success criterion
LICENSE = "CC BY-NC 4.0"


def create_db(db_path: str) -> sqlite3.Connection:
    if os.path.exists(db_path):
        os.remove(db_path)  # rebuilt from scratch every time (reproducible)
    con = sqlite3.connect(db_path)
    with open(os.path.join(HERE, "item_bank_schema.sql"), encoding="utf-8") as f:
        con.executescript(f.read())
    con.executemany("INSERT INTO skills VALUES (?, ?, ?)", SKILLS)
    return con


def load_eedi(con: sqlite3.Connection, src: str) -> pd.DataFrame:
    train = pd.read_csv(os.path.join(src, "train.csv"))
    mis = pd.read_csv(os.path.join(src, "misconception_mapping.csv"))
    subj2skill = {sid: sk for sk, ids in SKILL_SUBJECTS.items() for sid in ids}
    q = train[train["SubjectId"].isin(subj2skill)].copy()
    q["skill_id"] = q["SubjectId"].map(subj2skill)
    q["visual"] = q["QuestionText"].str.contains(VISUAL_PATTERN).astype(int)

    used = set()
    for o in "ABCD":
        used |= set(q[f"Misconception{o}Id"].dropna().astype(int))
    con.executemany(
        "INSERT INTO misconceptions VALUES (?, ?, 'eedi_kaggle')",
        mis[mis["MisconceptionId"].isin(used)][["MisconceptionId", "MisconceptionName"]].itertuples(index=False),
    )

    for _, r in q.iterrows():
        cur = con.execute(
            "INSERT INTO items (skill_id, pool, item_format, question_text, correct_answer, visual_flag,"
            " source, source_ref, license) VALUES (?, 'teaching', 'multiple_choice', ?, ?, ?, 'eedi_kaggle', ?, ?)",
            (r["skill_id"], r["QuestionText"], r["CorrectAnswer"], int(r["visual"]), str(r["QuestionId"]), LICENSE),
        )
        item_id = cur.lastrowid
        for o in "ABCD":
            mid = r[f"Misconception{o}Id"]
            is_correct = int(o == r["CorrectAnswer"])
            con.execute(
                "INSERT INTO item_options VALUES (?, ?, ?, ?, ?)",
                (item_id, o, r[f"Answer{o}Text"], is_correct, None if is_correct or pd.isna(mid) else int(mid)),
            )
    con.commit()
    return q


def report(con: sqlite3.Connection) -> str:
    rows = con.execute(
        """
        SELECT s.skill_id,
               COUNT(i.item_id),
               SUM(CASE WHEN i.visual_flag = 0 THEN 1 ELSE 0 END),
               (SELECT COUNT(*) FROM item_options o JOIN items j ON j.item_id = o.item_id
                 WHERE j.skill_id = s.skill_id AND j.visual_flag = 0 AND o.is_correct = 0),
               (SELECT COUNT(*) FROM item_options o JOIN items j ON j.item_id = o.item_id
                 WHERE j.skill_id = s.skill_id AND j.visual_flag = 0 AND o.is_correct = 0
                   AND o.misconception_id IS NOT NULL)
        FROM skills s LEFT JOIN items i ON i.skill_id = s.skill_id AND i.pool = 'teaching'
        GROUP BY s.skill_id ORDER BY s.skill_id
        """
    ).fetchall()
    L = ["| Beceri | Öğretim sorusu | Kullanılabilir (görselsiz) | Eksik (20'ye) | Etiketsiz yanlış şık |",
         "|---|---|---|---|---|"]
    for sk, n, usable, wrong, labelled in rows:
        usable = usable or 0
        L.append(f"| {sk} | {n} | {usable} | {max(0, MIN_TEACHING_ITEMS - usable)} | {wrong - labelled} / {wrong} |")
    return "\n".join(L)


def main() -> None:
    src = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "..", "data", "interim", "item_bank.sqlite")
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    con = create_db(db_path)
    load_eedi(con, src)
    print(report(con))
    con.close()


if __name__ == "__main__":
    main()
