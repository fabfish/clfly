"""E3 — which anchoring basis should the Fisher live in?

The core experiment.  For a circuit-constrained LGCL problem built from the
wiring (see :mod:`clfly.connectome.tasks`), measure the excess error of EWC in
each candidate anchoring basis relative to the exact Kalman oracle, at matched
capacity, and against group-size-matched random partitions.

Two questions, in order:

**Q1 (why do we need interaction at all).** Does the coordinate basis actually
lose anything here?  If the excess is ~0 in every basis, the fly's wiring has
already made the question moot -- which is a result, and the modularity
explanation for it is testable.

**Q2 (which basis).** Among the rungs of the annotation ladder, does the ranking
track the principal angles between each partition's indicator span and the tasks'
precision subspaces?  The biological rungs must beat their matched random
controls, or the answer is "any partition of this granularity does" and the
biology is decoration.

    python -m experiments.e3_basis_selection --circuit-size 1500 --seeds 2
    python -m experiments.e3_basis_selection --topology real,degree_swap
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import analytic_excess
from clfly.bench.oracle import (
    oracle_errors,
    paired_excess,
    task_subspaces,
)
from clfly.connectome import annotate, circuits, graph, rewiring, tasks
from clfly.lgcl.bases import (
    Diagonal,
    Partition,
    alignment_score,
    random_partition,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "runs"

#: Biological rungs to test, in the order they appear on the ladder.
BIOLOGICAL_BASES = ("side", "cell_class", "cell_type", "ito_lee_hemilineage", "supertype")


def candidate_bases(circ: circuits.Circuit, rng: np.random.Generator) -> dict:
    """Every anchoring basis to be compared, biological and control."""
    bases = {"diagonal(EWC)": Diagonal(circ.n_neurons)}
    for col in BIOLOGICAL_BASES:
        if col not in circ.labels:
            continue
        lab = circ.labels[col]
        bases[f"bio:{col}"] = Partition(lab)
        bases[f"rand:{col}"] = random_partition(lab, rng)
    return bases


def alignment_of(partition: Partition, seq, ranks, rng: np.random.Generator,
                 n_null: int = 8, top: int | None = None) -> dict:
    """Alignment between a partition's indicator span and the task subspaces.

    Raw alignment is not interpretable on its own: a finer partition has a
    *larger* indicator span, so it overlaps every subspace more and scores higher
    for free.  The first version of this function reported the raw number, and it
    came out anti-correlated with the anchoring benefit -- the finest biological
    rung scored highest and lost the most.

    So we also report ``excess``, the ratio to an empirically measured chance
    level: the mean alignment this same partition achieves against random
    subspaces of the same dimension.  Measuring the null rather than deriving it
    keeps the comparison honest if the indicator spans are not generic.

    ``top`` selects a spectrally *truncated* task subspace.  Without it the
    subspace is the task's entire range space, which is set by support membership
    alone and is bit-identical across large changes in drive strength -- so the
    predictor cannot see the structure it is supposed to be testing.  This is the
    most likely reason the untruncated version failed to rank the bases in e3.
    """
    Q = partition.indicator_span()
    p = Q.shape[1]
    V = task_subspaces(seq, ranks, top=top)
    raw, chance = [], []
    for k in range(seq.T):
        U = V[k]
        raw.append(alignment_score(Q, U))
        nulls = []
        for _ in range(n_null):
            Z = np.linalg.qr(rng.standard_normal((seq.d, U.shape[1])))[0]
            nulls.append(alignment_score(Q, Z))
        chance.append(float(np.mean(nulls)))
    raw_m, chance_m = float(np.mean(raw)), float(np.mean(chance))
    return {
        "alignment": raw_m,
        "alignment_chance": chance_m,
        "excess": raw_m / chance_m if chance_m > 0 else float("nan"),
        "span_dim": int(p),
        "align_top": int(V[0].shape[1]),
    }


def run(args) -> dict:
    """Paired design: one set of task sequences per seed, every basis scored on all of them.

    This is what makes the comparison interpretable.  Building tasks inside the
    basis loop would give each basis its own task draw, so basis differences would
    be contaminated by task differences -- and on this substrate the task-to-task
    spread is larger than most of the effects (see the metric-instability findings).
    """
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()

    results = {"config": vars(args), "topologies": {}, "timing": {}}
    for topology in args.topologies:
        circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
        if topology != "real":
            rng_top = np.random.default_rng(args.seed0)
            W0 = circ.net.weights()
            W = rewiring.apply_null(W0, topology, rng_top)
            results.setdefault("topology_notes", {})[topology] = {
                "edges_before": int(W0.nnz), "edges_after": int(W.nnz),
                "swap_fraction": rewiring.swap_fraction(W0, W),
            }
            circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, W.tocsr())
            print(f"  topology {topology}: edges {W0.nnz:,} -> {W.nnz:,}")

        # scores: name -> metric -> value, pooled across seeds
        seqs, ranks = [], []
        for seed in range(args.seed0, args.seed0 + args.seeds):
            wt = tasks.build_tasks(circ, support_size=args.support, q=args.q, seed=seed)
            seqs.append(wt.sequence)
            ranks.append(wt.ranks)
            print(f"    built tasks for seed {seed} ({time.time()-t0:.0f}s)  d={wt.sequence.d}")
        rank_ref = ranks[0]

        rng = np.random.default_rng(args.seed0)
        agg = {}
        for name, basis in candidate_bases(circ, rng).items():
            row = {"realized": paired_excess(seqs, basis),
                   "analytic": analytic_excess(seqs, basis)}
            row["n_parameters"] = basis.n_parameters
            total = seqs[0].d * (seqs[0].d + 1) // 2
            row["constrained_fraction"] = 1.0 - basis.n_parameters / total
            if isinstance(basis, Partition):
                # spectrally selected subspace, not the full range space: taking the
                # numerical rank returns the whole range, which is blind to drive
                # strength and cannot see the structure the predictor is about.
                row.update(alignment_of(basis, seqs[0], rank_ref, rng,
                                        top=args.align_top))
            agg[name] = row
            print(f"    {name:26} analytic={row['analytic']['excess_mean']:+.5f}"
                  f"+-{row['analytic']['excess_sem']:.5f}  "
                  f"realized={row['realized']['excess_mean']:+.5f}"
                  f"+-{row['realized']['excess_sem']:.5f}  ({time.time()-t0:.0f}s)")

        agg["_abs"] = {
            "oracle_final": float(np.mean([oracle_errors(s)["final_avg_error"] for s in seqs])),
            "oracle_final_analytic": agg["diagonal(EWC)"]["analytic"]["oracle_mean"],
            "d": seqs[0].d,
            "n_seeds": len(seqs),
        }
        results["topologies"][topology] = agg

    results["timing"]["total_s"] = time.time() - t0
    return results


def report(results: dict) -> None:
    for topology, agg in results["topologies"].items():
        if not agg or "diagonal(EWC)" not in agg:
            continue
        absl = agg.get("_abs", {})
        print(f"\n=== topology: {topology} ===")
        print(f"d={absl.get('d', '?')}  seeds={absl.get('n_seeds', '?')}  "
              f"oracle: realized {absl.get('oracle_final', float('nan')):.5f}  "
              f"analytic {absl.get('oracle_final_analytic', float('nan')):.5f}")
        print(f"{'basis':26} {'constr':>7} | {'a_excess':>10} {'a_sem':>8} "
              f"{'a_sd':>8} | {'r_excess':>10} {'r_sem':>8}")
        print("-" * 92)
        for name in sorted(agg):
            if name.startswith("_"):
                continue
            d = agg[name]
            a, r = d["analytic"], d["realized"]
            print(f"{name:26} {d['constrained_fraction']:7.4f} | "
                  f"{a['excess_mean']:+10.5f} {a['excess_sem']:8.5f} {a['excess_sd']:8.5f} | "
                  f"{r['excess_mean']:+10.5f} {r['excess_sem']:8.5f}")

        print("\n  paired contrast (biological minus size-matched random):")
        print(f"  {'rung':24} {'analytic delta':>15} {'sigma':>7} | "
              f"{'realized delta':>15} {'sigma':>7}")
        wins_a = wins_r = 0
        for col in BIOLOGICAL_BASES:
            b, r = agg.get(f"bio:{col}"), agg.get(f"rand:{col}")
            if not b or not r:
                continue
            da = b["analytic"]["excess_mean"] - r["analytic"]["excess_mean"]
            sa = float(np.hypot(b["analytic"]["excess_sem"], r["analytic"]["excess_sem"]))
            dr = b["realized"]["excess_mean"] - r["realized"]["excess_mean"]
            sr = float(np.hypot(b["realized"]["excess_sem"], r["realized"]["excess_sem"]))
            za = abs(da) / sa if sa else float("inf")
            zr = abs(dr) / sr if sr else float("inf")
            wins_a += bool(da < 0 and za > 2)
            wins_r += bool(dr < 0 and zr > 2)
            print(f"  {col:24} {da:+15.5f} {za:7.2f} | {dr:+15.5f} {zr:7.2f}")
        print(f"  -> resolved (>2 sigma, biology better): "
              f"analytic {wins_a}/{len(BIOLOGICAL_BASES)}, "
              f"realized {wins_r}/{len(BIOLOGICAL_BASES)}")
        print("  (the analytic column is the expected error, so its spread is task "
              "geometry alone;\n   the realized column also carries sampling noise, "
              "which is what made e3 unresolvable)")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=1500)
    p.add_argument("--support", type=int, default=150, help="neurons driven per task")
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--topologies", default="real")
    p.add_argument("--align-top", type=int, default=16,
                   help="spectral truncation for the alignment predictor; the "
                        "numerical rank would return the degener"
                        "ate full range space")
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
