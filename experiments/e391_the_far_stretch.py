"""E391 -- the far stretch: the four hundred updates between the hundredth and the five-hundredth.

`e390` put the wide step's first task on one trajectory at one replicate count -- the floor at fourteen reading
**0.5479**, the bottom flat to thirty, a hundred reading **0.6385** -- and named the largest gap it left: *"the
stretch from a hundred to five hundred is four hundred updates wide and holds most of the recovery, so it is the
largest unmeasured gap in the trajectory."*

**This unit samples it.** Three budgets between the ends -- **150**, **275**, **425** -- the same cell and rate at
the corpus's twenty replicates, with the hundred point read from `e390`'s artifact and the five-hundred point rolled
from `e380`'s saved bodies. The connectome's own weights read **0.6875** on these examples.

Five claims, registered before any of the new runs' readings was opened.

- **L1 -- one configuration except the budget.** Each new run agrees with `e385`'s budget-1 run, read through
  `e390`'s artifact, on every recorded field including the learning rate and the batch, differing in `iters` alone;
  `e380`'s own run differs in `iters` alone too. **Falsifier**: any other field differing.
- **L2 -- and the stretch ends higher than it starts.** The reading at a budget of **500** exceeds the reading at a
  budget of **100** by at least **0.05**. **Falsifier**: within **0.02**, which would say the four hundred updates
  between them buy nothing. **Null**: between. *The bar is smaller than `e390`'s for the same pair because this is
  the smaller half of the trajectory: `e390` measured 0.1990 from twenty to five hundred, and the floor-to-hundred
  leg accounts for 0.0906 of it.*
- **L3 -- and it rises at every sample on the way.** Over the five sampled budgets from **100** to **500** the series
  rises strictly: each is above the one before. **Falsifier**: any budget not above its predecessor, which would say
  the far stretch is a set of excursions rather than a climb.
- **L4 -- and the stretch is above the instrument.** The span from the lowest to the highest reading over those five
  budgets is at least **three times** the widest standard error among them. **Falsifier**: less than **two** times,
  which would say the stretch is inside the measurement. **Null**: between.
- **L5 -- and the recovery after a hundred is more than half of it.** The gain from **100** to **500** is more than
  **half** the whole gain from `e390`'s floor, **0.5479**, to five hundred. **Falsifier**: at or under a half, which
  would say the recovery is front-loaded on the floor-to-hundred leg. *This is `e390`'s reported sentence -- "most of
  the recovery happens after a hundred updates" -- made a registered claim rather than a remark.*

**What it can do beyond that.** With `e389` and `e390` it closes the wide step's first task as a measured
trajectory from one update to five hundred: the descent, the floor, the flat bottom, the first climb and the far
stretch each sampled, at one replicate count, against the connectome's own 0.6875.

**What it cannot do.** *Three budgets are three samples*: the stretch is bounded between samples and a turn inside
one of the gaps stays invisible, and two hundred updates is the widest gap left. *And a smaller budget is a
different run*: the batch order, the head's fitting and any schedule depend on how many steps were taken, so this is
a sequence of runs and not one run's history. *One cell and one draw*: the action source at `cue@0`, so the cue
source and the tight end are not resolved this way. *And a probe is not a mechanism*: a reading says how much of the
label a linear fit recovers from the world's eight numbers, so a climb is a shape in what is recoverable and not a
named process.
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
from experiments.e390_where_the_climb_starts import FAR_AT, FAR as FAR_END, FLOOR, NEAR_AT  # noqa: F401

#: the budgets this unit adds, inside the four hundred updates `e390` left unmeasured
NEW = (150, 275, 425)
RUNS = {b: {"run": Path(f"runs/e391_earned_label_iters{b}_cue0_actionsource_20reps.json"),
            "theta": Path(f"runs/e391_theta_{b}")} for b in NEW}
#: the two ends: `e390` for the hundred point, which carries its own standard error, and `e380` for five hundred
NEAR = Path("runs/e390_where_the_climb_starts.json")
FAR = {"run": FAR_END["run"], "theta": FAR_END["theta"]}
NEAR_LOW, NEAR_HIGH = 100, FAR_AT
REPS = 20
GAIN = 0.05
FIRES = 0.02
ABOVE = 3.0
BETWEEN = 2.0
CLAIMS = (
    ("L1", "one configuration except the budget",
     "Each new run agrees with `e385`'s budget-1 run on every recorded field, including the learning rate and the "
     "batch, differing in `iters` alone, and so does `e380`'s own run",
     "falsifier: any other field differing"),
    ("L2", f"and the stretch ends higher than it starts, by {GAIN:.2f}",
     f"The reading at a budget of {NEAR_HIGH} exceeds the reading at a budget of {NEAR_LOW} by at least {GAIN:.2f}",
     f"falsifier: within {FIRES:.2f}; null: between {FIRES:.2f} and {GAIN:.2f}"),
    ("L3", "and it rises at every sample on the way",
     f"Over the five sampled budgets from {NEAR_LOW} to {NEAR_HIGH} the series rises strictly at every step",
     "falsifier: any budget not above its predecessor"),
    ("L4", f"and the stretch is above the instrument, by {ABOVE:.1f} times",
     f"The span from the lowest to the highest reading over those budgets is at least {ABOVE:.1f} times the widest "
     "standard error among them",
     f"falsifier: less than {BETWEEN:.1f} times; null: between {BETWEEN:.1f} and {ABOVE:.1f}"),
    ("L5", "and the recovery after a hundred is more than half of it",
     f"The gain from {NEAR_LOW} to {NEAR_HIGH} is more than half the gain from the floor of {FLOOR:.4f} to "
     f"{NEAR_HIGH}",
     "falsifier: at or under a half, which would say the recovery is front-loaded on the floor-to-hundred leg"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(runs: dict = RUNS, near: Path = NEAR, far: dict = FAR, arm: str = NAIVE, reps: int = REPS) -> dict:
    from clfly.network.model import RateConfig, build_net

    circ, rs, loop_env, tasks = setup_wide()
    model = build_net(circ, RateConfig(tau=TAU)).torch_model()
    ctx = (model, loop_env, tasks, circ.n_neurons)
    out = {"ok": True, "reason": None, "budgets": {}, "facts": {}, "ends": {}, "arm": arm, "reps": reps}
    for b, spec in runs.items():
        doc = load(spec["run"])
        if not doc:
            return {**out, "ok": False, "reason": f"budget {b}: the artifact is absent"}
        got = one_budget(doc, spec["theta"], ctx, arm=arm, reps=reps)
        if not got.get("ok"):
            return {**out, "ok": False, "reason": f"budget {b}: {got['reason']}"}
        accs = [float(v) for v in got["cell"][("after_task_0", 0)]]
        out["budgets"][str(b)] = {"run": spec["run"].name, "iters": doc["config"].get("iters"),
                                  "repeats": doc["config"].get("repeats"),
                                  "probe_task_0": statistics.fmean(accs),
                                  "per_rep_task_0": accs,
                                  "sem_task_0": (statistics.stdev(accs) / len(accs) ** 0.5
                                                 if len(accs) > 1 else float("nan")),
                                  "head_task_0": float(doc["methods"][arm]["replicates"][0]["learned"][0])}
        out["facts"][str(b)] = {**_facts(doc), "lr": doc["config"].get("lr"), "batch": doc["config"].get("batch")}

    near_doc = load(near)
    if not near_doc:
        return {**out, "ok": False, "reason": f"{near} is absent, so the near end of the stretch is not on disk"}
    nb = (near_doc.get("budgets") or {}).get(str(NEAR_LOW))
    if not nb:
        return {**out, "ok": False, "reason": f"{near} does not carry a budget of {NEAR_LOW}"}
    out["ends"][str(NEAR_LOW)] = {"source": Path(near).name, "probe_task_0": float(nb["probe_task_0"]),
                                  "sem_task_0": float(nb.get("sem_task_0", float("nan")))}
    out["reference"] = {"artifact": Path(near).name, "facts": ((near_doc.get("reference") or {}).get("facts") or {})}

    far_doc = load(far["run"])
    if not far_doc:
        return {**out, "ok": False, "reason": f"{far['run']} is absent, so the far end of the stretch is not on disk"}
    got = one_budget(far_doc, far["theta"], ctx, arm=arm, reps=reps)
    if not got.get("ok"):
        return {**out, "ok": False, "reason": f"budget {FAR_AT}: {got['reason']}"}
    accs = [float(v) for v in got["cell"][("after_task_0", 0)]]
    out["ends"][str(FAR_AT)] = {"source": Path(far["run"]).name, "probe_task_0": statistics.fmean(accs),
                                "sem_task_0": (statistics.stdev(accs) / len(accs) ** 0.5
                                               if len(accs) > 1 else float("nan")),
                                "head_task_0": float(far_doc["methods"][arm]["replicates"][0]["learned"][0])}
    out["facts"][str(FAR_AT)] = {**_facts(far_doc), "lr": far_doc["config"].get("lr"),
                                 "batch": far_doc["config"].get("batch")}
    series = _series(out)
    window = {b: v for b, v in series.items() if NEAR_LOW <= b <= NEAR_HIGH}
    out["stretch"] = {"budgets": sorted(window), "low": min(window.values()), "high": max(window.values()),
                      "span": max(window.values()) - min(window.values()),
                      "sems": {str(b): _sem(out, b) for b in window},
                      "worst_sem": max((_sem(out, b) for b in window), default=float("nan")),
                      "gain": series[NEAR_HIGH] - series[NEAR_LOW],
                      "whole": series[NEAR_HIGH] - FLOOR,
                      "front_loaded": (series[NEAR_LOW] - FLOOR)}
    return out


def _sem(r: dict, b: int) -> float:
    if str(b) in r["budgets"]:
        return float(r["budgets"][str(b)]["sem_task_0"])
    return float((r.get("ends") or {}).get(str(b), {}).get("sem_task_0", float("nan")))


def _series(r: dict) -> dict:
    out = {int(k): float(v["probe_task_0"]) for k, v in (r.get("ends") or {}).items()}
    out.update({int(k): float(v["probe_task_0"]) for k, v in (r.get("budgets") or {}).items()})
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- a run, its weights or an end is absent"}
                for c in CLAIMS]
    ref = ((r.get("reference") or {}).get("facts") or {}).get("1") or {}
    keys = ("lr", "batch", "iters", "repeats") + tuple(SHARED) + tuple(FOLLOWS_FROM_THE_SOURCE)
    differ = {}
    for b in {int(k) for k in r["facts"]}:
        facts = r["facts"][str(b)]
        differ[b] = {k: [facts.get(k), ref.get(k)] for k in keys if facts.get(k) != ref.get(k)}
    bad = {b: v for b, v in differ.items() if sorted(v) not in (["iters"], ["iters", "repeats"])}
    j1 = {"id": "L1", "measured": f"each run against the reference configuration: "
                                  f"{ {b: sorted(v) for b, v in differ.items()} }",
          "verdict": "MET -- one configuration, and the budget is the only thing that moves" if not bad else
          f"FALSIFIER FIRED -- {bad} differ beyond the budget"}

    series = _series(r)
    stretch = r.get("stretch") or {}
    if NEAR_LOW not in series or NEAR_HIGH not in series:
        j2 = {"id": "L2", "measured": "an end of the stretch is missing", "verdict": "REFUSED"}
    else:
        gap = series[NEAR_HIGH] - series[NEAR_LOW]
        j2 = {"id": "L2", "measured": f"the reading at a budget of {NEAR_HIGH} is {series[NEAR_HIGH]:.4f} against "
                                      f"{series[NEAR_LOW]:.4f} at {NEAR_LOW}, so the stretch ends {gap:+.4f} higher",
              "verdict": f"MET -- the stretch ends higher than it starts, {gap:+.4f}" if gap >= GAIN else
              f"FALSIFIER FIRED -- only {gap:+.4f}: the four hundred updates buy nothing" if gap < FIRES else
              f"NULL -- {gap:+.4f}, between {FIRES:.2f} and {GAIN:.2f}"}

    window = sorted(b for b in series if NEAR_LOW <= b <= NEAR_HIGH)
    readings = [series[b] for b in window]
    if len(window) < 3:
        j3 = j4 = {"id": "L3", "measured": "fewer than three budgets between a hundred and five hundred are available",
                   "verdict": "REFUSED -- the stretch this claim is about is not sampled"}
    else:
        drops = [window[i] for i in range(len(window) - 1) if readings[i + 1] <= readings[i]]
        j3 = {"id": "L3", "measured": f"the readings over the budgets {window} are "
                                      f"{[round(v, 4) for v in readings]}, with {drops} not above their predecessors",
              "verdict": "MET -- it rises at every sample on the way" if not drops else
              f"FALSIFIER FIRED -- the stretch is not monotone: {drops} are not above their predecessors"}
        span = max(readings) - min(readings)
        worst = float(stretch.get("worst_sem", float("nan")))
        ratio = span / worst if worst == worst and worst > 0 else float("nan")
        j4 = {"id": "L4", "measured": f"the span over those budgets is {span:.4f} against the widest standard error "
                                      f"there, {worst:.4f}, so the stretch is {ratio:.2f} times it",
              "verdict": f"MET -- the stretch is above the instrument, {ratio:.2f} times" if ratio >= ABOVE else
              f"FALSIFIER FIRED -- only {ratio:.2f} times: the stretch is inside the measurement" if ratio < BETWEEN
              else f"NULL -- {ratio:.2f}, between {BETWEEN:.1f} and {ABOVE:.1f}"}

    if NEAR_LOW not in series or NEAR_HIGH not in series:
        j5 = {"id": "L5", "measured": "an end of the stretch is missing", "verdict": "REFUSED"}
    else:
        gain = series[NEAR_HIGH] - series[NEAR_LOW]
        whole = series[NEAR_HIGH] - FLOOR
        share = gain / whole if whole else float("nan")
        j5 = {"id": "L5", "measured": f"the stretch gains {gain:+.4f} against {series[NEAR_LOW] - FLOOR:+.4f} from "
                                      f"the floor to a hundred and {whole:+.4f} in all, so {100 * share:.1f}% of the "
                                      f"recovery is after a hundred",
              "verdict": f"MET -- the recovery after a hundred is more than half of it, {100 * share:.1f}%" if
              share > 0.5 else
              f"FALSIFIER FIRED -- {100 * share:.1f}% of the recovery is after a hundred: it is front-loaded"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== the far stretch ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the far stretch ==")
    print(f"   the wide step's first task at three budgets inside the four hundred updates `e390` left open, between "
          f"its hundred and `e380`'s five hundred, at {r['reps']} replicates on the `{r['arm']}` arm")
    series = _series(r)
    print(f"\n   {'iters':>7} {'probe':>9} {'sem':>8} {'head':>8}  {'new':>4}")
    for b in sorted(series):
        here = r["budgets"].get(str(b)) or (r.get("ends") or {}).get(str(b)) or {}
        print(f"   {b:>7} {series[b]:9.4f} {_sem(r, b):8.4f} {here.get('head_task_0', float('nan')):8.4f}  "
              f"{'*' if b in NEW else '':>4}")

    stretch = r.get("stretch") or {}
    if stretch:
        ratio = stretch["span"] / stretch["worst_sem"] if stretch["worst_sem"] else float("nan")
        print(f"\n   the stretch from {NEAR_LOW} to {NEAR_HIGH}: readings {stretch['low']:.4f} to "
              f"{stretch['high']:.4f}, a span of {stretch['span']:.4f} against the widest standard error there, "
              f"{stretch['worst_sem']:.4f}, {ratio:.2f} times it; the floor is {FLOOR:.4f} and the stretch's gain is "
              f"{stretch['gain']:+.4f} of the {stretch['whole']:+.4f} from the floor to five hundred")

    print("\n== the registered claims, L1-L5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e390` named the four hundred updates between a hundred and five hundred as the largest unmeasured")
    print("    gap in the wide step's trajectory; this samples three budgets inside it)")
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
