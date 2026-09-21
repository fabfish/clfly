"""Tests for the null topologies.

`rewiring` is load-bearing for every topology contrast in the project, and its
first implementation was wrong in a way that produced plausible numbers: a global
permutation of the target column lost 70% of the edges to summed collisions, so
the "rewired" condition was also the "sparser" condition.  That class of bug is
what these tests exist to catch, so the edge count is asserted explicitly rather
than assumed.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.sparse as sp

from clfly.connectome import rewiring


def _graph(n=60, m=300, seed=0, alpha=1.5):
    """A sparse signed graph with a *power-law* out-degree distribution.

    The tail matters.  Collisions under a global target permutation scale like
    ``sum(d_i^2) / (2n)``, so a graph with uniform out-degrees barely collides
    however dense it is -- and the effect this module's docstring warns about
    would not reproduce.  Real connectomes are heavy-tailed (the circuit used in
    ``e2`` has max out-degree in the thousands against a mean of 66), which is
    exactly why the rejected null lost 70% of the edges there.
    """
    rng = np.random.default_rng(seed)
    p = (np.arange(1, n + 1) ** -alpha)
    p /= p.sum()
    rows = rng.choice(n, size=m, p=p)
    cols = rng.integers(0, n, size=m)
    rows, cols = rows[rows != cols], cols[rows != cols]
    data = rng.choice([-1.0, 1.0], size=len(rows)) * rng.integers(1, 8, size=len(rows))
    W = sp.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
    W.sum_duplicates()
    return W


def test_swap_preserves_degrees_and_edge_count_exactly():
    """The invariant the whole contrast rests on."""
    W = _graph()
    for frac in (0.1, 0.5, 2.0):
        out = rewiring.double_edge_swap(W, n_swaps=int(frac * W.nnz),
                                        rng=np.random.default_rng(1))
        assert out.nnz == W.nnz, f"edge count changed at frac={frac}"
        np.testing.assert_array_equal(np.diff(out.indptr), np.diff(W.indptr))
        np.testing.assert_array_equal(np.diff(out.tocsc().indptr),
                                      np.diff(W.tocsc().indptr))


def test_swap_actually_moves_targets_and_more_swaps_move_more():
    W = _graph()
    moved = [rewiring.swap_fraction(
        W, rewiring.double_edge_swap(W, n_swaps=int(f * W.nnz),
                                     rng=np.random.default_rng(2)))
        for f in (0.1, 0.5, 2.0)]
    assert moved[0] > 0.0
    assert moved[0] < moved[1] < moved[2]
    assert moved[-1] > 0.5


def test_global_target_permutation_would_lose_edges():
    """Regression: the rejected null must be shown to be broken, not just unused.

    If this ever stops losing edges, the reasoning in `rewiring`'s docstring has
    gone stale and the alternative should be reconsidered.
    """
    W = _graph()
    rows, cols, data = rewiring._as_coo(W)
    shuffled = rewiring._rebuild(rows, np.random.default_rng(0).permutation(cols), data, W.shape[0])
    assert shuffled.nnz < 0.9 * W.nnz


def test_apply_null_real_is_the_identity():
    W = _graph()
    out = rewiring.apply_null(W, "real", np.random.default_rng(0))
    assert (out != W).nnz == 0


def test_apply_null_rejects_unknown_names():
    W = _graph()
    with pytest.raises(ValueError, match="unknown topology"):
        rewiring.apply_null(W, "degree_swap", np.random.default_rng(0))


def test_erdos_renyi_matches_edge_count_and_is_signed():
    W = _graph()
    out = rewiring.apply_null(W, "erdos_renyi", np.random.default_rng(0))
    assert out.nnz == W.nnz
    assert (out.data > 0).any() and (out.data < 0).any()
    assert (out.diagonal() == 0).all()


def test_null_names_are_ordered_by_swap_strength():
    names = rewiring.null_names()
    assert names[0] == "real" and names[-1] == "erdos_renyi"
    fracs = [float(n[4:]) for n in names if n.startswith("swap")]
    assert fracs == sorted(fracs)
