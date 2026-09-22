"""Tests for the analytic expected error.

The analytic formula is the project's answer to a metric that was too noisy to
resolve anything, so it has to be *right*, not merely smooth. Every test here
compares it against a Monte Carlo average of the realized error on the same task
precisions — a wrong-but-smooth formula would be far worse than a noisy one.

The drift flag matters and is easy to get wrong: the filter always believes the
parameter drifts (that is the stability/plasticity trade-off), but the reference
partial-observation family holds ``theta`` fixed. An earlier version added the
drift term unconditionally and inflated the non-drifting error by ~3x while leaving
the drifting case correct — which is exactly the failure the MC comparison exists
to catch.
"""

from __future__ import annotations

import numpy as np
import pytest

from clfly.bench.analytic import (
    analytic_excess,
    contrast_of_contrasts,
    expected_error_matrix,
    expected_oracle,
    paired_delta,
    response_matrices,
    summarize_expected,
    trajectory_cov,
)
from clfly.lgcl.bases import Diagonal, Full, Rank
from clfly.lgcl.kalman import filter_sequence
from clfly.lgcl.methods import AnchoredFilter
from clfly.lgcl.model import (
    Sequence,
    error_tensor,
    sample_full,
    sample_measurement,
    sample_partial,
    summarize,
)


def redraw(seq, rng):
    """Resample ``(theta, y)`` for *fixed* ``J`` and ``Sigma``."""
    theta = rng.standard_normal(seq.d)
    th, ys = [], []
    for k in range(seq.T):
        th.append(theta.copy())
        ys.append(sample_measurement(theta, seq.J[k], rng))
        if seq.drifted:
            theta = theta + np.sqrt(seq.q) * rng.standard_normal(seq.d)
    return Sequence(seq.d, seq.q, np.stack(th), seq.J, seq.Sigma,
                    np.stack(ys), None, seq.drifted)


def mc_error(seq, basis, draws=3000, seed=0):
    rng = np.random.default_rng(seed)
    acc = np.zeros((seq.T, seq.T))
    for _ in range(draws):
        s = redraw(seq, rng)
        acc += error_tensor(AnchoredFilter(basis).run(s), s)
    return acc / draws


@pytest.fixture(scope="module")
def drifting():
    return sample_full(d=20, T=5, n=40, sigma2=1.0, q=0.05,
                       rng=np.random.default_rng(0), rotation="random")


@pytest.fixture(scope="module")
def partial():
    return sample_partial(d=20, T=5, n=40, sigma2=1.0, q=0.02,
                          rng=np.random.default_rng(1), obs_dim=8)


# --------------------------------------------------------------------------
# the response matrices, against finite differences
# --------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["Full", "Diagonal"])
def test_response_matrices_match_finite_differences(drifting, name):
    """``R[k][j]`` must really be the filter's sensitivity to observation ``j``."""
    basis = Full(drifting.d) if name == "Full" else Diagonal(drifting.d)
    R, _, _ = response_matrices(drifting, basis)
    est0, _ = filter_sequence(drifting, basis)
    eps = 1e-6
    for j in range(drifting.T):
        for i in range(0, drifting.d, 5):
            e = np.zeros(drifting.d)
            e[i] = 1.0
            y2 = drifting.y.copy()
            y2[j] = y2[j] + eps * e
            s2 = Sequence(drifting.d, drifting.q, drifting.theta, drifting.J,
                          drifting.Sigma, y2, None, drifting.drifted)
            est2, _ = filter_sequence(s2, basis)
            for k in range(j, drifting.T):
                fd = (est2[k] - est0[k]) / eps
                np.testing.assert_allclose(fd, R[k][j][:, i], atol=1e-5)


# --------------------------------------------------------------------------
# the expected error, against Monte Carlo
# --------------------------------------------------------------------------
@pytest.mark.parametrize("basis_name", ["kalman", "ewc", "rank4"])
def test_expected_error_matches_monte_carlo_when_drifting(drifting, basis_name):
    basis = {"kalman": Full(drifting.d), "ewc": Diagonal(drifting.d),
             "rank4": Rank(drifting.d, 4)}[basis_name]
    A = expected_error_matrix(drifting, basis)
    B = mc_error(drifting, basis, draws=3000)
    assert np.abs(A - B).max() / max(1e-12, np.abs(B).max()) < 0.05


@pytest.mark.parametrize("basis_name", ["kalman", "ewc"])
def test_expected_error_matches_monte_carlo_without_drift(partial, basis_name):
    """The regression that caught the unconditional drift term (~3x error)."""
    basis = {"kalman": Full(partial.d), "ewc": Diagonal(partial.d)}[basis_name]
    A = expected_error_matrix(partial, basis)
    B = mc_error(partial, basis, draws=3000)
    assert np.abs(A - B).max() / max(1e-12, np.abs(B).max()) < 0.05


def test_trajectory_covariance_respects_the_drift_flag(drifting, partial):
    """``S[j, l] = P0 + q * min(j, l)`` when drifting, ``P0`` when not."""
    T, q = drifting.T, drifting.q
    Sp = trajectory_cov(partial)
    np.testing.assert_allclose(Sp, np.ones((partial.T, partial.T)))

    Sd = trajectory_cov(drifting)
    for j in range(T):
        for l in range(T):
            assert Sd[j, l] == pytest.approx(1.0 + q * min(j, l))
    assert Sd[0, T - 1] == pytest.approx(1.0)          # min(0, T-1) = 0
    assert Sd[T - 1, T - 1] == pytest.approx(1.0 + (T - 1) * q)


