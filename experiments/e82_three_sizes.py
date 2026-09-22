"""E82 -- the pressure mechanism at three circuit sizes, and whether the co-movement is the same quantity at each.

`e81` found the mechanism at d = 1307: the control's excess moves across relabellings with
`projection_pressure` — the precision-weighted projected deficit — at *r* = 0.906, *r*² = 0.828, against
0.170 / 0.066 for the bare alignment on the identical design. `e82` runs the same measurement at two other
sizes, chosen because **the co-movement needs no measured draw sd** and so has nothing to re-measure at a
new size: d = 952 (cs = 300, support 30 — `e6`'s `baseline` condition) and d = 1874 (cs = 1500,
support 150 — `e9`/`e79`'s ladder size).

This script puts the three side by side. It reports, per size: the mean co-movement and mean *r*², the
paired differences between sizes on the **same** partition labels, the full seed-level sign record, and —
because this vocabulary crowds the fine end differently at each size — **how many distinct partitions each
size actually has**, since two rows can be the same partition.

    python -m experiments.e82_three_sizes
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

#: size label -> (artifact, circuit size, d)
SIZES = [
    ("d = 952", "runs/e82_pressure_comovement_d300.json", 300),
    ("d = 1307", "runs/e81_pressure_comovement.json", 800),
    ("d = 1874", "runs/e82_pressure_comovement_d1500.json", 1500),
]

#: `e75`'s alignment co-movement on the same nine partitions, for the comparison `e81` made at one size.
ALIGNMENT_MEAN_R = 0.170


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def paired_stats(dl: np.ndarray) -> dict:
    n = dl.size
    mean = float(dl.mean())
    sem = float(dl.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    pos, neg = int((dl > 0).sum()), int((dl < 0).sum())
    return dict(n=int(n), delta=mean, sem=sem,
                sigma=(abs(mean) / sem if sem else float("inf")),
                signs="".join("+" if v > 0 else ("0" if v == 0 else "-") for v in dl),
                p=float(binomtest(pos, pos + neg).pvalue) if (pos + neg) else float("nan"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e82_three_sizes.json")
    args = ap.parse_args()

    data = {}
    for label, path, cs in SIZES:
        d = load(path)
        if d is None:
            print(f"   {label:<9} absent ({path})")
            continue
        data[label] = d
    if len(data) < 2:
        raise SystemExit("need at least two sizes on disk")

    print("=" * 104)
    print("1. THE THREE SIZES")
    print("=" * 104)
    print(f"   {'size':<9}{'n':>4}{'mean r':>10}{'mean r^2':>10}{'median r':>10}"
          f"{'seeds +':>10}{'all seeds > 0':>15}{'distinct partitions':>21}")
    summary = {}
    for label, d in data.items():
        rows = d["rows"]
        r = [x["pearson"] for x in rows]
        seeds = [v for x in rows for v in x["per_seed"]]
        #: two rows can be the SAME partition at a given size -- this vocabulary crowds the fine end --
        #: and the pressure mean is the observable that exposes it without re-deriving the labels
        means = [round(x["pressure_mean"], 9) for x in rows]
        distinct = len(set(means))
        summary[label] = dict(n=len(rows), mean_r=float(np.mean(r)), mean_r2=float(np.mean([x["r2"] for x in rows])),
                              median_r=float(np.median(r)), all_seeds_positive=bool(all(v > 0 for v in seeds)),
                              n_seeds=len(seeds), distinct_partitions=distinct)
        print(f"   {label:<9}{len(rows):>4}{np.mean(r):>10.3f}"
              f"{np.mean([x['r2'] for x in rows]):>10.3f}{np.median(r):>10.3f}"
              f"{sum(1 for v in seeds if v > 0):>7}/{len(seeds):<2}"
              f"{str(all(v > 0 for v in seeds)):>15}{distinct:>21}")
        if distinct < len(rows):
            dup = [x["label"] for x in rows if means.count(round(x["pressure_mean"], 9)) > 1]
            print(f"   {'':<9}   duplicate rows: {dup}")

    print()
    print("=" * 104)
    print("2. THE SAME PARTITION LABELS ACROSS SIZES")
    print("=" * 104)
    labels = [x["label"] for x in next(iter(data.values()))["rows"]]
    hdr = "   " + f"{'partition':<22}" + "".join(f"{l:>10}" for l in data)
    print(hdr)
    for lab in labels:
        cells = []
        for label, d in data.items():
            m = [x for x in d["rows"] if x["label"] == lab]
            cells.append(f"{m[0]['pearson']:>+10.3f}" if m else f"{'absent':>10}")
        print(f"   {lab:<22}" + "".join(cells))

    print()
    print("=" * 104)
    print("3. PAIRED DIFFERENCES BETWEEN SIZES, ON THE SHARED LABELS")
    print("=" * 104)
    keys = list(data)
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        ra = {x["label"]: x["pearson"] for x in data[a]["rows"]}
        rb = {x["label"]: x["pearson"] for x in data[b]["rows"]}
        shared = [l for l in ra if l in rb]
        dl = np.asarray([rb[l] - ra[l] for l in shared], float)
        st = paired_stats(dl)
        print(f"   {b} - {a}: mean difference {st['delta']:+.4f} +/- {st['sem']:.4f} = "
              f"{st['sigma']:.2f}sigma   signs {st['signs']}   p = {st['p']:.4f}   (n = {st['n']})")
        print(f"      mean r: {np.mean([ra[l] for l in shared]):+.3f} -> {np.mean([rb[l] for l in shared]):+.3f}"
              f"   (shared labels only)")

    print()
    print("=" * 104)
    print("4. AND THE COMPARISON THE MECHANISM IS FOR")
    print("=" * 104)
    print(f"   the bare alignment's co-movement, same nine partitions, same design: mean r "
          f"{ALIGNMENT_MEAN_R:+.3f}")
    for label, s in summary.items():
        print(f"   {label:<9} pressure {s['mean_r']:+.3f} (r^2 {s['mean_r2']:.3f})   "
              f"beats it: {s['mean_r'] > ALIGNMENT_MEAN_R}")

    out = {"sizes": summary, "artifacts": {l: p for l, p, _ in SIZES},
           "alignment_mean_r": ALIGNMENT_MEAN_R}
    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
