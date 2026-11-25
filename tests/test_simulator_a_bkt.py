import numpy as np
import pytest

from src.core.fraction_tutor_env import ACTION_NAMES, FINISH_ACTION, NUM_SKILLS, FractionTutorEnv
from src.core.simulator_a_bkt import (
    ASSISTMENTS_BKT_PARAMS,
    PROFILES,
    SIMULATOR_ID,
    SimulatorA,
    make_env,
)


def test_fitted_params_are_plausible():
    # WBS 6.1 sanity check: G, S < 0.5 and T > 0
    for p in ASSISTMENTS_BKT_PARAMS:
        assert 0 < p.t <= 1 and 0 <= p.l0 <= 1
        assert p.g < 0.5 and p.s < 0.5


def test_reset_is_reproducible_with_seed():
    a, b = SimulatorA(), SimulatorA()
    ha, hb = a.reset(seed=7), b.reset(seed=7)
    assert ha.student_profile_id == hb.student_profile_id
    assert np.array_equal(ha.true_mastery, hb.true_mastery)
    assert [a.answer(0, "easy_question") for _ in range(20)] == [b.answer(0, "easy_question") for _ in range(20)]


def test_hidden_state_fields():
    h = SimulatorA(profile="average").reset(seed=1)
    assert h.simulator_id == SIMULATOR_ID
    assert h.student_profile_id == "average"
    assert h.true_mastery.shape == (NUM_SKILLS,)
    assert set(np.unique(h.true_mastery)) <= {0.0, 1.0}


def test_all_profiles_sampled():
    sim = SimulatorA()
    seen = {sim.reset(seed=s).student_profile_id for s in range(200)}
    assert seen == set(PROFILES)


def test_unknown_profile_rejected():
    with pytest.raises(ValueError):
        SimulatorA(profile="nope")


def test_answer_rate_matches_bkt_for_unlearned_student():
    # never learns (T=0) -> P(correct) = G; short-answer G when no mc table is given
    sim = SimulatorA(profile="average", mc_guess_slip=(None,) * NUM_SKILLS)
    sim.reset(seed=3)
    sim._learned[:] = 0.0
    sim._params = tuple(p.__class__(l0=p.l0, t=0.0, g=p.g, s=p.s) for p in sim._params)
    n = 4000
    rate = np.mean([sim.answer(0, "easy_question")[0] for _ in range(n)])
    assert abs(rate - ASSISTMENTS_BKT_PARAMS[0].g) < 0.03


def test_exercises_use_multiple_choice_guess():
    from src.core.simulator_a_bkt import MC_GUESS_SLIP

    sim = SimulatorA(profile="average")
    sim.reset(seed=3)
    sim._learned[:] = 0.0
    sim._params = tuple(p.__class__(l0=p.l0, t=0.0, g=p.g, s=p.s) for p in sim._params)
    rate = np.mean([sim.answer(0, "easy_question")[0] for _ in range(4000)])
    assert abs(rate - MC_GUESS_SLIP[0][0]) < 0.03


def test_hard_question_is_harder():
    sim = SimulatorA(profile="average")
    sim.reset(seed=4)
    sim._learned[:] = 1.0
    easy = np.mean([sim.answer(0, "easy_question")[0] for _ in range(3000)])
    hard = np.mean([sim.answer(0, "hard_question")[0] for _ in range(3000)])
    assert hard < easy


def test_learning_is_monotone_and_hidden_state_stays_current():
    sim = SimulatorA(profile="fast_learner")
    h = sim.reset(seed=5)
    sim._learned[:] = 0.0
    for _ in range(200):
        sim.answer(4, "easy_question")
    assert h.true_mastery[4] == 1.0  # S5 has the largest T; learned after 200 items
    sim.answer(4, "easy_question")
    assert h.true_mastery[4] == 1.0  # no forgetting


def test_test_items_cause_no_learning():  # FR-17
    sim = SimulatorA(profile="average")
    sim.reset(seed=6)
    before = sim._learned.copy()
    for _ in range(100):
        sim.expected_test_score()
        sim.sampled_test_score()
    assert np.array_equal(before, sim._learned)


def test_expected_test_score_formula():
    sim = SimulatorA(profile="average")
    sim.reset(seed=8)
    sim._learned[:] = 1.0
    assert sim.expected_test_score() == pytest.approx(np.mean([1 - p.s for p in ASSISTMENTS_BKT_PARAMS]))
    sim._learned[:] = 0.0
    assert sim.expected_test_score() == pytest.approx(np.mean([p.g for p in ASSISTMENTS_BKT_PARAMS]))


def test_teach_effects_and_k0_ablation():
    # K0: hint and worked example switched off -> no learning from them
    sim = SimulatorA(profile="average", action_effects={"hint": 0.0, "worked_example": 0.0})
    sim.reset(seed=9)
    sim._learned[:] = 0.0
    for _ in range(500):
        sim.teach(4, "hint")
        sim.teach(4, "worked_example")
    assert sim._learned[4] == 0.0
    sim2 = SimulatorA(profile="average")
    sim2.reset(seed=9)
    sim2._learned[:] = 0.0
    for _ in range(500):
        sim2.teach(4, "worked_example")
    assert sim2._learned[4] == 1.0


def test_works_inside_env():
    env = make_env()
    obs, info = env.reset(seed=0)
    assert info == {}
    done = False
    steps = 0
    rng = np.random.default_rng(0)
    while not done:
        valid = np.flatnonzero(env.action_masks())
        action = int(rng.choice(valid[valid != FINISH_ACTION])) if len(valid) > 1 else int(valid[0])
        obs, reward, terminated, truncated, info = env.step(action)
        assert info == {}  # hidden state never leaks through info
        done = terminated or truncated
        steps += 1
    assert steps == env.max_steps
    assert set(ACTION_NAMES) >= {"hint", "worked_example"}


def test_make_env_uses_fitted_params_not_the_generic_placeholder():
    """The policy-side BKT tracker (FR-34) must start from Simulator A's real
    ASSISTments fit, not bkt_tracker.DEFAULT_PARAMS' uniform L0=0.3."""
    env = make_env()
    env.reset(seed=0)
    expected_l0 = np.array([p.l0 for p in ASSISTMENTS_BKT_PARAMS], dtype=np.float32)
    assert np.allclose(env._bkt_tracker.estimate(), expected_l0)
    assert not np.allclose(expected_l0, 0.3)  # sanity: real values aren't the placeholder
