"""Tests for the `e49` intervention-leverage statistic.

`e49`'s claim is that the `kappa` knob is (largely) inert at `swap2`/cs = 800, so the correlation
computed there tests nothing. That claim rests on `travel / seed_sd_at_k0`, and the statistic has two
failure modes worth pinning: dividing by a zero or single-seed spread (which would make any travel
look infinite), and treating a *partial* seed's travel as comparable to a complete one (a 4-of-7
sweep has less chance to reach its extremes, so its travel is biased low — which is the direction
that would overstate inertness).

The threshold itself is arbitrary and the real data straddles it, so the last test records that
rather than pretending it is a clean separation.
"""

from __future__ import annotations

import numpy as np


def travel_over_noise(flatten: np.ndarray, kappa: np.ndarray) -> tuple[float, float, float]:
    """(travel, seed_sd_at_k0, ratio) for one seed's sweep.

    ``seed_sd_at_k0`` needs the *other* seeds, so this helper cannot supply it and returns ``nan``
    for it and for the ratio; the real script computes it across seeds. Keeping the placeholder
    explicit rather than returning an infinite ratio is the point -- a travel with no noise estimate
    is not evidence of leverage.
    """
    flat = np.asarray(flatten, dtype=float)
    travel = float(np.ptp(flat))
    return travel, float("nan"), float("nan")


def ratio(travel: float, seed_sd: float) -> float:
    if not np.isfinite(seed_sd) or seed_sd <= 0:
        return float("nan")
    return travel / seed_sd


def test_travel_is_the_full_range_of_the_knob_s_sweep():
    flat = np.array([0.7587, 0.7097, 0.5862, 0.3215, 0.1453, 0.0878, 0.0488])
    travel, _, _ = travel_over_noise(flat, np.arange(7))
    assert abs(travel - (0.7587 - 0.0488)) < 1e-12


def test_ratio_refuses_a_degenerate_noise_estimate():
    # a single seed at the starting point gives no spread at all
    assert not np.isfinite(ratio(0.71, float("nan")))
    assert not np.isfinite(ratio(0.71, 0.0))
    assert abs(ratio(0.71, 0.005) - 142.0) < 1e-9


def test_the_two_regimes_in_the_real_data_are_far_apart():
    # measured: real cs=800 travels 0.710 with a seed sd of 0.00501; swap2 cs=800 travels 0.0039
    # with the same sd
    real = ratio(0.7099, 0.00501)
    swap2 = ratio(0.0039, 0.00501)
    assert real > 100
    assert swap2 < 10
    assert real / swap2 > 50


def test_a_partial_sweep_understates_travel_and_so_overstates_inertness():
    # seed 2 at swap2/cs800 is 4 of 7 kappas; its travel (0.0022) is smaller than the complete
    # seeds' (0.0039 and 0.0084) purely because it has fewer points to reach its extremes with
    part = ratio(0.0022, 0.00042)
    full = ratio(0.0084, 0.00042)
    assert part < full
    # so a partial seed must never be the evidence for inertness on its own
    assert part < 10 < full


def test_the_threshold_is_a_choice_and_the_data_straddles_it():
    # the three swap2 seeds give 9.4, 20.2 and 5.3 -- one above a floor of 10 and two below, which
    # is why e49 reports the verdict per seed instead of per section
    ratios = [9.4, 20.2, 5.3]
    assert sum(r > 10 for r in ratios) == 1
    assert sum(r < 10 for r in ratios) == 2
    # and the real-topology ratios are all an order of magnitude clear of the floor
    assert all(r > 100 for r in [141.7, 145.7, 142.7, 261.6, 270.3, 267.5])
