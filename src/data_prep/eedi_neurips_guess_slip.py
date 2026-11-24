"""WBS 5.5: multiple-choice guess/slip (G/S) and distractor probabilities from the
Eedi NeurIPS 2020 Education Challenge data (task 1-2; every question has 4 options).

The data is not in this repo. Download data.zip from
https://dqanonymousdata.blob.core.windows.net/neurips-public/data.zip and unzip it.

Usage:
    python src/data_prep/eedi_neurips_guess_slip.py <.../data> [out_dir]

out_dir defaults to data/interim/ (git-ignored). Outputs:
    eedi_neurips_bkt_mc.csv            - per skill: L0, T, G, S (multiple choice) + holdout AUC
    eedi_neurips_celdirici.csv         - per question and wrong option: P(option | wrong answer)
    eedi_neurips_mc_raporu.md

Method
- Skill mapping by Eedi SubjectId (same ids as the ASSISTments mapping):
  S1 226, S2 228, S3 230, S4 231, S5 232, S6 237/238. Questions tagged with more
  than one of the six skills are dropped.
- Answers are ordered per student by DateAnswered.
- BKT (pyBKT, forgets off) is fitted per skill on a random sample of students
  (MAX_ROWS rows per skill, to keep the run short), with an 80/20 student split
  for a holdout AUC, then refitted on the whole sample. Only G and S are meant to be
  used (for multiple-choice exercises in Simulator A); L0 and T stay from ASSISTments.
- Distractor probabilities use all answers of questions with at least
  MIN_WRONG wrong answers.
"""
from __future__ import annotations

import json
import os
import sys
import time
import warnings
from multiprocessing import Pool

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

SEED = 42
NUM_FITS = 3
MAX_ROWS = 60_000
MIN_WRONG = 50
CORE = {226: "S1", 228: "S2", 230: "S3", 231: "S4", 232: "S5", 237: "S6", 238: "S6"}
SKILLS = ["S1", "S2", "S3", "S4", "S5", "S6"]


