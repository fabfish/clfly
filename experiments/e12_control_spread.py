"""E12 — how much of a matched-pair delta is the *control draw*?

Every biological partition in this project is scored against a group-size-matched random
control, because a partition could otherwise "win" merely by having larger groups.  The
control is drawn **once**.  Its seed standard error is then reported as the delta's error
bar — but that sem measures the spread across *task geometries* for a single control draw,
and says nothing about how much the delta would move had a different random partition been
drawn.  The scientific claim ("biological groupings beat random partitions of matched
size") is about the *population* of random partitions, so the draw-to-draw spread belongs
in the error bar, and leaving it out inflates every sigma in the basis study.

The ladder gives a first estimate of the size of the effect without any new compute:
`bio:pool32` and `bio:pool64` are the **same partition** (beyond a threshold of 32 no
further cell type on this circuit is small enough to merge), so their 4.7 sigma difference
is entirely the two controls disagreeing.  That is one pair, though, and two draws are a
poor variance estimate.  This script draws many controls for one fixed partition and
measures the spread directly.

    python -m experiments.e12_control_spread --min-size 4 --seeds 6 --draws 12

Reports, for the chosen partition:

- the control's mean and **draw-to-draw** standard deviation, on a fixed seed set, so the
  task-geometry noise cancels and what is left is the draw noise;
- the sem the current protocol reports (seed spread within one draw);
- the ratio, i.e. how much a single-draw sigma is inflated;
- the delta and its sigma with and without the draw component, at this rung.

The oracle line is printed so the delta stays readable as a fraction of the gap that
actually exists.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import analytic_excess
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import Partition, random_partition

# the pooling device from e3, duplicated here rather than imported so that changing one
# experiment cannot silently change what another one measured
def _pool_small_groups(labels: np.ndarray, min_size: int) -> np.ndarray:
    counts = np.bincount(labels)
    keep = counts >= min_size
    remap = np.cumsum(keep) - 1
    pooled_id = int(remap.max()) + 1
    return np.where(keep, remap, pooled_id)[labels]


def run(args) -> dict:
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)

    seqs = []
    for seed in range(args.seed0, args.seed0 + args.seeds):
        wt = tasks.build_tasks(circ, support_size=args.support, q=args.q, seed=seed)
        seqs.append(wt.sequence)
        print(f"  built tasks for seed {seed} ({time.time() - t0:.0f}s)  d={wt.sequence.d}")

    labels = _pool_small_groups(circ.labels["cell_type"], args.min_size)
    bio = Partition(labels)
    bio_ex = analytic_excess(seqs, bio)
    print(f"\n  biological partition (cell_type, min_size {args.min_size}): "
          f"{bio.n_groups} groups, constrained {1 - bio.n_parameters / (seqs[0].d * (seqs[0].d + 1) // 2):.4f}")
    print(f"    excess {bio_ex['excess_mean']:+.5f} +- {bio_ex['excess_sem']:.5f} "
          f"(oracle {bio_ex['oracle_mean']:.5f})")

    # Draw the controls on one fixed seed set, so every draw sees the same task geometries
    # and the differences between draws are paired: what varies is the partition, not the
    # tasks.  The task-geometry spread is reported separately as the within-draw sem.
    rng = np.random.default_rng(args.seed0)
    ctrl = []
    for _ in range(args.draws):
        ex = analytic_excess(seqs, random_partition(labels, rng), )
        ctrl.append(ex)
    means = np.array([c["excess_mean"] for c in ctrl])
    sems = np.array([c["excess_sem"] for c in ctrl])
    sd_draw = float(means.std(ddof=1))
    sem_mean = sd_draw / np.sqrt(len(means))
    print(f"\n  {args.draws} independent control draws for that partition:")
    print(f"    per-draw means: " + " ".join(f"{m:+.5f}" for m in means))
    print(f"    mean over draws   {means.mean():+.5f} +- {sem_mean:.5f} (sem over draws)")
    print(f"    across-draw sd    {sd_draw:.5f}   <- the component a single-draw sem omits")
    print(f"    within-draw sem   {sems.mean():.5f}   <- what the protocol reports today")
    print(f"    inflation factor  {sd_draw / sems.mean():.1f}x")

    delta = bio_ex["excess_mean"] - means.mean()
    sem_seed = float(np.hypot(bio_ex["excess_sem"], sems.mean()))
    sem_honest = float(np.hypot(bio_ex["excess_sem"], sem_mean))
    print(f"\n  delta (biological minus matched-random): {delta:+.5f}")
    print(f"    sigma with a single control draw (protocol today): {abs(delta) / sem_seed:6.1f}")
    print(f"    sigma with the draw component included:            {abs(delta) / sem_honest:6.1f}")
    print(f"    both are readable against the oracle gap of {bio_ex['oracle_mean']:.5f}")

    return {
        "config": vars(args) | {"json_out": str(args.json_out)},
        "d": seqs[0].d,
        "biological": bio_ex,
        "control_means": means.tolist(),
        "control_sem_within_draw": sems.tolist(),
        "control_sd_across_draws": sd_draw,
        "control_sem_over_draws": sem_mean,
        "delta": float(delta),
        "sigma_single_draw": abs(delta) / sem_seed,
        "sigma_with_draw_noise": abs(delta) / sem_honest,
        "timing_s": time.time() - t0,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--support", type=int, default=80, help="neurons driven per task")
    p.add_argument("--seeds", type=int, default=6, help="task-geometry draws per control")
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--min-size", type=int, default=4,
                   help="merge cell types smaller than this; the pooling rung to test")
    p.add_argument("--draws", type=int, default=12, help="independent random controls")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    results = run(args)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(results, indent=1, default=str))
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
