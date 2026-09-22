"""E63 -- the predictor's "one failure" is an unresolved observation, and the rewired condition is untested.

The predictor is one of the project's two headline positive results: rank correlations of +0.97 to
+0.99 and **13 of 13** correct on the matched pairs that clear resolution, out of 25 pairs across five
out-of-sample conditions (`e6_predictor_6`, six seeds). The plan also names its *one failure* -- "on
heavily rewired wiring the biological-vs-random sign is called wrongly with a large margin".

This script reads the per-pair sigma that the artifact stores alongside each call, and asks what the
failure actually is:

* how many pairs are **resolvable** in each condition, and how many of those are called correctly;
* what sigma the disagreeing call has, and what it would take to resolve it;
* and what the "rewired" condition's 0-of-5 resolvability means for the scope of the claim.

    python -m experiments.e63_predictor_failure_is_unresolved
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load(path: str):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--big", default="runs/e6_predictor_6.json")
    ap.add_argument("--small", default="runs/e6_predictor.json")
    ap.add_argument("--json-out", default="runs/e63_predictor_resolvability.json")
    args = ap.parse_args()

    big, small = load(args.big), load(args.small)
    if big is None:
        print(f"{args.big} absent; nothing to do")
        return

    out: dict = {"conditions": [], "source": args.big}

    print("=" * 100)
    print("1. EVERY PAIR'S SIGMA, AND WHAT THE PREDICTOR ACTUALLY GOT RIGHT")
    print("=" * 100)
    print("   a `resolvable` pair is one whose excess difference clears its own seed resolution; the")
    print("   predictor's score should be quoted on those, because a sub-resolution call is a coin")
    print("   flip however the predictor got there.\n")
    n_res = n_res_ok = n_all = 0
    for c in big["conditions"]:
        label = c["condition"]["label"]
        rows = c["pairs"]
        res = [p for p in rows if p.get("resolvable")]
        ok = [p for p in res if p.get("sign_ok")]
        n_all += len(rows)
        n_res += len(res)
        n_res_ok += len(ok)
        print(f"   {label:<16} d={c['d']:<6} n_seeds={c['n_seeds']}  "
              f"resolvable {len(res)}/{len(rows)}, correct {len(ok)}/{len(res)}"
              if res else
              f"   {label:<16} d={c['d']:<6} n_seeds={c['n_seeds']}  "
              f"resolvable 0/{len(rows)}  <- NOTHING IN THIS CONDITION RESOLVES")
        print("      " + "  ".join(
            f"{p['rung']}={p['sigma']:.2f}sigma{'ok' if p['sign_ok'] else 'BAD'}" for p in rows))
        out["conditions"].append({
            "label": label, "d": c["d"], "n_seeds": c["n_seeds"],
            "n_pairs": len(rows), "n_resolvable": len(res), "n_resolvable_correct": len(ok),
            "pairs": [{"rung": p["rung"], "excess_delta": p.get("excess_delta"),
                       "pressure_delta": p.get("pressure_delta"), "sigma": p.get("sigma"),
                       "resolvable": bool(p.get("resolvable")), "sign_ok": bool(p["sign_ok"])}
                      for p in rows]})
    print(f"\n   over all conditions: **{n_res} of {n_all} pairs resolvable, {n_res_ok} of {n_res} "
          f"of those called correctly**.")
    print(f"   The headline '24 of 25 correct' counts the twelve sub-resolution calls as evidence.")
    out["totals"] = {"n_pairs": n_all, "n_resolvable": n_res, "n_resolvable_correct": n_res_ok}

    print()
    print("=" * 100)
    print("2. THE 'ONE FAILURE', WHICH IS THE LARGEST SIGMA IN A CONDITION WHERE NOTHING RESOLVES")
    print("=" * 100)
    for c in out["conditions"]:
        bad = [p for p in c["pairs"] if not p["sign_ok"]]
        if not bad:
            continue
        print(f"   {c['label']} (d = {c['d']}, n_seeds = {c['n_seeds']}), the disagreeing pair(s):")
        for p in bad:
            sig = p["sigma"]
            need = c["n_seeds"] * (3.0 / sig) ** 2 if sig else float("inf")
            print(f"     {p['rung']:<20} excess delta {p['excess_delta']:+.6f}"
                  f"  at {sig:.2f}sigma  (pressure delta {p['pressure_delta']:+.3f})")
            print(f"        resolvable: {p['resolvable']}   sigmas in this condition: "
                  + ", ".join(f"{q['sigma']:.2f}" for q in c["pairs"]))
            print(f"        to reach 3 sigma on the SEED component alone would need ~{need:.0f} seeds")
        print()
    print("   So the failure is not 'called wrongly with a large margin'. It is a confident")
    print("   *prediction* meeting an unresolved *observation*: the largest sigma of five, in a")
    print("   condition where the other four are 0.06-0.75 sigma.")

    print()
    print("=" * 100)
    print("3. AND THE REWIRED CONDITION IS UNTESTED, NOT FAILED")
    print("=" * 100)
    for c in out["conditions"]:
        if c["n_resolvable"] == 0:
            print(f"   {c['label']}: 0 of {c['n_pairs']} pairs resolve at {c['n_seeds']} seeds.")
            print("   So the predictor has NOT been tested on this topology and cannot be said to")
            print("   fail there -- the plan's condition list should say 'untested' where it")
            print("   currently implies an out-of-sample success or failure.")
    print("\n   The resolution requirement scales as 1/sqrt(n), so the `cell_class` pair above")
    print("   (~18 seeds) and this condition more generally are affordable but not free; a larger")
    print("   task suite would raise the signal instead, which is the other half of the same ratio.")

    print()
    print("=" * 100)
    print("4. WHAT DOES NOT CHANGE")
    print("=" * 100)
    print("   13 of 13 correct on the resolvable pairs is a real result and the strongest positive")
    print("   evidence in the project, with rank correlations of +0.97 to +0.99 on the full 25. The")
    print("   refinement above narrows *where* it is evidenced, not whether. And the e57 discipline")
    print("   applies here too: the pairs' deltas are stored as means over six seeds, so the")
    print("   per-seed structure of this score -- like the C2 ladder's, before `e58` -- is not checked.")

    Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
