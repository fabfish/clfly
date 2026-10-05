"""E420 -- the trade is a constant of the protocol: the newest task is cost on every one of the twelve draws.

`e419` read the two arms' per-task ledger on six worlds at five hundred updates and found the buffer buying the two
older tasks and paying with the newest, covering the loss five to twelve times over. It registered its own scope: *six
worlds*, one kind of redraw. The corpus holds more: four engine **world** redraws, two clean training **streams** and
five **cue**-population redraws, all of the earned-label world at five hundred updates and twenty replicates, all
carrying both arms.

**This unit reads all twelve.** Every cell's three per-task gains, each paired over its own twenty seeds with a
standard error, the two older gains against the newest loss, and the loss against the gain it is bought with. No
training, no probe. Five claims, registered before this unit's pass over the runs.

- **AU1 -- and the twelve cells are carried, over three kinds of redraw.** At least **10** cells, each with both arms
  at **20** replicates, covering at least **3** kinds of redraw (a world, a stream and a cue population). **Falsifier**:
  fewer cells, fewer replicates, or fewer kinds.
- **AU2 -- and the newest task is cost in every cell.** Every cell's task-2 final-accuracy gain is **below zero**.
  **Falsifier**: any cell at or above zero. *This is the unit's own prediction: the trade is a property of the
  protocol's order, so no draw the corpus varies reverses it.*
- **AU3 -- and the oldest task is recovered in every cell.** Every cell's task-0 gain is at least **0.20** and
  resolved at **5 sigma** over its own twenty seeds. **Falsifier**: any below **0.10**; **null**: between.
- **AU4 -- and the two older gains cover the newest loss.** In every cell the sum of the task-0 and task-1 gains is at
  least **four times** the task-2 loss. **Falsifier**: any below **twice**; **null**: between.
- **AU5 -- and the loss is small against the gain that pays for it.** In every cell the newest loss is at most **half**
  the oldest gain. **Falsifier**: any above **three quarters**.

**What it can do beyond that.** It says the one thing in this line that does not move with the draw. The six worlds'
task-0 readings span **0.3104** at the far point and their final accuracies span 0.0309; the aid's gain spans 0.0264.
Across twelve cells of three kinds of redraw the newest task is cost **every time**, by **-0.0115** to **-0.1031**,
while the oldest is recovered by +0.2333 to +0.3219, so the direction of the trade is a constant of the protocol and
the sizes are the draw's.

**What it cannot do.** *One order and one arm pair*: the corpus's three tasks in the as-built order, `naive` and
`replay`, at five hundred updates, so whether the trade's direction survives a reversed order is `e317`'s axis and not
this one. *And one cell is not resolved*: the smallest loss, **-0.0115**, is reported with its own sigma and the
claim's bar is its sign rather than a resolved difference. *And the cells overlap*: the card's world is also a cue
draw, so the twelve are not independent samples of the protocol. *And the metric is the corpus's*: the loss is a
`learned` loss as much as a forgetting one, since the last task is never forgotten after it is taught. *And a ledger
is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the twelve far-point cells, by the kind of redraw each moves
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
KIND = {"card": "card", "world1": "world", "world2": "world", "world3": "world", "world4": "world",
        "stream1": "stream", "stream2": "stream", "cue1": "cue", "cue3": "cue", "cue6": "cue", "cue9": "cue",
        "cue14": "cue"}
ARMS = ("naive", "replay")
N_TASKS = 3
OLDEST, MIDDLE, NEWEST = 0, 1, 2
MIN_CELLS = 10
MIN_KINDS = 3
MIN_REPS = 20
RECOVERY = 0.20
RECOVERY_FIRES = 0.10
RECOVERY_SIGMA = 5.0
RATIO = 4.0
RATIO_FIRES = 2.0
SHARE = 0.5
SHARE_FIRES = 0.75
CLAIMS = (
    ("AU1", f"and the twelve cells are carried, over at least {MIN_KINDS} kinds of redraw",
     "At least ten cells, each with both arms at twenty replicates, covering at least three kinds of redraw",
     "falsifier: fewer cells, fewer replicates, or fewer kinds"),
    ("AU2", "and the newest task is cost in every cell",
     "Every cell's task-2 final-accuracy gain is below zero",
     "falsifier: any cell at or above zero"),
    ("AU3", f"and the oldest task is recovered in every cell, {RECOVERY:.2f} at {RECOVERY_SIGMA:.0f} sigma",
     "Every cell's task-0 gain is at least 0.20 and resolved at 5 sigma over its own twenty seeds",
     f"falsifier: any below {RECOVERY_FIRES:.2f}; null: between"),
    ("AU4", f"and the two older gains cover the newest loss, {RATIO:.1f} times",
     "In every cell the sum of the task-0 and task-1 gains is at least four times the task-2 loss",
     f"falsifier: any below {RATIO_FIRES:.1f}; null: between"),
    ("AU5", f"and the loss is at most half the gain that pays for it",
     "In every cell the newest loss is at most half the oldest gain",
     f"falsifier: any above {SHARE_FIRES:.2f}"),
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


def _paired(naive_reps, replay_reps, key) -> list[dict]:
    out = []
    for k in range(N_TASKS):
        dif = [b[key][k] - a[key][k] for a, b in zip(naive_reps, replay_reps)]
        mean = statistics.fmean(dif)
        se = statistics.stdev(dif) / len(dif) ** 0.5 if len(dif) > 1 else float("nan")
        out.append({"gain": mean, "se": se, "sigma": (mean / se if se else float("nan"))})
    return out


def reading(runs: dict = RUNS) -> dict:
    out = {"ok": True, "reason": None, "cells": {}, "kinds": {}}
    for name, path in runs.items():
        doc = load(path)
        if not doc:
            return {**out, "ok": False, "reason": f"cell {name}: {path} is absent"}
        reps = {}
        for arm in ARMS:
            got = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
            if not got:
                return {**out, "ok": False, "reason": f"cell {name}: the {arm} arm carries no replicates"}
            reps[arm] = got
        paired = _paired(reps["naive"], reps["replay"], "final_per_task")
        gains = [p["gain"] for p in paired]
        entry = {"artifact": path.name, "kind": KIND.get(name, "?"), "name": name,
                 "replicates": min(len(reps["naive"]), len(reps["replay"])),
                 "naive_final": _per_task(reps["naive"], "final_per_task"),
                 "replay_final": _per_task(reps["replay"], "final_per_task"),
                 "gain": gains, "se": [p["se"] for p in paired], "sigma": [p["sigma"] for p in paired]}
        older = gains[OLDEST] + gains[MIDDLE]
        entry["newest_loss"] = -gains[NEWEST]
        entry["coverage"] = older / entry["newest_loss"] if entry["newest_loss"] > 0 else float("inf")
        entry["share"] = entry["newest_loss"] / gains[OLDEST] if gains[OLDEST] > 0 else float("inf")
        out["cells"][name] = entry
        out["kinds"].setdefault(entry["kind"], []).append(name)
    out["spans"] = {"cells": len(out["cells"]), "kinds": sorted(out["kinds"]),
                    "replicates": sorted({c["replicates"] for c in out["cells"].values()}),
                    "least_oldest": min(c["gain"][OLDEST] for c in out["cells"].values()),
                    "worst_newest": max(c["gain"][NEWEST] for c in out["cells"].values()),
                    "largest_loss": max(c["newest_loss"] for c in out["cells"].values()),
                    "least_coverage": min(c["coverage"] for c in out["cells"].values()),
                    "largest_share": max(c["share"] for c in out["cells"].values()),
                    "weakest_sigma": min(c["sigma"][OLDEST] for c in out["cells"].values())}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a cell's run or an arm is absent"}
                for c in CLAIMS]
    cells = r["cells"]
    thin = {n: c["replicates"] for n, c in cells.items() if c["replicates"] < MIN_REPS}
    kinds = sorted(r["kinds"])
    j1 = {"id": "AU1",
          "measured": f"{len(cells)} cells at {r['spans']['replicates']} replicates over {len(kinds)} kinds of "
                      f"redraw: { {k: len(v) for k, v in sorted(r['kinds'].items())} }",
          "verdict": f"MET -- the {len(cells)} cells are carried over {len(kinds)} kinds of redraw" if
                     (len(cells) >= MIN_CELLS and len(kinds) >= MIN_KINDS and not thin) else
                     f"FALSIFIER FIRED -- {len(cells)} cells, {len(kinds)} kinds, thin {thin}"}
    new = {n: c["gain"][NEWEST] for n, c in cells.items()}
    worst = max(new.values())
    j2 = {"id": "AU2",
          "measured": f"the task-2 gains run "
                      f"{ {n: round(v, 4) for n, v in sorted(new.items(), key=lambda kv: -kv[1])} }",
          "verdict": f"MET -- the newest task is cost in every one of the {len(cells)} cells, the smallest loss "
                     f"{-worst:+.4f}" if worst < 0 else
                     f"FALSIFIER FIRED -- {worst:+.4f} is not a loss"}
    old = {n: c["gain"][OLDEST] for n, c in cells.items()}
    weak = {n: c["sigma"][OLDEST] for n, c in cells.items() if c["sigma"][OLDEST] < RECOVERY_SIGMA}
    least_old = min(old.values())
    good3 = least_old >= RECOVERY and not weak
    j3 = {"id": "AU3",
          "measured": f"the task-0 gains run "
                      f"{ {n: round(v, 4) for n, v in sorted(old.items(), key=lambda kv: kv[1])} }, the weakest "
                      f"resolved at {r['spans']['weakest_sigma']:.2f} sigma",
          "verdict": f"MET -- the oldest task is recovered by {least_old:+.4f} at the least, every cell above "
                     f"{RECOVERY_SIGMA:.0f} sigma" if good3 else
                     f"FALSIFIER FIRED -- {least_old:+.4f} is under the bar" if least_old < RECOVERY_FIRES else
                     f"NULL -- {least_old:+.4f} between the bars, unresolved at {sorted(weak)[:3]}"}
    cov = {n: round(c["coverage"], 2) for n, c in cells.items()}
    least_cov = min(cov.values())
    j4 = {"id": "AU4",
          "measured": f"the coverage ratios run {dict(sorted(cov.items(), key=lambda kv: kv[1]))}, the least "
                      f"{least_cov:.2f} times",
          "verdict": f"MET -- the two older gains cover the newest loss by {least_cov:.2f} times at the least" if
                     least_cov >= RATIO else
                     f"FALSIFIER FIRED -- {least_cov:.2f} is under the bar" if least_cov < RATIO_FIRES else
                     f"NULL -- {least_cov:.2f}, between {RATIO_FIRES:.1f} and {RATIO:.1f}"}
    share = {n: round(c["share"], 3) for n, c in cells.items()}
    largest = max(share.values())
    j5 = {"id": "AU5",
          "measured": f"the loss over the oldest gain runs {dict(sorted(share.items(), key=lambda kv: -kv[1]))}, the "
                      f"largest {largest:.3f}",
          "verdict": f"MET -- the loss is at most {largest:.3f} of the gain that pays for it, under half" if
                     largest <= SHARE else
                     f"FALSIFIER FIRED -- {largest:.3f} is over the bar" if largest > SHARE_FIRES else
                     f"NULL -- {largest:.3f}, between {SHARE:.2f} and {SHARE_FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the trade is a constant of the protocol ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'a cell is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   the twelve far-point cells at five hundred updates, twenty replicates, per-task gains each paired over")
    print("   that cell's own twenty seeds")
    print(f"\n   {'cell':>8} {'kind':>7} {'naive 0/1/2':>26} {'replay 0/1/2':>26} {'gain 0/1/2':>26} "
          f"{'cover':>6} {'loss/gain0':>10}")
    for n in sorted(r["cells"], key=lambda x: r["cells"][x]["gain"][NEWEST]):
        c = r["cells"][n]
        print(f"   {n:>8} {c['kind']:>7} " + " ".join(f"{x:.4f}" for x in c["naive_final"]) + "  "
              + " ".join(f"{x:.4f}" for x in c["replay_final"]) + "  "
              + " ".join(f"{x:+.4f}" for x in c["gain"]) + f" {c['coverage']:6.2f} {c['share']:10.3f}")
    s = r["spans"]
    print(f"\n   {s['cells']} cells over {s['kinds']}, the least task-0 gain {s['least_oldest']:+.4f}, the worst "
          f"task-2 gain {s['worst_newest']:+.4f}, the largest loss {s['largest_loss']:.4f}, the least coverage "
          f"{s['least_coverage']:.2f}, the largest loss-over-gain {s['largest_share']:.3f}, the weakest sigma "
          f"{s['weakest_sigma']:.2f}")
    print("\n== the registered claims, AU1-AU5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e419` read the trade on six worlds and registered that it is six worlds; the corpus also holds four")
    print("    engine world redraws and two clean streams, and this reads all twelve cells)")
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
