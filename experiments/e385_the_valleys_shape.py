"""E385 -- the valley's shape: the wide step's dip resolved to three more budgets.

`e384` sampled the wide step's first task at five budgets and found the series is not the rise its claim predicted
but a **valley**: the connectome's own weights carry task 0 at **0.6875**, one update leaves **0.6792** (a loss of
**0.0083**), five updates leave **0.5500** (a loss of **0.1375**, **16.6** times as much), and by five hundred it
has climbed to **0.7792**, above where it started. It registered what that leaves: *"five budgets are five samples,
so the valley is bounded between one and five iterations and not located."*

**This unit locates it.** The same cell, the same rate and the same seed stream at budgets **2**, **3** and **4** --
three runs of five replicates, seconds each -- with `e384`'s own readings for 1, 5, 20, 100 and 500 read from its
artifact rather than rolled again, so the two units overlap at two budgets and the overlap is a check on both.

Five claims, registered before any of the new runs' readings was opened.

- **F1 -- one configuration, and the overlap agrees.** Each new run agrees with `e384`'s budget-1 run on every
  recorded field including the learning rate and the batch, differing in `iters` alone; and at the two budgets the
  units share, **1** and **5**, this unit's rolls reproduce `e384`'s readings within **0.02**. **Falsifier**: any
  other field differing, or an overlap apart by **0.05** or more, which would say the two units are not rolling one
  instrument.
- **F2 -- and the valley turns at a single step.** Over the seven budgets from 1 to 5 the series has exactly **one**
  minimum, reached at a budget below 5, with the readings strictly falling into it and strictly rising out of it.
  **Falsifier**: a flat region at the minimum, two budgets within **0.02** of each other there, which would say the
  dip is a plateau rather than a turn.
- **F3 -- and the dip is a tenth deep.** The minimum over those budgets is at least **0.10** below the reading at a
  budget of **1**. **Falsifier**: within **0.05**. **Null**: between.
- **F4 -- and the recovery has started by five.** The reading at a budget of **5** exceeds the minimum by at least
  **0.02**. **Falsifier**: within **0.01**, which would say the dip is still deepening at the last budget sampled.
  **Null**: between.
- **F5 -- and the dip happens while the head is unfitted.** At the budget where the minimum sits, the trained head
  reads no more than **0.10** above chance. **Falsifier**: the head above that, which would say the world dips while
  the head is already steering -- the mechanism `e384` reported, that the training's work at this end is fitting the
  head, would then be wrong.

**What it can do beyond that.** With `e384` it turns the wide step's first task into a **trajectory**: where the
world is at each of seven budgets, against what the connectome already carried and against what the head can read.
The tight end has no such shape -- one update and it is at the floor -- so this is the only one of the two ends where
a trajectory exists to resolve.

**What it cannot do.** *Seven budgets are seven samples*: the shape between them is not measured, so a turn between 2
and 3 is bounded and not located, and one inside a single update is invisible. *And a smaller budget is a different
run*: the batch order, the head's fitting and any schedule depend on how many steps were taken. *One cell and one
draw*: the action source at `cue@0`, so the cue source and the tight end are not resolved this way. *And a probe is
not a mechanism*: a reading says how much of the label a linear fit recovers from the world's eight numbers, so the
valley is a shape in what is recoverable and not a named process.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e379_what_the_body_did import N_TASKS, NAIVE, TAU  # noqa: F401  (the same instrument)
from experiments.e380_what_the_training_built import setup as setup_wide
from experiments.e382_when_the_world_loses_it import SWEEP_REPS, one_budget
from experiments.e383_the_collapse_at_two_step_sizes import SMALL

#: the budgets this unit adds, and the artifact whose series they join
#: the three budgets inside the valley, and the two the previous series already holds, rolled again so
#: the overlap is a measurement of two instruments rather than of one artifact against itself
NEW = (1, 2, 3, 4, 5)
SHARED_WITH = (1, 5)
PREVIOUS = Path("runs/e384_the_other_end_of_the_window.json")
RUNS = {b: {"run": Path(f"runs/e385_earned_label_iters{b}_cue0_actionsource_5reps.json"),
            "theta": Path(f"runs/e385_theta_{b}")} for b in NEW}
SAME = 0.02
FIRES = 0.05
DEEP = 0.10
STARTED = 0.02
FLAT = 0.01
STABLE = 0.02
UNFITTED = 0.10
CLAIMS = (
    ("F1", f"one configuration, and the overlap agrees within {SAME:.2f}",
     "Each new run differs from `e384`'s budget-1 run in `iters` alone, and at the two shared budgets the rolls "
     "reproduce that unit's readings within 0.02",
     f"falsifier: any other field differing, or an overlap {FIRES:.2f} apart"),
    ("F2", "and the valley turns at a single step",
     "Over the budgets from 1 to 5 the series has exactly one minimum below 5, falling into it and rising out of it",
     f"falsifier: a flat region at the minimum, two budgets within {SAME:.2f} of each other there"),
    ("F3", f"and the dip is a tenth deep, by {DEEP:.2f}",
     "The minimum over those budgets is at least 0.10 below the reading at a budget of 1",
     f"falsifier: within {FIRES:.2f}; null: between {FIRES:.2f} and {DEEP:.2f}"),
    ("F4", f"and the recovery has started by five, by {STARTED:.2f}",
     "The reading at a budget of 5 exceeds the minimum by at least 0.02",
     f"falsifier: within {FLAT:.2f}; null: between {FLAT:.2f} and {STARTED:.2f}"),
    ("F5", f"and the dip happens while the head is unfitted, within {UNFITTED:.2f} of chance",
     "At the budget where the minimum sits, the trained head reads no more than 0.10 above chance",
     "falsifier: the head above that at the minimum's budget"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(runs: dict = RUNS, previous: Path = PREVIOUS, arm: str = NAIVE, reps: int = SWEEP_REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "budgets": {}, "facts": {}, "previous": None, "arm": arm, "reps": reps}
    for b, spec in runs.items():
        doc = load(spec["run"])
        if not doc:
            return {"ok": False, "budgets": {}, "facts": {}, "previous": None,
                    "reason": f"budget {b}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {"ok": False, "budgets": {}, "facts": {}, "previous": None,
                    "reason": f"budget {b}: {got['reason']}"}
        cell = got["cell"]
        out["budgets"][str(b)] = {"run": spec["run"].name, "iters": doc["config"].get("iters"),
                                  "probe_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                                  "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                                  "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["facts"][str(b)] = {**_facts(doc), "lr": doc["config"].get("lr"), "batch": doc["config"].get("batch")}
    prev = load(previous)
    if not prev:
        return {"ok": False, "budgets": {}, "facts": {}, "previous": None,
                "reason": f"{previous} is absent, so the series has no ends to join"}
    series = {int(k): v for k, v in (prev.get("budgets") or {}).items()}
    out["previous"] = {"artifact": Path(previous).name,
                       "readings": {str(b): float(v["probe_task_0"]) for b, v in series.items()},
                       "heads": {str(b): float(v.get("head_task_0", float("nan"))) for b, v in series.items()},
                       "facts": {str(b): v for b, v in ((prev.get("facts") or {}).items())}}
    return out


def _series(r: dict) -> dict:
    out = {}
    for b, v in ((r.get("previous") or {}).get("readings") or {}).items():
        out[int(b)] = float(v)
    for b, v in (r.get("budgets") or {}).items():
        out[int(b)] = float(v["probe_task_0"])
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run, its weights or the previous series is "
                                                        "absent"} for c in CLAIMS]
    bud = {int(k): v for k, v in r["budgets"].items()}
    keys = ("lr", "batch", "iters") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
    #: the reference is `e384`'s own budget-1 run, since that is the cell the new ones have to match
    pf = ((r.get("previous") or {}).get("facts") or {}).get("1") or {}
    differ = {}
    for b, entry in bud.items():
        facts = r["facts"][str(b)]
        differ[b] = {k: [facts.get(k), pf.get(k)] for k in keys if facts.get(k) != pf.get(k)}
    #: budget 1 is the reference itself, so its difference against itself is not a finding
    bad = {b: v for b, v in differ.items()
           if b != 1 and sorted(v) not in (["iters"], ["iters", "repeats"])}
    overlaps = {}
    for b in SHARED_WITH:
        prev = ((r.get("previous") or {}).get("readings") or {}).get(str(b))
        here = (r["budgets"].get(str(b)) or {}).get("probe_task_0")
        if prev is not None and here is not None:
            overlaps[b] = here - prev
    worst = max((abs(v) for v in overlaps.values()), default=0.0)
    j1 = {"id": "F1", "measured": f"each new run against `e384`'s budget-1 run: "
                                  f"{ {b: sorted(v) for b, v in differ.items()} }; and the shared budgets' rolls "
                                  f"against that unit's readings { {b: round(v, 4) for b, v in overlaps.items()} }",
          "verdict": "MET -- one configuration, and the overlap reproduces the previous series" if not bad and
                     worst < SAME else
          f"FALSIFIER FIRED -- {bad} differ beyond the budget, or the overlap is {worst:.4f} apart"}

    series = _series(r)
    window = {b: v for b, v in sorted(series.items()) if b <= 5}
    if len(window) < 3:
        j2 = {"id": "F2", "measured": "fewer than three of the budgets from 1 to 5 are available",
              "verdict": "REFUSED -- the window this claim is about is not sampled"}
    else:
        ordered = sorted(window)
        low = min(ordered, key=lambda b: window[b])
        flat = [b for b in ordered if b != low and abs(window[b] - window[low]) < SAME]
        falls = all(window[ordered[i]] >= window[ordered[i + 1]] for i in range(ordered.index(low)))
        rises = all(window[ordered[i]] <= window[ordered[i + 1]] for i in range(ordered.index(low), len(ordered) - 1))
        good = low < max(ordered) and not flat and falls and rises
        j2 = {"id": "F2", "measured": f"the readings over the budgets {ordered} are "
                                      f"{[round(window[b], 4) for b in ordered]}, with the minimum at {low} and "
                                      f"{flat} within {SAME:.2f} of it",
              "verdict": f"MET -- the valley turns at a single step, at {low}" if good else
              f"FALSIFIER FIRED -- the minimum is at {low} with {flat} within {SAME:.2f} of it, or the series does "
              f"not fall into it and rise out of it"}

    if low is None:
        j3 = {"id": "F3", "measured": "the window is not sampled", "verdict": "REFUSED -- no minimum to price"}
    else:
        depth = window[min(ordered)] - window[low]
        j3 = {"id": "F3", "measured": f"the minimum is {window[low]:.4f} at a budget of {low} and the reading at a "
                                      f"budget of {min(ordered)} is {window[min(ordered)]:.4f}, so the dip is "
                                      f"{depth:+.4f} deep",
              "verdict": f"MET -- the dip is a tenth deep, {depth:+.4f}" if depth >= DEEP else
              f"FALSIFIER FIRED -- only {depth:+.4f} deep: the dip is within {FIRES:.2f} of the start" if
              depth < FIRES else
              f"NULL -- {depth:+.4f}, between {FIRES:.2f} and {DEEP:.2f}"}

    if 5 not in window or low is None:
        j4 = {"id": "F4", "measured": "the budget of five or the minimum is missing",
              "verdict": "REFUSED -- the comparison this claim makes is not computable"}
    else:
        back = window[5] - window[low]
        j4 = {"id": "F4", "measured": f"the reading at a budget of 5 is {window[5]:.4f} against the minimum's "
                                      f"{window[low]:.4f}, so it has come back {back:+.4f}",
              "verdict": f"MET -- the recovery has started by five, {back:+.4f}" if back >= STARTED else
              f"FALSIFIER FIRED -- only {back:+.4f}: the dip is still deepening at the last budget sampled" if
              back < FLAT else f"NULL -- {back:+.4f}, between {FLAT:.2f} and {STARTED:.2f}"}

    heads = {int(k): float(v) for k, v in ((r.get("previous") or {}).get("heads") or {}).items()}
    heads.update({b: v["head_task_0"] for b, v in bud.items()})
    if low is None or low not in heads:
        j5 = {"id": "F5", "measured": "the head's reading at the minimum's budget is missing",
              "verdict": "REFUSED -- the comparison this claim makes is not computable"}
    else:
        above = heads[low] - 0.25
        j5 = {"id": "F5", "measured": f"at a budget of {low}, where the minimum sits, the trained head reads "
                                      f"{heads[low]:.4f} against a chance of 0.25, {above:+.4f} above it",
              "verdict": f"MET -- the dip happens while the head is unfitted, {above:+.4f} over chance" if
              above <= UNFITTED else
              f"FALSIFIER FIRED -- the head is {above:+.4f} over chance at the minimum: it is steering already"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the valley's shape ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the valley's shape ==")
    print(f"   the wide step's first task at seven budgets, three of them new, with `e384`'s series read from its "
          f"artifact; {r['reps']} replicates on the `{r['arm']}` arm")
    series = _series(r)
    heads = {int(k): float(v) for k, v in ((r.get("previous") or {}).get("heads") or {}).items()}
    heads.update({b: v["head_task_0"] for b, v in r["budgets"].items()})
    print(f"\n   {'iters':>7} {'probe':>9} {'head':>8} {'initial':>9}")
    for b in sorted(series):
        init = ((r.get("previous") or {}).get("facts") or {}).get(str(b)) or {}
        here = r["budgets"].get(str(b)) or {}
        print(f"   {b:>7} {series[b]:9.4f} {heads.get(b, float('nan')):8.4f} "
              f"{here.get('initial_task_0', float('nan')):9.4f}")

    print("\n== the registered claims, F1-F5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e384` found the wide step's series is a valley between one and five updates and registered that")
    print("    the shape between them was not located; this samples three more budgets inside it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=SWEEP_REPS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(reps=args.reps)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
