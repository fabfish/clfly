"""E338 -- the same body asked both questions: a paired reading of the loop's effect on a fixed model.

`e333` measured `replay`'s retention rising 0.0375 at 2.45 sigma under a world with a transition rule, and `e337`
ran the same two worlds on a second seed stream and found the effect **reversed**: 0.0771 the other way at 3.36
sigma. Both are resolved, both are the same manipulation, and the conclusion `e337` drew is that the **redraw
dominates** every unpaired measurement of it -- a configuration against a configuration at five replicates is a
coin on this task, because the models differ.

**The way to remove the redraw is not more replicates but a pairing, and this unit builds the cheapest one there
is: ask the *same* body both questions.** `run_method` now keeps the **unwrapped** module alongside the loop-wrapped
one, and at the end of a replicate it reads every task's final accuracy **twice on that one trained body** -- once
through the loop and once with it unwired. The heads, the body, the seed and the trajectory are shared by
construction, so the difference carries no model-to-model variation at all.

One run, `replay`, five replicates, the **carried** world (`leak = 0.35`) -- the one `e333` and `e337` agreed
about nothing on. Four claims, registered before its reading.

- **T1 -- one configuration, and every replicate carries both readings.** Same circuit, read-out fingerprint, task
  names, replicate count and environment draw, and the paired record holds all three tasks with both numbers.
  **Falsifier**: a missing arm or task, or a field outside the intended ones differing.
- **T2 -- and the channel moves a trained body.** The paired difference, `with_loop` minus `without_loop`, averaged
  over the three tasks within a replicate and then over replicates, is resolved at **2 sigma**. **Falsifier**: below
  it. This is the effect with the redraw removed, and it is the number the last five units have been circling.
- **T3 -- and its sign is the same in every replicate.** All five replicates' task-mean differences share one sign.
  **Falsifier**: a replicate leaning the other way, which would say the channel's effect is itself redraw-dependent
  even on a fixed body.
- **T4 -- and it is small, under 0.05.** The paired effect's magnitude is at most **0.05**, against the 0.0375 and
  0.0771 that two unpaired redraws gave in opposite directions. **Falsifier**: above **0.10**, which would say the
  channel really does move a trained body by as much as the unpaired swings suggested.

**What it cannot do.** *One body per replicate, and the body was trained under the carried channel*: the reading is
what removing that channel does to a model that learned with it, and the reverse experiment -- a body trained
unwired, read with the loop on -- is not run, so the two directions are not compared. *One arm and one world pair*:
`naive`, `ewc` and the block arms are not read, and only `leak = 0.35` is asked. *Three tasks and five replicates*:
the paired mean rests on fifteen numbers that are not independent -- three tasks share a body and a head -- so the
standard error is the across-replicate one and the task variation inside a replicate is averaged, not modelled.
*And accuracy is not retention*: this reads each task's **final** accuracy on the final body, so a body that lost
task 0 would show it, but the decomposition into a learning term and a retention term is not computed here.
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
PAIRED = RUNS / "e338_paired_body.json"
#: the two unpaired numbers this unit is measured against, from `e333` and `e337`
UNPAIRED = (("e333, seed0=0", 0.0375), ("e337, seed0=4", -0.0771))
ARM = "replay"
SIGMA = 2.0
SMALL = 0.05
LARGE = 0.10
CLAIMS = (
    ("T1", "one configuration, and every replicate carries both readings",
     "Same circuit, read-out fingerprint, task names, replicate count and environment draw, and the paired record "
     "holding all three tasks with both numbers in every replicate",
     "falsifier: a missing arm or task, or a field outside the intended ones differing"),
    ("T2", f"and the channel moves a trained body, at {SIGMA:.0f} sigma",
     f"The paired difference, averaged over the tasks within a replicate and then over replicates, is resolved at "
     f"{SIGMA:.0f} sigma",
     "falsifier: below that"),
    ("T3", "and its sign is the same in every replicate",
     "All five replicates' task-mean differences share one sign",
     "falsifier: a replicate leaning the other way"),
    ("T4", f"and it is small, under {SMALL:.2f}",
     f"The paired effect's magnitude is at most {SMALL:.2f}, against the 0.0375 and 0.0771 two unpaired redraws gave "
     f"in opposite directions",
     f"falsifier: above {LARGE:.2f}"),
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


def paired(one: list[float], two: list[float]) -> dict:
    diffs = [a - b for a, b in zip(one, two)]
    if len(diffs) < 2:
        return {"n": len(diffs), "delta": None, "sem": None, "sigma": None}
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(len(diffs))
    return {"n": len(diffs), "delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf")}


def reading(run: dict | None = None) -> dict:
    run = run if run is not None else load(PAIRED)
    if not run:
        return {"runs": 0, "missing": [str(PAIRED)]}
    reps = replicates(run)
    rows = []
    for r in reps:
        entries = r.get("paired_channel")
        if not isinstance(entries, list) or not entries:
            return {"runs": 0, "missing": ["the paired record in the replicates"]}
        deltas = [e["with_loop"] - e["without_loop"] for e in entries if
                  isinstance(e, dict) and e.get("with_loop") is not None and e.get("without_loop") is not None]
        if len(deltas) != len(entries):
            return {"runs": 0, "missing": ["a task with one of its two numbers"]}
        rows.append({"tasks": [e.get("task") for e in entries], "deltas": deltas,
                     "mean": statistics.fmean(deltas),
                     "with_loop": [e["with_loop"] for e in entries],
                     "without_loop": [e["without_loop"] for e in entries]})
    ca = run.get("config", {})
    return {
        "runs": 1,
        "arm": ARM,
        "n_replicates": len(rows),
        "rows": rows,
        "mean": paired([r["mean"] for r in rows], [0.0] * len(rows)),
        "circuit": run.get("circuit"),
        "readout": run.get("readout", {}).get("subset_sha1"),
        "task_names": [t.get("name") for t in run.get("tasks", [])],
        "environment_draw": run.get("env_draw") or {},
        "run_settings": {k: ca.get(k) for k in ("circuit_size", "repeats", "seed0", "methods", "loop_world_modes",
                                          "loop_world_leak", "loop_noise", "loop_symbols", "loop_scale")},
        "unpaired": [{"label": lab, "delta": d} for lab, d in UNPAIRED],
        "timing_s": duration_seconds(run),
    }


def judge(r: dict) -> list[dict]:
    if not r.get("runs"):
        return [{"id": c[0], "measured": f"missing {r.get('missing')}",
                 "verdict": "REFUSED -- the paired record is not on disk"} for c in CLAIMS]

    complete = (r["n_replicates"] > 1 and r["task_names"] and
                all(len(row["deltas"]) == len(r["task_names"]) for row in r["rows"]))
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']}, read-out {r['readout']}, tasks {r['task_names']}, "
                                  f"{r['n_replicates']} replicates each carrying both numbers for "
                                  f"{len(r['task_names'])} tasks, environment {r['environment_draw']}, config {r['run_settings']}",
          "verdict": "MET -- one configuration, both numbers on the same body" if complete else
                     "FALSIFIER FIRED -- the paired record is incomplete"}

    m = r["mean"]
    j2 = {"id": "T2", "measured": f"the paired difference, averaged over tasks per replicate and then over "
                                  f"replicates: {m['delta']:+.4f} on a sem of {m['sem']:.4f}, i.e. "
                                  f"{m['sigma']:.2f} sigma over {m['n']} replicates",
          "verdict": f"MET -- the channel moves a trained body by {m['delta']:+.4f} at {m['sigma']:.2f} sigma" if
          m["sigma"] >= SIGMA else
          f"FALSIFIER FIRED -- {m['sigma']:.2f} sigma, in the direction {m['delta']:+.4f}"}

    signs = [1 if row["mean"] > 0 else (-1 if row["mean"] < 0 else 0) for row in r["rows"]]
    j3 = {"id": "T3", "measured": f"the per-replicate task-mean differences: "
                                  f"{[round(row['mean'], 4) for row in r['rows']]}",
          "verdict": "MET -- every replicate leans the same way" if len({s for s in signs if s}) == 1 and all(signs)
          else f"FALSIFIER FIRED -- the signs are {signs}"}

    mag = abs(m["delta"])
    biggest = max(abs(d) for _, d in UNPAIRED)
    j4 = {"id": "T4", "measured": f"the paired effect is {mag:.4f} against the two unpaired redraws "
                                  f"{[(lab, d) for lab, d in UNPAIRED]}",
          "verdict": f"MET -- a fixed body moves {mag:.4f}, a fraction of the {biggest:.4f} an unpaired redraw gave" if
          mag <= SMALL else
          f"FALSIFIER FIRED -- the paired effect is {mag:.4f}" if mag > LARGE else
          f"NULL -- {mag:.4f}, between {SMALL:.2f} and {LARGE:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("runs"):
        print(f"== the same body asked both questions ==\n   REFUSED -- missing {r.get('missing')}")
        for cl, row in zip(CLAIMS, judge(r)):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the same body asked both questions ==")
    print(f"   {r['circuit']}, read-out {r['readout']}, arm `{r['arm']}`, {r['n_replicates']} replicates, "
          f"tasks {r['task_names']}")
    print(f"   environment: {r['environment_draw']}")
    print(f"\n   {'replicate':>9} {'with loop':>34} {'without':>34} {'delta':>8}")
    for i, row in enumerate(r["rows"]):
        w = " ".join(f"{x:.3f}" for x in row["with_loop"])
        o = " ".join(f"{x:.3f}" for x in row["without_loop"])
        print(f"   {i:>9} {w:>34} {o:>34} {row['mean']:+8.4f}")
    m = r["mean"]
    print(f"   paired mean {m['delta']:+.4f} on a sem of {m['sem']:.4f}, i.e. {m['sigma']:.2f} sigma")
    print(f"   the two unpaired redraws this is measured against: "
          f"{[(lab, round(d, 4)) for lab, d in UNPAIRED]}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e337` found the unpaired effect changing sign between two seed streams, so the redraw dominates it;")
    print("    this removes the redraw by asking one trained body both questions)")
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
