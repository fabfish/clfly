"""E382 -- when the world loses it: the tight step's collapse, resolved in the training budget.

`e379` found the tight step's world carrying nothing after training and `e381` found its whole retention matrix
**frozen** at **0.2083, 0.2083, 0.2917** from the first checkpoint on -- so the failure is not forgetting but a
collapse during the **first** task's training that never recovers. Neither unit can say *when* in those 500
iterations it happened, and `--save-theta` keeps the body only at task ends.

**This unit samples the trajectory with the flag that already exists.** `--iters` is how many gradient steps each
task gets, so a run at a smaller budget is the same configuration stopped earlier: the body it saves is the body
after that many steps of task 0. Five budgets -- **1, 5, 20, 100 and 500** -- at `e379`'s cell (the action source at
`cue@8`, the larger step size), with the 500 point being that unit's own run, read with the same probe on the world
for every task's examples and for the connectome's own weights.

Five claims, registered before any of the new runs' readings was opened.

- **C1 -- one configuration except the budget.** Every sweep run agrees with `e379`'s on every recorded field --
  circuit, tasks and widths, basis, read-out, seed stream, the world's dimension, leak, coupling and mode, the cue's
  step, the drive's source and its seven fields, the controllability flags and the learning rate -- differing in
  `iters`, and in `repeats` where the sweep is shorter. **Falsifier**: any other field differing.
- **C2 -- and the collapse is complete by twenty iterations.** The probe on the body after task 0, on task 0's
  examples, is within **0.05** of its **500**-iteration value at a budget of **20**. **Falsifier**: **0.10** above it,
  which would say the world needs more than twenty steps to lose the cue. **Null**: between. *This is the claim the
  unit exists for.*
- **C3 -- and it is monotone in the budget.** Across the five budgets the reading is **non-increasing**, with no rise
  of **0.05** or more between consecutive budgets. **Falsifier**: any such rise, which would say the world gains the
  cue back partway through the task. **Null**: a rise below 0.05.
- **C4 -- and the first step already costs it.** At a budget of **1** the probe is at least **0.05** below the
  connectome's own weights' reading on the same examples. **Falsifier**: within **0.02**, which would say a single
  gradient step leaves the world where it was. **Null**: between.
- **C5 -- and the head tracks the world down.** At every budget the probe on the body after task 0 and the trained
  head's own accuracy for task 0 are within **0.05**. **Falsifier**: **0.10** apart at any budget, which would say
  the head and the world part company during the collapse rather than falling together.
  **REFUSED** when the artifact is absent.

**What it can do beyond that.** It puts a time axis under every diagonal this window has read: `e379`'s chance
reading, `e381`'s frozen matrix and `e374`'s original failure are all end states, and this says how much of the
training they needed.

**What it cannot do.** *Five budgets are five samples*: the trajectory between them is not measured, so a collapse
between 5 and 20 steps is bounded and not located, and one that happens inside a single step is invisible. *And a
smaller budget is a different run*: the learning rate schedule, the batch order and the head's own fitting all
depend on how many steps were taken, so a body stopped at 20 steps is the body a 20-step run produces and not
necessarily the body a 500-step run passed through -- which is the difference between sampling a trajectory and
measuring one. *And one cell, one draw, one source*: the action source at `cue@8` with the larger step size, so the
cue source and the wide end are not sampled.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e379_what_the_body_did import (  # noqa: F401  (the same instrument)
    ARMS,
    N_TASKS,
    NAIVE,
    TAU,
    _one_body,
    _roll,
    _set,
    _sg,
)
from experiments.e379_what_the_body_did import setup as setup_tight

#: the sweep's runs, and the point at 500 iterations that `e379` already made
BUDGETS = (1, 5, 20, 100, 500)
RUNS = {b: {"run": Path(f"runs/e382_earned_label_iters{b}_cue8_actionsource_5reps.json"),
            "theta": Path(f"runs/e382_theta_{b}")} for b in BUDGETS[:-1]}
RUNS[500] = {"run": Path("runs/e379_earned_label_lr03_cue8_actionsource_20reps.json"),
             "theta": Path("runs/e379_theta")}
SWEEP_REPS = 5
CHECKPOINTS = ("initial", "after_task_0")
SAME = 0.05
FIRES = 0.10
RISES = 0.05
COSTS = 0.05
FITS = 0.02
STABLE = 0.05
CLAIMS = (
    ("C1", "one configuration except the budget",
     "Every sweep run agrees with `e379`'s on every recorded field, differing in `iters`, and in `repeats` where the "
     "sweep is shorter",
     "falsifier: any other field differing"),
    ("C2", f"and the collapse is complete by twenty iterations, within {SAME:.2f}",
     "At a budget of 20 the probe on the body after task 0, on task 0's examples, is within 0.05 of its "
     "500-iteration value",
     f"falsifier: {FIRES:.2f} above it; null: between {SAME:.2f} and {FIRES:.2f}"),
    ("C3", f"and it is monotone in the budget, rises under {RISES:.2f}",
     "Across the five budgets the reading is non-increasing, with no rise of 0.05 or more between consecutive ones",
     f"falsifier: any rise of {RISES:.2f} or more; null: a rise below it"),
    ("C4", f"and the first step already costs it, by {COSTS:.2f}",
     "At a budget of 1 the probe is at least 0.05 below the connectome's own weights' reading on the same examples",
     f"falsifier: within {FITS:.2f}; null: between {FITS:.2f} and {COSTS:.2f}"),
    ("C5", f"and the head tracks the world down, within {SAME:.2f}",
     "At every budget the probe on the body after task 0 and the trained head's own accuracy for task 0 are within "
     "0.05",
     f"falsifier: {FIRES:.2f} apart at any budget; refused when the artifact is absent"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def one_budget(doc: dict, theta_dir: Path, ctx, arm: str = NAIVE, reps: int = SWEEP_REPS) -> dict:
    """The probe on the initial and the after-task-0 bodies, for every task, per replicate."""
    model, loop_env, tasks, n_neurons = ctx
    cell = {(c, k): [] for c in CHECKPOINTS for k in range(N_TASKS)}
    for r, _ in enumerate(((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []):
        if r >= reps:
            break
        seed = doc["config"].get("seed0", 0) + 100 * r
        path = Path(theta_dir) / f"{arm}_seed{seed}.npz"
        if not path.is_file():
            return {"ok": False, "reason": f"{path} is absent"}
        z = np.load(path)
        for k, task in enumerate(tasks):
            for c in CHECKPOINTS:
                key = "theta_initial" if c == "initial" else "after_task_0"
                bias = np.zeros(n_neurons) if c == "initial" else z["bias_after_task_0"]
                _set(model, z[key], bias)
                acc, _ = _one_body(model, loop_env, task)
                cell[(c, k)].append(acc)
    return {"ok": True, "cell": cell}


def reading(runs: dict = RUNS, arm: str = NAIVE, reps: int = SWEEP_REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_tight()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "budgets": {}, "arm": arm, "reps": reps, "facts": {}}
    for b, spec in runs.items():
        doc = load(spec["run"])
        if not doc:
            return {"ok": False, "budgets": {}, "reason": f"budget {b}: the artifact is absent", "facts": {}}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {"ok": False, "budgets": {}, "reason": f"budget {b}: {got['reason']}", "facts": {}}
        learned = [float(x) for x in doc["methods"][arm]["replicates"][0]["learned"]]
        entry = {"run": spec["run"].name, "iters": doc["config"].get("iters"),
                 "repeats": doc["config"].get("repeats"), "head_task_0": learned[0],
                 "cells": {f"{c}|{k}": v for (c, k), v in got["cell"].items()}}
        entry["probe_task_0"] = statistics.fmean(entry["cells"]["after_task_0|0"])
        entry["initial_task_0"] = statistics.fmean(entry["cells"]["initial|0"])
        entry["initial_mean"] = statistics.fmean([statistics.fmean(entry["cells"][f"initial|{k}"])
                                                  for k in range(N_TASKS)])
        entry["trained_mean"] = statistics.fmean([statistics.fmean(entry["cells"][f"after_task_0|{k}"])
                                                  for k in range(N_TASKS)])
        out["budgets"][str(b)] = entry
        out["facts"][str(b)] = _facts(doc)
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights are absent"}
                for c in CLAIMS]
    bud = {int(k): v for k, v in r["budgets"].items()}
    ordered = sorted(bud)
    ref = bud[max(ordered)]
    keys = ("iters", "repeats") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)

    facts = r.get("facts") or {}
    differ = {}
    for b in ordered[:-1]:
        a = facts.get(str(b)) or {}
        c = facts.get(str(max(ordered))) or {}
        diff = {k: [a.get(k), c.get(k)] for k in keys if a.get(k) != c.get(k)}
        differ[b] = diff
    bad = {b: v for b, v in differ.items() if sorted(v) != ["iters", "repeats"] and sorted(v) != ["iters"]}
    j1 = {"id": "C1", "measured": f"each sweep run against the 500-iteration one, over the fields the corpus records: "
                                  f"{ {b: sorted(v) for b, v in differ.items()} }",
          "verdict": "MET -- one configuration except the budget" if not bad else
          f"FALSIFIER FIRED -- {bad} differ beyond `iters` and `repeats`"}

    if 20 not in bud:
        j2 = {"id": "C2", "measured": "the 20-iteration budget is not in the sweep",
              "verdict": "REFUSED -- the budget this claim compares is absent"}
    else:
        gap = bud[20]["probe_task_0"] - ref["probe_task_0"]
        j2 = {"id": "C2", "measured": f"at 20 iterations the probe on the body after task 0 reads "
                                      f"{bud[20]['probe_task_0']:.4f} against {ref['probe_task_0']:.4f} at 500, "
                                      f"{gap:+.4f} above it",
              "verdict": f"MET -- the collapse is complete by twenty iterations, {gap:+.4f}" if abs(gap) < SAME else
              f"FALSIFIER FIRED -- {gap:+.4f} above: the world needs more than twenty steps" if gap >= FIRES else
              f"NULL -- {gap:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    series = [bud[b]["probe_task_0"] for b in ordered]
    rises = [(ordered[i], ordered[i + 1], series[i + 1] - series[i])
             for i in range(len(series) - 1) if series[i + 1] - series[i] >= RISES]
    j3 = {"id": "C3", "measured": f"the probe on task 0's examples across the budgets {ordered} is "
                                  f"{[round(x, 4) for x in series]}, with {rises} rising by {RISES:.2f} or more",
          "verdict": "MET -- the reading is non-increasing in the budget" if not rises else
          f"FALSIFIER FIRED -- it rises at {rises}: the world gains the cue back partway through"}

    if 1 not in bud:
        j4 = {"id": "C4", "measured": "the 1-iteration budget is not in the sweep",
              "verdict": "REFUSED -- the budget this claim needs is absent"}
    else:
        cost = bud[1]["initial_task_0"] - bud[1]["probe_task_0"]
        j4 = {"id": "C4", "measured": f"at one iteration the body reads {bud[1]['probe_task_0']:.4f} where the "
                                      f"connectome's own weights read {bud[1]['initial_task_0']:.4f} on the same "
                                      f"examples, so one step costs {cost:+.4f}",
              "verdict": f"MET -- the first step already costs it, {cost:+.4f}" if cost >= COSTS else
              f"FALSIFIER FIRED -- one step costs only {cost:+.4f}: the world is where it was" if cost < FITS else
              f"NULL -- {cost:+.4f}, between {FITS:.2f} and {COSTS:.2f}"}

    head = {}
    for b in ordered:
        head[b] = bud[b]["probe_task_0"] - bud[b]["head_task_0"]
    apart = {b: v for b, v in head.items() if abs(v) >= FIRES}
    j5 = {"id": "C5", "measured": f"the probe on the body against the trained head for task 0, by budget: "
                                  f"{ {b: round(v, 4) for b, v in head.items()} }",
          "verdict": "MET -- the head tracks the world down at every budget" if not apart else
          f"FALSIFIER FIRED -- they are {apart} apart, so the head and the world part company"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== when the world loses it ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== when the world loses it ==")
    print(f"   the same cell at five training budgets, the body after task 0 read with the corpus's own probe, "
          f"{r['reps']} replicates on the `{r['arm']}` arm")
    print(f"\n   {'iters':>7} {'initial t0':>11} {'trained t0':>11} {'initial mean':>13} {'trained mean':>13} "
          f"{'head t0':>8}")
    for b in sorted(int(k) for k in r["budgets"]):
        e = r["budgets"][str(b)]
        print(f"   {b:>7} {e['initial_task_0']:11.4f} {e['probe_task_0']:11.4f} {e['initial_mean']:13.4f} "
              f"{e['trained_mean']:13.4f} {e['head_task_0']:8.4f}")

    print("\n== the registered claims, C1-C5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e381` found the tight step's retention matrix frozen from the first checkpoint; this asks how")
    print("    much of the training the collapse needed, by stopping the same run at five budgets)")
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
