"""E7 — does circuit overlap predict interference?

Claim C4 in the research plan: FlyCL's tasks engage different circuits, so *which*
tasks interfere should be predictable from how much those circuits overlap. If it
holds, a benchmark gets something no existing CL suite has — a biology-derived
prior on the interference matrix, readable before any training run.

E2 already refuted the *aggregate* version of this story: along the rewiring axis the
total EWC excess moves opposite to mean task overlap. But that is a statement about
means. C4 is a **pairwise** claim — interference between task `j` and task `k` scales
with the overlap of their circuits — and pairwise structure can survive where the
aggregate trend does not, because the aggregate also carries the conditioning effects
that dominate e2's Erdős–Rényi point.

Two tests, in increasing order of realism.

**Controlled overlap.** Supports are built from a shared pool plus disjoint private
complements, so every pair has *exactly* the same overlap by construction
(:func:`clfly.connectome.tasks.overlap_controlled_supports`). Sweeping the pool size
sweeps one number with nothing else moving, and the prediction is simply that mean
pairwise interference rises with it.

**Real assemblies.** The actual mushroom body / central complex / antennal lobe
assemblies, whose pairwise overlaps are heterogeneous and measured. Here the
prediction is a correlation, and task *distance* is a confound that must be
controlled: a later task damages an earlier one more partly simply because more
learning has happened in between.

Interference is read off the exact analytic error matrix, which gives `E[k, m]` — the
expected error on task `m` of the estimate after task `k`. The marginal damage to task
`j` from learning task `k` alone is `E[k, j] - E[k-1, j]`.

    python -m experiments.e7_interference
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import expected_error_matrix, spearman, task_permutation_test
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import Diagonal

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Pool fractions to sweep.  0 means disjoint circuits, 1 means identical ones.
OVERLAP_LEVELS = (0.0, 0.1, 0.25, 0.5, 0.75, 1.0)


def interference_matrix(seq, basis) -> np.ndarray:
    """``I[j, k]`` = marginal damage to task ``j`` from learning task ``k`` (k > j)."""
    E = expected_error_matrix(seq, basis)
    T = seq.T
    I = np.full((T, T), np.nan)
    for j in range(T):
        for k in range(j + 1, T):
            I[j, k] = E[k, j] - E[k - 1, j]
    return I


def support_overlap(a: np.ndarray, b: np.ndarray) -> float:
    """Jaccard overlap of two supports."""
    sa, sb = set(a.tolist()), set(b.tolist())
    return len(sa & sb) / len(sa | sb) if sa | sb else 0.0


def propagation_overlap(seq, j: int, k: int, top: int = 16) -> float:
    """Alignment of two tasks' precision subspaces — overlap *after* propagation.

    The finer predictor: two disjoint input populations can still drive overlapping
    directions once the propagator mixes them, so this is the quantity a
    representation-level interference prior would have to use.
    """
    from clfly.lgcl.bases import alignment_score

    def top_sub(kk):
        w, V = np.linalg.eigh(seq.J[kk])
        return V[:, np.argsort(w)[::-1][:top]]

    return alignment_score(top_sub(j), top_sub(k))


def controlled_sweep(args, conn, ann) -> list[dict]:
    """Sweep a single exactly-controlled overlap number."""
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    rows = []
    for level in args.levels:
        seqs, mate = [], None
        for seed in range(args.seed0, args.seed0 + args.seeds):
            rng = np.random.default_rng(seed)
            supports = tasks.overlap_controlled_supports(
                circ.n_neurons, args.tasks, args.support, level, rng)
            asms = [tasks.SupportAssembly(name=f"o{level:g}_t{k}", support=s)
                    for k, s in enumerate(supports)]
            wt = tasks.build_tasks(circ, assemblies=asms, support_size=None,
                                   q=args.q, seed=seed)
            seqs.append(wt.sequence)
            mate = (supports, asms)

        E = [interference_matrix(s, Diagonal(s.d)) for s in seqs]
        pairwise, distances = [], []
        for I in E:
            T = I.shape[0]
            for j in range(T):
                for k in range(j + 1, T):
                    pairwise.append(I[j, k])
                    distances.append(k - j)
        # also record the *achieved* overlap, so the control cannot silently fail
        achieved = np.mean([support_overlap(mate[0][j], mate[0][k])
                            for j in range(args.tasks) for k in range(j + 1, args.tasks)])
        rows.append({
            "level": level,
            "achieved_overlap": float(achieved),
            "mean_interference": float(np.mean(pairwise)),
            "mean_interference_near": float(np.mean([p for p, d in zip(pairwise, distances) if d == 1])),
            "mean_interference_far": float(np.mean([p for p, d in zip(pairwise, distances) if d > 1])),
        })
        print(f"    overlap={level:5.2f} (achieved {achieved:.3f})  "
              f"mean interference {rows[-1]['mean_interference']:+.6f}  "
              f"near {rows[-1]['mean_interference_near']:+.6f}  "
              f"far {rows[-1]['mean_interference_far']:+.6f}")
    return rows


def real_assemblies(args, conn, ann) -> dict:
    """Heterogeneous real overlaps: correlate measured overlap with interference."""
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    seqs, ranks = [], []
    for seed in range(args.seed0, args.seed0 + args.seeds):
        wt = tasks.build_tasks(circ, support_size=args.support, q=args.q, seed=seed)
        seqs.append(wt.sequence)
        ranks.append(wt.ranks)

    T = seqs[0].T
    # the realised supports, recovered from each task's precision diagonal
    supports = [np.argsort(-np.diag(seqs[0].J[k]))[: ranks[0][k]] for k in range(T)]

    I = np.mean([interference_matrix(s, Diagonal(s.d)) for s in seqs], axis=0)
    pairs = []
    for j in range(T):
        for k in range(j + 1, T):
            pairs.append({
                "pair": f"{j}-{k}",
                "overlap": support_overlap(supports[j], supports[k]),
                "propagation": float(np.mean([propagation_overlap(s, j, k) for s in seqs])),
                "interference": float(I[j, k]),
                "distance": k - j,
            })

    ov = [p["overlap"] for p in pairs]
    prop = [p["propagation"] for p in pairs]
    inter = [p["interference"] for p in pairs]
    dist = [p["distance"] for p in pairs]

    res = {
        "n_pairs": len(pairs),
        "n_pairs_zero_support_overlap": int(sum(1 for p in pairs if p["overlap"] == 0.0)),
        "spearman_overlap_vs_interference": spearman(ov, inter),
        "spearman_propagation_vs_interference": spearman(prop, inter),
        "spearman_overlap_vs_propagation": spearman(ov, prop),
        "overlap_vs_distance": spearman(ov, dist),
        "pairs": pairs,
    }
    # Leave-one-out on the propagation correlation: with only T(T-1)/2 pairs, one
    # dominant pair can carry the whole coefficient, and saying so is the difference
    # between a finding and a coincidence.
    loo = []
    for drop in range(len(pairs)):
        keep = [i for i in range(len(pairs)) if i != drop]
        loo.append(spearman([prop[i] for i in keep], [inter[i] for i in keep]))
    res["propagation_loo_min"] = float(np.min(loo))
    res["propagation_loo_max"] = float(np.max(loo))
    res["propagation_loo_range"] = float(np.max(loo) - np.min(loo))
    # The pairs come from `n_tasks` tasks and are NOT independent: a permutation test over the
    # pairs is far too narrow. This is the exact task-LABEL permutation, which is the null the
    # design implies, and it cannot go below 1/(T!+1) however strong the association.
    res["task_permutation_propagation"] = task_permutation_test(prop, inter, n_tasks=args.tasks)

    # Size confound: interference may simply track how much information the two
    # tasks carry, which is not an overlap effect at all.
    size = [max(ranks[0][j], ranks[0][k]) for j in range(T) for k in range(j + 1, T)]
    res["spearman_size_vs_interference"] = spearman(size, inter)
    res["spearman_size_vs_propagation"] = spearman(size, prop)
    res["task_ranks"] = [int(x) for x in ranks[0]]

    # Within a fixed task distance the distance confound is removed exactly, so
    # these are the correlations that mean something.
    for label, key, sel in (("distance 1", "spearman_overlap_vs_interference_distance1",
                             [p for p in pairs if p["distance"] == 1]),
                            ("distance >1", "spearman_overlap_vs_interference_far",
                             [p for p in pairs if p["distance"] > 1])):
        if len(sel) > 2:
            res[key] = spearman([p["overlap"] for p in sel],
                                [p["interference"] for p in sel])
            res[key + "_n"] = len(sel)
    return res


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--support", type=int, default=80)
    p.add_argument("--tasks", type=int, default=5)
    p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--levels", default=",".join(str(x) for x in OVERLAP_LEVELS))
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    args.levels = tuple(float(x) for x in args.levels.split(",") if x)

    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    out = {"config": vars(args)}

    print("controlled overlap sweep (exact uniform pairwise overlap):")
    out["controlled"] = controlled_sweep(args, conn, ann)
    lv = [r["achieved_overlap"] for r in out["controlled"]]
    mi = [r["mean_interference"] for r in out["controlled"]]
    print(f"  Spearman(overlap, mean interference) = {spearman(lv, mi):+.3f}   "
          f"({time.time()-t0:.0f}s)")

    print("\nreal assemblies (heterogeneous overlap):")
    out["real"] = real_assemblies(args, conn, ann)
    r = out["real"]
    print(f"  pairs={r['n_pairs']}  of which {r['n_pairs_zero_support_overlap']} have "
          f"ZERO anatomical support overlap")
    print(f"  task ranks (support sizes): {r['task_ranks']}")
    print(f"  support overlap      vs interference: {r['spearman_overlap_vs_interference']:+.3f}")
    print(f"  propagation overlap  vs interference: {r['spearman_propagation_vs_interference']:+.3f}"
          f"   leave-one-out range [{r['propagation_loo_min']:+.3f}, {r['propagation_loo_max']:+.3f}]")
    tp = r["task_permutation_propagation"]
    print(f"    task-level permutation over {tp['n_tasks']} tasks: p = {tp['p_value']:.4f} "
          f"of {tp['n_permutations']} labelings; the design cannot go below "
          f"{tp['min_attainable_p']:.4f}, so p < 0.001 needs {tp['tasks_needed_for_p1e-3']} tasks")
    print(f"  support vs propagation overlap:       {r['spearman_overlap_vs_propagation']:+.3f}")
    print(f"  overlap vs task distance (confound):  {r['overlap_vs_distance']:+.3f}")
    print(f"  task SIZE vs interference (confound): {r['spearman_size_vs_interference']:+.3f}"
          f"   (size vs propagation: {r['spearman_size_vs_propagation']:+.3f})")
    for key, label in (("spearman_overlap_vs_interference_distance1", "distance 1 only"),
                       ("spearman_overlap_vs_interference_far", "distance >1 only")):
        if key in r:
            print(f"  overlap vs interference, {label}: {r[key]:+.3f}")
    out["timing_s"] = time.time() - t0

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(out, indent=1, default=str))
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
