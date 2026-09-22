"""E81 -- pre-registered: does `projection_pressure` CO-MOVE with the control's excess, within a seed?

`e80` gave this line its first positive result: the **absolute** draw-to-draw spread of
`projection_pressure` ranks the measured draw spread of the control's excess at **+0.767 (p = 0.016)**
over nine partitions, while correlating only +0.317 with concentration. Four subspace-overlap
candidates had failed before it.

But that is a **rank correlation across nine partitions**, which is weak evidence for a mechanism: it
says partitions with a bigger pressure spread tend to have a bigger excess spread. It does not say the
two quantities move together *on the same relabelling*. That is the difference between a lead and a
mechanism, and `e75` already showed how to test it — centre each variable by its own seed mean and
correlate within a seed, so the task draw is held fixed and only the dimension a relabelling moves is
left.

**The prediction, written before this run:**

* the within-seed co-movement between `projection_pressure` and the control's excess is **at least
  +0.5** on the mean over the nine partitions;
* the fraction of the draw-to-draw excess variance it explains (mean *r*²) is **at least 0.25**;
* and it beats the alignment's co-movement from `e75`, which was **+0.170** (mean *r*).

**Falsifier:** a mean co-movement **at or below +0.170** — no better than the bare alignment's, which
would demote `e80`'s +0.767 to a coincidence of nine rank positions rather than a relationship between
the two quantities.

This run also recomputes the spread statistic on the same data, so `e80`'s headline is reproduced
inside one artifact rather than across two.

    python -m experiments.e81_pressure_comovement
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.analytic import analytic_excess, projection_pressure, spearman
from clfly.bench.control import concentration
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import random_partition

from experiments.e3_basis_selection import _pool_small_groups

#: The same nine partitions as `e72`, `e75` and `e80`, with their measured excess draw sds.
PARTITIONS = [
    ("cell_type min 1", "cell_type", 1, 6.801960781803761e-05),
    ("cell_type min 2", "cell_type", 2, 0.0009286726398617035),
    ("cell_type min 3", "cell_type", 3, 0.0010104197596728626),
    ("cell_type min 4", "cell_type", 4, 0.00061304922373747),
    ("cell_type min 6", "cell_type", 6, 0.0007275845573211113),
    ("side", "side", 1, 0.00021569004909373701),
    ("cell_class", "cell_class", 1, 0.00023709633644934897),
    ("ito_lee_hemilineage", "ito_lee_hemilineage", 1, 4.158388952603153e-05),
    ("supertype", "supertype", 1, 8.350981282007466e-05),
]

PREDICTED_COMOVEMENT = 0.5
PREDICTED_R2 = 0.25
ALIGNMENT_BASELINE = 0.170      # e75's mean within-seed r
PREDICTED_SPREAD_RHO = 0.8


def residualise(x: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    out = x.astype(float).copy()
    for s in np.unique(seeds):
        m = seeds == s
        out[m] -= out[m].mean()
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--circuit-size", type=int, default=800)
    ap.add_argument("--support", type=int, default=80)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--draws", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json-out", default="runs/e81_pressure_comovement.json")
    args = ap.parse_args()

    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    seqs = []
    for s in range(args.seeds):
        wt = tasks.build_tasks(circ, support_size=args.support, q=0.02, seed=s)
        seqs.append(wt.sequence)
    print(f"circuit {circ.n_neurons} neurons, {args.seeds} task seeds, {args.draws} draws "
          f"({time.time()-t0:.0f}s)\n")
    print(f"  {'partition':<22}{'pressure':>10}{'excess':>10}{'within-seed r':>15}"
          f"{'r^2':>8}{'seeds +':>9}{'sd(draw)':>12}")

    specs = PARTITIONS[:args.limit] if args.limit else PARTITIONS
    rows = []
    for label, column, min_size, measured_sd in specs:
        if column not in circ.labels:
            print(f"  {label:<22} column absent")
            continue
        labels = np.asarray(circ.labels[column])
        if min_size > 1:
            labels = _pool_small_groups(labels, min_size)
        P_, E_, D_, S_ = [], [], [], []
        for d in range(args.draws):
            rng = np.random.default_rng(40_000 + d)
            P = random_partition(labels, rng)
            for s in range(args.seeds):
                P_.append(float(projection_pressure(seqs[s], P)))
                E_.append(float(analytic_excess([seqs[s]], P)["excess_mean"]))
                D_.append(d)
                S_.append(s)
        P_, E_, D_, S_ = map(np.asarray, (P_, E_, D_, S_))
        #: within-seed residual co-movement -- the only dimension a relabelling moves
        pr, er = residualise(P_, S_), residualise(E_, S_)
        pear = float(np.corrcoef(pr, er)[0, 1]) if pr.std() > 0 and er.std() > 0 else float("nan")
        spear = spearman(pr.tolist(), er.tolist())
        per_seed = []
        for s in np.unique(S_):
            m = S_ == s
            if pr[m].std() > 0 and er[m].std() > 0:
                per_seed.append(float(np.corrcoef(pr[m], er[m])[0, 1]))
        #: and the spread statistic `e80` reported, recomputed here on the same data
        seed_mean = np.array([P_[S_ == s].mean() for s in np.unique(S_)])
        per_draw = np.array([P_[(D_ == d)].mean() for d in np.unique(D_)])
        rows.append(dict(label=label, column=column, min_size=min_size,
                         concentration=concentration(labels), measured_sd=measured_sd,
                         pearson=pear, spearman=spear, r2=pear ** 2 if pear == pear else float("nan"),
                         per_seed=per_seed, n_pos_seed=sum(1 for v in per_seed if v > 0),
                         n_seed=len(per_seed),
                         pressure_mean=float(P_.mean()), pressure_sd=float(per_draw.std(ddof=1)),
                         relative_sd=float(per_draw.std(ddof=1) / per_draw.mean()),
                         label_seed_mean=seed_mean.tolist(),
                         pressure_values=P_.tolist(), excess_values=E_.tolist(),
                         draw_index=D_.tolist(), seed_index=S_.tolist()))
        label_seed_hits = f"{rows[-1]['n_pos_seed']}/{rows[-1]['n_seed']}"
        print(f"  {label:<22}{P_.mean():>10.4f}{E_.mean():>10.5f}{pear:>+15.3f}"
              f"{pear**2:>8.3f}{label_seed_hits:>9}"
              f"{rows[-1]['pressure_sd']:>12.5f}   ({time.time()-t0:.0f}s)")

    if len(rows) < 3:
        print("\n  too few partitions to order")
        return

    y = [r["measured_sd"] for r in rows]
    mean_r = float(np.mean([r["pearson"] for r in rows]))
    mean_rho = float(np.mean([r["spearman"] for r in rows]))
    mean_r2 = float(np.mean([r["r2"] for r in rows]))
    rho_spread = spearman([r["pressure_sd"] for r in rows], y)
    rho_conc = spearman([r["concentration"] for r in rows], y)

    print()
    print("=" * 108)
    print("THE PRE-REGISTERED TEST")
    print("=" * 108)
    print(f"   n = {len(rows)} partitions\n")
    print(f"   within-seed co-movement, mean r    {mean_r:+.3f}   predicted >= "
          f"{PREDICTED_COMOVEMENT:+.2f}   -> {'PASS' if mean_r >= PREDICTED_COMOVEMENT else 'FAIL'}")
    print(f"   mean r^2 (variance explained)      {mean_r2:.3f}   predicted >= "
          f"{PREDICTED_R2:.2f}   -> {'PASS' if mean_r2 >= PREDICTED_R2 else 'FAIL'}")
    print(f"   beats the alignment's {ALIGNMENT_BASELINE:+.3f}:  "
          f"{'YES' if mean_r > ALIGNMENT_BASELINE else 'NO'}")
    print(f"   (mean Spearman form: {mean_rho:+.3f})")
    print(f"\n   and the spread statistic reproduced on the same data: "
          f"Spearman(absolute pressure sd, measured sd) = {rho_spread:+.3f}"
          f"   (concentration: {rho_conc:+.3f})")

    neg = [r for r in rows if r["pearson"] <= 0]
    print()
    print("=" * 108)
    print("THE FALSIFIER: A CO-MOVEMENT NO BETTER THAN THE ALIGNMENT'S")
    print("=" * 108)
    if mean_r <= ALIGNMENT_BASELINE:
        print(f"   FIRES: {mean_r:+.3f} is no better than {ALIGNMENT_BASELINE:+.3f}, so `e80`'s +0.767 would be a")
        print(f"   coincidence of nine rank positions rather than a relationship between the two quantities")
    else:
        print(f"   does not fire: {mean_r:+.3f} against the alignment's {ALIGNMENT_BASELINE:+.3f}")
    print(f"   partitions with a non-positive co-movement: {len(neg)} of {len(rows)}")
    for r in neg:
        print(f"     -> {r['label']:<22} r {r['pearson']:+.3f}  ({r['n_pos_seed']}/{r['n_seed']} seeds positive)")

    out = {"config": vars(args), "n": len(rows), "rows": rows,
           "mean_pearson": mean_r, "mean_spearman": mean_rho, "mean_r2": mean_r2,
           "spearman_spread_vs_sd": rho_spread, "spearman_concentration_vs_sd": rho_conc,
           "predicted_comovement": PREDICTED_COMOVEMENT, "predicted_r2": PREDICTED_R2,
           "alignment_baseline": ALIGNMENT_BASELINE,
           "prediction_met": bool(mean_r >= PREDICTED_COMOVEMENT and mean_r2 >= PREDICTED_R2)}
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
