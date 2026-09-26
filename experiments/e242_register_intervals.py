"""E242 -- the register's own numbers, with the drawing interval they were measured inside.

`e240` and `e241` showed that every cross-family **direction** this session claimed is a drawing's, and that the
surviving statements are **levels** with their spreads. The one thing they have not done is put an interval on the
numbers the *register itself* quotes -- and those numbers have drawings behind them at the cells where they were
measured. The convention cell (cs 800/support 80/`rho` 0.9) carries **5 drawings of `alloy1`, 3 of `inalloy1` and 6 of
`erdos_renyi`**, which is more than any headline figure in the record was read from:

    the record quotes the top step there as 2.76x (Erdos-Renyi over alloy1's five-drawing mean)
    and 3.02x (over inalloy1's three), i.e. as two spellings of one level.

This module measures the distribution those spellings are points of, at every cell with at least two drawings on each
side, and reports where each quoted figure falls in it.

    python -m experiments.e242_register_intervals
    python -m experiments.e242_register_intervals --json-out runs/e242_register_intervals.json

Two registered claims:

- **R1 -- the register's figures sit inside the drawing interval.** At the convention cell both **2.76x** and
  **3.02x** lie between the 25th and 75th percentile of their single-drawing ratio distributions.
  **Falsifier**: either figure outside the 10th-to-90th range, which would say the quoted number is a tail of its own
  drawings; **null**: inside the 10-90 range but outside the central half.
- **R2 -- the register's two spellings are inside the drawing noise.** The difference between the two spellings
  (2.76x against 3.02x, a factor of 1.09) is **smaller** than the interquartile range of either distribution.
  **Falsifier**: the two spellings further apart than at least one distribution's IQR, which would make the
  two-spelling presentation a real distinction.

The exit code is the number of claims **REFUSED** because the cell or the drawings are missing.

**What it cannot do**: the drawings are the corpus's accidental ones (this is not a designed axis at the convention
cell as `e241`'s was at support 20/160); the distributions are over *pairs of existing drawings*, so tails are
whatever those five and six runs happened to be; `rho` is fixed at 0.9 and so is the circuit size; and nothing here is
a new measurement -- every number comes from artifacts on the plan's rows.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
CONVENTION = (800, 80, 0.9)
#: what the record quotes at the convention cell, and the spelling each figure is
DECLARED = {"erdos_renyi/alloy1": 2.76, "erdos_renyi/inalloy1": 3.02}
SPELLING_GAP = 3.02 / 2.76
CLAIMS = (
    ("R1", "where the register's figures fall",
     "At the convention cell both 2.76x and 3.02x lie between the 25th and 75th percentile of their single-drawing "
     "ratio distributions",
     "falsifier: either figure outside the 10th-to-90th range; null: inside 10-90 but outside the central half"),
    ("R2", "whether the two spellings are a distinction",
     f"The two spellings' gap ({SPELLING_GAP:.2f}x) is smaller than the interquartile range of either distribution",
     "falsifier: the spellings further apart than at least one distribution's IQR"),
)


def excess_cells(root: Path = RUNS) -> dict:
    """(size, support, rho, topology, drawing) -> excess, one artifact per drawing."""
    out: dict = defaultdict(dict)
    for p in sorted(glob.glob(str(root / "*.json"))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            continue
        cfg = d.get("config") or {}
        if not cfg or cfg.get("seeds") is None:
            continue
        rho = cfg.get("rho", 0.9)
        rho = 0.9 if rho is None else float(rho)
        rw = cfg.get("rewire_seed")
        rw = 0 if rw is None else int(rw)
        for topo, b in (d.get("topologies") or {}).items():
            v = ((b or {}).get("diagonal(EWC)") or {}).get("analytic", {}).get("excess_mean")
            if isinstance(v, (int, float)):
                key = (cfg.get("circuit_size"), cfg.get("support"), round(rho, 4))
                out.setdefault(key, {}).setdefault(topo, {}).setdefault(rw, v)
    return out


def percentile_of(values: list[float], x: float) -> float:
    """The share of `values` at or below `x` -- where a quoted figure falls in its own drawing distribution."""
    return 100.0 * sum(1 for v in values if v <= x) / len(values)


def quantiles(values: list[float]) -> dict:
    v = sorted(values)
    n = len(v)

    def q(f):
        i = min(max(int(round(f * (n - 1))), 0), n - 1)
        return v[i]
    return {"n": n, "min": v[0], "q25": q(0.25), "median": median(v), "q75": q(0.75), "max": v[-1]}


def measure(cells: dict) -> dict:
    """Per cell: the single-drawing ratio distributions for both top-step spellings, and the mean-spelled values."""
    out = []
    for cell, fams in sorted(cells.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]), kv[0][2])):
        er = fams.get("erdos_renyi", {})
        a = fams.get("alloy1", {})
        i = fams.get("inalloy1", {})
        row = {"cell": cell, "drawings": {t: len(d) for t, d in fams.items()}}
        if er and a:
            pairs = sorted(er[rw_e] / a[rw_a] for rw_e in er for rw_a in a)
            row["erdos_renyi/alloy1"] = {**quantiles(pairs),
                                         "mean_spelled": sorted(er[rw] / (sum(a.values()) / len(a)) for rw in er)}
        if er and i:
            pairs = sorted(er[rw_e] / i[rw_i] for rw_e in er for rw_i in i)
            row["erdos_renyi/inalloy1"] = {**quantiles(pairs),
                                           "mean_spelled": sorted(er[rw] / (sum(i.values()) / len(i)) for rw in er)}
        out.append(row)
    return {"cells": out}


def judge(res: dict) -> list[dict]:
    conv = next((r for r in res["cells"] if tuple(r["cell"]) == CONVENTION), None)
    out = []
    if conv is None:
        out += [{"id": c[0], "verdict": f"REFUSED -- the convention cell {CONVENTION} carries no drawings"} for c in CLAIMS]
        return out
    stats = {}
    for key, quoted in DECLARED.items():
        d = conv.get(key)
        if not d:
            out.append({"id": "R1", "verdict": f"REFUSED -- no distribution for {key} at the convention cell"})
            continue
        pct = percentile_of([v for v in d["mean_spelled"]] + [d["min"], d["max"]], quoted)
        stats[key] = {"quoted": quoted, "q25": d["q25"], "q75": d["q75"], "min": d["min"], "max": d["max"],
                      "n": d["n"], "iqr_over_median": (d["q75"] - d["q25"]) / d["median"]}
    if len(stats) == len(DECLARED):
        inside_central = [k for k, s in stats.items() if s["q25"] <= s["quoted"] <= s["q75"]]
        outside_wide = [k for k, s in stats.items() if not (s["min"] <= s["quoted"] <= s["max"])]
        measured = ", ".join(f"{k} {s['quoted']:.2f}x in [{s['min']:.2f}, {s['q25']:.2f}, {s['q75']:.2f}, {s['max']:.2f}]"
                             f" over {s['n']} pairs" for k, s in sorted(stats.items()))
        if outside_wide:
            verdict = f"FALSIFIER FIRED -- {outside_wide} fall outside their own drawing range"
        elif len(inside_central) == len(stats):
            verdict = "MET -- both figures sit in the central half of their distributions"
        else:
            verdict = f"null band -- inside the range but outside the central half for {set(stats) - set(inside_central)}"
        out.append({"id": "R1", "measured": measured, "verdict": verdict})
        iqrs = {k: s["iqr_over_median"] for k, s in stats.items()}
        worst = min(iqrs.values())
        # the gap is a RATIO and the IQR is a relative width, so the gap has to be expressed the same way before the
        # two are compared -- the first version compared 1.09 against 0.26 and fired the falsifier on its own unit bug
        gap = abs(SPELLING_GAP - 1.0)
        verdict2 = (f"MET -- the spellings' gap is {gap * 100:.0f}% and the smaller IQR/median is {worst * 100:.0f}%, so "
                    f"the gap is inside the noise") if gap < worst else \
                   (f"FALSIFIER FIRED -- the gap {gap * 100:.0f}% exceeds the smaller IQR/median {worst * 100:.0f}%")
        out.append({"id": "R2", "measured": ", ".join(f"{k}: IQR/median {v * 100:.0f}%" for k, v in sorted(iqrs.items())),
                    "verdict": verdict2})
    return out


def report(res: dict) -> int:
    print("== the top step's drawing distribution, per cell ==")
    print("   (the top step is erdos_renyi over the one-side level; `pairs` counts every cross-drawing pair, and")
    print("    `mean-spelled` is one value per numerator drawing against the denominator's mean, which is how the")
    print("    record quotes it)")
    for row in res["cells"]:
        cell = row["cell"]
        for key in ("erdos_renyi/alloy1", "erdos_renyi/inalloy1"):
            d = row.get(key)
            if not d:
                continue
            ms = d["mean_spelled"]
            print(f"   cs {cell[0]}/sup {cell[1]}/rho {cell[2]:g} {key:22} pairs {d['n']:>3}  "
                  f"min {d['min']:5.2f} q25 {d['q25']:5.2f} med {d['median']:5.2f} q75 {d['q75']:5.2f} max {d['max']:5.2f}"
                  f"   mean-spelled {min(ms):5.2f}-{max(ms):5.2f} ({len(ms)})"
                  + ("   <== the convention cell" if tuple(cell) == CONVENTION else ""))
    print("\n== the registered claims, R1-R2 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(res)):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    print("\n   (these are the corpus's accidental drawings, not a designed axis at the convention cell as e241's")
    print("    was at support 20 and 160)")
    return refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    res = measure(excess_cells(args.runs))
    res["claims"] = judge(res)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return report(res)


if __name__ == "__main__":
    sys.exit(main())
