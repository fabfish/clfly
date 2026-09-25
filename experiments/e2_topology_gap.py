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

from clfly.bench.analytic import analytic_excess
from clfly.bench.artifacts import write_json
from clfly.bench.control import paired_contrast
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
        # The rewiring stream is separable from the task stream. `seed0` drives both by default,
        # which confounds "a different swap realization" with "different tasks" -- and the swap2
        # endpoint's excess turned out to vary by a factor of three across realizations, so the two
        # have to be separable to tell which one moves it.
        rw_seed = args.seed0 if args.rewire_seed is None else args.rewire_seed
        W = rewiring.apply_null(W0, topology, np.random.default_rng(rw_seed))
        print(f"      edges {W.nnz:,} (was {W0.nnz:,})  "
              f"targets changed {rewiring.swap_fraction(W0, W):.3f}  "
              f"rewire_seed {rw_seed}")
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
                            for k in task_geometry(seqs[0], ranks[0])},
               # THE CIRCUIT, recorded because nothing else in this family does: the runner has printed `d=1307`
               # since its first run and no artifact of the topology line carries it, so a share like
               # `support / n_neurons` -- the quantity the support-share question turns on -- cannot be read from
               # the record (the analytic block's own `n` is the REPLICATE count, 3). The analytic ladder family
               # stores this as `_abs.d`; this one did not.
               "circuit": {"n_neurons": int(circ.n_neurons), "n_edges": int(W.nnz),
                           "targets_changed": float(rewiring.swap_fraction(W0, W))}}
        if args.geometry_only:
            # The screening path: the geometry block is what a design that samples BY ALIGNMENT needs to choose its
            # cells, and the three arms are what make a cell cost minutes. A screening artifact therefore carries no
            # `analytic` arm at all -- which also keeps it out of `e207`'s join, where a cell without a penalty is
            # not a cell.
            out["topologies"][topology] = agg
            print(f"      geometry only: alignment {agg['geometry']['all_pairs_alignment']:.5f} "
                  f"({agg['geometry']['all_pairs_alignment'] / agg['geometry']['chance_alignment']:.2f}x chance)"
                  f"  ({time.time()-t0:.0f}s)")
            continue
        for name, b in bases.items():
            # The realized arm is a single trajectory per seed and costs about half the runtime;
            # the analytic estimator supersedes it everywhere a conclusion is drawn, so it is
            # optional here for the same reason `e3` makes it optional (see `--no-realized`).
            agg[name] = {"realized": ({} if args.no_realized else paired_excess(seqs, b)),
                         "analytic": analytic_excess(seqs, b)}
        out["topologies"][topology] = agg

    out["timing_s"] = time.time() - t0
    return out


