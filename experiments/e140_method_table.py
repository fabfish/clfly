"""E140 -- the five-method table at forty replicates, in both arms, with the confound removed from every one.

`e135` ran the five-method table at **five** replicates and found exactly one contrast that moved when the
unpenalised channel was removed from every arm: **replay's advantage over `naive` is cut by 66%**, a move of
2.23 sigma — and under that arm the ranking becomes `ewc < replay < block-rand < block < naive`, i.e. **diagonal
EWC becomes the best method**. Five replicates is what the project keeps finding is not enough (`e133`), so
`e140` re-runs both arms at **forty**.

    python -m experiments.e140_method_table

**The registration's fire is resolvability arithmetic rather than hope.** At forty paired seeds the paired sem of
a contrast against `naive` on this configuration is about **0.008** (`e133`: ewc - naive is -0.0096 +/- 0.0080),
so the frozen arm's `ewc - naive` that `e135` saw at five replicates (**-0.0354**) is **4.4x** that sem and can
be resolved, while the plastic arm's (**-0.0096**) is **1.2x** it and cannot.

**The controls are per-replicate identities**, not comparisons: an arm of these runs must reproduce its
comparator to the last digit or the two are not on one footing. **And a missing artifact is reported as missing
and no verdict is printed from it**, so an unfinished arm cannot masquerade as a zero.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

METHODS = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
PLASTIC = "runs/e140_r32_methods_plastic_40reps.json"
FROZEN = "runs/e140_r32_methods_frozenbias_40reps.json"
#: (label, path, method, replicates, our arm, why)
C0_CONTROLS = (
    ("e133", "runs/e133_r32_naive_ewc_40reps.json", "naive", 40, "plastic",
     "the plastic arm's `naive`, all forty replicates"),
    ("e133", "runs/e133_r32_naive_ewc_40reps.json", "ewc", 40, "plastic",
     "the plastic arm's `ewc`, all forty replicates"),
    ("e135", "runs/e135_r32_methods_frozenbias.json", "ewc", 5, "frozen",
     "the frozen arm's `ewc`, the first five replicates"),
    ("e125", "runs/e125_r32_frozenbias.json", "naive", 40, "frozen",
     "the frozen arm's `naive`, all forty -- the C0b probe, whose fisher_batches, lam and replay settings differ"),
)
SERIES = ("mean_forgetting", "final_accuracy")


def load_arm(path: Path, method: str) -> dict | None:
    """One method's forty replicates, or None when the artifact or the method is not there."""
    if not Path(path).is_file():
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))["methods"]
    if method not in payload:
        return None
    entry = payload[method]
    return {
        "forgetting": np.array([r["mean_forgetting"] for r in entry["replicates"]]),
        "accuracy": np.array([r["final_accuracy"] for r in entry["replicates"]]),
        "per_task": np.array([r["forgetting_per_task"][:-1] for r in entry["replicates"]]),
        "sem": float(entry.get("forgetting_sem", float("nan"))),
        "final_accuracy": float(entry.get("final_accuracy", float("nan"))),
        "n": len(entry["replicates"]),
    }


def load_series(path: Path, method: str) -> dict | None:
    """The per-replicate fields of a named comparator, **under the same keys `load_arm` uses**.

    The first version returned the *artifact's* field names (`mean_forgetting`, `final_accuracy`) while
    `identity` was called with the arm dictionary's keys (`forgetting`, `accuracy`) — a KeyError that the tests
    missed because they exercised `identity` on raw arrays and never through `control_check`. The names are the
    interface between the two halves, so they are mapped here once and asserted by a test.
    """
    if not Path(path).is_file():
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))["methods"]
    if method not in payload:
        return None
    reps = payload[method]["replicates"]
    return {"forgetting": np.array([r["mean_forgetting"] for r in reps]),
            "accuracy": np.array([r["final_accuracy"] for r in reps])}


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = a - b
    sem = float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan")
    sigma = (abs(float(d.mean())) / sem) if sem else (0.0 if float(d.mean()) == 0 else float("nan"))
    return {"change": float(d.mean()), "sem": sem, "sigma": sigma, "n": len(d),
            "negative": int((d < 0).sum())}


