"""E329 -- the environment gets a noisy cue: the headroom `e328` ended by naming as missing.

`e328` put the feedback strength at 1.92 sigma and ended on a limitation that the whole thread shares: *"every
replicate learns every task, so nothing here speaks to acquisition"*, and *"the task whose read-out is not saturated
is still the missing instrument"*. Its own table says where the ceiling comes from -- with deterministic cue
patterns a two-symbol task is **two fixed vectors** in twelve cue neurons, so every arm solves it and the only
quantity left to move is whether a replicate forgot at all.

This unit adds the missing ingredient. `CueActionEnv` gained a **`noise`** field -- drawn once per example at step 0,
defaulting to zero so every earlier artifact is untouched -- and the runner gained `--loop-noise`. The environment
here is **eight cue symbols per task** with **noise 1.0**: a twenty-four-symbol world read out from a 32-neuron
linear head over a single-step pulse, which is a measurement rather than two fixed vectors.

Two runs, **scale 0.0 and scale 0.5** -- the open loop and the middling setting `e328` put at 1.92 sigma on the easy
environment -- with `naive` and `ewc-block` at five replicates each. Because the two runs share their seed schedule,
every contrast is **paired by replicate index**.

Four claims, registered before these runs' readings. Each task head is eight-way, so chance is **0.125**.

- **T1 -- one configuration except the strength.** Same circuit, read-out fingerprint, task names, replicate counts,
  cue symbols, cue noise and environment draw, the last differing only in the strength it records. **Falsifier**:
  any other field differing.
- **T2 -- and the environment has the headroom `e328` named.** `naive`'s final accuracy under the **open** setting
  is **below 0.95**, i.e. the task is no longer solved perfectly. **Falsifier**: at or above 0.99. **Null**: between
  0.95 and 0.99.
- **T3 -- and what it loses is graded rather than occasional.** The five-replicate mean `mean_forgetting` at the
  **middling** setting is at least **0.10**, where the easy environment's was 0.1297 on a rare-event count. A graded
  loss is what a task with room under the ceiling gives. **Falsifier**: at or below 0.02. **Null**: between 0.02 and
  0.10.
- **T4 -- and the middling setting still costs level.** `naive` reads **lower** at scale 0.5 than at scale 0.0 by at
  least **0.05**, paired by replicate index. This is `e328`'s accuracy observation (0.9625 against 0.9135) asked
  again where the task is not at the ceiling. **Falsifier**: higher by that much. **Null**: within.

**What it cannot do.** *Two settings, one noise level and one cue width*: the noise is 1.0 and the alphabet eight,
and neither is swept -- a different noise would move the ceiling and a different alphabet the class geometry. *Five
replicates* put one standard error of a paired accuracy difference near 0.02 here, so T4 can resolve 0.05 and not
much less. *One arm pair*: `replay` and the two block arms are not run. *The noise is on the cue and nowhere else*:
the environment's action channel is noiseless and deterministic, so what this measures is a noisy measurement and
not a stochastic world. *And there is still no reward*: the label is the cue, delivered at step 0, and the agent's
action is an input rather than a decision.
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
PATHS = {"0p00": RUNS / "e329_noisy_scale_0p00.json", "0p50": RUNS / "e329_noisy_scale_0p50.json"}
ORDER = ("0p00", "0p50")
SCALES = {"0p00": 0.0, "0p50": 0.5}
ARMS = ("naive", "ewc-block")
NAIVE = "naive"
#: the eight-way head's chance, and the three thresholds
CHANCE = 0.125
CEILING = 0.95
SOLD = 0.99
GRADED = 0.10
FLAT = 0.02
BAR_LEVEL = 0.05
CLAIMS = (
    ("T1", "one configuration except the strength",
     "Same circuit, read-out fingerprint, task names, replicate counts, cue symbols, cue noise and environment draw, "
     "the last differing only in the strength",
     "falsifier: any other field differing"),
    ("T2", f"and the environment has the headroom `e328` named: `{NAIVE}` below {CEILING:.2f} open",
     f"`{NAIVE}`'s final accuracy under the open setting is below {CEILING:.2f}, against a chance of {CHANCE:.3f}",
     f"falsifier: at or above {SOLD:.2f}"),
    ("T3", f"and what it loses is graded: mean forgetting at the middling setting at least {GRADED:.2f}",
     f"The five-replicate mean `mean_forgetting` at scale {SCALES['0p50']} is at least {GRADED:.2f}",
     f"falsifier: at or below {FLAT:.2f}"),
    ("T4", f"and the middling setting still costs level, by {BAR_LEVEL:.2f}",
     f"`{NAIVE}` reads lower at scale {SCALES['0p50']} than at {SCALES['0p00']} by at least {BAR_LEVEL:.2f}",
     "falsifier: higher by that much"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def replicates(run: dict | None, arm: str = NAIVE) -> list[dict]:
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
    ca, cb = a.get("config", {}), b.get("config", {})
    ignored = ("json_out", "loop_scale")
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {
        "runs": 2,
        "levels": present,
        "scales": [SCALES[t] for t in present],
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "config_diff": {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
                        if k not in ignored and ca.get(k) != cb.get(k)},
        "env_diff": {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                     if k != "scale" and ea.get(k) != eb.get(k)},
        "env": ea,
        "n_replicates": {arm: [len(replicates(a, arm)), len(replicates(b, arm))] for arm in ARMS},
        "accuracy": {arm: paired([r["final_accuracy"] for r in replicates(b, arm)],
                                 [r["final_accuracy"] for r in replicates(a, arm)]) for arm in ARMS},
        "forgetting": {arm: paired([r["mean_forgetting"] for r in replicates(b, arm)],
                                   [r["mean_forgetting"] for r in replicates(a, arm)]) for arm in ARMS},
        "open": {arm: {"final_accuracy": a["methods"][arm].get("final_accuracy"),
                       "mean_forgetting": a["methods"][arm].get("mean_forgetting")} for arm in ARMS},
        "mid": {arm: {"final_accuracy": b["methods"][arm].get("final_accuracy"),
                      "mean_forgetting": b["methods"][arm].get("mean_forgetting")} for arm in ARMS},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if r.get("runs", 0) < 2 or "circuits" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    same = (r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1]
            and r["task_names"][0] == r["task_names"][1]
            and all(v[0] == v[1] for v in r["n_replicates"].values()))
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks "
                                  f"{r['task_names'][0]}, counts {r['n_replicates']}, environment "
                                  f"{r['env']}, config differing {r['config_diff']}, environment differing "
                                  f"{r['env_diff']}",
          "verdict": "MET -- one configuration except the strength" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}"}

    acc = r["open"].get(NAIVE, {}).get("final_accuracy")
    j2 = {"id": "T2", "measured": f"`{NAIVE}` open-setting final accuracy {acc} against a chance of {CHANCE:.3f}",
          "verdict": ("REFUSED -- the arm is missing from one run" if acc is None else
                      f"MET -- the task reads {acc:.4f}, below the {CEILING:.2f} ceiling" if acc < CEILING else
                      f"NULL -- {acc:.4f}, between {CEILING:.2f} and {SOLD:.2f}" if acc < SOLD else
                      f"FALSIFIER FIRED -- it reads {acc:.4f}, still at the ceiling")}

    graded = r["mid"].get(NAIVE, {}).get("mean_forgetting")
    j3 = {"id": "T3", "measured": f"`{NAIVE}` mean forgetting at scale {r['scales'][1]} is {graded}, and at "
                                  f"{r['scales'][0]} it is {r['open'].get(NAIVE, {}).get('mean_forgetting')}",
          "verdict": ("REFUSED -- the arm is missing from one run" if graded is None else
                      f"MET -- the middling setting loses {graded:.4f}, graded rather than occasional"
                      if graded >= GRADED else
                      f"FALSIFIER FIRED -- it loses {graded:.4f}, no more than a rounding artefact"
                      if graded <= FLAT else
                      f"NULL -- {graded:.4f}, between {FLAT:.2f} and {GRADED:.2f}")}

    d = r["accuracy"].get(NAIVE, {}).get("delta")
    j4 = {"id": "T4", "measured": f"`{NAIVE}` accuracy {r['open'].get(NAIVE, {}).get('final_accuracy')} open "
                                  f"against {r['mid'].get(NAIVE, {}).get('final_accuracy')} at scale "
                                  f"{r['scales'][1]}, delta {d if d is None else f'{d:+.4f}'} "
                                  f"({r['accuracy'].get(NAIVE, {}).get('sigma')} sigma)",
          "verdict": ("REFUSED -- the arm is missing from one run" if d is None else
                      f"MET -- the middling setting reads {abs(d):.4f} lower" if d <= -BAR_LEVEL else
                      f"FALSIFIER FIRED -- it reads {d:+.4f} higher" if d >= BAR_LEVEL else
                      f"NULL -- {d:+.4f}, within {BAR_LEVEL:.2f}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if r.get("runs", 0) < 2:
        print(f"== the environment gets a noisy cue ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the environment gets a noisy cue ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, tasks {r['task_names'][0]}")
    print(f"   environment: {r['env']}")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'arm':12} {'open':>9} {'mid':>9} {'delta':>9} {'sigma':>7} "
          f"{'forget o':>9} {'forget m':>9} {'delta':>9} {'sigma':>7}")
    for arm in ARMS:
        a, b = r["open"].get(arm, {}), r["mid"].get(arm, {})
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
    print("\n   (`e328` put the middling loop at 1.92 sigma and ended on the ceiling the whole thread shares: with")
    print("    deterministic cues a two-symbol task is two fixed vectors, so nothing spoke to acquisition)")
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