def auc(y, p):
    y = np.asarray(y)
    n1 = y.sum()
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = pd.Series(np.asarray(p)).rank().values
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def fit_skill(args):
    skill, df = args
    from pyBKT.models import Model

    t0 = time.time()
    defaults = {"order_id": "order", "skill_name": "skill_code", "correct": "IsCorrect", "user_id": "UserId"}
    rng = np.random.RandomState(SEED)
    users = df["UserId"].unique()
    rng.shuffle(users)
    test_users = set(users[: len(users) // 5])
    train = df[~df["UserId"].isin(test_users)]
    test = df[df["UserId"].isin(test_users)]

    m = Model(seed=SEED, num_fits=NUM_FITS, parallel=False)
    m.fit(data=train, defaults=defaults)
    pred = m.predict(data=test)
    holdout_auc = auc(pred["IsCorrect"], pred["correct_predictions"])

    m = Model(seed=SEED, num_fits=NUM_FITS, parallel=False)
    m.fit(data=df, defaults=defaults)
    p = m.params().reset_index()

    def get(param):
        return float(p[p["param"] == param]["value"].iloc[0])

    print(f"{skill} bitti ({(time.time() - t0) / 60:.1f} dk)", flush=True)
    return {
        "skill": skill, "L0": get("prior"), "T": get("learns"), "G": get("guesses"), "S": get("slips"),
        "holdout_auc": holdout_auc, "rows": len(df), "students": df["UserId"].nunique(),
        "accuracy": float(df["IsCorrect"].mean()),
    }


def main():
    T0 = time.time()
    D = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "..", "..", "data", "interim")
    os.makedirs(out_dir, exist_ok=True)

    q = pd.read_csv(f"{D}/metadata/question_metadata_task_1_2.csv")

    def to_skill(s):
        ks = {CORE[x] for x in json.loads(s) if x in CORE}
        return ks.pop() if len(ks) == 1 else None

    q["skill_code"] = q["SubjectId"].map(to_skill)
    n_multi = int(q["SubjectId"].map(lambda s: len({CORE[x] for x in json.loads(s) if x in CORE}) > 1).sum())
    q = q.dropna(subset=["skill_code"])[["QuestionId", "skill_code"]]

    a = pd.read_csv(f"{D}/train_data/train_task_1_2.csv")
    a = a.merge(q, on="QuestionId")
    meta = pd.read_csv(f"{D}/metadata/answer_metadata_task_1_2.csv", usecols=["AnswerId", "DateAnswered"])
    a = a.merge(meta, on="AnswerId", how="left")
    a = a.sort_values(["UserId", "DateAnswered", "AnswerId"]).reset_index(drop=True)
    a["order"] = np.arange(len(a))

    # ---- distractor probabilities ----
    wrong = a[a["IsCorrect"] == 0]
    cnt = wrong.groupby(["QuestionId", "AnswerValue"]).size().rename("n").reset_index()
    tot = cnt.groupby("QuestionId")["n"].transform("sum")
    cnt["p_given_wrong"] = cnt["n"] / tot
    cnt = cnt[tot >= MIN_WRONG].merge(q, on="QuestionId")
    cnt.to_csv(os.path.join(out_dir, "eedi_neurips_celdirici.csv"), index=False)
    top_share = cnt.groupby(["skill_code", "QuestionId"])["p_given_wrong"].max().reset_index()

    # ---- BKT per skill on a student sample ----
    rng = np.random.RandomState(SEED)
    jobs = []
    for sk in SKILLS:
        d = a[a["skill_code"] == sk]
        users = d["UserId"].unique()
        rng.shuffle(users)
        sizes = d.groupby("UserId").size().loc[users].cumsum()
        keep = set(sizes[sizes <= MAX_ROWS].index)
        jobs.append((sk, d[d["UserId"].isin(keep)][["UserId", "order", "skill_code", "IsCorrect"]].copy()))
    with Pool(len(jobs)) as pool:
        res = pool.map(fit_skill, jobs)
    bkt = pd.DataFrame(res)
    bkt["makul"] = (bkt["G"] < 0.5) & (bkt["S"] < 0.5) & (bkt["T"] > 0)
    bkt.to_csv(os.path.join(out_dir, "eedi_neurips_bkt_mc.csv"), index=False)

    # ---- report ----
    L = ["# Eedi NeurIPS 2020: çoktan seçmeli G/S ve çeldirici olasılıkları (WBS 5.5)\n",
         f"Veri: task 1-2, {a['QuestionId'].nunique():,} kesir sorusu, {len(a):,} cevap, "
         f"{a['UserId'].nunique():,} öğrenci (birden fazla beceriye etiketli {n_multi} soru çıkarıldı). "
         f"BKT, beceri başına en fazla {MAX_ROWS:,} satırlık rastgele öğrenci örneğiyle kestirildi. "
         f"Süre: {(time.time() - T0) / 60:.1f} dk\n",
         "| Beceri | Satır (örnek) | Öğrenci | Doğruluk | L0 | T | G | S | Holdout AUC | Makul |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in bkt.iterrows():
        L.append(f"| {r.skill} | {r.rows:,} | {r.students:,} | {r.accuracy:.2f} | {r.L0:.3f} | {r['T']:.3f} | "
                 f"{r.G:.3f} | {r.S:.3f} | {r.holdout_auc:.3f} | {'evet' if r.makul else '**hayır**'} |")
    L.append(f"\n## Çeldirici yoğunlaşması (en az {MIN_WRONG} yanlış cevabı olan sorular)\n")
    L.append("En sık seçilen yanlış şıkkın yanlış cevaplardaki payı (rastgele seçimde 0,33).\n")
    L.append("| Beceri | Soru | Medyan pay | Payı ≥ 0,5 olan soru oranı |")
    L.append("|---|---|---|---|")
    for sk in SKILLS:
        t = top_share[top_share["skill_code"] == sk]["p_given_wrong"]
        if len(t):
            L.append(f"| {sk} | {len(t)} | {t.median():.2f} | %{100 * (t >= 0.5).mean():.0f} |")
    t = top_share["p_given_wrong"]
    L.append(f"| **Toplam** | {len(t)} | {t.median():.2f} | %{100 * (t >= 0.5).mean():.0f} |")
    text = "\n".join(L) + "\n"
    with open(os.path.join(out_dir, "eedi_neurips_mc_raporu.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
