"""Tests for the oracle/bench helpers, and for the determinism they depend on.

The metric-instability fire found that the headline statistic was chaotic. These
tests pin the two things that make it readable — bit-reproducible inputs, and an
effect size that comes with a spread — so the fix cannot silently regress.
"""

from __future__ import annotations

import numpy as np
import pytest

from clfly.bench.oracle import (
    error_levels,
    gap_bandwidth,
    gap_vs_oracle,
    paired_excess,
    rank_of,
    task_geometry,
    task_subspaces,
)
from clfly.lgcl.bases import Diagonal, Full
from clfly.lgcl.model import sample_full, sample_partial


@pytest.fixture(scope="module")
def seqs():
    """A small rank-deficient task family — the ill-conditioned regime."""
    return [
        sample_partial(d=30, T=5, n=20, sigma2=1.0, q=0.02,
                       rng=np.random.default_rng(s), obs_dim=8)
        for s in range(3)
    ]


@pytest.fixture(scope="module")
def seq_full():
    rng = np.random.default_rng(0)
    return sample_full(d=12, T=5, n=20, sigma2=1.0, q=0.05, rng=rng,
                       rotation="cumulative", alpha=0.3)


def test_oracle_is_the_best_filter(seqs):
    """The oracle line must actually be a lower bound, or nothing based on it holds."""
    for seq in seqs:
        lv = error_levels(seq, Diagonal(seq.d))
        assert lv["oracle_final"] <= lv["ewc_final"] + 1e-9
        assert lv["excess_final"] >= -1e-9


def test_gap_vs_oracle_is_zero_for_the_oracle_itself(seq_full):
    assert gap_vs_oracle(seq_full, Full(seq_full.d)) == pytest.approx(0.0, abs=1e-9)


def test_error_levels_are_self_consistent(seq_full):
    lv = error_levels(seq_full, Diagonal(seq_full.d))
    assert lv["excess_final"] == pytest.approx(lv["ewc_final"] - lv["oracle_final"])
    assert lv["oracle_forgetting"] >= 0


def test_paired_excess_reports_a_spread_and_a_sane_ratio(seqs):
    out = paired_excess(seqs, Diagonal(seqs[0].d))
    assert out["n"] == 3
    assert out["excess_sem"] > 0, "a 3-seed sem of zero means the pooling is wrong"
    assert out["excess_sd"] >= out["excess_sem"]
    # gap_of_means divides by the *averaged* oracle error, so it is the calm form
    assert out["gap_of_means"] == pytest.approx(
        out["excess_mean"] / out["oracle_mean"], rel=1e-9)


def test_paired_excess_sem_is_zero_for_a_single_sequence(seqs):
    out = paired_excess(seqs[:1], Diagonal(seqs[0].d))
    assert out["n"] == 1
    assert out["excess_sem"] == 0.0
    assert out["gap_sd"] == 0.0


def test_gap_bandwidth_is_non_negative_and_reports_the_base_gap(seqs):
    bw = gap_bandwidth(seqs[0], Diagonal(seqs[0].d), rel=1e-10, n=3)
    assert bw["band_std"] >= 0.0
    assert bw["band_max"] >= 0.0
    assert len(bw["band_vals"]) == 3
    assert bw["gap"] == pytest.approx(
        gap_vs_oracle(seqs[0], Diagonal(seqs[0].d)), abs=1e-12)


def test_geometry_names_the_expected_readings(seqs):
    ranks = [rank_of(seqs[0], k) for k in range(seqs[0].T)]
    g = task_geometry(seqs[0], ranks)
    for key in ("consecutive_alignment", "all_pairs_alignment", "mean_rank",
                "effective_rank", "flattening", "top_eig_share", "chance_alignment"):
        assert key in g
    assert 0.0 <= g["top_eig_share"] <= 1.0


def test_task_subspaces_top_truncates_the_range_space():
    """Regression for the range-space degeneracy that broke the e3 predictor.

    At the numerical rank the returned subspace is the task's *entire* range space,
    which is blind to the drive weights.  `top` must actually reduce the
    dimension, and it must do so by selecting strong directions rather than by
    slicing arbitrarily.
    """
    seq = sample_partial(d=30, T=3, n=20, sigma2=1.0, q=0.02,
                         rng=np.random.default_rng(0), obs_dim=10)
    ranks = [rank_of(seq, k) for k in range(seq.T)]
    full = task_subspaces(seq, ranks)
    top4 = task_subspaces(seq, ranks, top=4)
    assert all(v.shape[1] == ranks[k] for k, v in enumerate(full))
    assert all(v.shape[1] == 4 for v in top4)

    # the leading direction is unchanged; only the depth differs
    for k in range(seq.T):
        w, V = np.linalg.eigh(seq.J[k])
        lead = V[:, np.argsort(w)[::-1][:1]]
        overlap = float(np.abs(lead.T @ top4[k][:, :1]).ravel()[0])
        assert overlap > 0.99
