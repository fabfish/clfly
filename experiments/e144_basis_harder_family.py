"""E144 -- the basis question on the family whose difficulty is in the wiring, with a *three-draw* control.

On the base family the biological block partition never beats its group-size-matched random control, and the
comparison was made on a benchmark where **70% of the forgetting is carried by 800 offsets that no partition can
act on**. `e143` measured that on the shared-input family (**overlap 1.0**, read-out 32, forty replicates) the
extra forgetting **survives freezing those offsets** — **5.04σ** — so it lives in the **26,568 connectome-masked
weights**, the channel a synapse partition acts on. This script reads that family's four-method table and
evaluates the registered prediction against a control that is a **population** rather than one sample of it.

    python -m experiments.e144_basis_harder_family

**The control needs the draw term, and rule 10 says so**: `SynapsePartition.random_matched` is one draw from the
population of size-matched random partitions, and until 2026-09-24 the runner could not vary it at all. The
registration is amended to a **three-draw** control, and this script combines the draws the way the amendment
says: the contrast is `ewc-block` minus the **mean of the K control draws**, and its variance is

    Var(d) = Var_between(d_k) / K  +  mean_k(se_k^2) / K

with the **two components reported separately** — the first is the draw term (K − 1 = 2 degrees of freedom at K =
3) and the second is the ordinary paired error. **A missing artifact is reported as missing and no verdict is
printed from it**, so an unfinished arm cannot masquerade as a zero.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

MAIN = "runs/e144_r32_overlap1_methods_40reps.json"
DRAWS = ("runs/e144_r32_overlap1_methods_40reps.json",          # draw 0 is the main artifact's own block-rand row
         "runs/e144_r32_overlap1_rand_draw1.json",
         "runs/e144_r32_overlap1_rand_draw2.json")
COMPARATOR = "runs/e142_r32_overlap1.json"                     # the same family without the block methods, for C0a
METHODS = ("naive", "ewc", "ewc-block", "ewc-block-rand")
P1_SIGMA = 3.0
FALSIFIER_SIGMA = 2.0


def load(path: Path, method: str) -> dict | None:
    if not Path(path).is_file():
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))["methods"]
    if method not in payload:
        return None
    entry = payload[method]
    reps = entry["replicates"]
    return {"forgetting": np.array([r["mean_forgetting"] for r in reps]),
            "accuracy": np.array([r["final_accuracy"] for r in reps]),
            "sem": float(entry.get("forgetting_sem", float("nan"))),
            "final_accuracy": float(entry.get("final_accuracy", float("nan"))),
            "n": len(reps)}


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = a - b
    sem = float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan")
    sigma = (abs(float(d.mean())) / sem) if sem else (0.0 if float(d.mean()) == 0 else float("nan"))
    return {"change": float(d.mean()), "sem": sem, "sigma": sigma, "n": len(d),
            "negative": int((d < 0).sum())}


def combine_draws(draws: list[dict]) -> dict:
    """The registered combination: the mean contrast over draws, with the draw term beside the paired one."""
    changes = [d["change"] for d in draws]
    ses = [d["sem"] for d in draws]
    K = len(draws)
    between = float(np.var(changes, ddof=1)) if K > 1 else 0.0
    within = float(np.mean([s ** 2 for s in ses]))
    var = between / K + within / K
    sem = math.sqrt(var) if var > 0 else float("nan")
    mean = float(np.mean(changes))
    return {"k_draws": K, "mean_change": mean,
            "draw_sd": math.sqrt(between) if between > 0 else 0.0,
            "sem_draw_component": math.sqrt(between / K) if between > 0 else 0.0,
            "sem_paired_component": math.sqrt(within / K),
            "sem_total": sem,
            "sigma": abs(mean) / sem if sem else float("nan"),
            "draw_df": max(K - 1, 0)}


def verdicts(arms: dict, draws: list[dict] | None) -> dict:
    out: dict = {"arms_present": sorted(k for k, v in arms.items() if v is not None)}
    if arms.get("ewc-block") is None or arms.get("naive") is None:
        out["verdict"] = "the block arm and `naive` are both needed"
        return out
    if not draws:
        out["verdict"] = "no control draw is on disk, so P1 is not decidable"
        return out
    out["P1"] = combine_draws(draws)
    out["P1_holds"] = bool(out["P1"]["mean_change"] < 0 and out["P1"]["sigma"] >= P1_SIGMA)
    out["falsifier_fires"] = bool(out["P1"]["sigma"] < FALSIFIER_SIGMA)
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--main", type=Path, default=Path(MAIN))
    p.add_argument("--draws", nargs="*", type=Path, default=[Path(d) for d in DRAWS])
    p.add_argument("--comparator", type=Path, default=Path(COMPARATOR))
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    arms = {m: load(args.main, m) for m in METHODS}
    print("== the table, as it lands ==")
    for m in METHODS:
        a = arms[m]
        print(f"   {m:15} " + (f"forgetting {a['forgetting'].mean():+.4f} (sem {a['sem']:.4f})  "
                               f"accuracy {a['final_accuracy']:.4f}" if a else "not on disk"))

    print("\n== C0a: the `naive` row must be per-replicate identical to the same family without the block methods ==")
    ref = load(args.comparator, "naive")
    out: dict = {}
    if arms["naive"] is None or ref is None:
        print("   not checkable yet")
    else:
        same = bool(np.array_equal(arms["naive"]["forgetting"], ref["forgetting"])) and \
               bool(np.array_equal(arms["naive"]["accuracy"], ref["accuracy"]))
        worst = max(float(np.max(np.abs(arms["naive"]["forgetting"] - ref["forgetting"]))),
                    float(np.max(np.abs(arms["naive"]["accuracy"] - ref["accuracy"]))))
        out["C0a"] = {"identical": same, "worst_abs_difference": worst}
        print(f"   identical over {len(ref['forgetting'])} replicates: {same}   worst |difference| {worst:.3g}")

    print("\n== the control draws (rule 10: the control is a population, and one draw is one sample) ==")
    draws = []
    for d in args.draws:
        rand = load(d, "ewc-block-rand")
        if rand is None or arms["ewc-block"] is None:
            print(f"   {d}: not on disk")
            continue
        fp = json.loads(Path(d).read_text(encoding="utf-8")).get("partition_draw")
        c = paired(arms["ewc-block"]["forgetting"], rand["forgetting"])
        draws.append(c)
        print(f"   {Path(d).name}: block minus rand {c['change']:+.4f} +/- {c['sem']:.4f} = {c['sigma']:5.2f} sigma"
              + (f"   [partition seed {fp['matched_random_draw_seed']}, {fp['fingerprint_sha1']}]" if fp else
                 "   [no partition_draw block: written before the flag]"))

    v = verdicts(arms, draws)
    out.update(v)
    if "P1" not in v:
        print(f"\n{v['verdict']} -- no registered verdict is printed from an incomplete set.")
        if args.json_out:
            write_json(args.json_out, out)
        return 0

    c = v["P1"]
    print(f"\n== P1, the fire: does the biological partition beat its matched control at >= {P1_SIGMA:g} sigma? ==")
    print(f"   mean over {c['k_draws']} draws {c['mean_change']:+.4f}  (draw sd {c['draw_sd']:.4f}, "
          f"{c['draw_df']} df)")
    print(f"   sem: draw component {c['sem_draw_component']:.4f} + paired component "
          f"{c['sem_paired_component']:.4f} -> total {c['sem_total']:.4f}  = {c['sigma']:.2f} sigma")
    print(f"   ->  P1 {'HOLDS' if v['P1_holds'] else 'FAILS'}"
          + ("   (the falsifier FIRES: the contrast is within 2 sigma of zero)"
             if v["falsifier_fires"] else "   (the falsifier does not fire)"))
    print(f"   the base family's comparator is `e135` at five replicates: -0.0125, unresolved")

    print("\nNOTE: one read-out (32), one overlap value (1.0), one partition (`cell_class`), one lambda (3e-3),")
    print("      forty replicates. The draw term has K-1 degrees of freedom, so three draws bound it rather")
    print("      than measure it, and a contrast that resolves on the paired component alone is reported with")
    print("      that component named rather than folded into a single sigma.")
    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
