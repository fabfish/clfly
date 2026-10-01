"""E327 -- the feedback is a dose: four strengths, and what the loop does between zero and one.

`e325` built the closed loop, `e326` trained through it and found the direction the registration did not predict:
`naive` went to **1.0000** accuracy and **exactly 0.0000** forgetting, and `ewc-block` improved as well. Its own
finding named both the mechanism and the weakness in one sentence -- a channel whose input at step ``t`` is a
monotone function of the state at step ``t - 1`` is a **latch**, and a latch is a memory, so a task that is
*hold a value across a gap* is one a self-exciting channel can hold; but the feedback strength, `--loop-scale`, was
**a knob and not a sweep**, and a latch's effect should grow with it.

This unit turns the knob. Four strengths, `naive` at five replicates each, the same circuit, read-out, task names,
cue sets and seeds: **0.0, 0.25, 0.5 and 1.0**. The first of those is the control that makes the sweep readable --
a feedback of zero is the world disconnected -- and `e326`'s unwired run is what it is compared against.

Four claims, registered before the three lower doses were read. **The 1.0 point is `e326`'s closed run and the 0.0
point should reproduce its open run**; what is registered here is the **shape between them**, which nothing has
measured.

- **T1 -- one configuration in four doses.** Same circuit, read-out fingerprint, task names and replicate counts at
  every level; the configs differ only in the feedback strength and the output path, and the environment draws agree
  except in the strength they record. **Falsifier**: any other field differing, or a differing task name.
- **T2 -- and forgetting is non-increasing in the dose.** Along 0.0, 0.25, 0.5, 1.0 the five-replicate mean
  forgetting never rises by more than **0.005**. This is the latch's prediction stated as an ordering: the more of
  the agent's own state comes back, the less there is to lose. **Falsifier**: an adjacent rise above that.
- **T3 -- and the dose is real at the ends.** Mean forgetting at **0.0** exceeds mean forgetting at **1.0** by at
  least **0.02**. **Falsifier**: at or below 0.005. **Null**: between the two.
- **T4 -- and the zero dose is off.** The scale-0.0 run's five `naive` replicates reproduce `e326`'s **unwired** run
  exactly, on accuracy and on forgetting, replicate for replicate. A feedback of zero is not a small loop, it is no
  loop, and this is the check that says the two artifacts are the same computation. **Falsifier**: any replicate
  differing.

**What it cannot do.** *One arm and five replicates*: `replay` and the block arms are not swept, and five replicates
put one standard error of a paired difference near 0.02 on accuracy and near 0.01 on forgetting. *The task is still
the one `e326` showed is at or near ceiling* -- the unwired run reads 0.9708, so an accuracy dose-response has almost
no room and T2 and T3 are stated on **forgetting**, which does. *One circuit, one read-out width and one gain*: the
sweep moves the strength only, and a latch's effect at a different gain or a different action population size is not
measured. *Four levels are an order and not a curve*: a monotone rise across four points is a direction, and the
exponent is not in this grid. *And there is still no reward*: the label is the cue, delivered at step 0, and the
agent's action is an input rather than a decision.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the four doses, in the order the ordering claim is stated over
LEVELS = (("0p00", 0.0), ("0p25", 0.25), ("0p50", 0.5), ("1p00", 1.0))
PATHS = {tag: RUNS / f"e327_scale_{tag}.json" for tag, _ in LEVELS}
#: the unwired run the zero dose has to reproduce
UNWIRED = RUNS / "e326_open_loop.json"
NAIVE = "naive"
#: T2's tolerance, T3's bar and its falsifier
RISE = 0.005
BAR = 0.02
FLAT = 0.005
#: fields a config may differ in across the doses, being the manipulation and the output path
IGNORED_CONFIG = ("json_out", "loop_scale")
CLAIMS = (
    ("T1", "one configuration in four doses",
     "Same circuit, read-out fingerprint, task names and replicate counts; configs differing only in the feedback "
     "strength and the output path, and environment draws agreeing except in the strength",
     "falsifier: any other field differing, or a differing task name"),
    ("T2", f"and forgetting is non-increasing in the dose, no adjacent rise above {RISE:.3f}",
     f"Along {', '.join(tag for tag, _ in LEVELS)} the five-replicate mean forgetting never rises by more than "
     f"{RISE:.3f}",
     "falsifier: an adjacent rise above that"),
    ("T3", f"and the dose is real at the ends: 0.0 exceeds 1.0 by {BAR:.2f}",
     f"Mean forgetting at 0.0 exceeds mean forgetting at 1.0 by at least {BAR:.2f}",
     f"falsifier: at or below {FLAT:.3f}"),
    ("T4", "and the zero dose is off: scale 0.0 reproduces the unwired run exactly",
     "The scale-0.0 run's five replicates reproduce `e326`'s unwired run on accuracy and forgetting",
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


def replicates(run: dict | None, arm: str = NAIVE) -> list[dict]:
    if not run:
        return []
    method = run.get("methods", {}).get(arm)
    return list(method.get("replicates", [])) if isinstance(method, dict) else []


def config_diff(a: dict, b: dict) -> dict:
    ca, cb = a.get("config", {}), b.get("config", {})
    return {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
            if k not in IGNORED_CONFIG and ca.get(k) != cb.get(k)}


def env_diff(a: dict, b: dict) -> dict:
    """The environment draws of two doses, which are allowed to differ in the strength they record."""
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
            if k != "scale" and ea.get(k) != eb.get(k)}


def reading(paths=None, unwired=UNWIRED) -> dict:
    paths = paths or PATHS
    runs = {tag: load(path) for tag, path in paths.items()}
    present = [tag for tag, _ in LEVELS if runs.get(tag)]
    if len(present) < 2:
        return {"runs": len(present), "missing": [str(paths[t]) for t, _ in LEVELS if not runs.get(t)]}
    base = runs[present[0]]
    return {
        "runs": len(present),
        "missing": [str(paths[t]) for t, _ in LEVELS if not runs.get(t)],
        "levels": [tag for tag, _ in LEVELS],
        "scales": [next(s for t, s in LEVELS if t == tag) for tag in present],
        "circuits": [runs[tag].get("circuit") for tag in present],
        "readout": [runs[tag].get("readout", {}).get("subset_sha1") for tag in present],
        "task_names": [[t.get("name") for t in runs[tag].get("tasks", [])] for tag in present],
        "n_replicates": [len(replicates(runs[tag])) for tag in present],
        "config_diff": [config_diff(base, runs[tag]) for tag in present[1:]],
        "env_diff": [env_diff(base, runs[tag]) for tag in present[1:]],
        "accuracy": [runs[tag]["methods"][NAIVE].get("final_accuracy") for tag in present],
        "forgetting": [runs[tag]["methods"][NAIVE].get("mean_forgetting") for tag in present],
        "per_replicate": {tag: [{"final_accuracy": r["final_accuracy"],
                                 "mean_forgetting": r["mean_forgetting"]}
                                for r in replicates(runs[tag])] for tag in present},
        "unwired": ([{"final_accuracy": r["final_accuracy"], "mean_forgetting": r["mean_forgetting"]}
                     for r in replicates(load(unwired))] if load(unwired) else None),
    }


def judge(r: dict) -> list[dict]:
    tags = r.get("levels", [])
    if r.get("runs", 0) < 2 or "circuits" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- too few of the doses are on disk"} for c in CLAIMS]

    same = (len(set(r["circuits"])) == 1 and len(set(r["readout"])) == 1
            and len({tuple(n) for n in r["task_names"]}) == 1 and len(set(r["n_replicates"])) == 1)
    diffs = [d for d in r["config_diff"] if d] + [d for d in r["env_diff"] if d]
    j1 = {"id": "T1", "measured": f"{r['runs']} of {len(tags)} doses; circuits {r['circuits']}, read-out "
                                  f"{r['readout']}, counts {r['n_replicates']}, unexpected config differences "
                                  f"{diffs}",
          "verdict": "MET -- one configuration in four doses" if same and not diffs else
          f"FALSIFIER FIRED -- config {diffs}, read-out {r['readout']}, tasks {r['task_names']}"}

    forget = r["forgetting"]
    rises = [(tags[i], tags[i + 1], forget[i + 1] - forget[i])
             for i in range(len(forget) - 1) if forget[i + 1] - forget[i] > RISE]
    detail = " ".join(f"{t} {f:.4f}" for t, f in zip(tags, forget))
    j2 = {"id": "T2", "measured": f"mean forgetting along the doses: {detail}; rises above {RISE:.3f}: "
                                  f"{[(a, b, round(d, 4)) for a, b, d in rises]}",
          "verdict": "MET -- the dose does not raise forgetting anywhere along the sweep" if not rises else
                     f"FALSIFIER FIRED -- forgetting rises at {[b for _, b, _ in rises]}"}

    drop = forget[0] - forget[-1]
    j3 = {"id": "T3", "measured": f"forgetting {forget[0]:.4f} at scale {r['scales'][0]} against {forget[-1]:.4f} "
                                  f"at {r['scales'][-1]}, a drop of {drop:.4f}",
          "verdict": f"MET -- the loop removes {drop:.4f} of the forgetting" if drop >= BAR else
          f"FALSIFIER FIRED -- the ends differ by only {drop:.4f}" if drop <= FLAT else
          f"NULL -- {drop:.4f}, between {FLAT:.3f} and {BAR:.2f}"}

    zero, unwired = r["per_replicate"].get(tags[0]), r["unwired"]
    same_reps = bool(zero) and unwired is not None and len(zero) == len(unwired) and all(
        abs(a["final_accuracy"] - b["final_accuracy"]) == 0 and abs(a["mean_forgetting"] - b["mean_forgetting"]) == 0
        for a, b in zip(zero, unwired))
    j4 = {"id": "T4", "measured": f"{len(zero or [])} replicates at scale {r['scales'][0]} against "
                                  f"{len(unwired or [])} in `e326`'s unwired run; identical {same_reps}",
          "verdict": "MET -- a feedback of zero is no loop, to the last digit" if same_reps else
                     "REFUSED -- the unwired comparison is not on disk" if unwired is None else
                     "FALSIFIER FIRED -- the zero dose differs from the unwired run"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("runs"):
        print(f"== the feedback is a dose ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the feedback is a dose ==")
    print(f"   {r['runs']} doses at {r['circuits'][0]}, read-out {r['readout'][0]}, "
          f"{r['n_replicates'][0]} replicates each, arm `{NAIVE}`")
    print(f"   unexpected config differences: {[d for d in r['config_diff'] if d] or 'none'}")
    print(f"   unexpected environment differences: {[d for d in r['env_diff'] if d] or 'none'}")
    print(f"\n   {'scale':>7} {'accuracy':>10} {'forgetting':>12}")
    for tag, scale, acc, f in zip(r["levels"], r["scales"], r["accuracy"], r["forgetting"]):
        print(f"   {scale:7.2f} {acc:10.4f} {f:12.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e326` trained through the loop at one strength and found it made the task easier and drove")
    print("    forgetting to zero; this asks whether the strength is the knob that does it)")
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
