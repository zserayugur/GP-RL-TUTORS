"""Simulator A: BKT student simulator (WBS 6.2, FR-13).

Implements the `StudentModel` interface of `fraction_tutor_env.py`
(`reset()` and `answer()`), plus two extra hooks the environment will need:

  - `teach(skill, action_name)`: effect of the non-exercise actions
    (hint, worked example, short lecture, misconception feedback).
  - `expected_test_score()`: expected short-answer test score computed from the
    hidden state (privileged information, FR-22: expected gain reward). It does
    not change the hidden state, so test items cause no learning (FR-17).

Parameters come from the pyBKT fit on ASSISTments 2009-2010 (WBS 6.1,
24 Nov 2026; see log/worklog/seray.md). Raw data is not in this repo.

What is an assumption and still to be decided (marked "ASSUMPTION" below):
  - Student types (profiles): 5 types as multipliers on the fitted parameters.
    The number of types is not fixed in the approved text; the handoff/WBS say 5,
    FR list v4 says 4. Easy to change in `PROFILES`.
  - Effects of actions that are not in the data (hint, worked example, lecture,
    feedback) are hypothetical: an extra learning probability equal to
    `multiplier * T`, with multiplier in [0.5, 2] (WBS 6.4, K0-K3 ablation).
  - Hard vs easy question: BKT has no difficulty, so a hard question halves G
    and raises S by 1.5x.
  - Exercises (multiple choice) use Eedi NeurIPS G/S (WBS 5.5); tests (short
    answer) use ASSISTments G/S. L0 and T come from ASSISTments only.
  - No misconception layer yet (FR-15, planned for semester 2): `answer()`
    returns None as the misconception, so the env keeps feedback masked.
  - Skills learn independently (standard BKT); prerequisites only act through
    the env's action mask.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .bkt_tracker import BKTParams
from .fraction_tutor_env import ACTION_NAMES, NUM_SKILLS, HiddenState

SIMULATOR_ID = "A-BKT"

# --- WBS 6.1 results (pyBKT 1.4.3, seed 42, 5 restarts, forgets off) ---------
# Short-answer ("sa") G/S. Order: S1..S6.
ASSISTMENTS_BKT_PARAMS: tuple[BKTParams, ...] = (
    BKTParams(l0=0.627, t=0.093, g=0.081, s=0.293),  # S1 Equivalent Fractions
    BKTParams(l0=0.633, t=0.066, g=0.489, s=0.045),  # S2 Ordering Fractions
    BKTParams(l0=0.752, t=0.089, g=0.110, s=0.198),  # S3 Addition and Subtraction
    BKTParams(l0=0.578, t=0.134, g=0.305, s=0.214),  # S4 Multiplication
    BKTParams(l0=0.708, t=0.190, g=0.107, s=0.195),  # S5 Division
    BKTParams(l0=0.608, t=0.015, g=0.424, s=0.202),  # S6 Fraction-Decimal-Percent
)

# Multiple-choice G/S per skill: (g, s), used for exercise items (teaching is
# multiple choice). From Eedi NeurIPS 2020 task 1-2 (WBS 5.5, 24 Nov 2026;
# src/data_prep/eedi_neurips_guess_slip.py, pyBKT on <= 60k answers per skill).
# The ASSISTments S2 mc fit (g=0.522) is not used: G > 0.5 fails the sanity check.
MC_GUESS_SLIP: tuple[tuple[float, float] | None, ...] = (
    (0.401, 0.146),  # S1
    (0.394, 0.175),  # S2
    (0.386, 0.141),  # S3
    (0.386, 0.135),  # S4
    (0.389, 0.157),  # S5
    (0.421, 0.132),  # S6
)


# --- Student types (ASSUMPTION, proposal) -------------------------------------
@dataclass(frozen=True)
class Profile:
    name: str
    l0: float = 1.0  # multiplier on L0
    t: float = 1.0  # multiplier on T
    g: float = 1.0  # multiplier on G
    s: float = 1.0  # multiplier on S


PROFILES: dict[str, Profile] = {
    "average": Profile("average"),  # fitted values as they are
    "fast_learner": Profile("fast_learner", t=2.0),
    "slow_learner": Profile("slow_learner", t=0.5),
    "low_prior": Profile("low_prior", l0=0.5),  # weaker starting knowledge
    "guesser": Profile("guesser", g=1.5, s=1.5),  # noisy, guess-prone answers
}

# --- Action effects (ASSUMPTION, WBS 6.4) -------------------------------------
# Extra learning probability = multiplier * T. 1.0 is the centre of [0.5, 2].
DEFAULT_ACTION_EFFECTS: dict[str, float] = {
    "hint": 1.0,
    "worked_example": 1.0,
    "short_lecture": 1.0,
    "misconception_feedback": 0.0,  # no misconception layer yet
}

HARD_GUESS_FACTOR = 0.5  # ASSUMPTION
HARD_SLIP_FACTOR = 1.5  # ASSUMPTION

_MAX_GS = 0.5  # keep G and S in the plausible range (G, S < 0.5)


def _clip(x: float, lo: float, hi: float) -> float:
    return float(min(max(x, lo), hi))


def apply_profile(p: BKTParams, prof: Profile) -> BKTParams:
    return BKTParams(
        l0=_clip(p.l0 * prof.l0, 0.0, 1.0),
        t=_clip(p.t * prof.t, 0.0, 1.0),
        g=_clip(p.g * prof.g, 0.001, _MAX_GS),
        s=_clip(p.s * prof.s, 0.001, _MAX_GS),
    )


class SimulatorA:
    """BKT student: one hidden binary state (learned / not learned) per skill."""

    def __init__(
        self,
        params: tuple[BKTParams, ...] | list[BKTParams] = ASSISTMENTS_BKT_PARAMS,
        mc_guess_slip: tuple[tuple[float, float] | None, ...] = MC_GUESS_SLIP,
        profiles: dict[str, Profile] | None = None,
        profile: str | None = None,
        action_effects: dict[str, float] | None = None,
    ) -> None:
        if len(params) != NUM_SKILLS or len(mc_guess_slip) != NUM_SKILLS:
            raise ValueError("need one parameter set per skill")
        self.base_params = tuple(params)
        self.mc_guess_slip = tuple(mc_guess_slip)
        self.profiles = dict(profiles or PROFILES)
        if profile is not None and profile not in self.profiles:
            raise ValueError(f"unknown profile {profile!r}")
        self.fixed_profile = profile  # None -> sample a profile at every reset
        self.action_effects = dict(DEFAULT_ACTION_EFFECTS)
        if action_effects:
            unknown = set(action_effects) - set(DEFAULT_ACTION_EFFECTS)
            if unknown:
                raise ValueError(f"unknown actions: {sorted(unknown)}")
            self.action_effects.update(action_effects)

        self._rng = np.random.default_rng()
        self._params: tuple[BKTParams, ...] = self.base_params
        self._learned = np.zeros(NUM_SKILLS, dtype=np.float32)  # 1.0 = learned; shared with HiddenState
        self._profile_name = "average"

    # -- StudentModel interface ----------------------------------------------

    def reset(self, seed: int | None = None) -> HiddenState:
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self._profile_name = self.fixed_profile or str(self._rng.choice(sorted(self.profiles)))
        prof = self.profiles[self._profile_name]
        self._params = tuple(apply_profile(p, prof) for p in self.base_params)
        self._learned = np.array([self._rng.random() < p.l0 for p in self._params], dtype=np.float32)
        return self._hidden()

    def answer(self, skill: int, action_name: str) -> tuple[bool, int | None]:
        """Exercise item (easy or hard question). Answer, then the BKT transition."""
        if action_name not in ("easy_question", "hard_question"):
            raise ValueError(f"answer() is only for exercise actions, got {action_name!r}")
        g, s = self._exercise_guess_slip(skill)
        if action_name == "hard_question":
            g, s = g * HARD_GUESS_FACTOR, min(s * HARD_SLIP_FACTOR, _MAX_GS)
        p_correct = (1.0 - s) if self._learned[skill] >= 1.0 else g
        correct = bool(self._rng.random() < p_correct)
        self._learn(skill, self._params[skill].t)
        return correct, None  # no misconception layer yet (FR-15)

    # -- Extra hooks the env needs -----------------------------------------------

    def teach(self, skill: int, action_name: str) -> None:
        """Non-exercise action: extra learning chance = multiplier * T (WBS 6.4)."""
        if action_name not in self.action_effects:
            raise ValueError(f"teach() is not defined for {action_name!r}")
        self._learn(skill, self.action_effects[action_name] * self._params[skill].t)

    def expected_test_score(self, skills: list[int] | None = None) -> float:
        """Expected share of correct short-answer test items (privileged, FR-22).

        P(correct) = P(L)(1 - S) + (1 - P(L)) G, with P(L) the hidden state (0/1).
        Does not change the state: test items cause no learning (FR-17).
        """
        idx = range(NUM_SKILLS) if skills is None else skills
        vals = [(1.0 - self._params[k].s) if self._learned[k] >= 1.0 else self._params[k].g for k in idx]
        return float(np.mean(vals))

    def sampled_test_score(self, items_per_skill: int = 2, skills: list[int] | None = None) -> float:
        """Sampled short-answer test (evaluation). No learning (FR-17)."""
        idx = list(range(NUM_SKILLS)) if skills is None else list(skills)
        n_correct = 0
        for k in idx:
            p = self._params[k]
            pc = (1.0 - p.s) if self._learned[k] >= 1.0 else p.g
            n_correct += int((self._rng.random(items_per_skill) < pc).sum())
        return n_correct / (items_per_skill * len(idx))

    # -- internals --------------------------------------------------------------

    def _exercise_guess_slip(self, skill: int) -> tuple[float, float]:
        mc = self.mc_guess_slip[skill]
        if mc is None:
            p = self._params[skill]
            return p.g, p.s
        prof = self.profiles[self._profile_name]
        return _clip(mc[0] * prof.g, 0.001, _MAX_GS), _clip(mc[1] * prof.s, 0.001, _MAX_GS)

    def _learn(self, skill: int, p_learn: float) -> None:
        if self._learned[skill] < 1.0 and self._rng.random() < min(max(p_learn, 0.0), 1.0):
            self._learned[skill] = 1.0

    def _hidden(self) -> HiddenState:
        return HiddenState(
            true_mastery=self._learned,  # same array: stays current for replay (UC-07)
            student_profile_id=self._profile_name,
            simulator_id=SIMULATOR_ID,
            misconception_assignment={},
        )


assert set(DEFAULT_ACTION_EFFECTS) | {"easy_question", "hard_question"} == set(ACTION_NAMES)
