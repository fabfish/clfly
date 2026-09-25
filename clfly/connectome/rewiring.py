"""Null topologies: a monotone family for "how much wiring structure is left?"

A gap measured on the connectome means nothing without a null that keeps the
things that are *not* under test.  The family here is deliberately built from
**one operation applied at increasing strength**, so the contrast is monotone in a
single interpretable quantity rather than being a comparison between unrelated
constructions.

The operation is the classic **double-edge swap**: pick two edges ``(a,b)`` and
``(c,d)`` and replace them with ``(a,d)`` and ``(c,b)``.  That preserves in-degree
*and* out-degree exactly -- ``a`` and ``c`` each keep their outgoing count, ``b``
and ``d`` each keep their incoming count -- while moving *who talks to whom*.  A
duplicate guard rejects swaps that would collide with an existing edge, so the
edge count is preserved exactly too.

``apply_null`` therefore takes::

    real            the connectome, untouched
    swap<f>         f x m double-edge swaps, m = edge count
    erdos_renyi     matched edge count, no structure at all

**Why not a target-column permutation.** An earlier version of this module
randomised the post-synaptic target column globally.  That is a tempting null --
out-degree exactly preserved, one line of code -- and it is wrong here: with
86,443 edges over 1,307 neurons the permutation lands many synapses on pairs that
already exist, and rebuilding the graph sums those duplicates.  The result lost
**70% of the edges** (86,443 -> 25,594), so the "rewired" condition was also the
"much sparser" condition and no gap difference could be attributed to topology.
A collision-free swap does the same job without changing the graph's density.
"""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp


def _as_coo(W: sp.spmatrix):
    C = W.tocoo()
    return (C.row.astype(np.int64).copy(), C.col.astype(np.int64).copy(),
            C.data.astype(np.float64).copy())


def _rebuild(rows, cols, data, n):
    """Assemble CSR, summing any duplicate (row, col) pairs that arose.

    Swaps are duplicate-guarded so this should be a no-op; it is kept as a
    safety net and its effect is asserted in the tests.
    """
    M = sp.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
    M.sum_duplicates()
    return M


def double_edge_swap(W: sp.spmatrix, n_swaps: int | None = None,
                     rng: np.random.Generator | None = None,
                     max_tries_factor: int = 20) -> sp.csr_matrix:
    """``n_swaps`` double-edge swaps preserving in-degree, out-degree and edge count.

    ``n_swaps`` defaults to the edge count ``m``.  Failed swaps (self-loops,
    duplicate edges) are skipped rather than retried indefinitely, so the achieved
    count is at most ``n_swaps``; the caller should check how much actually moved
    via :func:`swap_fraction` rather than assuming.
    """
    rng = rng or np.random.default_rng(0)
    rows, cols, data = _as_coo(W)
    n = W.shape[0]
    m = len(rows)
    if m < 2:
        return W.tocsr()
    n_swaps = m if n_swaps is None else int(n_swaps)

    present = set(zip(rows.tolist(), cols.tolist()))
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

    return _rebuild(rows, cols, data, n)


def erdos_renyi(n: int, n_edges: int, rng: np.random.Generator,
                signed: bool = True) -> sp.csr_matrix:
    """Random graph with the same neuron count and edge count."""
    total = n * (n - 1)
    n_edges = min(int(n_edges), total)
    flat = rng.choice(total, size=n_edges, replace=False)
    rows = flat // (n - 1)
    cols = flat % (n - 1)
    cols = np.where(cols >= rows, cols + 1, cols)
    data = np.ones(n_edges, dtype=np.float64)
    if signed:
        data = data * rng.choice([-1.0, 1.0], size=n_edges)
    return _rebuild(rows, cols, data, n)


def swap_fraction(W_before: sp.spmatrix, W_after: sp.spmatrix) -> float:
    """Share of edges that changed target -- how much a null actually moved.

    Worth reporting for every null: a swap *count* is not a mixing guarantee, and
    a null that barely moved would make the connectome look special for no reason.
    """
    A = W_before.tocoo()
    B = W_after.tocoo()
    before = set(zip(A.row.tolist(), A.col.tolist()))
    after = set(zip(B.row.tolist(), B.col.tolist()))
    return 1.0 - len(before & after) / max(1, len(before))


