"""Tests for the `e47` per-seed contrast dissection.

`e47` asks whether the C1 contrasts are seed-robust, and the statistic that answers it is **seed
leverage** — the largest change in the mean from dropping one seed, in units of the all-seeds sem —
together with sign unanimity. Sigma alone is a poor detector and the first version of this test
module asserted the wrong thing about it: sigma is a mean-to-sem ratio, so removing the very seed
that carries a contrast can make sigma *larger* by collapsing the sem faster than the mean. That is
pinned here as a regression, alongside the degenerate cases (a 3-seed contrast cannot support a
drop-one check at all).
"""

from __future__ import annotations

import numpy as np


def delta_stats(delta: np.ndarray) -> tuple[float, float]:
    """Mean and paired sigma of a per-seed contrast -- the computation `e47` reports."""
    n = len(delta)
    sem = float(delta.std(ddof=1) / np.sqrt(n))
    return float(delta.mean()), (float(delta.mean() / sem) if sem else float("nan"))


def leave_one_out(delta: np.ndarray) -> tuple[list[float], float, bool]:
    """With each seed removed: its absolute sigma, the leverage, and any sign flip.

    ``leverage`` is the largest ``|mean(-k) - mean| / sem(all)`` over the removals. A drop-one check
    needs at least three seeds left, so a 3-seed contrast yields ``([], 0.0, False)`` rather than a
    fabricated number -- which is what `e47`'s cs = 300 row shows.
    """
    n = len(delta)
    sem = float(delta.std(ddof=1) / np.sqrt(n))
    sigmas, leverage, flip = [], 0.0, False
    for k in range(n):
        keep = np.delete(delta, k)
        if keep.size < 3:
            continue
        mean, sigma = delta_stats(keep)
        sigmas.append(abs(sigma))
        if sem:
            leverage = max(leverage, abs(mean - float(delta.mean())) / sem)
        if np.sign(mean) != np.sign(delta.mean()):
            flip = True
    return sigmas, leverage, flip


def test_delta_stats_reproduces_a_hand_computed_contrast():
    d = np.array([2.0, 4.0, 6.0, 8.0])
    mean, sigma = delta_stats(d)
    assert mean == 5.0
    # sd(ddof=1) = sqrt(20/3) = 2.58199, sem = 1.29099, sigma = 3.87298
    assert abs(sigma - 3.87298) < 1e-4


def test_a_fixed_effect_is_unanimous_with_low_leverage():
    d = np.array([0.010, 0.011, 0.009, 0.012, 0.010, 0.011])
    _, leverage, flip = leave_one_out(d)
    assert not flip
    assert leverage < 1.0  # no single seed moves the mean by a whole sem
    assert (d > 0).all()


def test_the_three_seed_case_refuses_a_drop_one_check():
    # cs = 300 is this case: n = 3, so removing a seed leaves 2 and nothing can be quoted
    sigmas, leverage, flip = leave_one_out(np.array([0.03, 0.04, 0.031]))
    assert sigmas == [] and leverage == 0.0 and flip is False


def test_leverage_saturates_at_one_when_a_single_seed_carries_the_contrast():
    # five seeds agreeing tightly on ~+0.009 and one outlier at +0.05
    d = np.array([0.009, 0.0092, 0.0088, 0.0091, 0.0089, 0.05])
    sigmas, leverage, flip = leave_one_out(d)
    assert d.mean() > 0 and not flip
    # Leverage is |mean(-k) - mean| / sem(all), and for a single outlier both terms are
    # (outlier - bulk)/n, so it saturates at exactly 1 -- it is a 0-to-1 scale with 1 meaning "one
    # seed is worth a whole sem on its own", not an unbounded detector. That is why e47 reports it
    # alongside sign unanimity rather than as a threshold test.
    assert abs(leverage - 1.0) < 0.02
    # and the same identity holds for a different n, which is what makes it an identity
    d5 = np.array([0.009, 0.0091, 0.0089, 0.00905, 0.05])
    assert abs(leave_one_out(d5)[1] - 1.0) < 0.02
    # removing the outlier RAISES sigma rather than shrinking it, because the sem collapses faster
    # than the mean. This is the direction the first version of this module got backwards: a
    # drop-one sigma range is not a detector of one-seed leverage.
    assert sigmas[-1] > abs(delta_stats(d)[1]) * 10


def test_a_sign_flip_is_detected_when_one_seed_reverses_the_mean():
    # four small negatives and one large positive: the mean is positive, and dropping the positive
    # seed makes it negative
    d = np.array([0.20, -0.02, -0.03, -0.02, -0.01])
    assert d.mean() > 0
    _, _, flip = leave_one_out(d)
    assert flip is True


def test_no_flip_is_reported_when_every_removal_keeps_the_sign():
    _, _, flip = leave_one_out(np.array([-0.05, -0.02, -0.03, -0.01]))
    assert flip is False


def test_unanimity_probability_matches_the_binomial_used_in_the_finding():
    # e47 quotes P(unanimous | fair coin) = 2^(1-n); 6 seeds gives 0.03125, which is the number in
    # the finding's table
    assert 2 ** (1 - 6) == 0.03125
    assert 2 ** (1 - 3) == 0.25
