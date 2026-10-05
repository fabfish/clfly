"""E421 -- the trade turns on: at twenty updates the newest task is cost in eight cells of thirteen, at five hundred in all twelve.

`e420` found the trade's direction to be the one quantity in this line no draw reverses: across twelve earned-label
far-point cells the buffer buys the two older tasks and pays with the newest, every time. `e412` had found the aid
itself turning on between twenty and forty-five updates on the card's world, and `e413` found the same rise on the
other five at the far point.

**This unit reads the per-task ledger at both ends of the same twelve cells.** The corpus rolled every one of them at
**twenty** updates as well as at five hundred -- the card and five cue redraws (`e407`), four engine world redraws
(`e393`) and two of the three clean streams (`e394`) -- each with both arms at twenty replicates. No training, no
probe. Five claims, registered before this unit's pass over the runs.

- **AV1 -- and the paired ledger is carried.** At least **10** cells carrying **both** budgets, both arms at **20**
  replicates, over at least **3** kinds of redraw. **Falsifier**: fewer cells, a missing budget, fewer replicates or
  fewer kinds.
- **AV2 -- and at twenty updates the newest task is not systematically cost.** Among the cells at twenty updates the
  task-2 gain takes **both** signs. **Falsifier**: one sign only, which would say the trade is already there before
  the weights move.
- **AV3 -- and at five hundred it is cost in every one.** Every cell's task-2 gain at five hundred is below zero.
  **Falsifier**: any at or above zero.
- **AV4 -- and the recovery is a twentieth of it at twenty and a fifth at five hundred.** Every cell's task-0 gain is
  at most **0.10** at twenty updates and at least **0.20** at five hundred. **Falsifier**: any cell above **0.20** at
  twenty or below **0.10** at five hundred; **null**: between the bar and its limit.
- **AV5 -- and the coverage is under one at twenty and over five at five hundred.** The least cell's two older gains
  over its newest loss is below **1.0** at twenty updates and above **5.0** at five hundred. **Falsifier**: the least
  at twenty at or above **2.0**, or the least at five hundred at or below **2.0**.

**What it can do beyond that.** It puts `e420`'s constant on `e412`'s axis: the trade is not a property of the three
tasks but of the training that creates the aid. At twenty updates the oldest task is recovered by at most **0.0750**
and the newest is cost in **8 of 13** cells, five of them gaining; at five hundred the oldest is recovered by at least
**0.2333** and the newest is cost in **12 of 12**. So what `e412` found the aid doing between twenty and five hundred
is what its price does too, and the two are the same turn-on read on two axes.

**What it cannot do.** *One order and one arm pair*: the as-built three tasks, `naive` and `replay`, so `e317`'s
order axis is not in this reading. *And the two ends are ten and twenty-five times apart*: nothing here locates the
turn-on between twenty and five hundred, which is `e412`'s twenty-rung ladder on the card's world alone. *And one
cell is unpaired*: the third stream has no five-hundred-update run, so it is in the near band and not in the pairing.
*And the metric is the corpus's*: the newest task is never forgotten after it is taught, so its loss is a `learned`
loss. *And a ledger is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the twelve cells rolled at both ends, each as (twenty updates, five hundred updates)
RUNS = {
    "card": (Path("runs/e407_earned_label_card_iters20_20reps.json"),
             Path("runs/e380_earned_label_cue0_actionsource_20reps.json")),
    "cue1": (Path("runs/e407_earned_label_cue1_iters20_20reps.json"),
             Path("runs/e398_earned_label_cueseed1_iters500_20reps.json")),
    "cue3": (Path("runs/e407_earned_label_cue3_iters20_20reps.json"),
             Path("runs/e398_earned_label_cueseed3_iters500_20reps.json")),
    "cue6": (Path("runs/e407_earned_label_cue6_iters20_20reps.json"),
             Path("runs/e401_earned_label_cueseed6_iters500_20reps.json")),
    "cue9": (Path("runs/e407_earned_label_cue9_iters20_20reps.json"),
             Path("runs/e399_earned_label_cueseed9_iters500_20reps.json")),
    "cue14": (Path("runs/e407_earned_label_cue14_iters20_20reps.json"),
              Path("runs/e399_earned_label_cueseed14_iters500_20reps.json")),
    "world1": (Path("runs/e393_earned_label_worldseed1_iters20_20reps.json"),
               Path("runs/e395_earned_label_worldseed1_iters500_20reps.json")),
    "world2": (Path("runs/e393_earned_label_worldseed2_iters20_20reps.json"),
               Path("runs/e395_earned_label_worldseed2_iters500_20reps.json")),
    "world3": (Path("runs/e393_earned_label_worldseed3_iters20_20reps.json"),
               Path("runs/e396_earned_label_worldseed3_iters500_20reps.json")),
    "world4": (Path("runs/e393_earned_label_worldseed4_iters20_20reps.json"),
               Path("runs/e396_earned_label_worldseed4_iters500_20reps.json")),
    "stream1": (Path("runs/e394_earned_label_stream1_iters20_20reps.json"),
                Path("runs/e403_earned_label_stream1_iters500_20reps.json")),
    "stream2": (Path("runs/e394_earned_label_stream2_iters20_20reps.json"),
                Path("runs/e403_earned_label_stream2_iters500_20reps.json")),
}
KIND = {"card": "card", "cue1": "cue", "cue3": "cue", "cue6": "cue", "cue9": "cue", "cue14": "cue",
        "world1": "world", "world2": "world", "world3": "world", "world4": "world",
        "stream1": "stream", "stream2": "stream"}
#: the third stream is rolled at twenty updates and has no five-hundred-update partner, so it is read beside the pair
UNPAIRED = Path("runs/e394_earned_label_stream3_iters20_20reps.json")
NEAR, FAR = "20", "500"
ARMS = ("naive", "replay")
N_TASKS = 3
OLDEST, MIDDLE, NEWEST = 0, 1, 2
MIN_CELLS = 10
MIN_KINDS = 3
MIN_REPS = 20
NEAR_BAR = 0.10
NEAR_LIMIT = 0.20
FAR_BAR = 0.20
FAR_FIRES = 0.10
COVERAGE_NEAR = 1.0
COVERAGE_FAR = 5.0
COVERAGE_FIRES = 2.0
CLAIMS = (
    ("AV1", f"and the paired ledger is carried, over at least {MIN_CELLS} cells and {MIN_KINDS} kinds",
     "At least ten cells carrying both budgets, both arms at twenty replicates, over at least three kinds of redraw",
     "falsifier: fewer cells, a missing budget, fewer replicates or fewer kinds"),
    ("AV2", "and at twenty updates the newest task is not systematically cost",
     "Among the cells at twenty updates the task-2 gain takes both signs",
     "falsifier: one sign only"),
    ("AV3", "and at five hundred it is cost in every one",
     "Every cell's task-2 gain at five hundred is below zero",
     "falsifier: any at or above zero"),
    ("AV4", f"and the recovery is a tenth of it at twenty and a fifth at five hundred",
     "Every cell's task-0 gain is at most 0.10 at twenty updates and at least 0.20 at five hundred",
     f"falsifier: any cell above {NEAR_LIMIT:.2f} at twenty or below {FAR_FIRES:.2f} at five hundred; null: between"),
    ("AV5", f"and the coverage is under one at twenty and over five at five hundred",
     "The least cell's two older gains over its newest loss is below 1.0 at twenty and above 5.0 at five hundred",
     f"falsifier: the least at twenty at or above {COVERAGE_FIRES:.1f}, or the least at five hundred at or below "
     f"{COVERAGE_FIRES:.1f}"),
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


def _end(path: Path) -> dict | None:
    doc = load(path)
    if not doc:
        return None
    reps = {}
    for arm in ARMS:
        got = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
        if not got:
            return None
        reps[arm] = got
    naive = _per_task(reps["naive"], "final_per_task")
    replay = _per_task(reps["replay"], "final_per_task")
    gains = [replay[k] - naive[k] for k in range(N_TASKS)]
    older = gains[OLDEST] + gains[MIDDLE]
    loss = -gains[NEWEST]
    return {"artifact": path.name, "replicates": min(len(reps["naive"]), len(reps["replay"])),
            "naive_final": naive, "replay_final": replay, "gain": gains, "newest_loss": loss,
            "coverage": (older / loss) if loss > 0 else None}


def reading(runs: dict = RUNS, unpaired: Path = UNPAIRED) -> dict:
    out = {"ok": True, "reason": None, "cells": {}, "kinds": {}, "unpaired": None}
    for name, (near, far) in runs.items():
        a, b = _end(near), _end(far)
        if a is None:
            return {**out, "ok": False, "reason": f"cell {name}: {near} is absent or carries no arm"}
        if b is None:
            return {**out, "ok": False, "reason": f"cell {name}: {far} is absent or carries no arm"}
        out["cells"][name] = {"kind": KIND.get(name, "?"), NEAR: a, FAR: b}
        out["kinds"].setdefault(KIND.get(name, "?"), []).append(name)
    lone = _end(unpaired)
    out["unpaired"] = ({"artifact": unpaired.name, "gain": lone["gain"], "coverage": lone["coverage"]}
                       if lone else None)
    near = [c[NEAR]["gain"][NEWEST] for c in out["cells"].values()]
    far = [c[FAR]["gain"][NEWEST] for c in out["cells"].values()]
    near_cov = [c[NEAR]["coverage"] for c in out["cells"].values() if c[NEAR]["coverage"] is not None]
    far_cov = [c[FAR]["coverage"] for c in out["cells"].values() if c[FAR]["coverage"] is not None]
    out["spans"] = {"cells": len(out["cells"]), "kinds": sorted(out["kinds"]),
                    "near_negative": sum(1 for x in near if x < 0), "near_positive": sum(1 for x in near if x > 0),
                    "far_negative": sum(1 for x in far if x < 0),
                    "near_oldest_max": max(c[NEAR]["gain"][OLDEST] for c in out["cells"].values()),
                    "far_oldest_min": min(c[FAR]["gain"][OLDEST] for c in out["cells"].values()),
                    #: a cell whose newest task is not cost has no loss to cover, so it does not bound the least
                    "near_coverage_min": min(near_cov) if near_cov else None,
                    "near_without_loss": len(out["cells"]) - len(near_cov),
                    "far_coverage_min": min(far_cov) if far_cov else None,
                    "replicates": sorted({c[e]["replicates"] for c in out["cells"].values() for e in (NEAR, FAR)})}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a cell's run or an arm is absent"}
                for c in CLAIMS]
    cells, s = r["cells"], r["spans"]
    thin = {n: {e: c[e]["replicates"] for e in (NEAR, FAR)} for n, c in cells.items()
            if any(c[e]["replicates"] < MIN_REPS for e in (NEAR, FAR))}
    j1 = {"id": "AV1",
          "measured": f"{len(cells)} cells paired at both budgets, {s['replicates']} replicates on both arms, over "
                      f"{len(s['kinds'])} kinds of redraw: { {k: len(v) for k, v in sorted(r['kinds'].items())} }",
          "verdict": f"MET -- the paired ledger is carried over {len(cells)} cells and {len(s['kinds'])} kinds" if
                     (len(cells) >= MIN_CELLS and len(s["kinds"]) >= MIN_KINDS and not thin) else
                     f"FALSIFIER FIRED -- {len(cells)} cells, {len(s['kinds'])} kinds, thin {thin}"}
    near = {n: c[NEAR]["gain"][NEWEST] for n, c in cells.items()}
    j2 = {"id": "AV2",
          "measured": f"at twenty updates the task-2 gains take {s['near_negative']} negative and "
                      f"{s['near_positive']} positive signs: "
                      f"{ {n: round(v, 4) for n, v in sorted(near.items(), key=lambda kv: kv[1])} }",
          "verdict": "MET -- the newest task is not systematically cost at twenty updates" if
                     (s["near_negative"] and s["near_positive"]) else
                     f"FALSIFIER FIRED -- one sign only at twenty updates"}
    far = {n: c[FAR]["gain"][NEWEST] for n, c in cells.items()}
    j3 = {"id": "AV3",
          "measured": f"at five hundred the task-2 gains are "
                      f"{ {n: round(v, 4) for n, v in sorted(far.items(), key=lambda kv: -kv[1])} }",
          "verdict": f"MET -- the newest task is cost in every one of the {len(cells)} cells at five hundred" if
                     s["far_negative"] == len(cells) else
                     f"FALSIFIER FIRED -- {len(cells) - s['far_negative']} cell(s) at or above zero"}
    over_near = {n: c[NEAR]["gain"][OLDEST] for n, c in cells.items() if c[NEAR]["gain"][OLDEST] > NEAR_BAR}
    under_far = {n: c[FAR]["gain"][OLDEST] for n, c in cells.items() if c[FAR]["gain"][OLDEST] < FAR_BAR}
    j4 = {"id": "AV4",
          "measured": f"the task-0 gain is at most {s['near_oldest_max']:+.4f} at twenty updates and at least "
                      f"{s['far_oldest_min']:+.4f} at five hundred, over the same cells",
          "verdict": f"MET -- at twenty the recovery is at most {s['near_oldest_max']:+.4f} and at five hundred at "
                     f"least {s['far_oldest_min']:+.4f}" if (not over_near and not under_far) else
                     f"FALSIFIER FIRED -- over the near bar {over_near}, under the far bar {under_far}" if
                     (over_near or under_far) and (s["near_oldest_max"] > NEAR_LIMIT
                                                   or s["far_oldest_min"] < FAR_FIRES) else
                     f"NULL -- {s['near_oldest_max']:+.4f} near and {s['far_oldest_min']:+.4f} far, between the bars"}
    nc, fc = s["near_coverage_min"], s["far_coverage_min"]
    nc_said = "none" if nc is None else format(nc, ".2f")
    fc_said = "none" if fc is None else format(fc, ".2f")
    lossless = s.get("near_without_loss", 0)
    j5 = {"id": "AV5",
          "measured": f"the least coverage is {nc_said} at twenty updates ({lossless} cell(s) losing nothing there) "
                      f"and {fc_said} at five hundred",
          "verdict": f"MET -- the least coverage is {nc:.2f} at twenty and {fc:.2f} at five hundred" if
                     (nc is not None and fc is not None and nc < COVERAGE_NEAR and fc > COVERAGE_FAR) else
                     f"FALSIFIER FIRED -- {nc_said} at twenty and {fc_said} at five hundred" if
                     (nc is None or fc is None or nc >= COVERAGE_FIRES or fc <= COVERAGE_FIRES) else
                     f"NULL -- {nc:.2f} and {fc:.2f}, between the bars"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the trade turns on ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a cell is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the same twelve cells at twenty updates and at five hundred, twenty replicates each")
    print(f"\n   {'cell':>8} {'kind':>7} {'gain 0/1/2 at 20':>26} {'coverage':>9} | {'gain 0/1/2 at 500':>26} "
          f"{'coverage':>9}")
    def _cov(x):
        return "none" if x is None else format(x, ".2f")
    for n in sorted(r["cells"], key=lambda x: r["cells"][x][FAR]["gain"][NEWEST]):
        c = r["cells"][n]
        a, b = c[NEAR], c[FAR]
        print(f"   {n:>8} {c['kind']:>7} " + " ".join(f"{x:+.4f}" for x in a["gain"]) + f" {_cov(a['coverage']):>9} | "
              + " ".join(f"{x:+.4f}" for x in b["gain"]) + f" {_cov(b['coverage']):>9}")
    s = r["spans"]
    print(f"\n   {s['cells']} cells over {s['kinds']}: at twenty the newest task is cost in {s['near_negative']} and "
          f"gains in {s['near_positive']}, the oldest gains at most {s['near_oldest_max']:+.4f}, the least coverage "
          f"{'none over ' + str(s.get('near_without_loss')) + ' lossless cell(s)' if s['near_coverage_min'] is None else format(s['near_coverage_min'], '.2f')}; "
          f"at five hundred it is cost in {s['far_negative']} of {s['cells']}, the "
          f"oldest gains at least {s['far_oldest_min']:+.4f}, the least coverage "
          f"{'none' if s['far_coverage_min'] is None else format(s['far_coverage_min'], '.2f')}")
    if r.get("unpaired"):
        u = r["unpaired"]
        print(f"   and the unpaired third stream at twenty updates: gains "
              f"{[round(x, 4) for x in u['gain']]}, coverage "
              f"{'none' if u['coverage'] is None else format(u['coverage'], '.2f')}")
    print("\n== the registered claims, AV1-AV5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e420` found the trade's direction constant across the far-point draws and `e412` found the aid")
    print("    turning on between twenty and forty-five updates; the corpus rolled both ends of the same cells)")
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
