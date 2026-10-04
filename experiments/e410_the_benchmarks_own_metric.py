"""E410 -- the benchmark's own metric: the retention on the six worlds, and it does not follow the world's reading.

The redraw series has measured one thing for thirteen units: the **world's** reading of task 0 by a linear probe --
the quantity `e396` put at **0.7729** on the card's world and 0.4625 to 0.5396 on the five that fail, and the
quantity the second revision of the card carries. What a **continual-learning** benchmark scores is a different pair:
the accuracy the trained head reaches on each task and how much of each it gives back. Every 500-update artifact in
this line carries that too -- the retention matrix, the per-task final accuracies and the per-task forgetting, over
twenty replicates -- and no unit has read it. **This unit does, on all six worlds, and trains nothing.**

Five claims, registered before any retention matrix was read.

- **AO1 -- and the matrices are carried.** Each of the six worlds' 500-update runs carries, for the `naive` arm,
  **twenty** replicates with a three-by-three retention matrix and the per-task final accuracies. **Falsifier**: any
  world missing one; **Bound**: at least **5** worlds and at least **20** replicates each.
- **AO2 -- and the last task is kept by every world.** At task 3 the per-task forgetting is **zero** on every one of
  the six worlds, to a thousandth. **Falsifier**: any world forgetting the last task.
- **AO3 -- and the first task is lost by every world.** At task 1 the per-task forgetting is at least **0.30** on
  every one of the six. **Falsifier**: any world below **0.20**, which would say the first task survives somewhere.
  **Null**: between.
- **AO4 -- and the card's world is not the benchmark's best.** Its mean final accuracy over the three tasks is **not**
  the largest of the six. **Falsifier**: it is. *The card's world is the one whose task-0 world reading recovers, the
  one the whole redraw series has been about; a benchmark that scored it would have it first, and a benchmark that
  scores retention need not.*
- **AO5 -- and the world's reading does not track the retention.** The rank correlation over the six worlds between
  the far-point **task-0 world reading** and the **final accuracy** over the three tasks has an absolute value of at
  most **0.5**. **Falsifier**: above **0.7**, which would say the quantity this line has been measuring is the
  benchmark's. **Null**: between.

**What it can do beyond that.** It puts the line's own instrument beside the benchmark's own metric for the first
time: thirteen units have been measuring what a probe can recover from the world's eight numbers, and this asks
whether that is what a continual-learning benchmark scores -- and, if it is not, what the six worlds' retention looks
like instead.

**What it cannot do.** *One arm and one rate*: the 3e-3 `naive` bodies only, and the `replay` arm's own retention is
in the same artifacts and is not read here. *And the metric is the corpus's*: `mean_forgetting` is the retention
matrix's diagonal minus its last row, which `e305` showed cannot see the part an arm never learned -- so "retention"
here is the corpus's own decomposition and not a mechanism. *And six worlds are six*: the four engine redraws are not
in the set. *And a probe is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: the six worlds' 500-update runs, and the far-point task-0 world reading each one carries (`e396`)
RUNS = {
    "card": (Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), 0.7729),
    "cue1": (Path("runs/e398_earned_label_cueseed1_iters500_20reps.json"), 0.5062),
    "cue3": (Path("runs/e398_earned_label_cueseed3_iters500_20reps.json"), 0.5240),
    "cue6": (Path("runs/e401_earned_label_cueseed6_iters500_20reps.json"), 0.4792),
    "cue9": (Path("runs/e399_earned_label_cueseed9_iters500_20reps.json"), 0.4625),
    "cue14": (Path("runs/e399_earned_label_cueseed14_iters500_20reps.json"), 0.5396),
}
ARM = "naive"
N_TASKS = 3
MIN_WORLDS = 5
MIN_REPS = 20
KEPT = 0.001
LOST = 0.30
LOST_FIRES = 0.20
TRACKS = 0.5
TRACKS_FIRES = 0.7
CLAIMS = (
    ("AO1", f"and the matrices are carried, over at least {MIN_WORLDS} worlds and {MIN_REPS} replicates",
     "Each of the six worlds' 500-update runs carries twenty replicates with a three-by-three retention matrix and "
     "the per-task final accuracies, for the `naive` arm",
     "falsifier: any world missing one"),
    ("AO2", "and the last task is kept by every world",
     "At task 3 the per-task forgetting is zero on every one of the six worlds, to a thousandth",
     "falsifier: any world forgetting the last task"),
    ("AO3", f"and the first task is lost by every world, by {LOST:.2f}",
     "At task 1 the per-task forgetting is at least 0.30 on every one of the six",
     f"falsifier: any world below {LOST_FIRES:.2f}; null: between"),
    ("AO4", "and the card's world is not the benchmark's best",
     "Its mean final accuracy over the three tasks is not the largest of the six",
     "falsifier: it is"),
    ("AO5", f"and the world's reading does not track the retention, within {TRACKS:.1f}",
     "The rank correlation over the six worlds between the far-point task-0 world reading and the final accuracy has "
     "an absolute value of at most 0.5",
     f"falsifier: above {TRACKS_FIRES:.1f}; null: between"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    for r, i in enumerate(order):
        ranks[i] = float(r)
    return ranks


def _spearman(a: list[float], b: list[float]) -> float:
    ra, rb = _rank(a), _rank(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def reading(runs: dict = RUNS, arm: str = ARM) -> dict:
    out = {"ok": True, "reason": None, "worlds": {}, "arm": arm}
    for name, (path, world_reading) in runs.items():
        doc = load(path)
        if not doc:
            return {**out, "ok": False, "reason": f"world {name}: {path} is absent"}
        reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
        if not reps:
            return {**out, "ok": False, "reason": f"world {name}: the {arm} arm carries no replicates"}
        matrices = [r.get("retention") for r in reps]
        complete = [m for m in matrices if m and len(m) == N_TASKS and all(len(row) == N_TASKS for row in m)]
        if not complete:
            return {**out, "ok": False, "reason": f"world {name}: no replicate carries a three-by-three matrix"}
        learned = [statistics.fmean([r["learned"][k] for r in reps]) for k in range(N_TASKS)]
        final = [statistics.fmean([r["final_per_task"][k] for r in reps]) for k in range(N_TASKS)]
        forget = [statistics.fmean([r["forgetting_per_task"][k] for r in reps]) for k in range(N_TASKS)]
        out["worlds"][name] = {
            "artifact": path.name, "replicates": len(reps), "matrices": len(complete),
            "world_reading_task_0": world_reading,
            "learned": learned, "final": final, "forgetting": forget,
            "mean_forgetting": statistics.fmean([r["mean_forgetting"] for r in reps]),
            "final_accuracy": statistics.fmean([r["final_accuracy"] for r in reps]),
        }
    names = list(out["worlds"])
    out["correlation_reading_vs_accuracy"] = _spearman(
        [out["worlds"][n]["world_reading_task_0"] for n in names],
        [out["worlds"][n]["final_accuracy"] for n in names])
    out["spread"] = {
        "final_accuracy": max(out["worlds"][n]["final_accuracy"] for n in names)
        - min(out["worlds"][n]["final_accuracy"] for n in names),
        "mean_forgetting": max(out["worlds"][n]["mean_forgetting"] for n in names)
        - min(out["worlds"][n]["mean_forgetting"] for n in names)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a world's run or its matrices is absent"}
                for c in CLAIMS]
    worlds = r["worlds"]
    short = {n: {"reps": w["replicates"], "matrices": w["matrices"]} for n, w in worlds.items()
             if w["replicates"] < MIN_REPS or w["matrices"] < MIN_REPS}
    j1 = {"id": "AO1", "measured": f"{len(worlds)} worlds, each carrying {sorted({w['replicates'] for w in worlds.values()})} "
                                  f"replicates and {sorted({w['matrices'] for w in worlds.values()})} three-by-three "
                                  f"matrices for the `{r['arm']}` arm",
          "verdict": f"MET -- the matrices are carried on all {len(worlds)} worlds" if
                     (not short and len(worlds) >= MIN_WORLDS) else f"FALSIFIER FIRED -- {short}"}

    last = {n: w["forgetting"][2] for n, w in worlds.items()}
    bad2 = {n: round(v, 4) for n, v in last.items() if abs(v) > KEPT}
    j2 = {"id": "AO2", "measured": f"the per-task forgetting at task 3 is "
                                  f"{sorted({round(v, 4) for v in last.values()})} across the six worlds",
          "verdict": "MET -- every world keeps the last task" if not bad2 else
          f"FALSIFIER FIRED -- {bad2} forgets the last task"}

    first = {n: w["forgetting"][0] for n, w in worlds.items()}
    worst = min(first.values())
    j3 = {"id": "AO3", "measured": f"the per-task forgetting at task 1 is "
                                  f"{ {n: round(v, 4) for n, v in sorted(first.items())} }, the least {worst:.4f}",
          "verdict": f"MET -- every world loses the first task, the least by {worst:.4f}" if worst >= LOST else
          f"FALSIFIER FIRED -- {worst:.4f} is below the bar" if worst < LOST_FIRES else
          f"NULL -- {worst:.4f}, between {LOST_FIRES:.2f} and {LOST:.2f}"}

    acc = {n: w["final_accuracy"] for n, w in worlds.items()}
    top = max(acc, key=lambda n: acc[n])
    j4 = {"id": "AO4", "measured": f"the final accuracies are "
                                  f"{ {n: round(v, 4) for n, v in sorted(acc.items(), key=lambda kv: -kv[1])} }",
          "verdict": "MET -- the card's world is not the benchmark's best" if top != "card" else
          f"FALSIFIER FIRED -- the card's world is the best of the six on the benchmark's own metric"}

    rho = r["correlation_reading_vs_accuracy"]
    j5 = {"id": "AO5", "measured": f"the rank correlation between the task-0 world reading and the final accuracy over "
                                  f"the six worlds is {rho:+.3f}, and the spreads are {r['spread']}",
          "verdict": f"MET -- the world's reading does not track the retention, {rho:+.3f}" if abs(rho) <= TRACKS else
          f"FALSIFIER FIRED -- {rho:+.3f}: the quantity this line measures is the benchmark's" if abs(rho) > TRACKS_FIRES
          else f"NULL -- {rho:+.3f}, between {TRACKS:.1f} and {TRACKS_FIRES:.1f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the benchmark's own metric ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the benchmark's own metric ==")
    print(f"   the retention the `{r['arm']}` arm reaches by 500 updates on the six worlds, and the world's reading the"
          f" redraw series measured")
    print(f"\n   {'world':>7} {'t0 reading':>11} {'learned (3)':>28} {'final (3)':>28} {'forget (3)':>28} "
          f"{'meanf':>7} {'finacc':>7}")
    for n in sorted(r["worlds"], key=lambda x: -r["worlds"][x]["final_accuracy"]):
        w = r["worlds"][n]
        f = lambda v: [round(x, 3) for x in v]  # noqa: E731
        print(f"   {n:>7} {w['world_reading_task_0']:11.4f} {str(f(w['learned'])):>28} {str(f(w['final'])):>28} "
              f"{str(f(w['forgetting'])):>28} {w['mean_forgetting']:7.4f} {w['final_accuracy']:7.4f}")

    print("\n== the registered claims, AO1-AO5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (thirteen units have measured what a probe recovers from the world's eight numbers; this asks what a")
    print("    continual-learning benchmark scores, from the retention matrices the same runs already carry)")
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