def report(results: dict) -> None:
    # The order is the artifact's OWN topology order, with the canonical names first: building it from
    # `TOPOLOGY_ORDER` alone printed an empty table for a run whose levels are `swap8`/`swap16`/`swap32`/`swap64`
    # (`--geometry-only`, `e209`), i.e. the report said nothing about what the run had measured.
    known = [t for t in TOPOLOGY_ORDER if t in results["topologies"]]
    order = known + [t for t in results["topologies"] if t not in known]
    armed = [t for t in order
             if isinstance(results["topologies"][t].get("diagonal(EWC)"), dict)]
    print(f"\n{'topology':14} {'overlap':>8} {'over/ch':>8} {'flatten':>8} | "
          f"{'a:EWC':>9} {'a_sem':>8} | {'r:EWC':>9} {'r_sem':>8} | "
          f"{'a:bio-rand':>11} {'sig':>6}")
    print("-" * 116)
    for t in order:
        a = results["topologies"][t]
        g = a["geometry"]
        if t not in armed:
            print(f"{t:14} {g['consecutive_alignment']:8.4f} "
                  f"{g['consecutive_alignment']/g['chance_alignment']:8.3f} "
                  f"{g['flattening']:8.3f} | " + f"{'(no arms: geometry-only)':>30} |")
            continue
        ab, ar = a["bio:cell_class"]["analytic"], a["rand:cell_class"]["analytic"]
        delta = ab["excess_mean"] - ar["excess_mean"]
        sem = float(np.hypot(ab["excess_sem"], ar["excess_sem"]))
        re = a["diagonal(EWC)"].get("realized") or {}
        realized = (f"{re['excess_mean']:+9.5f} {re['excess_sem']:8.5f} | "
                    if re else f"{'(no realized arm)':>30} | ")
        print(f"{t:14} {g['consecutive_alignment']:8.4f} "
              f"{g['consecutive_alignment']/g['chance_alignment']:8.3f} "
              f"{g['flattening']:8.3f} | "
              f"{a['diagonal(EWC)']['analytic']['excess_mean']:+9.5f} "
              f"{a['diagonal(EWC)']['analytic']['excess_sem']:8.5f} | "
              + realized +
              f"{delta:+11.5f} {abs(delta)/sem if sem else float('inf'):6.2f}")

    # Two ways this section used to print a claim it had not measured: `all()` over an EMPTY list is True, so a
    # screening run announced five `monotone=YES` lines with no values under them, and a one-topology run announced
    # an ordering from a single point. Both are the defect this project keeps finding -- a verdict produced by the
    # shape of an empty sequence rather than by a measurement.
    if not armed:
        print("\nno arms were computed (a screening run): the penalty column, the monotonicity readings and the")
        print("adjacent-contrast significances are NOT available, and none of them is reported as a verdict.")
        return
    print("\nmonotonicity along the null order (real -> erdos_renyi):")
    if len(order) < 2:
        print(f"  NOT COMPUTED -- {len(order)} topology in this artifact, and an ordering needs two")
        return
    readings = (
        ("task overlap", lambda a: a["geometry"]["consecutive_alignment"]),
        ("overlap/chance", lambda a: a["geometry"]["consecutive_alignment"]
            / a["geometry"]["chance_alignment"]),
        ("EWC excess (analytic)", lambda a: a["diagonal(EWC)"]["analytic"]["excess_mean"]),
        ("bio-rand (analytic)", lambda a: a["bio:cell_class"]["analytic"]["excess_mean"]
            - a["rand:cell_class"]["analytic"]["excess_mean"]),
    )
    if all((results["topologies"][t]["diagonal(EWC)"].get("realized") or {}) for t in armed):
        readings = readings + (
            ("EWC excess (realized)",
             lambda a: a["diagonal(EWC)"]["realized"]["excess_mean"]),)
    for label, getter in readings:
        vals = [getter(results["topologies"][t]) for t in order]
        rising = all(b >= a - 1e-9 for a, b in zip(vals, vals[1:]))
        shown = "  ".join(f"{v:+.5f}" for v in vals)
        print(f"  {label:24} {shown}   monotone={'YES' if rising else 'no'}")
    print("\n  adjacent-contrast significance (analytic excess, |delta| / sem):")
    print("    the task seeds are shared across topologies, so these contrasts are PAIRED;")
    print("    the paired figure is reported where per-seed values exist, and it is the right one")
    for label, getter in (("EWC excess", lambda a: a["diagonal(EWC)"]["analytic"]),
                          ("bio-cell_class", lambda a: a["bio:cell_class"]["analytic"]),
                          ("rand-cell_class", lambda a: a["rand:cell_class"]["analytic"])):
        stats = [getter(results["topologies"][t]) for t in order]
        parts = []
        for i in range(len(stats) - 1):
            a, b = stats[i], stats[i + 1]
            d = b["excess_mean"] - a["excess_mean"]
            if "excess_per_seed" in a and "excess_per_seed" in b and len(a["excess_per_seed"]) > 1:
                pc = paired_contrast(a["excess_per_seed"], b["excess_per_seed"])
                parts.append(f"{order[i]}->{order[i+1]} {d:+.5f} "
                             f"({pc['sigma_paired']:.1f}s paired, {pc['sigma_unpaired']:.1f}s unpaired)")
            else:
                s = float(np.hypot(b["excess_sem"], a["excess_sem"]))
                n = len(a.get("excess_per_seed") or [])
                why = "1 seed" if n == 1 else "no per-seed data"
                parts.append(f"{order[i]}->{order[i+1]} {d:+.5f} "
                             f"({abs(d)/s if s else float('inf'):.1f}s unpaired -- {why})")
        print(f"  {label:16} " + "  ".join(parts))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--support", type=int, default=80)
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--topologies", default=",".join(TOPOLOGY_ORDER))
    p.add_argument("--rewire-seed", type=int, default=None,
                   help="seed the swap stream separately from the tasks; without it `seed0` drives "
                        "both, confounding a different swap realization with different tasks")
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--no-realized", action="store_true",
                   help="skip the realized-error arm; the analytic estimator supersedes it "
                        "everywhere a conclusion is drawn and the arm costs about half the runtime")
    p.add_argument("--geometry-only", action="store_true",
                   help="write only the `geometry` block, skipping all three arms: the screening path for a design "
                        "that selects cells BY ALIGNMENT rather than by swap strength (see `e209`). A cell measured "
                        "this way carries no penalty and is therefore not a cell of `e207`'s join")
    args = p.parse_args(argv)
    args.topologies = tuple(t for t in args.topologies.split(",") if t)

    results = run(args)
    report(results)
    if args.json_out:
        write_json(args.json_out, results)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
