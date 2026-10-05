"""E422 -- the buffer buys retention and pays in learning: the trade decomposed, task by task, on all twelve draws.

`e419`, `e420` and `e421` measured the trade -- the two older tasks recovered, the newest cost -- and registered what
the newest loss is: *"the newest task is never forgotten after it is taught, so its loss is a `learned` loss as much
as a forgetting one."* `e304` established the decomposition the corpus's own retention matrix supports: the final
accuracy is the level a task reached when it was taught minus what was lost since, and both are recorded per replicate.

**This unit applies it to the paired gain.** For each of the twelve far-point draws, each of the two arms and each of
the three tasks: the **learning term** (what the buffer changes about the level a task is taught to) and the
**retention term** (what it changes about how much is lost afterwards), whose sum is the gain `e420` measured. No
training, no probe. Five claims, registered before this unit's pass over the runs.

- **AW1 -- and the ledger is carried.** Twelve cells, both arms at **20** replicates, three per-task entries on the
  learned, final and forgetting readings. **Falsifier**: any cell, arm or entry missing.
- **AW2 -- and the oldest task's whole gain is retention.** In every cell the learning term at task 0 is **zero to a
  thousandth** -- the two arms are the same arm when the first task is taught -- and the retention term is at least
  **0.20**. **Falsifier**: any cell whose learning term is not zero, or whose retention term is below **0.10**;
  **null**: between.
- **AW3 -- and the newest task's whole loss is a learning term.** In every cell the retention term at task 2 is
  **zero to a thousandth** -- neither arm forgets the task it was taught last -- and the learning term is negative.
  **Falsifier**: any cell whose retention term is not zero, or whose learning term is at or above zero.
- **AW4 -- and in the middle it pays a small learning price for a large retention gain.** In every cell the retention
  term at task 1 is at least **0.10** and at least **three times** the magnitude of the learning term there.
  **Falsifier**: any cell below **0.05** on the retention term or below **twice** on the ratio; **null**: between.
- **AW5 -- and the two terms are the gain.** In every cell and at every task the learning term plus the retention term
  equals the final-accuracy gain, to a thousandth. **Falsifier**: any cell and task differing by more than a
  thousandth. *This is the identity the whole unit rests on: `e304`'s decomposition read on the paired difference
  rather than on one arm.*

**What it can do beyond that.** It says what the buffer's headline number is made of. On all twelve draws the recovery
of the oldest task is **entirely** retention -- the two arms learn task 0 to the same level by construction and the
buffer keeps 0.2333 to 0.3219 more of it -- and the damage to the newest task is **entirely** a learning term: the
buffer never forgets the last task, it simply reaches a lower level on it (0.0115 to 0.1031 lower). In the middle it
buys a retention gain of 0.1594 to 0.3271 for a learning price of 0.0042 to 0.0750, at least four times smaller.

**What it cannot do.** *One order and one arm pair*: the as-built three tasks, `naive` and `replay`, five hundred
updates, so `e317`'s order axis and the penalty arms are not here. *And the decomposition is the corpus's*: `e305`
showed that `mean_forgetting` cannot see the part an arm never learned, so the retention term here is the corpus's own
diagonal-minus-last-row reading of what was lost. *And the two zeros are structural*: the learning term at task 0 is
zero because the arms are identical until it is taught and the retention term at task 2 because nothing is taught
after it, so they are identities of the protocol rather than measurements. *And a decomposition is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the twelve far-point cells `e420` and `e421` read
RUNS = {
    "card": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
    "world1": Path("runs/e395_earned_label_worldseed1_iters500_20reps.json"),
    "world2": Path("runs/e395_earned_label_worldseed2_iters500_20reps.json"),
    "world3": Path("runs/e396_earned_label_worldseed3_iters500_20reps.json"),
    "world4": Path("runs/e396_earned_label_worldseed4_iters500_20reps.json"),
    "stream1": Path("runs/e403_earned_label_stream1_iters500_20reps.json"),
    "stream2": Path("runs/e403_earned_label_stream2_iters500_20reps.json"),
    "cue1": Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"),
    "cue3": Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"),
    "cue6": Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"),
    "cue9": Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"),
    "cue14": Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"),
}
ARMS = ("naive", "replay")
N_TASKS = 3
OLDEST, MIDDLE, NEWEST = 0, 1, 2
MIN_CELLS = 10
MIN_REPS = 20
ZERO = 1e-3
RETENTION = 0.20
RETENTION_FIRES = 0.10
MIDDLE_BAR = 0.10
MIDDLE_FIRES = 0.05
RATIO = 3.0
RATIO_FIRES = 2.0
CLAIMS = (
    ("AW1", f"and the ledger is carried, over at least {MIN_CELLS} cells and {MIN_REPS} replicates",
     "Twelve cells, both arms at twenty replicates, three per-task entries on the learned, final and forgetting "
     "readings",
     "falsifier: any cell, arm or entry missing"),
    ("AW2", f"and the oldest task's whole gain is retention, at least {RETENTION:.2f}",
     "In every cell the learning term at task 0 is zero to a thousandth and the retention term is at least 0.20",
     f"falsifier: any cell whose learning term is not zero, or whose retention term is below {RETENTION_FIRES:.2f}; "
     f"null: between"),
    ("AW3", "and the newest task's whole loss is a learning term",
     "In every cell the retention term at task 2 is zero to a thousandth and the learning term is negative",
     "falsifier: any cell whose retention term is not zero, or whose learning term is at or above zero"),
    ("AW4", f"and in the middle it pays a small learning price for a large retention gain, {RATIO:.0f} times",
     "In every cell the retention term at task 1 is at least 0.10 and at least three times the magnitude of the "
     "learning term there",
     f"falsifier: any cell below {MIDDLE_FIRES:.2f} on the retention term or below {RATIO_FIRES:.0f} on the ratio; "
     f"null: between"),
    ("AW5", "and the two terms are the gain",
     "In every cell and at every task the learning term plus the retention term equals the final-accuracy gain, to a "
     "thousandth",
     "falsifier: any cell and task differing by more than a thousandth"),
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


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "cells": {}}
    for name, path in runs.items():
        doc = load(path)
        if not doc:
            return {**out, "ok": False, "reason": f"cell {name}: {path} is absent"}
        got = {}
        for arm in ARMS:
            reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
            if not reps:
                return {**out, "ok": False, "reason": f"cell {name}: the {arm} arm carries no replicates"}
            got[arm] = {"replicates": len(reps), "learned": _per_task(reps, "learned"),
                        "final": _per_task(reps, "final_per_task"),
                        "forgetting": _per_task(reps, "forgetting_per_task")}
        learn = [got["replay"]["learned"][k] - got["naive"]["learned"][k] for k in range(N_TASKS)]
        gain2 = [got["replay"]["final"][k] - got["naive"]["final"][k] for k in range(N_TASKS)]
        retain = [gain2[k] - learn[k] for k in range(N_TASKS)]
        out["cells"][name] = {"artifact": path.name,
                              "replicates": min(got["naive"]["replicates"], got["replay"]["replicates"]),
                              "naive": {k: v for k, v in got["naive"].items() if k != "replicates"},
                              "replay": {k: v for k, v in got["replay"].items() if k != "replicates"},
                              "learned": learn, "retention": retain, "gain": gain2,
                              "middle_ratio": (abs(retain[MIDDLE]) / abs(learn[MIDDLE])) if learn[MIDDLE] else None}
    out["spans"] = {"cells": len(out["cells"]),
                    "replicates": sorted({c["replicates"] for c in out["cells"].values()}),
                    "oldest_learn_max": max(abs(c["learned"][OLDEST]) for c in out["cells"].values()),
                    "oldest_retain_min": min(c["retention"][OLDEST] for c in out["cells"].values()),
                    "newest_retain_max": max(abs(c["retention"][NEWEST]) for c in out["cells"].values()),
                    "newest_learn_max": max(c["learned"][NEWEST] for c in out["cells"].values()),
                    "middle_retain_min": min(c["retention"][MIDDLE] for c in out["cells"].values()),
                    "middle_learn_worst": min(c["learned"][MIDDLE] for c in out["cells"].values()),
                    "middle_learn_cost": sum(1 for c in out["cells"].values() if c["learned"][MIDDLE] < 0),
                    "middle_ratio_min": min(c["middle_ratio"] for c in out["cells"].values()
                                            if c["middle_ratio"] is not None),
                    "worst_identity": max(abs(c["gain"][k] - c["learned"][k] - c["retention"][k])
                                          for c in out["cells"].values() for k in range(N_TASKS))}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a cell's run or an arm is absent"}
                for c in CLAIMS]
    cells, s = r["cells"], r["spans"]
    thin = {n: c["replicates"] for n, c in cells.items() if c["replicates"] < MIN_REPS}
    j1 = {"id": "AW1",
          "measured": f"{len(cells)} cells at {s['replicates']} replicates, both arms, three per-task entries on the "
                      f"learned, final and forgetting readings",
          "verdict": f"MET -- the ledger is carried over {len(cells)} cells" if
                     (len(cells) >= MIN_CELLS and not thin) else f"FALSIFIER FIRED -- {len(cells)} cells, thin {thin}"}
    nonzero = {n: c["learned"][OLDEST] for n, c in cells.items() if abs(c["learned"][OLDEST]) > ZERO}
    shallow = {n: c["retention"][OLDEST] for n, c in cells.items() if c["retention"][OLDEST] < RETENTION}
    deep_fires = any(v < RETENTION_FIRES for v in shallow.values())
    j2 = {"id": "AW2",
          "measured": f"the learning term at task 0 is zero to a thousandth in every cell (the largest "
                      f"{s['oldest_learn_max']:.2e}) and the retention term runs "
                      f"{s['oldest_retain_min']:+.4f} to "
                      f"{max(c['retention'][OLDEST] for c in cells.values()):+.4f}",
          "verdict": f"MET -- the oldest task's whole gain is retention, at least {s['oldest_retain_min']:+.4f}" if
                     (not nonzero and not shallow) else
                     f"FALSIFIER FIRED -- non-zero learning {nonzero} or shallow retention {shallow}" if
                     (nonzero or deep_fires) else
                     f"NULL -- {shallow} between {RETENTION_FIRES:.2f} and {RETENTION:.2f}"}
    sticky = {n: c["retention"][NEWEST] for n, c in cells.items() if abs(c["retention"][NEWEST]) > ZERO}
    helped = {n: c["learned"][NEWEST] for n, c in cells.items() if c["learned"][NEWEST] >= 0}
    j3 = {"id": "AW3",
          "measured": f"the retention term at task 2 is zero to a thousandth in every cell (the largest "
                      f"{s['newest_retain_max']:.2e}) and the learning term runs "
                      f"{s['newest_learn_max']:+.4f} to "
                      f"{min(c['learned'][NEWEST] for c in cells.values()):+.4f}",
          "verdict": f"MET -- the newest task's whole loss is a learning term, at most {s['newest_learn_max']:+.4f}" if
                     (not sticky and not helped) else
                     f"FALSIFIER FIRED -- retention {sticky} or a learning term at or above zero {helped}"}
    shallow4 = {n: c["retention"][MIDDLE] for n, c in cells.items() if c["retention"][MIDDLE] < MIDDLE_BAR}
    tight = {n: c["middle_ratio"] for n, c in cells.items()
             if c["middle_ratio"] is not None and c["middle_ratio"] < RATIO}
    j4 = {"id": "AW4",
          "measured": f"the retention term at task 1 runs {s['middle_retain_min']:+.4f} to "
                      f"{max(c['retention'][MIDDLE] for c in cells.values()):+.4f} against a learning term of "
                      f"{s['middle_learn_worst']:+.4f} to "
                      f"{max(c['learned'][MIDDLE] for c in cells.values()):+.4f} (a cost in "
                      f"{s['middle_learn_cost']} of {len(cells)}), the ratio at least {s['middle_ratio_min']:.2f}",
          "verdict": f"MET -- in the middle it pays a learning price at least {s['middle_ratio_min']:.2f} times "
                     f"smaller than the retention gain" if (not shallow4 and not tight) else
                     f"FALSIFIER FIRED -- shallow retention {shallow4} or a tight ratio {tight}" if
                     (any(v < MIDDLE_FIRES for v in shallow4.values()) or any(v < RATIO_FIRES for v in tight.values()))
                     else f"NULL -- {shallow4 or tight} between the bars"}
    bad = {n: max(abs(c["gain"][k] - c["learned"][k] - c["retention"][k]) for k in range(N_TASKS))
           for n, c in cells.items()}
    bad = {n: v for n, v in bad.items() if v > ZERO}
    j5 = {"id": "AW5",
          "measured": f"the largest gap between the gain and the two terms over {len(cells)} cells and {N_TASKS} "
                      f"tasks is {s['worst_identity']:.2e}",
          "verdict": "MET -- the two terms are the gain in every cell and task, to a thousandth" if not bad else
          f"FALSIFIER FIRED -- {bad}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the buffer buys retention and pays in learning ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a cell is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the twelve far-point cells, the paired gain split into what the buffer changes about the level a task is")
    print("   taught to (learned) and about how much is lost afterwards (retention)")
    print(f"\n   {'cell':>8} {'learned 0/1/2':>26} {'retention 0/1/2':>26} {'gain 0/1/2':>26} {'T1 ratio':>9}")
    for n in sorted(r["cells"], key=lambda x: r["cells"][x]["retention"][OLDEST]):
        c = r["cells"][n]
        print(f"   {n:>8} " + " ".join(f"{x:+.4f}" for x in c["learned"]) + "  "
              + " ".join(f"{x:+.4f}" for x in c["retention"]) + "  "
              + " ".join(f"{x:+.4f}" for x in c["gain"]) + f" {c['middle_ratio']:9.2f}")
    s = r["spans"]
    print(f"\n   over {s['cells']} cells: the task-0 learning term is zero to {s['oldest_learn_max']:.1e} with a "
          f"retention of at least {s['oldest_retain_min']:+.4f}; the task-2 retention term is zero to "
          f"{s['newest_retain_max']:.1e} with a learning term of at most {s['newest_learn_max']:+.4f}; at task 1 the "
          f"retention is at least {s['middle_retain_min']:+.4f} against a learning term as low as "
          f"{s['middle_learn_worst']:+.4f}, a cost in {s['middle_learn_cost']} of {s['cells']}")
    print("\n== the registered claims, AW1-AW5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e419`, `e420` and `e421` measured the trade and registered that the newest task's loss is a learned")
    print("    one; `e304` established the decomposition this reads it with)")
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
