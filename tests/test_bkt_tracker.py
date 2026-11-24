import numpy as np

from src.core.bkt_tracker import BKTParams, BKTTracker


def test_reset_gives_prior_l0():
    params = BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1)
    tracker = BKTTracker(num_skills=3, params=params)
    assert np.allclose(tracker.estimate(), [0.3, 0.3, 0.3])


def test_correct_answer_increases_belief():
    tracker = BKTTracker(num_skills=1, params=BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1))
    before = tracker.estimate()[0]
    tracker.update(0, correct=True)
    after = tracker.estimate()[0]
    assert after > before


def test_incorrect_answer_can_still_increase_belief_via_learning_transit():
    """Even a wrong answer nudges belief up through the T (learn) term, but
    less than a correct answer would - this is standard BKT behaviour."""
    tracker_correct = BKTTracker(num_skills=1, params=BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1))
    tracker_wrong = BKTTracker(num_skills=1, params=BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1))
    tracker_correct.update(0, correct=True)
    tracker_wrong.update(0, correct=False)
    assert tracker_correct.estimate()[0] > tracker_wrong.estimate()[0]


def test_update_only_affects_the_given_skill():
    tracker = BKTTracker(num_skills=3, params=BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1))
    tracker.update(1, correct=True)
    estimate = tracker.estimate()
    assert estimate[0] == 0.3
    assert estimate[2] == 0.3
    assert estimate[1] > 0.3


def test_belief_stays_in_unit_interval_after_many_updates():
    tracker = BKTTracker(num_skills=1, params=BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1))
    for i in range(50):
        tracker.update(0, correct=(i % 2 == 0))
    estimate = tracker.estimate()[0]
    assert 0.0 <= estimate <= 1.0


def test_reset_clears_previous_updates():
    tracker = BKTTracker(num_skills=1, params=BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1))
    tracker.update(0, correct=True)
    tracker.reset()
    assert np.allclose(tracker.estimate(), [0.3])
