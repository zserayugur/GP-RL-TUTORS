"""Policy-side BKT belief tracker (FR-34).

Estimates per-skill mastery P(L) purely from the sequence of observed
correct/incorrect answers - the same way for every simulator (A, B or C),
since it never touches simulator-internal state. This is what makes it valid
to place in the observation (NFR-02/NFR-10): a researcher could compute the
exact same numbers a real teacher would, from the same answer log.

Parameters (L0, T, G, S) are placeholders pending Seray's pyBKT fit on
ASSISTments (WBS 6.1); swap `DEFAULT_PARAMS` once that lands.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BKTParams:
    l0: float  # prior P(mastered) before any evidence
    t: float  # P(learn) per opportunity
    g: float  # P(correct | not mastered) - guess
    s: float  # P(incorrect | mastered) - slip


DEFAULT_PARAMS = BKTParams(l0=0.3, t=0.1, g=0.2, s=0.1)  # placeholder, pending WBS 6.1


class BKTTracker:
    """One belief P(L) per skill, updated only from observed correctness."""

    def __init__(self, num_skills: int, params: BKTParams | list[BKTParams] | None = None):
        self.num_skills = num_skills
        if params is None:
            params = [DEFAULT_PARAMS] * num_skills
        elif isinstance(params, BKTParams):
            params = [params] * num_skills
        if len(params) != num_skills:
            raise ValueError("params must have one entry per skill")
        self._params = params
        self._belief = np.array([p.l0 for p in self._params], dtype=np.float32)

    def reset(self) -> None:
        self._belief = np.array([p.l0 for p in self._params], dtype=np.float32)

    def update(self, skill: int, correct: bool) -> None:
        p = self._params[skill]
        prior = self._belief[skill]
        if correct:
            posterior = (prior * (1 - p.s)) / (prior * (1 - p.s) + (1 - prior) * p.g)
        else:
            posterior = (prior * p.s) / (prior * p.s + (1 - prior) * (1 - p.g))
        self._belief[skill] = posterior + (1 - posterior) * p.t

    def estimate(self) -> np.ndarray:
        """Current P(mastered) per skill, shape (num_skills,)."""
        return self._belief.copy()
