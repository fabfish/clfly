"""E87 -- the shared-draw correction, applied to the two comparisons that used a sign record across partitions as evidence.

`e82` compared the pressure mechanism's co-movement at three circuit sizes and reported the step from
d = 1307 to d = 1874 as **3.29σ with eight of nine partitions declining**. That treats the nine partitions
as nine independent observations of the difference. **They are not:** all nine partitions of one run see the
**same six relabellings**, so any draw-level effect enters every partition's correlation and therefore
every difference — and an eight-of-nine sign pattern is exactly what a shared-draw effect produces. The
right resampling unit is the **draw**, not the partition.

The same question applies to `e81`'s headline, which the paper quotes: the paired
`pressure − alignment` co-movement was **+0.736 ± 0.061, nine of nine positive, p = 0.0039**, also a sign
record across nine partitions on shared draws. **But that comparison has a protection this one does not:**
both arms are measured on the *same* draws, so a draw-favourability effect that inflates or deflates both
correlations cancels in their difference. A comparison of two *independent runs* has no such cancellation.

This script bootstraps over draws for both, so the two are read with the right interval:

* `e82`'s size steps, resampling draws independently within each run;
* `e81`'s paired `pressure − alignment`, resampling draws **once** and recomputing both arms on the same
  resample — which is what makes the cancellation visible.

    python -m experiments.e87_paired_co_movement_bootstrap
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

SIZES = [
    ("d = 952", "runs/e82_pressure_comovement_d300.json"),
    ("d = 1307", "runs/e81_pressure_comovement.json"),
    ("d = 1874", "runs/e82_pressure_comovement_d1500.json"),
]

#: The alignment run.  `e88` is `e75` re-run after its output was fixed to keep the per-(draw, seed)
#: alignment values; `e75`'s own artifact predates that fix and cannot be used for this check.
ALIGNMENT = "runs/e88_alignment_perseed_rerun.json"
PRESSURE_AT_D1307 = "runs/e81_pressure_comovement.json"


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def residualise(x: np.ndarray, seeds: np.ndarray) -> np.ndarray:
    out = x.astype(float).copy()
    for s in np.unique(seeds):
        m = seeds == s
        out[m] -= out[m].mean()
    return out


def r_on_draws(vals: np.ndarray, other: np.ndarray, draw: np.ndarray,
               seed: np.ndarray, draw_idx: np.ndarray) -> float:
    take = np.concatenate([np.where(draw == d)[0] for d in draw_idx])
    a, b, s = vals[take], other[take], seed[take]
    ar, br = residualise(a, s), residualise(b, s)
    if ar.std() == 0 or br.std() == 0:
        return float("nan")
    return float(np.corrcoef(ar, br)[0, 1])


def mean_r(rows, value_key, other_key, draw_idx):
    return float(np.nanmean([r_on_draws(np.asarray(r[value_key], float),
                                        np.asarray(r[other_key], float),
                                        np.asarray(r["draw_index"], int),
                                        np.asarray(r["seed_index"], int), draw_idx)
                             for r in rows]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e87_paired_co_movement_bootstrap.json")
    ap.add_argument("--n-boot", type=int, default=4000)
    args = ap.parse_args()

    out: dict = {}
    arts = {label: load(path) for label, path in SIZES}

    print("=" * 108)
    print("1. THE SIZE STEPS, WITH THE DRAWS AS THE RESAMPLING UNIT")
    print("=" * 108)
    print("   the nine partitions share their six draws, so a sem over the nine understates the")
    print("   uncertainty of their mean; resampling draws is the unit that respects that.\n")
    rng = np.random.default_rng(0)
    keys = [k for k, v in arts.items() if v is not None]
    out["size_steps"] = []
    for i in range(len(keys) - 1):
        a, b = keys[i], keys[i + 1]
        ra, rb = arts[a]["rows"], arts[b]["rows"]
        n_d = len(set(np.asarray(ra[0]["draw_index"], int)))
        per_part = np.array([x["pearson"] for x in rb]) - np.array([x["pearson"] for x in ra])
        naive_sem = float(per_part.std(ddof=1) / np.sqrt(per_part.size))
        boot = np.empty(args.n_boot)
        for j in range(args.n_boot):
            ia = rng.integers(0, n_d, n_d)
            ib = rng.integers(0, n_d, n_d)
            boot[j] = (mean_r(rb, "pressure_values", "excess_values", ib)
                       - mean_r(ra, "pressure_values", "excess_values", ia))
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print(f"   {b} - {a}")
        print(f"      independent-partition sem   {naive_sem:.4f}   ->  "
              f"{abs(per_part.mean())/naive_sem:.2f} sigma, signs "
              f"{''.join('+' if v > 0 else '-' for v in per_part)}")
        print(f"      draw bootstrap              {boot.std(ddof=1):.4f}   ->  "
              f"{abs(boot.mean())/boot.std(ddof=1):.2f} sigma")
        print(f"      mean {per_part.mean():+.4f}, 95% interval [{lo:+.4f}, {hi:+.4f}], "
              f"{100*(boot < 0).mean():.1f}% of resamples below zero")
        print(f"      -> the draw interval is {boot.std(ddof=1)/naive_sem:.1f}x the partition sem, and "
              f"{'EXCLUDES' if (lo > 0 or hi < 0) else 'INCLUDES'} zero")
        out["size_steps"].append(dict(a=a, b=b, mean=float(per_part.mean()), naive_sem=naive_sem,
                                      boot_sd=float(boot.std(ddof=1)), lo=float(lo), hi=float(hi),
                                      frac_below_zero=float((boot < 0).mean()),
                                      signs="".join('+' if v > 0 else '-' for v in per_part)))

    print()
    print("=" * 108)
    print("2. e81's PAIRED `pressure - alignment`, WHERE THE SHARED DRAW SHOULD CANCEL")
    print("=" * 108)
    print("   both arms are measured on the SAME draws, so a draw-favourability effect that moves both")
    print("   correlations cancels in their difference.  Bootstrapping draws once and recomputing BOTH")
    print("   arms on that resample is the check that it does.\n")
    al, pr = load(ALIGNMENT), load(PRESSURE_AT_D1307)
    if al is None or pr is None:
        print("   artifacts absent")
    elif "alignment_values" not in al["rows"][0]:
        #: `e75`'s first version dropped these fields from its output "to keep the file small", and the
        #: fix to the script does not retroactively add them to the artifact it already wrote.  The check
        #: therefore cannot run from disk and says so, rather than reporting a number computed from
        #: something else.
        print("   CANNOT RUN: `runs/e75_task_pair_spread.json` stores no per-(draw, seed) alignment")
        print("   values -- its first version filtered them out to keep the file small, and the fix to")
        print("   the script does not add them back to the artifact it already wrote.  Re-run `e75` to")
        print("   enable this check; until then the paired 9-of-9 stands unexamined for shared draws.")
        out["e81_paired"] = dict(available=False,
                                 reason="e75's artifact predates its own per-(draw, seed) storage")
    else:
        a_by = {r["label"]: r for r in al["rows"]}
        p_by = {r["label"]: r for r in pr["rows"]}
        labels = [l for l in p_by if l in a_by]
        per_part = np.array([p_by[l]["pearson"] - a_by[l]["pearson"] for l in labels])
        naive_sem = float(per_part.std(ddof=1) / np.sqrt(per_part.size))
        pos, neg = int((per_part > 0).sum()), int((per_part < 0).sum())
        rng2 = np.random.default_rng(1)
        n_d = len(set(np.asarray(p_by[labels[0]]["draw_index"], int)))
        boot = np.empty(args.n_boot)
        for j in range(args.n_boot):
            idx = rng2.integers(0, n_d, n_d)
            rp = mean_r([p_by[l] for l in labels], "pressure_values", "excess_values", idx)
            ra = mean_r([a_by[l] for l in labels], "alignment_values", "excess_values", idx)
            boot[j] = rp - ra
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print(f"   n = {len(labels)} partitions, signs "
              f"{''.join('+' if v > 0 else '-' for v in per_part)}")
        print(f"      paired mean difference      {per_part.mean():+.4f}")
        print(f"      independent-partition sem   {naive_sem:.4f}   ->  "
              f"{per_part.mean()/naive_sem:.2f} sigma (sign p = "
              f"{binomtest(pos, pos+neg).pvalue:.4f})")
        print(f"      shared-draw bootstrap       {boot.std(ddof=1):.4f}   ->  "
              f"{boot.mean()/boot.std(ddof=1):.2f} sigma")
        print(f"      95% interval [{lo:+.4f}, {hi:+.4f}], {100*(boot > 0).mean():.1f}% above zero")
        print(f"      -> the draw interval is {boot.std(ddof=1)/naive_sem:.2f}x the partition sem, and "
              f"{'EXCLUDES' if (lo > 0 or hi < 0) else 'INCLUDES'} zero")
        out["e81_paired"] = dict(n=len(labels), mean=float(per_part.mean()), naive_sem=naive_sem,
                                 boot_sd=float(boot.std(ddof=1)), lo=float(lo), hi=float(hi),
                                 sign_p=float(binomtest(pos, pos + neg).pvalue),
                                 signs="".join('+' if v > 0 else '-' for v in per_part))

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
