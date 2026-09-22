"""E80 -- pre-registered: does the draw-to-draw spread of `projection_pressure` predict the draw-to-draw spread of the control's excess?

Four candidates for the control's draw spread have now failed — group count (`e12`), concentration
(`e67`), the normalised alignment spread (`e72`) and the bare alignment's co-movement (`e75`). The two
that came closest are the **plainest partition-size scalars**, and every one of the four is a subspace
overlap of one kind or another.

`projection_pressure` is not a subspace overlap at all, which is what makes it the next candidate rather
than a fifth variation on a dead theme:

* it asks how much of the **exact filter's posterior trajectory** a basis would discard, and runs that
  filter itself — whose prior trajectory is basis-independent, so the number is a property of
  *(partition, tasks)* computable before any anchored filter exists;
* it weights the discarded part by the task's **measurement information** `J_k`, in the metric that makes
  it dimensionless. Without that weighting it would merely re-derive `constrained_fraction`, so the
  weighting is what gives it a chance.

**The prediction, from the plan's `e80` row, written before this run:** the spread of `pressure` across
control draws ranks the measured draw spread of the control's *excess* at **Spearman ≥ +0.8**, and its
correlation with **concentration** is **below +0.5** — because a quantity weighted by the task's
information should not reduce to a size scalar, and if it does, it is the fifth re-expression of size.
**Falsifier:** a concentration correlation as high as +0.85, which is what `e72`'s normalised alignment
spread achieved while failing the target.

**The absolute spread is confounded with the level, and both are reported.** `pressure` differs across
partitions by an order of magnitude (0.68 for a near-diagonal pooling, 0.08 for a coarse one), so its
absolute sd across draws may simply track its own mean. The relative spread `sd/mean` is therefore
reported beside it, and a win that appears only in the absolute column is a level effect and not a
predictor.

    python -m experiments.e80_pressure_draw_spread
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from clfly.bench.analytic import projection_pressure, spearman
from clfly.bench.control import concentration
from clfly.connectome import annotate, circuits, graph, tasks
from clfly.lgcl.bases import random_partition

from experiments.e3_basis_selection import _pool_small_groups

#: The same nine partitions `e72` and `e75` scored, with their measured excess draw sds.
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

PREDICTED_RHO = 0.8
PREDICTED_CONC = 0.5
FALSIFIER_CONC = 0.85
E72_NORMALISED_CONC = 0.850


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--circuit-size", type=int, default=800)
    ap.add_argument("--support", type=int, default=80)
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--draws", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json-out", default="runs/e80_pressure_draw_spread.json")
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
    print(f"  {'partition':<22}{'conc':>7}{'pressure':>10}{'sd(draw)':>10}{'rel sd':>9}"
          f"{'measured sd':>13}")

    specs = PARTITIONS[:args.limit] if args.limit else PARTITIONS
    rows = []
    for label, column, min_size, measured_sd in specs:
        if column not in circ.labels:
            print(f"  {label:<22} column absent")
            continue
        labels = np.asarray(circ.labels[column])
        if min_size > 1:
            labels = _pool_small_groups(labels, min_size)
        per_draw, per_draw_seed, used_labels = [], [], None
        for d in range(args.draws):
            rng = np.random.default_rng(30_000 + d)
            P = random_partition(labels, rng)
            used_labels = labels
            row = [projection_pressure(seqs[s], P) for s in range(args.seeds)]
            per_draw_seed.append([float(x) for x in row])
            per_draw.append(float(np.mean(row)))
        per_draw = np.asarray(per_draw, float)
        mean = float(per_draw.mean())
        sd = float(per_draw.std(ddof=1))
        conc = concentration(used_labels)
        rows.append(dict(label=label, column=column, min_size=min_size, concentration=conc,
                         measured_sd=measured_sd, pressure_mean=mean, pressure_sd=sd,
                         relative_sd=sd / mean if mean else float("nan"),
                         #: The per-(draw, seed) pressures are kept, not filtered out: the same
                         #: co-movement question `e75` answered for the alignment can be asked of the
                         #: pressure with them, and `e75`'s first version taught this project that
                         #: dropping a computed field to save bytes costs a rerun of the expensive
                         #: half.
                         per_draw=per_draw.tolist(), per_draw_seed=per_draw_seed))
        print(f"  {label:<22}{conc:>7.3f}{mean:>10.4f}{sd:>10.5f}{sd/mean:>9.4f}"
              f"{measured_sd:>13.3g}   ({time.time()-t0:.0f}s)")

    if len(rows) < 3:
        print("\n  too few partitions to order")
        return

    y = [r["measured_sd"] for r in rows]
    tests = {
        "absolute pressure sd": [r["pressure_sd"] for r in rows],
        "relative pressure sd (sd/mean)": [r["relative_sd"] for r in rows],
        "pressure level (mean)": [r["pressure_mean"] for r in rows],
        "concentration": [r["concentration"] for r in rows],
    }
    print()
    print("=" * 104)
    print("THE PRE-REGISTERED TEST")
    print("=" * 104)
    print(f"   n = {len(rows)} partitions;   target = the measured excess draw sd\n")
    print(f"   {'candidate':<34}{'Spearman vs sd':>16}{'p':>9}{'Spearman vs conc':>19}{'p':>9}")
    res = {}
    for name, x in tests.items():
        rho, p = spearmanr(x, y)
        rc, pc = spearmanr(x, [r["concentration"] for r in rows])
        res[name] = dict(rho=float(rho), p=float(p), rho_conc=float(rc), p_conc=float(pc))
        print(f"   {name:<34}{rho:>+16.3f}{p:>9.3f}{rc:>+19.3f}{pc:>9.3f}")
    print(f"\n   also reported as plain Spearman coefficients (ties averaged):")
    for name, x in tests.items():
        print(f"   {name:<34}{spearman(x, y):>+16.3f}"
              f"{'':>9}{spearman(x, [r['concentration'] for r in rows]):>+19.3f}")

    print()
    print("=" * 104)
    print("THE DECISION, ON THE PRE-REGISTERED CLAUSES")
    print("=" * 104)
    prim = "relative pressure sd (sd/mean)"
    rho_p, p_p = res[prim]["rho"], res[prim]["p"]
    rc_p = res[prim]["rho_conc"]
    print(f"   primary candidate: {prim}")
    print(f"   (1) Spearman vs the measured draw sd: {rho_p:+.3f} (p = {p_p:.3f})"
          f"   needs >= {PREDICTED_RHO:+.2f}   -> {'PASS' if rho_p >= PREDICTED_RHO else 'FAIL'}")
    print(f"   (2) Spearman vs concentration:        {rc_p:+.3f}"
          f"   needs <  {PREDICTED_CONC:+.2f}   -> {'PASS' if rc_p < PREDICTED_CONC else 'FAIL'}")
    print(f"   falsifier (concentration as high as `e72`'s {E72_NORMALISED_CONC:+.3f}): "
          f"{'FIRES' if rc_p >= FALSIFIER_CONC else 'does not fire'}")
    print(f"\n   the absolute-spread column, for the record: "
          f"{res['absolute pressure sd']['rho']:+.3f} vs sd, "
          f"{res['absolute pressure sd']['rho_conc']:+.3f} vs concentration")

    out = {"config": vars(args), "n": len(rows),
           "rows": [{k: v for k, v in r.items() if k != "per_draw"} for r in rows],
           "tests": res, "primary": prim, "predicted_rho": PREDICTED_RHO,
           "predicted_conc": PREDICTED_CONC, "falsifier_conc": FALSIFIER_CONC,
           "prediction_met": bool(rho_p >= PREDICTED_RHO and rc_p < PREDICTED_CONC)}
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
