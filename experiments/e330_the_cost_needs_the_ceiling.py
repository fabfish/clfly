"""E330 -- the cost needs the ceiling? Forty replicates of `naive` on the noisy environment.

`e328` put the middling feedback strength at **1.92 sigma** on forty replicates of the **easy** environment -- whose
cue is two fixed vectors in twelve neurons, so every arm solved every task and the only quantity left to move was
whether a replicate forgot at all. `e329` then built the instrument that environment lacked: eight cue symbols per
task and a noise of 1.0, so `naive` reads **0.5292** against a chance of 0.125. On that environment, at **five**
replicates, nothing reproduced: `naive`'s accuracy fell by 0.0361 at **0.92 sigma**, `ewc-block` read **higher**
under the loop, and neither arm resolved on either quantity. `e329`'s own finding named the fork: *the effect is not
there on a task with headroom, or five replicates cannot see it* -- and priced it, the honest interval being the
difference plus or minus 0.039.

This unit takes the fork at the same **forty** replicates `e328` used, and only for `naive`: two runs at scale
**0.0** and **0.5** on the **noisy eight-symbol** environment. Forty replicates of one arm is what the arithmetic
supports -- `e329`'s five-replicate standard error of 0.039 falls to about **0.014**, so an effect of the size that
unit saw would land near 2.6 sigma -- and it keeps the two units' power comparable, which is what makes their
answers comparable.

Four claims, registered before these runs' readings. Each head is eight-way, so chance is **0.125**.

- **T1 -- one configuration except the strength.** Same circuit, read-out fingerprint, task names, replicate counts
  and environment draw (24 symbols, twelve cue neurons, noise 1.0), the last differing only in the strength.
  **Falsifier**: any other field differing.
- **T2 -- and the accuracy cost is there.** `naive` reads **lower** at scale 0.5 than at 0.0 by at least **0.02**,
  paired over forty replicates. `e329`'s five-replicate point estimate was 0.0361 in that direction at 0.92 sigma;
  at forty replicates the same effect would be about 2.6. **Falsifier**: higher by 0.02 or more, which would say the
  sign is the other way and the five-replicate lean was noise. **Null**: within 0.02.
- **T3 -- and what it costs is level and not retention.** The mean forgetting at the middling setting differs from
  the open one by **less than 0.04**, a bar of about two standard errors at this n. **Falsifier**: a difference of
  0.06 or more. **Null**: between 0.04 and 0.06.
- **T4 -- and the instrument still has headroom.** `naive`'s open-setting accuracy is **below 0.60** where the
  chance is 0.125 and `e329` measured 0.5292, so this unit is measuring the same task and not a saturated one.
  **Falsifier**: at or above 0.70. **Null**: between 0.60 and 0.70.

**What it cannot do.** *One arm*: `ewc-block`, `replay` and the block arms are not run, and `e329`'s only resolved
lean was `ewc-block`'s -- backwards -- so this unit can speak to `naive` and not to whether a penalty changes it.
*Two settings of four*: 0.25 and 1.0 are not run, so the "hazard with a window" reading `e328` proposed is not
tested here. *Forty replicates put the accuracy standard error near 0.014 and the forgetting one near 0.021*, so a
real effect of 0.02 on either quantity would come back as this unit's null. *The accuracy and the forgetting claims
rest on the same forty runs*: the two quantities correlate within a replicate, so they are not two independent
tests. *And there is still no reward*: the label is the cue, delivered at step 0, and the agent's action is an input
rather than a decision.
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
PATHS = {"0p00": RUNS / "e330_noisy_naive40_scale_0p00.json",
         "0p50": RUNS / "e330_noisy_naive40_scale_0p50.json"}
ORDER = ("0p00", "0p50")
SCALES = {"0p00": 0.0, "0p50": 0.5}
NAIVE = "naive"
#: the eight-way head's chance, and the three thresholds
CHANCE = 0.125
BAR_ACCURACY = 0.02
FLAT_FORGET = 0.04
MOVED_FORGET = 0.06
CEILING = 0.60
SOLVED = 0.70
CLAIMS = (
    ("T1", "one configuration except the strength",
     "Same circuit, read-out fingerprint, task names, replicate counts and environment draw, the last differing only "
     "in the strength",
     "falsifier: any other field differing"),
    ("T2", f"and the accuracy cost is there, at least {BAR_ACCURACY:.2f} lower",
     f"`{NAIVE}` reads lower at scale {SCALES['0p50']} than at {SCALES['0p00']} by at least {BAR_ACCURACY:.2f}",
     f"falsifier: higher by {BAR_ACCURACY:.2f} or more"),
    ("T3", f"and what it costs is level and not retention: forgetting moves less than {FLAT_FORGET:.2f}",
     f"The mean forgetting differs between the settings by less than {FLAT_FORGET:.2f}",
     f"falsifier: a difference of {MOVED_FORGET:.2f} or more"),
    ("T4", f"and the instrument still has headroom: `{NAIVE}` below {CEILING:.2f} open",
     f"`{NAIVE}`'s open-setting accuracy is below {CEILING:.2f}, against a chance of {CHANCE:.3f}",
     f"falsifier: at or above {SOLVED:.2f}"),
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
                        if k not in ("json_out", "loop_scale") and ca.get(k) != cb.get(k)},
        "env_diff": {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                     if k != "scale" and ea.get(k) != eb.get(k)},
        "env": ea,
        "n": [len(replicates(a)), len(replicates(b))],
        "accuracy": paired([r["final_accuracy"] for r in replicates(b)],
                           [r["final_accuracy"] for r in replicates(a)]),
        "forgetting": paired([r["mean_forgetting"] for r in replicates(b)],
                             [r["mean_forgetting"] for r in replicates(a)]),
        "open": {"final_accuracy": a["methods"][NAIVE].get("final_accuracy"),
                 "mean_forgetting": a["methods"][NAIVE].get("mean_forgetting")},
        "mid": {"final_accuracy": b["methods"][NAIVE].get("final_accuracy"),
                "mean_forgetting": b["methods"][NAIVE].get("mean_forgetting")},
        "open_spread": {"accuracy_sd": (statistics.stdev([r["final_accuracy"] for r in replicates(a)])
                                        if len(replicates(a)) > 1 else None),
                        "forgetting_sd": (statistics.stdev([r["mean_forgetting"] for r in replicates(a)])
                                          if len(replicates(a)) > 1 else None)},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if r.get("runs", 0) < 2 or "circuits" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    same = (r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1]
            and r["task_names"][0] == r["task_names"][1] and r["n"][0] == r["n"][1] and r["n"][0] > 1)
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks {r['task_names'][0]}, "
                                  f"{r['n'][0]} replicates each, environment {r['env']}, config differing "
                                  f"{r['config_diff']}, environment differing {r['env_diff']}",
          "verdict": "MET -- one configuration except the strength" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}, counts {r['n']}"}

    d = r["accuracy"].get("delta")
    sem = r["accuracy"].get("sem")
    j2 = {"id": "T2", "measured": f"`{NAIVE}` accuracy {r['open'].get('final_accuracy')} open against "
                                  f"{r['mid'].get('final_accuracy')} at scale {r['scales'][1]}, delta "
                                  f"{'n/a' if d is None else f'{d:+.4f}'} "
                                  f"({'n/a' if sem is None else f'sem {sem:.4f}'}), "
                                  f"{r['accuracy'].get('sigma')} sigma over {r['accuracy'].get('n')} replicates",
          "verdict": ("REFUSED -- the arm is missing from one run" if d is None else
                      f"MET -- the middling setting reads {abs(d):.4f} lower" if d <= -BAR_ACCURACY else
                      f"FALSIFIER FIRED -- it reads {d:+.4f} higher" if d >= BAR_ACCURACY else
                      f"NULL -- {d:+.4f}, within {BAR_ACCURACY:.2f}")}

    f = r["forgetting"].get("delta")
    j3 = {"id": "T3", "measured": f"`{NAIVE}` forgetting {r['open'].get('mean_forgetting')} open against "
                                  f"{r['mid'].get('mean_forgetting')} at scale {r['scales'][1]}, delta "
                                  f"{'n/a' if f is None else f'{f:+.4f}'} "
                                  f"({r['forgetting'].get('sigma')} sigma)",
          "verdict": ("REFUSED -- the arm is missing from one run" if f is None else
                      f"MET -- the two settings differ by only {abs(f):.4f} of forgetting" if abs(f) < FLAT_FORGET
                      else f"FALSIFIER FIRED -- they differ by {abs(f):.4f}" if abs(f) >= MOVED_FORGET else
                      f"NULL -- {abs(f):.4f}, between {FLAT_FORGET:.2f} and {MOVED_FORGET:.2f}")}

    acc = r["open"].get("final_accuracy")
    j4 = {"id": "T4", "measured": f"`{NAIVE}` open-setting final accuracy {acc} against a chance of {CHANCE:.3f}, "
                                  f"per-replicate sd {r['open_spread'].get('accuracy_sd')}",
          "verdict": ("REFUSED -- the arm is missing from one run" if acc is None else
                      f"MET -- the instrument reads {acc:.4f}, with room under the ceiling" if acc < CEILING else
                      f"NULL -- {acc:.4f}, between {CEILING:.2f} and {SOLVED:.2f}" if acc < SOLVED else
                      f"FALSIFIER FIRED -- it reads {acc:.4f}, near the ceiling")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if r.get("runs", 0) < 2:
        print(f"== the cost needs the ceiling? ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the cost needs the ceiling? ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, tasks {r['task_names'][0]}, "
          f"{r['n'][0]} replicates each, arm `{NAIVE}`")
    print(f"   environment: {r['env']}")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'setting':>8} {'accuracy':>10} {'forgetting':>12}")
    for tag, key in zip(r["levels"], ("open", "mid")):
        print(f"   {SCALES[tag]:8.2f} {r[key]['final_accuracy']:10.4f} {r[key]['mean_forgetting']:12.4f}")
    for key, name in (("accuracy", "accuracy"), ("forgetting", "forgetting")):
        v = r[key]
        print(f"   paired {name:10} delta {v['delta']:+.4f}  sem {v['sem']:.4f}  sigma {v['sigma']:.2f}  "
              f"n {v['n']}")
    print(f"   open-setting per-replicate sd: accuracy {r['open_spread']['accuracy_sd']:.4f}, "
          f"forgetting {r['open_spread']['forgetting_sd']:.4f}")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e328` put this cost at 1.92 sigma on the EASY environment; `e329` built the noisy one and at five")
    print("    replicates saw nothing, naming the fork -- not there, or not seen. This takes it at forty)")
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
