"""E65 -- the `swap0.5` realization sweep, which turns the C1 contrast's rule-sigma from a lower bound into a measurement.

`e59` showed that every sigma in the C1 family is one of two: a sigma **about the particular graphs
drawn** (the seed sem) and a sigma **about the rewiring rule** (the spread of the excess across
independent draws of the rule).  For the `swap2` rule both were measured -- the realization sd came
out at 0.00377 against a seed sem of 0.00025, so 98%+ of a single point's variance is the wiring draw.
For `swap0.5` there was **no realization sweep**, so the C1 contrast's rule-sigma could only be
reported as a *lower bound* (2.7 sigma, computed with `swap0.5`'s realization sd set to zero), where
substituting a `swap2`-sized sd would give 1.9 sigma.  Those two differ by 40%, which is the whole
question.

`e65` is that sweep: `swap0.5` at cs = 800 and six independent rewire seeds, the same shape `e32`
already provided for `swap2`.  This script does the decomposition for every rule that has a sweep and
reports the C1 contrast under both sigmas.

    python -m experiments.e65_realization_sd_by_rule
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

#: rule -> (path template, rewire seeds, source artifact for the seed sem)
RULES = {
    "swap0.5": ("runs/e65_swap05_rewire{}.json", range(6)),
    "swap2": ("runs/e32_rewire{}.json", range(6)),
    "erdos_renyi": ("runs/e33_er_rewire{}.json", range(6)),
}

#: The rule whose missing sweep made the bound: the C1 contrast is `swap2` minus `swap0.5`.
CONTRAST = ("swap0.5", "swap2")

#: What `e59` reported, for the comparison the whole run exists to make.
E59 = {"pair_sigma": 28.8, "rule_sigma_lower_bound": 2.7, "rule_sigma_if_same_sd": 1.9,
       "swap2_realization_sd": 0.00377, "swap2_seed_sem": 0.00025}


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def excess_at(artifact: dict, rule: str, arm: str = "diagonal(EWC)") -> tuple[float, float, list]:
    a = artifact["topologies"][rule][arm]["analytic"]
    return float(a["excess_mean"]), float(a["excess_sem"]), list(a.get("excess_per_seed") or [])


def sweep(rule: str) -> dict | None:
    tmpl, seeds = RULES[rule]
    means, sems, per_seed = [], [], []
    for s in seeds:
        d = load(tmpl.format(s))
        if d is None:
            continue
        m, sem, ps = excess_at(d, rule)
        means.append(m)
        sems.append(sem)
        per_seed.append(ps)
    if not means:
        return None
    k = len(means)
    arr = np.asarray(means, dtype=float)
    #: spread of the rule's own draws -- the realization sd `e59` needed for `swap0.5`
    sd_real = float(arr.std(ddof=1)) if k > 1 else float("nan")
    #: sem over the realizations, i.e. how well the rule's mean is pinned
    sem_real = sd_real / np.sqrt(k) if k > 1 else float("nan")
    #: the within-draw seed sem, averaged -- the OTHER sigma
    seed_sem = float(np.mean(sems))
    return dict(rule=rule, k=k, realizations=means, mean=float(arr.mean()),
                sd_realization=sd_real, sem_over_realizations=sem_real,
                seed_sem=seed_sem, n_task_seeds=len(per_seed[0]) if per_seed and per_seed[0] else 0,
                ratio_realization_to_seed=sd_real / seed_sem if seed_sem else float("nan"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e65_realization_sd_by_rule.json")
    args = ap.parse_args()

    out: dict = {"e59_reported": E59, "rules": {}}

    print("=" * 104)
    print("1. THE REALIZATION SPREAD OF EACH RULE THAT HAS A SWEEP")
    print("=" * 104)
    print(f"   {'rule':<14}{'draws':>6}{'excess mean':>14}{'sd across draws':>18}"
          f"{'seed sem':>12}{'ratio':>9}")
    sweeps = {}
    for rule in RULES:
        s = sweep(rule)
        if s is None:
            print(f"   {rule:<14}{'absent':>6}   -- {RULES[rule][0].format(0)} not on disk")
            continue
        sweeps[rule] = s
        out["rules"][rule] = s
        print(f"   {rule:<14}{s['k']:>6}{s['mean']:>14.6f}{s['sd_realization']:>18.6f}"
              f"{s['seed_sem']:>12.6f}{s['ratio_realization_to_seed']:>9.1f}")
    print("\n   the ratio is how many times the wiring draw outweighs the task draw at that rule.")
    for rule, s in sweeps.items():
        print(f"   {rule:<14} draws: " + " ".join(f"{v:.6f}" for v in s["realizations"]))

    print()
    print("=" * 104)
    print("2. THE C1 CONTRAST UNDER BOTH SIGMAS")
    print("=" * 104)
    a, b = CONTRAST
    pub = load("runs/e48_cs800_perseed.json")
    if a not in sweeps or b not in sweeps or pub is None:
        missing = [r for r in CONTRAST if r not in sweeps] + ([] if pub else ["published column"])
        print(f"   cannot compute -- no sweep for {missing}")
    else:
        sa, sb = sweeps[a], sweeps[b]
        #: The published contrast is taken at ONE draw of each rule -- the draw `e48` used -- so the
        #: graph-level and one-redraw sigmas are built on that difference, not on the rule means.
        ma, sema, psa = excess_at(pub, a)
        mb, semb, psb = excess_at(pub, b)
        delta = mb - ma
        #: The two arms see the SAME task seeds in the same order, so the graph-level sigma is the
        #: paired one -- this is the figure `e48`/`e59` report and the unpaired `hypot` is the
        #: conservative substitute, not the same number (24.4 vs 28.8 here).
        pair_sem = float(np.hypot(sema, semb))
        if psa and psb and len(psa) == len(psb):
            dp = np.asarray(psb, float) - np.asarray(psa, float)
            pair_sem = float(dp.std(ddof=1) / np.sqrt(dp.size))
            delta = float(dp.mean())
        sigma_pair = abs(delta) / pair_sem
        rule_sem = float(np.hypot(sa["sd_realization"], sb["sd_realization"]))
        sigma_rule = abs(delta) / rule_sem
        sigma_rule_lb = abs(delta) / sb["sd_realization"]
        sigma_rule_same = abs(delta) / float(np.hypot(sb["sd_realization"], sb["sd_realization"]))

        #: And the different question: do the two RULES have different mean excess?  Averaging over
        #: draws shrinks the wiring noise by sqrt(k) instead of merely accounting for it, so this
        #: number is larger -- and it is the one more draws buy power for.  It is also the most
        #: outlier-sensitive figure here, so it is computed with and without each arm's worst draw.
        delta_means = sb["mean"] - sa["mean"]
        means_sem = float(np.hypot(sa["sem_over_realizations"], sb["sem_over_realizations"]))
        sigma_rule_means = abs(delta_means) / means_sem
        aa, bb = np.asarray(sa["realizations"], float), np.asarray(sb["realizations"], float)
        ja, jb = int(np.argmax(np.abs(aa - aa.mean()))), int(np.argmax(np.abs(bb - bb.mean())))
        a_wo, b_wo = np.delete(aa, ja), np.delete(bb, jb)
        sem_wo = float(np.hypot(a_wo.std(ddof=1) / np.sqrt(a_wo.size),
                                b_wo.std(ddof=1) / np.sqrt(b_wo.size)))
        delta_wo = float(b_wo.mean() - a_wo.mean())
        sigma_wo = abs(delta_wo) / sem_wo

        print(f"   at the PUBLISHED draw (both arms from `e48`): "
              f"excess({b}) - excess({a}) = {delta:+.6f}")
        print(f"   across all draws: mean({b}) - mean({a}) = {delta_means:+.6f}\n")
        print(f"   (i)  about THESE two graphs        sem {pair_sem:.6f}  ->  "
              f"{sigma_pair:.1f} sigma")
        print(f"   (ii) about the RULE, one redraw    sem {rule_sem:.6f}  ->  "
              f"{sigma_rule:.1f} sigma")
        print(f"          e59's lower bound ({a} sd := 0):     {sigma_rule_lb:.1f} sigma")
        print(f"          if {a} shared {b}'s sd:                {sigma_rule_same:.1f} sigma")
        print(f"   (iii) about the RULE, means of draws  sem {means_sem:.6f}  ->  "
              f"{sigma_rule_means:.1f} sigma")
        print(f"          ({sa['k']} draws of {a}, {sb['k']} of {b})")
        print(f"          dropping each arm's worst draw: mean {delta_wo:+.6f} sem {sem_wo:.6f}"
              f"  ->  {sigma_wo:.1f} sigma")
        print(f"\n   (i) and (ii) answer 'how solid is the published contrast'; (iii) answers 'do the two")
        print(f"   rules have different mean excess at all', which is the weaker question but the one")
        print(f"   that averaging over draws buys power for.")
        print(f"\n   e59 reported {E59['pair_sigma']} sigma about the graphs and "
              f"{E59['rule_sigma_lower_bound']} sigma about the rule,")
        print(f"   as the most favourable reading of it, with {E59['rule_sigma_if_same_sd']} sigma if the")
        print(f"   unswept arm had a {b}-sized realization sd.  Measured: {a}'s sd is")
        print(f"   {sa['sd_realization']:.6f} against {b}'s {sb['sd_realization']:.6f} -- a factor of only")
        print(f"   {sb['sd_realization']/sa['sd_realization']:.1f}, so the bound was "
              f"{'TIGHT (within 5%)' if abs(sigma_rule - sigma_rule_lb) < 0.05 * sigma_rule_lb else 'NOT tight'}")
        print(f"   and the 'same sd' branch was the close one "
              f"({sigma_rule_same:.1f} against the measured {sigma_rule:.1f}).")
        print(f"\n   Outlier diagnostic, because (iii) moves more than (ii) does: the worst draw of {a} is")
        print(f"   {aa[ja]:.6f} against a mean of {aa.mean():.6f} ({abs(aa[ja]-aa.mean())/aa.std(ddof=1):.1f} sd out),")
        print(f"   and the worst of {b} is {bb[jb]:.6f} against {bb.mean():.6f} "
              f"({abs(bb[jb]-bb.mean())/bb.std(ddof=1):.1f} sd out).")

        out["contrast"] = dict(
            rule_a=a, rule_b=b,
            published_delta=delta, pair_sem=pair_sem, sigma_pair=sigma_pair,
            rule_sem=rule_sem, sigma_rule_one_redraw=sigma_rule,
            sigma_rule_lower_bound=sigma_rule_lb, sigma_rule_if_same_sd=sigma_rule_same,
            delta_of_means=delta_means, means_sem=means_sem, sigma_rule_means=sigma_rule_means,
            delta_of_means_drop_worst=delta_wo, means_sem_drop_worst=sem_wo,
            sigma_rule_means_drop_worst=sigma_wo)

        print(f"\n   LIMITS, stated where the numbers are: the realization sd rests on {sa['k']} draws of")
        print(f"   {a} and {sb['k']} of {b}.  Plan rule 15 is that a variance cannot be decomposed at")
        print(f"   n = 3; at n = 6 an sd is still only pinned to about +/-30%, so (ii) is good to about")
        print(f"   a factor of 1.3.  (iii) is far more sensitive, and the sensitivity is measurable here")
        print(f"   rather than hypothetical: it moves from {sigma_rule_means:.1f} to {sigma_wo:.1f} sigma when each")
        print(f"   arm's worst draw is dropped, so it should be quoted as that range and not as a point.")
        print(f"   How much a single draw can move the sd is the other lesson: {a}'s first four draws gave")
        print(f"   an sd of 0.000535, and the fifth alone multiplied it by five.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
