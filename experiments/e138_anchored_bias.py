"""E138 -- does putting the bias **inside** the penalty fix what no lambda can reach?

`e125` showed the 800 per-neuron offsets carry 70% of this configuration's forgetting; `e137` that the diagonal
penalty relocates adaptation into them; `e133` that at forty replicates the penalty is 1.21 sigma from naive.
`e138`'s two arms add the bias's own diagonal Fisher to the loss, at two anchoring strengths that bracket the
ambiguity: `SCALE = 1.0` (every parameter alike, the bias carrying 2.9% of the penalty's mass) and
`SCALE = 33.2` (the two sets carrying equal total mass).

    python -m experiments.e138_anchored_bias

reading `runs/e133_r32_naive_ewc_40reps.json` for the unanchored comparators and the two `e138` artifacts for the
anchored arms. **A missing artifact is reported as missing and no verdict is printed from it**, so that an
unfinished run cannot masquerade as a zero.

The registered checks, in the order the pre-registration states them:

* **C0a** task 0's bias step is identical across the anchored arms and the unanchored one -- no Fisher and no
  anchor exist before the first task, so a difference would be a bug in the flag and not a result;
* **C0b** the bias's cumulative movement falls monotonically in the scale;
* **P1** the forgetting falls monotonically in the scale, with the frozen-bias value `e125` measured (+0.0227)
  as a limit a penalty should approach from above and not reach;
* **falsifier** the `SCALE 33.2` arm within 2 sigma of the unanchored arm -- covering the channel does not fix
  the penalty;
* **P2** per-task forgetting, because `e133`'s unanchored mean is the cancellation of a 3.79 sigma improvement on
  task 0 and a degradation on task 1, and the question is whether anchoring removes that trade or shifts it.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

UNANCHORED = "runs/e133_r32_naive_ewc_40reps.json"
SCALE1 = "runs/e138_r32_ewc_anchorbias1.json"
SCALE33 = "runs/e138_r32_ewc_anchorbias33.json"
FROZEN_LIMIT = 0.0227            # e125's frozen-bias forgetting: the limit, not a target
FALSIFIER_SIGMA = 2.0


def load_arm(path: Path, method: str) -> dict | None:
    """The three quantities the registration names, or None when the artifact is not on disk."""
    if not Path(path).is_file():
        return None
    m = json.loads(Path(path).read_text(encoding="utf-8"))["methods"][method]
    reps = m["replicates"]
    return {
        "forgetting": np.array([r["mean_forgetting"] for r in reps]),
        "per_task": np.array([r["forgetting_per_task"][:-1] for r in reps]),
        "bias_step_task0": np.array([r["bias_norms"][0]["step"] for r in reps]),
        "bias_from_zero_task0": np.array([r["bias_norms"][0]["from_zero"] for r in reps]),
        "bias_path": np.array([sum(b["step"] for b in r["bias_norms"]) for r in reps]),
        "bias_from_zero": np.array([r["bias_norms"][-1]["from_zero"] for r in reps]),
        "theta_drift": np.array([r["theta_drift"][-1] for r in reps]),
        "accuracy": float(m["final_accuracy"]),
        "n": len(reps),
    }


def paired(a: np.ndarray, b: np.ndarray) -> dict:
    d = a - b
    sem = float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float("nan")
    return {"a": float(a.mean()), "b": float(b.mean()), "change": float(d.mean()), "sem": sem,
            "sigma": float(abs(d.mean()) / sem) if sem else float("nan"), "n": len(d)}


def monotone_decreasing(values: list[float]) -> bool:
    return all(values[i] > values[i + 1] for i in range(len(values) - 1))


def verdicts(arms: dict[str, dict], frozen_limit: float = FROZEN_LIMIT) -> dict:
    """The registered checks, on whichever arms are present. Pure, so that a test can drive it."""
    present = [k for k, v in arms.items() if v is not None]
    out: dict = {"arms_present": present}
    if len(present) < 2:
        out["verdict"] = "not enough arms on disk"
        return out

    c0a = {k: float(arms[k]["bias_step_task0"].mean()) for k in present}
    out["C0a_task0_bias_step"] = c0a
    spread = max(c0a.values()) - min(c0a.values())
    out["C0a_spread"] = spread
    out["C0a_holds"] = bool(spread < 1e-9)

    path = {k: float(arms[k]["bias_path"].mean()) for k in present}
    out["C0b_bias_path"] = path
    order = [k for k in ("unanchored", "scale_1.0", "scale_33.2") if k in path]
    out["C0b_order"] = order
    out["C0b_holds"] = bool(monotone_decreasing([path[k] for k in order]))

    forget = {k: float(arms[k]["forgetting"].mean()) for k in present}
    out["P1_forgetting"] = forget
    out["P1_holds"] = bool(monotone_decreasing([forget[k] for k in order]))
    out["frozen_limit"] = frozen_limit

    if "scale_33.2" in present and "unanchored" in present:
        p = paired(arms["scale_33.2"]["forgetting"], arms["unanchored"]["forgetting"])
        out["P1_scale33_vs_unanchored"] = p
        out["falsifier_fired"] = bool(p["sigma"] < FALSIFIER_SIGMA)
        # and the same contrast for the manipulation check, which is the arm's own claim
        out["C0b_scale33_vs_unanchored"] = paired(arms["scale_33.2"]["bias_path"],
                                                  arms["unanchored"]["bias_path"])
    if "scale_1.0" in present and "unanchored" in present:
        out["P1_scale1_vs_unanchored"] = paired(arms["scale_1.0"]["forgetting"],
                                                arms["unanchored"]["forgetting"])
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--unanchored", type=Path, default=Path(UNANCHORED))
    p.add_argument("--scale1", type=Path, default=Path(SCALE1))
    p.add_argument("--scale33", type=Path, default=Path(SCALE33))
    p.add_argument("--frozen-limit", type=float, default=FROZEN_LIMIT)
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    arms = {
        "unanchored": load_arm(args.unanchored, "ewc"),
        "naive": load_arm(args.unanchored, "naive"),
        "scale_1.0": load_arm(args.scale1, "ewc"),
        "scale_33.2": load_arm(args.scale33, "ewc"),
    }
    out = {"inputs": {"unanchored": str(args.unanchored), "scale1": str(args.scale1),
                      "scale33": str(args.scale33)}}

    print("== the arms ==")
    for k, a in arms.items():
        if a is None:
            print(f"   {k:11} not on disk")
        else:
            print(f"   {k:11} n {a['n']:3d}  forgetting {a['forgetting'].mean():+.4f} "
                  f"(sd {a['forgetting'].std(ddof=1):.4f})  bias_path {a['bias_path'].mean():.4f}  "
                  f"theta_drift {a['theta_drift'].mean():.4f}  accuracy {a['accuracy']:.4f}")

    measured = {k: v for k, v in arms.items() if v is not None and k != "naive"}
    v = verdicts(measured, args.frozen_limit)
    out.update(v)
    if "P1_holds" not in v:
        print(f"\n{v['verdict']} -- no registered verdict is printed from an incomplete set of arms.")
        if args.json_out:
            write_json(args.json_out, out)
        return 0

    print("\n== C0a: task 0's bias step must be identical across arms (no Fisher, no anchor, before task 0) ==")
    for k, s in v["C0a_task0_bias_step"].items():
        print(f"   {k:11} {s:.10f}")
    print(f"   spread {v['C0a_spread']:.3e}  ->  C0a {'HOLDS' if v['C0a_holds'] else 'FAILS'}")

    print("\n== C0b: the bias's cumulative movement must fall in the scale (the manipulation check) ==")
    for k in v["C0b_order"]:
        print(f"   {k:11} bias_path {v['C0b_bias_path'][k]:.4f}")
    print(f"   ->  C0b {'HOLDS' if v['C0b_holds'] else 'FAILS'}")
    if "C0b_scale33_vs_unanchored" in v:
        c = v["C0b_scale33_vs_unanchored"]
        print(f"   scale 33.2 minus unanchored: {c['change']:+.4f} +/- {c['sem']:.4f} = {c['sigma']:.2f} sigma")

    print("\n== P1, the fire: the forgetting must fall in the scale ==")
    for k in v["C0b_order"]:
        print(f"   {k:11} forgetting {v['P1_forgetting'][k]:+.4f}")
    print(f"   frozen-bias limit (e125) {v['frozen_limit']:+.4f} -- to be approached from above, not reached")
    for key, label in (("P1_scale1_vs_unanchored", "scale 1.0  minus unanchored"),
                       ("P1_scale33_vs_unanchored", "scale 33.2 minus unanchored")):
        if key in v:
            c = v[key]
            print(f"   {label}: {c['change']:+.4f} +/- {c['sem']:.4f} = {c['sigma']:5.2f} sigma")
    print(f"   ->  P1 {'HOLDS' if v['P1_holds'] else 'FAILS'}")
    if "falsifier_fired" in v:
        print(f"   falsifier (scale 33.2 within {FALSIFIER_SIGMA} sigma of unanchored): "
              f"{'FIRED -- covering the channel does not fix the penalty' if v['falsifier_fired'] else 'does not fire'}")

    print("\n== P2, descriptive: per-task forgetting, and whether the trade moved ==")
    for k in ("naive", "unanchored", "scale_1.0", "scale_33.2"):
        a = arms.get(k)
        if a is None:
            continue
        per = a["per_task"].mean(axis=0)
        print(f"   {k:11} " + "  ".join(f"task {j} {per[j]:+.4f}" for j in range(len(per))))

    print("\nNOTE: one read-out (32), one lambda, one circuit, three tasks; the bias's share is read-out")
    print("      dependent (e134: 70/89/83% at read-outs 32/128/1307), so a result here is a result where the")
    print("      confound is largest. A penalty is not a freeze: the limit is e138's to approach, not to reach.")
    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
