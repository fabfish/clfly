"""E440 -- where the anchors' movement goes on the card's world: the two parameters, and the interference split, read on the one world where the anchors are not buffers.

`e438` and `e439` found that on the card's world **neither anchoring is a buffer**: `ewc-block` and `ewc-block-rand` read
**-0.0302** and **-0.0365** below `naive` on the mean diagonal while buying **-0.0474** and **-0.0229** of forgetting
back, where `replay` reads **+0.1594** ahead with **-0.2844** less forgetting. Both units closed on the same sentence:
*an arm is not a mechanism*, and named `e432`'s split of interference into its weight and bias halves -- and `e433`'s two
parameters -- as the instruments that had not been asked of this world.

**This unit asks them.** No training and no probe: it reads the two three-arm rolls already on disk, `e438`'s and
`e439`'s, through the corpus's own two parameters -- the drift of the recurrent weights over the baseline's, and the
final distance of the bias from zero over the baseline's -- and through `e432`'s per-task split of the whole-body
first-order interference term into its weight and bias halves.

**Registration, stated as `e276` stated his.** The two parameters in section 1 were **inspected while this module was
written**, because the question was whether this world sits inside or outside the corpus's pooled pattern (`e433`: drift
ratios **0.718**, **0.751**, **0.752** and bias ratios **1.508**, **1.473**, **1.456** for the three penalties, against
**0.984** and **0.946** for the buffer). **BR2 and BR3 are therefore confirmatory**, and the only thing they can fail is
a transcription. **The interference split in BR4 and BR5 was not computed before they were registered**, and it is the
half of this unit that can surprise.

- **BR1 -- and the ledger is carried.** Both rolls carry `naive`, `replay` and their anchor at **20** replicates each,
  and every arm's replicates carry `theta_drift`, `bias_from_zero` and an `interference` entry whose whole-body term is
  split into its weight and bias halves. **Falsifier**: any arm or field missing, or fewer replicates.
- **BR2 -- and the anchors hold the weights on this world too.** Each anchor's mean drift over the baseline's is below
  **0.75**. **Falsifier**: at or above **0.95**; **null**: between.
- **BR3 -- and they push the bias.** Each anchor's final bias distance over the baseline's is above **1.40**.
  **Falsifier**: at or below **1.10**; **null**: between.
- **BR4 -- and their interference runs through the bias more than the baseline's, on every task.** Each anchor's
  per-task share of the whole-body term carried by the bias half exceeds the baseline's on **all three** tasks.
  **Falsifier**: any anchor at or below the baseline on any task.
- **BR5 -- and the buffer's does not.** `replay`'s per-task bias share is at or below the baseline's on **all three**
  tasks. **Falsifier**: above the baseline on any task.

**What it can do beyond that.** It separates the two things `e438` and `e439` measured. If the anchors hold the weights
as hard as the corpus's typical penalty cell while `replay` barely holds them and forgets far less, then *holding the
weights* is not what buys the retention on this world -- the arm that stores is the arm that disturbs the parameters
least -- and the anchors' price is the price of a parameter they hold for nothing.

**What it cannot do.** *Two cells*: one world, one order, so this is the corpus's pattern read at two cells and not a
distribution. *And one draw*: the partition is a draw of the same group sizes. *And a parameter is not a cause*: that the
anchors hold the weights while their accuracy falls does not say the holding causes the fall, and neither half of the
split is a counterfactual. *And the split is one implementation's*: `e432`'s first-order term is the runner's own
account of interference and not an independent measurement of it.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the two rolls of the card's world carrying an anchor beside the baseline and the buffer
ROLLS = {
    "penalty": Path("runs/e438_earned_label_three_arms_20reps.json"),
    "rand": Path("runs/e439_earned_label_rand_20reps.json"),
}
BASELINE = "naive"
BUFFER = "replay"
ANCHORS = {"penalty": "ewc-block", "rand": "ewc-block-rand"}
DRIFT = "theta_drift"
BIAS = "bias_from_zero"
SPLIT = "whole_body"
MIN_REPS = 20
#: the interference account is indexed by the task a later task interferes with, so it carries T-1 entries
SPLIT_TASKS = 2
GEN = 0.75
GEN_FIRES = 0.95
PUSH = 1.40
PUSH_FLOOR = 1.10
CLAIMS = (
    ("BR1", f"and the ledger is carried, at {MIN_REPS} replicates",
     "Both rolls carry naive, replay and their anchor at twenty replicates each, every arm's replicates carrying "
     "theta_drift, bias_from_zero and an interference entry split into its weight and bias halves",
     "falsifier: any arm or field missing, or fewer replicates"),
    ("BR2", f"and the anchors hold the weights on this world too, below {GEN:.2f}",
     "Each anchor's mean drift over the baseline's is below 0.75",
     f"falsifier: at or above {GEN_FIRES:.2f}; null: between"),
    ("BR3", f"and they push the bias, above {PUSH:.2f}",
     "Each anchor's final bias distance over the baseline's is above 1.40",
     f"falsifier: at or below {PUSH_FLOOR:.2f}; null: between"),
    ("BR4", "and their interference runs through the bias more than the baseline's, on every task it accounts for",
     "Each anchor's per-task share of the whole-body term carried by the bias half exceeds the baseline's on both "
     "tasks",
     "falsifier: any anchor at or below the baseline on any task"),
    ("BR5", "and the buffer's does not",
     "replay's per-task bias share is at or below the baseline's on both tasks",
     "falsifier: above the baseline on any task"),
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
    return {"artifact": path.name, "arms": arms, "task_names": [t.get("name") if isinstance(t, dict) else t
                                                               for t in (doc.get("tasks") or [])]}


def reading(rolls: dict = ROLLS) -> dict:
    out = {"ok": True, "reason": None, "rolls": {}, "cells": [], "by_arm": {}, "shares": {}, "spans": {}}
    for label, path in rolls.items():
        got = _roll(path)
        if got is None:
            return {**out, "ok": False, "reason": f"roll {label}: {path} is absent or carries an arm without the fields"}
        out["rolls"][label] = got
    for label, roll in out["rolls"].items():
        base = roll["arms"].get(BASELINE)
        if base is None:
            return {**out, "ok": False, "reason": f"roll {label} carries no {BASELINE} arm"}
        anchor = ANCHORS[label]
        if anchor not in roll["arms"]:
            return {**out, "ok": False, "reason": f"roll {label} carries no {anchor} arm"}
        for arm in (anchor, BUFFER):
            if arm not in roll["arms"]:
                return {**out, "ok": False, "reason": f"roll {label} carries no {arm} arm"}
            got = roll["arms"][arm]
            cell = {"roll": label, "arm": arm, "anchor": arm == anchor, "replicates": got["replicates"],
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
                                **{arm: roll["arms"][arm]["share"] for arm in sorted(roll["arms"]) if arm != BASELINE}}
    for arm in sorted({c["arm"] for c in out["cells"]}):
        sub = [c for c in out["cells"] if c["arm"] == arm]
        out["by_arm"][arm] = {"cells": len(sub),
                              "mean_drift_ratio": statistics.fmean([c["drift_ratio"] for c in sub]),
                              "mean_bias_ratio": statistics.fmean([c["bias_ratio"] for c in sub]),
                              "held": sum(1 for c in sub if c["held"]),
                              "pushed": sum(1 for c in sub if c["pushed"]),
                              "both": sum(1 for c in sub if c["held"] and c["pushed"])}
    out["spans"] = {"cells": len(out["cells"]), "rolls": len(out["rolls"]),
                    "replicates": sorted({c["replicates"] for c in out["cells"]}),
                    "anchors": sorted(ANCHORS.values()), "tasks": SPLIT_TASKS}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no such arm"}
                for c in CLAIMS]
    thin = {f"{c['roll']}.{c['arm']}": c["replicates"] for c in r["cells"] if c["replicates"] < MIN_REPS}
    j1 = {"id": "BR1",
          "measured": f"{r['spans']['cells']} cells over {r['spans']['rolls']} rolls at "
                      f"{r['spans']['replicates']} replicates, every arm carrying the drift, the bias and the split",
          "verdict": "MET -- both rolls carry the baseline, the buffer and their anchor with all three fields" if
                     (not thin and r["spans"]["cells"] == 2 * len(r["rolls"])) else
                     f"FALSIFIER FIRED -- thin {thin}, cells {r['spans']['cells']}"}
    anchors = [c for c in r["cells"] if c["anchor"]]
    over = {f"{c['roll']}.{c['arm']}": round(c["drift_ratio"], 4) for c in anchors}
    high = {k: v for k, v in over.items() if v >= GEN_FIRES}
    j2 = {"id": "BR2",
          "measured": f"the anchors' drift over the baseline's is {over}",
          "verdict": f"MET -- every anchor holds the weights, the loosest {max(over.values()):.4f}" if
                     all(v < GEN for v in over.values()) else
                     f"FALSIFIER FIRED -- {high} at or above {GEN_FIRES:.2f}" if high else
                     f"NULL -- {over} between {GEN:.2f} and {GEN_FIRES:.2f}"}
    pushes = {f"{c['roll']}.{c['arm']}": round(c["bias_ratio"], 4) for c in anchors}
    low = {k: v for k, v in pushes.items() if v <= PUSH_FLOOR}
    j3 = {"id": "BR3",
          "measured": f"the anchors' final bias distance over the baseline's is {pushes}",
          "verdict": f"MET -- every anchor pushes the bias, the weakest {min(pushes.values()):.4f}" if
                     all(v > PUSH for v in pushes.values()) else
                     f"FALSIFIER FIRED -- {low} at or below {PUSH_FLOOR:.2f}" if low else
                     f"NULL -- {pushes} between {PUSH_FLOOR:.2f} and {PUSH:.2f}"}
    below = {f"{c['roll']}.{c['arm']}": [j for j, ok in enumerate(c["share_above"]) if not ok] for c in anchors}
    below = {k: v for k, v in below.items() if v}
    shares = {f"{c['roll']}.{c['arm']}": [None if s is None else round(s, 4) for s in c["share"]] for c in anchors}
    base_shares = {c["roll"]: [None if s is None else round(s, 4) for s in c["base_share"]] for c in anchors}
    j4 = {"id": "BR4",
          "measured": f"the anchors' per-task bias shares are {shares} against the baseline's {base_shares}",
          "verdict": "MET -- both anchors' interference runs through the bias more than the baseline's on every task it "
                     "accounts for" if not below else f"FALSIFIER FIRED -- at or below the baseline on {below}"}
    buffers = [c for c in r["cells"] if not c["anchor"]]
    above = {f"{c['roll']}.{c['arm']}": [j for j, ok in enumerate(c["share_above"]) if ok] for c in buffers}
    above = {k: v for k, v in above.items() if v}
    buffer_shares = {f"{c['roll']}.{c['arm']}": [None if s is None else round(s, 4) for s in c["share"]]
                     for c in buffers}
    j5 = {"id": "BR5",
          "measured": f"the buffer's per-task bias shares are {buffer_shares}, against the baseline's {base_shares}",
          "verdict": "MET -- the buffer's bias share is at or below the baseline's on both tasks" if not above
                     else f"FALSIFIER FIRED -- above the baseline on {above}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== where the anchors' movement goes on the card's world ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the two three-arm rolls of the card's world, read through e433's two parameters and e432's split")
    print(f"\n   {'roll':>9} {'arm':>16} {'drift ratio':>12} {'bias ratio':>11} {'held':>6} {'pushed':>7}")
    for c in r["cells"]:
        print(f"   {c['roll']:>9} {c['arm']:>16} {c['drift_ratio']:12.4f} {c['bias_ratio']:11.4f} "
              f"{str(c['held']):>6} {str(c['pushed']):>7}")
    print("\n   the corpus's pooled pattern (e433) was drift 0.718/0.751/0.752 and bias 1.508/1.473/1.456 for the")
    print("   penalties against 0.984 and 0.946 for the buffer")
    print("\n   the per-task share of the whole-body interference term carried by the bias half:")
    for label, shares in r["shares"].items():
        for arm, vals in shares.items():
            print(f"      {label:>8} {arm:>16}: " + " ".join("None" if v is None else f"{v:.4f}" for v in vals))
    print("\n== the registered claims, BR1-BR5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e438` and `e439` both closed on `an arm is not a mechanism`; this asks the corpus's own two")
    print("    instruments of that world, and BR4 and BR5 are the half registered before it was computed)")
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
