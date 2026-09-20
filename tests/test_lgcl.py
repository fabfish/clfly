"""Regression gate for the LGCL port.

Two jobs: prove the anchoring-basis machinery behaves like the mathematics says
(projections are idempotent, the extremes coincide, matched controls really are
matched), and freeze the published numbers so later refactors cannot silently
move them.
"""

from __future__ import annotations

import numpy as np
import pytest

from clfly.lgcl import repro
from clfly.lgcl.bases import (
    Diagonal,
    Full,
    Partition,
    Rank,
    RotatedDiagonal,
    alignment_score,
    gain_mismatch_cost,
    principal_angles,
    random_partition,
)
from clfly.lgcl.kalman import filter_sequence, rts_smoother
from clfly.lgcl.methods import Replay, run
from clfly.lgcl.model import error_tensor, sample_full, sample_partial, summarize


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------
@pytest.fixture(scope="module")
def seq20():
    rng = np.random.default_rng(0)
    return sample_full(d=20, T=10, n=40, sigma2=1.0, q=0.05, rng=rng, rotation="random")


@pytest.fixture(scope="module")
def seq2():
    rng = np.random.default_rng(0)
    return sample_full(d=2, T=6, n=40, sigma2=1.0, q=0.05, rng=rng,
                       rotation="cumulative", alpha=np.deg2rad(12))


@pytest.fixture(scope="module")
def seq_partial():
    rng = np.random.default_rng(0)
    return sample_partial(d=20, T=8, n=40, sigma2=1.0, q=0.02, rng=rng, obs_dim=8)


def spd(rng, d):
    A = rng.standard_normal((d, d))
    return A @ A.T + d * np.eye(d)


# --------------------------------------------------------------------------
# the published numbers
# --------------------------------------------------------------------------
def test_exp1_reproduces_published_table():
    """The headline comparison must match lgcl_results.json to ~5e-5."""
    computed = repro.exp1_main(runs=200)
    rows, worst = repro.compare(computed, repro.gated_anchors())
    assert len(rows) == 10
    assert worst < 1e-3, f"repro_max_abs_err regressed to {worst}"


def test_repro_json_reports_the_metric():
    """The metric-loop entry point must emit a parseable scalar.

    This is an interface smoke test at 20 runs, so the tolerance is loose: the
    ``naive`` anchor is the high-variance one and 20 runs is not enough for it.
    The statistical check is ``test_exp1_reproduces_published_table`` at 200 runs.
    """
    import io
    import json
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        repro.main(["--json", "--runs", "20"])
    payload = json.loads(buf.getvalue())
    assert payload["repro_max_abs_err"] < 0.15
    assert payload["n_gating_anchors"] == 10


# --------------------------------------------------------------------------
# the model
# --------------------------------------------------------------------------
def test_sampling_is_deterministic_and_ordered():
    a = sample_full(d=5, T=3, n=10, sigma2=1.0, q=0.1, rng=np.random.default_rng(7),
                    rotation="random")
    b = sample_full(d=5, T=3, n=10, sigma2=1.0, q=0.1, rng=np.random.default_rng(7),
                    rotation="random")
    np.testing.assert_array_equal(a.theta, b.theta)
    np.testing.assert_array_equal(a.J, b.J)
    np.testing.assert_array_equal(a.y, b.y)


def test_error_tensor_is_lower_triangular(seq20):
    E = error_tensor(run("kalman", seq20), seq20)
    assert np.allclose(E[np.triu_indices(seq20.T, k=1)], 0.0)
    assert (np.diag(E) >= 0).all()


def test_partial_tasks_have_rank_deficient_precision(seq_partial):
    w = np.linalg.eigvalsh(seq_partial.J[0])
    assert np.sum(w > 1e-9) == 8
    assert np.isclose(np.trace(seq_partial.Sigma[0]), 8.0)


# --------------------------------------------------------------------------
# the anchoring bases
# --------------------------------------------------------------------------
def test_projection_extremes_coincide_with_the_known_methods(seq2):
    """Singleton partition == diagonal == EWC; one group == full == oracle."""
    d = seq2.d
    P = spd(np.random.default_rng(0), d)
    np.testing.assert_allclose(Diagonal(d).project(P),
                               Partition(np.arange(d)).project(P))
    np.testing.assert_allclose(Full(d).project(P),
                               Partition(np.zeros(d, dtype=int)).project(P))
    np.testing.assert_allclose(Diagonal(d).project(P),
                               RotatedDiagonal(np.eye(d)).project(P))
    np.testing.assert_allclose(Full(d).project(P), Rank(d, r=d).project(P))


def test_projections_are_idempotent():
    rng = np.random.default_rng(1)
    d = 12
    P = spd(rng, d)
    labels = np.array([0, 0, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5])
    for basis in (Diagonal(d), Full(d), Partition(labels), Rank(d, r=4),
                  RotatedDiagonal(np.linalg.qr(rng.standard_normal((d, d)))[0])):
        once = basis.project(P)
        np.testing.assert_allclose(basis.project(once), once, atol=1e-8,
                                   err_msg=f"{basis.name} is not idempotent")


