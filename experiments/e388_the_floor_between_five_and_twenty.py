"""E388 -- the floor between five and twenty: where the wide step's valley bottoms out.

`e385` resolved the wide step's first task to seven budgets -- **1**, **2**, **3**, **4**, **5** from its own runs
and **20**, **100**, **500** joined from `e384`'s artifact -- and found the series falls the whole way to five:
**0.6792**, **0.5917**, **0.5750**, **0.5625**, **0.5500**. Its own reading at **5** is the lowest it sampled and
its **falsifier fired** on the turn, so it registered the shape it could not see: *"the floor is between five and
twenty updates (0.5875 by twenty) and the recovery between twenty and five hundred (0.7792)."*

**This unit locates the floor.** Five budgets inside that interval -- **6**, **8**, **11**, **14**, **17** -- the
same cell, the same rate and the same seed stream, five replicates each, with `e385`'s own series read from its
artifact as the ends the new samples join. The connectome's own weights read **0.6875** on these examples at every
budget, so the whole excursion is below where it started.

Five claims, registered before any of the new runs' readings was opened.

- **I1 -- one configuration except the budget.** Each new run agrees with `e384`'s budget-1 run, read through
  `e385`'s artifact, on every recorded field including the learning rate and the batch, differing in `iters`, and in
  `repeats` where the sweep is shorter. **Falsifier**: any other field differing. *The rate and the batch are named
  because `e383`'s first reading compared two sweeps over a field list that did not contain the rate.*
- **I2 -- and the floor is interior, not at either end.** Over the budgets from **5** to **20** the series has
  exactly **one** minimum, and it sits at a budget strictly between those two, with the readings falling into it and
  rising out of it. **Falsifier**: a flat region at the minimum, two budgets within **0.02** there, or the minimum
  at **5** or at **20**, which would say the dip is still deepening or already rising at an end and the turn is
  outside the interval this unit sampled.
- **I3 -- and the dip continues past five.** The floor is at least **0.02** below the reading at a budget of **5**.
  **Falsifier**: within **0.01**, which would say five is already the floor and `e385`'s registered interval is
  empty. **Null**: between.
- **I4 -- and the recovery has begun by twenty.** The reading at a budget of **20** exceeds the floor by at least
  **0.02**. **Falsifier**: within **0.01**, which would say the valley is still deepening at twenty. **Null**:
  between.
- **I5 -- and the floor happens while the head is unfitted.** At the budget where the floor sits, the trained head
  reads no more than **0.10** above chance. **Falsifier**: the head above that, which would say the world bottoms out
  while the head is already steering -- `e380`'s and `e385`'s account, that the training's work at this end is
  fitting the head, would then be wrong.

**What it can do beyond that.** With `e384` and `e385` it turns the wide step's first task into a series of twelve
budgets and locates the turn, which is the one number the valley's shape has left open. The tight end has no such
shape -- one update and it is at the floor -- so this is the only one of the two ends where a floor exists to find.

**What it cannot do.** *Five more budgets are five more samples*: the floor is bounded between two sampled budgets
and not located to a step, and a turn inside a single update is invisible. *And a smaller budget is a different run*:
the batch order, the head's fitting and any schedule depend on how many steps were taken. *One cell and one draw*:
the action source at `cue@0`, so the cue source and the tight end are not resolved this way. *And a probe is not a
mechanism*: a reading says how much of the label a linear fit recovers from the world's eight numbers, so the floor
is a shape in what is recoverable and not a named process.
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

#: the budgets this unit adds, inside the interval `e385` registered as holding the floor
NEW = (6, 8, 11, 14, 17)
#: `e385`'s artifact, which holds the series from 1 to 5 and the 20, 100 and 500 points joined from `e384`
PREVIOUS = Path("runs/e385_the_valleys_shape.json")
RUNS = {b: {"run": Path(f"runs/e388_earned_label_iters{b}_cue0_actionsource_5reps.json"),
            "theta": Path(f"runs/e388_theta_{b}")} for b in NEW}
#: the ends of the interval the floor was registered inside
LOW, HIGH = 5, 20
CHANCE = 0.25
SAME = 0.02
FIRES = 0.01
DEPTH = 0.02
UNFITTED = 0.10
CLAIMS = (
    ("I1", "one configuration except the budget",
     "Each new run agrees with `e384`'s budget-1 run on every recorded field, including the learning rate and the "
     "batch, differing in `iters` and in `repeats` where the sweep is shorter",
     "falsifier: any other field differing"),
    ("I2", "and the floor is interior, not at either end",
     f"Over the budgets from {LOW} to {HIGH} the series has exactly one minimum, strictly inside the interval, "
     "falling into it and rising out of it",
     f"falsifier: a flat region at the minimum, two budgets within {SAME:.2f} there, or the minimum at an end"),
    ("I3", f"and the dip continues past five, by {DEPTH:.2f}",
     f"The floor is at least {DEPTH:.2f} below the reading at a budget of {LOW}",
     f"falsifier: within {FIRES:.2f}; null: between {FIRES:.2f} and {DEPTH:.2f}"),
    ("I4", f"and the recovery has begun by twenty, by {DEPTH:.2f}",
     f"The reading at a budget of {HIGH} exceeds the floor by at least {DEPTH:.2f}",
     f"falsifier: within {FIRES:.2f}; null: between {FIRES:.2f} and {DEPTH:.2f}"),
    ("I5", f"and the floor happens while the head is unfitted, within {UNFITTED:.2f} of chance",
     "At the budget where the floor sits, the trained head reads no more than 0.10 above chance",
     "falsifier: the head above that at the floor's budget"),
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
            return {**out, "ok": False, "reason": f"budget {b}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"budget {b}: {got['reason']}"}
        cell = got["cell"]
        reps_acc = [float(v) for v in cell[("after_task_0", 0)]]
        out["budgets"][str(b)] = {"run": spec["run"].name, "iters": doc["config"].get("iters"),
                                  "probe_task_0": statistics.fmean(reps_acc),
                                  "per_rep_task_0": reps_acc,
                                  "sem_task_0": (statistics.stdev(reps_acc) / len(reps_acc) ** 0.5
                                                 if len(reps_acc) > 1 else float("nan")),
                                  "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                                  "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["facts"][str(b)] = {**_facts(doc), "lr": doc["config"].get("lr"), "batch": doc["config"].get("batch")}
    prev = load(previous)
    if not prev:
        return {**out, "ok": False, "reason": f"{previous} is absent, so the series has no ends to join"}
    readings = {int(k): float(v) for k, v in ((prev.get("previous") or {}).get("readings") or {}).items()}
    readings.update({int(k): float(v["probe_task_0"]) for k, v in (prev.get("budgets") or {}).items()})
    heads = {int(k): float(v) for k, v in ((prev.get("previous") or {}).get("heads") or {}).items()}
    heads.update({int(k): float(v.get("head_task_0", float("nan"))) for k, v in (prev.get("budgets") or {}).items()})
    initials = {int(k): float(v.get("initial_task_0", float("nan")))
                for k, v in (prev.get("budgets") or {}).items()}
    prev_facts = {**((prev.get("previous") or {}).get("facts") or {}), **(prev.get("facts") or {})}
    out["previous"] = {"artifact": Path(previous).name, "readings": {str(k): v for k, v in readings.items()},
                       "heads": {str(k): v for k, v in heads.items()},
                       "initials": {str(k): v for k, v in initials.items()},
                       "facts": prev_facts}
    #: the interval's own resolution: the reading means span this band, and the new budgets carry the standard
    #: error of each of those means over the five replicates, so the band can be read against the instrument
    inband = {b: v for b, v in _series(out, "readings").items() if LOW <= b <= HIGH}
    sems = {int(k): float(v.get("sem_task_0", float("nan"))) for k, v in out["budgets"].items()}
    out["band"] = {"budgets": sorted(inband), "low": min(inband.values()), "high": max(inband.values()),
                   "span": max(inband.values()) - min(inband.values()),
                   "min_budget": min(inband, key=lambda b: inband[b]),
                   "sems": {str(k): v for k, v in sems.items()},
                   "worst_sem": max((v for v in sems.values() if v == v), default=float("nan"))}
    return out


def _series(r: dict, key: str = "readings") -> dict:
    out = {}
    for b, v in ((r.get("previous") or {}).get(key) or {}).items():
        out[int(b)] = float(v)
    if key == "readings":
        out.update({int(k): float(v["probe_task_0"]) for k, v in (r.get("budgets") or {}).items()})
    else:
        out.update({int(k): float(v["head_task_0"]) for k, v in (r.get("budgets") or {}).items()})
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run, its weights or the previous series is "
                                                        "absent"} for c in CLAIMS]
    bud = {int(k): v for k, v in r["budgets"].items()}
    keys = ("lr", "batch", "iters") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
    #: the reference is `e384`'s own budget-1 run, read through `e385`'s artifact
    pf = (r.get("previous") or {}).get("facts", {}).get("1") or {}
    differ = {}
    for b, entry in bud.items():
        facts = r["facts"][str(b)]
        differ[b] = {k: [facts.get(k), pf.get(k)] for k in keys if facts.get(k) != pf.get(k)}
    bad = {b: v for b, v in differ.items() if sorted(v) not in (["iters"], ["iters", "repeats"])}
    j1 = {"id": "I1", "measured": f"each new run against `e384`'s budget-1 run: "
                                  f"{ {b: sorted(v) for b, v in differ.items()} }",
          "verdict": "MET -- one configuration, and the budget is the only thing that moves" if not bad else
          f"FALSIFIER FIRED -- {bad} differ beyond the budget"}

    series = _series(r, "readings")
    window = {b: v for b, v in sorted(series.items()) if LOW <= b <= HIGH}
    ordered = sorted(window)
    if len(window) < 3:
        missing = "fewer than three budgets between five and twenty are available"
        j2 = {"id": "I2", "measured": missing, "verdict": "REFUSED -- the interval this claim is about is not sampled"}
        j3 = {"id": "I3", "measured": missing, "verdict": "REFUSED -- the interval this claim is about is not sampled"}
        j4 = {"id": "I4", "measured": missing, "verdict": "REFUSED -- the interval this claim is about is not sampled"}
        low = None
    else:
        low = min(ordered, key=lambda b: window[b])
        flat = [b for b in ordered if b != low and abs(window[b] - window[low]) < SAME]
        falls = all(window[ordered[i]] >= window[ordered[i + 1]] for i in range(ordered.index(low)))
        rises = all(window[ordered[i]] <= window[ordered[i + 1]] for i in range(ordered.index(low), len(ordered) - 1))
        interior = low not in (LOW, HIGH)
        good = interior and not flat and falls and rises
        j2 = {"id": "I2", "measured": f"the readings over the budgets {ordered} are "
                                      f"{[round(window[b], 4) for b in ordered]}, with the minimum at {low} "
                                      f"(interior: {interior}) and {flat} within {SAME:.2f} of it",
              "verdict": f"MET -- the floor is interior, at a budget of {low}" if good else
              f"FALSIFIER FIRED -- the minimum is at {low}, with {flat} within {SAME:.2f} of it, or the series does "
              f"not fall into it and rise out of it"}
        depth_low = window[LOW] - window[low] if LOW in window else None
        j3 = {"id": "I3", "measured": f"the floor is {window[low]:.4f} at a budget of {low} and the reading at a "
                                      f"budget of {LOW} is {window[LOW]:.4f}, so the dip continues "
                                      f"{depth_low:+.4f} past five" if depth_low is not None else
                                      f"the reading at a budget of {LOW} is missing",
              "verdict": f"MET -- the dip continues past five, {depth_low:+.4f}" if depth_low is not None and
                         depth_low >= DEPTH else
              f"FALSIFIER FIRED -- only {depth_low:+.4f}: five is already the floor" if depth_low is not None and
              depth_low < FIRES else
              f"NULL -- {depth_low:+.4f}, between {FIRES:.2f} and {DEPTH:.2f}" if depth_low is not None else
              "REFUSED -- the comparison this claim makes is not computable"}
        back = window[HIGH] - window[low] if HIGH in window else None
        j4 = {"id": "I4", "measured": f"the reading at a budget of {HIGH} is {window[HIGH]:.4f} against the floor's "
                                      f"{window[low]:.4f}, so it has come back {back:+.4f}" if back is not None else
                                      f"the reading at a budget of {HIGH} is missing",
              "verdict": f"MET -- the recovery has begun by twenty, {back:+.4f}" if back is not None and
                         back >= DEPTH else
              f"FALSIFIER FIRED -- only {back:+.4f}: the valley is still deepening at twenty" if back is not None and
              back < FIRES else
              f"NULL -- {back:+.4f}, between {FIRES:.2f} and {DEPTH:.2f}" if back is not None else
              "REFUSED -- the comparison this claim makes is not computable"}

    heads = _series(r, "heads")
    if low is None or low not in heads:
        j5 = {"id": "I5", "measured": "the head's reading at the floor's budget is missing",
              "verdict": "REFUSED -- the comparison this claim makes is not computable"}
    else:
        above = heads[low] - CHANCE
        j5 = {"id": "I5", "measured": f"at a budget of {low}, where the floor sits, the trained head reads "
                                      f"{heads[low]:.4f} against a chance of {CHANCE:.2f}, {above:+.4f} above it",
              "verdict": f"MET -- the floor happens while the head is unfitted, {above:+.4f} over chance" if
              above <= UNFITTED else
              f"FALSIFIER FIRED -- the head is {above:+.4f} over chance at the floor: it is steering already"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the floor between five and twenty ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the floor between five and twenty ==")
    print(f"   the wide step's first task at five budgets inside the interval `e385` registered, with its series "
          f"as the ends; {r['reps']} replicates on the `{r['arm']}` arm")
    series = _series(r, "readings")
    heads = _series(r, "heads")
    initials = {int(k): float(v) for k, v in ((r.get("previous") or {}).get("initials") or {}).items()}
    print(f"\n   {'iters':>7} {'probe':>9} {'head':>8} {'initial':>9}  {'new':>4}")
    for b in sorted(series):
        print(f"   {b:>7} {series[b]:9.4f} {heads.get(b, float('nan')):8.4f} "
              f"{initials.get(b, float('nan')):9.4f}  {'*' if b in NEW else '':>4}")

    band = r.get("band") or {}
    if band:
        print(f"\n   the interval {LOW} to {HIGH}: readings {band['low']:.4f} to {band['high']:.4f}, a band "
              f"{band['span']:.4f} wide, lowest at a budget of {band['min_budget']}; the new budgets' own standard "
              f"errors over {r['reps']} replicates run "
              f"{min(v for v in band['sems'].values() if v == v):.4f} to {band['worst_sem']:.4f}, so the band is "
              f"{band['span'] / band['worst_sem']:.2f} of the widest of them")

    print("\n== the registered claims, I1-I5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e385` registered that the floor sits between five and twenty updates; this samples five budgets")
    print("    inside that interval and locates the turn)")
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
