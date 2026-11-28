import dataclasses

import numpy as np
import pytest

from src.core.fraction_tutor_env import (
    ACTION_NAMES,
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


def make_env(**kwargs) -> FractionTutorEnv:
    return FractionTutorEnv(student_model=FakeStudentModel(), **kwargs)


def set_tracker_belief(env: FractionTutorEnv, skill: int, value: float) -> None:
    """Test-only helper: force the policy-side BKT tracker's belief for a skill
    (white-box setup, since the tracker only updates from observed answers)."""
    env._bkt_tracker._belief[skill] = value


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
    """The observation must carry the *tracker-estimated* mastery (FR-34),
    never the ground-truth hidden mastery used by the simulator."""
    env = make_env()
    obs, _ = env.reset(seed=0)
    hidden = env.hidden_state
    tracker_estimate = env._bkt_tracker.estimate()
    # HiddenState.true_mastery (0.9) differs from the tracker's prior (L0=0.3)
    assert not np.allclose(hidden.true_mastery, tracker_estimate)
    block_b = obs[NUM_SKILLS : 2 * NUM_SKILLS]  # after the 6-dim per-skill pretest block
    assert np.allclose(block_b, tracker_estimate)
    assert not np.allclose(block_b, hidden.true_mastery)


def test_hidden_state_dataclass_fields_not_public_env_attributes():
    env = make_env()
    env.reset(seed=0)
    hidden_fields = {f.name for f in dataclasses.fields(HiddenState)}
    public_env_attrs = {name for name in vars(env) if not name.startswith("_")}
    assert hidden_fields.isdisjoint(public_env_attrs)


# -- Policy-side BKT tracker (FR-34) -------------------------------------

def test_bkt_tracker_updates_from_observed_answers_only():
    """The tracker must move on correct/incorrect answers alone - it never
    reads the simulator's hidden state, so it works identically for Simulator
    C (LLM), which has no internal P(L)."""
    env = make_env()
    env.reset(seed=0)
    before = env._bkt_tracker.estimate()[0]
    env.step(0)  # S1 easy_question, FakeStudentModel always answers correctly
    after = env._bkt_tracker.estimate()[0]
    assert after > before  # belief increases after an observed correct answer


# -- Domain masks (Karar Dokumani: Gozlem/Eylem/Odul) --------------------

def test_prerequisite_mask_blocks_dependent_skill_below_threshold():
    env = make_env()
    env.reset(seed=0)
    set_tracker_belief(env, 0, 0.4)  # S1 below 0.6 threshold
    mask = env.action_masks()
    # S2 (skill index 1) depends on S1 -> fully masked
    assert not mask[1 * 6 : 1 * 6 + 6].any()
    # S1 itself (no prerequisite) stays available
    assert mask[0 * 6 : 0 * 6 + 6].any()


def test_prerequisite_mask_opens_dependent_skill_once_threshold_met():
    env = make_env()
    env.reset(seed=0)
    set_tracker_belief(env, 0, 0.7)  # S1 above 0.6 threshold
    mask = env.action_masks()
    # S2 open except misconception_feedback (no outstanding wrong answer yet)
    assert mask[1 * 6 : 1 * 6 + 5].all()
    assert mask[1 * 6 + 5] == False


def test_misconception_feedback_masked_without_outstanding_wrong_answer():
    env = make_env()
    env.reset(seed=0)
    set_tracker_belief(env, 0, 0.9)
    mask = env.action_masks()
    misconception_feedback_action = 0 * 6 + 5  # skill 0, misconception_feedback
    assert mask[misconception_feedback_action] == False


def test_misconception_feedback_opens_after_wrong_answer():
    env = FractionTutorEnv(student_model=FakeStudentModel(always_correct=False))
    env.reset(seed=0)
    set_tracker_belief(env, 0, 0.9)
    env.step(0)  # S1 easy_question -> wrong answer, misconception recorded
    mask = env.action_masks()
    misconception_feedback_action = 0 * 6 + 5
    assert mask[misconception_feedback_action] == True


# -- "Son eylem" must be in the observation, not just used for masking ---
# (gap found by Seray while checking against the approved TUBITAK text,
# Yontem 2.1: "genel duzeyde son eylem... kullanilacaktir").

# Offset of the 13-dim last-action block inside the 143-dim observation
# (Karar Dokumani block layout, 25 Kasim fix): 6 (pretest) + 6 (bkt) +
# 6 (correct) + 6 (incorrect) + 6 (streaks) + 18 (last-N-answers, per skill)
# + 24 (teaching-action counts) + 6 (steps-since-last-exercise, per skill)
# + 1 + 1 (step counters) + 24 (current misconceptions) = 104
LAST_ACTION_OFFSET = 104
LAST_ACTION_TYPE_DIM = len(ACTION_NAMES) + 1  # 7


def test_last_action_block_is_zero_before_any_action():
    env = make_env()
    obs, _ = env.reset(seed=0)
    block = obs[LAST_ACTION_OFFSET : LAST_ACTION_OFFSET + LAST_ACTION_TYPE_DIM + NUM_SKILLS]
    assert not block.any()


def test_last_action_block_reflects_last_educational_action():
    env = make_env()
    env.reset(seed=0)
    obs, *_ = env.step(0)  # S1 (skill 0), easy_question (index 0)
    block = obs[LAST_ACTION_OFFSET : LAST_ACTION_OFFSET + LAST_ACTION_TYPE_DIM + NUM_SKILLS]
    assert block[ACTION_NAMES.index("easy_question")] == 1.0
    assert block[LAST_ACTION_TYPE_DIM + 0] == 1.0  # skill 0
    assert block.sum() == 2.0  # exactly one action-type bit + one skill bit


def test_last_action_block_reflects_finish():
    env = make_env()
    env.reset(seed=0)
    for _ in range(MIN_STEPS_BEFORE_FINISH):
        env.step(0)
    obs, *_ = env.step(FINISH_ACTION)
    block = obs[LAST_ACTION_OFFSET : LAST_ACTION_OFFSET + LAST_ACTION_TYPE_DIM + NUM_SKILLS]
    assert block[LAST_ACTION_TYPE_DIM - 1] == 1.0  # "finish" slot
    assert block[LAST_ACTION_TYPE_DIM:].sum() == 0.0  # no skill bit for finish


def test_short_lecture_cannot_repeat_back_to_back():
    env = make_env()
    env.reset(seed=0)
    set_tracker_belief(env, 0, 0.9)
    short_lecture_action = 0 * 6 + 4  # skill 0, short_lecture
    env.step(short_lecture_action)
    mask = env.action_masks()
    assert mask[short_lecture_action] == False
    # a different action on the same skill is still fine
    assert mask[0 * 6 + 0] == True


# -- Block layout must follow Karar Dokumani (per-skill, not global) -----
# (25 Kasim fix: pre-test, last-N-answers, teaching-action counts and
# steps-since-last-exercise were wrongly collapsed to global scalars.)


def test_pretest_scores_are_reported_per_skill():
    pretest = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6], dtype=np.float32)
    env = FractionTutorEnv(student_model=FakeStudentModel(), pretest_scores=pretest)
    obs, _ = env.reset(seed=0)
    assert np.allclose(obs[:NUM_SKILLS], pretest)


