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

from clfly.bench.oracle import paired_excess, task_geometry
from clfly.connectome import annotate, circuits, graph, rewiring, tasks
from clfly.lgcl.bases import Diagonal, Partition, random_partition

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Nulls ordered from least to most structure destroyed.
TOPOLOGY_ORDER = rewiring.null_names()


def run(args) -> dict:
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    out = {"config": vars(args), "topologies": {}}

    for topology in args.topologies:
        print(f"  topology: {topology}")
        # The circuit and its rewiring belong to the *topology*, not the seed.
        # Extracting inside the seed loop would give each seed a different
        # rewired graph, so the seeds would not be replicates of the same condition.
        circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
        W0 = circ.net.weights()
        W = rewiring.apply_null(W0, topology, np.random.default_rng(args.seed0))
        print(f"      edges {W.nnz:,} (was {W0.nnz:,})  "
              f"targets changed {rewiring.swap_fraction(W0, W):.3f}")
        circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())

        seqs, ranks = [], []
        for seed in range(args.seed0, args.seed0 + args.seeds):
            wt = tasks.build_tasks(circ, support_size=args.support, q=args.q, seed=seed)
            seqs.append(wt.sequence)
            ranks.append(wt.ranks)

        # identical groupings across topologies, and one matched random control
        rng_b = np.random.default_rng(args.seed0)
        bases = {
            "diagonal(EWC)": Diagonal(seqs[0].d),
            "bio:cell_class": Partition(circ.labels["cell_class"]),
            "rand:cell_class": random_partition(circ.labels["cell_class"], rng_b),
        }
        print(f"    built {len(seqs)} task sets ({time.time()-t0:.0f}s)  d={seqs[0].d}")

        agg = {"geometry": {k: float(np.mean([task_geometry(s, r)[k]
                                              for s, r in zip(seqs, ranks)]))
                            for k in task_geometry(seqs[0], ranks[0])}}
        for name, b in bases.items():
            agg[name] = paired_excess(seqs, b)
        out["topologies"][topology] = agg

    out["timing_s"] = time.time() - t0
    return out


def report(results: dict) -> None:
    order = [t for t in TOPOLOGY_ORDER if t in results["topologies"]]
    print(f"\n{'topology':14} {'overlap':>8} {'over/ch':>8} {'flatten':>8} "
          f"{'excess:EWC':>11} {'sem':>8} {'gap(sd)':>13} {'bio-rand':>10} {'sem':>8}")
    print("-" * 100)
    for t in order:
        a = results["topologies"][t]
        g = a["geometry"]
        bio, rnd = a["bio:cell_class"], a["rand:cell_class"]
        delta = bio["excess_mean"] - rnd["excess_mean"]
        sem = float(np.hypot(bio["excess_sem"], rnd["excess_sem"]))
        print(f"{t:14} {g['consecutive_alignment']:8.4f} "
              f"{g['consecutive_alignment']/g['chance_alignment']:8.3f} "
              f"{g['flattening']:8.3f} {a['diagonal(EWC)']['excess_mean']:+11.5f} "
              f"{a['diagonal(EWC)']['excess_sem']:8.5f} "
              f"{a['diagonal(EWC)']['gap_mean']:+7.3f}"
              f"({a['diagonal(EWC)']['gap_sd']:.3f}) "
              f"{delta:+10.5f} {sem:8.5f}")

    print("\nmonotonicity along the null order (real -> erdos_renyi):")
    readings = (
        ("task overlap", lambda a: a["geometry"]["consecutive_alignment"]),
        ("overlap/chance", lambda a: a["geometry"]["consecutive_alignment"]
            / a["geometry"]["chance_alignment"]),
        ("EWC excess", lambda a: a["diagonal(EWC)"]["excess_mean"]),
        ("bio - rand", lambda a: a["bio:cell_class"]["excess_mean"]
            - a["rand:cell_class"]["excess_mean"]),
    )
    for label, getter in readings:
        vals = [getter(results["topologies"][t]) for t in order]
        rising = all(b >= a - 1e-9 for a, b in zip(vals, vals[1:]))
        shown = "  ".join(f"{v:+.5f}" for v in vals)
        print(f"  {label:16} {shown}   monotone={'YES' if rising else 'no'}")
    print("  (monotone over 5 points on a chaotic metric is weak evidence; read the")
    print("   per-point standard errors before believing any trend)")


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
