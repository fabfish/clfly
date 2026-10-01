"""E328 -- is the middling loop worse than none? Forty replicates at the two settings that differed.

`e327` swept the feedback strength over 0.0, 0.25, 0.5 and 1.0 at five replicates each and its registration's
ordering **fired**: mean forgetting read 0.0437, 0.0000, **0.1000**, 0.0000. The table underneath said why the
sweep could not settle anything -- `learned` was `[1.0, 1.0, 1.0]` on all twenty arms, so every replicate at every
strength solved every task perfectly and the only thing that moved was **whether a replicate forgot anything at
all**: **1, 0, 2 and 0 replicates of five**. Those counts are the means divided by five, so the ordering rested on
**one replicate**, and at those proportions a 2 sigma separation needs about 40 replicates per level.

This unit buys that resolution for the two settings whose rates differed, and only for those two: **0.0 and 0.5**,
`naive`, **forty replicates each**. It is two runs rather than four because the question the five-replicate sweep
actually left open is the practical one -- is a middling loop worse than no loop? -- and because `e327`'s T4
established that a feedback of 0.0 is **bit-identical** to the loop unwired, so the 0.0 arm is also the control.

Four claims, registered before these runs' readings. A replicate counts as **forgetting** when its
`mean_forgetting` exceeds **0.05**, a convention recorded here because the quantity is a share of what the arm had
and gave back and can be a hair above zero for arithmetic reasons.

- **T1 -- one configuration except the strength.** Same circuit, read-out fingerprint, task names, replicate counts
  and environment draw, the last except in the strength it records. **Falsifier**: any other field differing.
- **T2 -- and the middling setting forgets more often.** The forget-rate at **0.5** exceeds the rate at **0.0** by
  at least **0.15**, which is what the five-replicate rates (0.20 against 0.40) would give at about 2 sigma on forty
  replicates each. **Falsifier**: at or below 0.00, i.e. the middling setting forgets no more often. **Null**:
  between 0.00 and 0.15.
- **T3 -- and the open setting is not perfect either.** Its forget-rate is at least **0.05**, i.e. two or more of its
  forty replicates forget. **Falsifier**: none of forty. **Null**: exactly one.
- **T4 -- and what a forgetting replicate loses is retention and never learning.** Every replicate at either
  setting whose mean forgetting exceeds 0.05 has `learned` of **`[1.0, 1.0, 1.0]`**, so the failure is what was
  given back and not what was never acquired. This is the claim the five-replicate sweep could only suggest, and it
  is the one that runs across **eighty** replicates here. **Falsifier**: one whose `learned` is short of perfect.

**What it cannot do.** *Two settings of four*: 0.25 and 1.0 stay at five replicates, so this unit can settle
whether 0.5 is worse than 0.0 and cannot order 0.25 or 1.0 against either. **Forty replicates resolve a difference
of about 0.20 and not one of 0.10**, so a real but small dose effect would come back as its null. *One arm, one
circuit, one read-out width, one gain*: `replay` and the block arms are not run, and the gain is fixed where the
sweep fixed it. *The task is at ceiling*: accuracy ran 0.93 to 1.00 across `e327`'s four settings, so only retention
is in play. *And there is still no reward*: the label is the cue, delivered at step 0, and the agent's action is an
input rather than a decision.
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
PATHS = {"0p00": RUNS / "e328_scale_0p00_40reps.json", "0p50": RUNS / "e328_scale_0p50_40reps.json"}
ORDER = ("0p00", "0p50")
SCALES = {"0p00": 0.0, "0p50": 0.5}
NAIVE = "naive"
#: a replicate counts as forgetting above this, and T2's and T3's bars
FORGETS = 0.05
BAR = 0.15
POSITIVE = 0.05
NONE = 0.0
CLAIMS = (
    ("T1", "one configuration except the strength",
     "Same circuit, read-out fingerprint, task names, replicate counts and environment draw, the last except in the "
     "strength",
     "falsifier: any other field differing"),
    ("T2", f"and the middling setting forgets more often, by {BAR:.2f}",
     f"The forget-rate at {SCALES['0p50']} exceeds the rate at {SCALES['0p00']} by at least {BAR:.2f}",
     "falsifier: at or below 0.00, the middling setting forgetting no more often"),
    ("T3", f"and the open setting is not perfect either, at least {POSITIVE:.2f}",
     f"The forget-rate at {SCALES['0p00']} is at least {POSITIVE:.2f}, i.e. two or more of its forty replicates",
     "falsifier: none of forty"),
    ("T4", "and a forgetting replicate loses retention and never learning",
     "Every replicate above the forgetting threshold has `learned` of [1.0, 1.0, 1.0]",
     "falsifier: one whose `learned` is short of perfect"),
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


def proportion(k: int, n: int) -> float | None:
    return (k / n) if n else None


def two_proportion_sem(k1: int, n1: int, k2: int, n2: int) -> float | None:
    """The standard error of a difference of two independent proportions, or ``None`` if either is undefined."""
    if not n1 or not n2:
        return None
    p1, p2 = k1 / n1, k2 / n2
    return math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)


def summarise(run: dict | None) -> dict:
    reps = replicates(run)
    forgets = [r for r in reps if r.get("mean_forgetting", 0.0) > FORGETS]
    return {
        "n": len(reps),
        "n_forgetting": len(forgets),
        "rate": proportion(len(forgets), len(reps)),
        "final_accuracy": (statistics.fmean([r["final_accuracy"] for r in reps]) if reps else None),
        "mean_forgetting": (statistics.fmean([r["mean_forgetting"] for r in reps]) if reps else None),
        #: what the forgetting replicates actually lost: `learned` is the per-task accuracy right after learning
        "forgetting_learned": [[float(x) for x in r.get("learned", [])] for r in forgets],
        "learned_short_of_perfect": [[float(x) for x in r.get("learned", [])] for r in forgets
                                     if any(float(x) < 1.0 for x in r.get("learned", []))],
    }


def reading(paths=None) -> dict:
    paths = paths or PATHS
    runs = {tag: load(path) for tag, path in paths.items()}
    present = [tag for tag in ORDER if runs.get(tag)]
    if len(present) < 2:
        return {"runs": len(present), "missing": [str(paths[t]) for t in ORDER if not runs.get(t)]}
    a, b = runs[present[0]], runs[present[1]]
    ca, cb = a.get("config", {}), b.get("config", {})
    ignored = ("json_out", "loop_scale")
    config_diff = {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
                   if k not in ignored and ca.get(k) != cb.get(k)}
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    env_diff = {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                if k != "scale" and ea.get(k) != eb.get(k)}
    return {
        "runs": 2,
        "levels": present,
        "scales": [SCALES[t] for t in present],
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "config_diff": config_diff,
        "env_diff": env_diff,
        "settings": {t: summarise(runs[t]) for t in present},
        "difference": (lambda sa, sb: (sb["rate"] - sa["rate"]) if sa["rate"] is not None and sb["rate"] is not None
                       else None)(summarise(a), summarise(b)),
        "difference_sem": two_proportion_sem(summarise(a)["n_forgetting"], summarise(a)["n"],
                                             summarise(b)["n_forgetting"], summarise(b)["n"]),
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if r.get("runs", 0) < 2 or "circuits" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk"} for c in CLAIMS]

    same = (r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1]
            and r["task_names"][0] == r["task_names"][1]
            and len({s["n"] for s in r["settings"].values()}) == 1)
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks "
                                  f"{r['task_names'][0]}, replicate counts "
                                  f"{[s['n'] for s in r['settings'].values()]}, config differing "
                                  f"{r['config_diff']}, environment differing {r['env_diff']}",
          "verdict": "MET -- one configuration except the strength" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}, tasks {r['task_names']}"}

    lo, hi = r["levels"][0], r["levels"][1]
    sa, sb = r["settings"][lo], r["settings"][hi]
    d, sem = r["difference"], r["difference_sem"]
    detail = f"{SCALES[lo]} {sa['n_forgetting']} of {sa['n']} ({sa['rate']:.3f}); " \
             f"{SCALES[hi]} {sb['n_forgetting']} of {sb['n']} ({sb['rate']:.3f})"
    j2 = {"id": "T2", "measured": f"forget-rates {detail}; difference {d:+.4f} with a two-proportion sem of "
                                  f"{sem:.4f}" if d is not None and sem else f"forget-rates {detail}",
          "verdict": ("REFUSED -- a rate is undefined" if d is None else
                      f"MET -- the middling setting forgets {d:.3f} more often" if d >= BAR else
                      f"FALSIFIER FIRED -- it forgets {d:+.4f} more often" if d <= NONE else
                      f"NULL -- {d:+.4f}, between {NONE:.2f} and {BAR:.2f}")}

    j3 = {"id": "T3", "measured": f"{sa['n_forgetting']} of {sa['n']} replicates forget at {SCALES[lo]}, a rate of "
                                  f"{sa['rate']:.3f}",
          "verdict": f"MET -- the open loop forgets on {sa['n_forgetting']} of {sa['n']}" if sa["rate"] >= POSITIVE
          else "FALSIFIER FIRED -- none of its replicates forgets" if sa["n_forgetting"] == 0 else
          f"NULL -- {sa['n_forgetting']} of {sa['n']}, below the {POSITIVE:.2f} bar"}

    bad = [[t, s["learned_short_of_perfect"]] for t, s in r["settings"].items() if s["learned_short_of_perfect"]]
    total = sum(s["n_forgetting"] for s in r["settings"].values())
    j4 = {"id": "T4", "measured": f"{total} forgetting replicates over the two settings; those whose `learned` is "
                                  f"short of perfect: {bad}",
          "verdict": "MET -- every forgetting replicate learned all of its tasks" if not bad else
                     f"FALSIFIER FIRED -- {len(bad)} setting(s) hold a replicate that never learned"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("runs"):
        print(f"== is the middling loop worse ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== is the middling loop worse than none ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, arm `{NAIVE}`, "
          f"forgetting threshold {FORGETS}")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'scale':>7} {'n':>4} {'forgets':>8} {'rate':>7} {'accuracy':>10} {'forgetting':>12}")
    for tag in r["levels"]:
        s = r["settings"][tag]
        print(f"   {SCALES[tag]:7.2f} {s['n']:4} {s['n_forgetting']:8} {s['rate']:7.3f} "
              f"{s['final_accuracy']:10.4f} {s['mean_forgetting']:12.4f}")
    if r["difference"] is not None:
        print(f"   difference {r['difference']:+.4f} with a two-proportion sem of {r['difference_sem']:.4f}")
    print(f"\n   what the forgetting replicates learned (per task, right after learning it): "
          f"{ {t: s['forgetting_learned'] for t, s in r['settings'].items()} }")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e327` swept four strengths at five replicates and its ordering rested on one of those replicates;")
    print("    this buys the resolution for the two settings whose rates differed)")
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