#: Swap strengths, as multiples of the edge count.  Chosen to span "barely
#: touched" to "thoroughly mixed" so a monotone response can actually be seen.
SWAP_STRENGTHS = (0.1, 0.5, 2.0)


def null_names(strengths=SWAP_STRENGTHS) -> tuple[str, ...]:
    return ("real", *(f"swap{s:g}" for s in strengths), "erdos_renyi")


def random_targets(W: sp.spmatrix, fraction: float,
                   rng: np.random.Generator, max_tries_factor: int = 40) -> sp.csr_matrix:
    """Replace the target of a ``fraction`` of the edges with a guarded uniformly random neuron.

    **The second null family, and the reason it exists.** Swaps preserve in-degree *and* out-degree, and `e209`/`e211`
    measured that they therefore cannot move the tasks' alignment: across strengths 8 to 1024 (a 128× range) the swap
    family stays at 0.65–1.72× chance while the edge-count-matched Erdős–Rényi family sits at 4.89–5.23×, so the
    interval between those two regimes is **not reachable by rewiring harder**. This operation is the knob that can
    place alignment anywhere in between: it keeps every neuron's **out-degree exactly** and the **edge count exactly**,
    and it destroys the *pairing* structure much faster than a swap, because the in-degree is free to move.

    The guard is what makes it different from the version this module's docstring records as a failure. Randomising the
    whole target column *without* a guard made 70% of the edges land on pairs that already existed, so rebuilding summed
    them and the "rewired" condition was also the "sparser" one (86,443 → 25,594 edges). Here a candidate target that
    already exists is rejected and redrawn, exactly as a swap rejects a collision, so the edge count is preserved and
    `swap_fraction` is a meaningful report of how far the graph moved.

    ``fraction`` is the share of edges touched, so ``alloy0`` is the untouched connectome and ``alloy1`` is every edge.
    """
    if not 0.0 <= fraction <= 1.0:
        # a fraction outside the unit interval is a caller error and not a zero: the first version of this
        # function silently returned the connectome for a negative fraction, which a test caught
        raise ValueError(f"fraction must be in [0, 1], got {fraction!r}")
    rows, cols, data = _as_coo(W)
    m = rows.shape[0]
    n = W.shape[0]
    n_touch = min(int(round(fraction * m)), m)
    if n_touch <= 0:
        return W.tocsr()
    existing = set(zip(rows.tolist(), cols.tolist()))
    idx = rng.choice(m, size=n_touch, replace=False)
    for i in idx:
        s = int(rows[i])
        for _ in range(max_tries_factor):
            t = int(rng.integers(0, n - 1))
            if t >= s:                     # uniform over neurons other than the source, so no self-loop
                t += 1
            if (s, t) in existing:
                continue
            existing.discard((s, int(cols[i])))
            existing.add((s, t))
            cols[i] = t
            break
        # a source whose targets are nearly exhausted keeps this edge as it is: the guard is what preserves the edge
        # count, and the cost of that is a few untouched edges on the densest sources, reported by `swap_fraction`
    return _rebuild(rows, cols, data, n)


def apply_null(W: sp.spmatrix, topology: str, rng: np.random.Generator) -> sp.csr_matrix:
    """Apply a named null topology.

    The single entry point for every topology contrast in the project, so an
    experiment cannot accidentally use a different null than the one it names.
    """
    if topology == "real":
        return W.tocsr()
    if topology.startswith("swap"):
        frac = float(topology[4:])
        return double_edge_swap(W, n_swaps=int(round(frac * W.nnz)), rng=rng)
    if topology.startswith("alloy"):
        return random_targets(W, float(topology[5:]), rng)
    if topology == "erdos_renyi":
        return erdos_renyi(W.shape[0], W.nnz, rng, signed=True)
    raise ValueError(
        f"unknown topology {topology!r}; expected 'real', 'swap<frac>', 'alloy<frac>' or 'erdos_renyi'"
    )
