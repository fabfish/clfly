"""E431 -- the bias ledger: across the corpus the buffer leaves the bias nearer zero and every penalty leaves it further.

`e430` read the bias's own trajectory on two runs -- the card's world's three arms and the plastic/frozen-bias pair --
and found the buffer nearest zero, the penalty furthest, and the frozen side exactly flat. Every arm's artifact carries
the same field, so the question can be asked of the whole corpus: on the same seeds and the same baseline, does an arm
leave the head's bias nearer or further from where the sequence started than the arm that does nothing?

**This unit reads every paired cell.** For each artifact carrying `naive` and any other arm with a final distance from
zero on both, the second arm's distance over the baseline's: how often it is below, how often above, and the mean
ratio, pooled by arm, with the corpus's own frozen-bias cells set aside because there both sides read zero. No training,
no probe. Five claims, registered before this unit's pass over the corpus.

- **BG1 -- and the ledger is carried.** At least **200** paired cells over at least **20** artifacts and at least **4**
  arms, of which at least **100** are the buffer's. **Falsifier**: fewer cells, artifacts, arms or buffer cells.
- **BG2 -- and every penalty leaves the bias at or above the baseline's.** For each of `ewc`, `ewc-block` and
  `ewc-block-rand`, the arm's final distance is at or above the baseline's in at least **95%** of its cells.
  **Falsifier**: any penalty arm below **85%**. **Null**: between.
- **BG3 -- and by a wide margin.** Each penalty arm's mean ratio is above **1.4**. **Falsifier**: any arm below
  **1.2**; **null**: between. *BG2 and BG3 are the unit's own prediction: `e430` found a penalty pushing the bias out
  and `e427` found three quarters of the aid in the bias, so an arm that regularises toward a basis should leave the
  head further from its start than the arm that does nothing, corpus-wide and not on one cell.*
- **BG4 -- and the buffer leaves it nearer.** `replay`'s final distance is below the baseline's in at least **70%** of
  its cells. **Falsifier**: below **50%**; **null**: between.
- **BG5 -- and its mean ratio is below one.** `replay`'s mean ratio is below **1.0**. **Falsifier**: at or above
  **1.05**; **null**: between.

**What it can do beyond that.** It turns `e430`'s two cells into the corpus's own statement about where an arm leaves
the head. Across the corpus's plastic cells the baseline-relative ratio is **0.946** for the buffer, below one in **103
of 131** cells, and **1.456**, **1.473** and **1.508** for the block penalty's matched random control, the block penalty
and the diagonal penalty. The two basis arms are at or above the baseline in **every** one of their cells; the matched
control is at or above in **18 of 19**, which is the null BG2 reports -- so the displacement is a property of the two
basis partitions and one cell short of universal on the control that shares their group sizes.

**What it cannot do.** *A ratio is not a mechanism*: where the bias ends and what an arm forgets are two readings of one
trajectory, and this unit intervenes on neither, so the association is a co-movement. *And the cells are not
independent*: the corpus's artifacts include several executions of one configuration, so the percentages are over the
corpus as it stands rather than over independent samples. *And the baseline is the same arm in each cell*: the ratio is
per cell, so a cell whose baseline bias is small contributes a large ratio. *And the distance is from the
initialisation*: the corpus records the distance from zero, which for a zero-initialised bias is the same thing and for
any other is not.
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
BASELINE = "naive"
BUFFER = "replay"
PENALTIES = ("ewc", "ewc-block", "ewc-block-rand")
FIELD = "bias_from_zero"
MIN_CELLS = 200
MIN_ARTIFACTS = 20
MIN_ARMS = 4
MIN_BUFFER = 100
MIN_REPS = 1
PENALTY_SHARE = 0.95
PENALTY_FIRES = 0.85
RATIO = 1.4
RATIO_FIRES = 1.2
BUFFER_SHARE = 0.70
BUFFER_FIRES = 0.50
BUFFER_RATIO = 1.0
BUFFER_RATIO_FIRES = 1.05
CLAIMS = (
    ("BG1", f"and the ledger is carried, over at least {MIN_CELLS} cells and {MIN_ARTIFACTS} artifacts",
     "At least two hundred paired cells over at least twenty artifacts and at least four arms, of which at least a "
     "hundred are the buffer's",
     "falsifier: fewer cells, artifacts, arms or buffer cells"),
    ("BG2", f"and every penalty leaves the bias at or above the baseline's, {PENALTY_SHARE:.0%}",
     "For each penalty arm the final distance is at or above the baseline's in at least 95 per cent of its cells",
     f"falsifier: any penalty arm below {PENALTY_FIRES:.0%}; null: between"),
    ("BG3", f"and by a wide margin, a mean ratio above {RATIO:.1f}",
     "Each penalty arm's mean ratio is above 1.4",
     f"falsifier: any arm below {RATIO_FIRES:.1f}; null: between"),
    ("BG4", f"and the buffer leaves it nearer, {BUFFER_SHARE:.0%}",
     "replay's final distance is below the baseline's in at least 70 per cent of its cells",
     f"falsifier: below {BUFFER_FIRES:.0%}; null: between"),
    ("BG5", "and its mean ratio is below one",
     "replay's mean ratio is below 1.0",
     f"falsifier: at or above {BUFFER_RATIO_FIRES:.2f}; null: between"),
)


def load(path) -> dict | None:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def reading(root: Path = ROOT) -> dict:
    out = {"ok": True, "reason": None, "cells": [], "by_arm": {}, "frozen_cells": 0, "collapsed": None}
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
        if not isinstance(methods, dict) or BASELINE not in methods:
            continue
        base = (methods.get(BASELINE) or {}).get(FIELD)
        base_reps = (methods.get(BASELINE) or {}).get("replicates") or []
        if not base or not base_reps:
            continue
        frozen = bool((doc.get("config") or {}).get("frozen_bias"))
        for arm in sorted(methods):
            if arm == BASELINE:
                continue
            got = methods.get(arm) or {}
            value = got.get(FIELD)
            if not value or not got.get("replicates"):
                continue
            cell = {"artifact": path.name, "arm": arm, "replicates": len(got.get("replicates") or []),
                    "baseline": float(base[-1]), "value": float(value[-1]), "frozen_bias": frozen}
            if cell["baseline"] and cell["baseline"] > 0:
                cell["ratio"] = cell["value"] / cell["baseline"]
                cell["direction"] = "below" if cell["value"] < cell["baseline"] else (
                    "above" if cell["value"] > cell["baseline"] else "equal")
            else:
                cell["ratio"] = None
                cell["direction"] = "flat"
            out["cells"].append(cell)
            if frozen:
                out["frozen_cells"] += 1
    usable = [c for c in out["cells"] if c["ratio"] is not None and c["replicates"] >= MIN_REPS]
    for arm in sorted({c["arm"] for c in usable}):
        sub = [c for c in usable if c["arm"] == arm]
        out["by_arm"][arm] = {"cells": len(sub),
                              "below": sum(1 for c in sub if c["direction"] == "below"),
                              "above": sum(1 for c in sub if c["direction"] == "above"),
                              "equal": sum(1 for c in sub if c["direction"] == "equal"),
                              "mean_ratio": statistics.fmean([c["ratio"] for c in sub]),
                              "artifacts": len({c["artifact"] for c in sub}),
                              "replicates": sorted({c["replicates"] for c in sub})}
        out["by_arm"][arm]["at_or_above"] = out["by_arm"][arm]["above"] + out["by_arm"][arm]["equal"]
        out["by_arm"][arm]["at_or_above_share"] = (out["by_arm"][arm]["at_or_above"] / len(sub))
        out["by_arm"][arm]["below_share"] = out["by_arm"][arm]["below"] / len(sub)
    out["spans"] = {"cells": len(usable), "artifacts": len({c["artifact"] for c in usable}),
                    "arms": sorted(out["by_arm"]), "frozen_cells": out["frozen_cells"],
                    "buffer_cells": out["by_arm"].get(BUFFER, {}).get("cells", 0)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus did not read"}
                for c in CLAIMS]
    s, by = r["spans"], r["by_arm"]
    j1 = {"id": "BG1",
          "measured": f"{s['cells']} paired cells over {s['artifacts']} artifacts and {len(s['arms'])} arms, "
                      f"{s['buffer_cells']} of them the buffer's, with {s['frozen_cells']} frozen-bias cells set aside "
                      f"and {r.get('collapsed')} second executions collapsed",
          "verdict": f"MET -- the ledger is carried, {s['cells']} cells over {s['artifacts']} artifacts" if
                     (s["cells"] >= MIN_CELLS and s["artifacts"] >= MIN_ARTIFACTS and len(s["arms"]) >= MIN_ARMS
                      and s["buffer_cells"] >= MIN_BUFFER) else
                     f"FALSIFIER FIRED -- {s}"}
    present = [a for a in PENALTIES if a in by]
    shares = {a: round(by[a]["at_or_above_share"], 4) for a in present}
    weak = {a: v for a, v in shares.items() if v < PENALTY_SHARE}
    j2 = {"id": "BG2",
          "measured": f"the penalty arms' share of cells at or above the baseline runs {shares}, over "
                      f"{ {a: by[a]['cells'] for a in present} } cells",
          "verdict": f"MET -- every penalty arm is at or above the baseline in at least {min(shares.values()):.1%} of "
                     f"its cells" if (present and not weak) else
                     f"FALSIFIER FIRED -- {weak}" if any(v < PENALTY_FIRES for v in weak.values()) else
                     f"NULL -- {weak} between the bars"}
    ratios = {a: round(by[a]["mean_ratio"], 3) for a in present}
    thin = {a: v for a, v in ratios.items() if v < RATIO}
    j3 = {"id": "BG3",
          "measured": f"the penalty arms' mean ratios are {ratios}",
          "verdict": f"MET -- every penalty arm displaces the bias by a mean ratio above {RATIO:.1f}" if
                     (present and not thin) else
                     f"FALSIFIER FIRED -- {thin}" if any(v < RATIO_FIRES for v in thin.values()) else
                     f"NULL -- {thin} between the bars"}
    buf = by.get(BUFFER, {})
    share = buf.get("below_share", 0.0)
    j4 = {"id": "BG4",
          "measured": f"the buffer is below the baseline in {buf.get('below', 0)} of {buf.get('cells', 0)} cells, "
                      f"{share:.1%}",
          "verdict": f"MET -- the buffer leaves the bias nearer in {share:.1%} of its cells" if share >= BUFFER_SHARE
                     else f"FALSIFIER FIRED -- {share:.1%} is under the bar" if share < BUFFER_FIRES else
                     f"NULL -- {share:.1%}, between {BUFFER_FIRES:.0%} and {BUFFER_SHARE:.0%}"}
    bratio = buf.get("mean_ratio")
    j5 = {"id": "BG5",
          "measured": f"the buffer's mean ratio is {bratio:.3f}" if bratio is not None
                      else "the buffer has no cells in the ledger",
          "verdict": f"MET -- the buffer's mean ratio is {bratio:.3f}, below one" if
                     (bratio is not None and bratio < BUFFER_RATIO) else
                     f"FALSIFIER FIRED -- {bratio} is not below one" if
                     (bratio is None or bratio >= BUFFER_RATIO_FIRES) else
                     f"NULL -- {bratio:.3f}, between {BUFFER_RATIO:.2f} and {BUFFER_RATIO_FIRES:.2f}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the bias ledger ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the corpus did not read')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   every artifact's arms against its own naive arm's final distance of the bias from zero")
    print(f"\n   {'arm':16} {'cells':>6} {'below':>6} {'above':>6} {'equal':>6} {'mean ratio':>11} {'artifacts':>10} "
          f"{'replicates':>12}")
    for arm, got in sorted(r["by_arm"].items(), key=lambda kv: kv[1]["mean_ratio"]):
        print(f"   {arm:16} {got['cells']:6d} {got['below']:6d} {got['above']:6d} {got['equal']:6d} "
              f"{got['mean_ratio']:11.3f} {got['artifacts']:10d} {str(got['replicates']):>12}")
    s = r["spans"]
    print(f"\n   {s['cells']} paired cells over {s['artifacts']} artifacts and {len(s['arms'])} arms, "
          f"{s['frozen_cells']} frozen-bias cells set aside, {r.get('collapsed')} second executions collapsed")
    print("\n== the registered claims, BG1-BG5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e430` read the bias on two runs; this asks the same of every paired cell the corpus holds)")
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
