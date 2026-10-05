"""E433 -- the penalties hold the weights and spend the drift on the bias.

`e431` found the penalties leaving the head's bias furthest from where the sequence started and the buffer nearest;
`e432` found the corpus's own interference account reading the penalised arms mostly through the bias. Both rest on one
parameter. Every arm's artifact carries the other one too -- the drift of the recurrent weights, per task -- so the two
can be read on the same cells: which parameter each arm spends its movement on.

**This unit reads both, cell by cell.** For every artifact carrying `naive` beside another arm with a drift and a final
distance from zero on both, the arm's drift over the baseline's and its bias over the baseline's, pooled by arm, with
the cell-by-cell joint pattern -- weights held and bias pushed. No training, no probe. Five claims, registered before
this unit's pass over the corpus.

- **BI1 -- and the ledger is carried.** At least **200** cells over at least **20** artifacts and at least **4** arms,
  of which at least **100** are the buffer's. **Falsifier**: fewer cells, artifacts, arms or buffer cells.
- **BI2 -- and every penalty holds the weights.** For each penalty arm the drift is below the baseline's in at least
  **60%** of its cells. **Falsifier**: any penalty arm below **45%**; **null**: between.
- **BI3 -- and by a wide margin.** Each penalty arm's mean drift ratio is below **0.8**. **Falsifier**: any arm above
  **0.9**; **null**: between. *BI2 and BI3 are the unit's own prediction: `e431` found the penalties displacing the
  bias furthest, and a penalty regularises toward a basis, so the movement it forbids on the weights should be the
  movement it leaves the bias to make.*
- **BI4 -- and the two parameters move opposite ways in a penalty's cells.** For each penalty arm, at least **60%** of
  its cells have the drift below the baseline's **and** the bias above it. **Falsifier**: any arm below **45%**.
- **BI5 -- and that is not the buffer's pattern.** The same joint share is below **20%** for the buffer. **Falsifier**:
  at or above **35%**; **null**: between.

**What it can do beyond that.** It names the parameter each arm spends its movement on. Pooled over the corpus's
plastic cells the penalty arms' drift ratios are **0.723**, **0.759** and **0.762** while their bias ratios are
**1.502**, **1.465** and **1.440**; the buffer's are **0.984** and **0.947**. So the two parameters order the arms
oppositely -- the penalties hold the weights and pay in the bias, the buffer moves both least -- and the joint pattern
(drift down and bias up) holds in **87.2%**, **80.8%** and **76.2%** of the three penalties' cells against **6.0%** of
the buffer's. That is the parameter signature of the channel `e432` found the corpus's interference account reading the
penalties through.

**What it cannot do.** *A ratio is not a mechanism*: where the parameters end is two readings of one trajectory and
this unit intervenes on neither. *And the cells are not independent*: the corpus's artifacts include several executions
of one configuration, so the shares are over the corpus as it stands. *And the drift is the corpus's own aggregate*:
the recorded `theta_drift` is per task and its definition is the runner's, so a ratio here is of that reading and not
of the displacement itself. *And the baseline is the same arm in each cell*: the ratios are per cell, so a cell whose
baseline is small contributes a large ratio. *And the distance is from the initialisation*: the corpus records the
distance from zero, which for a zero-initialised bias is the same thing and for any other is not.
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
DRIFT = "theta_drift"
BIAS = "bias_from_zero"
MIN_CELLS = 200
MIN_ARTIFACTS = 20
MIN_ARMS = 4
MIN_BUFFER = 100
HOLD_SHARE = 0.60
HOLD_FIRES = 0.45
HOLD_RATIO = 0.8
HOLD_RATIO_FIRES = 0.9
JOINT_SHARE = 0.60
JOINT_FIRES = 0.45
BUFFER_JOINT = 0.20
BUFFER_JOINT_FIRES = 0.35
CLAIMS = (
    ("BI1", f"and the ledger is carried, over at least {MIN_CELLS} cells and {MIN_ARTIFACTS} artifacts",
     "At least two hundred cells over at least twenty artifacts and at least four arms, of which at least a hundred are "
     "the buffer's",
     "falsifier: fewer cells, artifacts, arms or buffer cells"),
    ("BI2", f"and every penalty holds the weights, {HOLD_SHARE:.0%}",
     "For each penalty arm the drift is below the baseline's in at least 60 per cent of its cells",
     f"falsifier: any penalty arm below {HOLD_FIRES:.0%}; null: between"),
    ("BI3", f"and by a wide margin, a mean drift ratio below {HOLD_RATIO:.1f}",
     "Each penalty arm's mean drift ratio is below 0.8",
     f"falsifier: any arm above {HOLD_RATIO_FIRES:.1f}; null: between"),
    ("BI4", f"and the two parameters move opposite ways in a penalty's cells, {JOINT_SHARE:.0%}",
     "For each penalty arm, at least 60 per cent of its cells have the drift below the baseline's and the bias above it",
     f"falsifier: any arm below {JOINT_FIRES:.0%}"),
    ("BI5", f"and that is not the buffer's pattern, under {BUFFER_JOINT:.0%}",
     "The same joint share is below 20 per cent for the buffer",
     f"falsifier: at or above {BUFFER_JOINT_FIRES:.0%}; null: between"),
)


def load(path) -> dict | None:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _mean_drift(methods: dict, arm: str):
    reps = (methods.get(arm) or {}).get("replicates") or []
    if not reps or DRIFT not in reps[0]:
        return None
    return statistics.fmean([statistics.fmean(r[DRIFT]) for r in reps])


def reading(root: Path = ROOT) -> dict:
    out = {"ok": True, "reason": None, "cells": [], "by_arm": {}, "collapsed": None}
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
        base_drift, base_bias = _mean_drift(methods, BASELINE), (methods.get(BASELINE) or {}).get(BIAS)
        if not base_drift or base_drift <= 0 or not base_bias or base_bias[-1] <= 0:
            continue
        for arm in sorted(methods):
            if arm == BASELINE:
                continue
            got = methods.get(arm) or {}
            bias = got.get(BIAS)
            drift = _mean_drift(methods, arm)
            if drift is None or not bias or bias[-1] <= 0:
                continue
            cell = {"artifact": path.name, "arm": arm, "replicates": len(got.get("replicates") or []),
                    "drift_ratio": drift / base_drift, "bias_ratio": bias[-1] / base_bias[-1]}
            cell["held"] = cell["drift_ratio"] < 1.0
            cell["pushed"] = cell["bias_ratio"] > 1.0
            cell["both"] = cell["held"] and cell["pushed"]
            out["cells"].append(cell)
    for arm in sorted({c["arm"] for c in out["cells"]}):
        sub = [c for c in out["cells"] if c["arm"] == arm]
        out["by_arm"][arm] = {"cells": len(sub), "artifacts": len({c["artifact"] for c in sub}),
                              "held": sum(1 for c in sub if c["held"]),
                              "pushed": sum(1 for c in sub if c["pushed"]),
                              "both": sum(1 for c in sub if c["both"]),
                              "mean_drift_ratio": statistics.fmean([c["drift_ratio"] for c in sub]),
                              "mean_bias_ratio": statistics.fmean([c["bias_ratio"] for c in sub])}
        out["by_arm"][arm]["held_share"] = out["by_arm"][arm]["held"] / len(sub)
        out["by_arm"][arm]["both_share"] = out["by_arm"][arm]["both"] / len(sub)
    out["spans"] = {"cells": len(out["cells"]), "artifacts": len({c["artifact"] for c in out["cells"]}),
                    "arms": sorted(out["by_arm"]),
                    "buffer_cells": out["by_arm"].get(BUFFER, {}).get("cells", 0)}
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the corpus did not read"}
                for c in CLAIMS]
    s, by = r["spans"], r["by_arm"]
    j1 = {"id": "BI1",
          "measured": f"{s['cells']} cells over {s['artifacts']} artifacts and {len(s['arms'])} arms, "
                      f"{s['buffer_cells']} of them the buffer's, with {r.get('collapsed')} second executions "
                      f"collapsed",
          "verdict": f"MET -- the ledger is carried, {s['cells']} cells over {s['artifacts']} artifacts" if
                     (s["cells"] >= MIN_CELLS and s["artifacts"] >= MIN_ARTIFACTS and len(s["arms"]) >= MIN_ARMS
                      and s["buffer_cells"] >= MIN_BUFFER) else f"FALSIFIER FIRED -- {s}"}
    present = [a for a in PENALTIES if a in by]
    held = {a: round(by[a]["held_share"], 4) for a in present}
    weak = {a: v for a, v in held.items() if v < HOLD_SHARE}
    j2 = {"id": "BI2",
          "measured": f"the penalty arms' share of cells with the drift below the baseline's runs {held}, over "
                      f"{ {a: by[a]['cells'] for a in present} } cells",
          "verdict": f"MET -- every penalty arm holds the weights in at least {min(held.values()):.1%} of its cells" if
                     (present and not weak) else
                     f"FALSIFIER FIRED -- {weak}" if any(v < HOLD_FIRES for v in weak.values()) else
                     f"NULL -- {weak} between the bars"}
    ratios = {a: round(by[a]["mean_drift_ratio"], 3) for a in present}
    thick = {a: v for a, v in ratios.items() if v >= HOLD_RATIO}
    j3 = {"id": "BI3",
          "measured": f"the penalty arms' mean drift ratios are {ratios}",
          "verdict": f"MET -- every penalty arm holds the weights by a mean ratio below {HOLD_RATIO:.1f}" if
                     (present and not thick) else
                     f"FALSIFIER FIRED -- {thick}" if any(v > HOLD_RATIO_FIRES for v in thick.values()) else
                     f"NULL -- {thick} between the bars"}
    joint = {a: round(by[a]["both_share"], 4) for a in present}
    thin = {a: v for a, v in joint.items() if v < JOINT_SHARE}
    j4 = {"id": "BI4",
          "measured": f"the share of cells with the drift below the baseline's and the bias above it is {joint}, with "
                      f"the mean bias ratios { {a: round(by[a]['mean_bias_ratio'], 3) for a in present} }",
          "verdict": f"MET -- the two parameters move opposite ways in at least {min(joint.values()):.1%} of every "
                     f"penalty arm's cells" if (present and not thin) else
                     f"FALSIFIER FIRED -- {thin}"}
    buf = by.get(BUFFER, {})
    share = buf.get("both_share", 0.0)
    j5 = {"id": "BI5",
          "measured": f"the buffer's joint share is {buf.get('both', 0)} of {buf.get('cells', 0)} cells, {share:.1%}, "
                      f"against its drift ratio {buf.get('mean_drift_ratio', float('nan')):.3f} and its bias ratio "
                      f"{buf.get('mean_bias_ratio', float('nan')):.3f}",
          "verdict": f"MET -- the joint pattern is the penalties': {share:.1%} of the buffer's cells" if
                     share < BUFFER_JOINT else
                     f"FALSIFIER FIRED -- {share:.1%} is over the bar" if share >= BUFFER_JOINT_FIRES else
                     f"NULL -- {share:.1%}, between {BUFFER_JOINT:.0%} and {BUFFER_JOINT_FIRES:.0%}"}
    return [j1, j2, j3, j4, j5]


def report(r: dict) -> int:
    print("== the penalties hold the weights and spend the drift on the bias ==")
    if not r.get("ok"):
        print(f"   REFUSED -- {r.get('reason', 'the corpus did not read')}")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    print("   each arm's drift of the recurrent weights and its final distance of the bias from zero, both against")
    print("   its own run's naive arm")
    print(f"\n   {'arm':16} {'cells':>6} {'artifacts':>10} {'drift ratio':>12} {'held':>7} {'bias ratio':>11} "
          f"{'pushed':>7} {'both':>7}")
    for arm, got in sorted(r["by_arm"].items(), key=lambda kv: kv[1]["mean_drift_ratio"]):
        print(f"   {arm:16} {got['cells']:6d} {got['artifacts']:10d} {got['mean_drift_ratio']:12.3f} "
              f"{got['held_share']:7.1%} {got['mean_bias_ratio']:11.3f} "
              f"{got['pushed'] / got['cells']:7.1%} {got['both_share']:7.1%}")
    s = r["spans"]
    print(f"\n   {s['cells']} cells over {s['artifacts']} artifacts and {len(s['arms'])} arms, "
          f"{r.get('collapsed')} second executions collapsed")
    print("\n== the registered claims, BI1-BI5 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e431` read the bias side of these cells and `e432` the corpus's interference account; this reads the")
    print("    weights beside the bias, which is where the two parameters separate the arms)")
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
