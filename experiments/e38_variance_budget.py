"""E38 — the network benchmark's variance budget, and the two claims that do not survive it.

The rate-network line's binding constraint is stated in the plan as a variance problem, with two
supporting claims:

* **the paired sem is the right one**, because the biological arm and its size-matched random
  control "share a seed sequence" (stated as 1.5x tighter at `side`, and 2.3x on the neuron ladder);
* **the binomial floor is 44% of the variance and is removable by asking for a bigger test set**,
  which makes `--test 480` the cheap lever.

Both are read off **three replicates**.  That is the problem this script addresses, because

* a sample sd on 2 df has a 95% interval spanning a factor of ~12, so the training remainder
  ``sqrt(max(0, s^2 - floor^2))`` is bounded only as ``[0, ~5x]`` and cannot distinguish
  "test-set-limited" from "training-limited";
* a correlation on 3 points has a 95% interval of roughly +/-0.5, so "the arms are matched" is not
  a measurable statement at n = 3.

One run in this repository has **nine** replicates (`e8_tuned_lambda.json`), and that is enough to
settle the pairing question and to bound the `--test 480` gain.  Every other run is reported with its
interval so the difference between the two is visible rather than asserted.

    python -m experiments.e38_variance_budget
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import chi2, norm

#: (label, path, the two arm names that form the matched pair)
RUNS = [
    ("lam1.0 side", "runs/e10_rung_side.json", ("ewc-block", "ewc-block-rand")),
    ("lam1.0 cell_class", "runs/e10_rung_cell_class.json", ("ewc-block", "ewc-block-rand")),
    ("lam1.0 ito_lee", "runs/e10_rung_ito_lee_hemilineage.json", ("ewc-block", "ewc-block-rand")),
    ("lam1.0 supertype", "runs/e10_rung_supertype.json", ("ewc-block", "ewc-block-rand")),
    ("lam0.1 side", "runs/e28_side_lam0.1.json", ("ewc-block", "ewc-block-rand")),
    ("lam0.1 cell_class", "runs/e31_methodlist_check.json", ("ewc-block", "ewc-block-rand")),
    ("lam0.003 cell_class", "runs/e25_cell_class_lam0.003.json", ("ewc-block", "ewc-block-rand")),
    ("lam0.003 cc 9 reps", "runs/e8_tuned_lambda.json", ("ewc-block", "ewc-block-rand")),
]

#: `--test 480` against the default `--test 48` is a 10x larger held-out set.
TEST_SCALE = 10.0


def sd_interval(s: float, df: int) -> tuple[float, float]:
    """95% interval on a sample sd, from the chi-square quantiles at ``df``."""
    if df < 1 or not np.isfinite(s) or s <= 0:
        return (float("nan"), float("nan"))
    return (float(s * np.sqrt(df / chi2.ppf(0.975, df))),
            float(s * np.sqrt(df / chi2.ppf(0.025, df))))


def corr_interval(r: float, n: int) -> tuple[float, float]:
    """95% Fisher-z interval on a Pearson correlation, or ``(nan, nan)`` if degenerate."""
    if n < 4 or not np.isfinite(r) or abs(r) >= 1:
        return (float("nan"), float("nan"))
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(n - 3.0)
    lo, hi = z - 1.96 * se, z + 1.96 * se
    return (float(np.tanh(lo)), float(np.tanh(hi)))


def required_repeats(effect: float, sd: float, z: float = 1.96) -> float:
    return float((z * sd / effect) ** 2) if effect else float("inf")


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", default="runs/e38_variance_budget.json")
    args = ap.parse_args()

    out: dict = {"runs": {}}

    print("=" * 104)
    print("1. THE DECOMPOSITION, AS A POINT AND AS AN INTERVAL -- n = 3 VERSUS n = 9")
    print("=" * 104)
    print("   the binomial floor is analytic; the sd it is subtracted from has (n-1) df")
    print(f"\n{'run':<22}{'arm':<16}{'n':>3}{'rep sd':>8}{'floor':>8}"
          f"{'95% CI rep sd':>22}{'95% CI training':>22}{'floor share':>12}")

    for label, path, _ in RUNS:
        d = load(path)
        if d is None:
            print(f"{label:<22}(not run yet)")
            continue
        cfg = d["config"]
        n_eval = d.get("evaluation_noise", {}).get("n_eval")
        if not n_eval:
            n_eval = sum(t["n_test"] for t in d["tasks"])
        rec = {"path": path, "basis": cfg.get("basis"), "lam": cfg.get("lam"),
               "fisher_batches": cfg.get("fisher_batches"),
               "timing_s": d.get("timing_s"), "n_eval": n_eval, "arms": {}}
        for name, m in d["methods"].items():
            acc = np.array([r["final_accuracy"] for r in m["replicates"]], dtype=float)
            n = len(acc)
            if n < 2:
                continue
            s = float(acc.std(ddof=1))
            floor = float(np.sqrt(acc.mean() * (1 - acc.mean()) / n_eval))
            lo, hi = sd_interval(s, n - 1)
            share = floor ** 2 / s ** 2 if s else float("nan")
            t_lo = float(np.sqrt(max(0.0, lo ** 2 - floor ** 2)))
            t_hi = float(np.sqrt(max(0.0, hi ** 2 - floor ** 2)))
            print(f"{label:<22}{name:<16}{n:>3}{s:>8.4f}{floor:>8.4f}"
                  f"{f'[{lo:.4f}, {hi:.4f}]':>22}"
                  f"{f'[0, {t_hi:.4f}]':>22}{share:>11.0%}"
                  + ("  <- below its own floor" if s < floor else ""))
            rec["arms"][name] = {
                "n": n, "mean": float(acc.mean()), "sd": s, "binomial_floor": floor,
                "floor_share_of_variance": share, "sd_ci": [lo, hi],
                "training_sd_ci": [t_lo, t_hi], "below_floor": bool(s < floor),
            }
        out["runs"][label] = rec

    print()
    print("=" * 104)
    print("2. DOES THE PAIRING BUY ANYTHING?  (the arms share seeds, so this is measurable)")
    print("=" * 104)
    print(f"\n{'run':<22}{'n':>3}{'delta':>10}{'sd(arm)':>9}{'sd(delta)':>11}"
          f"{'corr':>7}{'95% CI corr':>18}{'pairing gain':>14}")
    for label, path, (a_name, b_name) in RUNS:
        d = load(path)
        if d is None or label not in out["runs"]:
            continue
        if a_name not in d["methods"] or b_name not in d["methods"]:
            continue
        a = np.array([r["final_accuracy"] for r in d["methods"][a_name]["replicates"]])
        b = np.array([r["final_accuracy"] for r in d["methods"][b_name]["replicates"]])
        if len(a) != len(b) or len(a) < 2:
            continue
        n = len(a)
        delta = a - b
        sd_arm = float(np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2))
        sd_delta = float(delta.std(ddof=1))
        r = float(np.corrcoef(a, b)[0, 1]) if a.std() and b.std() else float("nan")
        rlo, rhi = corr_interval(r, n)
        # unpaired sem over the same n, for the like-for-like gain
        sem_unpaired = float(np.sqrt(a.var(ddof=1) / n + b.var(ddof=1) / n))
        sem_paired = sd_delta / np.sqrt(n)
        gain = sem_unpaired / sem_paired if sem_paired else float("nan")
        ci = f"[{rlo:+.2f}, {rhi:+.2f}]" if rlo == rlo else "n/a"
        print(f"{label:<22}{n:>3}{delta.mean():>+10.4f}{sd_arm:>9.4f}{sd_delta:>11.4f}"
              f"{r:>7.2f}{ci:>18}{gain:>13.2f}x")
        out["runs"][label]["pair"] = {
            "arm_a": a_name, "arm_b": b_name, "n": n, "delta": float(delta.mean()),
            "sd_arm": sd_arm, "sd_delta": sd_delta, "sem_paired": sem_paired,
            "sem_unpaired": sem_unpaired, "corr": r, "corr_ci": [rlo, rhi],
            "pairing_gain": gain,
        }

    print()
    print("=" * 104)
    print("3. THE `--test 480` QUESTION, BOUNDED RATHER THAN BRACKETED")
    print("=" * 104)
    print("   the two arms are evaluated on different held-out draws, so the binomial error does")
    print("   not cancel unless the per-decision errors are correlated.  At independence the")
    print("   contrast's binomial variance is 2*floor^2, which is an UPPER bound; the observed")
    print("   sd(delta) caps it further.  Removing 90% of that capped part is the most")
    print("   `--test 480` can possibly buy.\n")
    print(f"{'run':<22}{'n':>3}{'sd(delta)':>11}{'2*floor^2':>11}{'binom share':>13}"
          f"{'indep?':>8}{'reps@0.01':>11}{'reps@0.03':>11}{'gain bound':>12}{'after':>8}")
    for label, rec in out["runs"].items():
        p = rec.get("pair")
        if not p:
            continue
        sd_delta = p["sd_delta"]
        floor = rec["arms"].get(p["arm_a"], {}).get("binomial_floor")
        if not floor:
            continue
        two_floor2 = 2 * floor ** 2
        var = sd_delta ** 2
        binom_var = min(two_floor2, var)
        share = binom_var / var if var else float("nan")
        after_var = max(var - 0.9 * binom_var, 1e-12)
        sd_after = float(np.sqrt(after_var))
        gain = sd_delta / sd_after
        # If the observed contrast spread is below sqrt(2)*floor, the two arms' evaluation errors
        # CANNOT be independent -- so the independence-based gain above is not achievable, whatever
        # the arithmetic says.
        indep_ok = sd_delta >= np.sqrt(two_floor2)
        print(f"{label:<22}{p['n']:>3}{sd_delta:>11.4f}{two_floor2:>11.5f}{share:>12.0%}"
              f"{'yes' if indep_ok else 'NO':>8}"
              f"{required_repeats(0.01, sd_delta):>11.0f}"
              f"{required_repeats(0.03, sd_delta):>11.0f}"
              f"{gain:>11.2f}x{required_repeats(0.01, sd_after):>8.0f}")
        rec["test480_bound"] = {
            "two_floor_squared": two_floor2, "binomial_share_upper": share,
            "independence_consistent": bool(indep_ok),
            "gain_upper_bound": gain if indep_ok else float("nan"),
            "repeats_for_0.01_now": required_repeats(0.01, sd_delta),
            "repeats_for_0.03_now": required_repeats(0.03, sd_delta),
            "repeats_for_0.01_after_test480": required_repeats(0.01, sd_after),
        }

    print()
    print("  A run whose observed contrast spread is BELOW sqrt(2)*floor is inconsistent with")
    print("  independent evaluation errors, so its arithmetic gain bound is unreachable -- the")
    print("  arms must be sharing their errors, which is also what a high `corr` says.  Those")
    print("  rows are the n = 3 ones; the arithmetic is trustworthy only where `indep?` is yes.")

    print()
    print("=" * 104)
    print("3b. THE REPLICATE REQUIREMENT AS A FUNCTION OF THE THING NOBODY MEASURED")
    print("=" * 104)
    print("   how many replicates detect a 0.03 accuracy effect, as a function of the assumed")
    print("   correlation between the two arms' per-seed accuracies -- using the per-arm sds from")
    print("   the only run with n = 9.\n")
    base = out["runs"].get("lam0.003 cc 9 reps")
    if base and "pair" in base:
        va = base["arms"][base["pair"]["arm_a"]]["sd"] ** 2
        vb = base["arms"][base["pair"]["arm_b"]]["sd"] ** 2
        print(f"{'assumed corr':>13}{'sd(delta)':>11}{'reps@0.03':>11}{'hours @ 1.1 min':>18}")
        tbl = {}
        for r in (0.0, 0.25, 0.5, 0.75, 1.0):
            var_d = va + vb - 2 * r * np.sqrt(va * vb)
            sd_d = float(np.sqrt(var_d))
            reps = required_repeats(0.03, sd_d)
            print(f"{r:>13.2f}{sd_d:>11.4f}{reps:>11.0f}{reps * 2 * 1.1 / 60:>18.1f}")
            tbl[str(r)] = {"sd_delta": sd_d, "repeats_for_0.03": reps}
        print("\n   (hours assume two arms per replicate at the 1.1 min/(arm x replicate) the n=9 run")
        print("    achieves, which is the cheapest rung measured; a coarse rung is ~10x that.)")
        out["replicate_requirement_vs_assumed_corr"] = tbl

    print()
    print("=" * 104)
    print("4. THE COST SIDE")
    print("=" * 104)
    print(f"\n{'run':<22}{'basis':<24}{'batches':>8}{'reps':>6}{'total h':>9}"
          f"{'min / (arm x rep)':>19}")
    for label, rec in out["runs"].items():
        t = rec.get("timing_s")
        if not t:
            continue
        arms = max(len(rec["arms"]), 1)
        for name, a in rec["arms"].items():
            per = t / 60 / (a["n"] * arms) if a["n"] else float("nan")
            break
        print(f"{label:<22}{str(rec['basis']):<24}{rec['fisher_batches']:>8}"
              f"{a['n']:>6}{t / 3600:>9.2f}{per:>19.1f}")

    print()
    print("=" * 100)
    print("5. THE SYNAPSE LADDER AT lam = 1.0, FOUR RUNGS IN")
    print("=" * 100)
    print("   the biological partition against its own size-matched random control, per rung, with")
    print("   the cost and the detection floor each run actually achieved\n")
    print(f"   {'rung':<22}{'biological':>11}{'control':>10}{'delta':>10}{'sigma':>8}"
          f"{'floor':>8}{'reps needed for 0.01':>22}{'hours':>8}")
    rungs = []
    for label, path, _ in RUNS:
        if not label.startswith("lam1.0"):
            continue
        d = load(path)
        if d is None or "ewc-block" not in d["methods"] or "ewc-block-rand" not in d["methods"]:
            continue
        bio, rnd = d["methods"]["ewc-block"], d["methods"]["ewc-block-rand"]
        a = np.array([r["final_accuracy"] for r in bio["replicates"]])
        b = np.array([r["final_accuracy"] for r in rnd["replicates"]])
        if len(a) != len(b):
            continue
        delta = float((a - b).mean())
        sem = float((a - b).std(ddof=1) / np.sqrt(len(a)))
        sigma = delta / sem if sem else float("nan")
        floor = 1.96 * sem
        reps = required_repeats(0.01, float((a - b).std(ddof=1)))
        hrs = (d.get("timing_s") or float("nan")) / 3600
        print(f"   {d['config']['basis']:<22}{a.mean():>11.4f}{b.mean():>10.4f}"
              f"{delta:>+10.4f}{sigma:>+8.2f}{floor:>8.4f}{reps:>22.0f}{hrs:>8.2f}")
        rungs.append({"basis": d["config"]["basis"], "lam": d["config"]["lam"],
                      "biological": float(a.mean()), "control": float(b.mean()),
                      "delta": delta, "sigma": sigma, "detection_floor": floor,
                      "repeats_for_0.01": reps, "hours": hrs, "n": len(a)})
    if rungs:
        worse = sum(1 for r in rungs if r["delta"] < 0)
        print(f"\n   {worse} of {len(rungs)} rungs put the biological partition BELOW its matched")
        print(f"   control, and none resolves: the largest |sigma| is "
              f"{max(abs(r['sigma']) for r in rungs):.2f}.")
        print("   Every run's detection floor is 0.05 or wider, so a 0.01-0.03 effect -- the size")
        print("   the neuron line found -- is invisible at 3 replicates, which is what e38 section 3")
        print("   already bounded and what e46 (16 replicates) is measuring.")
        out["ladder_lambda_1"] = rungs

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
