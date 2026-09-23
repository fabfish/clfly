"""E86 -- `e80`'s spread statistic at two more circuit sizes, which is the half of the mechanism that had no replication.

`e80` found that the **absolute** draw-to-draw spread of `projection_pressure` ranks the measured draw
spread of the control's excess at **+0.767 (p = 0.016)** at d = 1307, while correlating only +0.317 with
concentration. `e81` then showed the *co-movement* explains 83% of the variance on the same relabelling,
and `e82` replicated the co-movement at d = 952 and d = 1874.

**The spread half was never replicated, and it is the half that matters for a predictor**: the co-movement
says pressure and the excess move together; the spread statistic says the *size* of pressure's own
variation calibrates the *size* of the control's. `e82` already computed the pressure spreads at both
sizes; what was missing is the **target** — nine measured draw sds per size — which is what `e86` supplies,
at `e14`/`e74`'s protocol (3 task seeds, 5 draws) so the new points sit beside the old ones.

**The prediction, from the plan's `e86` row, written before the run:** at each new size the absolute
pressure spread outranks the measured draw spread at **Spearman ≥ +0.7** *and* beats concentration's
correlation on the same nine partitions. **Falsifier:** the absolute pressure spread failing to beat
concentration at either size — which is a live risk, because at d = 1307 the margin was only +0.767
against +0.617 on nine points.

    python -m experiments.e86_spread_at_other_sizes
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

#: The nine partitions, keyed as the artifact filenames encode them.
PARTITIONS = [
    ("cell_type", 1), ("cell_type", 2), ("cell_type", 3), ("cell_type", 4), ("cell_type", 6),
    ("side", 1), ("cell_class", 1), ("ito_lee_hemilineage", 1), ("supertype", 1),
]

#: The artifact that carries the labels in the order these filenames map onto.
LABEL_FOR = {
    ("cell_type", 1): "cell_type min 1", ("cell_type", 2): "cell_type min 2",
    ("cell_type", 3): "cell_type min 3", ("cell_type", 4): "cell_type min 4",
    ("cell_type", 6): "cell_type min 6", ("side", 1): "side", ("cell_class", 1): "cell_class",
    ("ito_lee_hemilineage", 1): "ito_lee_hemilineage", ("supertype", 1): "supertype",
}

#: size label -> (circuit size used by `e86`, the pressure-spread artifact from `e80`/`e82`)
SIZES = [
    ("d = 952", 300, "runs/e82_pressure_comovement_d300.json"),
    ("d = 1307", 800, "runs/e80_pressure_draw_spread.json"),
    ("d = 1874", 1500, "runs/e82_pressure_comovement_d1500.json"),
]

PREDICTED_RHO = 0.7


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def measured_sd(cs: int, column: str, min_size: int) -> tuple[float | None, int | None, str]:
    d = load(f"runs/e86_drawsd_cs{cs}_{column}_min{min_size}.json")
    if d is None:
        return None, None, "absent"
    return (float(d["control_sd_across_draws"]), int(d["config"]["draws"]),
            f"{d['config']['draws']} draws x {d['config']['seeds']} seeds")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e86_spread_at_other_sizes.json")
    args = ap.parse_args()

    out: dict = {"sizes": {}}
    verdicts = {}
    for label, cs, spread_path in SIZES:
        spread = load(spread_path)
        if spread is None:
            print(f"   {label:<9} no pressure-spread artifact ({spread_path})")
            continue
        by_label = {r["label"]: r for r in spread["rows"]}
        rows = []
        for column, min_size in PARTITIONS:
            lab = LABEL_FOR[(column, min_size)]
            src = by_label.get(lab)
            if src is None:
                continue
            sd, draws, prov = measured_sd(cs, column, min_size)
            if sd is None and cs != 800:
                continue
            if cs == 800:
                #: d = 1307's targets are the ones `e80` used, already in its artifact
                sd = src["measured_sd"]
                draws, prov = 5, "the targets `e80` used"
            rows.append(dict(label=lab, concentration=src["concentration"],
                             pressure_sd=src["pressure_sd"], relative_sd=src["relative_sd"],
                             measured_sd=sd, draws=draws, provenance=prov))
        if len(rows) < 4:
            print(f"   {label:<9} only {len(rows)} partitions have a measured target -- skipped")
            verdicts[label] = None
            continue

        print()
        print("=" * 104)
        print(f"{label}  (cs = {cs}, {len(rows)} partitions)")
        print("=" * 104)
        print(f"   {'partition':<22}{'conc':>8}{'pressure sd':>13}{'rel sd':>9}{'measured sd':>13}"
              f"{'draws':>7}   source")
        for r in rows:
            print(f"   {r['label']:<22}{r['concentration']:>8.3f}{r['pressure_sd']:>13.5f}"
                  f"{r['relative_sd']:>9.4f}{r['measured_sd']:>13.4g}{r['draws']:>7}   {r['provenance']}")

        y = [r["measured_sd"] for r in rows]
        conc = [r["concentration"] for r in rows]
        tests = {
            "absolute pressure sd": [r["pressure_sd"] for r in rows],
            "relative pressure sd": [r["relative_sd"] for r in rows],
            "concentration": conc,
        }
        print()
        print(f"   {'candidate':<24}{'rho vs measured sd':>20}{'p':>9}{'rho vs conc':>13}")
        res = {}
        for name, x in tests.items():
            rho, p = spearmanr(x, y)
            rc, _ = spearmanr(x, conc)
            res[name] = dict(rho=float(rho), p=float(p), rho_conc=float(rc))
            print(f"   {name:<24}{rho:>+20.3f}{p:>9.3f}{rc:>+13.3f}")
        best = res["absolute pressure sd"]
        beats = best["rho"] > res["concentration"]["rho"]
        print(f"\n   absolute pressure sd beats concentration: ** {beats} **"
              f"   ({best['rho']:+.3f} against {res['concentration']['rho']:+.3f})")
        print(f"   and reaches the pre-registered {PREDICTED_RHO:+.2f}: "
              f"** {best['rho'] >= PREDICTED_RHO} **")
        verdicts[label] = dict(rows=rows, tests=res, beats_concentration=bool(beats),
                               meets_threshold=bool(best["rho"] >= PREDICTED_RHO))
        out["sizes"][label] = dict(n=len(rows), rows=rows, tests=res,
                                   beats_concentration=bool(beats),
                                   meets_threshold=bool(best["rho"] >= PREDICTED_RHO))

    print()
    print("=" * 104)
    print("THE PRE-REGISTERED TEST, ACROSS SIZES")
    print("=" * 104)
    for label in [s[0] for s in SIZES]:
        v = verdicts.get(label)
        if v is None:
            print(f"   {label:<9} no verdict")
            continue
        print(f"   {label:<9} rho {v['tests']['absolute pressure sd']['rho']:+.3f}   "
              f"beats conc: {v['beats_concentration']}   "
              f"meets >= {PREDICTED_RHO:+.1f}: {v['meets_threshold']}")
    print(f"\n   the d = 1307 row is `e80`'s own result, repeated here so the three are read together.")

    #: The nine labels are the same at every size, but they are **not the same partitions**: a pooling
    #: that leaves 29 groups at d = 1307 leaves a handful at d = 952, so the sizes sample different
    #: regions of partition space.  When that happens a rank correlation over "the same nine rows" is
    #: comparing different objects, so the region each size covers is reported and the comparison is
    #: redone on the overlap.
    print()
    print("=" * 104)
    print("AND WHETHER THE SIZES ARE COMPARING THE SAME PARTITIONS AT ALL")
    print("=" * 104)
    ranges = {label: (min(r["concentration"] for r in v["rows"]),
                      max(r["concentration"] for r in v["rows"]))
              for label, v in verdicts.items() if v}
    for label, (lo, hi) in ranges.items():
        print(f"   {label:<9} concentration {lo:.3f} to {hi:.3f}")
    if len(ranges) >= 2:
        lo = max(r[0] for r in ranges.values())
        hi = min(r[1] for r in ranges.values())
        print(f"   overlap:            {lo:.3f} to {hi:.3f}")
        for label, v in verdicts.items():
            if not v:
                continue
            keep = [r for r in v["rows"] if lo <= r["concentration"] <= hi]
            if len(keep) < 4:
                print(f"   {label:<9} only {len(keep)} rows inside the overlap -- not computable")
                continue
            y2 = [r["measured_sd"] for r in keep]
            a = spearmanr([r["pressure_sd"] for r in keep], y2)
            c = spearmanr([r["concentration"] for r in keep], y2)
            print(f"   {label:<9} inside the overlap (n = {len(keep)}): absolute pressure sd "
                  f"{a.statistic:+.3f} (p = {a.pvalue:.3f}) against concentration "
                  f"{c.statistic:+.3f} (p = {c.pvalue:.3f})")
            out.setdefault("overlap", {})[label] = dict(
                n=len(keep), rho_pressure=float(a.statistic), p_pressure=float(a.pvalue),
                rho_concentration=float(c.statistic), p_concentration=float(c.pvalue))

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
