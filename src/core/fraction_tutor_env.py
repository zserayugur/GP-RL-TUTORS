"""Gymnasium environment skeleton for the RL fraction tutor.

Implements the POMDP interface fixed in the approved TUBITAK text (Section 2.1)
and the 17 Kasim team decisions:

  - Action space:  Discrete(37)   -> 6 skills x 6 actions + 1 "finish session" action.
  - Observation:   Box(143,)      -> observable-only features (see _build_observation).
  - Episode length: H = 60 steps max (team decision, 18 Kasim).
  - "finish" action is masked for the first MIN_STEPS_BEFORE_FINISH steps.
  - Hidden state (true per-skill mastery, student profile, simulator identity) is
    tracked internally but is NEVER placed in the observation or the info dict
    returned to the agent. See `hidden_state` property and test_fraction_tutor_env.py.

This module is the environment *skeleton* (WBS 7.1). The student-model transition
(T) and misconception layer (Z) are injected via `StudentModel` so Simulators
A (BKT), B (AFM/PFA) and C (LLM student) can plug into the same env. The exact
143-dim feature layout is reserved/padded where it depends on Elifnaz's formal
RL definition (last-answer window N, misconception taxonomy size); those blocks
are clearly marked below and sized dynamically so OBS_DIM stays fixed at 143.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np
from gymnasium import Env, spaces

from .bkt_tracker import BKTParams, BKTTracker

NUM_SKILLS = 6
ACTIONS_PER_SKILL = 6
FINISH_ACTION = NUM_SKILLS * ACTIONS_PER_SKILL  # 36
NUM_ACTIONS = FINISH_ACTION + 1  # 37

MAX_STEPS_H = 60  # team decision, 18 Kasim
MIN_STEPS_BEFORE_FINISH = 6  # "finish" masked for the first 6 steps

OBS_DIM = 143
LAST_N_ANSWERS_DEFAULT = 3  # open question to hoca: 3 or 5
NUM_MISCONCEPTION_CLASSES = 3  # proposal: 3 main classes per skill (Eedi ~48% finding)

ACTION_NAMES = (
    "easy_question",
    "hard_question",
    "hint",
    "worked_example",
    "short_lecture",
    "misconception_feedback",
)

# "Ogretim eylemleri" (Karar Dokumani "Eylem sayaclari": ipucu, cozumlu ornek,
# anlatim, yanilgi geri bildirimi - NOT the two question actions, those are
# already reflected in the correct/incorrect-count blocks).
TEACHING_ACTION_NAMES = ("hint", "worked_example", "short_lecture", "misconception_feedback")
TEACHING_ACTION_INDICES = tuple(ACTION_NAMES.index(a) for a in TEACHING_ACTION_NAMES)

ACTION_COST = {
    "easy_question": 1.0,
    "hard_question": 1.0,
    "hint": 1.0,
    "worked_example": 1.5,
    "misconception_feedback": 1.5,
    "short_lecture": 2.0,
}

LAMBDA_COST = 0.003  # cost coefficient, rescaled for H=60 (team decision, 18 Kasim)

# Skill graph (Seray, Beceri_Grafigi_ve_UseCase_v2): S1=0 .. S6=5.
# S1 -> S2, S3, S6 ; S4 -> S5. S1 and S4 are root skills (no prerequisite).
SKILL_PREREQS: dict[int, tuple[int, ...]] = {
    1: (0,),  # S2 <- S1
    2: (0,),  # S3 <- S1
    5: (0,),  # S6 <- S1
    4: (3,),  # S5 <- S4
}
PREREQ_MASTERY_THRESHOLD = 0.6  # team proposal (Karar Dokumani Gozlem/Eylem/Odul); pending hoca confirmation


@dataclass
class HiddenState:
    """Privileged information. Must never reach the observation/info given to a policy."""

    true_mastery: np.ndarray  # shape (NUM_SKILLS,), ground-truth mastery per skill
    student_profile_id: str
    simulator_id: str
    misconception_assignment: dict[int, int] = field(default_factory=dict)  # skill -> class id


class StudentModel(Protocol):
    """Interface each simulator (A=BKT, B=AFM/PFA, C=LLM student) must implement."""

    def reset(self, seed: int | None = None) -> HiddenState: ...

    def answer(self, skill: int, action_name: str) -> tuple[bool, int | None]:
        """Returns (is_correct, misconception_class_or_None)."""
        ...


class FractionTutorEnv(Env):
    """RL environment for selecting the next tutoring action across 6 fraction skills."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        student_model: StudentModel,
        pretest_scores: np.ndarray | list[float] | float = 0.0,
        max_steps: int = MAX_STEPS_H,
        min_steps_before_finish: int = MIN_STEPS_BEFORE_FINISH,
        last_n_answers: int = LAST_N_ANSWERS_DEFAULT,
        num_misconception_classes: int = NUM_MISCONCEPTION_CLASSES,
        bkt_params: BKTParams | list[BKTParams] | None = None,
    ) -> None:
        super().__init__()
        self.student_model = student_model
        # Per-skill pre-test accuracy (Karar Dokumani: "Pre-test score", 6 dims).
        # A single float is broadcast to all 6 skills for convenience.
        if np.isscalar(pretest_scores):
            self.pretest_scores = np.full(NUM_SKILLS, float(pretest_scores), dtype=np.float32)
        else:
            self.pretest_scores = np.asarray(pretest_scores, dtype=np.float32)
            if self.pretest_scores.shape != (NUM_SKILLS,):
                raise ValueError(f"pretest_scores must have shape ({NUM_SKILLS},)")
        self.max_steps = max_steps
        self.min_steps_before_finish = min_steps_before_finish
        self.last_n_answers = last_n_answers
        self.num_misconception_classes = num_misconception_classes
        # Policy-side BKT tracker (FR-34): estimates mastery from observed
        # correctness only, identically regardless of which simulator (A/B/C)
        # is behind the env. Never reads simulator-internal state.
        self._bkt_tracker = BKTTracker(NUM_SKILLS, bkt_params)

        self.action_space = spaces.Discrete(NUM_ACTIONS)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(OBS_DIM,), dtype=np.float32
        )

        self._hidden: HiddenState | None = None
        self._step_count = 0
        self._correct_counts = np.zeros(NUM_SKILLS, dtype=np.float32)
        self._incorrect_counts = np.zeros(NUM_SKILLS, dtype=np.float32)
        self._streaks = np.zeros(NUM_SKILLS, dtype=np.float32)
        self._action_counts = np.zeros((NUM_SKILLS, ACTIONS_PER_SKILL), dtype=np.float32)
        self._steps_since_last_exercise = np.zeros(NUM_SKILLS, dtype=np.float32)
        self._current_misconception = np.full(NUM_SKILLS, -1, dtype=np.int32)
        # Per-skill sliding window of the last `last_n_answers` attempts on
        # that skill (True/False); used for the "last N answers" obs block.
        self._skill_answer_history: list[list[bool]] = [[] for _ in range(NUM_SKILLS)]
        self._post_test_score: float | None = None
        # Last action taken (TUBITAK Yontem 2.1: "genel duzeyde son eylem...
        # kullanilacaktir" - must be observable, not just used for masking).
        self._last_action_name: str | None = None  # one of ACTION_NAMES, or "finish"
        self._last_action_skill: int | None = None  # None for "finish" / no action yet

    # -- Gymnasium API --------------------------------------------------

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self._hidden = self.student_model.reset(seed=seed)
        self._bkt_tracker.reset()
        self._step_count = 0
        self._correct_counts[:] = 0
        self._incorrect_counts[:] = 0
        self._streaks[:] = 0
        self._action_counts[:] = 0
        self._steps_since_last_exercise[:] = 0
        self._current_misconception[:] = -1
        self._skill_answer_history = [[] for _ in range(NUM_SKILLS)]
        self._post_test_score = None
        self._last_action_name = None
        self._last_action_skill = None
        return self._build_observation(), {}

    def step(self, action: int):
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action {action!r} for Discrete({NUM_ACTIONS})")
        mask = self.action_masks()
        if not mask[action]:
            raise ValueError(f"Action {action} is masked at step {self._step_count}")

        self._step_count += 1
        terminated = False
        cost = 0.0

        if action == FINISH_ACTION:
            terminated = True
            self._last_action_name = "finish"
            self._last_action_skill = None
        else:
            skill, action_name = self._decode_action(action)
            cost = ACTION_COST[action_name]
            self._action_counts[skill, ACTION_NAMES.index(action_name)] += 1

            # "Steps since last exercise" ages for every skill each step, and
            # resets to 0 only for the skill actually exercised this step
            # (Karar Dokumani: "O beceri en son kac adim once calisildi").
            self._steps_since_last_exercise += 1

            is_exercise = action_name in ("easy_question", "hard_question")
            if is_exercise:
                is_correct, misconception = self.student_model.answer(skill, action_name)
                self._bkt_tracker.update(skill, is_correct)
                self._steps_since_last_exercise[skill] = 0
                if is_correct:
                    self._correct_counts[skill] += 1
                    self._streaks[skill] += 1
                    self._current_misconception[skill] = -1
                else:
                    self._incorrect_counts[skill] += 1
                    self._streaks[skill] = 0
                    self._current_misconception[skill] = misconception if misconception is not None else -1
                self._skill_answer_history[skill].append(is_correct)
                if len(self._skill_answer_history[skill]) > self.last_n_answers:
                    self._skill_answer_history[skill].pop(0)

            self._last_action_name = action_name
            self._last_action_skill = skill

        truncated = self._step_count >= self.max_steps
        if truncated and not terminated:
            terminated = True

        reward = 0.0
        if terminated:
            reward = self._terminal_reward() - cost * LAMBDA_COST
        else:
            reward = -cost * LAMBDA_COST

        return self._build_observation(), reward, terminated, truncated, {}

    def action_masks(self) -> np.ndarray:
        """Boolean validity mask of length NUM_ACTIONS, for sb3-contrib MaskablePPO.

        Masks only ever read observable information (the BKT tracker's estimated
        mastery, the last outstanding wrong answer, the last action taken) -
        never the hidden state. Source: Karar Dokumani (Gozlem/Eylem/Odul), 2.
        """
        mask = np.ones(NUM_ACTIONS, dtype=bool)
        mask[FINISH_ACTION] = self._step_count >= self.min_steps_before_finish

        estimated_mastery = self._bkt_tracker.estimate()
        misconception_feedback_idx = ACTION_NAMES.index("misconception_feedback")
        short_lecture_idx = ACTION_NAMES.index("short_lecture")

        for skill in range(NUM_SKILLS):
            base = skill * ACTIONS_PER_SKILL

            # Prerequisite mask: block the whole skill if any prerequisite's
            # BKT-tracker estimate is below threshold (0,6, team proposal).
            prereqs = SKILL_PREREQS.get(skill, ())
            if any(estimated_mastery[p] < PREREQ_MASTERY_THRESHOLD for p in prereqs):
                mask[base : base + ACTIONS_PER_SKILL] = False
                continue

            # Misconception feedback only valid with an outstanding wrong answer
            # tied to a known misconception for this skill.
            if self._current_misconception[skill] < 0:
                mask[base + misconception_feedback_idx] = False

        # No repeating short_lecture back-to-back on the same skill.
        if self._last_action_name == "short_lecture":
            mask[self._last_action_skill * ACTIONS_PER_SKILL + short_lecture_idx] = False

        # TODO: mask an action once its item-bank pool is exhausted for a
        # skill/difficulty (needs WBS 5.2 item bank; not available yet).
        return mask

    # -- Hidden state: deliberately NOT exposed via reset()/step() ------

    @property
    def hidden_state(self) -> HiddenState:
        """For internal evaluation / researcher replay (UC-07) only.

        Never read this from policy code. It is intentionally absent from the
        observation and info dict returned by reset()/step().
        """
        assert self._hidden is not None, "call reset() first"
        return self._hidden

    # -- Observation construction ----------------------------------------

    def _build_observation(self) -> np.ndarray:
        """Block layout follows Karar Dokumani (Gozlem/Eylem/Odul), which the
        18 Kasim team decision kept as the structural reference (only the
        *total* dim count and the finish-mask step defer to Elifnaz's formal
        definition): every per-skill quantity is reported per skill (6 dims),
        not collapsed into a single global scalar.
        """
        blocks: list[np.ndarray] = []

        blocks.append(self.pretest_scores.astype(np.float32))  # 6, per skill

        blocks.append(self._bkt_tracker.estimate().astype(np.float32))  # 6 (FR-34: policy-side BKT tracker, not ground truth)

        denom = max(self._step_count, 1)
        blocks.append((self._correct_counts / denom).astype(np.float32))  # 6
        blocks.append((self._incorrect_counts / denom).astype(np.float32))  # 6
        blocks.append((self._streaks / denom).astype(np.float32))  # 6

        blocks.append(self._encode_last_n_answers().astype(np.float32))  # NUM_SKILLS * last_n_answers = 18

        # "Ogretim eylemi" sayaclari: yalnizca 4 ogretim eylemi (ipucu, cozumlu
        # ornek, anlatim, yanilgi geri bildirimi), soru eylemleri degil (onlar
        # zaten correct/incorrect bloklarinda yansitiliyor). 6 * 4 = 24.
        blocks.append(
            (self._action_counts[:, TEACHING_ACTION_INDICES].flatten() / denom).astype(np.float32)
        )

        blocks.append((self._steps_since_last_exercise / self.max_steps).astype(np.float32))  # 6, per skill
        blocks.append(np.array([self._step_count / self.max_steps], dtype=np.float32))  # 1
        blocks.append(np.array([(self.max_steps - self._step_count) / self.max_steps], dtype=np.float32))  # 1

        blocks.append(self._encode_current_misconceptions().astype(np.float32))  # NUM_SKILLS * (num_misconception_classes+1) = 24

        # "Son eylem" (TUBITAK Yontem 2.1; Karar Dokumani "Genel alanlar": son
        # eylem turu (7) + son beceri (6)). Previously tracked only for masking
        # (short_lecture repeat check) and never exposed - gap found by Seray.
        blocks.append(self._encode_last_action().astype(np.float32))  # 7 + 6 = 13

        obs = np.concatenate(blocks)

        reserved = OBS_DIM - obs.shape[0]
        if reserved < 0:
            raise ValueError(
                f"Observation blocks ({obs.shape[0]}) exceed OBS_DIM ({OBS_DIM}); "
                "adjust last_n_answers/num_misconception_classes or OBS_DIM."
            )
        if reserved:
            # Reserved for dims pending Elifnaz's formal RL definition doc
            # (final 143-dim layout: 117 from Karar Dokumani + whatever she
            # adds). Replace this padding once that spec lands.
            obs = np.concatenate([obs, np.zeros(reserved, dtype=np.float32)])

        return obs

    def _encode_last_action(self) -> np.ndarray:
        """7 dims: one-hot over (6 action types + 'finish'), all-zero if no
        action taken yet. 6 dims: one-hot of the skill it targeted, all-zero
        for 'finish' or no action yet."""
        action_type_dim = len(ACTION_NAMES) + 1  # 6 + "finish"
        out = np.zeros(action_type_dim + NUM_SKILLS, dtype=np.float32)
        if self._last_action_name == "finish":
            out[action_type_dim - 1] = 1.0
        elif self._last_action_name is not None:
            out[ACTION_NAMES.index(self._last_action_name)] = 1.0
            out[action_type_dim + self._last_action_skill] = 1.0
        return out

    def _encode_last_n_answers(self) -> np.ndarray:
        """Per-skill scalar history (Karar Dokumani: "Her biri: dogru = 1,
        yanlis = 0, cevap yok = 0,5"), most recent attempt first. Misconception
        info is not repeated here - it lives in _encode_current_misconceptions."""
        out = np.full((NUM_SKILLS, self.last_n_answers), 0.5, dtype=np.float32)
        for skill in range(NUM_SKILLS):
            history = self._skill_answer_history[skill]
            recent = list(reversed(history[-self.last_n_answers :]))
            for i, correct in enumerate(recent):
                out[skill, i] = 1.0 if correct else 0.0
        return out.flatten()

    def _encode_current_misconceptions(self) -> np.ndarray:
        slot_dim = self.num_misconception_classes + 1  # +1 for "none"
        out = np.zeros(NUM_SKILLS * slot_dim, dtype=np.float32)
        for skill in range(NUM_SKILLS):
            cls = self._current_misconception[skill]
            offset = skill * slot_dim
            if cls < 0:
                out[offset + self.num_misconception_classes] = 1.0
            else:
                out[offset + cls] = 1.0
        return out

    # -- Helpers ------------------------------------------------------

    @staticmethod
    def _decode_action(action: int) -> tuple[int, str]:
        skill, action_idx = divmod(action, ACTIONS_PER_SKILL)
        return skill, ACTION_NAMES[action_idx]

    def _terminal_reward(self) -> float:
        # Main reward: g_norm = (post - pre) / (1 - pre), evaluated from the
        # student model's (expected, during training, or sampled, during eval)
        # pre/post test score. Sampled short-answer post-test wiring belongs to
        # the simulator / evaluation harness, not this env skeleton. pre/post
        # are scalar averages over skills (onayli metin Yontem 2.1: E(s) =
        # (1/K) * sum_k P(dogru | gizli durum, beceri k)), separate from the
        # per-skill pretest_scores block in the observation.
        pre = float(self.pretest_scores.mean())
        post = self._post_test_score if self._post_test_score is not None else pre
        if pre >= 1.0:
            return 0.0
        return (post - pre) / (1.0 - pre)
