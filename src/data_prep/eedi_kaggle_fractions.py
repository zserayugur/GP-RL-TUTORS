"""WBS 5.4: select fraction questions from Kaggle "Eedi - Mining Misconceptions in
Mathematics" and count their misconception labels.

The data is CC BY-NC 4.0 and must not be redistributed: it is NOT in this repo.
Each team member downloads it with their own Kaggle account
(https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics).

Usage:
    python src/data_prep/eedi_kaggle_fractions.py <folder with train.csv> [out_dir]

out_dir defaults to data/interim/ (git-ignored). Outputs:
    eedi_kaggle_kesir_sorulari.csv   - selected questions (S1-S6), one row per question
    eedi_kaggle_kesir_yanilgilar.csv - one row per (question, wrong option) with its misconception
    eedi_kaggle_kesir_raporu.md      - counts per skill

Skill mapping uses Eedi SubjectId (same ids as in the NeurIPS 2020 analysis):
    S1 226 Equivalent Fractions        S4 231 Multiplying Fractions
    S2 228 Ordering Fractions          S5 232 Dividing Fractions
    S3 230 Adding and Subtracting Fr.  S6 237 Fractions<->Decimals, 238 Fractions<->Percentages
Candidate extra subjects (not in the approved 6 skills; reported separately, not selected):
    225 Fractions of an Amount, 227 Simplifying Fractions,
    229 Mixed Number and Improper Fractions, 239 Decimals<->Percentages.
Algebraic fractions (1077-1079) are out of scope.

Visual items: a question is flagged when its text contains an embedded image
"![...]()" or words such as diagram / shaded / number line / image / picture.
This is a heuristic; flagged items must be checked by hand (approved text: visual
items are flagged and not used in experiments).
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd

SKILL_SUBJECTS = {
    "S1": [226],
    "S2": [228],
    "S3": [230],
    "S4": [231],
    "S5": [232],
    "S6": [237, 238],
}
CANDIDATE_SUBJECTS = [225, 227, 229, 239]
VISUAL_PATTERN = re.compile(r"!\[|diagram|shaded|number line|\bimage\b|picture", re.IGNORECASE)
OPTIONS = ["A", "B", "C", "D"]

# Success criterion from the approved work plan (IP1): per skill at least
# 20 teaching items and 8 assessment items.
MIN_TEACHING_ITEMS = 20


def main() -> None:
    src = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "..", "data", "interim")
    os.makedirs(out_dir, exist_ok=True)

    train = pd.read_csv(os.path.join(src, "train.csv"))
    mis = pd.read_csv(os.path.join(src, "misconception_mapping.csv")).set_index("MisconceptionId")["MisconceptionName"]

    subj2skill = {sid: sk for sk, ids in SKILL_SUBJECTS.items() for sid in ids}
    q = train[train["SubjectId"].isin(subj2skill)].copy()
    q["skill_code"] = q["SubjectId"].map(subj2skill)
    q["visual_flag"] = q["QuestionText"].str.contains(VISUAL_PATTERN)

    # one row per wrong option
    rows = []
    for _, r in q.iterrows():
        for o in OPTIONS:
            if o == r["CorrectAnswer"]:
                continue
            mid = r[f"Misconception{o}Id"]
            rows.append({
                "QuestionId": r["QuestionId"],
                "skill_code": r["skill_code"],
                "option": o,
                "visual_flag": r["visual_flag"],
                "MisconceptionId": None if pd.isna(mid) else int(mid),
                "MisconceptionName": None if pd.isna(mid) else mis.get(int(mid)),
            })
    opts = pd.DataFrame(rows)

    q.drop(columns=[c for c in q.columns if c.startswith("Misconception")]).to_csv(
        os.path.join(out_dir, "eedi_kaggle_kesir_sorulari.csv"), index=False)
    opts.to_csv(os.path.join(out_dir, "eedi_kaggle_kesir_yanilgilar.csv"), index=False)

    # --- report ---
    L = ["# Eedi (Kaggle) kesir soruları ve yanılgı etiketleri (WBS 5.4)\n",
         f"Kaynak: `train.csv` ({len(train):,} soru, hepsi 4 şıklı). Seçilen kesir sorusu: **{len(q)}**.\n",
         "| Beceri | Soru | Görsel olabilir | Görselsiz soru | Yanlış şık | Etiketli yanlış şık | Farklı yanılgı | En az 20 görselsiz soru? |",
         "|---|---|---|---|---|---|---|---|"]
    for sk in SKILL_SUBJECTS:
        qs = q[q["skill_code"] == sk]
        os_ = opts[opts["skill_code"] == sk]
        lab = os_["MisconceptionId"].notna()
        n_novis = int((~qs["visual_flag"]).sum())
        L.append(f"| {sk} | {len(qs)} | {int(qs['visual_flag'].sum())} | {n_novis} | {len(os_)} | "
                 f"{int(lab.sum())} (%{100 * lab.mean():.0f}) | {os_.loc[lab, 'MisconceptionId'].nunique()} | "
                 f"{'evet' if n_novis >= MIN_TEACHING_ITEMS else '**hayır**'} |")
    lab_all = opts["MisconceptionId"].notna()
    L.append(f"| **Toplam** | {len(q)} | {int(q['visual_flag'].sum())} | {int((~q['visual_flag']).sum())} | "
             f"{len(opts)} | {int(lab_all.sum())} (%{100 * lab_all.mean():.0f}) | "
             f"{opts.loc[lab_all, 'MisconceptionId'].nunique()} | |")

    L.append("\n## Beceri başına en sık yanılgılar (ilk 3)\n")
    for sk in SKILL_SUBJECTS:
        top = opts[(opts["skill_code"] == sk) & opts["MisconceptionId"].notna()]["MisconceptionName"].value_counts().head(3)
        L.append(f"- **{sk}:** " + ("; ".join(f"{name} ({n})" for name, n in top.items()) or "—"))

    L.append("\n## Kapsam dışı aday konular (seçilmedi)\n")
    for sid in CANDIDATE_SUBJECTS:
        sub = train[train["SubjectId"] == sid]
        name = sub["SubjectName"].iloc[0] if len(sub) else "?"
        L.append(f"- {sid} {name}: {len(sub)} soru")
    L.append("\nNot: Görsel işareti sezgiseldir; elle kontrol edilmeli.")

    text = "\n".join(L) + "\n"
    with open(os.path.join(out_dir, "eedi_kaggle_kesir_raporu.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
