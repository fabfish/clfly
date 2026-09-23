"""E92 -- the concentration-matched grid: one profile of group sizes per cell, the same cells at every size.

`e86` closed the cross-size test as **not well-posed**: the nine labels are the same at every circuit size
and the *partitions* are not, because a pooling that leaves 29 groups at d = 1307 leaves a handful at
d = 952. The concentration ranges do not even overlap enough to restrict the comparison — 0.006 to 0.754 at
d = 952, 0.020 to 0.536 at d = 1307, 0.034 to 0.324 at d = 1874. So "the same nine rows" were different
objects, and the 1-1 split between the sizes is a statement about the design as much as about the
statistic.

This script supplies the design the finding pre-registered: **choose partitions by concentration, not by
label, and use the same concentration grid at every size.**

The observation that makes it cheap and exact is that both halves of the measurement depend on the
partition only through its **group-size multiset**. `e80`'s pressure is computed on
`random_partition(labels, rng)` — a size-matched relabelling — so which neuron sits in which group never
enters; and `e12`'s target is the draw-to-draw spread of that same size-matched control. A profile of
group sizes is therefore a legitimate object of study, and it lets concentration be **set** rather than
found. Two profiles at different circuit sizes have the same concentration by construction, so "cell i of
the grid" names the same region of partition space at every size.

    python -m experiments.e92_grid_profiles --circuit-size 300 --k 13 --shape flat
    python -m experiments.e92_grid_profiles --circuit-size 800 --k 13 --shape harmonic

One profile per invocation, one artifact per profile, so a grid that takes hours is resumable and its
partial progress is durable on disk.

**The prediction and the falsifier are pre-registered in
`docs/findings/2026-09-23-the-concentration-matched-grid-preregistered.md` and were written before any
grid artifact existed.** In short: the partial rank correlation of the pressure spread against the
measured draw spread, **controlling for concentration**, is positive at all three sizes, and the whole
point is that a positive partial is the only form of the claim a concentration restatement cannot fake.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import analytic_excess, projection_pressure
from clfly.bench.artifacts import write_json
from clfly.bench.control import concentration
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import Partition, random_partition

#: The grid's group counts, log-spaced so that `flat` spans concentration 0.5 down to 0.006 — the whole
#: range the nine biological partitions covered, and a little of the coarse end beyond it.
K_GRID = [2, 3, 5, 8, 13, 21, 34, 55, 96, 160]

#: Two group-size shapes per group count. `flat` is the equal-size profile, whose concentration is exactly
#: `1/k`; `harmonic` is a Zipf-like decay, which at the same `k` is far more concentrated, because one
#: group holds a large share of the neurons. Two shapes at one `k` are two points at two concentrations,
#: so the grid is over concentration rather than over shape.
SHAPES = ["flat", "harmonic"]


def group_sizes(d: int, k: int, shape: str) -> np.ndarray:
    """Group sizes for a profile: ``d`` neurons in ``k`` groups, shaped ``flat`` or ``harmonic``.

    Largest-remainder apportionment, so the sizes sum to ``d`` exactly and the rounding does not
    accumulate. Every group gets at least one neuron; the mass comes back off the largest groups, which
    keeps the shape intact wherever the profile is not degenerate.
    """
    if k > d:
        raise ValueError(f"{k} groups cannot be made from {d} neurons")
    if shape == "flat":
        base = np.ones(k)
    elif shape == "harmonic":
        base = 1.0 / np.arange(1, k + 1)
    else:
        raise ValueError(f"unknown shape {shape!r}")

    raw = d * base / base.sum()
    sizes = np.floor(raw).astype(np.int64)
    rem = d - int(sizes.sum())
    if rem > 0:
        #: the largest fractional parts get the remainder, as apportionment does
        order = np.argsort(-(raw - sizes))[:rem]
        sizes[order] += 1
    sizes = np.maximum(sizes, 1)
    while int(sizes.sum()) > d:
        sizes[int(np.argmax(sizes))] -= 1
    while int(sizes.sum()) < d:
        sizes[int(np.argmax(sizes))] += 1
    return sizes


def profile_labels(sizes: np.ndarray) -> np.ndarray:
    """The labels array a partition needs — the group id repeated once per neuron.

    Which neuron gets which group is irrelevant here: ``Partition.project`` compares labels pairwise, and
    the control is a relabelling of the same multiset, so the arrangement carries no information.
    """
    return np.repeat(np.arange(len(sizes)), sizes)


def run(args) -> dict:
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    seqs = []
    for s in range(args.seeds):
        wt = tasks.build_tasks(circ, support_size=args.support, q=0.02, seed=args.seed0 + s)
        seqs.append(wt.sequence)
    d = seqs[0].d
    print(f"  circuit {circ.n_neurons} neurons, d = {d}, T = {seqs[0].T}, {args.seeds} task seeds "
          f"({time.time() - t0:.0f}s)")

    sizes = group_sizes(d, args.k, args.shape)
    labels = profile_labels(sizes)
    assert len(labels) == d
    conc = concentration(labels)
    print(f"  profile k = {args.k} {args.shape}: {len(sizes)} groups, sizes "
          f"{np.array2string(np.sort(sizes)[::-1][:6], separator=',')}...  concentration {conc:.4f}")

    #: The biological profile's own excess, for the record -- it is not the target, which is the
    #: size-matched control's draw spread.
    bio_ex = analytic_excess(seqs, Partition(labels))
    print(f"  profile's own excess {bio_ex['excess_mean']:+.5f} "
          f"(oracle {bio_ex['oracle_mean']:.5f})   ({time.time() - t0:.0f}s)")

    #: One rng per draw, as `e80` used, so the two halves of the measurement see the same relabelling and
    #: every comparison between them is paired.
    pressure_draw_seed, excess_draw_seed = [], []
    for i in range(args.draws):
        rng = np.random.default_rng(30_000 + i)
        P = random_partition(labels, rng)
        pressure_draw_seed.append([float(projection_pressure(seqs[s], P)) for s in range(args.seeds)])
        ex = analytic_excess(seqs, P)
        excess_draw_seed.append([float(v) for v in ex["excess_per_seed"]])
        print(f"    draw {i}: pressure {np.mean(pressure_draw_seed[-1]):.5f}   "
              f"excess {np.mean(excess_draw_seed[-1]):+.6f}   ({time.time() - t0:.0f}s)")

    Pds = np.asarray(pressure_draw_seed, float)   # (draws, seeds)
    Eds = np.asarray(excess_draw_seed, float)     # (draws, seeds)
    per_draw_pressure = Pds.mean(axis=1)
    per_draw_excess = Eds.mean(axis=1)
    pressure_sd = float(per_draw_pressure.std(ddof=1))
    measured_sd = float(per_draw_excess.std(ddof=1))
    pressure_mean = float(per_draw_pressure.mean())
    measured_mean = float(per_draw_excess.mean())

    #: per-seed spreads: the same two quantities with the task geometry held fixed, which is what the
    #: per-seed discipline asks for. Three numbers each, so the sign record is over 3 per profile.
    pressure_sd_per_seed = [float(Pds[:, s].std(ddof=1)) for s in range(args.seeds)]
    measured_sd_per_seed = [float(Eds[:, s].std(ddof=1)) for s in range(args.seeds)]

    print(f"\n  pressure mean {pressure_mean:.5f}  spread across draws {pressure_sd:.5f} "
          f"(relative {pressure_sd / pressure_mean:.4f})")
    print(f"  control  mean {measured_mean:+.6f}  spread across draws {measured_sd:.4g}")
    print(f"  per-seed pressure spreads {np.array2string(np.array(pressure_sd_per_seed), precision=5)}")
    print(f"  per-seed measured spreads {np.array2string(np.array(measured_sd_per_seed), precision=5)}")

    return {
        "config": vars(args) | {"json_out": str(args.json_out)},
        "d": d,
        "T": int(seqs[0].T),
        "k": int(args.k),
        "shape": args.shape,
        "n_groups": int(len(sizes)),
        "group_sizes": [int(x) for x in sizes],
        "concentration": float(conc),
        "constrained_fraction": 1.0 - Partition(labels).n_parameters / (d * (d + 1) // 2),
        "biological": bio_ex,
        "pressure_mean": pressure_mean,
        "pressure_sd": pressure_sd,
        "relative_sd": pressure_sd / pressure_mean if pressure_mean else float("nan"),
        "measured_mean": measured_mean,
        "measured_sd": measured_sd,
        "pressure_sd_per_seed": pressure_sd_per_seed,
        "measured_sd_per_seed": measured_sd_per_seed,
        #: kept, not filtered out: the per-(draw, seed) values are what a paired test between the two
        #: halves or a seed-level resample needs, and this project has paid for dropping them before.
        "per_draw_pressure": [float(x) for x in per_draw_pressure],
        "per_draw_excess": [float(x) for x in per_draw_excess],
        "pressure_values": Pds.ravel().tolist(),
        "excess_values": Eds.ravel().tolist(),
        "draw_index": [i for i in range(args.draws) for _ in range(args.seeds)],
        "seed_index": [s for _ in range(args.draws) for s in range(args.seeds)],
        "rng_scheme": "default_rng(30000 + draw), e80's scheme",
        "timing_s": time.time() - t0,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--circuit-size", type=int, default=300)
    p.add_argument("--support", type=int, default=30)
    p.add_argument("--k", type=int, required=True, help=f"groups in the profile, from {K_GRID}")
    p.add_argument("--shape", choices=SHAPES, required=True)
    p.add_argument("--seeds", type=int, default=3)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--draws", type=int, default=5, help="size-matched relabellings, e12/e80's protocol")
    p.add_argument("--json-out", type=Path, default=None)
    p.add_argument("--overwrite", action="store_true",
                   help="re-measure a cell whose artifact is already on disk.  Without this the script "
                        "skips it and exits, so a sweep that was interrupted can be re-launched as the "
                        "same loop and costs only the cells it is missing.")
    args = p.parse_args(argv)

    out = args.json_out or Path(f"runs/e92_grid_cs{args.circuit_size}_{args.shape}_k{args.k}.json")
    #: **The skip guard is here because its absence cost a cell.** The first sweep ran all sixty cells as
    #: one background task behind a four-hour timeout and was killed on the sixtieth, so the completion had
    #: to be reconstructed by enumerating which files were missing and re-running that one by hand.  With
    #: this guard the same loop is resumable: it re-launches, skips the fifty-nine, and measures only what
    #: the timeout ate.
    if out.exists() and not args.overwrite:
        print(f"{out} is already on disk -- skipping (pass --overwrite to re-measure).")
        return 0

    results = run(args)
    write_json(out, results)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
