# Literature notes — Seray (student models and simulators)

Format requested by the advisor (17 Nov): *previous work – limitation – our contribution*.
Reference numbers follow the approved TÜBİTAK reference list (`TYBS_Kaynakca`). Claims below are taken from Seray's draft of Sections 2.2–2.3 and from our own results; the "Check while reading" line lists what still has to be confirmed against the full text.

---

## [1] Corbett & Anderson (1994) — Bayesian Knowledge Tracing

Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge. *User Modeling and User-Adapted Interaction, 4*(4), 253–278. https://doi.org/10.1007/BF01099821

- **What it does:** Models each skill as a hidden binary state (learned / not learned) with four parameters: initial knowledge (L0), learning per practice opportunity (T), guess (G) and slip (S). The estimates drove mastery learning in a programming tutor; letting the parameters vary per skill clearly improved the fit to student data.
- **Limitation:** Knowledge is never forgotten, skills are independent of each other, and misconceptions are not represented: the model sees only whether an answer is correct, not why it is wrong. Instructional actions other than practice (hints, worked examples, explanations) have no place in the model.
- **Where in our project:** The basis of Simulator A (WBS 6.1–6.2) and of the policy-side BKT tracker in the observation (FR-34). We fitted per-skill L0, T, G, S for S1–S6 on ASSISTments 2009–2010 (24 Nov 2026).
- **Our contribution:** We use BKT as one of several student models rather than the only one, add a misconception layer on top of it (FR-15), and treat the effects of non-practice actions as explicit assumptions tested by ablation (K0–K3, H5).
- **Check while reading:** the exact form of the per-skill vs. global parameter comparison and the size of the improvement.

---

## [7] Badrinath, Wang & Pardos (2021) — pyBKT

Badrinath, A., Wang, F., & Pardos, Z. A. (2021). pyBKT: An accessible Python library of Bayesian Knowledge Tracing models. *Proceedings of the 14th International Conference on Educational Data Mining*, 468–474.

- **What it does:** A Python library that fits BKT and its variants, including skill-specific and format-specific guess and slip parameters (in our code: `multigs`), with built-in prediction and evaluation.
- **Limitation (from our use):** Fitting quality is not the same as simulator quality (see [4]); a good AUC does not show that a policy trained on the model will transfer. In practice, the pip build we got on macOS is the slow pure-Python version, and its built-in parallel mode was very slow there, so we parallelised over folds ourselves.
- **Where in our project:** WBS 6.1 (ASSISTments: L0, T and short-answer G/S; student-level 5-fold CV, AUC 0.66–0.74) and WBS 5.5 (Eedi NeurIPS: multiple-choice G/S, G ≈ 0.39–0.42, S ≈ 0.13–0.18). Format-specific G/S is exactly what the approved text asks for (short answer vs. multiple choice).
- **Our contribution:** We combine two data sources per skill (learning parameters from ASSISTments, multiple-choice G/S from Eedi), which neither data set allows alone.
- **Check while reading:** which variants the paper lists (forgetting, item difficulty, multiple priors), and which evaluation metrics it recommends.

---

## [8] Käser & Alexandron (2024) — Simulated learners review

Käser, T., & Alexandron, G. (2024). Simulated learners in educational technology: A systematic literature review and a Turing-like test. *International Journal of Artificial Intelligence in Education, 34*(2), 545–585. https://doi.org/10.1007/s40593-023-00337-2

- **What it does:** A systematic review of studies that use simulated learners in educational technology, plus a Turing-like test for judging how realistic a simulated learner is.
- **Limitation (of the field, as reported):** Many studies with simulated learners capture only narrow aspects of learning, and almost half provide no evidence that the simulator is valid.
- **Where in our project:** Motivates why we do not trust a single simulator, and why we report calibration checks (held-out AUC, parameter plausibility G, S < 0.5, T > 0) for Simulators A and B, and compare LLM option choices with real Eedi choices (FR-40).
- **Our contribution:** Instead of claiming one valid simulator, we measure how much a tutoring policy's advantage changes across three different student models, including an LLM-based one.
- **Check while reading:** how the Turing-like test works and whether it could be used for our LLM student (Simulator C).

---

## Optional: [4] Doroudi, Aleven & Brunskill (2017) — Robust Evaluation Matrix

Doroudi, S., Aleven, V., & Brunskill, E. (2017). Robust Evaluation Matrix: Towards a more principled offline exploration of instructional policies. *Proceedings of the Fourth ACM Conference on Learning @ Scale*, 3–12. https://doi.org/10.1145/3051457.3051463

- **What it does:** In a fractions tutor, adaptive policies derived from one student model were predicted to give a large gain, but showed no significant difference with more than 300 real students. Under other models with similar accuracy the ranking changed. The authors propose evaluating every policy under several plausible student models (REM).
- **Limitation:** REM is used to *diagnose* whether a policy will transfer, not to *train* policies that transfer better; its student models are cognitive or statistical only.
- **Where in our project:** The starting point of the project: our BKT × PFA × LLM cross matrix is an REM.
- **Our contribution:** We add an LLM-simulated student as a new row, measure the transfer gap of deep RL and bandit tutors (RQ2), and test whether domain randomization reduces it (RQ3). Our student types follow the authors' own suggestion to add models of different student populations.
