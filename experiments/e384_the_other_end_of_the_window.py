"""E384 -- the other end of the window: does the wide step's series rise where the tight step's falls?

`e382` and `e383` sampled the tight step's first task at five training budgets and found the whole loss in **one**
gradient step, at either of the two rates the corpus has run: the connectome's own weights carry task 0 at
**0.6875** and one Adam update leaves **0.2083**. `e383` registered what that implies and did not test: the world's
spread at `cue@8` is **0.0478** against **0.2780** at `cue@0`, six times larger, and one step moves a coordinate by
about `lr`, so at the tight step a single step's perturbation is of the same order as the whole signal where at the
wide step it is a fraction of it -- *"the run that would [test it] is the same five budgets at `cue@0`, where the
prediction is a series that **rises** from the first step rather than falling to the floor."*

**This unit runs it.** The five budgets at `cue@0`, the action source, the corpus's own rate and the bodies kept,
with `e380`'s own twenty-replicate run as the 500 point -- that unit was the same cell with the same flags. The
tight step's series is read from `e383`'s artifact rather than rolled again, since it is the corpus's own record of
the comparison this claim is about.

Five claims, registered before any of the new runs' readings was opened.

- **E1 -- one configuration except the budget.** Each sweep run agrees with `e380`'s on every recorded field -- the
  circuit, the tasks and their widths, the basis, the read-out, the seed stream, the learning rate, the batch, the
  world's dimension, leak, coupling and mode, the cue's step, the drive's source and its seven fields and the
  controllability flags -- differing in `iters`, and in `repeats` where the sweep is shorter. **Falsifier**: any
  other field differing. *The rate and the batch are named because `e383`'s first reading compared two sweeps over a
  field list that did not contain the rate, and reported a manipulation as no difference at all.*
- **E2 -- and the wide step's series rises.** The probe on the body after task 0, on task 0's examples, is at least
  **0.05** higher at a budget of 500 than at a budget of **1**. **Falsifier**: within **0.02**, which would say the
  wide step's first update costs nothing and gains nothing either. **Null**: between. *This is the claim the unit
  exists for, and it is `e383`'s registered prediction.*
- **E3 -- and the wide step's first update leaves the world above the floor.** At a budget of **1** the probe is at
  least **0.10** above chance. **Falsifier**: within **0.05**, which would say one update empties the wide end too
  and the difference between the two ends is not the step. **Null**: between.
- **E4 -- and the two ends differ at the first update.** At a budget of **1** the wide step's probe exceeds the tight
  step's by at least **0.10**, the tight one being `e383`'s own reading for the same budget, rate and seed stream.
  **Falsifier**: within **0.05**. **Null**: between. **REFUSED** when that artifact is absent.
- **E5 -- and the wide step's training adds to what the connectome already carried.** At a budget of **500** the probe
  exceeds the connectome's own weights' reading on the same examples by at least **0.05**. **Falsifier**: within
  **0.02**. **Null**: between. This is the mirror of `e383`'s D2, which is where the tight step **loses 0.4583**.

**What it can do beyond that.** With `e382`, `e383` and this, the window's two ends have the same measurement: the
first task's trajectory in gradient steps, at the corpus's own rate, with the connectome's own weights as the
reference. One end falls to the floor in one update and the other is predicted to rise, and the difference between
them would then be the scale of the world rather than anything the optimiser does.

**What it cannot do.** *Five budgets*: the trajectory between samples is not measured, so a rise that happens inside
the first step and one spread over the five hundred look the same here. *And a smaller budget is a different run*:
the batch order and the head's fitting depend on how many steps were taken. *And the two ends are not one
experiment*: `cue@0` and `cue@8` differ in the world's spread and in where the cue reaches the drive, so a
difference between them is about the two cells and not about one variable -- which is exactly what `e369`'s formula
and `e370`'s sweep are for. *And a probe is not a mechanism*: a reading above chance says a linear fit recovers some
of the label from the world's eight numbers, not that the body built it there in the way a mechanism would name.
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

#: the sweep at the wide step, with `e380`'s own run as the 500 point
BUDGETS = (1, 5, 20, 100, 500)
RUNS = {b: {"run": Path(f"runs/e384_earned_label_iters{b}_cue0_actionsource_5reps.json"),
            "theta": Path(f"runs/e384_theta_{b}")} for b in BUDGETS[:-1]}
RUNS[500] = {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"),
             "theta": Path("runs/e380_theta")}
#: `e383`'s artifact, which holds the tight step's series at the same rate and the same budgets
TIGHT = Path("runs/e383_the_collapse_at_two_step_sizes.json")
SAME = 0.05
STABLE = 0.02
LEARNS = 0.10
CLAIMS = (
    ("E1", "one configuration except the budget",
     "Each sweep run agrees with `e380`'s on every recorded field including the learning rate and the batch, "
     "differing in `iters`, and in `repeats` where the sweep is shorter",
     "falsifier: any other field differing"),
    ("E2", f"and the wide step's series rises, by {SAME:.2f}",
     "The probe on the body after task 0 is at least 0.05 higher at a budget of 500 than at a budget of 1",
     f"falsifier: within {STABLE:.2f}; null: between {STABLE:.2f} and {SAME:.2f}"),
    ("E3", f"and its first update leaves the world above the floor, {LEARNS:.2f} over chance",
     "At a budget of 1 the probe is at least 0.10 above chance",
     f"falsifier: within {SAME:.2f} of chance; null: between"),
    ("E4", f"and the two ends differ at the first update, by {LEARNS:.2f}",
     "At a budget of 1 the wide step's probe exceeds the tight step's, read from `e383`'s artifact, by at least 0.10",
     f"falsifier: within {SAME:.2f}; refused when that artifact is absent"),
    ("E5", f"and its training adds to what the connectome carried, by {SAME:.2f}",
     "At a budget of 500 the probe exceeds the connectome's own weights' reading by at least 0.05",
     f"falsifier: within {STABLE:.2f}; null: between {STABLE:.2f} and {SAME:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(runs: dict = RUNS, tight_path: Path = TIGHT, arm: str = NAIVE, reps: int = SWEEP_REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "budgets": {}, "facts": {}, "arm": arm, "reps": reps, "tight": None}
    for b, spec in runs.items():
        doc = load(spec["run"])
        if not doc:
            return {"ok": False, "budgets": {}, "facts": {}, "tight": None, "reason": f"budget {b}: the artifact is "
                                                                                     f"absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {"ok": False, "budgets": {}, "facts": {}, "tight": None,
                    "reason": f"budget {b}: {got['reason']}"}
        cell = got["cell"]
        out["budgets"][str(b)] = {"run": spec["run"].name, "iters": doc["config"].get("iters"),
                                  "lr": doc["config"].get("lr"), "repeats": doc["config"].get("repeats"),
                                  "probe_task_0": statistics.fmean(cell[("after_task_0", 0)]),
                                  "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                                  "probe_mean": statistics.fmean([statistics.fmean(cell[("after_task_0", k)])
                                                                  for k in range(N_TASKS)]),
                                  "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        #: the rate and the batch are added here: `e383`'s first reading compared two sweeps over a field list that
        #: did not contain the rate, which reported the manipulation as no difference at all
        out["facts"][str(b)] = {**_facts(doc), "lr": doc["config"].get("lr"), "batch": doc["config"].get("batch")}
    tdoc = load(tight_path)
    if tdoc:
        series = (tdoc.get("sweeps") or {}).get(str(SMALL)) or {}
        one = series.get("1")
        if one:
            out["tight"] = {"artifact": Path(tight_path).name, "budget_1": float(one["probe_task_0"]),
                            "budget_500": float(series.get("500", {}).get("probe_task_0")
                                                if series.get("500") else float("nan"))}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights are absent"}
                for c in CLAIMS]
    bud = {int(k): v for k, v in r["budgets"].items()}
    ordered = sorted(bud)
    keys = ("lr", "batch", "iters", "repeats") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
    ref = r["facts"][str(max(ordered))]
    differ = {}
    for b in ordered:
        a = r["facts"].get(str(b)) or {}
        differ[b] = {k: [a.get(k), ref.get(k)] for k in keys if a.get(k) != ref.get(k)}
    #: the 500-iteration run is the reference itself, so its difference against itself is not a finding
    bad = {b: v for b, v in differ.items()
           if b != max(ordered) and sorted(v) not in (["iters"], ["iters", "repeats"])}
    j1 = {"id": "E1", "measured": f"each sweep run against the 500-iteration one: { {b: sorted(v) for b, v in differ.items()} }",
          "verdict": "MET -- one configuration except the budget" if not bad else
          f"FALSIFIER FIRED -- {bad} differ beyond `iters` and `repeats`"}

    if 1 not in bud:
        j2 = {"id": "E2", "measured": "the budget of one is not in the sweep",
              "verdict": "REFUSED -- the budget this claim compares is absent"}
    else:
        rise = bud[max(ordered)]["probe_task_0"] - bud[1]["probe_task_0"]
        j2 = {"id": "E2", "measured": f"at cue@0 the body after task 0 reads {bud[1]['probe_task_0']:.4f} at a budget "
                                      f"of one and {bud[max(ordered)]['probe_task_0']:.4f} at "
                                      f"{max(ordered)}, so the series rises by {rise:+.4f}",
              "verdict": f"MET -- the wide step's series rises, by {rise:+.4f}" if rise >= SAME else
              f"FALSIFIER FIRED -- it rises by only {rise:+.4f}: the first update neither costs nor gains" if
              abs(rise) < STABLE else f"NULL -- {rise:+.4f}, between {STABLE:.2f} and {SAME:.2f}"}

    chance = 1.0 / 4
    above = bud[1]["probe_task_0"] - chance
    j3 = {"id": "E3", "measured": f"at a budget of one the probe reads {bud[1]['probe_task_0']:.4f} against a chance "
                                  f"of {chance:.2f}, {above:+.4f} above it, where the connectome's own weights read "
                                  f"{bud[1]['initial_task_0']:.4f}",
          "verdict": f"MET -- the first update leaves the world above the floor, {above:+.4f}" if above >= LEARNS
          else f"FALSIFIER FIRED -- only {above:+.4f} over chance: one update empties the wide end too" if
          above < SAME else f"NULL -- {above:+.4f}, between {SAME:.2f} and {LEARNS:.2f}"}

    tight = r.get("tight")
    if not tight or 1 not in bud:
        j4 = {"id": "E4", "measured": "the tight step's series or the budget of one is missing",
              "verdict": "REFUSED -- the artifact this comparison needs is absent"}
    else:
        gap = bud[1]["probe_task_0"] - tight["budget_1"]
        j4 = {"id": "E4", "measured": f"at a budget of one the wide step reads {bud[1]['probe_task_0']:.4f} and the "
                                      f"tight step {tight['budget_1']:.4f} in `{tight['artifact']}`, so they differ "
                                      f"by {gap:+.4f} at the first update",
              "verdict": f"MET -- the two ends differ at the first update, by {gap:+.4f}" if gap >= LEARNS else
              f"FALSIFIER FIRED -- only {gap:+.4f}: one update empties both ends equally" if gap < SAME else
              f"NULL -- {gap:+.4f}, between {SAME:.2f} and {LEARNS:.2f}"}

    gains = bud[max(ordered)]["probe_task_0"] - bud[max(ordered)]["initial_task_0"]
    j5 = {"id": "E5", "measured": f"at a budget of {max(ordered)} the body reads "
                                  f"{bud[max(ordered)]['probe_task_0']:.4f} where the connectome's own weights read "
                                  f"{bud[max(ordered)]['initial_task_0']:.4f}, so the training adds {gains:+.4f}",
          "verdict": f"MET -- the training adds to what the connectome carried, by {gains:+.4f}" if gains >= SAME else
          f"FALSIFIER FIRED -- only {gains:+.4f}: the training adds nothing to the world" if gains < STABLE else
          f"NULL -- {gains:+.4f}, between {STABLE:.2f} and {SAME:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the other end of the window ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the other end of the window ==")
    print(f"   the five budgets at cue@0, the action source at the corpus's rate, the body after task 0 read with the "
          f"corpus's own probe, {r['reps']} replicates on the `{r['arm']}` arm")
    print(f"\n   {'iters':>7} {'probe t0':>9} {'initial t0':>11} {'head t0':>8} {'run':>44}")
    for b in sorted(int(k) for k in r["budgets"]):
        e = r["budgets"][str(b)]
        print(f"   {b:>7} {e['probe_task_0']:9.4f} {e['initial_task_0']:11.4f} {e['head_task_0']:8.4f} "
              f"{e['run']:>44}")
    if r.get("tight"):
        print(f"   the tight step at the same rate and budget reads {r['tight']['budget_1']:.4f} at one iteration "
              f"(`{r['tight']['artifact']}`)")

    print("\n== the registered claims, E1-E5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e383` found both rates lose the tight step's cue in one update and registered what that implies")
    print("    about the world's scale, with this sweep as the run that would test it)")
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
