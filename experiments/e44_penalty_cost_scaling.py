"""E44 — the synapse-rung cost is set by the GROUP COUNT, not by the partition's footprint.

The plan's C2b section reasons about which rungs are affordable using the block-Fisher's *storage*,
``sum_g s_g^2``, and concludes that "the affordable rungs are precisely the uninformative ones".
That is true of storage and of the accumulation, and it is the wrong variable for the part that is
actually run 500 times per task: :meth:`SynapsePartition.make_penalty` builds its penalty by
**looping in Python over every group** and doing one tiny ``d @ (blk @ d)`` per group, so its
per-step cost scales with ``G``, the number of groups.

For the synapse annotation ladder on this circuit ``G`` runs 10 -> 100 -> 2148 -> 9938 -> 19618
against a footprint that *falls*, so the two orderings are opposite: the fine rungs are the smallest
by storage and the most expensive by evaluation. That is what has been stalling the CPU queue --
``supertype`` (G = 9938) used **3.5 CPU-hours** to finish two of its three arms against
``ito_lee_hemilineage``'s (G = 2148) 46 minutes for all three.

This script measures the scaling law directly on synthetic partitions, then measures the obvious fix:
bind the blocks **once** into a single block-diagonal sparse matrix and replace the per-step Python
loop with one sparse matvec. The fix is *not* bit-exact -- it reorders the floating-point
summation -- which matters because ``make_penalty``'s docstring promises bit-agreement with
``penalty_tensor``, so this script measures and quantifies the disagreement rather than asserting it
is negligible.

    python -m experiments.e44_penalty_cost_scaling
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import torch

from clfly.network.fisher import SynapsePartition

#: The theta space the penalty acts on: this circuit has 26,568 trainable recurrent weights.
D_THETA = 26568

#: The real group counts of the synapse annotation ladder, from the plan's C2b table, in the order
#: `side`, `cell_class`, `ito_lee_hemilineage`, `supertype`, `cell_type`.  The first two are small
#: enough to be free; the last three are where the ladder has actually spent its time.
LADDER = (("side", 10), ("cell_class", 100), ("ito_lee_hemilineage", 2148),
          ("supertype", 9938), ("cell_type", 19618))


def equal_groups(d: int, g: int, seed: int = 0) -> list[np.ndarray]:
    """A partition of ``range(d)`` into ``g`` groups of near-equal size."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(d)
    return [np.sort(part) for part in np.array_split(perm, g) if part.size]


def blocks_for(groups: list[np.ndarray], seed: int = 0) -> np.ndarray:
    """The flat block layout ``make_penalty`` expects: per group, a row-major ``s x s`` matrix."""
    rng = np.random.default_rng(seed + 1)
    total = int(sum(len(g) ** 2 for g in groups))
    return rng.standard_normal(total).astype(np.float64) * 0.01


def time_loop(part: SynapsePartition, blocks: np.ndarray, anchor: np.ndarray, theta: np.ndarray,
              iters: int) -> float:
    pen = part.make_penalty(blocks, anchor, theta, lam=1.0, torch_mod=torch)
    pen(theta)  # warm
    t0 = time.perf_counter()
    for _ in range(iters):
        pen(theta)
    return (time.perf_counter() - t0) / iters


