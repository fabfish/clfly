"""E432 -- the interference runs through the bias for the arms that are penalised and through the weights for the arm that is not.

Every arm's artifact carries the corpus's own one-line interference account per task: the gradient of a task's loss at
the final body against the displacement that task experienced, split into the half taken over the recurrent weights and
the half taken over the bias (`e139` built the split after finding the weight-only form reads one channel and the
effect lives mostly in the other). `e427`, `e430` and `e431` found the bias carrying three quarters of the buffer's
worth and the penalties pushing it out furthest; this reads the corpus's own instrument on that split.

**This unit reads three rolls.** The card's world with `naive`, `ewc-block` and `replay` in one run at twenty
replicates; the plastic/frozen-bias pair at forty, whose frozen side is the control that makes every bias displacement
zero. Per arm and per task: the two halves of the first-order term, their shares, and the whole-body total. No training,
no probe. Five claims, registered before this unit's pass over the runs.

- **BH1 -- and the ledger is carried.** The three-arm run at **20** replicates and the pair at **40**, each arm
  carrying a per-task first-order term split into its weight and bias halves. **Falsifier**: any arm or entry missing,
  or fewer replicates.
- **BH2 -- and the control's own reading is zero.** With the bias frozen, the bias half is **exactly 0.0000** on every
  arm and every task at forty replicates, while the weight half is not zero. **Falsifier**: any non-zero bias half on
  the frozen side, or an all-zero weight half.
- **BH3 -- and every penalty's interference runs mostly through the bias.** On both runs, on both tasks, each penalty
  arm's bias share of the whole-body term is above the **naive** arm's. **Falsifier**: any penalty arm at or below the
  baseline on either task. *This is the unit's own prediction: an arm that regularises toward a basis should be read by
  the instrument through the parameter `e431` found it displacing.*
- **BH4 -- and the diagonal penalty's is above nine tenths.** On the plastic pair the `ewc` arm's bias share is at
  least **0.9** on both tasks. **Falsifier**: below **0.8**; **null**: between.
- **BH5 -- and the buffer's whole term is below the baseline's.** `replay`'s whole-body first-order term is below the
  `naive` arm's on every task of all three rolls -- six comparisons. **Falsifier**: any task where it is not.

**What it can do beyond that.** It reads the corpus's own instrument on the parameter the last three units converged
on. On the card's world the penalty's bias share is **0.76** and **0.90** where the arm that does nothing is at **0.40**
and **0.49**; on the plastic pair the diagonal penalty's is **0.98** and **0.92**. So the answer to *which channel the
forgetting runs through* is the arm's: the penalties' interference is mostly bias, the unpenalised arm's is mostly
weights, and the buffer's whole term is below the baseline's on every task of all three rolls.

**What it cannot do.** *Three rolls and one instrument*: the account is the corpus's own first-order form (`e109` found
its second-order term non-monotone and `e336` found the update direction not reproducible at five replicates), so a
share here is a share of that one-line reading and not of the forgetting itself. *And a frozen bias zeroes one channel
by construction*: BH2 is the control validating the split and not a measurement. *And the buffer's own share is
noise*: its two halves are of comparable size -- 0.43 and 0.41 on the card's world, 0.59 and 0.74 on the plastic pair
-- but three orders of magnitude below the baseline's on the pair, so the share of a tiny term is not a reading, which
is why no claim is made about it. *And the metric is the corpus's*: `mean_forgetting` is the diagonal minus
the last row, which `e305` showed cannot see the part an arm never learned.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the three-arm cell `e415`, `e423` and `e430` read, and the plastic/frozen-bias pair `e427` read
CELL = Path("runs/e356_earned_label_r32_20reps.json")
PAIR = (Path("runs/e140_r32_methods_frozenbias_40reps.json"), Path("runs/e140_r32_methods_plastic_40reps.json"))
BASELINE = "naive"
BUFFER = "replay"
PENALTIES = ("ewc", "ewc-block", "ewc-block-rand")
MIN_REPS = 20
PAIR_REPS = 40
ZERO = 1e-6
DIAGONAL = "ewc"
DIAGONAL_SHARE = 0.90
DIAGONAL_FIRES = 0.80
CLAIMS = (
    ("BH1", f"and the ledger is carried, at {MIN_REPS} and {PAIR_REPS} replicates",
     "The three-arm run at twenty replicates and the pair at forty, each arm carrying a per-task first-order term "
     "split into its weight and bias halves",
     "falsifier: any arm or entry missing, or fewer replicates"),
    ("BH2", "and the control's own reading is zero",
     "With the bias frozen the bias half is exactly 0.0000 on every arm and every task at forty replicates, while the "
     "weight half is not zero",
     "falsifier: any non-zero bias half on the frozen side, or an all-zero weight half"),
    ("BH3", "and every penalty's interference runs mostly through the bias",
     "On both runs and both tasks each penalty arm's bias share of the whole-body term is above the naive arm's",
     "falsifier: any penalty arm at or below the baseline on either task"),
    ("BH4", f"and the diagonal penalty's is above {DIAGONAL_SHARE:.1f}",
     "On the plastic pair the ewc arm's bias share is at least 0.9 on both tasks",
     f"falsifier: below {DIAGONAL_FIRES:.1f}; null: between"),
    ("BH5", "and the buffer's whole term is below the baseline's",
     "replay's whole-body first-order term is below the naive arm's on every task of all three rolls",
     "falsifier: any task where it is not"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _roll(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    methods = doc.get("methods") or {}
    arms = {}
    for arm in sorted(methods):
        reps = (methods.get(arm) or {}).get("replicates") or []
        if not reps or "interference" not in reps[0]:
            continue
        tasks = len(reps[0]["interference"])
        theta, bias, whole = [], [], []
        for j in range(tasks):
            body = [r["interference"][j]["whole_body"] for r in reps]
            theta.append(statistics.fmean([b["theta_only_cumulative"] for b in body]))
            bias.append(statistics.fmean([b["bias_only_cumulative"] for b in body]))
            whole.append(statistics.fmean([b["cumulative"] for b in body]))
        arms[arm] = {"replicates": len(reps), "tasks": tasks, "theta": theta, "bias": bias, "whole": whole,
                     "share": [abs(bias[j]) / abs(whole[j]) if whole[j] else None for j in range(tasks)]}
    return arms or None


def reading(cell: Path = CELL, pair=PAIR) -> dict:
    out = {"ok": True, "reason": None, "rolls": {}}
    for label, path in [("cell", cell)] + [(f"pair/{lbl}", p) for lbl, p in zip(("frozen", "plastic"), pair)]:
        got = _roll(path)
        if not got:
            return {**out, "ok": False, "reason": f"{path} is absent or carries no interference record"}
        out["rolls"][label] = {"artifact": path.name, "arms": got}
    missing = [k for k, v in out["rolls"].items()
               if any(a not in v["arms"] for a in (BASELINE, BUFFER))]
    if missing:
        return {**out, "ok": False, "reason": f"a roll carries no baseline or buffer arm: {missing}"}
    frozen = out["rolls"]["pair/frozen"]["arms"]
    plastic = out["rolls"]["pair/plastic"]["arms"]
    out["spans"] = {"rolls": len(out["rolls"]),
                    "replicates": sorted({v["replicates"] for r in out["rolls"].values()
                                          for v in r["arms"].values()}),
                    "frozen_bias_max": max((abs(x) for a in frozen for x in frozen[a]["bias"]), default=None),
                    "frozen_theta_max": max((abs(x) for a in frozen for x in frozen[a]["theta"]), default=None),
                    "diagonal_shares": [round(v, 4) for v in (plastic[DIAGONAL]["share"]
                                                              if DIAGONAL in plastic else [])],
                    "shares": {lbl: {a: [None if s is None else round(s, 4) for s in v["share"]]
                                     for a, v in roll["arms"].items()}
                               for lbl, roll in out["rolls"].items()},
                    "buffer_below_baseline": sum(
                        1 for roll in out["rolls"].values()
                        for j in range(roll["arms"][BUFFER]["tasks"])
                        if abs(roll["arms"][BUFFER]["whole"][j]) < abs(roll["arms"][BASELINE]["whole"][j])),
                    "comparisons": sum(roll["arms"][BUFFER]["tasks"] for roll in out["rolls"].values())}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a roll is absent or carries no interference record"}
                for c in CLAIMS]
    rolls, s = r["rolls"], r["spans"]
    thin = {lbl: {a: v["replicates"] for a, v in roll["arms"].items() if v["replicates"] < MIN_REPS}
            for lbl, roll in rolls.items()}
    thin = {k: v for k, v in thin.items() if v}
    pair_thin = {a: v["replicates"] for lbl in ("pair/frozen", "pair/plastic")
                 for a, v in rolls[lbl]["arms"].items() if v["replicates"] < PAIR_REPS}
    j1 = {"id": "BH1",
          "measured": f"{s['rolls']} rolls at {s['replicates']} replicates, each arm with a per-task first-order term "
                      f"split into its two halves",
          "verdict": f"MET -- the ledger is carried at {MIN_REPS} and {PAIR_REPS} replicates" if
                     (not thin and not pair_thin) else f"FALSIFIER FIRED -- {thin or pair_thin}"}
    nonzero = {a: [round(x, 6) for x in rolls["pair/frozen"]["arms"][a]["bias"]]
               for a in sorted(rolls["pair/frozen"]["arms"])
               if any(abs(x) > ZERO for x in rolls["pair/frozen"]["arms"][a]["bias"])}
    flat_theta = all(abs(x) < ZERO for a in rolls["pair/frozen"]["arms"]
                     for x in rolls["pair/frozen"]["arms"][a]["theta"])
    j2 = {"id": "BH2",
          "measured": f"with the bias frozen the bias half is at most {s['frozen_bias_max']:.2e} over the roll's arms "
                      f"and tasks, against a weight half of at most {s['frozen_theta_max']:.2e}",
          "verdict": f"MET -- the frozen side's bias half is exactly zero on every arm and task while the weight half "
                     f"is not" if (not nonzero and not flat_theta) else
                     f"FALSIFIER FIRED -- non-zero {nonzero} or a flat weight half {flat_theta}"}
    comparisons = {}
    #: the two rolls with a live bias; the frozen roll's shares are zero on both sides by construction
    for lbl in ("cell", "pair/plastic"):
        roll = rolls.get(lbl)
        if not roll:
            continue
        arms = roll["arms"]
        for a in PENALTIES:
            if a not in arms:
                continue
            for j in range(arms[a]["tasks"]):
                comparisons[f"{lbl}/{a}/task{j}"] = (arms[a]["share"][j] is not None
                                                     and arms[BASELINE]["share"][j] is not None
                                                     and arms[a]["share"][j] > arms[BASELINE]["share"][j])
    behind = {k: v for k, v in comparisons.items() if not v}
    live = {lbl: {a: rolls[lbl]["arms"][a]["share"] for a in PENALTIES if a in rolls[lbl]["arms"]}
            for lbl in ("cell", "pair/plastic") if lbl in rolls}
    j3 = {"id": "BH3",
          "measured": f"the penalty arms' bias shares against the baseline's are {live}, the frozen roll's being zero "
                      f"on both sides by construction",
          "verdict": f"MET -- every penalty arm's bias share is above the baseline's on every task of both live runs, "
                     f"{len(comparisons)} comparisons" if (comparisons and not behind) else
                     f"FALSIFIER FIRED -- {behind}"}
    diag = s["diagonal_shares"]
    j4 = {"id": "BH4",
          "measured": f"the diagonal penalty's bias shares on the plastic pair are {diag}",
          "verdict": f"MET -- the diagonal penalty's bias share is at least {DIAGONAL_SHARE:.1f} on both tasks" if
                     (diag and all(v >= DIAGONAL_SHARE for v in diag)) else
                     f"FALSIFIER FIRED -- {diag}" if (not diag or any(v < DIAGONAL_FIRES for v in diag)) else
                     f"NULL -- {diag}, between {DIAGONAL_FIRES:.1f} and {DIAGONAL_SHARE:.1f}"}
    n, total = s["buffer_below_baseline"], s["comparisons"]
    j5 = {"id": "BH5",
          "measured": f"the buffer's whole-body term is below the baseline's on {n} of {total} task comparisons",
          "verdict": f"MET -- the buffer's whole term is below the baseline's on every task of all three rolls, "
                     f"{n} of {total}" if n == total else f"FALSIFIER FIRED -- {n} of {total}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the interference runs through the bias for the penalised arms ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a roll is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the corpus's own one-line interference account, split into its weight and bias halves")
    print(f"\n   {'roll':>14} {'arm':>16} {'theta 0/1':>22} {'bias 0/1':>22} {'whole 0/1':>22} {'bias share':>18}")
    for lbl, roll in r["rolls"].items():
        for a in sorted(roll["arms"]):
            v = roll["arms"][a]
            print(f"   {lbl:>14} {a:>16} " + " ".join(f"{x:+.4f}" for x in v["theta"]) + "  "
                  + " ".join(f"{x:+.4f}" for x in v["bias"]) + "  "
                  + " ".join(f"{x:+.4f}" for x in v["whole"]) + "  "
                  + " ".join("none" if x is None else f"{x:.2f}" for x in v["share"]))
    s = r["spans"]
    print(f"\n   the frozen side's bias half at most {s['frozen_bias_max']:.2e} against a weight half of at most "
          f"{s['frozen_theta_max']:.2e}")
    print("\n== the registered claims, BH1-BH5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e139` built the split after the weight-only form read one channel; `e427`, `e430` and `e431` found")
    print("    the bias carrying the aid and the penalties displacing it, which is what this reads the instrument on)")
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