def test_last_n_answers_is_per_skill_scalar_not_global_list():
    env = make_env()
    env.reset(seed=0)
    offset = 5 * NUM_SKILLS  # after pretest(6)+bkt(6)+correct(6)+incorrect(6)+streaks(6)
    last_n = env.last_n_answers
    env.step(0)  # S1 (skill 0) easy_question, FakeStudentModel always correct
    obs, *_ = env.step(6)  # S2 (skill 1) easy_question
    block = obs[offset : offset + NUM_SKILLS * last_n]
    skill0_slots = block[0 * last_n : 0 * last_n + last_n]
    skill1_slots = block[1 * last_n : 1 * last_n + last_n]
    skill2_slots = block[2 * last_n : 2 * last_n + last_n]
    assert skill0_slots[0] == 1.0  # S1's one attempt, correct
    assert skill1_slots[0] == 1.0  # S2's one attempt, correct
    assert np.all(skill2_slots == 0.5)  # S3 never attempted -> "cevap yok"


def test_teaching_action_counts_exclude_questions():
    env = make_env()
    env.reset(seed=0)
    offset = 5 * NUM_SKILLS + NUM_SKILLS * env.last_n_answers  # pretest..streaks (5*6) + last-N
    env.step(0)  # S1 easy_question - must NOT bump the teaching-action block
    obs, *_ = env.step(2)  # S1 hint - must bump it
    block = obs[offset : offset + NUM_SKILLS * 4]
    skill0_counts = block[0:4]  # order: hint, worked_example, short_lecture, misconception_feedback
    assert skill0_counts[0] > 0  # hint was used
    assert skill0_counts.sum() == pytest.approx(skill0_counts[0])  # only hint, nothing else


def test_steps_since_last_exercise_is_per_skill():
    env = make_env()
    env.reset(seed=0)
    pretest_bkt_counts_streaks_lastn = 5 * NUM_SKILLS + NUM_SKILLS * env.last_n_answers
    teaching_block = NUM_SKILLS * 4
    offset = pretest_bkt_counts_streaks_lastn + teaching_block
    env.step(0)  # S1 (skill 0) easy_question -> resets skill 0's counter to 0
    obs, *_ = env.step(8)  # S2 (skill 1) hint -> skill 1 not exercised, both counters age by 1 more step
    block = obs[offset : offset + NUM_SKILLS]
    assert block[0] == pytest.approx(1 / env.max_steps)  # one step since S1 was exercised
    assert block[1] == pytest.approx(2 / env.max_steps)  # S2 never exercised, aged 2 steps

