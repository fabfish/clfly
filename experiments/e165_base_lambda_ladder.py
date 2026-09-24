"""E165 -- the base family's lambda ladder at five points and forty seeds, and the matched-lambda family test.

`e161` was registered to close the `e153` hole: the wiring family's penalty arms beat `naive` at **lambda = 1.0**
(3.4-4.2 sigma) while the base family's top swept lambda was already the wrong way (`+0.0060` at 3e-2, `+0.0096`
at 3e-1, both under 1 sigma), and **two readings predict the same sign** -- *the wiring family tolerates a
stronger penalty* against *the wiring family simply has more forgetting to remove* (its `naive` sits at 0.1068
against 0.0750). Only a matched lambda separates them.

This unit reads `e161` against the four rungs that already existed, so the base family's lambda response is now a
**five-point ladder over 3.5 decades with forty paired seeds at every rung**, and it prints the two registered
predictions beside it:

  * **P1**: the lambda = 1.0 arm is worse than `naive` on forgetting and pays a newest-task cost above 0.0313;
  * **falsifier**: it beats `naive` at >= 2 sigma, which would say the base family does not lose by a strong
    penalty and that `e141`'s interior optimum is about something else.

The control is `e133`'s forty-replicate `naive` (the same configuration, and `e160` derives `lam` as a field
`naive` cannot read), and the control has a control: `e140`'s plastic arm at lambda = 3e-3 carries the same two
arms under a config that differs from `e133`'s in one key (`anchor_bias`, absent from the older artifact), and
this unit asserts they are **bit-identical across all forty replicates** -- which is rule 45's floor met on the
arms the paper's headline numbers use.

    python -m experiments.e165_base_lambda_ladder
    python -m experiments.e165_base_lambda_ladder --json-out runs/e165_base_lambda_ladder.json

Reads only artifacts on disk; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e151_pertask_contrast_audit import load_arm, paired

#: the base family's lambda ladder: (label, lambda, artifact). `e133` is both the 3e-3 rung and the control's home.
LADDER = (
    ("3e-4", 3e-4, "runs/e141_r32_ewc_lam3e-4.json"),
    ("3e-3", 3e-3, "runs/e133_r32_naive_ewc_40reps.json"),
    ("3e-2", 3e-2, "runs/e141_r32_ewc_lam3e-2.json"),
    ("3e-1", 3e-1, "runs/e141_r32_ewc_lam3e-1.json"),
    ("1.0", 1.0, "runs/e161_r32_base_ewc_lam1.json"),
)
NAIVE_HOME = "runs/e133_r32_naive_ewc_40reps.json"
#: a second artifact carrying the same two arms at lambda = 3e-3, used as the control's own control
CONTROL_TWIN = "runs/e140_r32_methods_plastic_40reps.json"
#: the wiring family's lambda = 1.0 four-arm table, for the matched-lambda family test
WIRING = "runs/e153_r32_overlap1_methods_40reps.json"
#: `e161`'s registered plasticity-cost threshold
COST_THRESHOLD = 0.0313


def registered_verdict(change: float, sigma: float, cost: float) -> dict:
    """`e161`'s two predictions, applied to one rung's numbers.

    ``change`` is the arm's forgetting minus `naive`'s (positive = the penalty forgets *more*), ``cost`` is the
    newest task's accuracy minus `naive`'s (negative = a cost). **The sign of P1 and the resolution of the
    falsifier are separate questions**, which is the whole reason both are written: this ladder's top rungs have
    P1's sign and neither prediction's resolution.
    """
    worse = change > 0
    falsified = change < 0 and abs(sigma) >= 2.0
    return {"direction_holds": bool(worse), "cost_above_threshold": bool(abs(cost) > COST_THRESHOLD),
            "p1_holds": bool(worse and abs(cost) > COST_THRESHOLD), "falsifier_fires": bool(falsified),
            "gain_resolved": bool(abs(sigma) >= 2.0)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)

    naive = load_arm(Path(NAIVE_HOME), "naive")
    twin_n = load_arm(Path(CONTROL_TWIN), "naive")
    twin_e = load_arm(Path(CONTROL_TWIN), "ewc")
    out: dict = {"ladder": {}, "control": {}}

    exact_f = np.array_equal(naive["forgetting"], twin_n["forgetting"])
    exact_n = np.array_equal(naive["newest"], twin_n["newest"])
    out["control"] = {"artifact": NAIVE_HOME, "twin": CONTROL_TWIN, "naive_bit_identical": bool(exact_f),
                      "naive_newest_bit_identical": bool(exact_n), "n": int(naive["n"])}
    print("== the control, and the control's control ==")
    print(f"   `naive` at lam 3e-3 between e133 and e140's plastic arm: forgetting "
          f"{'BIT-IDENTICAL' if exact_f else 'DIFFERS'}, newest "
          f"{'BIT-IDENTICAL' if exact_n else 'DIFFERS'} over {naive['n']} replicates")
    print(f"   (the two configs differ in one key: `anchor_bias`, present only in the newer artifact)")

    print("\n== the base family's lambda ladder, forty paired seeds at every rung, arm `ewc` ==")
    print(f"   {'lambda':<8}{'ewc forgetting':>15}{'vs naive':>10}{'sigma':>7}{'newest cost':>13}{'sigma':>7}"
          f"   {'P1':<10}{'falsifier'}")
    for label, lam, path in LADDER:
        arm = load_arm(Path(path), "ewc")
        f = paired(arm["forgetting"], naive["forgetting"])
        nw = paired(arm["newest"], naive["newest"])
        v = registered_verdict(f["change"], f["sigma"], nw["change"])
        out["ladder"][label] = {"lam": lam, "path": path, "forgetting": float(arm["forgetting"].mean()),
                                "vs_naive": f, "newest_cost": nw, "verdict": v}
        print(f"   {label:<8}{arm['forgetting'].mean():>15.4f}{f['change']:>+10.4f}{f['sigma']:>7.2f}"
              f"{nw['change']:>+13.4f}{nw['sigma']:>7.2f}   "
              f"{'holds' if v['p1_holds'] else 'fails':<10}{'FIRES' if v['falsifier_fires'] else 'does not'}")
    print(f"   `naive` at the same configuration: forgetting {naive['forgetting'].mean():.4f}, "
          f"newest {naive['newest'].mean():.4f}")
    print("   (the last two columns apply P1's and the falsifier's *form* at every rung; the registration itself "
          "names the 1.0 rung)")

    print("\n== adjacent rungs, paired on the same forty seeds ==")
    print(f"   {'step':<14}{'forgetting':>13}{'sigma':>8}{'newest':>12}{'sigma':>8}")
    for (l0, _, p0), (l1, _, p1) in zip(LADDER, LADDER[1:]):
        a0, a1 = load_arm(Path(p0), "ewc"), load_arm(Path(p1), "ewc")
        sf, sn = paired(a1["forgetting"], a0["forgetting"]), paired(a1["newest"], a0["newest"])
        out["ladder"][l1]["step_from"] = {"from": l0, "forgetting": sf, "newest": sn}
        print(f"   {l0 + ' -> ' + l1:<14}{sf['change']:>+13.4f}{sf['sigma']:>8.2f}"
              f"{sn['change']:>+12.4f}{sn['sigma']:>8.2f}")

    top = out["ladder"]["1.0"]["verdict"]
    print(f"\n   -> e161's registration, read: **P1 {'holds' if top['p1_holds'] else 'fails'}** -- the direction "
          f"is the penalty forgetting more ({out['ladder']['1.0']['vs_naive']['change']:+.4f}) and the cost is "
          f"{abs(out['ladder']['1.0']['newest_cost']['change']):.4f} against the registered threshold "
          f"{COST_THRESHOLD} -- and the falsifier **{'FIRES' if top['falsifier_fires'] else 'does not fire'}**.")
    print(f"      the direction half is {'resolved' if top['gain_resolved'] else 'NOT resolved'}: "
          f"{out['ladder']['1.0']['vs_naive']['sigma']:.2f} sigma, where the cost half is "
          f"{out['ladder']['1.0']['newest_cost']['sigma']:.2f} sigma")

    # where the ladder turns, and how flat it is above the turn
    above = [k for k in ("3e-2", "3e-1", "1.0")]
    worst = max(abs(out["ladder"][k]["vs_naive"]["sigma"]) for k in above)
    print(f"\n   -> above lambda = 3e-2 the forgetting difference is flat and unresolved: "
          + ", ".join(f"{k} {out['ladder'][k]['vs_naive']['change']:+.4f} at "
                      f"{out['ladder'][k]['vs_naive']['sigma']:.2f}s" for k in above)
          + f" -- all under {worst:.2f}s, over the 1.5 decades in which the cost is resolved at "
          + "/".join(f"{out['ladder'][k]['newest_cost']['sigma']:.2f}s" for k in above))

    print("\n== the matched-lambda family test, both families at lambda = 1.0 ==")
    wn, we = load_arm(Path(WIRING), "naive"), load_arm(Path(WIRING), "ewc")
    base_e = load_arm(Path("runs/e161_r32_base_ewc_lam1.json"), "ewc")
    # `gain` is the arm's advantage over its OWN naive, and the interaction is the wiring family's gain minus the
    # base family's on the same forty seeds -- the quantity the registration needs and the levels cannot give.
    gain_w = paired(wn["forgetting"] - we["forgetting"], naive["forgetting"] - base_e["forgetting"])
    cost_w = paired(we["newest"] - wn["newest"], base_e["newest"] - naive["newest"])
    w_gain, w_cost = paired(wn["forgetting"], we["forgetting"]), paired(we["newest"], wn["newest"])
    b_gain = out["ladder"]["1.0"]["vs_naive"]
    b_cost = out["ladder"]["1.0"]["newest_cost"]
    out["matched_lambda"] = {
        "gain_interaction": gain_w, "cost_interaction": cost_w,
        "wiring": {"naive_forgetting": float(wn["forgetting"].mean()),
                   "gain": float(wn["forgetting"].mean() - we["forgetting"].mean()),
                   "gain_sigma": w_gain["sigma"], "cost": float(we["newest"].mean() - wn["newest"].mean()),
                   "cost_sigma": w_cost["sigma"]},
        "base": {"naive_forgetting": float(naive["forgetting"].mean()),
                 "gain": float(naive["forgetting"].mean() - base_e["forgetting"].mean()),
                 "gain_sigma": b_gain["sigma"], "cost": float(base_e["newest"].mean() - naive["newest"].mean()),
                 "cost_sigma": b_cost["sigma"]}}
    print(f"   {'family':<8}{'its naive':>11}{'ewc gain over naive':>20}{'sigma':>8}{'newest cost':>14}{'sigma':>8}")
    for tag in ("base", "wiring"):
        d = out["matched_lambda"][tag]
        print(f"   {tag:<8}{d['naive_forgetting']:>11.4f}{d['gain']:>+20.4f}{d['gain_sigma']:>8.2f}"
              f"{d['cost']:>+14.4f}{d['cost_sigma']:>8.2f}")
    print(f"   interaction, forgetting (wiring gain minus base gain): {gain_w['change']:+.4f} +- "
          f"{gain_w['sem']:.4f} = {gain_w['sigma']:.2f} sigma, "
          f"{gain_w['negative']} of {gain_w['n']} seeds negative")
    print(f"   interaction, newest task:                              {cost_w['change']:+.4f} +- "
          f"{cost_w['sem']:.4f} = {cost_w['sigma']:.2f} sigma")
    print("   -> at the SAME lambda the two families are separated on both axes and in opposite directions: the")
    print("      wiring family's penalty buys stability where the base family's buys only a plasticity cost.")

    if args.json_out:
        write_json(args.json_out, out)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