def test_expected_error_is_lower_triangular_and_non_negative(drifting):
    E = expected_error_matrix(drifting, Diagonal(drifting.d))
    assert np.allclose(E[np.triu_indices(drifting.T, k=1)], 0.0)
    assert (np.diag(E) > 0).all()
    assert (E[~np.triu(np.ones_like(E, dtype=bool), 1)] >= 0).all()


def test_oracle_is_the_best_expected_filter(drifting):
    """The oracle line must be a genuine lower bound on the expected error."""
    o = expected_oracle(drifting)
    for basis in (Diagonal(drifting.d), Rank(drifting.d, 4)):
        a = summarize_expected(expected_error_matrix(drifting, basis))
        assert o["final_avg_error"] <= a["final_avg_error"] + 1e-9


def test_analytic_excess_is_deterministic_and_pools_cleanly(drifting):
    """No draws anywhere: the same input must give bit-identical output, sd 0."""
    seqs = [drifting] * 3
    out = analytic_excess(seqs, Diagonal(drifting.d))
    assert out["n"] == 3
    assert out["excess_sd"] == 0.0, "identical sequences must give identical excess"
    assert out["excess_sem"] == 0.0
    again = analytic_excess(seqs, Diagonal(drifting.d))
    assert again["excess_mean"] == out["excess_mean"]


def test_analytic_excess_decomposition_is_consistent(drifting):
    out = analytic_excess([drifting], Diagonal(drifting.d))
    assert out["excess_mean"] == pytest.approx(out["ewc_mean"] - out["oracle_mean"])
    assert out["gap_of_means"] == pytest.approx(out["excess_mean"] / out["oracle_mean"])


# --------------------------------------------------------------------------
# paired contrasts -- the difference between "resolves from zero" and "differs
# from its neighbour", which is what decides whether a curve has a shape
# --------------------------------------------------------------------------
def _arms(corr, n=200, sd_a=1.0, sd_b=1.0, mean_a=2.0, mean_b=1.0, seed=0):
    """Two synthetic per-seed arms with a chosen correlation across seeds."""
    rng = np.random.default_rng(seed)
    z = rng.normal(size=n)
    w = rng.normal(size=n)
    a = mean_a + sd_a * z
    b = mean_b + sd_b * (corr * z + np.sqrt(1 - corr ** 2) * w)
    return ({"excess_mean": float(a.mean()), "excess_sem": float(a.std(ddof=1) / np.sqrt(n)),
             "excess_per_seed": a.tolist()},
            {"excess_mean": float(b.mean()), "excess_sem": float(b.std(ddof=1) / np.sqrt(n)),
             "excess_per_seed": b.tolist()})


def test_paired_delta_is_exact_for_perfectly_correlated_arms():
    # with corr = 1 the difference is constant across seeds, so its sem is 0
    a, b = _arms(corr=1.0)
    out = paired_delta(a, b)
    assert out["corr"] == pytest.approx(1.0)
    assert out["sem_paired"] == pytest.approx(0.0, abs=1e-12)
    assert out["delta"] == pytest.approx(a["excess_mean"] - b["excess_mean"])
    assert out["conservatism"] > 1e6          # the unpaired figure paid a huge price


def test_paired_delta_matches_the_unpaired_figure_when_arms_are_independent():
    a, b = _arms(corr=0.0)
    out = paired_delta(a, b)
    assert out["corr"] == pytest.approx(0.0, abs=0.15)
    assert out["sem_paired"] == pytest.approx(out["sem_unpaired"], rel=0.25)


def test_pairing_helps_exactly_when_the_sample_correlation_is_positive():
    # the quadrature figure is an upper bound only under independence. With a negative
    # sample correlation the PAIRED sem is the larger one -- and it is the right one.
    for corr in (0.0, 0.3, 0.6, 0.9, 1.0, -0.3, -0.9):
        a, b = _arms(corr=corr)
        out = paired_delta(a, b)
        if out["corr"] > 1e-9:
            assert out["sem_paired"] < out["sem_unpaired"]
        elif out["corr"] < -1e-9:
            assert out["sem_paired"] > out["sem_unpaired"]
        else:
            assert out["sem_paired"] == pytest.approx(out["sem_unpaired"], rel=0.05)


def test_paired_delta_degrades_cleanly_without_per_seed_values():
    a, b = _arms(corr=0.5)
    del a["excess_per_seed"]
    out = paired_delta(a, b)
    assert "sem_paired" not in out and "corr" not in out
    assert out["delta"] == pytest.approx(a["excess_mean"] - b["excess_mean"])
    assert out["sigma_unpaired"] > 0


def test_contrast_of_contrasts_is_paired_too():
    # two rungs whose deltas share a seed axis: the contrast is far better resolved
    # paired than not, which is the whole reason the shape test needs per-seed values
    a, b = _arms(corr=0.9, mean_a=2.0, mean_b=1.0, seed=1)
    c, d = _arms(corr=0.9, mean_a=1.9, mean_b=1.0, seed=2)
    out = contrast_of_contrasts(paired_delta(a, b), paired_delta(c, d))
    assert out["delta"] == pytest.approx((2.0 - 1.0) - (1.9 - 1.0), abs=0.4)
    assert out["sem_paired"] <= out["sem_unpaired"]
    assert out["conservatism"] >= 1.0


def test_contrast_of_contrasts_without_per_seed_falls_back_to_unpaired():
    a, b = _arms(corr=0.9, seed=3)
    c, d = _arms(corr=0.9, seed=4)
    pa, pc = paired_delta(a, b), paired_delta(c, d)
    for pc_ in (pa, pc):
        pc_.pop("per_seed_delta")
    out = contrast_of_contrasts(pa, pc)
    assert "sem_paired" not in out
    assert out["sigma_unpaired"] > 0
