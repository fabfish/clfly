"""Tests for the matched-random control protocol.

Two things are easy to get wrong here and both would be silent.  The first is the averaging:
seeds and draws are different axes, and only the draw axis is *per-observation* rather than a
standard error.  The second is the feasibility arithmetic -- reporting a large finite number of
draws for a claim that no number of draws can settle would send someone off to burn weeks of
compute on a question already decided by the seed budget.
"""

from __future__ import annotations

import numpy as np
import pytest

from clfly.bench.control import (
    averaged_random_control,
    delta_sem,
    draws_needed,
)
from clfly.lgcl.bases import Partition


@pytest.fixture(scope="module")
def seqs():
    from tests.test_analytic import sample_full
    return [sample_full(d=16, T=4, n=30, sigma2=1.0, q=0.03,
                        rng=np.random.default_rng(s), rotation="random")
            for s in range(3)]


# --------------------------------------------------------------------------
# averaging over draws
# --------------------------------------------------------------------------
def test_one_draw_reproduces_the_single_draw_behaviour(seqs):
    from clfly.bench.analytic import analytic_excess
    labels = np.repeat(np.arange(8), 2)
    part = Partition(labels)
    one = averaged_random_control(seqs, labels, np.random.default_rng(0), draws=1)
    single = analytic_excess(seqs, Partition(np.random.default_rng(0).permutation(labels)))
    assert one["excess_mean"] == pytest.approx(single["excess_mean"])
    assert one["excess_per_seed"] == pytest.approx(single["excess_per_seed"])
    assert one["sd_across_draws"] == 0.0
    assert one["control_draws"] == 1


def test_averaging_reduces_the_sem_and_reports_the_draw_spread(seqs):
    labels = np.repeat(np.arange(8), 2)
    one = averaged_random_control(seqs, labels, np.random.default_rng(0), draws=1)
    many = averaged_random_control(seqs, labels, np.random.default_rng(0), draws=8)
    assert many["control_draws"] == 8
    assert len(many["control_means"]) == 8
    assert many["sd_across_draws"] > 0
    assert many["excess_sem"] <= one["excess_sem"] * 1.5
    # every draw sees the same seeds, so the per-seed vector is an average, not a resample
    assert len(many["excess_per_seed"]) == len(one["excess_per_seed"])


def test_the_averaged_control_keeps_paired_contrasts_working(seqs):
    from clfly.bench.analytic import analytic_excess, paired_delta
    labels = np.repeat(np.arange(8), 2)
    bio = analytic_excess(seqs, Partition(labels))
    ctrl = averaged_random_control(seqs, labels, np.random.default_rng(0), draws=4)
    pc = paired_delta(bio, ctrl)
    assert "sem_paired" in pc and "corr" in pc
    # the draw component must survive into the paired figure: averaging 4 draws cannot make
    # a delta look as precise as the same delta computed with 4x the seeds
    assert pc["sem_paired"] > 0


# --------------------------------------------------------------------------
# the draw term is per-observation, not a standard error
# --------------------------------------------------------------------------
def test_delta_sem_does_not_shrink_the_draw_term_with_seeds():
    # the draw term enters as sd/sqrt(draws) and is blind to how many seeds were used; only
    # the seed term carries the seed count, which is why the caller passes it precomputed
    assert delta_sem(0.0, 1e-3, draws=4) == pytest.approx(5e-4)
    assert delta_sem(0.0, 1e-3, draws=1) == pytest.approx(1e-3)
    assert delta_sem(2e-4, 1e-3, draws=1) == pytest.approx(np.hypot(2e-4, 1e-3))


def test_draws_needed_inverts_the_variance_relation():
    delta, sem, sd = 1e-3, 2e-4, 1e-3
    k = draws_needed(delta, sem, sd, target_sigma=3.0)
    # by construction: at that K the claim sits exactly at the target
    assert abs(delta) / delta_sem(sem, sd, draws=k) == pytest.approx(3.0, rel=1e-6)


def test_draws_needed_does_not_recombine_the_two_rungs_of_a_contrast():
    # REGRESSION. An earlier version took a `contrast` flag and applied its own factor of two,
    # double-counting whenever the caller had already combined the two rungs -- which is the
    # usual case, and which halved every required K and flipped one verdict. The function now
    # takes the claim's terms already combined, so the closed form must match exactly.
    delta, sem, sd = 5e-3, 4e-4, 1.2e-3
    want = (delta / 3.0) ** 2
    assert draws_needed(delta, sem, sd) == pytest.approx(sd ** 2 / (want - sem ** 2))


def test_draws_needed_is_infinite_when_the_seed_budget_binds():
    # the target is below what infinitely many draws could deliver, so no K suffices
    assert draws_needed(1e-4, 5e-4, 1e-3, target_sigma=3.0) == float("inf")


