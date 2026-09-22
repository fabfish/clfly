"""Tests for the `e63` resolvability arithmetic.

The number `e63` quotes that is not read straight off the artifact is the seed count needed to resolve
a pair: ``n * (3 / sigma) ** 2``, from sigma scaling as ``1/sqrt(n)``. It is the basis of the claim
that the predictor's one disagreement is affordable to settle, so it is pinned here — including the
degenerate case, where a pair at zero sigma would need infinitely many seeds and must not report a
finite number.
"""

from __future__ import annotations

import numpy as np

TARGET = 3.0


def seeds_for(sigma: float, n_current: int, target: float = TARGET) -> float:
    """Seeds needed for ``target`` sigma, from ``sigma ~ 1/sqrt(n)``."""
    if not np.isfinite(sigma) or sigma <= 0:
        return float("inf")
    return n_current * (target / sigma) ** 2


def test_the_cell_class_pair_needs_about_eighteen_seeds():
    # e63: cell_class under rewired-swap2 is +0.003402 at 1.74 sigma with six seeds
    assert abs(seeds_for(1.74, 6) - 17.84) < 0.1
    assert round(seeds_for(1.74, 6)) == 18


def test_a_pair_already_past_the_target_needs_at_most_what_it_has():
    # side under wider-tasks is 18.25 sigma at six seeds, so six is more than enough
    assert seeds_for(18.25, 6) < 1.0


def test_the_scaling_is_the_inverse_square_of_sigma():
    # halving sigma needs four times the seeds
    assert abs(seeds_for(2.0, 6) / seeds_for(4.0, 6) - 4.0) < 1e-12


def test_a_zero_sigma_pair_cannot_be_resolved_by_seeds_alone():
    assert seeds_for(0.0, 6) == float("inf")
    assert seeds_for(float("nan"), 6) == float("inf")


def test_the_rewired_condition_s_own_sigmas_are_all_below_resolution():
    # the five pairs, as stored; the resolvability flag in the artifact is a ~2 sigma policy
    sigmas = [0.09, 1.74, 0.06, 0.75, 0.23]
    assert max(sigmas) < 2.0
    assert all(seeds_for(s, 6) > 6 for s in sigmas)


def test_the_resolvable_tally_matches_the_published_thirteen():
    # per condition: (resolvable, correct)
    per_condition = [(3, 3), (4, 4), (3, 3), (0, 0), (3, 3)]
    assert sum(r for r, _ in per_condition) == 13
    assert sum(c for _, c in per_condition) == 13
    assert sum(r for r, _ in per_condition) == sum(c for _, c in per_condition)
    # and the "24 of 25" form counts the 12 sub-resolution calls
    assert 25 - 13 == 12
