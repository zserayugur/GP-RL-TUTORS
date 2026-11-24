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

ACTION_COST = {
    "easy_question": 1.0,
    "hard_question": 1.0,
    "hint": 1.0,
    "worked_example": 1.5,
    "misconception_feedback": 1.5,
    "short_lecture": 2.0,
}

LAMBDA_COST = 0.003  # cost coefficient, rescaled for H=60 (team decision, 18 Kasim)


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

    def estimated_mastery(self) -> np.ndarray:
        """BKT/PFA tracker's *estimated* mastery per skill (observable, not ground truth)."""
        ...


class FractionTutorEnv(Env):
    """RL environment for selecting the next tutoring action across 6 fraction skills."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        student_model: StudentModel,
        pretest_score: float = 0.0,
        max_steps: int = MAX_STEPS_H,
        min_steps_before_finish: int = MIN_STEPS_BEFORE_FINISH,
        last_n_answers: int = LAST_N_ANSWERS_DEFAULT,
        num_misconception_classes: int = NUM_MISCONCEPTION_CLASSES,
    ) -> None:
        super().__init__()
        self.student_model = student_model
        self.pretest_score = pretest_score
        self.max_steps = max_steps
        self.min_steps_before_finish = min_steps_before_finish
        self.last_n_answers = last_n_answers
        self.num_misconception_classes = num_misconception_classes

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
        self._steps_since_last_exercise = 0
        self._current_misconception = np.full(NUM_SKILLS, -1, dtype=np.int32)
        # ring buffer of (skill, correct, misconception_class_or_-1)
        self._answer_history: list[tuple[int, bool, int]] = []
        self._post_test_score: float | None = None

    # -- Gymnasium API --------------------------------------------------

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self._hidden = self.student_model.reset(seed=seed)
        self._step_count = 0
        self._correct_counts[:] = 0
        self._incorrect_counts[:] = 0
        self._streaks[:] = 0
        self._action_counts[:] = 0
        self._steps_since_last_exercise = 0
        self._current_misconception[:] = -1
        self._answer_history.clear()
        self._post_test_score = None
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
        else:
            skill, action_name = self._decode_action(action)
            cost = ACTION_COST[action_name]
            self._action_counts[skill, ACTION_NAMES.index(action_name)] += 1

            is_exercise = action_name in ("easy_question", "hard_question")
            if is_exercise:
                is_correct, misconception = self.student_model.answer(skill, action_name)
                self._steps_since_last_exercise = 0
                if is_correct:
                    self._correct_counts[skill] += 1
                    self._streaks[skill] += 1
                    self._current_misconception[skill] = -1
                else:
                    self._incorrect_counts[skill] += 1
                    self._streaks[skill] = 0
                    self._current_misconception[skill] = misconception if misconception is not None else -1
                self._record_answer(skill, is_correct, self._current_misconception[skill])
            else:
                self._steps_since_last_exercise += 1

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
        """Boolean validity mask of length NUM_ACTIONS, for sb3-contrib MaskablePPO."""
        mask = np.ones(NUM_ACTIONS, dtype=bool)
        mask[FINISH_ACTION] = self._step_count >= self.min_steps_before_finish
        # TODO (domain masks, pending content/BKT-tracker wiring):
        #  - mask a skill's actions when its prerequisite skill is not yet mastered
        #  - mask misconception_feedback when there is no outstanding wrong answer
        #  - mask short_lecture repeated back-to-back for the same skill
        #  - mask redundant repetition of an already-mastered skill
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
        blocks: list[np.ndarray] = []

        blocks.append(np.array([self.pretest_score], dtype=np.float32))  # 1
        blocks.append(self.student_model.estimated_mastery().astype(np.float32))  # 6 (observable BKT estimate, not ground truth)

        denom = max(self._step_count, 1)
        blocks.append((self._correct_counts / denom).astype(np.float32))  # 6
        blocks.append((self._incorrect_counts / denom).astype(np.float32))  # 6
        blocks.append((self._streaks / denom).astype(np.float32))  # 6

        blocks.append(self._encode_last_n_answers().astype(np.float32))  # last_n_answers * (6+1+num_misconception_classes)

        blocks.append((self._action_counts.flatten() / denom).astype(np.float32))  # 36

        blocks.append(np.array([self._steps_since_last_exercise / self.max_steps], dtype=np.float32))  # 1
        blocks.append(np.array([self._step_count / self.max_steps], dtype=np.float32))  # 1
        blocks.append(np.array([(self.max_steps - self._step_count) / self.max_steps], dtype=np.float32))  # 1

        blocks.append(self._encode_current_misconceptions().astype(np.float32))  # NUM_SKILLS * (num_misconception_classes+1)

        obs = np.concatenate(blocks)

        reserved = OBS_DIM - obs.shape[0]
        if reserved < 0:
            raise ValueError(
                f"Observation blocks ({obs.shape[0]}) exceed OBS_DIM ({OBS_DIM}); "
                "adjust last_n_answers/num_misconception_classes or OBS_DIM."
            )
        if reserved:
            # Reserved for dims pending Elifnaz's formal RL definition doc
            # (final 143-dim layout). Replace this padding once that spec lands.
            obs = np.concatenate([obs, np.zeros(reserved, dtype=np.float32)])

        return obs

    def _encode_last_n_answers(self) -> np.ndarray:
        slot_dim = NUM_SKILLS + 1 + self.num_misconception_classes
        out = np.zeros(self.last_n_answers * slot_dim, dtype=np.float32)
        recent = self._answer_history[-self.last_n_answers :]
        for i, (skill, correct, misconception) in enumerate(recent):
            offset = i * slot_dim
            out[offset + skill] = 1.0
            out[offset + NUM_SKILLS] = 1.0 if correct else 0.0
            if not correct and 0 <= misconception < self.num_misconception_classes:
                out[offset + NUM_SKILLS + 1 + misconception] = 1.0
        return out

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

    def _record_answer(self, skill: int, correct: bool, misconception: int) -> None:
        self._answer_history.append((skill, correct, int(misconception)))

    def _terminal_reward(self) -> float:
        # Main reward: g_norm = (post - pre) / (1 - pre), evaluated from the
        # student model's (expected, during training, or sampled, during eval)
        # pre/post test score. Sampled short-answer post-test wiring belongs to
        # the simulator / evaluation harness, not this env skeleton.
        pre = self.pretest_score
        post = self._post_test_score if self._post_test_score is not None else pre
        if pre >= 1.0:
            return 0.0
        return (post - pre) / (1.0 - pre)
