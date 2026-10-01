"""E333 -- the world gets a transition rule: the answer carries the action history and not the last action.

`e332` gave the world a **state** and no rule. Its action channel became two patterns the agent's action selects
between, so what came back was a consequence the agent picked -- but the consequence of the **last** action and of
nothing earlier. Its own finding names what that leaves: *"the world has a state and no transition rule: the action
picks a consequence, and nothing else about the world evolves, so it is a world with a state and not yet a world
with dynamics."*

This gives it the rule. `CueActionEnv` gained `world_leak`, and the world's state is now

    w_t = (1 - leak) * w_{t-1} + leak * action_{t-1}

so `leak = 1` is the instantaneous world `e332` measured -- the recursion is the identity `w = action` -- and
anything below it makes the channel at step ``t`` a **decaying sum of the whole action history**. The endpoint is
exact rather than approximate, which is what makes the control cheap: the two runs here are `leak = 1.0` and
`leak = 0.35`, with `naive` and `replay` at five replicates each and the same seeds.

Four claims, registered before these runs' readings. `delta` is the carried world minus the instantaneous one,
paired by replicate index.

- **T1 -- one configuration except the rule.** Same circuit, read-out fingerprint, task names, replicate counts,
  cue symbols, cue noise, world state count and environment draw, the last differing only in the leak it records.
  **Falsifier**: any other field differing.
- **T2 -- and the rule moves the level.** `naive`'s final accuracy differs by at least **0.03**. **Falsifier**:
  less than 0.01. **Null**: between. `e332` moved `naive`'s level by 0.0056 when the world's response became a
  state at all, so this is the same quantity asked of a smaller change.
- **T3 -- and it moves retention.** `naive`'s `mean_forgetting` differs by at least **0.03**, with the same two
  bounds.
- **T4 -- and the rule's own endpoint is exact.** The `leak = 1.0` run reproduces `e332`'s state-world artifact
  **exactly**, replicate for replicate, on accuracy and on forgetting, for both arms -- the claim that the recursion
  at one *is* the instantaneous world rather than merely close to it. **Falsifier**: any replicate differing.

**What it cannot do.** *One leak*: 0.35 against 1.0, with the shape between them and anything faster or slower not
measured, and `leak = 0` a world that never changes at all is not run either. *Two arms*: `ewc` and the two block
arms are not run, so the arm that noticed `e332`'s change is the only one asked here. *Five replicates*, whose
paired standard error at this per-replicate spread is near 0.02 on accuracy and near 0.03 on forgetting, so T2 and
T3 resolve 0.03 and not much less. *The world's rule is linear and scalar*: one leaky integrator of one action, with
no state-to-state coupling and nothing the agent's actions can push it into. *And the label is still delivered*: the
cue arrives at step 0, so the reward is still not earned.
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
PATHS = {"instant": RUNS / "e333_world_instant.json", "carry": RUNS / "e333_world_carry.json"}
ORDER = ("instant", "carry")
LEAKS = {"instant": 1.0, "carry": 0.35}
#: the artifact whose world `leak = 1.0` has to be, to the last digit
ENDPOINT = RUNS / "e332_world_state.json"
ARMS = ("naive", "replay")
NAIVE = "naive"
MOVED = 0.03
STILL = 0.01
CLAIMS = (
    ("T1", "one configuration except the rule",
     "Same circuit, read-out fingerprint, task names, replicate counts, cue symbols, cue noise, world state count "
     "and environment draw, the last differing only in the leak it records",
     "falsifier: any other field differing"),
    ("T2", f"and the rule moves the level, by {MOVED:.2f}",
     f"`{NAIVE}`'s final accuracy differs between the two worlds by at least {MOVED:.2f}, paired",
     f"falsifier: a difference of less than {STILL:.2f}"),
    ("T3", f"and it moves retention, by {MOVED:.2f}",
     f"`{NAIVE}`'s mean forgetting differs between the two worlds by at least {MOVED:.2f}, paired",
     f"falsifier: a difference of less than {STILL:.2f}"),
    ("T4", "and the rule's own endpoint is exact",
     "The leak-1.0 run reproduces `e332`'s state-world artifact exactly, replicate for replicate, on accuracy and "
     "forgetting, for both arms",
     "falsifier: any replicate differing"),
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


def ledger(run: dict | None, arm: str) -> list[tuple]:
    """Each replicate's two numbers, so an exact comparison is an exact comparison and not a tolerance."""
    return [(r.get("final_accuracy"), r.get("mean_forgetting")) for r in replicates(run, arm)]


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def reading(paths=None, endpoint=ENDPOINT) -> dict:
    paths = paths or PATHS
    runs = {tag: load(path) for tag, path in paths.items()}
    present = [tag for tag in ORDER if runs.get(tag)]
    if len(present) < 2:
        return {"runs": len(present), "missing": [str(paths[t]) for t in ORDER if not runs.get(t)]}
    a, b = runs[present[0]], runs[present[1]]
    end = load(endpoint)
    arms = [arm for arm in ARMS if replicates(a, arm) and replicates(b, arm)]
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {
        "runs": 2,
        "levels": present,
        "leaks": [(runs[t].get("env_draw") or {}).get("world_leak") for t in present],
        "arms": arms,
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "n_replicates": {arm: [len(replicates(a, arm)), len(replicates(b, arm))] for arm in arms},
        "config_diff": {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
                        if k not in ("json_out", "loop_world_leak") and ca.get(k) != cb.get(k)},
        "env_diff": {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                     if k != "world_leak" and ea.get(k) != eb.get(k)},
        "env": ea,
        "accuracy": {arm: paired([r["final_accuracy"] for r in replicates(b, arm)],
                                 [r["final_accuracy"] for r in replicates(a, arm)]) for arm in arms},
        "forgetting": {arm: paired([r["mean_forgetting"] for r in replicates(b, arm)],
                                   [r["mean_forgetting"] for r in replicates(a, arm)]) for arm in arms},
        "instant": {arm: {"final_accuracy": a["methods"][arm].get("final_accuracy"),
                          "mean_forgetting": a["methods"][arm].get("mean_forgetting")} for arm in arms},
        "carry": {arm: {"final_accuracy": b["methods"][arm].get("final_accuracy"),
                        "mean_forgetting": b["methods"][arm].get("mean_forgetting")} for arm in arms},
        "endpoint": (None if end is None else
                     {arm: {"identical": ledger(a, arm) == ledger(end, arm),
                            "n_instant": len(ledger(a, arm)), "n_endpoint": len(ledger(end, arm))}
                      for arm in ARMS}),
        #: `loop_world_leak` is excluded and the exclusion is the point: `e332`'s artifact predates the flag, so
        #: it has no key at all, and the default it ran under **is** this unit's endpoint. The raw key sets are
        #: reported beside the diff so that a missing key is visible rather than absorbed.
        "endpoint_config_diff": (None if end is None else
                                 {k: [ca.get(k), (end.get("config") or {}).get(k)]
                                  for k in sorted(set(ca) | set(end.get("config") or {}))
                                  if k not in ("json_out", "loop_world_leak")
                                  and ca.get(k) != (end.get("config") or {}).get(k)}),
        "endpoint_keys_absent": (None if end is None else
                                 sorted(k for k in ca if k not in (end.get("config") or {}))),
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
            and r["leaks"][0] == 1.0 and r["leaks"][1] < 1.0)
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks {r['task_names'][0]}, "
                                  f"arms {r['arms']}, counts {counts}, leaks {r['leaks']}, environment {r['env']}, "
                                  f"config differing {r['config_diff']}, environment differing {r['env_diff']}",
          "verdict": "MET -- one configuration except the rule" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}, leaks {r['leaks']}"}

    out = [j1]
    for cid, key, field, name in (("T2", "accuracy", "final_accuracy", "final accuracy"),
                                  ("T3", "forgetting", "mean_forgetting", "mean forgetting")):
        v = r[key].get(NAIVE, {})
        d = v.get("delta")
        measured = (f"`{NAIVE}` {name} {r['instant'].get(NAIVE, {}).get(field)} instantaneous against "
                    f"{r['carry'].get(NAIVE, {}).get(field)} carried, delta "
                    f"{'n/a' if d is None else f'{d:+.4f}'} ({v.get('sigma')} sigma)")
        if d is None:
            verdict = "REFUSED -- the arm is missing from one run"
        elif abs(d) >= MOVED:
            verdict = f"MET -- the rule moves {name} by {abs(d):.4f}"
        elif abs(d) < STILL:
            verdict = f"FALSIFIER FIRED -- it moves {name} by only {abs(d):.4f}"
        else:
            verdict = f"NULL -- {abs(d):.4f}, between {STILL:.2f} and {MOVED:.2f}"
        out.append({"id": cid, "measured": measured, "verdict": verdict})

    end = r.get("endpoint")
    if end is None:
        j4 = {"id": "T4", "measured": "the endpoint artifact is absent",
              "verdict": "REFUSED -- `e332`'s state-world artifact is not on disk"}
    else:
        bad = [arm for arm, v in end.items() if not v["identical"]]
        j4 = {"id": "T4", "measured": f"the leak-1.0 run against `e332`'s state world, replicate for replicate: "
                                      f"{ {arm: v['identical'] for arm, v in end.items()} }; unexpected config "
                                      f"differences {r['endpoint_config_diff']}; keys the older artifact has not "
                                      f"got {r['endpoint_keys_absent']}",
              "verdict": "MET -- the rule at one is that world to the last digit" if not bad
              and not r["endpoint_config_diff"] else
              f"FALSIFIER FIRED -- {bad} differ, config {r['endpoint_config_diff']}"}
    out.append(j4)
    return out


