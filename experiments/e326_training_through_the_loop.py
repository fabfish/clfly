"""E326 -- training through the loop: the first arm whose gradient crosses its own output.

`e325` built the closed loop and measured it **frozen**: `CueActionEnv` shows a cue at step 0 and takes it away,
after which the only thing in the input is the agent's own last action, and the model's forward pass adds a
``feedback(x, t)`` callable to every step's input. It ended by naming what was missing: *nothing here trains on the
loop, so all four claims are the frozen substrate's behaviour*, and *a reward and a policy*.

This unit trains. `e8_rate_network` gained `--closed-loop`, which builds the suite out of the environment -- three
cue sets in **one** world, so one feedback function serves the whole suite -- and `--no-feedback`, which runs the
identical tasks, cue sets, seeds and read-out with the world disconnected. The feedback reaches every forward pass
by **wrapping** the module rather than by editing the dozen call sites, so training, evaluation, the Fisher blocks
and the replay features all see the same dynamical system.

Four claims, registered before these runs' readings were taken. The suite is three tasks with two cue symbols each,
so chance is **0.50** per task head, and `delta` is the closed loop minus the open one paired by replicate index.

- **T1 -- one configuration except the loop.** Same circuit, same read-out fingerprint, same task names, same seed
  schedule and replay counts, and a config differing only in the feedback switch and the output path. **Falsifier**:
  any other field differing, or a differing task name.
- **T2 -- and the loop trains.** `naive`'s `final_accuracy` under the closed loop is at least **0.10** above chance.
  Backprop-through-time has to cross the loop for this to work at all, and a feedback that destabilised the
  recurrence would show up here first. **Falsifier**: at or below 0.05 above chance. **Null**: between the two.
- **T3 -- and the loop costs level.** `naive` reads **lower** under the closed loop by at least **0.05**, the agent's
  own action being a source of input the task did not ask for. **Falsifier**: higher by that much. **Null**: within.
- **T4 -- and the loop costs retention.** `naive`'s `mean_forgetting` is **higher** under the closed loop by at least
  **0.02**: what has to be held across a boundary now includes a channel the body itself drives. **Falsifier**: lower
  by that much. **Null**: within.

**What it cannot do.** *Two arms and five replicates*: `replay` and the two block arms are not run here, and five
replicates put one standard error of a paired accuracy difference near 0.02. *Two suites at one circuit, one
read-out width, one scale and one gain*: the two runs differ in the loop and nothing else by T1's check, but the
**cue** is a single pulse at step 0 in both, so this is the loop's effect on a task `e325` showed is nearly
saturated for a linear probe. *The action is smooth*, a ``tanh`` of the mean activity over eight neurons, so the
gradient crosses it; a hard threshold would not and is not measured. *And there is still no reward*: the label is
the cue, delivered at step 0, and the agent's action is an input and not a decision -- so this is the first training
run through a closed loop in this repository and not yet a game.
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
CLOSED = RUNS / "e326_closed_loop.json"
OPEN = RUNS / "e326_open_loop.json"
ARMS = ("naive", "ewc-block")
NAIVE = "naive"
#: chance for a two-symbol task head, and the four thresholds
CHANCE = 0.5
BAR_LEARN = 0.10
BAR_LEVEL = 0.05
BAR_FORGET = 0.02
#: fields the two runs may differ in, being the manipulation and the output path
IGNORED_CONFIG = ("json_out", "no_feedback")
CLAIMS = (
    ("T1", "one configuration except the loop",
     "Same circuit, read-out fingerprint, task names, seed schedule and replicate counts; a config differing only "
     "in the feedback switch and the output path",
     "falsifier: any other field differing, or a differing task name"),
    ("T2", f"and the loop trains: `{NAIVE}` at least {BAR_LEARN:.2f} above chance",
     f"`{NAIVE}`'s final accuracy under the closed loop is at least {BAR_LEARN:.2f} above {CHANCE:.2f}",
     "falsifier: at or below 0.05 above chance"),
    ("T3", f"and the loop costs level: `{NAIVE}` lower by {BAR_LEVEL:.2f}",
     f"`{NAIVE}` reads lower under the closed loop by at least {BAR_LEVEL:.2f}",
     "falsifier: higher by that much"),
    ("T4", f"and the loop costs retention: `{NAIVE}` forgets {BAR_FORGET:.2f} more",
     f"`{NAIVE}`'s mean forgetting is higher under the closed loop by at least {BAR_FORGET:.2f}",
     "falsifier: lower by that much"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def config_diff(a: dict, b: dict) -> dict:
    ca, cb = a.get("config", {}), b.get("config", {})
    return {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
            if k not in IGNORED_CONFIG and ca.get(k) != cb.get(k)}


def replicates(run: dict, arm: str) -> list[dict]:
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def reading(closed_path=CLOSED, open_path=OPEN) -> dict:
    a, b = load(closed_path), load(open_path)
    if not a or not b:
        return {"runs": 0,
                "missing": [str(p) for p, d in ((closed_path, a), (open_path, b)) if not d]}
    arms = sorted(set(a.get("methods", {})) & set(b.get("methods", {})))
    return {
        "runs": 2,
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": {"closed": [t.get("name") for t in a.get("tasks", [])],
                       "open": [t.get("name") for t in b.get("tasks", [])]},
        "n_replicates": {arm: [len(replicates(a, arm)), len(replicates(b, arm))] for arm in arms},
        "config_diff": config_diff(a, b),
        "env_draw": [a.get("env_draw"), b.get("env_draw")],
        "accuracy": {arm: paired([r["final_accuracy"] for r in replicates(a, arm)],
                                 [r["final_accuracy"] for r in replicates(b, arm)]) for arm in arms},
        "forgetting": {arm: paired([r["mean_forgetting"] for r in replicates(a, arm)],
                                   [r["mean_forgetting"] for r in replicates(b, arm)]) for arm in arms},
        "closed": {arm: {"final_accuracy": a["methods"][arm].get("final_accuracy"),
                         "mean_forgetting": a["methods"][arm].get("mean_forgetting")} for arm in arms},
        "open": {arm: {"final_accuracy": b["methods"][arm].get("final_accuracy"),
                       "mean_forgetting": b["methods"][arm].get("mean_forgetting")} for arm in arms},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    counts = r["n_replicates"]
    same_counts = all(v[0] == v[1] for v in counts.values())
    same_tasks = r["task_names"]["closed"] == r["task_names"]["open"] and bool(r["task_names"]["closed"])
    same_env = r["env_draw"][0] == r["env_draw"][1] and r["env_draw"][0] is not None
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks "
                                  f"{r['task_names']['closed']}, counts {counts}, config differing "
                                  f"{r['config_diff']}",
          "verdict": "MET -- one configuration in two loops" if
          r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1] and same_counts
          and same_tasks and same_env and not r["config_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, tasks {same_tasks}, env {same_env}, "
          f"read-out {r['readout']}"}

    closed_acc = r["closed"].get(NAIVE, {}).get("final_accuracy")
    above = None if closed_acc is None else closed_acc - CHANCE
    j2 = {"id": "T2", "measured": f"`{NAIVE}` closed-loop final accuracy {closed_acc} against a chance of "
                                  f"{CHANCE:.2f}, i.e. {above if above is None else f'{above:+.4f}'}",
          "verdict": ("REFUSED -- the arm is missing from one run" if above is None else
                      f"MET -- the loop trains to {above:+.4f} above chance" if above >= BAR_LEARN else
                      f"FALSIFIER FIRED -- it reads {above:+.4f} above chance" if above <= 0.05 else
                      f"NULL -- {above:+.4f}, between 0.05 and {BAR_LEARN:.2f}")}

    d = r["accuracy"].get(NAIVE, {}).get("delta")
    j3 = {"id": "T3", "measured": f"`{NAIVE}` accuracy {r['open'].get(NAIVE, {}).get('final_accuracy')} open "
                                  f"against {closed_acc} closed, delta {d if d is None else f'{d:+.4f}'} "
                                  f"({r['accuracy'].get(NAIVE, {}).get('sigma')} sigma)",
          "verdict": ("REFUSED -- the arm is missing from one run" if d is None else
                      f"MET -- the closed loop reads {abs(d):.4f} lower" if d <= -BAR_LEVEL else
                      f"FALSIFIER FIRED -- it reads {d:+.4f} higher" if d >= BAR_LEVEL else
                      f"NULL -- {d:+.4f}, within {BAR_LEVEL:.2f}")}

    f = r["forgetting"].get(NAIVE, {}).get("delta")
    j4 = {"id": "T4", "measured": f"`{NAIVE}` forgetting {r['open'].get(NAIVE, {}).get('mean_forgetting')} open "
                                  f"against {r['closed'].get(NAIVE, {}).get('mean_forgetting')} closed, delta "
                                  f"{f if f is None else f'{f:+.4f}'} "
                                  f"({r['forgetting'].get(NAIVE, {}).get('sigma')} sigma)",
          "verdict": ("REFUSED -- the arm is missing from one run" if f is None else
                      f"MET -- the closed loop forgets {f:.4f} more" if f >= BAR_FORGET else
                      f"FALSIFIER FIRED -- it forgets {f:+.4f} less" if f <= -BAR_FORGET else
                      f"NULL -- {f:+.4f}, within {BAR_FORGET:.2f}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("runs"):
        print(f"== training through the loop ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== training through the loop ==")
    print(f"   circuits {r['circuits']}  read-out {r['readout']}")
    print(f"   tasks {r['task_names']['closed']}")
    print(f"   config fields differing: {r['config_diff'] or 'none'}")
    print(f"   environment draw equal: {r['env_draw'][0] == r['env_draw'][1]}  "
          f"({r['env_draw'][0]})")
    print(f"\n   {'arm':12} {'open':>9} {'closed':>9} {'delta':>9} {'sigma':>7} "
          f"{'forget o':>9} {'forget c':>9} {'delta':>9} {'sigma':>7}")
    for arm in sorted(r["accuracy"]):
        a, b = r["open"].get(arm, {}), r["closed"].get(arm, {})
        va, vb = r["accuracy"][arm], r["forgetting"][arm]
        print(f"   {arm:12} {a.get('final_accuracy'):9.4f} {b.get('final_accuracy'):9.4f} "
              f"{va['delta']:+9.4f} {va['sigma']:7.2f} "
              f"{a.get('mean_forgetting'):9.4f} {b.get('mean_forgetting'):9.4f} "
              f"{vb['delta']:+9.4f} {vb['sigma']:7.2f}")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e325` built the loop and measured it frozen and named the two things missing -- training through")
    print("    it and a reward; this is the first, and the label is still delivered rather than earned)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--closed", type=Path, default=CLOSED)
    ap.add_argument("--open", dest="open_path", type=Path, default=OPEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.closed, args.open_path)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
