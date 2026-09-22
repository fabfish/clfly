"""E55 — the seed resolution of the neuron-level excess, at n = 12 instead of n = 3.

Plan rule 3 prescribes the **absolute** excess over the oracle instead of the relative gap, on the
grounds that the relative gap "has a standard deviation comparable to its own mean", and it closes
with *"at current settings, excess differences below ~0.05 are not resolvable"*. That number has been
carried since the rule was written from a handful of seeds.

`e42` supplies **twelve** seeds of one configuration (cs = 800, `real`, seven `kappa`), so both halves
of that rule can be measured rather than asserted. This script asks:

1. **Is the across-seed spread comparable to the mean for the absolute metric too, or only for the
   relative gap?** Rule 3 implies the absolute metric is the fix for the variance; if its CV is also
   ~1, the fix is for the *ratio* pathology and not for the spread.
2. **What is the unpaired resolution at n = 12**, and what would it be at n = 3?
3. **How does it compare with the paired resolution** the project actually uses for its contrasts?

    python -m experiments.e55_seed_resolution_of_excess
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

#: The one configuration with twelve seeds, then three-seed sections for the n-dependence.
SECTIONS = [
    ("real cs800, 12 seeds", "runs/e42_e5_reseed.json"),
    ("real cs800, 3 seeds", "runs/e5_anisotropy.json"),
    ("real cs300, 3 seeds", "runs/e37_kappa_real_cs300.json"),
    ("swap2 cs800, 3 seeds", "runs/e37_kappa_swap2_cs800.json"),
    ("swap2 cs300, 3 seeds", "runs/e37_kappa_swap2_cs300.json"),
]

#: The effect sizes the project actually tries to resolve, for context.
BASIS_DELTA_RANGE = (0.0015, 0.004)   # rung-to-rung basis deltas on the neuron ladder
C1_CONTRAST_RANGE = (0.0022, 0.0353)  # the swap-family contrasts


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def excess_of(pt: dict) -> float:
    """The absolute excess, stored or derived.

    `e42` and later store `excess_ewc` directly; `e5_anisotropy.json` predates the field, so the same
    quantity is recovered as ``gap_ewc x oracle_final`` -- exact, because `gap_vs_oracle` returns a
    relative excess of final average error.  `e41` established that the two agree bit-for-bit on the
    runs that carry both.
    """
    if "excess_ewc" in pt:
        return float(pt["excess_ewc"])
    return float(pt["gap_ewc"]) * float(pt["oracle_final"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e55_seed_resolution.json")
    args = ap.parse_args()

    out: dict = {"sections": {}}

    print("=" * 100)
    print("1. THE ABSOLUTE METRIC'S ACROSS-SEED SPREAD, AGAINST THE RELATIVE ONE")
    print("=" * 100)
    print("   rule 3's stated reason for preferring the absolute excess is that the relative gap's")
    print("   sd is comparable to its own mean.  If the absolute metric's CV is also ~1, the rule is")
    print("   a fix for the RATIO and not for the spread, and should say so.\n")

    for label, path in SECTIONS:
        d = load(path)
        if d is None:
            continue
        P = d["points"]
        seeds = sorted({p["seed"] for p in P})
        ks = sorted({p["kappa"] for p in P})
        print(f"   {label}   (n seeds = {len(seeds)})")
        print(f"     {'kappa':>6}{'abs mean':>10}{'abs sd':>10}{'abs CV':>8}"
              f"{'rel mean':>10}{'rel sd':>10}{'rel CV':>8}")
        rows = []
        for k in ks:
            a = np.array([excess_of(p) for p in P if p["kappa"] == k], dtype=float)
            g = np.array([p["gap_ewc"] for p in P if p["kappa"] == k], dtype=float)
            if len(a) < 2:
                continue
            cv_a = float(a.std(ddof=1) / abs(a.mean())) if a.mean() else float("nan")
            cv_g = float(g.std(ddof=1) / abs(g.mean())) if g.mean() else float("nan")
            print(f"     {k:>6}{a.mean():>10.5f}{a.std(ddof=1):>10.5f}{cv_a:>8.2f}"
                  f"{g.mean():>10.3f}{g.std(ddof=1):>10.3f}{cv_g:>8.2f}")
            rows.append(dict(kappa=float(k), n_seeds=len(a),
                             abs_mean=float(a.mean()), abs_sd=float(a.std(ddof=1)), abs_cv=cv_a,
                             rel_mean=float(g.mean()), rel_sd=float(g.std(ddof=1)), rel_cv=cv_g))
        cv_a_all = [r["abs_cv"] for r in rows]
        cv_g_all = [r["rel_cv"] for r in rows]
        print(f"     CV across kappa: absolute {min(cv_a_all):.2f}-{max(cv_a_all):.2f}, "
              f"relative {min(cv_g_all):.2f}-{max(cv_g_all):.2f}")
        out["sections"][label] = dict(n_seeds=len(seeds), kappas=rows,
                                      abs_cv_range=[min(cv_a_all), max(cv_a_all)],
                                      rel_cv_range=[min(cv_g_all), max(cv_g_all)])
        print()

    print("=" * 100)
    print("2. THE UNPAIRED RESOLUTION, AND WHAT n BUYS")
    print("=" * 100)
    print("   'minimum detectable' is 2.8 x sem, i.e. 80% power at a two-sided 5% test\n")
    main_label = SECTIONS[0][0]
    rec = out["sections"].get(main_label)
    if rec:
        sds = np.array([r["abs_sd"] for r in rec["kappas"]])
        sd_typ = float(np.median(sds))
        print(f"   {main_label}: across-seed sd of the absolute excess, median over kappa = "
              f"{sd_typ:.5f}")
        print(f"     (range across kappa: {sds.min():.5f} to {sds.max():.5f})\n")
        print(f"     {'n seeds':>8}{'sem':>10}{'min detectable':>17}")
        for n in (3, 6, 12, 24, 48):
            sem = sd_typ / np.sqrt(n)
            print(f"     {n:>8}{sem:>10.5f}{2.8 * sem:>17.5f}")
        print(f"\n   the plan's rule 3 says 'differences below ~0.05 are not resolvable'.")
        print(f"   At n = 12 that figure is **{2.8 * sd_typ / np.sqrt(12):.4f}**, and even at n = 3 it is"
              f" {2.8 * sd_typ / np.sqrt(3):.4f} —")
        print(f"   so the ~0.05 was conservative by a factor of "
              f"{0.05 / (2.8 * sd_typ / np.sqrt(12)):.1f}x at n = 12, or"
              f" {0.05 / (2.8 * sd_typ / np.sqrt(3)):.1f}x at n = 3.")
        out["resolution"] = {"median_across_seed_sd": sd_typ,
                             "min_detectable": {str(n): 2.8 * sd_typ / np.sqrt(n)
                                                for n in (3, 6, 12, 24, 48)}}

    print()
    print("=" * 100)
    print("3. THE TWO RESOLUTIONS THE PROJECT ACTUALLY USES, AS A PAIR")
    print("=" * 100)
    print("   Everything in section 2 is the UNPAIRED resolution: two arms whose seeds are")
    print("   independent.  The project's contrasts are within-seed DIFFERENCES, whose resolution is")
    print("   set by the sd of the difference rather than of either arm.  Measured on `e48`:\n")
    cs = load("runs/e48_cs800_perseed.json")
    if cs is not None:
        a = np.array(cs["topologies"]["swap0.5"]["diagonal(EWC)"]["analytic"]["excess_per_seed"])
        b = np.array(cs["topologies"]["swap2"]["diagonal(EWC)"]["analytic"]["excess_per_seed"])
        d = b - a
        n = len(d)
        sd_a, sd_b, sd_d = a.std(ddof=1), b.std(ddof=1), d.std(ddof=1)
        r = float(np.corrcoef(a, b)[0, 1])
        unpaired_sem = float(np.hypot(sd_a, sd_b) / np.sqrt(n))
        paired_sem = sd_d / np.sqrt(n)
        print(f"   cs = 800, swap0.5 and swap2, {n} seeds:")
        print(f"     per-seed sd of the arms        {sd_a:.5f} and {sd_b:.5f}")
        print(f"     per-seed sd of their DIFFERENCE {sd_d:.5f}   (arm correlation r = {r:+.2f})")
        print(f"     min detectable, arms treated independently  2.8 x {unpaired_sem:.5f} = "
              f"{2.8 * unpaired_sem:.5f}")
        print(f"     min detectable, as a within-seed difference 2.8 x {paired_sem:.5f} = "
              f"{2.8 * paired_sem:.5f}")
        print(f"     -> a factor of {unpaired_sem / paired_sem:.1f}x")
        print(f"\n   And note what that factor is NOT: the arms' correlation is only r = {r:+.2f}, so")
        print(f"   pairing on the seed cancels little.  The resolution comes from the DIFFERENCE being")
        print(f"   a stable quantity while each arm is not -- which is a statement about what is being")
        print(f"   compared, not about the design.")
        out["resolution"]["contrast_example"] = dict(
            n=n, arm_sd=[float(sd_a), float(sd_b)], diff_sd=float(sd_d), arm_correlation=r,
            min_detectable_independent=float(2.8 * unpaired_sem),
            min_detectable_within_seed=float(2.8 * paired_sem),
            factor=float(unpaired_sem / paired_sem))
    print(f"\n   effect sizes for context: basis deltas the neuron ladder resolves "
          f"{BASIS_DELTA_RANGE[0]:.4f}-{BASIS_DELTA_RANGE[1]:.4f}; the C1 contrast's span "
          f"{C1_CONTRAST_RANGE[0]:.4f}-{C1_CONTRAST_RANGE[1]:.4f}.")
    print("   Those are BELOW the unpaired resolution at n = 12 (section 2) and well above the")
    print("   within-seed one.  So rule 3 needs a pair of numbers, not one: quoting the unpaired")
    print("   figure alone reads as though a 0.0015 basis delta were unmeasurable, and the project")
    print("   has measured thousands of them.")

    print()
    print("   And a third number, which argues against quoting any single figure at all: the SAME")
    print("   topology's across-seed spread depends on the drive construction by an order of")
    print("   magnitude.  `excess(real)` at cs = 800 has an across-seed sd of "
          f"{float(np.median([r['abs_sd'] for r in rec['kappas']])):.5f}")
    print("   in `e42`'s sweep (uniform drive at kappa = 0), and 0.00175 in `e48`'s run, which uses")
    print("   `e2`'s default drive instead.  Both are `real` at cs = 800 with the same six-or-more")
    print("   seeds; the task construction is what differs.  So a resolution figure is only")
    print("   meaningful with the configuration attached, and 'at current settings' in rule 3 is")
    print("   doing more work than it looks.")
    if cs is not None:
        ra = np.array(cs["topologies"]["real"]["diagonal(EWC)"]["analytic"]["excess_per_seed"])
        out["resolution"]["real_across_constructions"] = {
            "e42_uniform_drive_sd": float(np.median([r["abs_sd"] for r in rec["kappas"]])),
            "e48_default_drive_sd": float(ra.std(ddof=1))}

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