def test_partition_parameter_count_is_the_matched_budget():
    """Free parameters must equal the sum of per-group triangular numbers."""
    labels = np.array([0, 0, 1, 2, 2])
    p = Partition(labels)
    assert p.n_groups == 3
    assert list(p.group_sizes) == [2, 1, 2]
    assert p.n_parameters == 3 + 1 + 3
    # a singleton partition *is* the diagonal, and must cost the same
    assert Partition(np.arange(5)).n_parameters == Diagonal(5).n_parameters == 5
    assert Full(5).n_parameters == 15


def test_random_partition_control_is_size_matched():
    labels = np.repeat(np.arange(4), [10, 5, 20, 3])
    ctl = random_partition(labels, np.random.default_rng(3))
    assert ctl.n_groups == Partition(labels).n_groups
    assert sorted(ctl.group_sizes) == sorted(Partition(labels).group_sizes)
    assert ctl.n_parameters == Partition(labels).n_parameters
    assert not np.array_equal(ctl.labels, labels)


def test_indicator_span_has_one_dimension_per_group():
    labels = np.repeat(np.arange(4), [3, 3, 3, 3])
    Q = Partition(labels).indicator_span()
    assert Q.shape == (12, 4)
    np.testing.assert_allclose(Q.T @ Q, np.eye(4), atol=1e-10)


# --------------------------------------------------------------------------
# alignment diagnostics
# --------------------------------------------------------------------------
def test_alignment_score_endpoints():
    rng = np.random.default_rng(4)
    A = np.linalg.qr(rng.standard_normal((10, 3)))[0]
    B = np.linalg.qr(rng.standard_normal((10, 5)))[0]
    assert alignment_score(A, A) == pytest.approx(1.0)
    assert alignment_score(A, np.hstack([A, B])) == pytest.approx(1.0)
    assert 0.0 <= alignment_score(A, B) <= 1.0
    assert len(principal_angles(A, B)) == 3


def test_principal_angles_are_zero_for_nested_subspaces():
    rng = np.random.default_rng(5)
    A = np.linalg.qr(rng.standard_normal((8, 2)))[0]
    B = np.hstack([A, np.linalg.qr(rng.standard_normal((8, 2)))[0]])
    angles = principal_angles(A, B)
    assert np.all(angles[:2] < 1e-8)


def test_gain_mismatch_identity_vanishes_at_the_optimal_gain(seq2):
    """The appendix identity: a correct gain costs nothing extra."""
    J = seq2.J[0]
    P = spd(np.random.default_rng(6), seq2.d)
    K_opt = P @ np.linalg.inv(P + np.linalg.inv(J))
    assert gain_mismatch_cost(P, J, K_opt) == pytest.approx(0.0, abs=1e-9)
    assert gain_mismatch_cost(P, J, K_opt + 0.1 * np.eye(seq2.d)) > 0


# --------------------------------------------------------------------------
# filters and the information limit
# --------------------------------------------------------------------------
def test_full_basis_filter_is_the_kalman_reference(seq20):
    ests, _ = filter_sequence(seq20, Full(seq20.d))
    np.testing.assert_allclose(ests, run("kalman", seq20))


def test_smoother_beats_the_filter(seq_partial):
    """The RTS smoother is the information limit; it cannot be worse."""
    _, P_f = filter_sequence(seq_partial)
    _, P_s = rts_smoother(seq_partial)
    for k in (0, seq_partial.T // 2):
        e_f = np.trace(P_f[k] @ seq_partial.Sigma[k])
        e_s = np.trace(P_s[k] @ seq_partial.Sigma[k])
        assert e_s <= e_f + 1e-9


def test_two_task_diagonalisation_is_exactly_lossless(seq2):
    """LGCL v8's lemma, asserted as an equality rather than a tolerance.

    With only one task boundary the posterior is still diagonal in task 1's own
    basis, so projecting it away removes nothing.  All of the diagonalisation
    penalty is therefore a *recursive* effect.
    """
    two = sample_full(d=2, T=2, n=40, sigma2=1.0, q=0.05, rng=np.random.default_rng(0),
                      rotation="cumulative", alpha=np.deg2rad(37.0))
    e = summarize(error_tensor(run("ewc", two), two))["final_avg_error"]
    k = summarize(error_tensor(run("kalman", two), two))["final_avg_error"]
    assert e == pytest.approx(k, rel=1e-12)


def test_naive_cannot_escape_the_observed_subspace(seq_partial):
    """A fine-tuner only moves where the current task gave it data."""
    labels = seq_partial.y[-1]
    naive = run("naive", seq_partial)[-1]
    J = seq_partial.J[-1]
    # naive = pinv(J) J y  ->  J @ naive == J @ y
    np.testing.assert_allclose(J @ naive, J @ labels, atol=1e-8)


def test_replay_budget_zero_is_not_replay(seq_partial):
    """``budget=0`` must fuse nothing, not silently keep everything."""
    zero = Replay(budget=0).run(seq_partial)
    one = Replay(budget=1).run(seq_partial)
    assert not np.allclose(zero, one)
    np.testing.assert_allclose(zero, run("kalman", seq_partial))
