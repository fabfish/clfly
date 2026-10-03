"""E390 -- where the climb starts: the wide step's recovery sampled between twenty updates and five hundred.

`e389` rolled the wide step's first task at twenty replicates from one update to twenty and located the floor at a
budget of **14**, reading **0.5479**. It also showed that the recovery off that floor is flat: 17 and 20 both read
**0.5740**. The corpus's far end is `e380`'s twenty-replicate run at **500** updates, which reads **0.7792** in
`e384`'s series, so between a flat twenty and a recovered five hundred there is a climb of about **0.21** and
nothing between the two budgets samples it. `e389`'s finding registered exactly that: *"the flat recovery covers at
least three budgets and where the climb to 0.7000 at a hundred starts is left open."*

**This unit samples it.** Five budgets between the ends -- **30**, **45**, **65**, **85**, **100** -- the same cell
and rate at the corpus's twenty replicates, with the twenty point read from `e389`'s artifact and the five-hundred
point rolled from `e380`'s saved bodies, so the ends are the units that measured them. The connectome's own weights
read **0.6875** on these examples.

Five claims, registered before any of the new runs' readings was opened.

- **K1 -- one configuration except the budget.** Each new run agrees with `e385`'s budget-1 run, read through
  `e389`'s artifact, on every recorded field including the learning rate and the batch, differing in `iters` alone;
  `e380`'s own run differs in `iters` alone too. **Falsifier**: any other field differing.
- **K2 -- and the far end is above the near end.** The reading at a budget of **500** exceeds the reading at a
  budget of **20** by at least **0.10**. **Falsifier**: within **0.05**, which would say the recovery attributed to
  five hundred updates is not there. **Null**: between. *This is the claim the interval exists inside, and `e384`'s
  five-replicate series stated the same gap as 0.1917 without ever testing it at twenty.*
- **K3 -- and the climb is under way by a hundred.** The reading at a budget of **100** exceeds `e389`'s floor,
  **0.5479**, by at least **0.05**. **Falsifier**: within **0.02**, which would say a hundred updates have not
  lifted the body off the floor. **Null**: between.
- **K4 -- and it rises at every sample on the way.** Over the six sampled budgets from **20** to **100** the series
  rises strictly: each is above the one before. **Falsifier**: any budget not above its predecessor, which would say
  the recovery is not a monotone climb but a set of excursions.
- **K5 -- and the climb is above the instrument.** The span from the lowest to the highest reading over those six
  budgets is at least **three times** the widest standard error among them. **Falsifier**: less than **two** times,
  which would say the climb is inside the measurement the way `e388` found the floor to be. **Null**: between.

**What it can do beyond that.** It closes the last open question the valley's shape left -- the corpus knows the
wide step's reading at one, at five, at fourteen, at twenty and at five hundred, and this puts readings between the
last two so the recovery has a shape rather than two ends. Together with `e389` it makes the wide step's first task
a measured trajectory from one update to five hundred, at one replicate count.

**What it cannot do.** *Five budgets are five samples*: where between two of them a climb starts is bounded and not
located, and a step inside one budget stays invisible. *And a smaller budget is a different run*: the batch order,
the head's fitting and any schedule depend on how many steps were taken, so this is a sequence of runs and not one
run's history. *One cell and one draw*: the action source at `cue@0`, so the cue source and the tight end are not
resolved this way. *And a probe is not a mechanism*: a reading says how much of the label a linear fit recovers from
the world's eight numbers, so a climb is a shape in what is recoverable and not a named process.
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
from experiments.e388_the_floor_between_five_and_twenty import LOW, HIGH  # noqa: F401  (the interval's own ends)

#: the budgets this unit adds, between `e389`'s flat twenty and `e380`'s five hundred
NEW = (30, 45, 65, 85, 100)
RUNS = {b: {"run": Path(f"runs/e390_earned_label_iters{b}_cue0_actionsource_20reps.json"),
            "theta": Path(f"runs/e390_theta_{b}")} for b in NEW}
#: the two ends: `e389` for the twenty point, which carries its own standard error, and `e380` for five hundred
NEAR = Path("runs/e389_the_interval_at_twenty_replicates.json")
FAR = {"run": Path("runs/e380_earned_label_cue0_actionsource_20reps.json"), "theta": Path("runs/e380_theta")}
REPS = 20
NEAR_AT, FAR_AT = 20, 500
FLOOR = 0.5479
CHANCE = 0.25
CLIMB = 0.10
FIRES = 0.05
LIFT = 0.05
LIFT_FIRES = 0.02
ABOVE = 3.0
BETWEEN = 2.0
CLAIMS = (
    ("K1", "one configuration except the budget",
     "Each new run agrees with `e385`'s budget-1 run on every recorded field, including the learning rate and the "
     "batch, differing in `iters` alone, and so does `e380`'s own run",
     "falsifier: any other field differing"),
    ("K2", f"and the far end is above the near end, by {CLIMB:.2f}",
     f"The reading at a budget of {FAR_AT} exceeds the reading at a budget of {NEAR_AT} by at least {CLIMB:.2f}",
     f"falsifier: within {FIRES:.2f}; null: between {FIRES:.2f} and {CLIMB:.2f}"),
    ("K3", f"and the climb is under way by a hundred, by {LIFT:.2f}",
     f"The reading at a budget of 100 exceeds `e389`'s floor of {FLOOR:.4f} by at least {LIFT:.2f}",
     f"falsifier: within {LIFT_FIRES:.2f}; null: between {LIFT_FIRES:.2f} and {LIFT:.2f}"),
    ("K4", "and it rises at every sample on the way",
     f"Over the six sampled budgets from {NEAR_AT} to 100 the series rises strictly at every step",
     "falsifier: any budget not above its predecessor"),
    ("K5", f"and the climb is above the instrument, by {ABOVE:.1f} times",
     f"The span from the lowest to the highest reading over those budgets is at least {ABOVE:.1f} times the widest "
     "standard error among them",
     f"falsifier: less than {BETWEEN:.1f} times; null: between {BETWEEN:.1f} and {ABOVE:.1f}"),
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
        return {**out, "ok": False, "reason": f"{near} is absent, so the near end of the climb is not on disk"}
    nb = (near_doc.get("budgets") or {}).get(str(NEAR_AT))
    if not nb:
        return {**out, "ok": False, "reason": f"{near} does not carry a budget of {NEAR_AT}"}
    out["ends"][str(NEAR_AT)] = {"source": Path(near).name, "probe_task_0": float(nb["probe_task_0"]),
                                 "sem_task_0": float((near_doc.get("band") or {}).get("sems", {}).get(str(NEAR_AT),
                                                                                                      float("nan"))),
                                 "floor": float((near_doc.get("band") or {}).get("low", float("nan")))}
    out["reference"] = {"artifact": Path(near).name, "facts": ((near_doc.get("previous") or {}).get("facts") or {})}

    far_doc = load(far["run"])
    if not far_doc:
        return {**out, "ok": False, "reason": f"{far['run']} is absent, so the far end of the climb is not on disk"}
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
    span = _series(out)
    window = {b: v for b, v in span.items() if NEAR_AT <= b <= 100}
    out["climb"] = {"budgets": sorted(window), "low": min(window.values()), "high": max(window.values()),
                    "span": max(window.values()) - min(window.values()),
                    "sems": {str(b): _sem(out, b) for b in window},
                    "worst_sem": max((_sem(out, b) for b in window), default=float("nan"))}
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
    for b, entry in {int(k): v for k, v in r["facts"].items()}.items():
        facts = r["facts"][str(b)]
        differ[b] = {k: [facts.get(k), ref.get(k)] for k in keys if facts.get(k) != ref.get(k)}
    bad = {b: v for b, v in differ.items() if sorted(v) not in (["iters"], ["iters", "repeats"])}
    j1 = {"id": "K1", "measured": f"each run against the reference configuration: "
                                  f"{ {b: sorted(v) for b, v in differ.items()} }",
          "verdict": "MET -- one configuration, and the budget is the only thing that moves" if not bad else
          f"FALSIFIER FIRED -- {bad} differ beyond the budget"}

    series = _series(r)
    climb = r.get("climb") or {}
    if NEAR_AT not in series or FAR_AT not in series:
        j2 = {"id": "K2", "measured": "an end of the climb is missing", "verdict": "REFUSED"}
    else:
        gap = series[FAR_AT] - series[NEAR_AT]
        j2 = {"id": "K2", "measured": f"the reading at a budget of {FAR_AT} is {series[FAR_AT]:.4f} against "
                                      f"{series[NEAR_AT]:.4f} at {NEAR_AT}, so the far end is {gap:+.4f} above",
              "verdict": f"MET -- the far end is above the near end, {gap:+.4f}" if gap >= CLIMB else
              f"FALSIFIER FIRED -- only {gap:+.4f}: the recovery attributed to five hundred updates is not there"
              if gap < FIRES else f"NULL -- {gap:+.4f}, between {FIRES:.2f} and {CLIMB:.2f}"}

    if 100 not in series:
        j3 = {"id": "K3", "measured": "the budget of a hundred is missing", "verdict": "REFUSED"}
    else:
        lift = series[100] - FLOOR
        j3 = {"id": "K3", "measured": f"the reading at a budget of 100 is {series[100]:.4f} against the floor's "
                                      f"{FLOOR:.4f}, so it is {lift:+.4f} above it",
              "verdict": f"MET -- the climb is under way by a hundred, {lift:+.4f}" if lift >= LIFT else
              f"FALSIFIER FIRED -- only {lift:+.4f}: a hundred updates have not lifted the body off the floor"
              if lift < LIFT_FIRES else f"NULL -- {lift:+.4f}, between {LIFT_FIRES:.2f} and {LIFT:.2f}"}

    window = sorted(b for b in series if NEAR_AT <= b <= 100)
    readings = [series[b] for b in window]
    if len(window) < 3:
        j4 = j5 = {"id": "K4", "measured": "fewer than three budgets between twenty and a hundred are available",
                   "verdict": "REFUSED -- the interval this claim is about is not sampled"}
    else:
        drops = [window[i] for i in range(len(window) - 1) if readings[i + 1] <= readings[i]]
        good = not drops
        j4 = {"id": "K4", "measured": f"the readings over the budgets {window} are "
                                      f"{[round(v, 4) for v in readings]}, with {drops} not above their "
                                      f"predecessors",
              "verdict": "MET -- it rises at every sample on the way" if good else
              f"FALSIFIER FIRED -- the climb is not monotone: {drops} are not above their predecessors"}
        span = max(readings) - min(readings)
        worst = float(climb.get("worst_sem", float("nan")))
        ratio = span / worst if worst == worst and worst > 0 else float("nan")
        j5 = {"id": "K5", "measured": f"the span over those budgets is {span:.4f} against the widest standard error "
                                      f"there, {worst:.4f}, so the climb is {ratio:.2f} times it",
              "verdict": f"MET -- the climb is above the instrument, {ratio:.2f} times" if ratio >= ABOVE else
              f"FALSIFIER FIRED -- only {ratio:.2f} times: the climb is inside the measurement" if ratio < BETWEEN
              else f"NULL -- {ratio:.2f}, between {BETWEEN:.1f} and {ABOVE:.1f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    if not r.get("ok"):
        print("== where the climb starts ==")
        print(f"   REFUSED -- {r.get('reason', 'a run is absent')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== where the climb starts ==")
    print(f"   the wide step's first task at five budgets between `e389`'s twenty and `e380`'s five hundred, at "
          f"{r['reps']} replicates on the `{r['arm']}` arm")
    series = _series(r)
    print(f"\n   {'iters':>7} {'probe':>9} {'sem':>8} {'head':>8}  {'new':>4}")
    for b in sorted(series):
        here = r["budgets"].get(str(b)) or (r.get("ends") or {}).get(str(b)) or {}
        print(f"   {b:>7} {series[b]:9.4f} {_sem(r, b):8.4f} {here.get('head_task_0', float('nan')):8.4f}  "
              f"{'*' if b in NEW else '':>4}")

    climb = r.get("climb") or {}
    if climb:
        ratio = climb["span"] / climb["worst_sem"] if climb["worst_sem"] else float("nan")
        print(f"\n   the climb from {NEAR_AT} to 100: readings {climb['low']:.4f} to {climb['high']:.4f}, a span of "
              f"{climb['span']:.4f} against the widest standard error there, {climb['worst_sem']:.4f}, "
              f"{ratio:.2f} times it; the floor `e389` located is {FLOOR:.4f}")

    print("\n== the registered claims, K1-K5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e389` found the recovery off the floor flat by twenty and registered that where the climb to a")
    print("    hundred starts was left open; this samples five budgets between the two ends)")
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
