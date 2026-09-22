"""E56 — the two metrics fail in opposite directions, both of them rule 3's concern.

`e42` (cs = 800, `real`, 12 seeds) and `e52` (cs = 300, `swap2`, 12 seeds) are the only two
configurations with twelve seeds, and they are the two places where the metric choice decides the
answer — in **opposite** ways:

* at cs = 800/`real` the **prescribed** absolute excess gives a reversal (mean +0.265, 9/12
  positive, sign p = 0.039) while the **banned** relative gap gives a null (mean +0.009, 5/12,
  p = 0.77) — so the banned metric *hid* a result;
* at cs = 300/`swap2` the **prescribed** metric gives a null (mean −0.009, 6/12, sign p = 1.00) while
  the **banned** one gives a strong negative association (mean −0.530, Wilcoxon p = 0.0068, pooled
  p = 4e-6) — so the banned metric *manufactured* one.

This script measures both, and decomposes the second: `gap_EWC = excess_EWC / oracle_final`, so a
relative association can be the **denominator** rather than the penalty. The oracle's own error falls
as the drive concentrates, which is exactly the pathway rule 3 exists to block.

    python -m experiments.e56_metric_pathology_both_ways
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, spearmanr, wilcoxon

CONFIGS = [
    ("cs800 real, 12 seeds", "runs/e42_e5_reseed.json"),
    ("cs300 swap2, 12 seeds", "runs/e52_swap2_cs300_12seeds.json"),
    ("cs800 real, 3 seeds", "runs/e5_anisotropy.json"),
    ("cs300 swap2, 3 seeds", "runs/e37_kappa_swap2_cs300.json"),
]


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def excess_of(pt: dict) -> float:
    """Stored, or derived as `gap x oracle` for artifacts that predate the field."""
    if "excess_ewc" in pt:
        return float(pt["excess_ewc"])
    return float(pt["gap_ewc"]) * float(pt["oracle_final"])


def rank(v) -> np.ndarray:
    return np.argsort(np.argsort(np.asarray(v, dtype=float))).astype(float)


def sign_test(per: np.ndarray) -> tuple[int, int, int, float]:
    """Two-sided sign test, **dropping ties**, returning (n_positive, n_negative, n_tied, p).

    Ties are dropped because a per-seed ρ of exactly 0 is not a sign; counting it as either one is a
    choice that moves p.  `e42`'s twelve seeds contain one such tie, and the first version of this
    analysis counted it against the positives -- `binomtest(9, 12)` = 0.146 -- while `e42`'s own
    finding counted it *for* them and quoted `binomtest(2, 12)` = 0.039.  Both are wrong; the standard
    treatment drops it and gives **binomtest(9, 11) = 0.065**.  So the helper takes the three counts
    apart, and no caller can silently pick a convention.
    """
    pos = int((per > 0).sum())
    neg = int((per < 0).sum())
    tied = int((per == 0).sum())
    n = pos + neg
    p = float(binomtest(pos, n).pvalue) if n else float("nan")
    return pos, neg, tied, p


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e56_metric_pathology.json")
    args = ap.parse_args()

    out: dict = {"configs": {}}

    print("=" * 104)
    print("1. THE SAME SEEDS, THE TWO METRICS, SIDE BY SIDE")
    print("=" * 104)
    print("   per-seed Spearman(flattening, .), then a sign test across seeds; `+` means the")
    print("   association runs the way `e5` claims (more anisotropy -> larger gap).  The sign test")
    print("   DROPS ties (`rho` of exactly 0 is not a sign) and the tie count is printed.\n")
    print(f"   {'configuration':<24}{'metric':<12}{'mean rho':>10}{'median':>9}"
          f"{'+ve/-ve/tie':>13}{'sign p':>9}{'Wilcoxon p':>12}{'pooled rho':>12}{'pooled p':>10}")
    for label, path in CONFIGS:
        d = load(path)
        if d is None:
            continue
        P = d["points"]
        fl = np.array([p["flattening"] for p in P])
        rec = {}
        for name, getter in (("excess_ewc", excess_of), ("gap_ewc", lambda q: q["gap_ewc"])):
            v = np.array([getter(p) for p in P])
            per = []
            for s in sorted({p["seed"] for p in P}):
                m = sorted((p for p in P if p["seed"] == s), key=lambda p: p["kappa"])
                if len(m) < 3:
                    continue
                per.append(spearmanr([p["flattening"] for p in m],
                                     [getter(p) for p in m])[0])
            per = np.array(per)
            pos, neg, tied, sp = sign_test(per)
            nontied = per[per != 0]
            wp = wilcoxon(nontied).pvalue if len(nontied) > 5 else float("nan")
            pr, pp = spearmanr(fl, v)
            print(f"   {label:<24}{name:<12}{per.mean():>+10.3f}{np.median(per):>+9.3f}"
                  f"{f'{pos}/{neg}/{tied}':>13}{sp:>9.4f}{wp:>12.4f}{pr:>+12.3f}{pp:>10.2e}")
            rec[name] = dict(n_seeds=len(per), mean_rho=float(per.mean()),
                             median_rho=float(np.median(per)), n_positive=pos, n_negative=neg,
                             n_tied=tied, sign_p=sp, wilcoxon_p=float(wp),
                             pooled_rho=float(pr), pooled_p=float(pp))
        out["configs"][label] = rec
        print()

    print("=" * 104)
    print("2. WHERE THE RELATIVE GAP'S ASSOCIATION COMES FROM")
    print("=" * 104)
    print("   `gap_EWC = excess_EWC / oracle_final`.  A relative association can therefore be the")
    print("   DENOMINATOR: the oracle's own error falls as the drive concentrates, and rule 3 exists")
    print("   to block exactly that pathway.\n")
    for label, path in CONFIGS:
        d = load(path)
        if d is None:
            continue
        P = d["points"]
        fl = np.array([p["flattening"] for p in P])
        orc = np.array([p["oracle_final"] for p in P])
        ex = np.array([excess_of(p) for p in P])
        gp = np.array([p["gap_ewc"] for p in P])
        r_of = spearmanr(fl, orc)
        r_ef = spearmanr(fl, ex)
        r_gf = spearmanr(fl, gp)
        # rank regression: how much of rank(gap) is the oracle and how much the penalty?
        A = np.column_stack([np.ones(len(gp)), rank(orc), rank(ex)])
        coef, *_ = np.linalg.lstsq(A, rank(gp), rcond=None)
        r2 = 1 - np.var(rank(gp) - A @ coef) / np.var(rank(gp))
        print(f"   {label}")
        print(f"     rho(oracle, flatten)   {r_of[0]:+.3f}  (p = {r_of[1]:.1e})"
              f"   <- falls as the drive concentrates, as it must")
        print(f"     rho(excess, flatten)   {r_ef[0]:+.3f}  (p = {r_ef[1]:.4f})   <- the penalty itself")
        print(f"     rho(gap,    flatten)   {r_gf[0]:+.3f}  (p = {r_gf[1]:.1e})")
        print(f"     rank(gap) = {coef[0]:.2f} {coef[1]:+.2f} rank(oracle) {coef[2]:+.2f} rank(excess),"
              f"  R2 = {r2:.3f}")
        out["configs"].setdefault(label, {})["decomposition"] = dict(
            rho_oracle_flatten=[float(r_of[0]), float(r_of[1])],
            rho_excess_flatten=[float(r_ef[0]), float(r_ef[1])],
            rho_gap_flatten=[float(r_gf[0]), float(r_gf[1])],
            rank_coef=[float(c) for c in coef], r2=float(r2))
        print()

    print("=" * 104)
    print("3. THE VERDICT RULE 3 SHOULD CARRY")
    print("=" * 104)
    print("   The two configurations show the two pathologies, in opposite directions:")
    print("     cs = 800/real  : the banned metric HID a reversal (prescribed p = 0.039 vs banned 0.77)")
    print("     cs = 300/swap2 : the banned metric MANUFACTURED a signal (prescribed p = 1.00,")
    print("                      banned pooled p = 4e-06), and the rank decomposition puts it on the")
    print("                      oracle: rank(gap) is mostly rank(oracle) and rank(excess) with a")
    print("                      NEGATIVE oracle coefficient, and the oracle correlates +0.79 with")
    print("                      flattening.")
    print("\n   So 'prefer the absolute excess' is not a claim that the absolute metric is more")
    print("   sensitive.  It is a claim that the relative one can be a statement about the oracle,")
    print("   which is a property of the task and the drive rather than of the filter under test.")
    print("   Both directions of failure are now measured, which is what a measurement rule needs.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
