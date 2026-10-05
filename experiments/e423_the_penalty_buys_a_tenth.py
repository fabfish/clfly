"""E423 -- the penalty buys a tenth of the retention: the two arms' trade on one cell, arm against arm.

`e422` split the buffer's paired gain into a learning term and a retention term on the twelve far-point draws and
found the buffer buying retention and paying in learning. `e415` measured the penalty against the same buffer on one
cell -- the card's world at five hundred updates, `naive`, `ewc-block` and `replay` in **one run** at twenty
replicates -- and found the buffer ahead on both axes at eleven sigma, with the penalty unresolved against `naive`.

**This unit puts the two readings together.** The cell `e415` read carries the same per-task recordings `e422` used,
so both arms can be decomposed against the same `naive` baseline, on the same seeds, in the same run: what each arm
buys in retention and what each pays in learning. No training, no probe. Five claims, registered before this unit's
pass over the run.

- **AX1 -- and the ledger is carried.** One artifact carrying `naive`, `ewc-block` and `replay` at **20** replicates,
  with the learned, final and forgetting readings per task on each. **Falsifier**: any arm or entry missing, or fewer
  replicates.
- **AX2 -- and the penalty buys retention too.** `ewc-block`'s retention terms at tasks **0** and **1** are both
  positive. **Falsifier**: either at or below zero. *This is the unit's own prediction: a penalty regularises toward
  the past, so if the buffer's retention is a mechanism the penalty shares, the penalty should show it too.*
- **AX3 -- and the two arms pay about the same price.** The gap between the two arms' learning terms is at most
  **0.05** at the middle task and at the newest. **Falsifier**: any gap above **0.10**; **null**: between. *Together
  with AX4 this is the unit's own prediction: if the two arms pay the same, the difference in what they gain is a
  difference in what they buy.*
- **AX4 -- and the buffer buys at least five times the retention.** `replay`'s retention term is at least **five
  times** `ewc-block`'s at task 0 and at task 1. **Falsifier**: either ratio below **twice**; **null**: between.
- **AX5 -- and only the buffer's trade pays.** `ewc-block`'s gain at task 1 is negative while `replay`'s is at least
  **+0.20**. **Falsifier**: the penalty's task-1 gain at or above **+0.05**, or the buffer's below **+0.10**.

**What it can do beyond that.** It explains `e415`'s eleven-sigma result: on the same run the penalty buys a
**+0.0292** retention on the oldest task and **+0.0406** on the middle where the buffer buys **+0.2844** and
**+0.2896** -- **7.13** to **9.75** times as much -- while the two arms' learning prices differ by at most **0.0344**
in either direction. So the failure of the penalty on this substrate is not that it does not regularise; it is that it
regularises a tenth as much for the same price.

**What it cannot do.** *One cell, one strength and one penalty*: the card's world at `lam = 1.0` with `ewc-block`, so
the `lam` ladder, the diagonal penalty and the other draws are not in this reading, and `e416`'s corpus-wide ledger is
not either. *And the cell's world predates the coupling*: `e415` reported that `e380` records the world as coupled and
this artifact carries no such field. *And the two arms share a run but not a mechanism*: the split says what each arm
changed, not how. *And the decomposition is the corpus's*: the retention term is the diagonal-minus-last-row reading,
which `e305` showed cannot see the part an arm never learned.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the one cell that carries all three arms at twenty replicates, the cell `e415` read
RUN = Path("runs/e356_earned_label_r32_20reps.json")
BASELINE = "naive"
ARMS = ("ewc-block", "replay")
N_TASKS = 3
OLDEST, MIDDLE, NEWEST = 0, 1, 2
MIN_REPS = 20
PRICE = 0.05
PRICE_FIRES = 0.10
RATIO = 5.0
RATIO_FIRES = 2.0
BUFFER_GAIN = 0.20
BUFFER_FIRES = 0.10
PENALTY_GAIN = 0.05
CLAIMS = (
    ("AX1", f"and the ledger is carried, at least {MIN_REPS} replicates and all three arms",
     "One artifact carrying naive, ewc-block and replay at twenty replicates, with the learned, final and forgetting "
     "readings per task on each",
     "falsifier: any arm or entry missing, or fewer replicates"),
    ("AX2", "and the penalty buys retention too",
     "ewc-block's retention terms at tasks 0 and 1 are both positive",
     "falsifier: either at or below zero"),
    ("AX3", f"and the two arms pay about the same price, within {PRICE:.2f}",
     "The gap between the two arms' learning terms is at most 0.05 at the middle task and at the newest",
     f"falsifier: any gap above {PRICE_FIRES:.2f}; null: between"),
    ("AX4", f"and the buffer buys at least five times the retention",
     "replay's retention term is at least five times ewc-block's at task 0 and at task 1",
     f"falsifier: either ratio below {RATIO_FIRES:.0f}; null: between"),
    ("AX5", "and only the buffer's trade pays",
     "ewc-block's gain at task 1 is negative while replay's is at least +0.20",
     f"falsifier: the penalty's task-1 gain at or above {PENALTY_GAIN:+.2f}, or the buffer's below "
     f"{BUFFER_FIRES:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _per_task(reps, key) -> list[float]:
    return [statistics.fmean([r[key][k] for r in reps]) for k in range(N_TASKS)]


def reading(run: Path = RUN) -> dict:
    out = {"ok": True, "reason": None, "artifact": None, "arms": {}, "terms": {}}
    doc = load(run)
    if not doc:
        return {**out, "ok": False, "reason": f"{run} is absent"}
    out["artifact"] = run.name
    for arm in (BASELINE,) + ARMS:
        reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
        if not reps:
            return {**out, "ok": False, "reason": f"the {arm} arm carries no replicates"}
        out["arms"][arm] = {"replicates": len(reps), "learned": _per_task(reps, "learned"),
                            "final": _per_task(reps, "final_per_task"),
                            "forgetting": _per_task(reps, "forgetting_per_task")}
    base = out["arms"][BASELINE]
    for arm in ARMS:
        got = out["arms"][arm]
        learned = [got["learned"][k] - base["learned"][k] for k in range(N_TASKS)]
        gain = [got["final"][k] - base["final"][k] for k in range(N_TASKS)]
        retention = [gain[k] - learned[k] for k in range(N_TASKS)]
        out["terms"][arm] = {"learned": learned, "retention": retention, "gain": gain}
    out["spans"] = {"replicates": sorted({v["replicates"] for v in out["arms"].values()}),
                    "ratios": {str(k): (out["terms"]["replay"]["retention"][k]
                                        / out["terms"]["ewc-block"]["retention"][k])
                               if out["terms"]["ewc-block"]["retention"][k] else None
                               for k in (OLDEST, MIDDLE)},
                    "worst_gap": max(abs(out["terms"][a]["gain"][k] - out["terms"][a]["learned"][k]
                                         - out["terms"][a]["retention"][k])
                                     for a in ARMS for k in range(N_TASKS))}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the run or an arm is absent"}
                for c in CLAIMS]
    arms, terms, s = r["arms"], r["terms"], r["spans"]
    thin = {a: v["replicates"] for a, v in arms.items() if v["replicates"] < MIN_REPS}
    j1 = {"id": "AX1",
          "measured": f"`{r['artifact']}` carries {sorted(arms)} at {s['replicates']} replicates, three per-task "
                      f"readings each",
          "verdict": f"MET -- the ledger is carried with all three arms at {MIN_REPS} replicates" if not thin else
                     f"FALSIFIER FIRED -- {thin}"}
    pen = terms["ewc-block"]["retention"]
    buys = [pen[OLDEST] > 0, pen[MIDDLE] > 0]
    j2 = {"id": "AX2",
          "measured": f"ewc-block's retention terms are {[round(x, 4) for x in pen]}",
          "verdict": f"MET -- the penalty buys retention at the two older tasks, {pen[OLDEST]:+.4f} and "
                     f"{pen[MIDDLE]:+.4f}" if all(buys) else
                     f"FALSIFIER FIRED -- {[round(x, 4) for x in pen]}"}
    lp, lb = terms["ewc-block"]["learned"], terms["replay"]["learned"]
    gaps = {k: lp[k] - lb[k] for k in (MIDDLE, NEWEST)}
    widest = max(abs(v) for v in gaps.values())
    j3 = {"id": "AX3",
          "measured": f"the learning terms are {lp[MIDDLE]:+.4f} against {lb[MIDDLE]:+.4f} at the middle task and "
                      f"{lp[NEWEST]:+.4f} against {lb[NEWEST]:+.4f} at the newest, gaps of "
                      f"{abs(gaps[MIDDLE]):.4f} and {abs(gaps[NEWEST]):.4f}",
          "verdict": f"MET -- the two arms pay within {widest:.4f} of each other at both tasks" if
                     widest <= PRICE else
                     f"FALSIFIER FIRED -- a gap of {widest:.4f}" if widest > PRICE_FIRES else
                     f"NULL -- the widest gap is {widest:.4f}, between {PRICE:.2f} and {PRICE_FIRES:.2f}"}
    ratios = {k: (terms["replay"]["retention"][k] / pen[k]) if pen[k] else None for k in (OLDEST, MIDDLE)}
    worst = min(v for v in ratios.values() if v is not None) if any(v is not None for v in ratios.values()) else None
    j4 = {"id": "AX4",
          "measured": f"the buffer's retention over the penalty's is {ratios[OLDEST]:.2f} at task 0 and "
                      f"{ratios[MIDDLE]:.2f} at task 1" if worst is not None else
                      "the penalty buys no retention at one of the two older tasks",
          "verdict": f"MET -- the buffer buys {worst:.2f} times the retention at the least" if
                     (worst is not None and worst >= RATIO) else
                     f"FALSIFIER FIRED -- {worst} is under the bar" if (worst is None or worst < RATIO_FIRES) else
                     f"NULL -- {worst:.2f}, between {RATIO_FIRES:.0f} and {RATIO:.0f}"}
    gp, gb = terms["ewc-block"]["gain"][MIDDLE], terms["replay"]["gain"][MIDDLE]
    j5 = {"id": "AX5",
          "measured": f"the middle gain is {gp:+.4f} for the penalty and {gb:+.4f} for the buffer",
          "verdict": f"MET -- the penalty's trade does not pay ({gp:+.4f}) where the buffer's does ({gb:+.4f})" if
                     (gp < 0 and gb >= BUFFER_GAIN) else
                     f"FALSIFIER FIRED -- the penalty gains {gp:+.4f} and the buffer {gb:+.4f}" if
                     (gp >= PENALTY_GAIN or gb < BUFFER_FIRES) else
                     f"NULL -- {gp:+.4f} and {gb:+.4f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the penalty buys a tenth of the retention ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print(f"   `{r['artifact']}`, twenty replicates, the three arms of one run, each decomposed against "
          f"`{BASELINE}`")
    print(f"\n   {'arm':>10} {'learned 0/1/2':>26} {'retention 0/1/2':>26} {'gain 0/1/2':>26}")
    print(f"   {BASELINE:>10} " + " ".join(f"{x:.4f}" for x in r['arms'][BASELINE]['learned']) + "  "
          + " ".join(f"{x:.4f}" for x in r['arms'][BASELINE]['forgetting']) + "  "
          + " ".join(f"{x:.4f}" for x in r['arms'][BASELINE]['final']))
    for arm in ("ewc-block", "replay"):
        t = r["terms"][arm]
        print(f"   {arm:>10} " + " ".join(f"{x:+.4f}" for x in t["learned"]) + "  "
              + " ".join(f"{x:+.4f}" for x in t["retention"]) + "  "
              + " ".join(f"{x:+.4f}" for x in t["gain"]))
    s = r["spans"]
    print(f"\n   the buffer's retention over the penalty's: {s['ratios']['0']:.2f} at task 0 and "
          f"{s['ratios']['1']:.2f} at task 1; the largest gap between a gain and its two terms {s['worst_gap']:.2e}")
    print("\n== the registered claims, AX1-AX5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e422` split the buffer's gain and `e415` measured the penalty against the same buffer on one cell;")
    print("    this splits both arms on that cell's own run)")
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
