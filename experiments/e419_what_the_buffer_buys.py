"""E419 -- what the buffer buys and what it costs: a gain on the two older tasks and a loss on the newest, on every world.

`e410` read the `naive` arm's decomposition on the six worlds and `e411` the two arms' means, and both reported a
single number per arm: the mean final accuracy. `e304`, `e310` and `e312` established that the mean is an average over
three tasks with different positions, and that the newest task's accuracy is the quantity an aggregate cannot contain.
Nobody has read the buffer's own per-task ledger.

**This unit reads it, off the same six runs.** The card's world and five cue redraws at five hundred updates, twenty
replicates, both arms, and each replicate carries `learned`, `final_per_task` and `forgetting_per_task` over the three
tasks. No training, no probe. Five claims, registered before this unit's pass over the runs.

- **AT1 -- and the ledger is carried.** Six worlds at the far point, both arms at **20** replicates, each replicate
  carrying three per-task entries on both quantities. **Falsifier**: any world, arm or entry missing.
- **AT2 -- and the buffer gains on the oldest task.** On every world, `replay`'s final accuracy at task **0** exceeds
  `naive`'s by at least **0.10**. **Falsifier**: any world below **0.05**; **null**: between.
- **AT3 -- and on the middle one.** The same at task **1**, by at least **0.10**. **Falsifier**: any world below
  **0.05**; **null**: between.
- **AT4 -- and it costs the newest one.** On every world, `replay`'s final accuracy at task **2** is **below**
  `naive`'s. **Falsifier**: any world at or above zero. *This is the unit's own prediction: the buffer's headline
  number is a net, and the term it is net of is the task the corpus's protocol trains last.*
- **AT5 -- and the two older gains cover the newest loss.** On every world the sum of the task-0 and task-1 gains is
  at least **four times** the task-2 loss. **Falsifier**: any world below **twice**; **null**: between.

**What it can do beyond that.** It says what the corpus's headline arm does, task by task: on all six worlds `replay`
recovers the oldest task from about 0.33 to about 0.62 and the middle one from about 0.44 to about 0.68, and it pays
for both by finishing the newest task **0.04 to 0.10** lower than the arm that does nothing. So `e411`'s
**+0.1330** to **+0.1594** is a net of a gain five to eight times the loss it hides, and the benchmark's aggregate
metric reads as improvement a change that has a systematic loser.

**What it cannot do.** *One setting and one pair*: the corpus's buffer (`--replay-per-task 16 --replay-batch 16`) and
the `naive`/`replay` arms, at five hundred updates on six worlds, so nothing here is about the penalty arms `e415` and
`e416` read elsewhere. *And the loss is on the arm's own last task*: the protocol trains the tasks in one order, and
`e317` showed the order moves the arms that read a penalty and not the ones that do not, so where the loss falls is a
property of this order. *And the metric is the corpus's*: `mean_forgetting` is the retention matrix's diagonal minus
its last row, which `e305` showed cannot see the part an arm never learned. *And a decomposition is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the six worlds at the far point, the same six `e410`, `e411` and `e413` read
RUNS = {
    "card": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
    "cue1": Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
    "cue3": Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
    "cue6": Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"),
    "cue9": Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
    "cue14": Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
}
ARMS = ("naive", "replay")
N_TASKS = 3
OLDEST, MIDDLE, NEWEST = 0, 1, 2
MIN_WORLDS = 5
MIN_REPS = 20
GAIN = 0.10
GAIN_FIRES = 0.05
LOSS = 0.0
RATIO = 4.0
RATIO_FIRES = 2.0
CLAIMS = (
    ("AT1", f"and the ledger is carried, over at least {MIN_WORLDS} worlds and {MIN_REPS} replicates",
     "Six worlds at the far point, both arms at twenty replicates, each replicate carrying three per-task entries on "
     "the learned, final and forgetting readings",
     "falsifier: any world, arm or entry missing"),
    ("AT2", f"and the buffer gains on the oldest task, {GAIN:.2f}",
     "On every world replay's final accuracy at task 0 exceeds naive's by at least 0.10",
     f"falsifier: any world below {GAIN_FIRES:.2f}; null: between"),
    ("AT3", f"and on the middle one, {GAIN:.2f}",
     "The same at task 1, by at least 0.10",
     f"falsifier: any world below {GAIN_FIRES:.2f}; null: between"),
    ("AT4", "and it costs the newest one",
     "On every world replay's final accuracy at task 2 is below naive's",
     "falsifier: any world at or above zero"),
    ("AT5", f"and the two older gains cover the newest loss, {RATIO:.1f} times",
     "On every world the sum of the task-0 and task-1 gains is at least four times the task-2 loss",
     f"falsifier: any world below {RATIO_FIRES:.1f}; null: between"),
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


def reading(runs: dict = RUNS, arms=ARMS) -> dict:
    out = {"ok": True, "reason": None, "worlds": {}, "arms": list(arms)}
    for name, path in runs.items():
        doc = load(path)
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: {path} is absent"}
        entry = {"artifact": path.name, "arms": {}}
        for arm in arms:
            reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
            if not reps:
                return {**out, "ok": False, "reason": f"world {name}: the {arm} arm carries no replicates"}
            entry["arms"][arm] = {"replicates": len(reps),
                                  "learned": _per_task(reps, "learned"),
                                  "final": _per_task(reps, "final_per_task"),
                                  "forgetting": _per_task(reps, "forgetting_per_task")}
        n, r = entry["arms"]["naive"], entry["arms"]["replay"]
        gains = [r["final"][k] - n["final"][k] for k in range(N_TASKS)]
        entry["gain_by_task"] = gains
        entry["older_gain"] = gains[OLDEST] + gains[MIDDLE]
        entry["newest_loss"] = -gains[NEWEST]
        entry["coverage"] = entry["older_gain"] / entry["newest_loss"] if entry["newest_loss"] > 0 else float("inf")
        out["worlds"][name] = entry
    gains = [w["gain_by_task"][k] for w in out["worlds"].values() for k in range(N_TASKS)]
    out["spans"] = {"worlds": len(out["worlds"]),
                    "oldest": [out["worlds"][n]["gain_by_task"][OLDEST] for n in out["worlds"]],
                    "middle": [out["worlds"][n]["gain_by_task"][MIDDLE] for n in out["worlds"]],
                    "newest": [out["worlds"][n]["gain_by_task"][NEWEST] for n in out["worlds"]],
                    "least_oldest": min(out["worlds"][n]["gain_by_task"][OLDEST] for n in out["worlds"]),
                    "least_middle": min(out["worlds"][n]["gain_by_task"][MIDDLE] for n in out["worlds"]),
                    "worst_newest": max(out["worlds"][n]["gain_by_task"][NEWEST] for n in out["worlds"]),
                    "least_coverage": min(out["worlds"][n]["coverage"] for n in out["worlds"]),
                    "mean_gain": statistics.fmean(gains)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a world's run or an arm is absent"}
                for c in CLAIMS]
    worlds = r["worlds"]
    missing = {n: sorted({a for a in ARMS if w["arms"][a]["replicates"] < MIN_REPS})
               for n, w in worlds.items()
               if any(w["arms"][a]["replicates"] < MIN_REPS for a in ARMS)}
    short = {n: sorted({a for a in ARMS for k in ("learned", "final", "forgetting")
                        if len(w["arms"][a][k]) != N_TASKS}) for n, w in worlds.items()}
    short = {n: v for n, v in short.items() if v}
    j1 = {"id": "AT1",
          "measured": f"{len(worlds)} worlds, both arms at "
                      f"{sorted({w['arms'][a]['replicates'] for w in worlds.values() for a in ARMS})} replicates, "
                      f"each carrying {N_TASKS} per-task entries on the learned, final and forgetting readings",
          "verdict": f"MET -- the ledger is carried over {len(worlds)} worlds" if
                     (len(worlds) >= MIN_WORLDS and not missing and not short) else
                     f"FALSIFIER FIRED -- {missing or short}"}
    old = {n: w["gain_by_task"][OLDEST] for n, w in worlds.items()}
    least_old = min(old.values())
    j2 = {"id": "AT2",
          "measured": f"the task-0 gains are "
                      f"{ {n: round(v, 4) for n, v in sorted(old.items(), key=lambda kv: kv[1])} }",
          "verdict": f"MET -- the buffer gains on the oldest task on every world, the least {least_old:+.4f}" if
                     least_old >= GAIN else
                     f"FALSIFIER FIRED -- {least_old:+.4f} is under the bar" if least_old < GAIN_FIRES else
                     f"NULL -- {least_old:+.4f}, between {GAIN_FIRES:.2f} and {GAIN:.2f}"}
    mid = {n: w["gain_by_task"][MIDDLE] for n, w in worlds.items()}
    least_mid = min(mid.values())
    j3 = {"id": "AT3",
          "measured": f"the task-1 gains are "
                      f"{ {n: round(v, 4) for n, v in sorted(mid.items(), key=lambda kv: kv[1])} }",
          "verdict": f"MET -- the buffer gains on the middle task on every world, the least {least_mid:+.4f}" if
                     least_mid >= GAIN else
                     f"FALSIFIER FIRED -- {least_mid:+.4f} is under the bar" if least_mid < GAIN_FIRES else
                     f"NULL -- {least_mid:+.4f}, between {GAIN_FIRES:.2f} and {GAIN:.2f}"}
    new = {n: w["gain_by_task"][NEWEST] for n, w in worlds.items()}
    worst = max(new.values())
    j4 = {"id": "AT4",
          "measured": f"the task-2 gains are "
                      f"{ {n: round(v, 4) for n, v in sorted(new.items(), key=lambda kv: -kv[1])} }",
          "verdict": f"MET -- the buffer costs the newest task on every world, the least loss "
                     f"{min(new.values()):+.4f}" if worst < LOSS else
                     f"FALSIFIER FIRED -- {worst:+.4f} is not a loss"}
    cov = {n: round(w["coverage"], 2) for n, w in worlds.items()}
    least_cov = min(cov.values())
    j5 = {"id": "AT5",
          "measured": f"the coverage ratios are {dict(sorted(cov.items(), key=lambda kv: kv[1]))}, the least "
                      f"{least_cov:.2f} times",
          "verdict": f"MET -- the two older gains cover the newest loss by {least_cov:.2f} times at the least" if
                     least_cov >= RATIO else
                     f"FALSIFIER FIRED -- {least_cov:.2f} is under the bar" if least_cov < RATIO_FIRES else
                     f"NULL -- {least_cov:.2f}, between {RATIO_FIRES:.1f} and {RATIO:.1f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== what the buffer buys and what it costs ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a world is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the six worlds at five hundred updates, twenty replicates, the per-task final accuracy of both arms")
    print(f"\n   {'world':>7} {'naive 0/1/2':>26} {'replay 0/1/2':>26} {'gain 0/1/2':>26} {'coverage':>9}")
    for n in sorted(r["worlds"], key=lambda x: -r["worlds"][x]["gain_by_task"][0]):
        w = r["worlds"][n]
        print(f"   {n:>7} " + " ".join(f"{x:.4f}" for x in w["arms"]["naive"]["final"]) + "  "
              + " ".join(f"{x:.4f}" for x in w["arms"]["replay"]["final"]) + "  "
              + " ".join(f"{x:+.4f}" for x in w["gain_by_task"]) + f" {w['coverage']:9.2f}")
    s = r["spans"]
    print(f"\n   the least task-0 gain {s['least_oldest']:+.4f}, the least task-1 gain {s['least_middle']:+.4f}, the "
          f"worst task-2 gain {s['worst_newest']:+.4f}, the least coverage {s['least_coverage']:.2f}, the mean gain "
          f"over the eighteen task-world pairs {s['mean_gain']:+.4f}")
    print("\n== the registered claims, AT1-AT5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e410` read the naive arm's decomposition and `e411` the two arms' means; this reads the buffer's own")
    print("    per-task ledger, which is where the net is taken)")
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
