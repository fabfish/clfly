"""E5 — is the gap driven by *spectral richness*? Decoupling the confounded axis.

E2 found the diagonalisation gap falls as the wiring is randomised, alongside a
fall in the task precision's effective rank, and proposed spectral richness as the
driver.  That evidence is weak for one reason: **richness was confounded with swap
strength**.  Both moved together because both were consequences of the same
manipulation, so the four points cannot separate "the gap tracks richness" from
"the gap tracks something else that rewiring also destroys".

This experiment breaks the confound by varying richness *directly*, at fixed
topology, fixed support size, fixed rank and fixed seeds.  The knob is the shape
of the drive distribution on each task's assembly:

    w_i proportional to exp(kappa * z_i),  z ~ N(0, 1), normalised to mean one

Every ``kappa`` reuses the same ``z`` draw, so only the *concentration* changes.
At ``kappa = 0`` the assembly is driven uniformly and each task's precision is as
flat as the propagator allows; at large ``kappa`` a few neurons carry the drive
and the precision collapses toward rank one.  The support size -- and therefore
the rank -- is untouched throughout.

Prediction, if E2's proposal is right: the gap should fall monotonically as
``kappa`` rises, and the gap should be a function of the measured flattening
rather than of ``kappa`` itself.

    python -m experiments.e5_anisotropy_axis --circuit-size 800 --support 80
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.oracle import gap_vs_oracle, oracle_errors, task_geometry
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import Diagonal, Partition, random_partition

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Drive-concentration sweep.  Spans "uniform drive" to "a few neurons carry it".
KAPPAS = (0.0, 0.25, 0.5, 1.0, 1.75, 2.5, 4.0)


def run(args) -> dict:
    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    out = {"config": vars(args), "points": [], "timing_s": 0.0}

    for seed in range(args.seed0, args.seed0 + args.seeds):
        circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
        for kappa in args.kappas:
            wt = tasks.build_tasks(circ, support_size=args.support, q=args.q,
                                   seed=seed, weight_concentration=kappa)
            seq = wt.sequence
            geom = task_geometry(seq, wt.ranks)
            oracle = oracle_errors(seq)
            rng = np.random.default_rng(seed)
            point = {
                "seed": seed,
                "kappa": float(kappa),
                "flattening": geom["flattening"],
                "effective_rank": geom["effective_rank"],
                "mean_rank": geom["mean_rank"],
                "top_eig_share": geom["top_eig_share"],
                "overlap": geom["consecutive_alignment"],
                "chance_alignment": geom["chance_alignment"],
                "oracle_final": oracle["final_avg_error"],
                "gap_ewc": gap_vs_oracle(seq, Diagonal(seq.d)),
                "gap_bio_cc": gap_vs_oracle(seq, Partition(circ.labels["cell_class"])),
                "gap_rand_cc": gap_vs_oracle(
                    seq, random_partition(circ.labels["cell_class"], rng)),
            }
            out["points"].append(point)
            print(f"  seed {seed} kappa={kappa:<5g} flatten={point['flattening']:.4f} "
                  f"effrank={point['effective_rank']:6.1f} "
                  f"gap_ewc={point['gap_ewc']:+.4f} ({time.time()-t0:.0f}s)")

    out["timing_s"] = time.time() - t0
    return out


def report(results: dict) -> None:
    pts = results["points"]
    print(f"\n{'kappa':>7} {'flatten':>9} {'eff_rank':>9} {'top_share':>10} "
          f"{'overlap':>9} {'gap_EWC':>9} {'bio-rand':>9}")
    print("-" * 70)
    for p in pts:
        print(f"{p['kappa']:7g} {p['flattening']:9.4f} {p['effective_rank']:9.1f} "
              f"{p['top_eig_share']:10.4f} {p['overlap']:9.4f} {p['gap_ewc']:+9.4f} "
              f"{p['gap_bio_cc'] - p['gap_rand_cc']:+9.4f}")

    # Averaged over seeds when there is more than one.
    by_kappa: dict[float, list[dict]] = {}
    for p in pts:
        by_kappa.setdefault(p["kappa"], []).append(p)
    ks = sorted(by_kappa)
    flat = [float(np.mean([q["flattening"] for q in by_kappa[k]])) for k in ks]
    gap = [float(np.mean([q["gap_ewc"] for q in by_kappa[k]])) for k in ks]

    print("\nsweep of the decoupled axis:")
    print(f"  flattening vs kappa: {' -> '.join(f'{v:.3f}' for v in flat)}")
    print(f"  gap_EWC    vs kappa: {' -> '.join(f'{v:+.3f}' for v in gap)}")
    falling = all(b <= a + 1e-9 for a, b in zip(gap, gap[1:]))
    print(f"  gap monotone decreasing in kappa: {'YES' if falling else 'no'}")

    if len(ks) > 2:
        rho = _spearman(flat, gap)
        print(f"  Spearman(flattening, gap) over all points = {rho:+.3f}")
        print("  (negative rho means richer spectra give a LARGER gap)")


def _spearman(x, y) -> float:
    def rank(v):
        order = np.argsort(np.argsort(v))
        return order.astype(float)
    rx, ry = rank(np.asarray(x)), rank(np.asarray(y))
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / denom) if denom else float("nan")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--support", type=int, default=80)
    p.add_argument("--seeds", type=int, default=1)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--q", type=float, default=0.02)
    p.add_argument("--kappas", default=",".join(str(k) for k in KAPPAS))
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)
    args.kappas = tuple(float(k) for k in args.kappas.split(",") if k)

    results = run(args)
    report(results)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(results, indent=1, default=str))
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
