"""E72 -- pre-registered: does the draw-to-draw spread of a partition's task ALIGNMENT predict the draw-to-draw spread of its excess?

`e67` refuted the project's one-scalar model of the control's draw spread. The scalar was
`concentration = sum_g s_g^2 / d^2`, and the refutation has a mechanical explanation that the scalar
cannot express: **a relabelling preserves group sizes exactly**, so concentration is *identical* for
every draw. The only thing a control draw changes is *which* neurons share a group — that is, how the
partition's indicator span sits against the task subspaces.

That makes the spread of the partition's **task alignment** the natural candidate, and it is
computable with no filter: `e3`'s `alignment_of` returns the alignment between a partition's indicator
span and the task's (spectrally truncated) subspace, as an excess over random subspaces of the same
dimension.

**The prediction, written before this ran** (plan row `e72`): over the nine partitions that have both a
measured excess draw sd and a computable alignment spread, the alignment spread ranks the excess spread
at **Spearman ≥ +0.8**, where concentration is **non-monotone** (0.325 → 9.3e-4, **0.498 → 2.2e-4**,
0.678 → 1.06e-3). **Falsifier:** `side`'s alignment spread coming out *larger* than pooled-min-2's
while its excess spread is 4.3× smaller.

    python -m experiments.e72_alignment_draw_spread
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import spearman
from clfly.bench.control import concentration
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import random_partition

from experiments.e3_basis_selection import _pool_small_groups, alignment_of

#: (label, column, min_size, measured excess draw sd, draws used in that measurement, source).  All at
#: d = 1307, cs = 800, support 80, q = 0.02, on the seed set 0..5 -- so the target and the predictor are
#: measured on the same task geometries.
MEASURED = [
    ("cell_type min 1", "cell_type", 1, 6.801960781803761e-05, 8, "e67"),
    ("cell_type min 2", "cell_type", 2, 0.0009286726398617035, 5, "e14"),
    ("cell_type min 3", "cell_type", 3, 0.0010104197596728626, 5, "e14"),
    ("cell_type min 4", "cell_type", 4, 0.00061304922373747, 5, "e14"),
    ("cell_type min 6", "cell_type", 6, 0.0007275845573211113, 5, "e14"),
    ("side", "side", 1, 0.00021569004909373701, 8, "e67"),
    ("cell_class", "cell_class", 1, 0.00023709633644934897, 5, "e17"),
    ("ito_lee_hemilineage", "ito_lee_hemilineage", 1, 4.158388952603153e-05, 5, "e17b"),
    ("supertype", "supertype", 1, 8.350981282007466e-05, 5, "e17b"),
]

#: The pre-registered threshold and the concentration values it has to beat.
PREDICTED_RHO = 0.8
CONCENTRATION_POINTS = {0.020: 6.8e-5, 0.325: 9.3e-4, 0.498: 2.2e-4, 0.678: 1.06e-3}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--circuit-size", type=int, default=800)
    ap.add_argument("--support", type=int, default=80)
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--top", type=int, default=16,
                    help="spectral truncation of the task subspace; untruncated is set by support "
                         "membership alone and cannot see the structure under test")
    ap.add_argument("--nulls", type=int, default=4, help="random subspaces per alignment call")
    ap.add_argument("--limit", type=int, default=0, help="run only the first N partitions (timing)")
    ap.add_argument("--json-out", default="runs/e72_alignment_draw_spread.json")
    args = ap.parse_args()

    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    seqs, ranks = [], []
    for seed in range(args.seeds):
        wt = tasks.build_tasks(circ, support_size=args.support, q=0.02, seed=seed)
        seqs.append(wt.sequence)
        ranks.append(wt.ranks)
    print(f"circuit {circ.n_neurons} neurons, {args.seeds} task seeds built ({time.time()-t0:.0f}s)\n")

    rows = []
    specs = MEASURED[:args.limit] if args.limit else MEASURED
    for label, column, min_size, target_sd, n_draws, source in specs:
        if column not in circ.labels:
            print(f"  {label:<22} column absent")
            continue
        labels = np.asarray(circ.labels[column])
        if min_size > 1:
            labels = _pool_small_groups(labels, min_size)
        per_draw_excess, per_draw_raw, per_draw_chance = [], [], []
        span_dim = None
        for k in range(n_draws):
            rng = np.random.default_rng(10_000 + k)   # a fresh permutation and fresh null subspaces
            P = random_partition(labels, rng)
            ex, raw, ch = [], [], []
            for s in range(args.seeds):
                a = alignment_of(P, seqs[s], ranks[s], rng, n_null=args.nulls, top=args.top)
                ex.append(a["excess"])
                raw.append(a["alignment"])
                ch.append(a["alignment_chance"])
                span_dim = a["span_dim"]
            per_draw_excess.append(float(np.mean(ex)))
            per_draw_raw.append(float(np.mean(raw)))
            per_draw_chance.append(float(np.mean(ch)))
        sd_excess = float(np.std(per_draw_excess, ddof=1))
        sd_raw = float(np.std(per_draw_raw, ddof=1))
        conc = concentration(labels)
        rows.append(dict(label=label, column=column, min_size=min_size, n_draws=n_draws,
                         measured_sd=target_sd, source=source, concentration=conc,
                         alignment_spread=sd_excess, raw_alignment_spread=sd_raw,
                         span_dim=span_dim,
                         mean_alignment_excess=float(np.mean(per_draw_excess)),
                         mean_alignment=float(np.mean(per_draw_raw)),
                         mean_chance=float(np.mean(per_draw_chance)),
                         per_draw_excess=per_draw_excess))
        print(f"  {label:<22} span {span_dim:>5}  concentration {conc:.3f}  "
              f"alignment spread {sd_excess:.6f}  excess sd (measured, {source}) {target_sd:.6g}"
              f"  ({time.time()-t0:.0f}s)")

    if len(rows) < 3:
        print("\n  too few partitions to rank")
        return

    print()
    print("=" * 112)
    print("THE PRE-REGISTERED TEST")
    print("=" * 112)
    lab = [r["label"] for r in rows]
    y = [r["measured_sd"] for r in rows]
    rho_align = spearman([r["alignment_spread"] for r in rows], y)
    rho_raw = spearman([r["raw_alignment_spread"] for r in rows], y)
    rho_conc = spearman([r["concentration"] for r in rows], y)
    print(f"   n = {len(rows)} partitions\n")
    print(f"   Spearman(alignment spread, measured excess sd)   ** {rho_align:+.3f} **   "
          f"predicted >= {PREDICTED_RHO:+.2f}")
    print(f"   Spearman(raw alignment spread, measured sd)      {rho_raw:+.3f}")
    print(f"   Spearman(concentration, measured sd)             {rho_conc:+.3f}"
          f"   <- the refuted scalar")

    print()
    print("=" * 112)
    print("THE FALSIFIER THE PREDICTION NAMED")
    print("=" * 112)
    by = {r["label"]: r for r in rows}
    side, pool2 = by.get("side"), by.get("cell_type min 2")
    if side and pool2:
        le = side["alignment_spread"] > pool2["alignment_spread"]
        print(f"   side's alignment spread  {side['alignment_spread']:.6f}  "
              f"vs pooled-min-2's {pool2['alignment_spread']:.6f}")
        print(f"   side's excess sd         {side['measured_sd']:.6g}  "
              f"vs pooled-min-2's {pool2['measured_sd']:.6g}  "
              f"(ratio {pool2['measured_sd']/side['measured_sd']:.1f}x)")
        print(f"   -> the named falsifier {'FIRES: the alignment spread gets side the wrong way' if le else 'does not fire'}")

    out = {"config": vars(args), "rows": rows, "n": len(rows),
           "spearman_alignment": rho_align, "spearman_raw_alignment": rho_raw,
           "spearman_concentration": rho_conc, "predicted_rho": PREDICTED_RHO,
           "prediction_met": bool(rho_align >= PREDICTED_RHO),
           "labels": lab}
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