def report(r: dict) -> int:
    if r.get("runs", 0) < 2:
        print(f"== the world gets a transition rule ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the world gets a transition rule ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, tasks {r['task_names'][0]}, arms {r['arms']}")
    print(f"   environment: {r['env']}")
    print(f"   the two leaks: {r['leaks']}")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'arm':12} {'acc inst':>10} {'acc carry':>10} {'delta':>9} {'sigma':>7} "
          f"{'for inst':>10} {'for carry':>10} {'delta':>9} {'sigma':>7}")
    for arm in r["arms"]:
        a, b = r["instant"].get(arm, {}), r["carry"].get(arm, {})
        va, vb = r["accuracy"][arm], r["forgetting"][arm]
        print(f"   {arm:12} {a.get('final_accuracy'):10.4f} {b.get('final_accuracy'):10.4f} "
              f"{va['delta']:+9.4f} {va['sigma']:7.2f} "
              f"{a.get('mean_forgetting'):10.4f} {b.get('mean_forgetting'):10.4f} "
              f"{vb['delta']:+9.4f} {vb['sigma']:7.2f}")
    print(f"   endpoint (`e332`'s state world): "
          f"{None if r['endpoint'] is None else {a: v['identical'] for a, v in r['endpoint'].items()}}, "
          f"config differences {r['endpoint_config_diff']}")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e332` gave the world a state and no rule, and named it; this gives it the rule, with the")
    print("    instantaneous world as its exact `leak = 1` endpoint)")
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
