"""E373 -- the price of acting across the window: the whole grid is trained, and the price is zero at both ends.

`e363`'s frozen grid read six cells -- two drive sources at three cue steps -- and `e364`, `e365`, `e362`, `e367`,
`e371` and `e372` have since trained all six of them, at 20 replicates each, on the same suite, the same basis and
the same seed stream. **That makes the grid's own question answerable without a new run**, and the question is the
one `e372` left open: that unit paired the two sources at `cue@0`, where `e369`'s window is **widest**, and
registered a null between bars of 0.05 and 0.10 rather than a verdict, saying that nothing in it spoke to *"what
acting costs where the window is narrow"*.

**This unit reads the six trained runs and the frozen grid they were paired against.** The window is the margin
between the cue and the world's last readable state, so `cue@0` is the widest step, `cue@11` is the read step
itself, and `cue@10` is one step inside it -- the step where `e369`'s formula puts the action source's boundary and
where its world is provably **at rest**, which is why the frozen grid reads chance there and the cue source reads
0.8555.

Four claims, registered before any of the six readings was opened in this unit.

- **S1 -- and each step is one configuration with two drive sources.** For all three steps the cue-source and
  action-source runs agree on every shared field -- circuit, tasks and widths, basis, read-out, replicate count,
  seed stream, the world's dimension, leak, nonlinearity, mode and the cue's step -- with the drive's source and
  the seven fields that follow from it the only differences, and the couplings being `1b7d09f2b469` for the cue
  source and `5326f4a0edb4` for the action source. **Falsifier**: any shared field differing within a pair.
- **S2 -- and the price grows as the window narrows.** The paired cost of acting -- the cue-source diagonal minus
  the action-source one over the twenty shared seeds -- is larger at `cue@10` than at `cue@0` by at least **0.05**.
  **Falsifier**: within **0.02**, or reversed, which would say the price does not depend on the margin at all.
  **Null**: between.
- **S3 -- and at the read step there is no price to pay because there is no task to pay it for.** At `cue@11` both
  sources are within **0.05** of chance and the paired difference is within **0.05**. **Falsifier**: either source
  at least **0.05** above chance, which would refute `e364`'s finding that training cannot beat the interface at
  zero margin, or the difference being **0.10** or more. **Null**: between.
- **S4 -- and training shrinks the price where the task exists.** At both `cue@0` and `cue@10` the frozen price --
  the frozen grid's cue cell minus its action cell -- exceeds the trained cost by at least **0.03**. **Falsifier**:
  the trained cost reaching or exceeding the frozen price at either step, which would say twenty replicates of
  training buy nothing against a least-squares probe on a frozen body.

**What it can do beyond that.** The frozen prices are `e363`'s own numbers and the trained ones are six artifacts'
diagonals, so the reading is a **shape over the margin** rather than a number at one step: what the price of acting
is at the widest margin, one step inside the boundary, and at the boundary itself.

**What it cannot do.** *Three steps*: `cue@0` and `cue@10` and `cue@11` are the steps `e363` chose, so the curve has
three points and the region between 0 and 10 is not walked -- `e369`'s formula predicts the action source's boundary
at **8** to **9** depending on the draw, and a step between the training's three is a run this unit does not have.
*And the frozen prices are not paired*: `e363` rolled 512 examples once per cell, so its two cells per step are two
independent readings and their difference carries that grid's own resolution rather than the twenty replicates the
trained costs carry. *And the cost is a diagonal*: the retention matrices and the channel readings of all six runs
are in their artifacts, and this unit reads only the diagonal, so "the price of acting" is a statement about the
level a task reaches and not about what it costs to keep.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e367_the_world_the_agent_drives import FOLLOWS_FROM_THE_SOURCE, SHARED, _facts
from experiments.e371_the_game_the_agent_can_play import _sg, arm_reading, paired

#: the six trained runs: `e363`'s own grid, cell by cell, twenty replicates each
RUNS = {
    ("cue", 0): Path("runs/e372_earned_label_cue0_cuesource_20reps.json"),
    ("action", 0): Path("runs/e371_earned_label_cue0_actionsource_20reps.json"),
    ("cue", 10): Path("runs/e365_earned_label_cue10_cuesource_20reps.json"),
    ("action", 10): Path("runs/e367_earned_label_cue10_actionsource_20reps.json"),
    ("cue", 11): Path("runs/e364_earned_label_drivefromcue_20reps.json"),
    ("action", 11): Path("runs/e362_earned_label_latecue_20reps.json"),
}
FROZEN = Path("runs/e363_where_the_cue_can_reach_the_world.json")
SOURCES = ("cue", "action")
STEPS_USED = (0, 10, 11)
NAIVE = "naive"
REPLICATES = 20
CUE_COUPLING = "1b7d09f2b469"
ACTION_COUPLING = "5326f4a0edb4"
LEARNS = 0.10
FLAT = 0.05
GROWS = 0.05
SAME = 0.02
FIRES = 0.10
SHRINKS = 0.03
CLAIMS = (
    ("S1", "and each step is one configuration with two drive sources",
     "For all three steps the two runs agree on every shared field, the drive's source and the seven fields that "
     "follow from it the only differences, with couplings 1b7d09f2b469 and 5326f4a0edb4",
     "falsifier: any shared field differing within a pair"),
    ("S2", f"and the price grows as the window narrows, by {GROWS:.2f}",
     "The paired cost of acting is larger at cue@10 than at cue@0 by at least 0.05",
     f"falsifier: within {SAME:.2f}, or reversed; null: between {SAME:.2f} and {GROWS:.2f}"),
    ("S3", f"and at the read step there is no price because there is no task, within {FLAT:.2f}",
     "At cue@11 both sources are within 0.05 of chance and the paired difference is within 0.05",
     f"falsifier: either source 0.05 above chance, or the difference {FIRES:.2f} or more; null: between"),
    ("S4", f"and training shrinks the price where the task exists, by {SHRINKS:.2f}",
     "At both cue@0 and cue@10 the frozen price exceeds the trained cost by at least 0.03",
     "falsifier: the trained cost reaching or exceeding the frozen price at either step"),
)


def load(path) -> dict | None:
    import json
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def frozen_cells(path: Path = FROZEN) -> dict:
    doc = load(path)
    if not doc:
        return {}
    return {(c.get("source"), c.get("cue_at")): {"accuracy": float(c["accuracy"]), "chance": float(c["chance"]),
                                                 "world_sd": float(c["world_sd"])} for c in doc.get("cells") or []}


def reading(steps=STEPS_USED, frozen_path: Path = FROZEN) -> dict:
    frozen = frozen_cells(frozen_path)
    cells, pairs = {}, {}
    for step in steps:
        for source in SOURCES:
            run = load(RUNS[(source, step)])
            cells[f"{source}@{step}"] = {"run": RUNS[(source, step)].name if run else None,
                                         "present": run is not None,
                                         "arm": arm_reading(run, NAIVE),
                                         "facts": _facts(run)}
        cue, action = cells[f"cue@{step}"], cells[f"action@{step}"]
        if cue["present"] and action["present"]:
            pairs[step] = paired(cue["arm"]["diagonal"], action["arm"]["diagonal"])
    out = {"steps": [int(s) for s in steps], "cells": {k: {"run": v["run"], "present": v["present"],
                                                           "facts": v["facts"],
                                                           "diagonal": v["arm"].get("mean_diagonal"),
                                                           "forgetting": v["arm"].get("mean_forgetting"),
                                                           "channel": v["arm"].get("paired", {}).get("delta"),
                                                           "channel_sigma": v["arm"].get("paired", {}).get("sigma")}
                                                      for k, v in cells.items()},
           "facts": {k: v["facts"] for k, v in cells.items() if v["present"]}, "cost": pairs,
           "frozen": {f"{s}@{t}": v for (s, t), v in frozen.items()},
           "frozen_price": {t: (frozen[("cue", t)]["accuracy"] - frozen[("action", t)]["accuracy"])
                            if ("cue", t) in frozen and ("action", t) in frozen else None for t in steps},
           "replicates": REPLICATES, "expected_couplings": [CUE_COUPLING, ACTION_COUPLING]}
    return out


def checked_steps(facts: dict, steps) -> list:
    """The steps whose two runs are both on disk, which is what the configuration claim can speak about."""
    return [s for s in steps if facts.get(f"cue@{s}") and facts.get(f"action@{s}")]


def judge(r: dict) -> list[dict]:
    facts = r.get("facts") or {}
    #: an artifact on disk carries JSON's string keys where the in-memory reading carries the steps themselves,
    #: so both forms are normalized here rather than at every use
    cost = {int(k): v for k, v in (r.get("cost") or {}).items()}
    frozen_price = {int(k): v for k, v in (r.get("frozen_price") or {}).items()}
    steps = r.get("steps") or list(STEPS_USED)
    if not cost:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no step has both of its runs on disk"}
                for c in CLAIMS]

    broken, skipped = {}, []
    for step in steps:
        fc, fa = facts.get(f"cue@{step}"), facts.get(f"action@{step}")
        if not fc or not fa:
            #: a step with one run of its pair absent is not a configuration that differs; it is a step this claim
            #: cannot speak about, and it is named rather than counted against the pairs that can be checked
            skipped.append(step)
            continue
        sh = {k: [fc.get(k), fa.get(k)] for k in SHARED if fc.get(k) != fa.get(k)}
        moved = [k for k in FOLLOWS_FROM_THE_SOURCE if fc.get(k) != fa.get(k)]
        ok = (not sh and len(moved) == len(FOLLOWS_FROM_THE_SOURCE)
              and fc.get("world_coupling_sha1") == CUE_COUPLING and fa.get("world_coupling_sha1") == ACTION_COUPLING
              and fc.get("loop_cue_at") == step and fa.get("loop_cue_at") == step
              and fc.get("repeats") == REPLICATES)
        if not ok:
            broken[step] = {"shared": sh, "moved": sorted(moved),
                            "couplings": [fc.get("world_coupling_sha1"), fa.get("world_coupling_sha1")]}
    if not checked_steps(facts, steps):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no step has both of its runs on disk"}
                for c in CLAIMS]
    j1 = {"id": "S1", "measured": f"over the steps this unit can pair {[s for s in steps if s not in skipped]}"
                                  f"{f', with {skipped} unpaired and skipped' if skipped else ''}, the shared "
                                  f"fields differ {broken if broken else '{}'} and the drive's source moves all "
                                  f"{len(FOLLOWS_FROM_THE_SOURCE)} of its own fields in every pair",
          "verdict": "MET -- each step is one configuration with two drive sources" if not broken else
          f"FALSIFIER FIRED -- {broken}"}

    if 0 not in cost or 10 not in cost:
        j2 = {"id": "S2", "measured": "one of the two steps has no pair",
              "verdict": "REFUSED -- the two costs this claim compares are not both computable"}
    else:
        grow = cost[10]["delta"] - cost[0]["delta"]
        j2 = {"id": "S2", "measured": f"the cost is {cost[0]['delta']:+.4f} at cue@0 and {cost[10]['delta']:+.4f} "
                                      f"at cue@10, so it grows by {grow:+.4f} as the window narrows",
              "verdict": f"MET -- the price grows as the window narrows, by {grow:+.4f}" if grow >= GROWS else
              f"FALSIFIER FIRED -- the cost does not depend on the margin: {grow:+.4f}" if grow < SAME else
              f"NULL -- {grow:+.4f}, between {SAME:.2f} and {GROWS:.2f}"}

    if 11 not in cost:
        j3 = {"id": "S3", "measured": "the read step has no pair",
              "verdict": "REFUSED -- the read step's two runs are not both on disk"}
    else:
        above = {s: (r["cells"][f"{s}@11"]["diagonal"] - (r.get("frozen") or {}).get(f"{s}@11", {}).get("chance", 0.25))
                 for s in SOURCES if r["cells"].get(f"{s}@11", {}).get("present")}
        diff = cost[11]["delta"]
        bad = [s for s, a in above.items() if a >= FLAT]
        j3 = {"id": "S3", "measured": f"at the read step the sources read "
                                      f"{ {s: round(r['cells'][f'{s}@11']['diagonal'], 4) for s in above} } against a "
                                      f"chance of 0.25, and their paired difference is {diff:+.4f} on a sem of "
                                      f"{cost[11]['sem']:.4f}",
              "verdict": "MET -- no price and no task at the read step" if not bad and abs(diff) < FLAT else
              f"FALSIFIER FIRED -- {bad} clears chance at zero margin" if bad else
              f"FALSIFIER FIRED -- the two sources differ by {diff:+.4f} at the read step" if abs(diff) >= FIRES else
              f"NULL -- {diff:+.4f}, between {FLAT:.2f} and {FIRES:.2f}"}

    fp = frozen_price
    shrunk = {t: (fp.get(t) - cost[t]["delta"]) for t in (0, 10) if t in cost and fp.get(t) is not None}
    if not shrunk:
        j4 = {"id": "S4", "measured": "the frozen grid has no pair for the two steps",
              "verdict": "REFUSED -- the frozen prices are not on disk"}
    else:
        failing = sorted(t for t, v in shrunk.items() if v < 0.0)
        weak = sorted(t for t, v in shrunk.items() if 0.0 <= v < SHRINKS)
        j4 = {"id": "S4", "measured": f"the frozen price is { {t: round(fp[t], 4) for t in sorted(shrunk)} } and the "
                                      f"trained cost { {t: round(cost[t]['delta'], 4) for t in sorted(shrunk)} }, so "
                                      f"training removes { {t: round(v, 4) for t, v in sorted(shrunk.items())} }",
              "verdict": f"MET -- training shrinks the price at every step where the task exists, by "
                         f"{ {t: round(v, 4) for t, v in sorted(shrunk.items())} }" if not failing and not weak else
              f"FALSIFIER FIRED -- the trained cost reaches or exceeds the frozen price at {failing}" if failing else
              f"NULL -- {weak} shrink by less than {SHRINKS:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    if not r.get("cost"):
        print("== the price of acting across the window ==\n   REFUSED -- no step has both of its runs on disk")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the price of acting across the window ==")
    print(f"   `{FROZEN}`'s six cells, each trained by its own unit at {r['replicates']} replicates; the window is "
          f"the cue's margin, so cue@0 is widest and cue@11 is the read step")
    print(f"\n   {'cue at':>7} {'source':>7} {'run':>44} {'diagonal':>9} {'forget':>8} {'channel':>9} {'sigma':>6}")
    for step in r["steps"]:
        for source in SOURCES:
            cell = r["cells"][f"{source}@{step}"]
            print(f"   {step:>7} {source:>7} {str(cell['run']):>44} {cell['diagonal']:9.4f} "
                  f"{cell['forgetting']:8.4f} {cell['channel']:+9.4f} {_sg(cell['channel_sigma']):>6}")
    print(f"\n   {'cue at':>7} {'frozen price':>13} {'trained cost':>13} {'sem':>8} {'sigma':>7} {'shrunk by':>10}")
    cost = {int(k): v for k, v in (r.get("cost") or {}).items()}
    frozen_price = {int(k): v for k, v in (r.get("frozen_price") or {}).items()}
    for step in r["steps"]:
        c, f = cost.get(step), frozen_price.get(step)
        if c and f is not None:
            print(f"   {step:>7} {f:13.4f} {c['delta']:13.4f} {c['sem']:8.4f} {_sg(c['sigma']):>7} {f - c['delta']:10.4f}")

    print("\n== the registered claims, S1-S4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e372` paired the two sources where the window is widest and could not say what acting costs")
    print("    where it is narrow; `e363`'s grid has since been trained cell by cell, so the whole shape is here")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frozen", type=Path, default=FROZEN)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(frozen_path=args.frozen)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
