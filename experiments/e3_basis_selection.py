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

from clfly.bench.oracle import gap_vs_oracle as _gap
from clfly.bench.oracle import oracle_errors
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


def gap_vs_oracle(seq, basis) -> dict:
    """Excess error of the basis-anchored filter over the exact oracle.

    Wraps :func:`clfly.bench.oracle.gap_vs_oracle` and adds the matching variable:
    the share of the covariance the projection zeroes.  NOT
    ``discarded_fraction(eye)``, which is always zero -- the identity is already
    within-group, so probing the projection with it measures nothing.
    """
    raw = _gap(seq, basis, keys=("final_avg_error", "forgetting"))
    out = {f"gap_{k}": v for k, v in raw.items()}
    total = seq.d * (seq.d + 1) // 2
    out["constrained_fraction"] = 1.0 - basis.n_parameters / total
    out["n_parameters"] = basis.n_parameters
    return out


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
                 n_null: int = 8) -> dict:
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
    """
    Q = partition.indicator_span()
    p = Q.shape[1]
    raw, chance = [], []
    for k in range(seq.T):
        w, V = np.linalg.eigh(seq.J[k])
        q = int(ranks[k])
        U = V[:, np.argsort(w)[::-1][:q]]
        raw.append(alignment_score(Q, U))
        nulls = []
        for _ in range(n_null):
            Z = np.linalg.qr(rng.standard_normal((seq.d, q)))[0]
            nulls.append(alignment_score(Q, Z))
        chance.append(float(np.mean(nulls)))
    raw_m, chance_m = float(np.mean(raw)), float(np.mean(chance))
    return {
        "alignment": raw_m,
        "alignment_chance": chance_m,
        "excess": raw_m / chance_m if chance_m > 0 else float("nan"),
        "span_dim": int(p),
    }


def run(args) -> dict:
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()

    results = {"config": vars(args), "topologies": {}, "timing": {}}
    for topology in args.topologies:
        rng_top = np.random.default_rng(args.seed0)
        circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
        if topology != "real":
            rng = np.random.default_rng(args.seed0)
            W = circ.net.weights()
            if topology == "target_shuffle":
                new = rewiring.shuffle_targets(W, rng)
            elif topology == "degree_swap":
                new = rewiring.degree_preserving_swap(W, rng)
            elif topology == "erdos_renyi":
                new = rewiring.erdos_renyi(circ.n_neurons, W.nnz, rng, signed=True)
            else:
                raise SystemExit(f"unknown topology {topology!r}")
            circ.net = graph.Connectome(circ.net.n_neurons, circ.net.root_ids, new.tocsr())
            results["topologies"].setdefault(topology, {})["swap_fraction"] = \
                rewiring.swap_fraction(circ.net.weights(), new)

        per_seed = []
        for seed in range(args.seed0, args.seed0 + args.seeds):
            wt = tasks.build_tasks(circ, support_size=args.support, q=args.q, seed=seed)
            seq = wt.sequence
            rng = np.random.default_rng(seed)
            row = {"_abs": {}}
            for name, basis in candidate_bases(circ, rng).items():
                g = gap_vs_oracle(seq, basis)
                if isinstance(basis, Partition):
                    g.update(alignment_of(basis, seq, wt.ranks, rng))
                row[name] = g
            # absolute levels, so a ratio against a near-zero oracle cannot
            # masquerade as a large effect
            oracle = oracle_errors(seq)
            row["_abs"] = {
                "oracle_final": oracle["final_avg_error"],
                "oracle_forgetting": oracle["forgetting"],
                "d": seq.d,
            }
            per_seed.append(row)
            print(f"    seed {seed} done ({time.time()-t0:.0f}s)  d={seq.d}")

        agg = {}
        for name in per_seed[0]:
            keys = per_seed[0][name]
            agg[name] = {k: float(np.nanmean([r[name][k] for r in per_seed])) for k in keys}
        results["topologies"].setdefault(topology, {}).update(agg)

    results["timing"]["total_s"] = time.time() - t0
    return results


def report(results: dict) -> None:
    for topology, agg in results["topologies"].items():
        if not agg or "diagonal(EWC)" not in agg:
            continue
        absl = agg.get("_abs", {})
        print(f"\n=== topology: {topology} ===")
        print(f"d={absl.get('d', '?')}  oracle final={absl.get('oracle_final', float('nan')):.4f}"
              f"  oracle forgetting={absl.get('oracle_forgetting', float('nan')):.5f}")
        print(f"{'basis':26} {'n_params':>10} {'constr':>8} {'gap_final':>10} "
              f"{'gap_forget':>11} {'align':>7} {'excess':>7}")
        print("-" * 86)
        for name in sorted(agg):
            if name.startswith("_"):
                continue
            d = agg[name]
            line = (f"{name:26} {d.get('n_parameters', 0):10,.0f} "
                    f"{d['constrained_fraction']:8.4f} {d['gap_final_avg_error']:+10.5f} "
                    f"{d['gap_forgetting']:+11.4f} {d.get('alignment', float('nan')):7.4f} "
                    f"{d.get('excess', float('nan')):7.3f}")
            print(line)

        print("\n  paired contrast (biological minus size-matched random), gap_final:")
        for col in BIOLOGICAL_BASES:
            b, r = agg.get(f"bio:{col}"), agg.get(f"rand:{col}")
            if not b or not r:
                continue
            delta = b["gap_final_avg_error"] - r["gap_final_avg_error"]
            verdict = "bio better" if delta < 0 else "no gain"
            print(f"    {col:24} bio {b['gap_final_avg_error']:+.5f}  "
                  f"rand {r['gap_final_avg_error']:+.5f}  "
                  f"delta {delta:+.5f}  {verdict}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=1500)
    p.add_argument("--support", type=int, default=150, help="neurons driven per task")
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--topologies", default="real")
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
