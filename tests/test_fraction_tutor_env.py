import dataclasses

import numpy as np
import pytest

from src.core.fraction_tutor_env import (
    FINISH_ACTION,
    MIN_STEPS_BEFORE_FINISH,
    NUM_ACTIONS,
    NUM_SKILLS,
    OBS_DIM,
    FractionTutorEnv,
    HiddenState,
)


class FakeStudentModel:
    """Deterministic stand-in for Simulator A/B/C used only in tests."""

    def __init__(self, always_correct: bool = True):
        self.always_correct = always_correct
        self._mastery = np.full(NUM_SKILLS, 0.4, dtype=np.float32)

    def reset(self, seed=None) -> HiddenState:
        return HiddenState(
            true_mastery=np.full(NUM_SKILLS, 0.9, dtype=np.float32),
            student_profile_id="student-secret-42",
            simulator_id="sim-A-bkt",
            misconception_assignment={0: 1},
        )

    def answer(self, skill: int, action_name: str):
        correct = self.always_correct
        return correct, None if correct else 1

    def estimated_mastery(self) -> np.ndarray:
        return self._mastery


def make_env(**kwargs) -> FractionTutorEnv:
    return FractionTutorEnv(student_model=FakeStudentModel(), **kwargs)


def test_action_space_is_37():
    env = make_env()
    assert env.action_space.n == NUM_ACTIONS == 37
    assert FINISH_ACTION == 36


def test_observation_space_is_143():
    env = make_env()
    assert env.observation_space.shape == (143,)
    assert OBS_DIM == 143


def test_reset_observation_matches_space():
    env = make_env()
    obs, info = env.reset(seed=0)
    assert obs.shape == (OBS_DIM,)
    assert env.observation_space.contains(obs)
    assert info == {}


def test_finish_action_masked_for_first_six_steps():
    env = make_env()
    env.reset(seed=0)
    for t in range(MIN_STEPS_BEFORE_FINISH):
        mask = env.action_masks()
        assert mask[FINISH_ACTION] is np.bool_(False) or mask[FINISH_ACTION] == False
        env.step(0)  # S1 easy_question, always available
    mask = env.action_masks()
    assert mask[FINISH_ACTION] == True


def test_finish_action_raises_while_masked():
    env = make_env()
    env.reset(seed=0)
    with pytest.raises(ValueError):
        env.step(FINISH_ACTION)


def test_finish_action_allowed_after_min_steps():
    env = make_env()
    env.reset(seed=0)
    for _ in range(MIN_STEPS_BEFORE_FINISH):
        env.step(0)
    obs, reward, terminated, truncated, info = env.step(FINISH_ACTION)
    assert terminated is True
    assert obs.shape == (OBS_DIM,)


def test_episode_truncates_at_max_steps():
    env = make_env(max_steps=10, min_steps_before_finish=100)
    env.reset(seed=0)
    terminated = truncated = False
    steps = 0
    while not (terminated or truncated):
        _, _, terminated, truncated, _ = env.step(0)
        steps += 1
    assert steps == 10
    assert truncated is True


# -- Hidden state must never reach the policy ---------------------------

def test_hidden_state_not_in_reset_observation_or_info():
    env = make_env()
    obs, info = env.reset(seed=0)
    assert info == {}
    hidden = env.hidden_state
    for leaked_value in (
        hidden.student_profile_id,
        hidden.simulator_id,
    ):
        assert leaked_value not in str(obs)
        assert leaked_value not in str(info)
    assert not np.any(np.isin(hidden.true_mastery, obs))


def test_hidden_state_not_in_step_observation_or_info():
    env = make_env()
    env.reset(seed=0)
    obs, reward, terminated, truncated, info = env.step(0)
    assert info == {}
    hidden = env.hidden_state
    assert hidden.student_profile_id not in str(obs)
    assert hidden.simulator_id not in str(obs)


def test_hidden_state_fields_disjoint_from_observable_mastery():
    """The observation must carry the *estimated* (BKT-tracker) mastery,
    never the ground-truth hidden mastery used to generate it."""
    env = make_env()
    env.reset(seed=0)
    obs, _ = env.reset(seed=0)
    hidden = env.hidden_state
    # FakeStudentModel deliberately sets true_mastery (0.9) != estimated_mastery (0.4)
    assert not np.allclose(hidden.true_mastery, env.student_model.estimated_mastery())
    block_b = obs[1 : 1 + NUM_SKILLS]
    assert np.allclose(block_b, env.student_model.estimated_mastery())
    assert not np.allclose(block_b, hidden.true_mastery)


def test_hidden_state_dataclass_fields_not_public_env_attributes():
    env = make_env()
    env.reset(seed=0)
    hidden_fields = {f.name for f in dataclasses.fields(HiddenState)}
    public_env_attrs = {name for name in vars(env) if not name.startswith("_")}
    assert hidden_fields.isdisjoint(public_env_attrs)
