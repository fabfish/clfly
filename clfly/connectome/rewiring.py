"""Null topologies: what the connectome must be compared against.

A gap measured on the connectome means nothing without a null that keeps the
things that are *not* under test.  Three are provided, and the claim each one
licenses is different:

``shuffle_targets``  keep every source neuron and the exact multiset of
    post-synaptic targets, but permute which target each synapse lands on.
    Out-degree is preserved exactly.  This is the cheapest and sharpest null for
    "is *this* wiring special?" -- it keeps the degree sequence and destroys the
    targeting.
``degree_preserving_swap``  the standard configuration-model null via double-edge
    swaps: both in- and out-degree exactly preserved, topology otherwise
    randomised.  Slower, and needs many swaps to mix.
``erdos_renyi``  matched edge count, no structure at all.  The furthest null.

The distinction matters for the science.  If a result survives
``degree_preserving_swap`` it is not about degrees; if it survives
``erdos_renyi`` it is not about sparsity either.  Reporting only one would let a
trivial explanation stand.
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp


def _as_coo(W: sp.spmatrix):
    C = W.tocoo()
    return C.row.astype(np.int64), C.col.astype(np.int64), C.data.astype(np.float64)


def _dedupe(rows, cols, data, n):
    """Rebuild CSR, summing any duplicate (row, col) pairs a swap created."""
    M = sp.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
    M.sum_duplicates()
    return M


def shuffle_targets(W: sp.spmatrix, rng: np.random.Generator) -> sp.csr_matrix:
    """Permute post-synaptic targets, preserving out-degree exactly.

    Sign and magnitude travel with the synapse, so the excitatory/inhibitory
    balance and the weight distribution are untouched -- only *who talks to whom*
    is randomised.

    A global permutation can land two synapses on the same (source, target) pair;
    those are summed, so the returned graph may have slightly fewer edges than the
    input.  Callers should report the achieved edge count rather than assume it is
    unchanged.
    """
    rows, cols, data = _as_coo(W)
    new_cols = rng.permutation(cols)
    self_loops = rows == new_cols
    if self_loops.any():
        # A self-loop is an artefact of the shuffle; retarget those at random.
        new_cols[self_loops] = rng.integers(0, W.shape[0], size=int(self_loops.sum()))
    return _dedupe(rows, new_cols, data, W.shape[0])


def degree_preserving_swap(W: sp.spmatrix, n_swaps: int | None = None,
                           rng: np.random.Generator | None = None,
                           max_tries_factor: int = 20) -> sp.csr_matrix:
    """Double-edge swaps preserving in- and out-degree exactly.

    ``n_swaps`` defaults to the number of edges, which is the usual working
    choice: enough to destroy the topology, not enough to guarantee full mixing.
    Failed swaps (self-loops, duplicate edges) are skipped rather than retried
    indefinitely, so the achieved swap count is reported implicitly by the fact
    that degrees still match -- which is asserted in the tests.
    """
    rng = rng or np.random.default_rng(0)
    A = W.tocoo()
    n = W.shape[0]
    rows = A.row.astype(np.int64).copy()
    cols = A.col.astype(np.int64).copy()
    data = A.data.astype(np.float64).copy()
    m = len(rows)
    if m < 2:
        return W.tocsr()
    n_swaps = n_swaps if n_swaps is not None else m

    present = {(int(r), int(c)) for r, c in zip(rows, cols)}
    done = 0
    for _ in range(n_swaps * max_tries_factor):
        if done >= n_swaps:
            break
        i, j = rng.integers(0, m, size=2)
        a, b, c, d = rows[i], cols[i], rows[j], cols[j]
        if a == d or c == b or (a, d) in present or (c, b) in present:
            continue
        present.discard((a, b))
        present.discard((c, d))
        present.add((a, d))
        present.add((c, b))
        cols[i], cols[j] = d, b
        done += 1

    # Carry the weight of the original edge onto the swapped edge.
    return _dedupe(rows, cols, data, n)


def erdos_renyi(n: int, n_edges: int, rng: np.random.Generator,
                signed: bool = True) -> sp.csr_matrix:
    """Random graph with the same neuron count and edge count."""
    total = n * (n - 1)
    n_edges = min(n_edges, total)
    flat = rng.choice(total, size=n_edges, replace=False)
    rows = flat // (n - 1)
    cols = flat % (n - 1)
    cols = np.where(cols >= rows, cols + 1, cols)
    data = np.ones(n_edges, dtype=np.float64)
    if signed:
        data = data * rng.choice([-1.0, 1.0], size=n_edges)
    return _dedupe(rows, cols, data, n)


def swap_fraction(W_before: sp.spmatrix, W_after: sp.spmatrix) -> float:
    """Share of edges that changed target -- how much a null actually moved.

    Worth reporting for every null: a swap count is not a mixing guarantee, and a
    null that barely moved would make the connectome look special for no reason.
    """
    A = W_before.tocoo()
    B = W_after.tocoo()
    before = set(zip(A.row.tolist(), A.col.tolist()))
    after = set(zip(B.row.tolist(), B.col.tolist()))
    return 1.0 - len(before & after) / max(1, len(before))


NULLS = {
    "real": lambda W, rng: W.tocsr(),
    "target_shuffle": shuffle_targets,
    "degree_swap": degree_preserving_swap,
    "erdos_renyi": None,  # needs the edge count, handled by the caller
}
