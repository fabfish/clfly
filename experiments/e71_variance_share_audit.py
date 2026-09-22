"""E71 -- the "62% of the variance is the learner" figure is the *evaluation floor's* share, and three documents state it backwards.

The project's summary of the network line's binding axis is stated in three places -- the paper's
retraction section, the plan's binding-axes paragraph, and `e57`'s finding -- as

    the learner's seeds: 62% of the per-replicate variance is the learner, not the test set

and in a fourth ("the floor is 62% learner").  Both readings cannot be right, and neither is what the
artifact says.

`runs/e38_variance_budget.json` records, per arm, a field named `floor_share_of_variance`: the share of
an arm's per-replicate variance that the **test set's binomial sampling floor** accounts for.  For the
`naive` arm of the nine-replicate run it is **0.619**.  So 62% is the *test set's* share and the
learner's share is the other 38% -- and the same document then reports, for the well-measured contrast
(it is the contrast the claims are about), a binomial share of at most **43%**.

This script recomputes both quantities from the artifacts rather than re-quoting them, at n = 9 and at
the n = 16 pool `e54` assembled, and prints which sentence each number supports.

    python -m experiments.e71_variance_share_audit
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

E54 = "runs/e54_naive_seed_pool.json"
E38 = "runs/e38_variance_budget.json"

#: The well-measured contrast: `lambda` 0.003, `cell_class`, nine replicates.  It is the one the
#: `--test 480` bound was computed on.
CONTRAST_RUN = "lam0.003 cc 9 reps"

#: What three documents say, and what the artifact field they come from is called.
STATED = "62% of the per-replicate variance is the learner, not the test set"
SOURCE_FIELD = "floor_share_of_variance"


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def decompose(sd: float, n_eval: int, mean: float) -> dict:
    """Split a per-replicate sd into the test-set floor and the remainder.

    The floor is the sd of a binomial accuracy estimate on ``n_eval`` test items at ``mean``.  It is
    what a bigger test set shrinks, and it is *measurement*: the remainder is everything else, of which
    the learner's seed-to-seed variability is the part more seeds average over.
    """
    floor = float(np.sqrt(mean * (1.0 - mean) / n_eval))
    var = sd * sd
    fvar = floor * floor
    rest_var = var - fvar
    return dict(sd=sd, n_eval=n_eval, mean=mean, floor=floor,
                floor_share=fvar / var, rest_share=rest_var / var,
                rest_sd=float(np.sqrt(rest_var)) if rest_var > 0 else 0.0,
                floor_below_sd=bool(floor < sd))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e71_variance_share_audit.json")
    args = ap.parse_args()

    e54, e38 = load(E54), load(E38)
    if e54 is None or e38 is None:
        raise SystemExit("need both artifacts")

    pooled = e54["pooled"]
    n_eval = e38["runs"][CONTRAST_RUN]["n_eval"]
    nine = e38["runs"][CONTRAST_RUN]["arms"]["naive"]

    out: dict = {"stated": STATED, "artifact_field": SOURCE_FIELD}

    print("=" * 104)
    print("1. THE SENTENCE, THE FIELD, AND WHAT THE FIELD MEASURES")
    print("=" * 104)
    print(f"   stated in the paper, the plan and e57:  \"{STATED}\"")
    print(f"   the field the number comes from:        `{SOURCE_FIELD}`")
    print(f"   `e38`'s value of that field, naive arm, nine replicates: "
          f"{nine['floor_share_of_variance']:.3f}")
    print("\n   the field is the share of the variance the TEST SET's binomial sampling floor accounts")
    print("   for.  So the sentence is inverted: 62% is the measurement, and the learner is what is")
    print("   left over.")

    print()
    print("=" * 104)
    print("2. THE `naive` ARM'S OWN SPREAD, DECOMPOSED AT BOTH SAMPLE SIZES")
    print("=" * 104)
    print(f"   {'pool':<22}{'n':>4}{'mean':>9}{'sd':>9}{'floor':>9}{'floor share':>13}"
          f"{'learner share':>15}{'learner sd':>12}")
    rows = {}
    for label, n, sd, mean in (
        ("e38 naive, nine reps", 9, nine["sd"], nine["mean"]),
        ("e54 pool, sixteen reps", 16, pooled["sd"], pooled["mean"]),
    ):
        d = decompose(sd, n_eval, mean)
        rows[label] = d
        print(f"   {label:<22}{n:>4}{mean:>9.4f}{sd:>9.5f}{d['floor']:>9.5f}"
              f"{d['floor_share']:>12.1%}{d['rest_share']:>15.1%}{d['rest_sd']:>12.5f}")
    out["naive_arm"] = rows

    #: The 95% interval on the learner's share, propagated from the pooled sd's own interval rather
    #: than assumed.  `e54` reports the sd CI; the floor is treated as known, which is what it is.
    lo, hi = pooled["sd_ci"]
    fvar = pooled["binomial_floor"] ** 2
    share_lo = max(0.0, (lo * lo - fvar) / (lo * lo))
    share_hi = (hi * hi - fvar) / (hi * hi)
    print(f"\n   at sixteen replicates the learner's share is "
          f"{rows['e54 pool, sixteen reps']['rest_share']:.1%} with a 95% interval of "
          f"[{share_lo:.0%}, {share_hi:.0%}]")
    print(f"   (propagated from the sd's own interval [{lo:.5f}, {hi:.5f}], floor treated as known)")
    out["learner_share_ci_n16"] = [share_lo, share_hi]

    print()
    print("=" * 104)
    print("3. AND THE CONTRAST, WHICH IS WHAT THE CLAIMS ARE ABOUT")
    print("=" * 104)
    blk = e38["runs"][CONTRAST_RUN]
    pair = blk["pair"]
    fl_a = blk["arms"][pair["arm_a"]]["binomial_floor"]
    fl_b = blk["arms"][pair["arm_b"]]["binomial_floor"]
    two_f2 = 2.0 * float(np.mean([fl_a, fl_b])) ** 2
    sd_delta = pair["sd_delta"]
    share = two_f2 / (sd_delta * sd_delta)
    gain_90 = sd_delta / float(np.sqrt(sd_delta ** 2 - 0.9 * two_f2))
    print(f"   run: {CONTRAST_RUN}, n = {pair['n']}, both arms' floors "
          f"{fl_a:.5f} / {fl_b:.5f}")
    print(f"   sd of the paired contrast        {sd_delta:.5f}")
    print(f"   its variance                     {sd_delta**2:.6f}")
    print(f"   the floor's contribution, 2*f^2  {two_f2:.6f}   ->  binomial share "
          f"{share:.1%}")
    print(f"   removing 90% of that             ->  {gain_90:.2f}x  (e38 reports 1.28x)")
    #: `e38`'s own figure is reproduced here only to a few percent, so the difference is named rather
    #: than hidden: their 2*f^2 of 0.00162 corresponds to using one arm's floor twice, and the two
    #: arms' floors differ (0.02848 / 0.03017).  Both are reported; neither moves the conclusion.
    alt = 2.0 * fl_a ** 2
    print(f"   e38's 2*f^2 was 0.00162 (using one arm's floor twice) against this "
          f"{two_f2:.5f} (both arms), so")
    print(f"   the binomial share is {alt/sd_delta**2:.1%}-{share:.1%} depending on which is used.")
    print(f"\n   So for the CONTRAST the measurement is a minority ({share:.0%}) and everything else --")
    print(f"   including the learner -- is {1-share:.0%}.  For the naive arm's OWN spread the")
    print(f"   measurement is the majority ({rows['e54 pool, sixteen reps']['floor_share']:.0%}).  Two different")
    print(f"   quantities, and the sentence above assigns the arm's number to the contrast's axis.")
    out["contrast"] = dict(run=CONTRAST_RUN, n=pair["n"], sd_delta=sd_delta,
                           two_floor_sq=two_f2, binomial_share=share,
                           gain_bound_90pct=gain_90,
                           naive_floor_shares=[fl_a, fl_b])

    print()
    print("=" * 104)
    print("4. THE CORRECTED STATEMENT, AND WHY THE CONCLUSION DOES NOT CHANGE")
    print("=" * 104)
    print("   The claim the number was doing work for is that the C2b line's binding constraint is")
    print("   SEEDS.  That survives, for a reason the documents state backwards:")
    d16 = rows["e54 pool, sixteen reps"]
    print(f"   - the test-set floor is {d16['floor_share']:.0%} of the naive arm's spread, but it is")
    print(f"     cheaply removable only to a point: ten times the test set divides it by sqrt(10),")
    k = 10.0
    new_sd = float(np.sqrt(d16["rest_sd"] ** 2 + d16["floor"] ** 2 / k))
    print(f"     taking {pooled['sd']:.5f} down to {new_sd:.5f} -- a {pooled['sd']/new_sd:.2f}x gain and no more;")
    print(f"   - the learner's share is {d16['rest_share']:.0%} of the arm and at least "
          f"{1-share:.0%} of the contrast, and more seeds remove it entirely,")
    print(f"     which is why 12-16 replicates is the answer and a bigger test set is not.")
    print(f"\n   The corrected sentence for all three documents:")
    print(f"   \"the evaluation floor is {d16['floor_share']:.0%} of the naive arm's per-replicate variance")
    print(f"    (and at most {share:.0%} of the contrast's), so the learner contributes "
          f"{d16['rest_share']:.0%} of the arm")
    print(f"    and at least {1-share:.0%} of the contrast -- which is why seeds, not test size, is the lever.\"")
    out["corrected"] = dict(naive_floor_share=float(d16["floor_share"]),
                            naive_learner_share=float(d16["rest_share"]),
                            contrast_binomial_share=float(share),
                            test480_gain_recomputed=float(pooled["sd"] / new_sd))

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, default=str)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
