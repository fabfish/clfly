"""E442 -- the two parameters under two orders: whether the mechanism `e440` read on the card's world is the order's too.

`e440` read the corpus's own two parameters on the card's world -- the drift of the recurrent weights over the
baseline's and the final distance of the bias from zero over the baseline's -- and found the anchors holding the
recurrent weights to **0.6234** and **0.6188** of the baseline's against the corpus's pooled **0.718**, **0.751** and
**0.752**, with bias ratios **1.4483** and **1.4622** at the corpus's own **1.456** to **1.508**, and the buffer at
**0.9556** and **0.8531**. `e441` then put the anchor on that world under a **second order** and found its standing
there is the order's: **-0.0302** below the baseline as-built against **+0.0229** above it under `1,0,2`, with its
forgetting purchase nearly tripling from **-0.0474** to **-0.1240**. `e441` closed by naming the gap: *`e440`'s two
parameters were read at the as-built order only and could be read here.*

**This unit reads them.** No training and no probe: the two rolls of the card's world already on disk, `e438`'s as-built
and `e441`'s rotated, through the same two parameters and the same per-task split of the whole-body first-order
interference term into its weight and bias halves. Five claims, registered before either roll's parameters were read.

- **BT1 -- and the ledger is carried.** Both rolls carry `naive`, `replay` and `ewc-block` at **20** replicates each,
  every arm's replicates carrying `theta_drift`, `bias_norms` and an `interference` entry split into its weight and bias
  halves. **Falsifier**: any arm or field missing, or fewer replicates.
- **BT2 -- and the anchor holds the weights under the rotated order too.** Its drift over the baseline's under `1,0,2`
  is below **0.75**. **Falsifier**: at or above **0.95**; **null**: between.
- **BT3 -- and the buffer does not.** Under `1,0,2` the buffer's drift over the baseline's exceeds the anchor's.
  **Falsifier**: at or below it.
- **BT4 -- and the anchor holds them about as hard under both orders.** Its drift ratio under `1,0,2` is within **0.10**
  of its as-built **0.6234**. **Falsifier**: **0.20** or more apart; **null**: between. *This is the claim with the
  unit's question in it: `e441` measured the anchor's accuracy and forgetting moving with the order, and whether the
  parameter `e440` named moves with them is what says whether the two parameters carry the order's effect.*
- **BT5 -- and its interference still runs through the bias on every task it accounts for.** Under `1,0,2` the anchor's
  per-task share of the whole-body term carried by the bias half exceeds the baseline's on **both** tasks.
  **Falsifier**: at or below the baseline on any task.

**What it can do beyond that.** `e440`'s reading was that holding the recurrent weights is not what buys the retention,
because the arm that buys six times as much holds them to 0.956 while the arms that hold them to 0.62 buy almost none.
If the anchor's drift ratio under the rotated order is where it was as-built while its forgetting purchase has nearly
tripled, that reading is what the second order repeats: **the parameter `e440` named does not move when the thing it is
supposed to explain moves**, and the two parameters are the order's less than the accuracy is.

**What it cannot do.** *Two orders* of a three-task suite's six. *And one anchor*: `ewc-block-rand` is absent from the
rotated roll, so whether the matched-random arm's parameters move with the order is not measured. *And one cell*: the
card's world at twenty replicates, so the other five draws and the three streams are not in the reading. *And a
parameter is not a cause*: that the drift ratio is stable across the orders does not say the weights' movement is what
the accuracy's movement is not, and neither half of the split is a counterfactual.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the card's world under the as-built order and under `1,0,2`
ROLLS = {
    "asbuilt": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "rotated": Path("runs/e441_earned_label_anchor_order102_20reps.json"),
}
BASELINE = "naive"
BUFFER = "replay"
ANCHOR = "ewc-block"
ARMS = (BASELINE, ANCHOR, BUFFER)
DRIFT = "theta_drift"
SPLIT = "whole_body"
MIN_REPS = 20
SPLIT_TASKS = 2
HOLD = 0.75
HOLD_FIRES = 0.95
MOVES = 0.10
MOVES_FIRES = 0.20
#: the anchor's as-built drift ratio, which `e440` read and BT4 is registered against
AS_BUILT_DRIFT = 0.6234
CLAIMS = (
    ("BT1", f"and the ledger is carried, at {MIN_REPS} replicates on all three arms",
     "Both rolls carry naive, replay and ewc-block at twenty replicates each, every arm's replicates carrying "
     "theta_drift, bias_norms and an interference entry split into its weight and bias halves",
     "falsifier: any arm or field missing, or fewer replicates"),
    ("BT2", f"and the anchor holds the weights under the rotated order too, below {HOLD:.2f}",
     "Its drift over the baseline's under 1,0,2 is below 0.75",
     f"falsifier: at or above {HOLD_FIRES:.2f}; null: between"),
    ("BT3", "and the buffer does not",
     "Under 1,0,2 the buffer's drift over the baseline's exceeds the anchor's",
     "falsifier: at or below it"),
    ("BT4", f"and the anchor holds them about as hard under both orders, within {MOVES:.2f}",
     f"Its drift ratio under 1,0,2 is within 0.10 of its as-built {AS_BUILT_DRIFT:.4f}",
     f"falsifier: {MOVES_FIRES:.2f} or more apart; null: between"),
    ("BT5", "and its interference still runs through the bias on every task it accounts for",
     "Under 1,0,2 the anchor's per-task share of the whole-body term carried by the bias half exceeds the baseline's on "
     "both tasks",
     "falsifier: at or below the baseline on any task"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _arm(methods: dict, arm: str) -> dict | None:
    got = methods.get(arm) or {}
    reps = got.get("replicates") or []
    if not reps or DRIFT not in reps[0] or "interference" not in reps[0] or "bias_norms" not in reps[0]:
        return None
    drift = statistics.fmean([statistics.fmean(r[DRIFT]) for r in reps])
    bias = statistics.fmean([r["bias_norms"][-1]["from_zero"] for r in reps])
    tasks = len(reps[0]["interference"])
    theta_only, bias_only, whole = [], [], []
    for j in range(tasks):
        body = [r["interference"][j][SPLIT] for r in reps]
        theta_only.append(statistics.fmean([b["theta_only_cumulative"] for b in body]))
        bias_only.append(statistics.fmean([b["bias_only_cumulative"] for b in body]))
        whole.append(statistics.fmean([b["cumulative"] for b in body]))
    share = [abs(bias_only[j]) / abs(whole[j]) if whole[j] else None for j in range(tasks)]
    return {"replicates": len(reps), "drift": drift, "bias": bias, "tasks": tasks,
            "theta_only": theta_only, "bias_only": bias_only, "whole": whole, "share": share}


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in sorted(methods):
        got = _arm(methods, arm)
        if got is None:
            return None
        arms[arm] = got
    cfg = doc.get("config") or {}
    return {"artifact": path.name, "arms": arms, "task_order": cfg.get("task_order"),
            "task_names": [t.get("name") if isinstance(t, dict) else t for t in (doc.get("tasks") or [])]}


def reading(rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "rolls": {}, "cells": [], "shares": {}, "spans": {}}
    for label, path in rolls.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries an arm without the fields"}
        out["rolls"][label] = got
    for label, roll in out["rolls"].items():
        for arm in ARMS:
            if arm not in roll["arms"]:
                return {**out, "ok": False, "reason": f"roll {label} carries no {arm} arm"}
        base = roll["arms"][BASELINE]
        for arm in (ANCHOR, BUFFER):
            got = roll["arms"][arm]
            cell = {"roll": label, "arm": arm, "replicates": got["replicates"],
                    "drift_ratio": got["drift"] / base["drift"], "bias_ratio": got["bias"] / base["bias"],
                    "share": got["share"], "base_share": base["share"],
                    "share_above": [None if got["share"][j] is None or base["share"][j] is None
                                    else got["share"][j] > base["share"][j] for j in range(len(got["share"]))]}
            cell["held"] = cell["drift_ratio"] < 1.0
            cell["pushed"] = cell["bias_ratio"] > 1.0
            out["cells"].append(cell)
    for label, roll in out["rolls"].items():
        base = roll["arms"][BASELINE]
        out["shares"][label] = {"base": base["share"],
                                **{arm: roll["arms"][arm]["share"] for arm in ARMS if arm != BASELINE}}
    by = {(c["roll"], c["arm"]): c for c in out["cells"]}
    a_as, a_ro = by[("asbuilt", ANCHOR)], by[("rotated", ANCHOR)]
    b_as, b_ro = by[("asbuilt", BUFFER)], by[("rotated", BUFFER)]
    out["spans"] = {"rolls": sorted(out["rolls"]), "cells": len(out["cells"]),
                    "replicates": sorted({c["replicates"] for c in out["cells"]}),
                    "orders": {label: roll["task_order"] for label, roll in out["rolls"].items()},
                    "anchor_drift": {"asbuilt": a_as["drift_ratio"], "rotated": a_ro["drift_ratio"],
                                     "move": a_ro["drift_ratio"] - a_as["drift_ratio"]},
                    "anchor_bias": {"asbuilt": a_as["bias_ratio"], "rotated": a_ro["bias_ratio"],
                                    "move": a_ro["bias_ratio"] - a_as["bias_ratio"]},
                    "buffer_drift": {"asbuilt": b_as["drift_ratio"], "rotated": b_ro["drift_ratio"]},
                    "buffer_bias": {"asbuilt": b_as["bias_ratio"], "rotated": b_ro["bias_ratio"]},
                    "tasks": SPLIT_TASKS}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no such arm"}
                for c in CLAIMS]
    thin = {f"{c['roll']}.{c['arm']}": c["replicates"] for c in r["cells"] if c["replicates"] < MIN_REPS}
    j1 = {"id": "BT1",
          "measured": f"{r['spans']['cells']} cells over {len(r['spans']['rolls'])} rolls at "
                      f"{r['spans']['replicates']} replicates, the orders {r['spans']['orders']}, every arm carrying "
                      f"the drift, the bias and the split",
          "verdict": "MET -- both rolls carry the baseline, the buffer and the anchor with all three fields" if
                     (not thin and r["spans"]["cells"] == 2 * len(r["rolls"])) else
                     f"FALSIFIER FIRED -- thin {thin}, cells {r['spans']['cells']}"}
    d_ro = r["spans"]["anchor_drift"]["rotated"]
    j2 = {"id": "BT2",
          "measured": f"the anchor's drift over the baseline's under `1,0,2` is {d_ro:.4f}, against the buffer's "
                      f"{r['spans']['buffer_drift']['rotated']:.4f}",
          "verdict": f"MET -- the anchor holds the weights under this order too, {d_ro:.4f}" if d_ro < HOLD else
                     f"FALSIFIER FIRED -- {d_ro:.4f} at or above {HOLD_FIRES:.2f}" if d_ro >= HOLD_FIRES else
                     f"NULL -- {d_ro:.4f} between {HOLD:.2f} and {HOLD_FIRES:.2f}"}
    b_ro = r["spans"]["buffer_drift"]["rotated"]
    j3 = {"id": "BT3",
          "measured": f"under `1,0,2` the buffer's drift ratio is {b_ro:.4f} against the anchor's {d_ro:.4f}",
          "verdict": f"MET -- the buffer moves the weights more than the anchor by {b_ro - d_ro:+.4f}" if b_ro > d_ro
                     else "FALSIFIER FIRED -- the buffer is not above the anchor"}
    move = abs(r["spans"]["anchor_drift"]["move"])
    j4 = {"id": "BT4",
          "measured": f"the anchor's drift ratio is {d_ro:.4f} under `1,0,2` and "
                      f"{r['spans']['anchor_drift']['asbuilt']:.4f} as-built, {move:.4f} apart",
          "verdict": f"MET -- the anchor holds them about as hard under both orders, {move:.4f} apart" if move <= MOVES
                     else f"FALSIFIER FIRED -- the move is {move:.4f}" if move >= MOVES_FIRES else
                     f"NULL -- the move is {move:.4f}, between {MOVES:.2f} and {MOVES_FIRES:.2f}"}
    anchor_cell = next(c for c in r["cells"] if c["roll"] == "rotated" and c["arm"] == ANCHOR)
    below = [j for j, ok in enumerate(anchor_cell["share_above"]) if not ok]
    shares = [None if s is None else round(s, 4) for s in anchor_cell["share"]]
    base_shares = [None if s is None else round(s, 4) for s in anchor_cell["base_share"]]
    j5 = {"id": "BT5",
          "measured": f"under `1,0,2` the anchor's per-task bias shares are {shares} against the baseline's "
                      f"{base_shares}",
          "verdict": "MET -- the anchor's interference runs through the bias more than the baseline's on every task it "
                     "accounts for" if not below else f"FALSIFIER FIRED -- at or below the baseline on {below}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the two parameters under two orders ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the card's world at `cue@0` with the action source and the earned label, as-built and `1,0,2`")
    print(f"\n   {'roll':>9} {'order':>9} {'arm':>12} {'drift ratio':>12} {'bias ratio':>11} {'held':>6} {'pushed':>7}")
    for c in r["cells"]:
        print(f"   {c['roll']:>9} {str(r['spans']['orders'][c['roll']]):>9} {c['arm']:>12} {c['drift_ratio']:12.4f} "
              f"{c['bias_ratio']:11.4f} {str(c['held']):>6} {str(c['pushed']):>7}")
    print("\n   the corpus's pooled pattern (e433) was drift 0.718/0.751/0.752 and bias 1.508/1.473/1.456 for the")
    print("   penalties against 0.984 and 0.946 for the buffer")
    print("\n   the per-task share of the whole-body interference term carried by the bias half:")
    for label, shares in r["shares"].items():
        for arm, vals in shares.items():
            print(f"      {label:>9} {arm:>12}: " + " ".join("None" if v is None else f"{v:.4f}" for v in vals))
    print("\n   and the ledger e441 read on these same two rolls, for the comparison:")
    print("      the anchor over the baseline on the mean diagonal is -0.0302 as-built and +0.0229 under `1,0,2`,")
    print("      its forgetting purchase -0.0474 at 2.77 sigma against -0.1240 at 4.54 sigma")
    print("\n== the registered claims, BT1-BT5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e441` moved the anchor to a second order and found its standing there is the order's; this asks the")
    print("    two parameters `e440` named of the same two rolls, which e441 named as what it could not read)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