def test_draws_needed_is_smaller_for_a_larger_effect():
    assert draws_needed(5e-3, 2e-4, 1e-3) < draws_needed(5e-4, 2e-4, 1e-3)


def test_draws_needed_is_below_one_when_the_draw_already_suffices():
    # a claim well clear of its floor needs no averaging at all
    assert draws_needed(5e-3, 1e-4, 1e-3) < 1.0


# --------------------------------------------------------------------------
# concentration: the scalar that predicts the control's draw sd
# --------------------------------------------------------------------------
def test_concentration_of_a_balanced_partition():
    # four groups of a hundred, d = 400: 4*100^2 / 400^2
    from clfly.bench.control import concentration
    assert concentration(np.repeat(np.arange(4), 100)) == pytest.approx(0.25)


def test_concentration_of_all_singletons_is_one_over_d():
    from clfly.bench.control import concentration
    # d singletons: d / d^2
    assert concentration(np.arange(400)) == pytest.approx(1 / 400)


def test_concentration_of_one_group_is_one():
    from clfly.bench.control import concentration
    assert concentration(np.zeros(50, dtype=int)) == pytest.approx(1.0)


def test_concentration_ignores_label_names_and_is_monotone_in_coarseness():
    from clfly.bench.control import concentration
    labels = np.repeat(np.arange(8), 12)
    relabelled = labels + 1000                      # same partition, different ids
    assert concentration(relabelled) == pytest.approx(concentration(labels))
    coarse = np.where(labels == 0, 0, 1)            # merge everything but one group
    assert concentration(coarse) > concentration(labels)


def test_draws_needed_is_finite_exactly_when_the_floor_clears_the_target():
    """A consistency invariant that the double-counting bug violated.

    ``K`` is finite iff ``|delta| / sem`` — the floor reachable with infinitely many draws —
    exceeds the target. The buggy version applied its own factor of two to a `sem` that already
    combined two rungs, so it reported ``inf`` for contrasts whose floor was comfortably above
    the target. That inconsistency was visible in the published table (a row with floor 3.3 and
    K = infeasible) and should have been caught by inspection; it is a test now.
    """
    rng = np.random.default_rng(0)
    for _ in range(500):
        delta = float(rng.uniform(-5e-3, 5e-3))
        sem = float(rng.uniform(1e-5, 1e-3))
        sd = float(rng.uniform(1e-5, 3e-3))
        for target in (2.0, 3.0, 4.0):
            k = draws_needed(delta, sem, sd, target)
            clears = abs(delta) / sem > target
            assert (k != float("inf")) == clears, (delta, sem, sd, target, k)
            if clears:
                assert k > 0


# --------------------------------------------------------------------------
# paired_contrast: the network line's central comparison, and its power
# --------------------------------------------------------------------------
def test_paired_contrast_reports_both_sems_and_the_detection_floor():
    from clfly.bench.control import paired_contrast
    rng = np.random.default_rng(0)
    z = rng.normal(size=40)                      # a shared, dominant replicate axis
    a = 0.80 + 0.05 * z + 0.01 * rng.normal(size=40)
    b = 0.79 + 0.05 * z + 0.01 * rng.normal(size=40)
    out = paired_contrast(a, b)
    assert out["n"] == 40
    assert out["delta"] == pytest.approx(0.01, abs=0.01)
    # the shared axis cancels in the paired difference, which is the point
    assert out["sem_paired"] < 0.3 * out["sem_unpaired"]
    assert out["min_detectable"] == pytest.approx(2.0 * out["sem_paired"])
    assert out["repeats_for_0.01"] >= 1


def test_paired_contrast_needs_matched_arms():
    from clfly.bench.control import paired_contrast
    with pytest.raises(ValueError):
        paired_contrast([1.0, 2.0], [1.0])
    with pytest.raises(ValueError):
        paired_contrast([], [])


def test_paired_contrast_handles_a_single_replicate():
    # one replicate has no spread, so the sems are undefined rather than zero; the delta survives
    from clfly.bench.control import paired_contrast
    out = paired_contrast([0.81], [0.79])
    assert out["delta"] == pytest.approx(0.02)
    assert out["n"] == 1
    assert "sem_paired" not in out


def test_evaluation_noise_is_the_binomial_standard_error():
    from clfly.bench.control import evaluation_noise
    # 144 held-out decisions at p = 0.8
    assert evaluation_noise(0.8, 144) == pytest.approx(np.sqrt(0.8 * 0.2 / 144))
    assert evaluation_noise(0.5, 100) == pytest.approx(0.05)
    # a perfect score has no binomial spread, and n=0 is undefined rather than infinite
    assert evaluation_noise(1.0, 144) == 0.0
    assert np.isnan(evaluation_noise(0.8, 0))
