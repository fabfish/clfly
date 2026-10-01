"""E334 -- what replay is actually scored on: the loss on its stored features, under two worlds.

`e333` gave the world a transition rule and measured `replay`'s retention moving in **opposite directions** under the
thread's last two changes to the world's channel -- **falling 0.0292 at 2.89 sigma** when the response became a
*state* (`e332`), and **rising 0.0375 at 2.45 sigma** when that state acquired a *rule* (`e333`). Both were the only
resolved moves in their tables, and both were `replay`'s. `e333`'s finding named what it could not test:

    "`replay` carries replayed activations, so its stored features are features of a world; change the world's
    response and the features are stale in a new way, which can cost retention (the rule) or -- less obviously --
    help it (the state). Both signs are measurements, neither is a mechanism, and separating them needs the stored
    features read out, which nothing here does."

**This reads them out.** `train_task` now takes a `replay_probe` dict and records the loss on the stored replay
features at the **first** and the **last** training iteration of each task; `run_method` keeps it per task in the
replicate record as `replay_loss`. That is the staleness in the units the arm is trained in, at a cost of two floats
per task, and it is recorded for every method and empty for the ones that store nothing.

Two runs, `replay` alone, five replicates each, on the same two worlds `e333` compared -- **`leak = 1.0`** (the
instantaneous world) and **`leak = 0.35`** (the carried one) -- with the same seeds, so every contrast is paired by
replicate index and by task.

Four claims, registered before these runs' readings.

- **T1 -- one configuration except the rule.** Same circuit, read-out fingerprint, task names, replicate counts,
  cue symbols, cue noise and environment draw, the last differing only in the leak. **Falsifier**: any other field
  differing.
- **T2 -- and the stored features are staler in the world with a rule.** The **last-iteration replay loss**,
  averaged over tasks 1 and 2 and paired by replicate, is **higher** in the carried world by at least **0.05**.
  This is the mechanism `e333` named, in its own units: if the features are features of a world, changing the world
  leaves them worse fitted. **Falsifier**: lower by 0.05 or more, which would put the sign the other way and make
  `e333`'s retention move a consequence of something else. **Null**: within 0.05.
- **T3 -- and the staleness grows within a task's training, more in the carried world.** The rise from the first to
  the last iteration is **larger** in the carried world by at least **0.05**. **Falsifier**: smaller by 0.05.
  **Null**: within.
- **T4 -- and the loss rises at all in both worlds.** Within each run the last-iteration loss exceeds the first by
  at least **0.02**, averaged over tasks 1 and 2 -- the sanity check that the quantity is doing anything. This is
  the one claim of the four that is a claim about both runs rather than about their difference, and it is the one
  that can fail for the least interesting reason. **Falsifier**: a rise below 0.02 in either world.

**What it cannot do.** *One arm and one pair of worlds*: `naive`, `ewc` and the block arms are not run, and only
`e333`'s two leaks are compared, so the **other** sign `e332` measured -- retention *improving* when the world's
response became a state -- is not asked here at all. *Two scalars per task*: the loss on the stored features is
recorded at the first and last iteration and not through training, so a non-monotone history is invisible.
*The probe is the training loss itself*, so it is measured on the same batch schedule the arm trains on and not on a
held-out replay set. *And the stored features are not read out*: this measures how well they are fitted, and not
what they are, so a change that makes them *different* without making them worse fitted is invisible to it.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

RUNS = Path("runs")
PATHS = {"instant": RUNS / "e334_replay_instant.json", "carry": RUNS / "e334_replay_carry.json"}
ORDER = ("instant", "carry")
LEAKS = {"instant": 1.0, "carry": 0.35}
ARM = "replay"
#: the tasks after the first, being the ones with a buffer to replay -- task 0's entries are empty by construction
TASKS = (1, 2)
BAR = 0.05
STILL = 0.02
CLAIMS = (
    ("T1", "one configuration except the rule",
     "Same circuit, read-out fingerprint, task names, replicate counts, cue symbols, cue noise and environment draw, "
     "the last differing only in the leak",
     "falsifier: any other field differing"),
    ("T2", f"and the stored features are staler in the world with a rule, by {BAR:.2f}",
     f"The last-iteration replay loss, averaged over tasks {TASKS} and paired by replicate, is higher in the carried "
     f"world by at least {BAR:.2f}",
     f"falsifier: lower by {BAR:.2f} or more, which would put the sign the other way"),
    ("T3", f"and the within-task staleness grows more there, by {BAR:.2f}",
     f"The rise from the first to the last iteration is larger in the carried world by at least {BAR:.2f}",
     f"falsifier: smaller by {BAR:.2f}"),
    ("T4", f"and the loss rises at all in both worlds, by {STILL:.2f}",
     f"Within each run the last-iteration loss exceeds the first by at least {STILL:.2f}, averaged over tasks "
     f"{TASKS}",
     f"falsifier: a rise below {STILL:.2f} in either world"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(run: dict | None, arm: str = ARM) -> list[dict]:
    if not run:
        return []
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def per_replicate_loss(run: dict | None, task: int, when: str) -> list:
    """The loss at the first or the last iteration of one task, per replicate, or ``None`` where it was not kept."""
    out = []
    for r in replicates(run):
        entries = r.get("replay_loss") or []
        out.append(entries[task].get(when) if task < len(entries) and isinstance(entries[task], dict) else None)
    return out


def mean_over_tasks(run: dict | None, when: str) -> list:
    """The replicate-wise mean over the tasks that have a buffer, so pairing stays by replicate index."""
    rows = [per_replicate_loss(run, task, when) for task in TASKS]
    out = []
    for i in range(len(replicates(run))):
        vals = [row[i] for row in rows if i < len(row) and row[i] is not None]
        out.append(statistics.fmean(vals) if vals else None)
    return out


def _rise(last, first):
    return None if last is None or first is None else last - first


def paired(one: list, two: list) -> dict:
    diffs = [a - b for a, b in zip(one, two) if a is not None and b is not None]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def reading(paths=None) -> dict:
    paths = paths or PATHS
    runs = {tag: load(path) for tag, path in paths.items()}
    present = [tag for tag in ORDER if runs.get(tag)]
    if len(present) < 2:
        return {"runs": len(present), "missing": [str(paths[t]) for t in ORDER if not runs.get(t)]}
    a, b = runs[present[0]], runs[present[1]]
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {
        "runs": 2,
        "levels": present,
        "leaks": [(runs[t].get("env_draw") or {}).get("world_leak") for t in present],
        "arm": ARM,
        "task_indices": list(TASKS),
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "n_replicates": [len(replicates(a)), len(replicates(b))],
        "config_diff": {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
                        if k not in ("json_out", "loop_world_leak") and ca.get(k) != cb.get(k)},
        "env_diff": {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                     if k != "world_leak" and ea.get(k) != eb.get(k)},
        "env": ea,
        #: the mechanism's own quantity: the last-iteration loss on the stored features, paired by replicate
        "last": {"instant": mean_over_tasks(a, "last"), "carry": mean_over_tasks(b, "last")},
        "first": {"instant": mean_over_tasks(a, "first"), "carry": mean_over_tasks(b, "first")},
        "delta_last": paired(mean_over_tasks(b, "last"), mean_over_tasks(a, "last")),
        "rise": {"instant": paired(mean_over_tasks(a, "last"), mean_over_tasks(a, "first")),
                 "carry": paired(mean_over_tasks(b, "last"), mean_over_tasks(b, "first"))},
        "raw_rise": {"instant": [_rise(l, f) for l, f in zip(mean_over_tasks(a, "last"),
                                                            mean_over_tasks(a, "first"))],
                     "carry": [_rise(l, f) for l, f in zip(mean_over_tasks(b, "last"),
                                                          mean_over_tasks(b, "first"))]},
        #: a replicate whose rise is not computable stays `None` and is skipped by the pairing, so a run that
        #: never recorded the quantity refuses the claims rather than reading a zero for them
        "delta_rise": paired(
            [_rise(l, f) for l, f in zip(mean_over_tasks(b, "last"), mean_over_tasks(b, "first"))],
            [_rise(l, f) for l, f in zip(mean_over_tasks(a, "last"), mean_over_tasks(a, "first"))]),
        "accuracy": {tag: runs[tag]["methods"][ARM].get("final_accuracy") for tag in present},
        "forgetting": {tag: runs[tag]["methods"][ARM].get("mean_forgetting") for tag in present},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if r.get("runs", 0) < 2 or "env" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    same = (r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1]
            and r["task_names"][0] == r["task_names"][1] and r["n_replicates"][0] == r["n_replicates"][1] > 1
            and r["leaks"][0] == 1.0 and r["leaks"][1] < 1.0)
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks {r['task_names'][0]}, "
                                  f"arm `{r['arm']}`, {r['n_replicates'][0]} replicates each, leaks {r['leaks']}, "
                                  f"environment {r['env']}, config differing {r['config_diff']}, environment "
                                  f"differing {r['env_diff']}",
          "verdict": "MET -- one configuration except the rule" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}, leaks {r['leaks']}"}

    lo, hi = r["levels"]
    d = r["delta_last"]
    inst = statistics.fmean([x for x in r["last"][lo] if x is not None]) if any(
        x is not None for x in r["last"][lo]) else None
    car = statistics.fmean([x for x in r["last"][hi] if x is not None]) if any(
        x is not None for x in r["last"][hi]) else None
    delta = d["delta"]
    delta_text = "n/a" if delta is None else f"{delta:+.4f}"
    sem_text = "n/a" if d["sem"] is None else f"{d['sem']:.4f}"
    j2 = {"id": "T2", "measured": f"`{r['arm']}`'s last-iteration replay loss, averaged over tasks {r['task_indices']}: "
                                  f"{inst} instantaneous against {car} carried, delta {delta_text} "
                                  f"(sem {sem_text}, {d['sigma']} sigma, n {d['n']})",
          "verdict": ("REFUSED -- the loss was not recorded in both runs" if d["delta"] is None else
                      f"MET -- the stored features are staler in the carried world by {d['delta']:.4f}" if
                      d["delta"] >= BAR else
                      f"FALSIFIER FIRED -- they are less stale there by {abs(d['delta']):.4f}" if
                      d["delta"] <= -BAR else
                      f"NULL -- {d['delta']:+.4f}, within {BAR:.2f}")}

    dr = r["delta_rise"]
    detail = "; ".join(f"{tag} {v['delta']:+.4f} ({v['sigma']} sigma)" for tag, v in r["rise"].items()
                       if v["delta"] is not None)
    dr_delta = dr["delta"]
    j3 = {"id": "T3", "measured": f"the within-task rise, first to last: {detail}; carried minus instantaneous "
                                  f"{'n/a' if dr_delta is None else f'{dr_delta:+.4f}'} ({dr['sigma']} sigma)",
          "verdict": ("REFUSED -- the rise is not computable in both runs" if dr["delta"] is None else
                      f"MET -- the rise is larger in the carried world by {dr['delta']:.4f}" if dr["delta"] >= BAR
                      else f"FALSIFIER FIRED -- it is smaller there by {abs(dr['delta']):.4f}" if
                      dr["delta"] <= -BAR else
                      f"NULL -- {dr['delta']:+.4f}, within {BAR:.2f}")}

    rises = {tag: v["delta"] for tag, v in r["rise"].items()}
    thin = [tag for tag, v in rises.items() if v is not None and v < STILL]
    j4 = {"id": "T4", "measured": f"the rise in each world: {rises}, against a floor of {STILL:.2f}",
          "verdict": ("REFUSED -- the rise is not computable" if any(v is None for v in rises.values()) else
                      "MET -- the loss rises within a task in both worlds" if not thin else
                      f"FALSIFIER FIRED -- it rises by less than {STILL:.2f} in {thin}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if r.get("runs", 0) < 2:
        print(f"== what replay is scored on ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== what replay is scored on ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, tasks {r['task_names'][0]}, arm `{r['arm']}`, "
          f"{r['n_replicates'][0]} replicates each")
    print(f"   the two leaks: {r['leaks']}   environment: {r['env']}")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'world':12} {'first':>9} {'last':>9} {'rise':>9} {'accuracy':>10} {'forgetting':>12}")
    for tag in r["levels"]:
        f = [x for x in r["first"][tag] if x is not None]
        l = [x for x in r["last"][tag] if x is not None]
        print(f"   {tag:12} {statistics.fmean(f):9.4f} {statistics.fmean(l):9.4f} "
              f"{statistics.fmean(l) - statistics.fmean(f):+9.4f} {r['accuracy'][tag]:10.4f} "
              f"{r['forgetting'][tag]:12.4f}")
    print(f"   carried minus instantaneous, last: {r['delta_last']}")
    print(f"   carried minus instantaneous, rise: {r['delta_rise']}")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e333` found replay's retention moving in opposite directions under its last two changes to the")
    print("    world and named the mechanism it could not test; this reads the loss on the stored features out)")
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
