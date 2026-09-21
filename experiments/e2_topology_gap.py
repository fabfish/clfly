"""E2 — does the wiring cause the task geometry, and does the geometry cause the gap?

This is claim C1's *mechanism*, not just its symptom.  E3 found that EWC's
diagonal gap on wiring-derived tasks is ~45% of the oracle's error, against <1%
in LGCL's synthetic random-rotation family, and that the tasks there come out
near-orthogonal with disjoint supports.  Near-orthogonal tasks barely interfere,
so the obvious reading is: **the fly's modular wiring is what keeps the tasks
apart, and that is why the coordinate basis survives.**

That reading makes a falsifiable prediction, and this script tests it.  If the
wiring is responsible, then destroying the wiring while holding everything else
fixed -- same neurons, same assemblies, same support sizes, same seeds, same
budgets -- should scramble the assemblies together, make the task subspaces
overlap, and grow the gap.  Monotonicity along the null axis is the test.

The nulls are one operation at increasing strength, so the contrast is monotone in
a single interpretable quantity::

    real            the connectome
    swap0.1         double-edge swaps at 0.1 x edge count
    swap0.5         ... 0.5 x
    swap2           ... 2 x
    erdos_renyi     matched edge count, no structure at all

Each swap preserves in-degree, out-degree and edge count *exactly*, so the only
thing that changes is *who talks to whom*.  (An earlier version permuted the
target column instead; that lost 70% of the edges to summed collisions, which
confounded "rewired" with "sparser".  See :mod:`clfly.connectome.rewiring`.)

The claim is supported only if the gap grows along that order *and* the task
geometry degrades along it.  Either alone is not enough: a gap that grows without
the geometry moving has some other cause, and a geometry that moves without the
gap growing means the geometry does not matter after all.

    python -m experiments.e2_topology_gap --circuit-size 800 --seeds 1
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.connectome import annotate, circuits, graph, rewiring, tasks
from clfly.lgcl.bases import Diagonal, Full, Partition, alignment_score, random_partition
from clfly.lgcl.kalman import filter_sequence
from clfly.lgcl.methods import AnchoredFilter
from clfly.lgcl.model import error_tensor, summarize

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Nulls ordered from least to most structure destroyed.
TOPOLOGY_ORDER = rewiring.null_names()


def task_subspaces(seq, ranks):
    """The leading precision subspace of each task, strongest directions first."""
    out = []
    for k in range(seq.T):
        w, V = np.linalg.eigh(seq.J[k])
        out.append(V[:, np.argsort(w)[::-1][: ranks[k]]])
    return out


def geometry(seq, ranks) -> dict:
    """Summarise the task geometry -- the quantity the null should move.

    Four readings, because "interference" is easy to assert and hard to pin down,
    and because Phase 1 identified a *different* driver than overlap:

    ``consecutive_alignment`` / ``all_pairs_alignment``  mean ``cos^2`` between
        task precision subspaces.  High means tasks live where the last one did.
    ``effective_rank``  participation ratio ``1 / sum(w_i^2)`` of each task's
        normalised precision spectrum, averaged.  Equals the support size when the
        spectrum is flat and falls toward 1 as it concentrates, so
        ``flattening = effective_rank / rank`` measures how anisotropic a task is
        -- the variable Phase 1 found governs the diagonalisation penalty.
    ``top_eig_share``  share of each task's precision carried by its single
        strongest direction, the crudest anisotropy reading.
    """
    V = task_subspaces(seq, ranks)
    consec = [alignment_score(V[k], V[k + 1]) for k in range(len(V) - 1)]
    pairs = [alignment_score(V[j], V[k])
             for j in range(len(V)) for k in range(j + 1, len(V))]

    eff, top = [], []
    for k in range(seq.T):
        w = np.linalg.eigvalsh(seq.J[k])
        w = w[w > 1e-12 * max(1.0, float(w.max()))]
        if w.size == 0:
            continue
        w = w / w.sum()
        eff.append(1.0 / float(np.sum(w ** 2)))
        top.append(float(w.max()))
    mean_rank = float(np.mean(ranks))
    return {
        "consecutive_alignment": float(np.mean(consec)) if consec else float("nan"),
        "all_pairs_alignment": float(np.mean(pairs)) if pairs else float("nan"),
        "mean_rank": mean_rank,
        "mean_rank_fraction": mean_rank / seq.d,
        "effective_rank": float(np.mean(eff)) if eff else float("nan"),
        "flattening": float(np.mean(eff)) / mean_rank if eff and mean_rank else float("nan"),
        "top_eig_share": float(np.mean(top)) if top else float("nan"),
        "chance_alignment": mean_rank / seq.d,
    }


def gap_vs_oracle(seq, basis) -> float:
    oracle = summarize(error_tensor(filter_sequence(seq, Full(seq.d))[0], seq))
    got = summarize(error_tensor(AnchoredFilter(basis).run(seq), seq))
    ref = oracle["final_avg_error"]
    return (got["final_avg_error"] - ref) / ref if ref else float("nan")


def run(args) -> dict:
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    out = {"config": vars(args), "topologies": {}}

    for topology in args.topologies:
        print(f"  topology: {topology}")
        rows = []
        for seed in range(args.seed0, args.seed0 + args.seeds):
            circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
            rng = np.random.default_rng(seed)
            W0 = circ.net.weights()
            W = rewiring.apply_null(W0, topology, rng)
            moved = rewiring.swap_fraction(W0, W)
            print(f"      {topology:12} edges {W.nnz:,} (was {W0.nnz:,})  "
                  f"targets changed {moved:.3f}")
            circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())

            wt = tasks.build_tasks(circ, support_size=args.support, q=args.q, seed=seed)
            seq = wt.sequence

            # identical groupings across topologies, and one matched random control
            rng_b = np.random.default_rng(seed)
            bases = {
                "diagonal(EWC)": Diagonal(seq.d),
                "bio:cell_class": Partition(circ.labels["cell_class"]),
                "rand:cell_class": random_partition(circ.labels["cell_class"], rng_b),
            }
            row = {"geometry": geometry(seq, wt.ranks)}
            for name, b in bases.items():
                row[f"gap:{name}"] = gap_vs_oracle(seq, b)
            rows.append(row)
            print(f"    seed {seed} done ({time.time()-t0:.0f}s)  d={seq.d}")

        agg = {}
        for key in rows[0]:
            if key == "geometry":
                agg["geometry"] = {k: float(np.nanmean([r["geometry"][k] for r in rows]))
                                   for k in rows[0]["geometry"]}
            else:
                agg[key] = float(np.nanmean([r[key] for r in rows]))
        out["topologies"][topology] = agg

    out["timing_s"] = time.time() - t0
    return out


def report(results: dict) -> None:
    order = [t for t in TOPOLOGY_ORDER if t in results["topologies"]]
    print(f"\n{'topology':14} {'overlap':>9} {'chance':>8} {'over/ch':>8} "
          f"{'eff_rank':>9} {'flatten':>8} {'gap:EWC':>10} {'bio-rand':>9}")
    print("-" * 88)
    for t in order:
        a = results["topologies"][t]
        g = a["geometry"]
        ov = g["consecutive_alignment"]
        ch = g["chance_alignment"]
        print(f"{t:14} {ov:9.4f} {ch:8.4f} {ov/ch:8.3f} {g['effective_rank']:9.1f} "
              f"{g['flattening']:8.3f} {a['gap:diagonal(EWC)']:+10.4f} "
              f"{a['gap:bio:cell_class'] - a['gap:rand:cell_class']:+9.4f}")

    print("\nmonotonicity along the null order (real -> erdos_renyi):")
    readings = (
        ("task overlap", lambda a: a["geometry"]["consecutive_alignment"]),
        ("overlap/chance", lambda a: a["geometry"]["consecutive_alignment"]
            / a["geometry"]["chance_alignment"]),
        ("flattening", lambda a: a["geometry"]["flattening"]),
        ("EWC gap", lambda a: a["gap:diagonal(EWC)"]),
        ("bio - rand", lambda a: a["gap:bio:cell_class"] - a["gap:rand:cell_class"]),
    )
    for label, getter in readings:
        vals = [getter(results["topologies"][t]) for t in order]
        rising = all(b >= a - 1e-9 for a, b in zip(vals, vals[1:]))
        shown = "  ".join(f"{v:+.4f}" for v in vals)
        print(f"  {label:16} {shown}   monotone={'YES' if rising else 'no'}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--support", type=int, default=80)
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--topologies", default=",".join(TOPOLOGY_ORDER))
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    args.topologies = tuple(t for t in args.topologies.split(",") if t)

    results = run(args)
    report(results)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(results, indent=1, default=str))
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
