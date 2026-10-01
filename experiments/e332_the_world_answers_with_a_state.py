"""E332 -- the world answers with a state: the action picks a consequence instead of being reported back.

`e331` asked the line's headline ordering under the loop and found it surviving, on a world whose response to the
agent is a **scalar report**: the action is a ``tanh`` of the mean activity over eight neurons, scattered onto
twelve others, so what comes back says *what the agent did* and nothing else. That is a mirror. `e325`'s
"what it cannot do" and `e326`'s both name the same missing thing in the same words -- *a reward and a policy*, with
*the label delivered at step 0 rather than earned* -- and a mirror is the reason: a world with no state of its own
can only correct the agent, never present it with a consequence.

This unit gives the world a state, and only that. `CueActionEnv` gained `world_modes`: at zero the channel is the
scalar report exactly as before, and at two or more the agent's action **selects** one of that many patterns by a
smooth interpolation, so what comes back is a consequence the agent picked. Nothing else moves -- the circuit, the
read-out, the cue symbols, the noise, the action and feedback populations and the feedback strength are the same
objects in both runs.

Two runs, `naive` and `replay`, five replicates each, share seeds: **the scalar report** and **the two-state
world**. Four claims, registered before these runs' readings.

- **T1 -- one configuration except the world's response.** Same circuit, read-out fingerprint, task names, replicate
  counts, cue symbols, cue noise and environment draw, the last differing only in `world_modes` and the pattern
  fingerprint that comes with it. **Falsifier**: any other field differing.
- **T2 -- and the world's response moves the level.** `naive`'s final accuracy differs between the two worlds by at
  least **0.03**, paired by replicate index. **Falsifier**: a difference of less than 0.01. **Null**: between.
- **T3 -- and it moves retention.** `naive`'s `mean_forgetting` differs between the two worlds by at least **0.03**.
  **Falsifier**: less than 0.01. **Null**: between.
- **T4 -- and `replay`'s forgetting advantage is still an order of magnitude, in the world with a state.**
  `replay`'s mean forgetting is at least **0.10 lower** than `naive`'s in the **state** world. `e331` measured that
  gap at about 0.16 on the mirror world, six to ten times any accuracy contrast in its table, and this asks whether
  the largest number in the corpus's neighbourhood survives a world that answers with a consequence.
  **Falsifier**: a gap below 0.05. **Null**: between 0.05 and 0.10.

**What it cannot do.** *Two arms*: `ewc` and the two block arms are not run, so T4 is one pair and not the ordering.
*Two world sizes*: zero modes and two, with three or more not run and the interpolation between more than two
states a design this unit does not have. *Five replicates*, which put one standard error of a paired difference near
0.02 on accuracy and near 0.03 on forgetting, so T2 and T3 can resolve 0.03 and not much less. *The world's state is
two patterns and no transition rule*: the action picks a consequence and the world does not otherwise evolve, so
this is a world with a state and not yet a world with dynamics. *And the label is still delivered*: the cue arrives
at step 0 and the reward is not earned, so this is the first world that answers with a consequence and not yet a
game.
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
PATHS = {"report": RUNS / "e332_world_report.json", "state": RUNS / "e332_world_state.json"}
ORDER = ("report", "state")
MODES = {"report": 0, "state": 2}
ARMS = ("naive", "replay")
NAIVE = "naive"
REPLAY = "replay"
MOVED = 0.03
STILL = 0.01
GAP = 0.10
FLAT = 0.05
CLAIMS = (
    ("T1", "one configuration except the world's response",
     "Same circuit, read-out fingerprint, task names, replicate counts, cue symbols, cue noise and environment draw, "
     "the last differing only in the world's state count and its pattern fingerprint",
     "falsifier: any other field differing"),
    ("T2", f"and the world's response moves the level, by {MOVED:.2f}",
     f"`{NAIVE}`'s final accuracy differs between the two worlds by at least {MOVED:.2f}, paired",
     f"falsifier: a difference of less than {STILL:.2f}"),
    ("T3", f"and it moves retention, by {MOVED:.2f}",
     f"`{NAIVE}`'s mean forgetting differs between the two worlds by at least {MOVED:.2f}, paired",
     f"falsifier: a difference of less than {STILL:.2f}"),
    ("T4", f"and `{REPLAY}`'s forgetting advantage is still an order of magnitude, at least {GAP:.2f}, in the state "
           f"world",
     f"`{REPLAY}`'s mean forgetting is at least {GAP:.2f} lower than `{NAIVE}`'s in the state world",
     f"falsifier: a gap below {FLAT:.2f}"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(run: dict | None, arm: str) -> list[dict]:
    if not run:
        return []
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
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
    arms = [arm for arm in ARMS if replicates(a, arm) and replicates(b, arm)]
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {
        "runs": 2,
        "levels": present,
        #: read off the artifacts rather than from `MODES`, so a run whose draw says something else is reported
        #: as what it was rather than as what this module expects
        "world_modes": [(runs[t].get("env_draw") or {}).get("world_modes") for t in present],
        "arms": arms,
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "n_replicates": {arm: [len(replicates(a, arm)), len(replicates(b, arm))] for arm in arms},
        "config_diff": {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
                        if k not in ("json_out", "loop_world_modes") and ca.get(k) != cb.get(k)},
        "env_diff": {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                     if k not in ("world_modes", "world_sha1") and ea.get(k) != eb.get(k)},
        "env": ea,
        "accuracy": {arm: paired([r["final_accuracy"] for r in replicates(b, arm)],
                                 [r["final_accuracy"] for r in replicates(a, arm)]) for arm in arms},
        "forgetting": {arm: paired([r["mean_forgetting"] for r in replicates(b, arm)],
                                   [r["mean_forgetting"] for r in replicates(a, arm)]) for arm in arms},
        "report": {arm: {"final_accuracy": a["methods"][arm].get("final_accuracy"),
                         "mean_forgetting": a["methods"][arm].get("mean_forgetting")} for arm in arms},
        "state": {arm: {"final_accuracy": b["methods"][arm].get("final_accuracy"),
                        "mean_forgetting": b["methods"][arm].get("mean_forgetting")} for arm in arms},
        "gap": {tag: (runs[tag]["methods"][NAIVE].get("mean_forgetting")
                      - runs[tag]["methods"][REPLAY].get("mean_forgetting")) for tag in present},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if r.get("runs", 0) < 2 or "env" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    counts = r["n_replicates"]
    same = (r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1]
            and r["task_names"][0] == r["task_names"][1]
            and all(v[0] == v[1] and v[0] > 1 for v in counts.values())
            and r["world_modes"][0] == 0 and r["world_modes"][1] > 1)
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks {r['task_names'][0]}, "
                                  f"arms {r['arms']}, counts {counts}, world states {r['world_modes']}, "
                                  f"environment {r['env']}, config differing {r['config_diff']}, environment "
                                  f"differing {r['env_diff']}",
          "verdict": "MET -- one configuration except the world's response" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}, world {r['world_modes']}"}

    out = [j1]
    for cid, key, name in (("T2", "accuracy", "final accuracy"), ("T3", "forgetting", "mean forgetting")):
        v = r[key].get(NAIVE, {})
        d = v.get("delta")
        field = "final_accuracy" if key == "accuracy" else "mean_forgetting"
        measured = (f"`{NAIVE}` {name} {r['report'].get(NAIVE, {}).get(field)} under the report against "
                    f"{r['state'].get(NAIVE, {}).get(field)} in the state world, delta "
                    f"{'n/a' if d is None else f'{d:+.4f}'} ({v.get('sigma')} sigma)")
        if d is None:
            verdict = "REFUSED -- the arm is missing from one run"
        elif abs(d) >= MOVED:
            verdict = f"MET -- the world's response moves {name} by {abs(d):.4f}"
        elif abs(d) < STILL:
            verdict = f"FALSIFIER FIRED -- it moves {name} by only {abs(d):.4f}"
        else:
            verdict = f"NULL -- {abs(d):.4f}, between {STILL:.2f} and {MOVED:.2f}"
        out.append({"id": cid, "measured": measured, "verdict": verdict})

    gap = r["gap"].get(r["levels"][1])
    detail = ", ".join(f"{r['state'].get(arm, {}).get('mean_forgetting')}" for arm in r["arms"])
    j4 = {"id": "T4", "measured": f"`{NAIVE}` minus `{REPLAY}` mean forgetting in the state world: {gap} "
                                  f"(the arms read {detail})",
          "verdict": ("REFUSED -- the arm is missing from one run" if gap is None else
                      f"MET -- `{REPLAY}` forgets {gap:.4f} less than `{NAIVE}`" if gap >= GAP else
                      f"FALSIFIER FIRED -- the gap is only {gap:.4f}" if gap < FLAT else
                      f"NULL -- {gap:.4f}, between {FLAT:.2f} and {GAP:.2f}")}
    out.append(j4)
    return out


def report(r: dict) -> int:
    if r.get("runs", 0) < 2:
        print(f"== the world answers with a state ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the world answers with a state ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, tasks {r['task_names'][0]}, arms {r['arms']}")
    print(f"   environment: {r['env']}")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'arm':12} {'acc report':>11} {'acc state':>10} {'delta':>9} {'sigma':>7} "
          f"{'for report':>11} {'for state':>10} {'delta':>9} {'sigma':>7}")
    for arm in r["arms"]:
        a, b = r["report"].get(arm, {}), r["state"].get(arm, {})
        va, vb = r["accuracy"][arm], r["forgetting"][arm]
        print(f"   {arm:12} {a.get('final_accuracy'):11.4f} {b.get('final_accuracy'):10.4f} "
              f"{va['delta']:+9.4f} {va['sigma']:7.2f} "
              f"{a.get('mean_forgetting'):11.4f} {b.get('mean_forgetting'):10.4f} "
              f"{vb['delta']:+9.4f} {vb['sigma']:7.2f}")
    print(f"   `{NAIVE}` minus `{REPLAY}` forgetting: report {r['gap'].get(r['levels'][0])}, "
          f"state {r['gap'].get(r['levels'][1])}")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e331` found the ordering surviving a world whose response is a scalar report -- a mirror; this")
    print("    gives the world a state, so what comes back is a consequence the agent picked)")
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
