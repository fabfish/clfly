"""E389 -- the interval at twenty replicates: the floor re-measured at the resolution `e388` asked for.

`e388` sampled the wide step's first task at **6**, **8**, **11**, **14** and **17** updates, joined them to
`e385`'s series, and asked whether the interval from five to twenty holds a turn. It does not: the readings are
0.5500, 0.5667, 0.5542, 0.5875, 0.5292, 0.5750, 0.5875, rising from 5 to 6 and again from 8 to 11, so there is no
monotone approach to the minimum at 14. The unit then measured why it could not have found one: the whole band from
5 to 20 spans **0.0583**, and the standard error of the new budgets' means over their five replicates is **0.0232**
to **0.0546**, so the excursion is **1.07 times the widest of those errors**. Its finding registered the consequence
plainly: *"the turn is not located because it is smaller than five replicates can resolve; twenty replicates, the
corpus's own replicate count for a decisive cell, would halve it."*

**This unit runs that.** The same cell at eleven budgets -- **1**, **2**, **3**, **4**, **5**, **6**, **8**, **11**,
**14**, **17**, **20** -- all rolled again at **twenty** replicates rather than joined, so the whole series is one
instrument at one resolution. The connectome's own weights read **0.6875** on these examples.

Five claims, registered before any of the new runs' readings was opened.

- **J1 -- one configuration except the budget.** Each run agrees with `e385`'s budget-1 run on every recorded field
  including the learning rate and the batch, differing in `iters` and in `repeats`. **Falsifier**: any other field
  differing.
- **J2 -- and the resolution improved.** At every budget from **5** to **20** the standard error of the mean over
  twenty replicates is at most **0.030**, against the **0.0232** to **0.0546** the same budgets showed at five.
  **Falsifier**: any budget above **0.035**, which would say four times the replicates bought less than the square
  root. **Null**: between.
- **J3 -- and the interval's spread is now above the instrument.** The band from **5** to **20** is at least
  **twice** the widest of those standard errors, so whatever the interval does, the instrument can see it.
  **Falsifier**: less than **1.5** times, which would say the floor is flat within the measurement at twenty
  replicates too. **Null**: between.
- **J4 -- and with the noise under it, the interval turns.** Over the budgets from **5** to **20** the series has
  exactly **one** minimum, strictly inside the interval, with the readings monotonically falling into it and
  monotonically rising out of it. **Falsifier**: a flat region at the minimum, two budgets within **0.02** there,
  the minimum at **5** or at **20**, or any rise on the way in or fall on the way out. This is `e388`'s I2 asked
  again where it can be decided: if the turn is real it survives the noise being halved, and if the interval is
  genuinely flat this is where that becomes a result rather than a resolution limit.
- **J5 -- and the floor is a fifth of the way below five.** The minimum over that interval is at least **0.02**
  below the reading at a budget of **5**. **Falsifier**: within **0.01**. **Null**: between. *`e388` met the same
  bar by 0.0208 at five replicates, where the standard error at the budget of 5 was 0.0440; the claim is worth
  making again only if it survives the error coming down.*

**What it can do beyond that.** It converts `e388`'s "the interval is one standard error wide" from a caveat into a
measurement with a verdict: either the turn appears when the error halves, or the interval is flat and the valley's
floor is a band rather than a point. Either answer closes the question `e385` opened when it registered that the
floor sat between five and twenty.

**What it cannot do.** *Eleven budgets are eleven samples*: the floor is bounded between two budgets and not located
to a step, and a turn inside a single update stays invisible. *And a smaller budget is a different run*: the batch
order, the head's fitting and any schedule depend on how many steps were taken, so the series is a sequence of runs
and not one run's history. *One cell and one draw*: the action source at `cue@0`, so the cue source and the tight
end are not resolved this way. *And a probe is not a mechanism*: a reading says how much of the label a linear fit
recovers from the world's eight numbers, so a floor is a shape in what is recoverable and not a named process.
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
from experiments.e382_when_the_world_loses_it import one_budget
from experiments.e388_the_floor_between_five_and_twenty import LOW, HIGH

#: the corpus's replicate count for a decisive cell, and every budget this unit rolls at it
REPS = 20
BUDGETS = (1, 2, 3, 4, 5, 6, 8, 11, 14, 17, 20)
RUNS = {b: {"run": Path(f"runs/e389_earned_label_iters{b}_cue0_actionsource_20reps.json"),
            "theta": Path(f"runs/e389_theta_{b}")} for b in BUDGETS}
#: `e388`'s artifact, which holds the five-replicate standard errors this unit's have to beat
PREVIOUS = Path("runs/e388_the_floor_between_five_and_twenty.json")
CHANCE = 0.25
SAME = 0.02
FIRES = 0.01
DEPTH = 0.02
RESOLVED = 0.030
UNRESOLVED = 0.035
ABOVE = 2.0
BETWEEN = 1.5
CLAIMS = (
    ("J1", "one configuration except the budget and the replicate count",
     "Each run agrees with `e385`'s budget-1 run on every recorded field, including the learning rate and the "
     "batch, differing in `iters` and in `repeats`",
     "falsifier: any other field differing"),
    ("J2", f"and the resolution improved, every error within {RESOLVED:.3f}",
     f"At every budget from {LOW} to {HIGH} the standard error over {REPS} replicates is at most {RESOLVED:.3f}",
     f"falsifier: any budget above {UNRESOLVED:.3f}; null: between {RESOLVED:.3f} and {UNRESOLVED:.3f}"),
    ("J3", f"and the interval's spread is above the instrument, by {ABOVE:.1f} times",
     f"The band from {LOW} to {HIGH} is at least {ABOVE:.1f} times the widest standard error there",
     f"falsifier: less than {BETWEEN:.1f} times; null: between {BETWEEN:.1f} and {ABOVE:.1f}"),
    ("J4", "and with the noise under it, the interval turns",
     f"Over the budgets from {LOW} to {HIGH} the series has exactly one minimum, strictly inside the interval, "
     "falling into it and rising out of it",
     f"falsifier: a flat region at the minimum, two budgets within {SAME:.2f} there, the minimum at an end, or any "
     "rise on the way in or fall on the way out"),
    ("J5", f"and the floor is a fifth of the way below five, by {DEPTH:.2f}",
     f"The minimum over that interval is at least {DEPTH:.2f} below the reading at a budget of {LOW}",
     f"falsifier: within {FIRES:.2f}; null: between {FIRES:.2f} and {DEPTH:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(runs: dict = RUNS, previous: Path = PREVIOUS, arm: str = NAIVE, reps: int = REPS) -> dict:
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
        accs = [float(v) for v in cell[("after_task_0", 0)]]
        out["budgets"][str(b)] = {"run": spec["run"].name, "iters": doc["config"].get("iters"),
                                  "repeats": doc["config"].get("repeats"),
                                  "probe_task_0": statistics.fmean(accs),
                                  "per_rep_task_0": accs,
                                  "sem_task_0": (statistics.stdev(accs) / len(accs) ** 0.5
                                                 if len(accs) > 1 else float("nan")),
                                  "initial_task_0": statistics.fmean(cell[("initial", 0)]),
                                  "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["facts"][str(b)] = {**_facts(doc), "lr": doc["config"].get("lr"), "batch": doc["config"].get("batch")}
    prev = load(previous)
    if prev:
        #: only the five-replicate standard errors are needed: they are the bar this unit's have to beat
        prev_sems = {int(k): float(v.get("sem_task_0", float("nan")))
                     for k, v in (prev.get("budgets") or {}).items()}
        out["previous"] = {"artifact": Path(previous).name, "reps": prev.get("reps"),
                           "sems": {str(k): v for k, v in prev_sems.items()},
                           "readings": {k: float(v.get("probe_task_0", float("nan")))
                                        for k, v in (prev.get("budgets") or {}).items()},
                           "band": prev.get("band"),
                           "facts": (prev.get("previous") or {}).get("facts") or {}}
    window = {b: v for b, v in _series(out, "readings").items() if LOW <= b <= HIGH}
    sems = {b: out["budgets"][str(b)]["sem_task_0"] for b in window if str(b) in out["budgets"]}
    out["band"] = {"budgets": sorted(window), "low": min(window.values()), "high": max(window.values()),
                   "span": max(window.values()) - min(window.values()),
                   "min_budget": min(window, key=lambda b: window[b]),
                   "sems": {str(k): v for k, v in sems.items()},
                   "worst_sem": max(sems.values(), default=float("nan")),
                   "five_rep_worst": ((prev or {}).get("band") or {}).get("worst_sem")}
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
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run or its weights is absent"}
                for c in CLAIMS]
    bud = {int(k): v for k, v in r["budgets"].items()}
    keys = ("lr", "batch", "iters", "repeats") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
    #: the reference is `e385`'s budget-1 run at five replicates, read through `e388`'s artifact
    ref = ((r.get("previous") or {}).get("facts") or {}).get("1") or {}
    differ = {}
    for b, entry in bud.items():
        facts = r["facts"][str(b)]
        differ[b] = {k: [facts.get(k), ref.get(k)] for k in keys if facts.get(k) != ref.get(k)}
    bad = {b: v for b, v in differ.items()
           if sorted(v) not in (["iters"], ["repeats"], ["iters", "repeats"])}
    j1 = {"id": "J1", "measured": f"each run against the reference configuration: "
                                  f"{ {b: sorted(v) for b, v in differ.items()} }",
          "verdict": "MET -- one configuration, and the budget and the replicate count are the only things that "
                     "move" if not bad else f"FALSIFIER FIRED -- {bad} differ beyond the budget and the replicates"}

    sems = {int(k): float(v) for k, v in (r.get("band") or {}).get("sems", {}).items()}
    if not sems:
        j2 = j3 = {"id": "J2", "measured": "no standard errors were computed", "verdict": "REFUSED"}
    else:
        worst = max(sems.values())
        five = (r.get("band") or {}).get("five_rep_worst")
        j2 = {"id": "J2", "measured": f"the standard errors over {r['reps']} replicates run "
                                      f"{min(sems.values()):.4f} to {worst:.4f}, against the five-replicate "
                                      f"worst of {five:.4f} at the same budgets",
              "verdict": f"MET -- the resolution improved, every error within {RESOLVED:.3f}" if worst <= RESOLVED
              else f"FALSIFIER FIRED -- the worst is {worst:.4f}: four times the replicates bought less than the "
                   f"square root" if worst > UNRESOLVED else
              f"NULL -- {worst:.4f}, between {RESOLVED:.3f} and {UNRESOLVED:.3f}"}
        span = float((r.get("band") or {}).get("span", float("nan")))
        ratio = span / worst if worst == worst and worst > 0 else float("nan")
        j3 = {"id": "J3", "measured": f"the band from {LOW} to {HIGH} spans {span:.4f} against the widest standard "
                                      f"error there, {worst:.4f}, so the spread is {ratio:.2f} times it",
              "verdict": f"MET -- the interval's spread is above the instrument, {ratio:.2f} times" if ratio >= ABOVE
              else f"FALSIFIER FIRED -- only {ratio:.2f} times: the floor is flat within the measurement at {REPS} "
                   f"replicates too" if ratio < BETWEEN else
              f"NULL -- {ratio:.2f}, between {BETWEEN:.1f} and {ABOVE:.1f}"}

    series = _series(r, "readings")
    window = {b: v for b, v in sorted(series.items()) if LOW <= b <= HIGH}
    ordered = sorted(window)
    if len(window) < 3:
        low = None
        j4 = {"id": "J4", "measured": "fewer than three budgets between five and twenty are available",
              "verdict": "REFUSED -- the interval this claim is about is not sampled"}
        j5 = {"id": "J5", "measured": "fewer than three budgets between five and twenty are available",
              "verdict": "REFUSED -- the interval this claim is about is not sampled"}
    else:
        low = min(ordered, key=lambda b: window[b])
        flat = [b for b in ordered if b != low and abs(window[b] - window[low]) < SAME]
        at = ordered.index(low)
        falls = all(window[ordered[i]] > window[ordered[i + 1]] for i in range(at))
        rises = all(window[ordered[i]] < window[ordered[i + 1]] for i in range(at, len(ordered) - 1))
        interior = low not in (LOW, HIGH)
        good = interior and not flat and falls and rises
        j4 = {"id": "J4", "measured": f"the readings over the budgets {ordered} are "
                                      f"{[round(window[b], 4) for b in ordered]}, with the minimum at {low} "
                                      f"(interior: {interior}), {flat} within {SAME:.2f} of it, a strict fall in "
                                      f"{falls} and a strict rise out {rises}",
              "verdict": f"MET -- the interval turns, at a budget of {low}" if good else
              f"FALSIFIER FIRED -- the minimum is at {low}, with {flat} within {SAME:.2f} of it, or the series "
              f"neither falls into it strictly nor rises out of it strictly"}
        depth = window[LOW] - window[low] if LOW in window else None
        j5 = {"id": "J5", "measured": f"the floor is {window[low]:.4f} at a budget of {low} and the reading at a "
                                      f"budget of {LOW} is {window[LOW]:.4f}, so the dip is {depth:+.4f} deep"
              if depth is not None else f"the reading at a budget of {LOW} is missing",
              "verdict": f"MET -- the floor is a fifth of the way below five, {depth:+.4f}"
              if depth is not None and depth >= DEPTH else
              f"FALSIFIER FIRED -- only {depth:+.4f}: five is the floor" if depth is not None and depth < FIRES else
              f"NULL -- {depth:+.4f}, between {FIRES:.2f} and {DEPTH:.2f}" if depth is not None else
              "REFUSED -- the comparison this claim makes is not computable"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the interval at twenty replicates ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the interval at twenty replicates ==")
    print(f"   the wide step's first task at eleven budgets rolled again at {r['reps']} replicates on the "
          f"`{r['arm']}` arm, against `e388`'s five-replicate standard errors")
    series = _series(r, "readings")
    heads = _series(r, "heads")
    print(f"\n   {'iters':>7} {'probe':>9} {'head':>8} {'sem':>8} {'5-rep sem':>10}")
    five = (r.get("previous") or {}).get("sems") or {}
    for b in sorted(series):
        here = r["budgets"].get(str(b)) or {}
        print(f"   {b:>7} {series[b]:9.4f} {heads.get(b, float('nan')):8.4f} "
              f"{here.get('sem_task_0', float('nan')):8.4f} {float(five.get(str(b), float('nan'))):10.4f}")

    band = r.get("band") or {}
    if band:
        ratio = band["span"] / band["worst_sem"] if band["worst_sem"] else float("nan")
        print(f"\n   the interval {LOW} to {HIGH}: readings {band['low']:.4f} to {band['high']:.4f}, a band "
              f"{band['span']:.4f} wide, lowest at a budget of {band['min_budget']}; the widest standard error "
              f"there is {band['worst_sem']:.4f} against {band['five_rep_worst']:.4f} at five replicates, so the "
              f"band is {ratio:.2f} times it")

    print("\n== the registered claims, J1-J5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e388` found the interval from five to twenty to be one standard error wide and registered twenty")
    print("    replicates as what would resolve it; this rolls the whole series again at that count)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reps", type=int, default=REPS)
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
