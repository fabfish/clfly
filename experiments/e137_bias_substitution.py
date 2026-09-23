"""E137 -- the penalty relocates adaptation into the channel it does not cover.

`e125` measured that holding the 800 per-neuron offsets at their initialisation takes this configuration's naive
forgetting from **+0.0750 to +0.0227** — 70% of it — and `e133` found that diagonal EWC at forty replicates is
**1.21σ** from naive, against the **2.47σ** the paper quotes from five. Those are two facts about the same
channel, and this script puts them together: **the penalty constrains `theta`, so where does the adaptation go?**

    python -m experiments.e137_bias_substitution --json-out runs/e137_bias_substitution.json

The claim is checkable in the code — `model.bias` appears in `e8_rate_network.py` only in the optimiser's
parameter list, the drift record and the checkpoint save, and `clfly/network/fisher.py` does not mention it — but
**a code claim about what a penalty does not touch is not a measurement of what happens instead**, and the two
quantities that matter are recorded in every artifact: `theta_drift` and `bias_norms`.

**And one lead, printed as a lead.** If the channel carries 70% of the forgetting, then across seeds its own
movement should be the trajectory quantity with the most purchase on the forgetting. It is measured here for the
first time at n = 40, and it is printed **with its `n` and its sign in the other arm** rather than as a result:
one arm showing r = +0.34 at n = 40 is a 3% draw and the project's rule is that such a lead is a lead.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

DEFAULT_RUN = "runs/e133_r32_naive_ewc_40reps.json"
QUANTITIES = ("bias_from_zero", "bias_step", "theta_drift", "full_train_loss")


def arm(run: Path, method: str) -> dict:
    m = json.loads(Path(run).read_text(encoding="utf-8"))["methods"][method]
    reps = m["replicates"]
    return {
        "forgetting": np.array([r["mean_forgetting"] for r in reps]),
        "bias_from_zero": np.array([r["bias_norms"][-1]["from_zero"] for r in reps]),
        "bias_step": np.array([r["bias_norms"][-1]["step"] for r in reps]),
        "theta_drift": np.array([r["theta_drift"][-1] for r in reps]),
        "full_train_loss": np.array([r["full_train_loss"][0] for r in reps]),
        "per_task_forgetting": np.array([r["forgetting_per_task"][:-1] for r in reps]),
        "bias_step_per_task": np.array([[b["step"] for b in r["bias_norms"][:-1]] for r in reps]),
        "accuracy": float(m["final_accuracy"]),
    }


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = a - b
    sem = float(d.std(ddof=1) / math.sqrt(len(d)))
    return {"difference": float(d.mean()), "sem": sem,
            "sigma": float(abs(d.mean()) / sem) if sem else float("nan"), "n": len(d)}


def correlate(x: np.ndarray, y: np.ndarray) -> dict:
    r = float(np.corrcoef(x, y)[0, 1])
    n = len(x)
    t = r * math.sqrt(n - 2) / math.sqrt(max(1 - r * r, 1e-300))
    return {"r": r, "spearman": float(np.corrcoef(np.argsort(np.argsort(x)),
                                                  np.argsort(np.argsort(y)))[0, 1]),
            "n": n, "t": t,
            # two-sided p from a t distribution with n-2 df, via the incomplete beta is overkill for one number:
            # reported as the t so that the reader can see the size rather than a p dressed as a verdict.
            "p_two_sided_approx": float(2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2)))))}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", type=Path, default=Path(DEFAULT_RUN))
    p.add_argument("--methods", nargs="*", default=["naive", "ewc"])
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    A = {m: arm(args.run, m) for m in args.methods}
    out = {"run": str(args.run), "arms": {}}

    print(f"== {args.run} ==")
    print("1. where does the adaptation go? (last checkpoint, n = %d each)" % len(A[args.methods[0]]["forgetting"]))
    for m, a in A.items():
        print(f"   {m:6} theta_drift {a['theta_drift'].mean():.4f}   bias_from_zero "
              f"{a['bias_from_zero'].mean():.4f}   forgetting {a['forgetting'].mean():+.4f}   "
              f"accuracy {a['accuracy']:.4f}")
    if len(A) == 2:
        x, y = args.methods
        for q in ("theta_drift", "bias_from_zero", "forgetting"):
            r = paired(A[x][q], A[y][q])
            ratio = A[x][q].mean() / A[y][q].mean()
            print(f"   {x} minus {y} on {q:16}: {r['difference']:+.4f} +/- {r['sem']:.4f} = "
                  f"{r['sigma']:5.2f} sigma   (ratio {ratio:.3f})")
            out["arms"].setdefault(q, {})[f"{x}_minus_{y}"] = {**r, "ratio": float(ratio)}

    print(f"\n2. the lead: does a quantity track the forgetting ACROSS SEEDS, within one arm?")
    for m, a in A.items():
        f = a["forgetting"]
        out["arms"].setdefault("correlations", {})[m] = {}
        for q in QUANTITIES:
            c = correlate(a[q], f)
            out["arms"]["correlations"][m][q] = c
            print(f"   {m:6} {q:18} r {c['r']:+.3f}  spearman {c['spearman']:+.3f}  n {c['n']}  "
                  f"t {c['t']:+.2f}")
    print("\n   and per task, where the task-specific step might track the task-specific forgetting:")
    for m, a in A.items():
        for k in range(a["per_task_forgetting"].shape[1]):
            c = correlate(a["bias_step_per_task"][:, k], a["per_task_forgetting"][:, k])
            out["arms"].setdefault("per_task", {}).setdefault(m, {})[f"task_{k}"] = c
            print(f"   {m:6} task {k}: r(bias_step_{k}, forgetting_{k}) {c['r']:+.3f}  n {c['n']}")

    print("\nNOTE: one arm at r = +0.34 with n = 40 is a 3% draw, and the same quantity is negative in the other")
    print("      arm -- so section 2 is a LEAD and not a result, which is why it is printed with its n and its")
    print("      other-arm sign rather than as a finding. Section 1 is a paired comparison of forty seeds and")
    print("      carries its own resolution.")
    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
