"""E336 -- the direction of the update: the one quantity three exclusions point at.

`e333` measured `replay`'s retention moving in opposite directions under the thread's last two changes to the
world's channel, and `e334` and `e335` between them excluded the three accounts a **norm** can speak to:

    e334   not the stored features fitting worse          0.32 sigma on the loss the arm minimises
    e335   not the buffer's contents differing            byte-identical, element by element
    e335   not the body drifting further                  the carried body moved 2.93% LESS

`e335` ended on the one its own "what it cannot do" had written in advance -- *"drift is a norm and not a
direction: a body that moved the same distance in a different direction is invisible"* -- and named the instrument:
a per-task **direction** of `theta_final - theta_before`, which no artifact in this corpus records.

**This unit records it.** `run_method` now keeps, per task, the update `theta_after - theta_before` sampled at a
fixed index set and normalised to a unit vector -- a fixed subspace drawn from a constant seed, so two runs' vectors
live in the **same** coordinates and a cosine between them estimates the cosine between the full updates. Two runs,
`replay` alone, five replicates, on `e333`'s two worlds, same seeds.

Four claims, registered before these runs' readings. Every cosine is between unit vectors in the same 256-dimensional
subspace, and the three groups are: **within** a run (pairs of its own five replicates), and **across** the two runs.

- **T1 -- one configuration except the rule, on the same coordinates.** Same circuit, read-out fingerprint, task
  names, replicate counts and environment draw, the last differing only in the leak; and every recorded direction
  carries the **same index fingerprint**. **Falsifier**: any other field differing, or two runs whose subspaces are
  not the same.
- **T2 -- and the direction is reproducible within a world.** The mean within-run cosine, over tasks and over
  replicate pairs, is at least **0.5**. Without this the across-run comparison has no scale: two runs of one
  configuration must point the same way if a difference between configurations is to mean anything.
  **Falsifier**: below 0.25. **Null**: between.
- **T3 -- and the direction differs between the worlds.** The mean **across**-run cosine is **lower** than the mean
  within-run cosine by at least **0.10**. This is the account the three exclusions leave: the body that retained
  less did not move further, it moved **differently**. **Falsifier**: a drop below 0.02. **Null**: between.
- **T4 -- and it differs in every task.** The across-run cosine is below the within-run cosine for **each of the
  three tasks**, by at least **0.05**. **Falsifier**: a task where it is not. **Null**: a task between 0.02 and
  0.05.

**What it cannot do.** *Two runs and one arm*: `naive`, `ewc` and the block arms are not run, and `e332`'s other
sign is not asked. *A 256-dimensional subspace of a 20,079-dimensional update*: a cosine here estimates the full
one and is not it, and a difference that lives entirely outside the subspace is invisible -- the subspace is fixed
and recorded, so a reader can see which one it was. *Direction is a summary of the whole trajectory*: the update is
taken once per task, so a path that curved and came back is indistinguishable from a straight one. *And the claim
is about the four arms' shared body*: what moves is `theta`, so this says nothing about the bias channel, which no
penalty in this project covers.
"""

from __future__ import annotations

import argparse
import itertools
import json
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