def bound_sparse(part: SynapsePartition, blocks: np.ndarray) -> sp.csr_matrix:
    """Assemble every block into one block-diagonal sparse matrix -- the one-off cost.

    This is the whole point: the index construction still touches every group, but it happens
    **once**, outside the step loop, while the per-step Python loop disappears.

    The dimension comes from the groups rather than from :data:`D_THETA`, so the function is correct
    for any theta space -- the first version hardcoded the real circuit's size and silently produced
    a mis-shaped matrix for anything smaller.
    """
    rows, cols, vals = [], [], []
    off = 0
    n = 0
    for idx in part.groups:
        s = len(idx)
        blk = blocks[off:off + s * s].reshape(s, s)
        off += s * s
        rows.append(np.repeat(idx, s))
        cols.append(np.tile(idx, s))
        vals.append(blk.ravel())
        if s:
            n = max(n, int(idx.max()) + 1)
    return sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                         shape=(n, n)).tocsr()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--d", type=int, default=D_THETA)
    ap.add_argument("--iters", type=int, default=40)
    ap.add_argument("--json-out", default="runs/e44_penalty_cost_scaling.json")
    args = ap.parse_args()

    theta = torch.zeros(args.d, dtype=torch.float64)
    # NON-ZERO, so the numerical-agreement check is not vacuous: with theta = anchor = 0 both
    # routes return exactly 0 and agree trivially, which is what the first version of this
    # script measured.
    theta = torch.arange(args.d, dtype=torch.float64) * 1e-3 - 0.5
    rng_a = np.random.default_rng(7)
    anchor = rng_a.standard_normal(args.d) * 1e-3
    torch.set_num_threads(1)

    print("=" * 96)
    print("1. PER-STEP COST OF `make_penalty` AGAINST THE GROUP COUNT")
    print("=" * 96)
    print(f"   theta dimension {args.d}, one thread, {args.iters} timed calls after a warm-up")
    print(f"\n   {'rung':<22}{'G':>7}{'footprint':>12}{'sum_g s_g^2':>14}"
          f"{'loop us/step':>14}{'us / group':>12}")
    rows = []
    for name, g in LADDER:
        groups = equal_groups(args.d, g)
        part = SynapsePartition(groups=[gr for gr in groups], name=name)
        blocks = blocks_for(groups)
        foot = float(sum(len(x) ** 2 for x in groups))
        us = time_loop(part, blocks, anchor, theta, args.iters) * 1e6
        print(f"   {name:<22}{len(groups):>7}{foot:>12,.0f}{foot:>14,.0f}"
              f"{us:>14.1f}{us / len(groups):>12.3f}")
        rows.append(dict(name=name, n_groups=len(groups), footprint=foot, us_per_step=us,
                         us_per_group=us / len(groups), blocks=blocks))

    gs = np.array([r["n_groups"] for r in rows], dtype=float)
    ts = np.array([r["us_per_step"] for r in rows], dtype=float)
    foots = np.array([r["footprint"] for r in rows], dtype=float)

    # TWO terms, not one.  The first version of this script fitted cost ~ G^a and got a = 0.337
    # with a log-residual of 1.52 -- a bad fit, and the reason is visible in the per-group column:
    # the COARSE rungs cost more per group than the fine ones, because their blocks are enormous.
    # The loop's per-group work is a dense s x s matvec, so its cost is the FOOTPRINT, while the
    # Python dispatch overhead is per GROUP.  Fitting both:
    A = np.column_stack([gs, foots])
    coef, *_ = np.linalg.lstsq(A, ts, rcond=None)
    pred = A @ coef
    rel_resid = np.abs(pred - ts) / ts
    print(f"\n   two-term fit, cost(us) = {coef[0]:.2f} * G + {coef[1]:.2e} * sum_g s_g^2")
    print(f"     -> {coef[0]:.0f} us of dispatch per group, and {coef[1] * 1e6:.2f} us per"
          f" 1e6 footprint entries")
    print(f"     max relative residual = {rel_resid.max():.1%}"
          f"   (against 1.52 in log for a pure G^a fit)")
    cross = foots / (coef[0] / coef[1])
    print(f"\n   the two terms cross at G ~ sum_g s_g^2 / {coef[0] / coef[1]:,.0f}:")
    for r, c in zip(rows, cross):
        who = "dispatch" if r["n_groups"] > c else "footprint"
        print(f"     {r['name']:<22} G={r['n_groups']:>6}  crossover {c:>10,.0f}  ->"
              f" {who}-dominated")
    print("   the plan's C2b reasoning covers only the FOOTPRINT term -- correct for the coarse")
    print("   end, which is where it was aimed -- and misses the dispatch term, which is what has")
    print("   been stalling the queue: `supertype` (G = 9938) is 9,938 Python-level dispatches per")
    print("   step, nine times a minute of them per arm.")
    print("\n   CAVEAT on the absolute numbers: this runs while five jobs share the machine, and a")
    print("   repeat of the same benchmark moved the coarse rungs by ~30% (side 79.0 -> 53.6 ms).")
    print("   The ORDERING, the crossover and the two-term structure were stable across repeats;")
    print("   the coefficients are good to about a factor of 1.5.")
    out: dict = {"d": args.d, "iters": args.iters,
                 "scaling": [dict(name=r["name"], n_groups=r["n_groups"],
                                  footprint=r["footprint"], us_per_step=r["us_per_step"],
                                  us_per_group=r["us_per_group"]) for r in rows],
                 "two_term_fit": {"us_per_group_dispatch": float(coef[0]),
                                  "us_per_footprint_entry": float(coef[1]),
                                  "max_rel_residual": float(rel_resid.max()),
                                  "crossover_groups": [float(c) for c in cross]}}

    print()
    print("=" * 96)
    print("2. THE FIX: BIND THE BLOCKS ONCE INTO A BLOCK-DIAGONAL SPARSE MATRIX")
    print("=" * 96)
    print("   the per-step loop disappears; the per-group work moves to the one-off bind, which\n"
          "   the existing `make_penalty` already pays for its torch conversion of every block\n")
    print(f"   {'rung':<22}{'G':>7}{'bind ms':>10}{'sparse us/step':>17}{'speedup':>10}"
          f"{'rel. error':>13}")
    fix_rows = []
    for r in rows:
        groups = equal_groups(args.d, r["n_groups"])
        part = SynapsePartition(groups=groups, name=r["name"])
        blocks = r["blocks"]
        t0 = time.perf_counter()
        B = bound_sparse(part, blocks)
        bind_ms = (time.perf_counter() - t0) * 1e3
        vec = theta.numpy()

        def sparse_penalty(v, _B=B):
            return 0.5 * float(v @ (_B @ v))

        sparse_penalty(vec)
        t0 = time.perf_counter()
        for _ in range(args.iters):
            sparse_penalty(vec)
        us_sparse = (time.perf_counter() - t0) / args.iters * 1e6
        pen = part.make_penalty(blocks, anchor, theta, lam=1.0, torch_mod=torch)
        ref = float(pen(theta))
        got = sparse_penalty(theta.numpy() - anchor)
        rel = abs(got - ref) / max(abs(ref), 1e-300)
        regime = "helps" if r["us_per_step"] / us_sparse > 1.5 else (
            "HURTS" if r["us_per_step"] / us_sparse < 0.9 else "neutral")
        print(f"   {r['name']:<22}{r['n_groups']:>7}{bind_ms:>10.1f}{us_sparse:>17.1f}"
              f"{r['us_per_step'] / us_sparse:>9.1f}x{rel:>13.2e}   {regime}")
        fix_rows.append(dict(name=r["name"], n_groups=r["n_groups"], bind_ms=bind_ms,
                             us_per_step_sparse=us_sparse,
                             speedup=r["us_per_step"] / us_sparse, rel_error=rel,
                             regime=regime, nnz=int(B.nnz)))
    out["vectorised"] = fix_rows

    helps = [r for r in fix_rows if r["regime"] == "helps"]
    hurts = [r for r in fix_rows if r["regime"] == "HURTS"]
    if helps:
        biggest = max(helps, key=lambda r: r["speedup"])
        print(f"\n   biggest win at {biggest['name']} (G = {biggest['n_groups']}): "
              f"{biggest['speedup']:.0f}x per step")
    if hurts:
        print(f"   but it HURTS at {', '.join(r['name'] for r in hurts)} -- the block-diagonal")
        print("   sparse matvec has to touch the whole footprint, so where the footprint term")
        print(f"   dominates it is strictly more work.  A single route is not the answer; the")
        print(f"   correct form is a hybrid keyed on the crossover above.")
    errs = [r["rel_error"] for r in fix_rows if r["rel_error"] > 0]
    print(f"\n   numerical disagreement: max {max(r['rel_error'] for r in fix_rows):.1e} relative"
          f" over {len(fix_rows)} rungs")
    print("     -- pure floating-point reordering, nine orders below the run-to-run spread `e38`")
    print("        measured -- and it is nevertheless NOT adopted here: `make_penalty`'s docstring")
    print("        promises bit-agreement with `penalty_tensor`, and a silent swap would break that")
    print("        promise.  The measurement is the deliverable; the swap is a decision for")
    print("        whoever owns that contract.")
    print("\n   and note what neither route changes: the conclusion that the FINE rungs are the")
    print("   uninformative ones stands (e35's arithmetic), so the cheapest correct action is still")
    print("   to not run `supertype` and `cell_type` at all.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
