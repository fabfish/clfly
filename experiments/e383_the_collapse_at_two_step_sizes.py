"""E383 -- the collapse at two step sizes: one update at the corpus's larger rate, or hundreds at its own.

`e382` stopped `e379`'s cell at five training budgets and found the whole loss in the **first** gradient step: the
connectome's own weights carry task 0 at **0.6875**, one batch of thirty-two at `lr = 0.03` leaves **0.2083**, and
five, twenty, a hundred and five hundred steps read the same number. That unit registered its own limit: *"`e377`
showed the smaller rate reaches the same end state after five hundred steps ... so the natural next question is
whether the **smaller** step also collapses at the first update or drifts there over hundreds."*

**This unit runs that comparison.** The five budgets again at the corpus's own `lr = 0.003`, with the bodies kept,
read by the same probe and against the same connectome weights -- so the two step sizes give two series at one cell,
one draw, one arm and one source, and the question is where each of them loses the cue.

Five claims, registered before any of the new runs' readings was opened.

- **D1 -- one configuration across the two sweeps.** Each run at `0.003` agrees with its counterpart at `0.03` on
  every recorded field -- circuit, tasks and widths, basis, read-out, seed stream, iteration budget, replicate count,
  the world's dimension, leak, coupling and mode, the cue's step, the drive's source and its seven fields, and the
  controllability flags -- differing in `lr` alone. **Falsifier**: any other field differing.
- **D2 -- and the smaller step loses the cue by five hundred.** At `0.003` the probe on the body after task 0, on
  task 0's examples, is at least **0.10** below the connectome's own weights' reading on the same examples.
  **Falsifier**: within **0.05**, which would say the smaller step keeps the cue where the larger one loses it.
  **Null**: between. *The licence: without this there is nothing for the first step to have avoided.*
- **D3 -- but not in the first step.** At `0.003` the probe at a budget of **1** is at least **0.05 above** its
  value at **500**. **Falsifier**: within **0.02**, which would say one step at the corpus's own rate collapses the
  world exactly as one step at the larger rate does. **Null**: between. *This is the claim the unit exists for.*
- **D4 -- and it loses the rest over many steps.** At `0.003` the drop from a budget of 1 to a budget of 500 is at
  least **0.10**, with no rise of **0.05** or more between consecutive budgets. **Falsifier**: a flat series from the
  first budget, or a rise of 0.05 or more. **Null**: between **0.05** and **0.10** of total drop.
- **D5 -- and the larger rate costs more at the first update.** At a budget of **1**, the probe at `0.03` is at
  least **0.10** below the probe at `0.003`. **Falsifier**: within **0.05**, which would say the two rates take the
  same amount out of the world in one step. **Null**: between. Together with D3 this is the whole comparison: one
  series falls at the first sample and the other does not.

**What it can do beyond that.** It turns `e382`'s one number into a **rate dependence**: the tight step's failure
has a size in gradient steps, and this says what that size is at the two rates the corpus has run.

**What it cannot do.** *Five budgets per rate*: so the trajectory between samples is not measured, and "drifts over
many steps" is bounded between the first and the five-hundredth and not located -- a collapse at step 2 and one at
step 400 are the same series at this resolution. *And a smaller budget is a different run*, as `e382` says: the batch
order and the head's fitting depend on how many steps were taken. *And one cell, one draw, one source*: the action
source at `cue@8`, so the cue source and the wide end are not compared at either rate, and `e370` showed the boundary
moves with the draw. *And a probe is not a mechanism*: a reading at chance says a linear fit recovers nothing of the
label from the world's eight numbers and not that the label is absent in every form.
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
from experiments.e379_what_the_body_did import setup as setup_tight
from experiments.e382_when_the_world_loses_it import SWEEP_REPS, one_budget

#: the two sweeps: `e382`'s at the larger rate and this unit's at the corpus's own
BUDGETS = (1, 5, 20, 100, 500)
BIG = 0.03
SMALL = 0.003
RUNS = {SMALL: {b: {"run": Path(f"runs/e383_earned_label_iters{b}_cue8_actionsource_5reps.json"),
                    "theta": Path(f"runs/e383_theta_{b}")} for b in BUDGETS}}
RUNS[SMALL][500] = {"run": Path("runs/e383_earned_label_iters500_cue8_actionsource_5reps.json"),
                    "theta": Path("runs/e383_theta_500")}
RUNS[BIG] = {b: {"run": Path(f"runs/e382_earned_label_iters{b}_cue8_actionsource_5reps.json"),
                 "theta": Path(f"runs/e382_theta_{b}")} for b in BUDGETS[:-1]}
RUNS[BIG][500] = {"run": Path("runs/e379_earned_label_lr03_cue8_actionsource_20reps.json"),
                  "theta": Path("runs/e379_theta")}
SAME = 0.05
FIRES = 0.10
STABLE = 0.02
RISES = 0.05
CLAIMS = (
    ("D1", "one configuration across the two sweeps",
     "Each run at 0.003 agrees with its counterpart at 0.03 on every recorded field, differing in `lr`, and in "
     "`repeats` where the counterpart is `e379`'s twenty-replicate run",
     "falsifier: any other field differing"),
    ("D2", f"and the smaller step loses the cue by five hundred, by {FIRES:.2f}",
     "At 0.003 the probe at a budget of 500 is at least 0.10 below the connectome's own weights' reading",
     f"falsifier: within {SAME:.2f}; null: between {SAME:.2f} and {FIRES:.2f}"),
    ("D3", f"but not in the first step, by {SAME:.2f}",
     "At 0.003 the probe at a budget of 1 is at least 0.05 above its value at 500",
     f"falsifier: within {STABLE:.2f}; null: between {STABLE:.2f} and {SAME:.2f}"),
    ("D4", "and it loses the rest over many steps",
     "At 0.003 the drop from a budget of 1 to 500 is at least 0.10 with no rise of 0.05 or more between budgets",
     "falsifier: a flat series from the first budget, or a rise of 0.05 or more; null: between 0.05 and 0.10"),
    ("D5", f"and the larger rate costs more at the first update, by {FIRES:.2f}",
     "At a budget of 1 the probe at 0.03 is at least 0.10 below the probe at 0.003",
     f"falsifier: within {SAME:.2f}; null: between {SAME:.2f} and {FIRES:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(runs: dict = RUNS, arm: str = NAIVE, reps: int = SWEEP_REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_tight()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "sweeps": {}, "facts": {}, "arm": arm, "reps": reps, "budgets": list(BUDGETS)}
    for lr, spec in runs.items():
        series, facts = {}, {}
        for b, s in spec.items():
            doc = load(s["run"])
            if not doc:
                return {"ok": False, "sweeps": {}, "facts": {}, "reason": f"lr {lr} budget {b}: the artifact is "
                                                                          f"absent"}
            got = one_budget(doc, s["theta"], ctx, arm=arm, reps=reps)
            if not got.get("ok"):
                return {"ok": False, "sweeps": {}, "facts": {}, "reason": f"lr {lr} budget {b}: {got['reason']}"}
            cell = got["cell"]
            series[str(b)] = {"run": s["run"].name, "iters": doc["config"].get("iters"),
                              "lr": doc["config"].get("lr"), "repeats": doc["config"].get("repeats"),
                              "probe_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                              "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                              "trained_mean": statistics.fmean([statistics.fmean(cell[("after_task_0", k)])
                                                                for k in range(N_TASKS)]),
                              "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
            #: `_facts` records the environment and the budget but not the two knobs this unit turns, so
            #: they are added here -- without them the comparison below cannot see the manipulation
            facts[str(b)] = {**_facts(doc), "lr": doc["config"].get("lr"),
                             "batch": doc["config"].get("batch")}
        out["sweeps"][str(lr)] = series
        out["facts"][str(lr)] = facts
    return out


def _series(r: dict, lr: float) -> list[float]:
    s = r["sweeps"][str(lr)]
    return [s[str(b)]["probe_task_0"] for b in BUDGETS]


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights are absent"}
                for c in CLAIMS]
    keys = ("lr", "batch", "iters", "repeats") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
    facts = r["facts"]
    differ = {}
    for b in BUDGETS:
        a = (facts.get(str(SMALL)) or {}).get(str(b)) or {}
        c = (facts.get(str(BIG)) or {}).get(str(b)) or {}
        differ[b] = {k: [a.get(k), c.get(k)] for k in keys if a.get(k) != c.get(k)}
    #: the 500 point at the larger rate is `e379`'s twenty-replicate run, so its replicate count moves too
    bad = {b: v for b, v in differ.items() if sorted(v) not in (["lr"], ["lr", "repeats"])}
    j1 = {"id": "D1", "measured": f"each 0.003 run against its 0.03 counterpart: "
                                  f"{ {b: sorted(v) for b, v in differ.items()} }",
          "verdict": "MET -- one configuration across the two sweeps, `lr` alone differing except at the budget "
                     "whose counterpart carries twenty replicates" if not bad else
          f"FALSIFIER FIRED -- {bad} differ beyond `lr` and `repeats`"}

    small = r["sweeps"][str(SMALL)]
    s500, s1 = small["500"], small["1"]
    cost = s1["initial_task_0"] - s500["probe_task_0"]
    j2 = {"id": "D2", "measured": f"at 0.003 the body after 500 iterations reads {s500['probe_task_0']:.4f} where "
                                  f"the connectome's own weights read {s500['initial_task_0']:.4f}, a loss of "
                                  f"{cost:+.4f}",
          "verdict": f"MET -- the smaller step loses the cue by five hundred, {cost:+.4f}" if cost >= FIRES else
          f"FALSIFIER FIRED -- only {cost:+.4f}: the smaller step keeps the cue" if cost < SAME else
          f"NULL -- {cost:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    first = s1["probe_task_0"] - s500["probe_task_0"]
    j3 = {"id": "D3", "measured": f"at 0.003 the body after one iteration reads {s1['probe_task_0']:.4f} and after "
                                  f"five hundred {s500['probe_task_0']:.4f}, so the first step costs {first:+.4f}",
          "verdict": f"MET -- the first step at the corpus's own rate keeps the cue, {first:+.4f} above the "
                     f"five-hundredth" if first >= SAME else
          f"FALSIFIER FIRED -- only {first:+.4f}: one step at this rate collapses the world too" if first < STABLE
          else f"NULL -- {first:+.4f}, between {STABLE:.2f} and {SAME:.2f}"}

    series = _series(r, SMALL)
    rises = [(BUDGETS[i], BUDGETS[i + 1], series[i + 1] - series[i]) for i in range(len(series) - 1)
             if series[i + 1] - series[i] >= RISES]
    drop = series[0] - series[-1]
    j4 = {"id": "D4", "measured": f"at 0.003 the probe across the budgets {list(BUDGETS)} is "
                                  f"{[round(x, 4) for x in series]}, a total drop of {drop:+.4f} with {rises} "
                                  f"rising by {RISES:.2f} or more",
          "verdict": f"MET -- it loses the rest over many steps, {drop:+.4f} between the first and the last" if
          drop >= FIRES and not rises else
          f"FALSIFIER FIRED -- {drop:+.4f} from the first budget with rises {rises}: a flat series or a rise" if
          drop < SAME or rises else
          f"NULL -- {drop:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}

    big1 = r["sweeps"][str(BIG)]["1"]["probe_task_0"]
    gap = s1["probe_task_0"] - big1
    j5 = {"id": "D5", "measured": f"at a budget of one the body reads {s1['probe_task_0']:.4f} at 0.003 and "
                                  f"{big1:.4f} at 0.03, so the larger rate costs {gap:+.4f} more in one step",
          "verdict": f"MET -- the larger rate costs more at the first update, {gap:+.4f}" if gap >= FIRES else
          f"FALSIFIER FIRED -- only {gap:+.4f}: the two rates take the same out of the world in one step" if
          gap < SAME else f"NULL -- {gap:+.4f}, between {SAME:.2f} and {FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the collapse at two step sizes ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the collapse at two step sizes ==")
    print(f"   the same cell at five budgets and two step sizes, the body after task 0 read with the corpus's own "
          f"probe, {r['reps']} replicates on the `{r['arm']}` arm")
    print(f"\n   {'iters':>7} {'0.003 probe':>12} {'0.003 head':>11} {'0.03 probe':>11} {'0.03 head':>10} "
          f"{'initial':>9}")
    for b in BUDGETS:
        s = r["sweeps"][str(SMALL)][str(b)]
        g = r["sweeps"][str(BIG)][str(b)]
        print(f"   {b:>7} {s['probe_task_0']:12.4f} {s['head_task_0']:11.4f} {g['probe_task_0']:11.4f} "
              f"{g['head_task_0']:10.4f} {s['initial_task_0']:9.4f}")

    print("\n== the registered claims, D1-D5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e382` found the whole loss in one gradient step at the larger rate and named this comparison;")
    print("    this runs the same five budgets at the corpus's own and asks where each series loses the cue)")
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