RUNS = Path("runs")
PATHS = {"instant": RUNS / "e336_direction_instant.json", "carry": RUNS / "e336_direction_carry.json"}
ORDER = ("instant", "carry")
LEAKS = {"instant": 1.0, "carry": 0.35}
ARM = "replay"
REPRODUCIBLE = 0.5
FLOOR = 0.25
DROP = 0.10
THIN = 0.02
EACH = 0.05
EACH_THIN = 0.02
CLAIMS = (
    ("T1", "one configuration except the rule, on the same coordinates",
     "Same circuit, read-out fingerprint, task names, replicate counts and environment draw, differing only in the "
     "leak, and every recorded direction carrying the same index fingerprint",
     "falsifier: any other field differing, or two runs whose subspaces are not the same"),
    ("T2", f"and the direction is reproducible within a world, at least {REPRODUCIBLE:.2f}",
     f"The mean within-run cosine over tasks and replicate pairs is at least {REPRODUCIBLE:.2f}",
     f"falsifier: below {FLOOR:.2f}"),
    ("T3", f"and the direction differs between the worlds, by {DROP:.2f}",
     f"The mean across-run cosine is lower than the mean within-run cosine by at least {DROP:.2f}",
     f"falsifier: a drop below {THIN:.2f}"),
    ("T4", f"and it differs in every task, by {EACH:.2f}",
     f"The across-run cosine is below the within-run cosine for each of the three tasks by at least {EACH:.2f}",
     f"falsifier: a task where it is not"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def directions(run: dict | None, arm: str = ARM) -> list[list] | None:
    """Per replicate, per task: the unit vector the update was recorded as, or ``None`` where it is absent."""
    if not run:
        return None
    reps = run.get("methods", {}).get(arm, {}).get("replicates")
    if not isinstance(reps, list) or not reps:
        return None
    out = []
    for r in reps:
        entries = r.get("theta_direction")
        if not isinstance(entries, list) or not entries:
            return None
        out.append([e.get("values") for e in entries])
    return out


def fingerprint(run: dict | None, arm: str = ARM) -> list | None:
    if not run:
        return None
    reps = run.get("methods", {}).get(arm, {}).get("replicates")
    if not isinstance(reps, list) or not reps:
        return None
    entries = reps[0].get("theta_direction")
    return [e.get("index_sha1") for e in entries] if isinstance(entries, list) else None


def cosine(a: list, b: list) -> float | None:
    if not a or not b or len(a) != len(b):
        return None
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb) if na and nb else None


def within(vectors: list[list]) -> list[list]:
    """Per task, the cosines between every pair of replicates of one run."""
    n_tasks = len(vectors[0]) if vectors and vectors[0] else 0
    out = []
    for j in range(n_tasks):
        out.append([c for c in (cosine(vectors[i][j], vectors[k][j])
                                for i, k in itertools.combinations(range(len(vectors)), 2))
                    if c is not None])
    return out


def across(a: list[list], b: list[list]) -> list[list]:
    """Per task, the cosines between every replicate of one run and every replicate of the other."""
    n_tasks = min(len(a[0]), len(b[0])) if a and b else 0
    return [[c for c in (cosine(x[j], y[j]) for x in a for y in b) if c is not None]
            for j in range(n_tasks)]


def reading(paths=None) -> dict:
    paths = paths or PATHS
    runs = {tag: load(path) for tag, path in paths.items()}
    present = [tag for tag in ORDER if runs.get(tag)]
    if len(present) < 2:
        return {"runs": len(present), "missing": [str(paths[t]) for t in ORDER if not runs.get(t)]}
    a, b = runs[present[0]], runs[present[1]]
    va, vb = directions(a), directions(b)
    if va is None or vb is None:
        return {"runs": 2, "missing": ["the recorded directions"],
                "recorded": {"instant": va is not None, "carry": vb is not None}}
    wa, wb, xw = within(va), within(vb), across(va, vb)
    ca, cb = a.get("config", {}), b.get("config", {})
    ea, eb = a.get("env_draw") or {}, b.get("env_draw") or {}
    return {
        "runs": 2,
        "levels": present,
        "leaks": [(runs[t].get("env_draw") or {}).get("world_leak") for t in present],
        "arm": ARM,
        "n_replicates": [len(va), len(vb)],
        "n_tasks": len(wa),
        "dim": len(va[0][0]),
        "fingerprints": [fingerprint(a), fingerprint(b)],
        "circuits": [a.get("circuit"), b.get("circuit")],
        "readout": [a.get("readout", {}).get("subset_sha1"), b.get("readout", {}).get("subset_sha1")],
        "task_names": [[t.get("name") for t in a.get("tasks", [])],
                       [t.get("name") for t in b.get("tasks", [])]],
        "config_diff": {k: [ca.get(k), cb.get(k)] for k in sorted(set(ca) | set(cb))
                        if k not in ("json_out", "loop_world_leak") and ca.get(k) != cb.get(k)},
        "env_diff": {k: [ea.get(k), eb.get(k)] for k in sorted(set(ea) | set(eb))
                     if k != "world_leak" and ea.get(k) != eb.get(k)},
        "within": {"instant": wa, "carry": wb},
        "across": xw,
        "mean_within": {"instant": statistics.fmean([c for row in wa for c in row]) if any(wa) else None,
                        "carry": statistics.fmean([c for row in wb for c in row]) if any(wb) else None},
        "mean_across": [statistics.fmean(row) if row else None for row in xw],
        "mean_within_per_task": [[statistics.fmean(row) if row else None for row in wa],
                                 [statistics.fmean(row) if row else None for row in wb]],
        #: the norm the direction was normalised by, which e335 already compared; recorded beside the vectors
        "subspace_norm": [[e.get("subspace_norm") for e in r.get("theta_direction", [])]
                          for r in a.get("methods", {}).get(ARM, {}).get("replicates", [])],
        "forgetting": {"instant": a["methods"][ARM].get("mean_forgetting"),
                       "carry": b["methods"][ARM].get("mean_forgetting")},
        "timing_s": [duration_seconds(a), duration_seconds(b)],
    }


def judge(r: dict) -> list[dict]:
    if r.get("runs", 0) < 2 or "across" not in r:
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the two runs are not both on disk, or neither recorded a direction"}
                for c in CLAIMS]

    same = (r["circuits"][0] == r["circuits"][1] and r["readout"][0] == r["readout"][1]
            and r["task_names"][0] == r["task_names"][1] and r["n_replicates"][0] == r["n_replicates"][1] > 1
            and r["leaks"][0] == 1.0 and r["leaks"][1] < 1.0
            and r["fingerprints"][0] is not None and r["fingerprints"][0] == r["fingerprints"][1])
    j1 = {"id": "T1", "measured": f"circuits {r['circuits']}, read-out {r['readout']}, tasks {r['task_names'][0]}, "
                                  f"{r['n_replicates'][0]} replicates each, leaks {r['leaks']}, subspace "
                                  f"{r['dim']}-dimensional with fingerprints {r['fingerprints']}, config differing "
                                  f"{r['config_diff']}, environment differing {r['env_diff']}",
          "verdict": "MET -- one configuration except the rule, on one subspace" if same and not r["config_diff"]
          and not r["env_diff"] else
          f"FALSIFIER FIRED -- config {r['config_diff']}, environment {r['env_diff']}, fingerprints "
          f"{r['fingerprints']}, leaks {r['leaks']}"}

    mw = r["mean_within"]
    pooled = ([c for row in r["within"]["instant"] for c in row]
              + [c for row in r["within"]["carry"] for c in row])
    mean_within = statistics.fmean(pooled) if pooled else None
    j2 = {"id": "T2", "measured": f"the mean within-run cosine over tasks and replicate pairs: {mean_within} "
                                  f"(instantaneous {mw['instant']}, carried {mw['carry']})",
          "verdict": ("REFUSED -- no within-run pair was recorded" if mean_within is None else
                      f"MET -- two runs of one configuration point the same way, at {mean_within:.4f}" if
                      mean_within >= REPRODUCIBLE else
                      f"FALSIFIER FIRED -- the within-run cosine is only {mean_within:.4f}" if mean_within < FLOOR
                      else f"NULL -- {mean_within:.4f}, between {FLOOR:.2f} and {REPRODUCIBLE:.2f}")}

    per_task_across = r["mean_across"]
    drop = (mean_within - statistics.fmean([c for c in per_task_across if c is not None])
            if mean_within is not None and any(c is not None for c in per_task_across) else None)
    j3 = {"id": "T3", "measured": f"the across-run cosine per task {per_task_across}, mean "
                                  f"{None if drop is None else f'{statistics.fmean([c for c in per_task_across if c is not None]):.4f}'}"
                                  f" against the within-run mean {None if mean_within is None else f'{mean_within:.4f}'}"
                                  f", a drop of {None if drop is None else f'{drop:.4f}'}",
          "verdict": ("REFUSED -- a group is missing" if drop is None else
                      f"MET -- the worlds' updates point differently by {drop:.4f}" if drop >= DROP else
                      f"FALSIFIER FIRED -- they differ by only {drop:.4f}" if drop < THIN else
                      f"NULL -- {drop:.4f}, between {THIN:.2f} and {DROP:.2f}")}

    per_task_within = [(a + b) / 2 if a is not None and b is not None else (a if a is not None else b)
                       for a, b in zip(*r["mean_within_per_task"])]
    deltas = [w - x if w is not None and x is not None else None
              for w, x in zip(per_task_within, per_task_across)]
    thin = [i for i, d in enumerate(deltas) if d is not None and d < EACH_THIN]
    j4 = {"id": "T4", "measured": f"per task, within-run cosine {per_task_within} against across-run "
                                  f"{per_task_across}, drops {deltas}",
          "verdict": ("REFUSED -- a task's groups are missing" if any(d is None for d in deltas) else
                      "MET -- every task's update points differently across the worlds" if not thin else
                      f"FALSIFIER FIRED -- the drop is under {EACH_THIN:.2f} for task(s) {thin}")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if r.get("runs", 0) < 2 or "across" not in r:
        print(f"== the direction of the update ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the direction of the update ==")
    print(f"   {r['circuits'][0]}, read-out {r['readout'][0]}, tasks {r['task_names'][0]}, arm `{r['arm']}`, "
          f"{r['n_replicates'][0]} replicates each, subspace {r['dim']}-dimensional, fingerprints "
          f"{r['fingerprints'][0]}")
    print(f"   the two leaks: {r['leaks']}   `{r['arm']}` forgetting: "
          f"{ {k: round(v, 4) for k, v in r['forgetting'].items()} }")
    print(f"   unexpected config differences: {r['config_diff'] or 'none'}")
    print(f"   unexpected environment differences: {r['env_diff'] or 'none'}")
    print(f"\n   {'task':6} {'within inst':>12} {'within carry':>13} {'across':>9} {'drop':>8}")
    for j in range(r["n_tasks"]):
        wa = r["mean_within_per_task"][0][j]
        wb = r["mean_within_per_task"][1][j]
        x = r["mean_across"][j]
        drop = ((wa + wb) / 2 - x) if wa is not None and wb is not None and x is not None else None
        print(f"   {j:<6} {wa:12.4f} {wb:13.4f} {x:9.4f} {'n/a' if drop is None else f'{drop:8.4f}'}")
    print(f"   timing_s {r['timing_s']}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e334` and `e335` excluded the accounts a norm can speak to -- fit, contents and distance -- and")
    print("    `e335` ended on the direction, which no artifact recorded; this records it)")
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
