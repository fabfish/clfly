from __future__ import annotations

import numpy as np
import pytest
import scipy.sparse as sp

from clfly.connectome import rewiring as rw


def toy(n: int = 60, m: int = 200, seed: int = 0) -> sp.csr_matrix:
    """A small directed graph with no self-loops and no duplicated edges."""
    rng = np.random.default_rng(seed)
    flat = rng.choice(n * (n - 1), size=m, replace=False)
    rows = flat // (n - 1)
    cols = flat % (n - 1)
    cols = np.where(cols >= rows, cols + 1, cols)
    return sp.csr_matrix((np.ones(m), (rows, cols)), shape=(n, n))


def out_degrees(W) -> np.ndarray:
    return np.asarray(W.sum(axis=1)).ravel()


def test_the_alloy_keeps_the_edge_count_and_every_out_degree_at_every_fraction():
    """The property the module's own docstring records as a failure of the unguarded version: randomising targets
    without a guard lost 70% of the edges to summed collisions, so the "rewired" condition was also the "sparser"
    one. Out-degree is held exactly here, and the edge count with it."""
    W = toy()
    rng = np.random.default_rng(1)
    for frac in (0.0, 0.25, 0.5, 1.0):
        A = rw.apply_null(W, f"alloy{frac:g}", rng)
        assert A.nnz == W.nnz, (frac, A.nnz, W.nnz)
        assert np.array_equal(out_degrees(A), out_degrees(W)), frac
        C = A.tocoo()
        assert int((C.row == C.col).sum()) == 0, frac


def test_fraction_zero_is_the_connectome_untouched_and_one_moves_almost_every_edge():
    """`alloy0` must be an identity, and `alloy1` must move nearly every edge -- the small shortfall is the guard
    doing its job on sources whose targets are nearly exhausted, which `swap_fraction` is the report of."""
    W = toy()
    rng = np.random.default_rng(2)
    assert (rw.apply_null(W, "alloy0", rng) != W).nnz == 0
    moved = rw.swap_fraction(W, rw.apply_null(W, "alloy1", rng))
    assert moved > 0.9, moved


def test_the_guard_bites_on_a_dense_graph_and_the_edge_count_still_holds():
    """Where most pairs already exist the guard rejects a candidate and redraws it, so the realised fraction can
    fall short of the requested one -- and the test's point is that the shortfall shows up in `swap_fraction` while
    the edge count stays exact. Without the guard this is the case that loses edges."""
    n = 12
    W = sp.csr_matrix((np.ones(n * (n - 1)), ([r for r in range(n) for _ in range(n - 1)],
                                              [c for r in range(n) for c in range(n) if c != r])),
                      shape=(n, n))
    rng = np.random.default_rng(3)
    A = rw.apply_null(W, "alloy1", rng)
    assert A.nnz == W.nnz
    assert rw.swap_fraction(W, A) < 1.0, "a complete graph has no free target, so nothing can move"


def test_an_unknown_topology_name_is_refused_and_the_swap_family_is_unchanged():
    """`apply_null` is the single entry point for every contrast in the project, so a name it does not know must
    raise rather than silently fall back to something -- and the new branch must not disturb the old ones."""
    W = toy()
    rng = np.random.default_rng(4)
    # `alloy-1` parses as a fraction and is nonsense rather than an unknown name, so it raises a ValueError too --
    # the point is that no unknown spelling is quietly treated as one of the family
    for name in ("alloy-1", "rewire0.5", "swap"):
        with pytest.raises(ValueError):
            rw.apply_null(W, name, rng)
    swap = rw.apply_null(W, "swap2", rng)
    assert swap.nnz == W.nnz
    assert rw.swap_fraction(W, swap) > 0.5
    assert rw.null_names() == ("real", "swap0.1", "swap0.5", "swap2", "erdos_renyi")
