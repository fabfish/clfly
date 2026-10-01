"""E344 -- the latch hypothesis, tested by moving the cue to the step it is read.

`e343` closed the alternative explanations for the loop's 85% state divergence: a decoder fitted inside one loop and
read inside the other loses **one decision in ninety-six**, so the divergence lives in directions the task does not
use. The only explanation left standing is the **latch**: the loop is a self-exciting memory, its state keeps
whatever the task needs kept, and that is why the state moves and the answer does not.

**The latch makes a prediction that is cheap to test and has never been tested.** If the channel works by holding
the cue across the gap, then it should help exactly when something must be held. The world this repository builds is
already *a delayed report of a cue that is gone*: the label arrives at **step 0** and the read-out happens at the
**last step**. Move that label to the last step -- same world, same symbols, same noise, same populations, one
integer -- and the trial stops needing memory: the cue is on the drive at the instant the decoder reads it.

That is the whole experiment. Three runs at feedback strength 1.0, identical in every recorded field but `cue_at`
(0, 11 and 10), each with five replicates of the three closed-loop tasks; the paired channel reading (`e338`'s
instrument) is taken on all three, so each condition is *one trained body read twice* rather than two bodies
compared. The first two were launched and read first, and the third is the correction they asked for: a cue at the
read step itself is injected on neurons the read-out does not see until one further recurrent step, so the
`cue_at = 11` task came back at **chance** and its zero paired effect is a floor and not a latch test. T5 was
registered, with no reading of the `cue_at = 10` artifact, as soon as that was known. Four claims on the
0-against-11 contrast, plus the fifth on the corrected control.

- **T1 -- one configuration, differing only in `cue_at`.** Same circuit, read-out fingerprint, task names, replicate
  count, seeds, leak, world modes, populations and settings, with `cue_at` 0 in one run and 11 in the other.
  **Falsifier**: any other field differing.
- **T2 -- and for the memory task the channel helps, by 2 sigma.** In the `cue_at = 0` condition, where the cue is
  gone eleven steps before it is read, the with-loop accuracy exceeds the without-loop one by at least **2 sigma**
  and in the positive direction. **Falsifier**: the effect is at or below zero, or under 2 sigma, which says the
  latch is not load-bearing even here.
- **T3 -- and where nothing must be held it does not help, within 0.02.** In the `cue_at = 11` condition the paired
  difference is within **0.02** of zero. **Falsifier**: **0.05** or more, which would say the channel does something
  to the answer that has nothing to do with holding and T2's effect is not memory either. **Null**: between.
- **T4 -- and the two conditions differ, by 0.03.** The memory condition's paired difference exceeds the late-cue
  one's by at least **0.03**. **Falsifier**: **0.01** or less, which is the latch's death -- one channel strength,
  one body architecture, the same divergence in the state, and help that does not depend on whether memory is
  needed. **Null**: between.
- **T5 -- and the corrected control is learnable and still not helped, within 0.02.** The `cue_at = 10` task, where
  one recurrent step can carry the cue to the read-out neurons, is **above chance by 0.10** with the loop on, and its
  paired difference is within **0.02** of zero. **Falsifier**: the effect is **0.05** or more. **REFUSED**: the task
  is still at chance, which would say this control cannot carry the claim either and the honest statement is about
  the memory condition alone. **Null**: between.

**What it cannot do.** *The `cue_at = 11` condition measured a floor and not a task*: the cue is injected on
neurons the read-out does not see until one further recurrent step, so that run is at chance and its zero paired
effect says nothing about the latch -- which is exactly why `cue_at = 10` was added (T5) and why T3's verdict says
so in its own words. *`cue_at = 10` is one recurrent step of margin*: the cue reaches the read-out neurons through
one application of the connectome's weights, so whether the task is learnable at all is measured rather than
assumed, and a REFUSED T5 is the honest end of that branch. *The trial still has eleven recurrent steps in every
condition*, so the two conditions differ in how much *recurrence* is needed as well as how much *the channel*
helps -- which is why the claim is about the channel's paired effect and not about the tasks' difficulty. *One
integer, one world.* *Five replicates and three tasks*, so fifteen paired numbers that share a body and a head; the
sigma is the across-replicate spread of a per-replicate mean and not fifteen independent draws. *And moving the cue
changes the input's timing but not the read-out*: the decoder's probe still reads the last step of the same 32
neurons, so a difference between the conditions is a property of the loop and not of the read-out.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the three conditions, in the order every claim is stated over: the memory condition first, the late cue second,
#: and the corrected control third -- a cue the read-out's own neurons cannot see until one further recurrent step
CONDITIONS = (("memory", 0), ("none", 11), ("near", 10))
PATHS = {tag: RUNS / f"e344_cue_{tag}.json" for tag, _ in CONDITIONS}
ARM = "replay"
#: T2's bar, T3's window and its falsifier, T4's, and T5's margin over chance and its window
SIGMA = 2.0
FLAT = 0.02
MOVED = 0.05
DIFFERED = 0.03
SAME = 0.01
LEARNABLE = 0.10
CLAIMS = (
    ("T1", "one configuration, differing only in `cue_at`",
     "Same circuit, read-out fingerprint, task names, replicate count, seeds, leak, world modes, populations and "
     "settings, with `cue_at` 0, 11 and 10",
     "falsifier: any other field differing"),
    ("T2", f"and for the memory task the channel helps, by {SIGMA:.0f} sigma",
     f"In the `cue_at = 0` condition the paired difference is positive and at least {SIGMA:.0f} sigma",
     "falsifier: at or below zero, or under 2 sigma"),
    ("T3", f"and where nothing must be held it does not help, within {FLAT:.2f}",
     f"In the `cue_at = 11` condition the paired difference is within {FLAT:.2f} of zero",
     f"falsifier: {MOVED:.2f} or more"),
    ("T4", f"and the two conditions differ, by {DIFFERED:.2f}",
     f"The memory condition's paired difference exceeds the late-cue one's by at least {DIFFERED:.2f}",
     f"falsifier: {SAME:.2f} or less"),
    ("T5", f"and the corrected control is learnable and still not helped, within {FLAT:.2f}",
     f"The `cue_at = 10` task is above chance by {LEARNABLE:.2f} with the loop on, and its paired difference is "
     f"within {FLAT:.2f} of zero",
     f"falsifier: {MOVED:.2f} or more; refused if the task is at chance"),
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


def _sg(sigma) -> str:
    """Format a sigma that may be infinite: the writer turns a non-finite float into `null`, so a relicate that did
    not move reads back as None and a `:.2f` on it raises rather than printing."""
    return "inf" if sigma is None else f"{sigma:.2f}"


def condition_reading(run: dict | None, tag: str) -> dict:
    """One condition: the paired channel effect, replicate by replicate, plus the fields T1 compares."""
    if not run:
        return {"tag": tag, "ok": False}
    reps = replicates(run)
    if not reps:
        return {"tag": tag, "ok": False, "why": "no replicates"}
    rows = []
    for r in reps:
        entries = r.get("paired_channel")
        if not isinstance(entries, list) or not entries:
            return {"tag": tag, "ok": False, "why": "no paired record"}
        deltas = [e["with_loop"] - e["without_loop"] for e in entries]
        rows.append({"tasks": [e.get("task") for e in entries], "deltas": deltas,
                     "with_loop": [e["with_loop"] for e in entries],
                     "without_loop": [e["without_loop"] for e in entries],
                     "mean": statistics.fmean(deltas)})
    ca = run.get("config", {})
    ed = run.get("env_draw") or {}
    n_classes = (run.get("tasks") or [{}])[0].get("n_classes")
    return {
        "tag": tag, "ok": True,
        #: where the run's own environment draw says the cue landed. This is the field that is ALLOWED to differ;
        #: every claim's T1 is the statement that nothing else does.
        "cue_at": ed.get("cue_at"),
        "circuit": run.get("circuit"),
        "readout": run.get("readout", {}).get("subset_sha1"),
        "task_names": [t.get("name") for t in run.get("tasks", [])],
        "n": len(rows),
        "n_classes": n_classes,
        "chance": (1.0 / n_classes) if n_classes else None,
        "seed0": ca.get("seed0"),
        "readout_seed": ca.get("readout_seed"),
        "loop_seed": ca.get("loop_seed"),
        "leak": ed.get("world_leak"),
        "world_modes": ed.get("world_modes"),
        "populations": {k: ed.get(k) for k in ("cue_sha1", "action_sha1", "feedback_sha1")},
        "settings": {k: ca.get(k) for k in ("circuit_size", "repeats", "train", "test", "readout_size",
                                            "loop_noise", "loop_symbols", "loop_world_modes", "loop_scale")},
        "rows": rows,
        #: the loop-on accuracy, averaged over every task and replicate: this is what says whether a condition is
        #: learnable at all, which a paired difference of zero cannot say by itself
        "with_loop_mean": statistics.fmean([v for r in rows for v in r["with_loop"]]),
        #: the per-replicate mean, averaged over replicates: one number per condition, with its across-replicate sem
        "mean": paired([r["mean"] for r in rows], [0.0] * len(rows)),
    }


def reading(paths=None) -> dict:
    paths = paths or PATHS
    out = {"conditions": [condition_reading(load(paths[tag]), tag) if tag in paths else {"tag": tag, "ok": False}
                          for tag, _ in CONDITIONS],
           "cue_ats": [at for _, at in CONDITIONS], "arm": ARM}
    out["missing"] = [c["tag"] for c in out["conditions"] if not c.get("ok")]
    return out


def judge(r: dict) -> list[dict]:
    conds = r.get("conditions") or []
    good = [c for c in conds if c.get("ok")]
    if len(good) < len(CONDITIONS):
        return [{"id": c[0], "measured": f"present {[c['tag'] for c in good]}",
                 "verdict": "REFUSED -- the three conditions are not all on disk"} for c in CLAIMS]

    mem, non, near = good[0], good[1], good[2]
    fields = ("circuit", "readout", "task_names", "n", "seed0", "readout_seed", "loop_seed", "leak", "world_modes")
    agree = all(all(c[k] == mem[k] for k in fields) for c in good)
    settings_agree = all(c["settings"] == mem["settings"] for c in good)
    pops_agree = all(c["populations"] == mem["populations"] for c in good)
    cue_at = [c["cue_at"] for c in good]
    cue_differ = len(set(cue_at)) == len(CONDITIONS)
    j1 = {"id": "T1", "measured": f"circuit {mem['circuit']}, read-out {mem['readout']}, tasks {mem['task_names']}, "
                                  f"{mem['n']} replicates each, seeds "
                                  f"{[mem['seed0'], mem['readout_seed'], mem['loop_seed']]}, leak {mem['leak']}, "
                                  f"world modes {mem['world_modes']}, populations {mem['populations']}, settings "
                                  f"{mem['settings']}, cue_at {cue_at}",
          "verdict": "MET -- one configuration, differing only in `cue_at`" if
          agree and settings_agree and pops_agree and cue_differ else
          f"FALSIFIER FIRED -- fields agree {agree}, settings {settings_agree}, populations {pops_agree}, "
          f"cue_at differ {cue_differ}"}

    m = mem["mean"]
    helped = m["delta"] is not None and m["sem"] and m["delta"] > 0 and m["sigma"] >= SIGMA
    j2 = {"id": "T2", "measured": f"cue at {mem['cue_at']}: paired difference {m['delta']:+.4f} on a sem of "
                                  f"{m['sem']:.4f} ({_sg(m['sigma'])} sigma), per-replicate "
                                  f"{[round(row['mean'], 4) for row in mem['rows']]}",
          "verdict": "MET -- the channel helps when the cue must be held" if helped else
          f"FALSIFIER FIRED -- {m['delta']:+.4f} at {_sg(m['sigma'])} sigma" if m["delta"] is not None else
          "REFUSED -- the effect was not measured"}

    q = non["mean"]
    quiet = q["delta"] is not None and abs(q["delta"]) < FLAT
    j3 = {"id": "T3", "measured": f"cue at {non['cue_at']}: paired difference {q['delta']:+.4f} on a sem of "
                                  f"{q['sem']:.4f} ({_sg(q['sigma'])} sigma), with the loop on the task reads "
                                  f"{non['with_loop_mean']:.4f} against a chance of {non['chance']:.2f}",
          "verdict": f"MET -- the difference is {q['delta']:+.4f}, within {FLAT:.2f} of zero, "
                     f"and the task is at chance ({non['with_loop_mean']:.3f})" if quiet and
          non["chance"] is not None and non["with_loop_mean"] < non["chance"] + LEARNABLE else
          f"MET -- the difference is {q['delta']:+.4f}, within {FLAT:.2f} of zero" if quiet else
          f"FALSIFIER FIRED -- the channel moves the answer by {abs(q['delta']):.4f} with nothing to hold" if
          q["delta"] is not None and abs(q["delta"]) >= MOVED else
          f"NULL -- {q['delta']:+.4f}, between {FLAT:.2f} and {MOVED:.2f}" if q["delta"] is not None else
          "REFUSED -- the effect was not measured"}

    if m["delta"] is None or q["delta"] is None:
        j4 = {"id": "T4", "measured": "one of the two effects was not measured",
              "verdict": "REFUSED -- the difference is not computable"}
    else:
        gap = m["delta"] - q["delta"]
        j4 = {"id": "T4", "measured": f"the memory condition's {m['delta']:+.4f} less the late-cue condition's "
                                      f"{q['delta']:+.4f} is {gap:+.4f}, but the late-cue task is at "
                                      f"{non['with_loop_mean']:.3f} against a chance of {non['chance']:.2f}",
              "verdict": f"MET -- the two conditions differ by {gap:.4f}, and the help is memory" if gap >= DIFFERED
              else f"FALSIFIER FIRED -- they differ by {gap:.4f}, so the help does not depend on memory" if
              gap <= SAME else f"NULL -- {gap:+.4f}, between {SAME:.2f} and {DIFFERED:.2f}"}

    n_mean = near["mean"]
    learnable = (near["chance"] is not None
                 and near["with_loop_mean"] >= near["chance"] + LEARNABLE)
    if n_mean["delta"] is None:
        j5 = {"id": "T5", "measured": "the corrected control's effect was not measured",
              "verdict": "REFUSED -- the effect was not measured"}
    elif not learnable:
        j5 = {"id": "T5", "measured": f"cue at {near['cue_at']}: with the loop on the task reads "
                                      f"{near['with_loop_mean']:.4f} against a chance of {near['chance']:.2f}, "
                                      f"and the paired difference is {n_mean['delta']:+.4f}",
              "verdict": "REFUSED -- the corrected control is at chance and cannot carry the claim either, so the "
                         "honest statement is about the memory condition alone"}
    elif abs(n_mean["delta"]) < FLAT:
        j5 = {"id": "T5", "measured": f"cue at {near['cue_at']}: with the loop on the task reads "
                                      f"{near['with_loop_mean']:.4f} against a chance of {near['chance']:.2f}, and "
                                      f"the paired difference is {n_mean['delta']:+.4f} on a sem of "
                                      f"{n_mean['sem']:.4f} ({_sg(n_mean['sigma'])} sigma)",
              "verdict": f"MET -- learnable, and the channel does not help, within {FLAT:.2f}"}
    elif abs(n_mean["delta"]) >= MOVED:
        j5 = {"id": "T5", "measured": f"cue at {near['cue_at']}: paired difference {n_mean['delta']:+.4f}",
              "verdict": f"FALSIFIER FIRED -- the channel moves the answer by {abs(n_mean['delta']):.4f} with "
                         f"nothing to hold"}
    else:
        j5 = {"id": "T5", "measured": f"cue at {near['cue_at']}: paired difference {n_mean['delta']:+.4f}",
              "verdict": f"NULL -- {n_mean['delta']:+.4f}, between {FLAT:.2f} and {MOVED:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the latch hypothesis ==")
    for c in r.get("conditions", []):
        if not c.get("ok"):
            print(f"   {c['tag']}: REFUSED -- {'missing' if 'why' not in c else c['why']}")
            continue
        m = c["mean"]
        print(f"   cue at step {c['cue_at']:<2} ({c['tag']}): paired difference {m['delta']:+.4f} on a sem of "
              f"{m['sem']:.4f} ({_sg(m['sigma'])} sigma), loop-on accuracy {c['with_loop_mean']:.4f} against a "
              f"chance of {c['chance']:.2f}, per-task deltas "
              f"{[round(d, 4) for d in c['rows'][0]['deltas']]}")

    print("\n== the registered claims, T1-T5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the cue is a pulse at step 0 and the read-out is the last step; a cue at the read step cannot reach")
    print("    the read-out's own neurons until one further recurrent step, so the no-memory control is cue_at = 10)")
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
