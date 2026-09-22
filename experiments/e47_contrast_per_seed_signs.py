"""E47 — is the C1 contrast seed-robust?  Leave-one-seed-out on every published sigma.

`e41`, `e45` and the `e5` line in general have established that in this project a *pooled* statistic
can be carried by one seed of three. The C1 topology contrasts are pooled over task seeds too, and
the most-quoted of them — the `swap0.5 -> swap2` contrast at cs = 800, reported at **32.7 sigma** —
carries the whole interference refutation.

So the same question is asked of them, which costs nothing because the per-seed values were stored:
for each published contrast, (a) the per-seed signs, (b) the paired sigma, and (c) **the
leave-one-seed-out sigma and sign** — the direct test of whether a single seed is doing the work.

It also checks the storage rule while it is here. Plan rule 8 says store per-seed values so a run can
be re-analysed paired; `runs/e2_analytic.json` — the artifact behind the 32.7 sigma figure — has
`excess_per_seed` for its `swap2` arm and **not** for its `swap0.5` arm, so that contrast cannot be
re-examined per seed at all. That is exactly the omission rule 8 exists to prevent, on the project's
most-quoted number.

    python -m experiments.e47_contrast_per_seed_signs
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

#: (label, path) for every run that may hold per-seed excesses for both arms of a contrast.
RUNS = [
    ("cs300", "runs/e21_e2_paired.json"),
    ("cs400", "runs/e26_size400.json"),
    ("cs500", "runs/e26_size500.json"),
    ("cs600", "runs/e26_size600.json"),
    ("cs700", "runs/e26_size700.json"),
    ("cs800", "runs/e2_analytic.json"),
]

PAIR = ("swap0.5", "swap2")


def per_seed(entry, topology: str):
    topo = entry["topologies"].get(topology)
    if topo is None:
        return None
    a = topo["diagonal(EWC)"]["analytic"]
    return a.get("excess_per_seed")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e47_contrast_per_seed_signs.json")
    args = ap.parse_args()

    print("=" * 100)
    print("PER-SEED DISSECTION OF THE C1 CONTRAST  (", PAIR[1], "minus", PAIR[0], ")")
    print("=" * 100)
    out: dict = {"pair": list(PAIR), "rows": [], "unusable": []}
    print(f"\n  {'size':<8}{'n':>3}{'mean delta':>12}{'paired sigma':>14}"
          f"{'signs (seed order)':>22}{'max seed leverage':>19}{'drop-one sigma':>16}"
          f"{'flips?':>8}")
    print("  'max seed leverage' is the largest change in the mean from dropping one seed, in")
    print("  units of the all-seeds sem -- the direct measure of whether one seed carries the")
    print("  contrast.  Sigma alone is a poor detector: it is a mean/sem ratio, so removing a seed")
    print("  can raise it by collapsing the sem faster than the mean.")

    for label, path in RUNS:
        p = Path(path)
        if not p.exists():
            print(f"  {label:<8}(absent)")
            continue
        with open(p, encoding="utf-8") as fh:
            entry = json.load(fh)
        a, b = per_seed(entry, PAIR[0]), per_seed(entry, PAIR[1])
        if a is None or b is None:
            missing = [PAIR[i] for i, v in enumerate((a, b)) if v is None]
            print(f"  {label:<8}NO per-seed for {missing} -> this contrast cannot be examined")
            out["unusable"].append({"label": label, "path": path, "missing": missing})
            continue
        a, b = np.array(a, dtype=float), np.array(b, dtype=float)
        n = min(len(a), len(b))
        a, b = a[:n], b[:n]
        delta = b - a
        sem = float(delta.std(ddof=1) / np.sqrt(n))
        sigma = float(delta.mean() / sem) if sem else float("nan")
        signs = "".join("+" if d > 0 else "-" for d in delta)
        loo_sigma, leverage, loo_flip = [], 0.0, False
        for k in range(n):
            keep = np.delete(delta, k)
            if keep.size < 3:
                continue
            s = float(keep.std(ddof=1) / np.sqrt(keep.size))
            sg = float(keep.mean() / s) if s else float("nan")
            loo_sigma.append(abs(sg))
            leverage = max(leverage, abs(float(keep.mean()) - float(delta.mean())) / sem)
            if np.sign(keep.mean()) != np.sign(delta.mean()):
                loo_flip = True
        loo_txt = (f"[{min(loo_sigma):.1f}, {max(loo_sigma):.1f}]" if loo_sigma else "n/a")
        print(f"  {label:<8}{n:>3}{delta.mean():>+12.5f}{sigma:>+14.2f}"
              f"{signs:>22}{leverage:>18.2f}{loo_txt:>16}{str(loo_flip):>8}")
        out["rows"].append(dict(label=label, path=path, n=n, delta_mean=float(delta.mean()),
                                sem=sem, sigma=sigma, signs=signs,
                                max_seed_leverage=leverage,
                                leave_one_out_abs_sigma=loo_sigma, leave_one_out_flips=loo_flip,
                                per_seed=delta.tolist()))

    print("\n  Sign unanimity plus a small leverage is a seed-robust contrast.  A leverage near or")
    print("  above 1 means one seed moves the mean by a whole standard error on its own -- which is")
    print("  what the `e5` association failed on, at one strong seed in three.")

    print()
    print("=" * 100)
    print("SIGN UNANIMITY, AGAINST WHAT A FAIR COIN WOULD GIVE")
    print("=" * 100)
    print("  if the contrast were a fixed effect measured with noise, its per-seed signs would be")
    print("  unanimous; if the mean is small relative to the seed spread, they need not be.\n")
    print(f"  {'size':<8}{'n':>3}{'same-sign':>11}{'P(unanimous | fair coin)':>27}{'verdict':>12}")
    total_same = total_n = 0
    for r in out["rows"]:
        k = max(r["signs"].count("+"), r["signs"].count("-"))
        n = len(r["signs"])
        p_unanim = 2 ** (1 - n)  # two-sided probability of a unanimous split
        verdict = "unanimous" if k == n else "split"
        print(f"  {r['label']:<8}{n:>3}{f'{k}/{n}':>11}{p_unanim:>27.4f}{verdict:>12}")
        total_same += k
        total_n += n
    if total_n:
        print(f"\n  pooled over the usable sizes: {total_same}/{total_n} seeds agree with their")
        print(f"  contrast's sign, i.e. {total_same / total_n:.0%}. A contrast that is a fixed")
        print("  effect measured with noise should be near 100%.")

    print()
    print("=" * 100)
    print("RULE 8 COMPLIANCE: WHICH CONTRASTS CAN BE RE-EXAMINED AT ALL")
    print("=" * 100)
    if out["unusable"]:
        for u in out["unusable"]:
            print(f"  {u['label']:<8} {u['path']} is missing per-seed values for {u['missing']}")
        print("\n  so the cs = 800 contrast -- the 32.7 sigma figure that carries the interference")
        print("  refutation -- has to be quoted as it stands, and its paired form cannot be checked")
        print("  per seed. Note that its sigma was reported UNPAIRED for that reason, which is")
        print("  visible in the published table, but the underlying omission is the storage one.")
    else:
        print("  every contrast in the sweep has per-seed values for both arms.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