def identity(have: dict, want: dict, field: str, n: int) -> dict:
    """Are the first ``n`` per-replicate values equal to the last digit, and by how much do they differ?"""
    a, b = have[field][:n], want[field][:n]
    return {"identical": bool(np.array_equal(a, b)),
            "worst_abs_difference": float(np.max(np.abs(a - b))) if len(a) else float("nan"),
            "n": int(len(a))}


def control_check(arms: dict, path: Path, method: str, arm_key: str, field: str, n: int) -> dict | None:
    have = arms.get(arm_key, {}).get(method)
    want = load_series(Path(path), method)
    if have is None or want is None:
        return None
    return identity(have, want, field, n)


def verdicts(arms: dict[str, dict | None]) -> dict:
    """The registered checks, on whichever arms are present. Pure, so that a test can drive it."""
    present = {k: v for k, v in arms.items() if v is not None}
    out: dict = {"arms_present": sorted(present)}
    if "plastic" not in present or "frozen" not in present:
        out["verdict"] = ("neither arm is on disk yet" if not present else
                          "both arms are needed and only " + ", ".join(sorted(present)) + " is present")
        return out
    if "naive" not in present["plastic"] or "naive" not in present["frozen"]:
        out["verdict"] = "both arms need a `naive` row: every contrast here is against it"
        return out

    out["table"] = {k: {m: {"forgetting": float(a[m]["forgetting"].mean()),
                            "sem": float(a[m]["sem"]),
                            "accuracy": float(a[m]["final_accuracy"])}
                        for m in METHODS if m in a}
                    for k, a in present.items()}
    out["contrasts_vs_naive"] = {k: {m: paired(a[m]["forgetting"], a["naive"]["forgetting"])
                                     for m in METHODS if m in a and m != "naive"}
                                 for k, a in present.items()}

    if "ewc" in out["contrasts_vs_naive"]["frozen"]:
        ewc_frozen = out["contrasts_vs_naive"]["frozen"]["ewc"]
        out["P1_ewc_frozen"] = ewc_frozen
        out["P1_holds"] = bool(ewc_frozen["sigma"] >= 3.0 and ewc_frozen["change"] < 0)
    else:
        out["P1_holds"] = None            # the frozen arm has no `ewc` row, so P1 is not decidable

    # P2, the difference of differences: replay's margin over naive in the frozen arm against its margin in the
    # plastic arm, which is a paired comparison inside one seed set.
    if "replay" in present["plastic"] and "replay" in present["frozen"]:
        d_plastic = present["plastic"]["replay"]["forgetting"] - present["plastic"]["naive"]["forgetting"]
        d_frozen = present["frozen"]["replay"]["forgetting"] - present["frozen"]["naive"]["forgetting"]
        out["P2_replay_margin"] = {
            "plastic": float(d_plastic.mean()), "frozen": float(d_frozen.mean()),
            "difference_of_differences": paired(d_frozen, d_plastic),
            "cut": float(1 - d_frozen.mean() / d_plastic.mean()) if d_plastic.mean() else float("nan")}
        out["P2_holds"] = bool(out["P2_replay_margin"]["difference_of_differences"]["sigma"] >= 2.0
                               and out["P2_replay_margin"]["cut"] > 0)

    # P3, the penalties' mutual ordering -- the paper's central network result, confound-robust at five
    # replicates. Read as an ordering rather than as a contrast.
    ordering = {k: [m for m in sorted((m for m in METHODS if m in a),
                                      key=lambda m: float(a[m]["forgetting"].mean()))]
                for k, a in present.items()}
    out["P3_ordering"] = ordering
    out["P3_holds"] = bool(ordering["plastic"] == ordering["frozen"])
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--plastic", type=Path, default=Path(PLASTIC))
    p.add_argument("--frozen", type=Path, default=Path(FROZEN))
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    arms = {"plastic": {m: load_arm(args.plastic, m) for m in METHODS},
            "frozen": {m: load_arm(args.frozen, m) for m in METHODS}}
    out: dict = {}

    print("== the arms, as they land ==")
    for k in ("plastic", "frozen"):
        have = [m for m in METHODS if arms[k][m]]
        print(f"   {k:8} {len(have)}/5 methods: {', '.join(have) if have else 'not on disk'}")

    print("\n== C0: per-replicate identities, which are controls rather than comparisons ==")
    c0: dict = {}
    for label, path, method, n, arm_key, why in C0_CONTROLS:
        got = {f: control_check(arms, Path(path), method, arm_key, f, n) for f in ("forgetting", "accuracy")}
        if any(v is None for v in got.values()):
            print(f"   {label}/{method}: not checkable yet -- {why}")
            continue
        same = all(v["identical"] for v in got.values())
        worst = max(v["worst_abs_difference"] for v in got.values())
        c0[f"{label}/{method}"] = {"identical": same, "worst_abs_difference": worst, "n": n}
        print(f"   {label}/{method}: {why}\n      identical on {n} replicates: {same}   worst |difference| "
              f"{worst:.3g}")
    out["C0"] = c0

    complete = {k: (arms[k] if all(arms[k][m] for m in METHODS) else None) for k in ("plastic", "frozen")}
    out.update(verdicts(complete))
    if out.get("P1_holds") is None:
        print(f"\n{out.get('verdict', 'P1 is not decidable from these arms')} -- no registered verdict is "
              f"printed from an incomplete set of arms.")
        if args.json_out:
            write_json(args.json_out, out)
        return 0

    print("\n== the table, per arm ==")
    for k in ("plastic", "frozen"):
        print(f"   {k}")
        for m in out["P3_ordering"][k]:
            cell = out["table"][k][m]
            print(f"     {m:15} forgetting {cell['forgetting']:+.4f} (sem {cell['sem']:.4f})   "
                  f"accuracy {cell['accuracy']:.4f}")

    print("\n== the contrasts against `naive`, paired over the forty shared seeds ==")
    for k in ("plastic", "frozen"):
        for m, c in out["contrasts_vs_naive"][k].items():
            print(f"   {k:8} {m:15} {c['change']:+.4f} +/- {c['sem']:.4f} = {c['sigma']:5.2f} sigma   "
                  f"({c['negative']}/40 negative)")

    print("\n== P1: the frozen arm's `ewc` must beat `naive` at >= 3 sigma ==")
    c = out["P1_ewc_frozen"]
    print(f"   {c['change']:+.4f} +/- {c['sem']:.4f} = {c['sigma']:.2f} sigma  ->  "
          f"P1 {'HOLDS' if out['P1_holds'] else 'FAILS'}")
    print("   (the plastic arm's same contrast is the comparator: `e133` gives -0.0096 +/- 0.0080 = 1.21 sigma)")

    if "P2_replay_margin" in out:
        m = out["P2_replay_margin"]
        print("\n== P2: replay's margin over `naive` shrinks when the channel is removed ==")
        print(f"   plastic {m['plastic']:+.4f}   frozen {m['frozen']:+.4f}   cut {m['cut']:.0%} at "
              f"{m['difference_of_differences']['sigma']:.2f} sigma  ->  "
              f"P2 {'HOLDS' if out['P2_holds'] else 'FAILS'}")
        print("   (`e135`'s five-replicate version of this is +0.0563 +/- 0.0252 = 2.23 sigma, a 66% cut)")

    print("\n== P3: the penalties' mutual ordering, which is the paper's central network result ==")
    for k in ("plastic", "frozen"):
        print(f"   {k:8} {' < '.join(out['P3_ordering'][k])}")
    print(f"   ->  P3 {'HOLDS' if out['P3_holds'] else 'DIFFERS BETWEEN ARMS'}")

    print("\nNOTE: one read-out (32), one lambda, three tasks, one circuit. The thresholds are compared against")
    print("      a sem estimated from forty pairs, which itself carries about 11% relative uncertainty (rule")
    print("      37), so a value within a few percent of a bar is at the bar rather than past it.")
    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
