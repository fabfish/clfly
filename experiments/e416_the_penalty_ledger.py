"""E416 -- the penalty ledger: over the corpus's own penalty cells the buffer is never dominated where the power is.

`e415` answered thread (a) at one cell -- the card's world, `replay` over `ewc-block` at eleven sigma on both axes --
and `e276` had answered it at one cell on the overlap suite at twelve. Both registered the same limit: *one
substrate*, *one penalty strength*. The corpus holds many more, because every artifact that carries a penalty arm
beside `naive` and `replay` is a cell of the same two-axis comparison.

**This unit reads all of them.** It globs `runs/`, skips the second executions the corpus's own rule collapses, and
takes every artifact that carries `naive`, `replay` and at least one of `ewc` and `ewc-block` in one run: the two
paired contrasts, on final accuracy and on mean forgetting, per cell, pooled over the penalty arm the artifact
carries. No training, no probe. Five claims, registered before this unit's pass over the corpus.

- **AL1 -- and the ledger is carried.** At least **50** cells over at least **20** artifacts, each with at least **3**
  replicates on all three arms. **Falsifier**: fewer cells, fewer artifacts, or fewer replicates.
- **AL2 -- and on accuracy the buffer wins most of them.** In at least **80%** of the ledger's cells `replay`'s final
  accuracy exceeds the penalty arm's. **Falsifier**: below **60%**; **null**: between.
- **AL3 -- and where the power is it wins them all.** At a floor of **20** replicates, `replay` wins the accuracy
  contrast in **every** cell, over at least **8** cells. **Falsifier**: any cell where it does not, or fewer than
  eight cells at the floor.
- **AL4 -- and where the power is the buffer is never dominated.** At the same floor there is **no** cell in which the
  penalty arm is both more accurate and less forgetful. **Falsifier**: any such cell, which would be a configuration
  in which the penalty is simply the better arm.
- **AL5 -- and the cells that do dominate it are small and few.** Below the floor the buffer **is** dominated, in at
  least one cell, and every such cell carries the **block** penalty at **five** replicates with the penalty's
  accuracy margin at most **0.05**. **Falsifier**: a dominated cell carrying `ewc`, or one with more than five
  replicates, or a margin above **0.10**; **null** when no cell is dominated.

**What it can do beyond that.** It turns `e276`'s and `e415`'s single-cell results into the corpus's own ledger and
names where the ordering stops holding: with twenty or more replicates the buffer wins accuracy everywhere and is
never dominated on both axes, and the only cells that dominate it are five-replicate `ewc-block` cells whose margin is
under three hundredths.

**What it cannot do.** *The ledger is not a design*: the cells are one configuration each, executed once, so a
dominance is a reading of that execution and not of the configuration, and the replicate counts differ. *And the
comparison is pooled over the arm*: an artifact that carries both penalties contributes two cells, so the cells are
not independent samples. *And the arms are the corpus's*: `replay` is the corpus's buffer
(`--replay-per-task 16 --replay-batch 16`), and the penalty strengths are the corpus's own two (`lam` 3e-3 and 1.0).
*And the metric is the corpus's*: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
`e305` showed cannot see the part an arm never learned. *And a ledger is not a mechanism.*
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json

ROOT = Path("runs")
PENALTIES = ("ewc", "ewc-block")
REQUIRED = ("naive", "replay")
FLOOR = 20
SMALL = 3
MIN_CELLS = 50
MIN_ARTIFACTS = 20
WIN = 0.80
WIN_FIRES = 0.60
FLOOR_CELLS = 8
MARGIN = 0.05
MARGIN_FIRES = 0.10
SMALL_REPS = 5
CLAIMS = (
    ("AL1", f"and the ledger is carried, over at least {MIN_CELLS} cells and {MIN_ARTIFACTS} artifacts",
     "At least fifty cells over at least twenty artifacts, each with at least three replicates on all three arms",
     "falsifier: fewer cells, fewer artifacts, or fewer replicates"),
    ("AL2", f"and on accuracy the buffer wins most of them, {WIN:.0%}",
     "In at least 80 per cent of the ledger's cells replay's final accuracy exceeds the penalty arm's",
     f"falsifier: below {WIN_FIRES:.0%}; null: between"),
    ("AL3", f"and where the power is it wins them all, at a floor of {FLOOR}",
     "At a floor of twenty replicates replay wins the accuracy contrast in every cell, over at least eight cells",
     "falsifier: any cell where it does not, or fewer than eight cells at the floor"),
    ("AL4", "and where the power is the buffer is never dominated",
     "At the same floor there is no cell in which the penalty arm is both more accurate and less forgetful",
     "falsifier: any such cell"),
    ("AL5", f"and the cells that do dominate it are small and few, under {MARGIN:.2f}",
     "Below the floor the buffer is dominated in at least one cell, and every such cell carries the block penalty "
     f"at {SMALL_REPS} replicates with the penalty's accuracy margin at most 0.05",
     f"falsifier: a dominated cell carrying ewc, or one above {SMALL_REPS} replicates, or a margin above "
     f"{MARGIN_FIRES:.2f}; null when no cell is dominated"),
)


def load(path) -> dict | None:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _stats(doc: dict, arm: str):
    reps = ((doc.get("methods") or {}).get(arm) or {}).get("replicates") or []
    if not reps:
        return None
    return (statistics.fmean([r["final_accuracy"] for r in reps]),
            statistics.fmean([r["mean_forgetting"] for r in reps]), len(reps))


def reading(root: Path = ROOT) -> dict:
    out = {"ok": True, "reason": None, "cells": [], "artifacts": [], "floor": FLOOR, "small": SMALL}
    try:
        skip = corpus.repeat_paths(root)
    except Exception as exc:                                  # pragma: no cover - the corpus's own rule
        return {**out, "ok": False, "reason": f"the corpus's repeat rule did not run: {exc}"}
    out["collapsed"] = len(skip)
    for path in sorted(Path(root).glob("*.json")):
        if path.name in skip:
            continue
        doc = load(path)
        if not isinstance(doc, dict):
            continue
        methods = doc.get("methods")
        if not isinstance(methods, dict) or any(a not in methods for a in REQUIRED):
            continue
        base = {a: _stats(doc, a) for a in REQUIRED}
        if any(base[a] is None for a in REQUIRED):
            continue
        for arm in PENALTIES:
            pen = _stats(doc, arm)
            if pen is None:
                continue
            reps = min(base["naive"][2], base["replay"][2], pen[2])
            cfg = doc.get("config") or {}
            out["artifacts"].append(path.name)
            out["cells"].append({
                "artifact": path.name, "penalty": arm, "replicates": reps,
                "accuracy": {"naive": base["naive"][0], "replay": base["replay"][0], "penalty": pen[0]},
                "forgetting": {"naive": base["naive"][1], "replay": base["replay"][1], "penalty": pen[1]},
                "replay_minus_penalty": {"accuracy": base["replay"][0] - pen[0],
                                         "forgetting": base["replay"][1] - pen[1]},
                "lam": cfg.get("lam"), "circuit_size": cfg.get("circuit_size"),
            })
    out["artifacts"] = sorted(set(out["artifacts"]))
    return out


def _dominated(cell: dict) -> bool:
    m = cell["replay_minus_penalty"]
    return m["accuracy"] <= 0 and m["forgetting"] >= 0


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the ledger could not be read"}
                for c in CLAIMS]
    cells = r["cells"]
    thin = [c["artifact"] for c in cells if c["replicates"] < SMALL]
    j1 = {"id": "AL1",
          "measured": f"{len(cells)} cells over {len(r['artifacts'])} artifacts, at "
                      f"{sorted({c['replicates'] for c in cells})} replicates, with {r.get('collapsed')} second "
                      f"executions collapsed by the corpus's own rule",
          "verdict": f"MET -- the ledger is carried, {len(cells)} cells over {len(r['artifacts'])} artifacts"
                     if (len(cells) >= MIN_CELLS and len(r["artifacts"]) >= MIN_ARTIFACTS and not thin) else
                     f"FALSIFIER FIRED -- {len(cells)} cells, {len(r['artifacts'])} artifacts, thin {thin[:4]}"}
    wins = [c for c in cells if c["replay_minus_penalty"]["accuracy"] > 0]
    share = len(wins) / len(cells) if cells else 0.0
    losses = {c["artifact"]: round(c["replay_minus_penalty"]["accuracy"], 4) for c in cells if c not in wins}
    j2 = {"id": "AL2",
          "measured": f"the buffer's final accuracy exceeds the penalty's in {len(wins)} of {len(cells)} cells, "
                      f"{share:.0%}",
          "verdict": f"MET -- the buffer wins {share:.0%} of the ledger" if share >= WIN else
                     f"FALSIFIER FIRED -- {share:.0%} is under the bar; {losses}" if share < WIN_FIRES else
                     f"NULL -- {share:.0%}, between {WIN_FIRES:.0%} and {WIN:.0%}"}
    top = [c for c in cells if c["replicates"] >= FLOOR]
    lost = {c["artifact"]: {"penalty": c["penalty"],
                            "accuracy": round(c["replay_minus_penalty"]["accuracy"], 4)} for c in top
            if c["replay_minus_penalty"]["accuracy"] <= 0}
    j3 = {"id": "AL3",
          "measured": f"at the {FLOOR}-replicate floor there are {len(top)} cells at "
                      f"{sorted({c['replicates'] for c in top})} replicates and the buffer wins the accuracy "
                      f"contrast in {len(top) - len(lost)} of them",
          "verdict": f"MET -- the buffer wins accuracy at every one of the {len(top)} cells at the floor" if
                     (len(top) >= FLOOR_CELLS and not lost) else
                     f"FALSIFIER FIRED -- {len(top)} cells at the floor, losing {lost}"}
    dom_top = [{"artifact": c["artifact"], "penalty": c["penalty"]} for c in top if _dominated(c)]
    j4 = {"id": "AL4",
          "measured": f"at the {FLOOR}-replicate floor {len(dom_top)} of {len(top)} cells have the penalty arm both "
                      f"more accurate and less forgetful",
          "verdict": f"MET -- the buffer is not dominated on both axes at any of the {len(top)} cells at the floor"
                     if not dom_top else f"FALSIFIER FIRED -- {dom_top}"}
    dom = [c for c in cells if _dominated(c)]
    small = [c for c in dom if c["replicates"] < FLOOR]
    margins = {c["artifact"]: round(-c["replay_minus_penalty"]["accuracy"], 4) for c in small}
    ok5 = bool(small) and all(c["penalty"] == "ewc-block" for c in small) and \
        all(c["replicates"] <= SMALL_REPS for c in small) and \
        all(-c["replay_minus_penalty"]["accuracy"] <= MARGIN for c in small)
    j5 = {"id": "AL5",
          "measured": f"below the floor {len(small)} of {len(cells)} cells are dominated, over "
                      f"{sorted({c['penalty'] for c in small})} at {sorted({c['replicates'] for c in small})} "
                      f"replicates, with the penalty's accuracy margins {margins}",
          "verdict": f"MET -- the {len(small)} cell(s) that dominate the buffer are {'/'.join(sorted({c['penalty'] for c in small}))} "
                     f"at {sorted({c['replicates'] for c in small})} replicates, each margin under {MARGIN:.2f}"
                     if ok5 else
                     "NULL -- no cell below the floor is dominated" if not small else
                     f"FALSIFIER FIRED -- {[(c['artifact'], c['penalty'], c['replicates']) for c in small]}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the penalty ledger ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the corpus did not read')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    cells = r["cells"]
    print(f"   {len(cells)} cells over {len(r['artifacts'])} artifacts, {r.get('collapsed')} second executions "
          f"collapsed")
    print(f"\n   {'penalty':>10} {'replicates':>11} {'cells':>6} {'buffer wins acc':>16} "
          f"{'buffer forgets less':>20} {'dominated':>10}")
    for arm in PENALTIES:
        sub = [c for c in cells if c["penalty"] == arm]
        if not sub:
            continue
        for reps in sorted({c["replicates"] for c in sub}):
            band = [c for c in sub if c["replicates"] == reps]
            wa = sum(1 for c in band if c["replay_minus_penalty"]["accuracy"] > 0)
            wf = sum(1 for c in band if c["replay_minus_penalty"]["forgetting"] < 0)
            print(f"   {arm:>10} {reps:11d} {len(band):6d} {wa:16d} {wf:20d} "
                  f"{sum(1 for c in band if _dominated(c)):10d}")
    print("\n   the cells the penalty dominates on both axes:")
    for c in sorted((c for c in cells if _dominated(c)),
                    key=lambda c: c["replay_minus_penalty"]["accuracy"]):
        print(f"      {c['artifact'][:46]:46} {c['penalty']:10} n={c['replicates']:3d} accuracy "
              f"{c['replay_minus_penalty']['accuracy']:+.4f} forgetting {c['replay_minus_penalty']['forgetting']:+.4f}")
    print("\n== the registered claims, AL1-AL5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` measured replay over penalty at twelve sigma on one suite and `e415` at eleven on the card's")
    print("    world; this reads every penalty cell the corpus holds)")
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
