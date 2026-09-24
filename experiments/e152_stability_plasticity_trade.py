"""E152 -- the constraint's two prices: `mean_forgetting` and the accuracy on the task no forgetting term covers.

`e151` established, per task, that the aggregate is a mean over the first `T - 1` tasks and that the newest
task's final accuracy is the one quantity it cannot contain -- and that ten of the twelve distinct constrained
arms pay a resolved cost there. This script asks the follow-up question the plan's lambda sweep already half
answers: **is that cost a trade against the stability gain, or is it inside the same movement?**

The plan's lambda sweep concluded a **bracketed interior optimum** at `lam = 3e-4`: forgetting falls from +0.0750
at `lam = 0` to +0.0396 at 3e-4 and rises afterwards. That statement is about ONE axis, and a trade-off needs
two. So every constrained arm is placed in the (forgetting, newest-task accuracy) plane here, and the question
is answered by **dominance** rather than by a curve:

    arm X is dominated by arm Y  <=>  Y's forgetting is no worse AND Y's newest-task accuracy is no worse,
                                      strictly better on at least one

**An arm that is dominated is not a point on a trade-off -- it is a worse method, full stop**, and the two
classes are what this script separates:

    dominated      some other arm is at least as good on both axes
    on the frontier  no arm is, so its cost is the price of something it uniquely buys

and, along a one-dimensional knob, the step test: **if moving the knob one step worsens both axes, the knob has
no further use above that point**, which is a stronger statement than "the benefit stopped growing".

    python -m experiments.e152_stability_plasticity_trade
    python -m experiments.e152_stability_plasticity_trade --json-out runs/e152_trade.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import load_arm, paired

#: the reference every contrast is against, and every arm in the plane
REFERENCE = ("naive", "runs/e133_r32_naive_ewc_40reps.json", "naive")
ARMS: tuple[tuple[str, str, str, str], ...] = (
    ("ewc lam 3e-4", "runs/e141_r32_ewc_lam3e-4.json", "ewc", "the sweep's optimum"),
    ("ewc lam 3e-3", "runs/e133_r32_naive_ewc_40reps.json", "ewc", "the paper's own lam"),
    ("ewc lam 3e-2", "runs/e141_r32_ewc_lam3e-2.json", "ewc", "top of the sweep"),
    ("ewc lam 3e-1", "runs/e141_r32_ewc_lam3e-1.json", "ewc", "top of the sweep"),
    ("anchored 1.0", "runs/e138_r32_ewc_anchorbias1.json", "ewc", "the coverage route, weak scale"),
    ("anchored 33.2", "runs/e138_r32_ewc_anchorbias33.json", "ewc", "the coverage route, strong scale"),
    ("frozen offsets", "runs/e125_r32_frozenbias.json", "naive", "the free constraint"),
    ("frozen+ewc 3e-4", "runs/e147_r32_frozenbias_ewc_lam3e-4.json", "ewc", "the pair"),
    ("frozen+ewc 3e-3", "runs/e147_r32_frozenbias_ewc_lam3e-3.json", "ewc",
     "the pair at the other lambda, added when it landed"),
    ("replay", "runs/e140_r32_methods_plastic_40reps.json", "replay", "not a constraint"),
)
#: the one-dimensional knob, in order -- the step test walks this
LAMBDA_LADDER = ("ewc lam 3e-4", "ewc lam 3e-3", "ewc lam 3e-2", "ewc lam 3e-1")

#: the same plane on the **harder family**, whose baseline forgets 42% more. Added when `e148` landed, so that
#: the frontier is a cross-family statement rather than one family's. Its reference is that family's own `naive`.
WIRING_ARMS: tuple[tuple[str, str, str, str], ...] = (
    ("ewc (wiring)", "runs/e144_r32_overlap1_methods_40reps.json", "ewc", "the diagonal, this family's best penalty"),
    ("block (wiring)", "runs/e144_r32_overlap1_methods_40reps.json", "ewc-block", "the coarser partition"),
    ("block-rand (wiring)", "runs/e144_r32_overlap1_methods_40reps.json", "ewc-block-rand",
     "its group-size-matched control, draw 0"),
    ("frozen offsets (wiring)", "runs/e143_r32_overlap1_frozenbias.json", "naive", "the free constraint"),
    ("replay (wiring)", "runs/e148_r32_overlap1_replay.json", "replay", "not a constraint"),
)
WIRING_REFERENCE = ("naive (wiring)", "runs/e144_r32_overlap1_methods_40reps.json", "naive")


def plane(arms: dict[str, dict], ref: dict) -> dict:
    """Each arm's position: the stability gain, the plasticity cost, and the index between them.

    ``efficiency`` is ``abs(forgetting change) / abs(newest change)`` and it is a **heuristic index**, not a
    quantity with units: the two axes are a retention difference and an accuracy, so the ratio is quoted to rank
    arms and never to compare to 1.
    """
    out: dict = {}
    for label, arm in arms.items():
        if arm is None:
            continue
        forg = paired(arm["forgetting"], ref["forgetting"])
        newest = paired(arm["newest"], ref["newest"])
        out[label] = {
            "forgetting_change": forg["change"], "forgetting_sigma": forg["sigma"],
            "newest_change": newest["change"], "newest_sigma": newest["sigma"],
            "newest_level": float(arm["newest"].mean()),
            "efficiency": (abs(forg["change"]) / abs(newest["change"])) if newest["change"] else float("nan"),
        }
    return out


def dominates(a: dict, b: dict) -> bool:
    """Is ``a`` at least as good as ``b`` on BOTH axes, and strictly better on one?

    Better is: lower forgetting (a retention difference that falls), higher newest-task accuracy. **This is a
    comparison of point estimates**, and the report says so: whether a dominance is *resolved* is a separate
    question, graded below, because a frontier drawn from point estimates at a resolution the pairwise contrast
    does not have is exactly the kind of claim this project keeps having to retract.
    """
    no_worse = a["forgetting_change"] <= b["forgetting_change"] and a["newest_change"] >= b["newest_change"]
    strictly = (a["forgetting_change"] < b["forgetting_change"]
                or a["newest_change"] > b["newest_change"])
    return bool(no_worse and strictly)


def evidence(arms: dict, better: str, worse: str) -> dict:
    """How resolved is one dominance? Its own paired contrasts on the two axes, with the `e56` grade."""
    a, b = arms[better], arms[worse]
    forg = paired(a["forgetting"], b["forgetting"])
    newest = paired(a["newest"], b["newest"])
    resolved = int(forg["sigma"] >= 2) + int(newest["sigma"] >= 2)
    return {"forgetting_sigma": forg["sigma"], "newest_sigma": newest["sigma"], "resolved_axes": resolved,
            "grade": ("resolved on both" if resolved == 2 else
                      "resolved on one" if resolved == 1 else "point estimates only")}


def frontier(pts: dict, arms: dict | None = None) -> dict:
    """Who is dominated by whom, how well resolved each dominance is, and who is left on the frontier."""
    out = {}
    for label, p in pts.items():
        dominators = sorted(k for k, q in pts.items() if k != label and dominates(q, p))
        out[label] = {"dominated_by": dominators}
        if arms is not None:
            out[label]["evidence"] = {k: evidence(arms, k, label) for k in dominators}
    return {"arms": out, "frontier": sorted(k for k, v in out.items() if not v["dominated_by"])}


def ladder_steps(arms: dict[str, dict], ladder=LAMBDA_LADDER) -> list[dict]:
    """The step test along the knob: does moving one step worsen BOTH axes, and is each step resolved?

    Each step is its own **paired** contrast between the two arms, on the same forty seeds -- not a difference of
    the two arms' sigmas, which would be a resolution the step does not have.
    """
    steps = []
    for lo, hi in zip(ladder, ladder[1:]):
        a, b = arms.get(lo), arms.get(hi)
        if a is None or b is None:
            continue
        forg = paired(b["forgetting"], a["forgetting"])
        newest = paired(b["newest"], a["newest"])
        steps.append({"from": lo, "to": hi,
                      "forgetting_change": forg["change"], "forgetting_sigma": forg["sigma"],
                      "newest_change": newest["change"], "newest_sigma": newest["sigma"],
                      "both_worse": bool(forg["change"] > 0 and newest["change"] < 0),
                      "both_resolved": bool(forg["sigma"] >= 2 and newest["sigma"] >= 2)})
    return steps


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    ref = load_arm(Path(REFERENCE[1]), REFERENCE[2])
    if ref is None:
        print(f"the reference arm is not on disk: {REFERENCE[1]} [{REFERENCE[2]}]")
        return 1
    arms, missing = {}, []
    for label, path, method, note in ARMS:
        arm = load_arm(Path(path), method)
        if arm is None:
            missing.append(f"{label} <- {path} [{method}]")
        arms[label] = arm
    if missing:
        print("not printed: " + "; ".join(missing))
        return 1

    pts = plane(arms, ref)
    print(f"== the plane, against `{REFERENCE[0]}` (forgetting lower is better, newest accuracy higher is) ==")
    print(f"   {'arm':<17}{'d_forgetting':>13}{'sigma':>7}{'d_newest':>11}{'sigma':>7}"
          f"{'newest':>9}{'index':>8}")
    for label, p in sorted(pts.items(), key=lambda kv: kv[1]["forgetting_change"]):
        print(f"   {label:<17}{p['forgetting_change']:>+13.4f}{p['forgetting_sigma']:>7.2f}"
              f"{p['newest_change']:>+11.4f}{p['newest_sigma']:>7.2f}{p['newest_level']:>9.4f}"
              f"{p['efficiency']:>8.2f}")

    fr = frontier(pts, arms)
    print("\n== dominance: an arm that is worse on BOTH axes is not a point on a trade-off ==")
    for label in sorted(pts, key=lambda k: len(fr["arms"][k]["dominated_by"])):
        dom = fr["arms"][label]["dominated_by"]
        print(f"   {label:<17} dominated by {len(dom):>2} arm(s)"
              + (" -- ON THE FRONTIER" if not dom else ""))
        for k in dom:
            e = fr["arms"][label]["evidence"][k]
            print(f"       by {k:<16} forgetting {e['forgetting_sigma']:>5.2f}s  newest {e['newest_sigma']:>5.2f}s"
                  f"   -> {e['grade']}")

    print("\n== the step test along `lam`, each step its own paired contrast ==")
    for s in ladder_steps(arms):
        print(f"   {s['from']:<14} -> {s['to']:<14} forgetting {s['forgetting_change']:+.4f} "
              f"({s['forgetting_sigma']:.2f}s)   newest {s['newest_change']:+.4f} ({s['newest_sigma']:.2f}s)   "
              f"both worse: {s['both_worse']}   both resolved: {s['both_resolved']}")

    print("\n== the same plane on the harder family, whose baseline forgets 42% more ==")
    wiring, missing_w = {}, []
    for label, path, method, note in WIRING_ARMS:
        a = load_arm(Path(path), method)
        if a is None:
            missing_w.append(f"{label} <- {path} [{method}]")
        wiring[label] = a
    ref_w = load_arm(Path(WIRING_REFERENCE[1]), WIRING_REFERENCE[2])
    wiring_summary = None
    if missing_w or ref_w is None:
        print("   not printed: " + "; ".join(missing_w + ([] if ref_w else [WIRING_REFERENCE[0]])))
    else:
        pts_w = plane(wiring, ref_w)
        print(f"   {'arm':<24}{'d_forgetting':>13}{'sigma':>7}{'d_newest':>11}{'sigma':>7}"
              f"{'newest':>9}{'index':>8}")
        for label, p in sorted(pts_w.items(), key=lambda kv: kv[1]["forgetting_change"]):
            print(f"   {label:<24}{p['forgetting_change']:>+13.4f}{p['forgetting_sigma']:>7.2f}"
                  f"{p['newest_change']:>+11.4f}{p['newest_sigma']:>7.2f}{p['newest_level']:>9.4f}"
                  f"{p['efficiency']:>8.2f}")
        fr_w = frontier(pts_w, wiring)
        for label in sorted(pts_w, key=lambda k: len(fr_w["arms"][k]["dominated_by"])):
            dom = fr_w["arms"][label]["dominated_by"]
            print(f"   {label:<24} dominated by {len(dom):>2} arm(s)"
                  + (" -- ON THE FRONTIER" if not dom else ""))
            for k in dom:
                e = fr_w["arms"][label]["evidence"][k]
                print(f"       by {k:<22} forgetting {e['forgetting_sigma']:>5.2f}s  "
                      f"newest {e['newest_sigma']:>5.2f}s   -> {e['grade']}")
        wiring_summary = {"plane": pts_w, "frontier": fr_w}

    if args.json_out:
        write_json(args.json_out, {"reference": REFERENCE[0], "plane": pts,
                                   "frontier": fr, "ladder_steps": ladder_steps(arms),
                                   "wiring_reference": WIRING_REFERENCE[0],
                                   "wiring": wiring_summary})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
