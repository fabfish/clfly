"""E139 -- is the interference instrument channel-blind? `theta`'s term falls 45-fold while the forgetting does not.

The interference account's prediction is one line: `first_order = <grad_j(theta), theta_final - theta_j>`, the
change a later task's displacement causes in task `j`'s loss. `e133` has `naive` and `ewc` at forty paired seeds
on this configuration, so the two arms' interference terms can be compared directly — and the answer is that the
penalty **reduces the term by 98% (10.34σ) while its forgetting moves 1.21σ**.

    python -m experiments.e139_whole_body_interference \
        --paired runs/e133_r32_naive_ewc_40reps.json --methods naive ewc

**The explanation is that the term is built from `theta` alone.** `e125` measured that 70% of this
configuration's forgetting is carried by the 800 per-neuron offsets, and `e137` that the penalty's effect on
`theta` is matched by an opposite movement in that channel — so the instrument is evaluated over the half the
penalty squeezed and not the half the damage moved to.

**Which is why the same script reads the `whole_body` block** that `e8_rate_network.py` now records beside it:
the same one-line account with the bias's gradient and displacement included, and the `theta`-only and
`bias`-only halves of it separately. If the whole-body term does **not** fall the way the `theta`-only form does,
the channel-blindness is the explanation; if it falls as hard, the explanation is wrong and something else makes
the forgetting insensitive. **The verdict is printed only when the artifact exists**, so that a missing file is
reported as missing rather than as a zero.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

TERMS = ("first_order", "cosine", "grad_norm", "disp_norm")
WHOLE_BODY_RATIO_BOUND = 0.5      # P1: the whole-body term is NOT reduced as the theta-only form is
FALSIFIER_RATIO = 0.1             # ... and if it is, the explanation is wrong


def arm_cumulative(rep: dict, j: int, key: str) -> float:
    return float(rep["interference"][j]["cumulative"][key])


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = a - b
    sem = float(d.std(ddof=1) / math.sqrt(len(d)))
    return {"naive": float(b.mean()), "other": float(a.mean()), "change": float(d.mean()),
            "sem": sem, "sigma": float(abs(d.mean()) / sem) if sem else float("nan"),
            "ratio": float(a.mean() / b.mean()) if b.mean() else float("nan"), "n": len(d)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paired", type=Path, default=Path("runs/e133_r32_naive_ewc_40reps.json"),
                   help="an artifact holding both arms at the same seeds")
    p.add_argument("--methods", nargs=2, default=["naive", "ewc"], metavar=("BASELINE", "OTHER"))
    p.add_argument("--whole-body", type=Path, default=Path("runs/e139_r32_wholebody.json"),
                   help="the artifact carrying the whole_body block; reported as missing if it is not there")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    out = {"paired": str(args.paired), "methods": args.methods}
    base, other = args.methods
    d = json.loads(args.paired.read_text(encoding="utf-8"))
    rb, ro = d["methods"][base]["replicates"], d["methods"][other]["replicates"]

    print(f"== {args.paired} ==  ({base} against {other}, {len(rb)} paired seeds)")
    print("1. the theta-only first-order account, per task")
    for j in range(len(rb[0]["interference"])):
        print(f"   task {j}:")
        for key in TERMS:
            x = np.array([arm_cumulative(r, j, key) for r in ro])
            y = np.array([arm_cumulative(r, j, key) for r in rb])
            v = paired(x, y)
            out.setdefault("theta_only", {}).setdefault(f"task_{j}", {})[key] = v
            print(f"     cumulative {key:12} {base} {v['naive']:+10.4f}  {other} {v['other']:+10.4f}  "
                  f"change {v['change']:+10.4f} +/- {v['sem']:.4f} = {v['sigma']:6.2f} sigma   "
                  f"ratio {v['ratio']:.3f}")

    print("\n2. the forgetting, on the same artifact -- the effect the term exists to predict")
    f = paired(np.array([r["mean_forgetting"] for r in ro]),
               np.array([r["mean_forgetting"] for r in rb]))
    out["forgetting"] = f
    print(f"   {base} {f['naive']:+.4f}  {other} {f['other']:+.4f}  change {f['change']:+.4f} = "
          f"{f['sigma']:.2f} sigma")
    first = out["theta_only"]["task_0"]["first_order"]
    print(f"\n   SO: the term falls by a factor of {1 / first['ratio']:.0f} at {first['sigma']:.1f} sigma while the")
    print(f"       effect it exists to predict moves {f['sigma']:.2f} sigma.")

    print("\n3. and the whole-body form, which is the explanation being tested")
    if not args.whole_body.is_file():
        out["whole_body"] = {"attempted": False, "reason": "artifact not on disk"}
        print(f"   {args.whole_body} is not on disk -- the whole-body test is NOT reported, rather than")
        print(f"   reported as a zero.")
    else:
        w = json.loads(args.whole_body.read_text(encoding="utf-8"))
        wb, wo = w["methods"][base]["replicates"], w["methods"][other]["replicates"]
        for label, key in (("whole_body cumulative", "cumulative"),
                           ("  of which theta-only", "theta_only_cumulative"),
                           ("  of which bias-only", "bias_only_cumulative")):
            j = 0
            x = np.array([r["interference"][j]["whole_body"][key] for r in wo])
            y = np.array([r["interference"][j]["whole_body"][key] for r in wb])
            v = paired(x, y)
            out.setdefault("whole_body", {})[key] = v
            print(f"   task {j} {label:22} {base} {v['naive']:+10.4f}  {other} {v['other']:+10.4f}  "
                  f"change {v['change']:+10.4f} = {v['sigma']:6.2f} sigma   ratio {v['ratio']:.3f}")
        r = out["whole_body"]["cumulative"]["ratio"]
        out["P1_whole_body_ratio"] = r
        out["P1_holds"] = bool(r > WHOLE_BODY_RATIO_BOUND)
        out["falsifier_fired"] = bool(r < FALSIFIER_RATIO)
        print(f"\n   P1 (whole-body ratio > {WHOLE_BODY_RATIO_BOUND}) : "
              f"{'HOLDS' if out['P1_holds'] else 'FAILS'}   (the theta-only ratio was {first['ratio']:.3f})")
        print(f"   falsifier (ratio < {FALSIFIER_RATIO})          : "
              f"{'FIRED -- channel-blindness is not the explanation' if out['falsifier_fired'] else 'does not fire'}")

    print("\nNOTE: the lead in the finding -- r(first_order, forgetting) = +0.329 in the naive arm and -0.221 in")
    print("      the ewc arm -- is a within-arm correlation at n = 40 with the sign absent in the other arm, so")
    print("      it is a lead and is not part of any verdict here.")
    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
