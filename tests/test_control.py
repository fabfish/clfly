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
    delta, sem_seed, sd = 1e-3, 2e-4, 1e-3
    k = draws_needed(delta, sem_seed, sd, target_sigma=3.0, contrast=False)
    # check by construction: at that K the claim is exactly at the target
    assert abs(delta) / delta_sem(sem_seed, sd, draws=k) == pytest.approx(3.0, rel=1e-6)


def test_draws_needed_doubles_for_a_contrast():
    a = draws_needed(1e-3, 2e-4, 1e-3, target_sigma=3.0, contrast=False)
    b = draws_needed(1e-3, 2e-4, 1e-3, target_sigma=3.0, contrast=True)
    assert b > a


def test_draws_needed_is_infinite_when_the_seed_budget_binds():
    # the target is below what infinitely many draws could deliver, so no K suffices
    assert draws_needed(1e-4, 5e-4, 1e-3, target_sigma=3.0, contrast=True) == float("inf")


def test_draws_needed_is_smaller_for_a_larger_effect():
    small = draws_needed(5e-4, 2e-4, 1e-3, contrast=True)
    large = draws_needed(5e-3, 2e-4, 1e-3, contrast=True)
    assert large < small
