"""E240 -- the cross-family contrasts re-tested on the corpus's OWN drawings, because three was never enough.

`e232`, `e236` and `e239` each dissolved a cross-family claim that had been measured on one drawing, and the last of
them named the pattern: **within a family the `rho` curve is the substrate's; across families a single-drawing
comparison is a draw.** That is a claim about this corpus and it is testable with the corpus itself -- the artifacts
already on disk hold several drawings of the same cell for the constructions that matter:

| cell (all `rho` 0.9) | `alloy1` | `inalloy1` | `erdos_renyi` |
|---|---|---|---|
| cs 300, support 30 | 3 | 3 | 3 |
| cs 400, support 40 | 3 | 3 | 3 |
| cs 400, support 80 | 2 | 2 | 2 |
| cs 800, support 20 | 2 | 2 | 2 |
| cs 800, support 160 | 2 | 2 | 2 |
| cs 800, support 80 | 5 | 3 | **1** |

A **drawing** is a distinct `rewire_seed`; two artifacts that share one are the same drawing measured twice (that is
how 12 `alloy1` artifacts at cs 800/support 80 are 5 drawings).

    python -m experiments.e240_cross_family_drawings
    python -m experiments.e240_cross_family_drawings --json-out runs/e240_cross_family_drawings.json

Three registered claims:

- **C1 — the rank contrast has no systematic direction.** At every cell with at least two drawings on both sides, the
  **median** pairwise `alloy1 ÷ inalloy1` *rank* ratio lies between 0.5 and 2. **Falsifier**: a median at or above
  4.14 (the bar `e231`'s P3 used) or at or below 0.25 at any cell, which would be a direction the drawings do not
  wash out.
- **C2 — the two-side advantage survives the drawings.** At the cells where `erdos_renyi` itself has at least two
  drawings, the **median** pairwise `erdos_renyi ÷ alloy1` *excess* ratio is above 3x (the bar `e233`'s E2 used).
  **Falsifier**: a median at or below 3x at any of them; **null**: above at some and below at others.
- **C3 — the drawings dominate the contrasts.** At every cell, the within-family spread of the excess across drawings
  (the larger of `alloy1`'s and `inalloy1`'s) is **larger** than the between-family difference of their means.
  **Falsifier**: the between-family difference larger at a majority of cells, which would say the contrasts are
  resolvable from one drawing after all.

The exit code is the number of claims **REFUSED** because a cell it needs is missing.

**What it cannot do**: it re-tests contrasts on cells the corpus happens to have drawings for, which is not the same as
a designed drawing axis; the drawings within a cell are not independent of when they were written (`e227`'s drift);
`erdos_renyi` has two or more drawings at only three cells; and nothing here is a new measurement -- every number comes
from artifacts already on the plan's rows.
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
ONE_SIDE = ("alloy1", "inalloy1")
C1_BAR_HIGH, C1_BAR_LOW = 4.14, 0.25
C2_BAR = 3.0
CLAIMS = (
    ("C1", "the rank contrast's direction across drawings",
     "At every cell with two or more drawings on both sides, the median pairwise alloy1/inalloy1 RANK ratio lies "
     "between 0.5 and 2",
     f"falsifier: a median at or above {C1_BAR_HIGH} or at or below {C1_BAR_LOW} at any cell"),
    ("C2", "the two-side advantage across drawings",
     f"At the cells where erdos_renyi has two or more drawings, the median pairwise erdos_renyi/alloy1 EXCESS ratio "
     f"is above {C2_BAR:g}x",
     f"falsifier: a median at or below {C2_BAR:g}x at any of them; null: above at some and below at others"),
    ("C3", "which spread is larger",
     "At every cell the within-family spread of the excess across drawings exceeds the between-family difference of "
     "the two one-side means",
     "falsifier: the between-family difference larger at a majority of cells"),
)


def cells(root: Path = RUNS) -> dict:
    """Per (size, support, rho, topology, drawing): the rank and the excess, one artifact per drawing."""
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
            if not isinstance(b, dict):
                continue
            rank = (b.get("geometry") or {}).get("effective_rank")
            excess = ((b.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
            if not isinstance(rank, (int, float)) and not isinstance(excess, (int, float)):
                continue
            key = (cfg.get("circuit_size"), cfg.get("support"), round(rho, 4), topo, rw)
            if key not in out:                       # one artifact per drawing, first in file order
                out[key] = {"rank": rank if isinstance(rank, (int, float)) else None,
                            "excess": excess if isinstance(excess, (int, float)) else None,
                            "artifact": Path(p).name}
    return out


def blocks(data: dict) -> list[dict]:
    """Every (size, support, rho) cell with its per-family drawing lists."""
    grouped: dict = defaultdict(lambda: defaultdict(dict))
    for (size, support, rho, topo, rw), v in data.items():
        grouped[(size, support, rho)][topo][rw] = v
    out = []
    for key, fams in sorted(grouped.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]), kv[0][2])):
        out.append({"cell": key, "families": {t: {rw: v for rw, v in sorted(f.items())}
                                              for t, f in sorted(fams.items())}})
    return out


def ratios(fams: dict, topo_a: str, field_a: str, topo_b: str, field_b: str) -> list[float]:
    """Every cross-drawing pair's ratio between two families -- the distribution a single-drawing claim is a draw of."""
    out = []
    for av in fams.get(topo_a, {}).values():
        for bv in fams.get(topo_b, {}).values():
            a, b = av.get(field_a), bv.get(field_b)
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b:
                out.append(a / b)
    return sorted(out)


def judge(blocks_: list[dict]) -> list[dict]:
    out = []
    rank_medians, excess_medians, spreads = {}, {}, {}
    for b in blocks_:
        fams = b["families"]
        if len(fams.get("alloy1", {})) >= 2 and len(fams.get("inalloy1", {})) >= 2:
            r = ratios(fams, "alloy1", "rank", "inalloy1", "rank")
            if r:
                rank_medians[b["cell"]] = median(r)
        if len(fams.get("erdos_renyi", {})) >= 2 and len(fams.get("alloy1", {})) >= 2:
            r = ratios(fams, "erdos_renyi", "excess", "alloy1", "excess")
            if r:
                excess_medians[b["cell"]] = median(r)
        a = [v["excess"] for v in fams.get("alloy1", {}).values() if isinstance(v["excess"], (int, float))]
        i = [v["excess"] for v in fams.get("inalloy1", {}).values() if isinstance(v["excess"], (int, float))]
        if a and i:
            within = max(max(a) / min(a), max(i) / min(i))
            between = abs(median(a) - median(i)) / max(min(median(a), median(i)), 1e-12)
            spreads[b["cell"]] = (within, between)
    if not rank_medians:
        out.append({"id": "C1", "verdict": "REFUSED -- no cell carries two or more rank drawings on both one-side "
                                           "families"})
    else:
        bad = [k for k, v in rank_medians.items() if v >= C1_BAR_HIGH or v <= C1_BAR_LOW]
        out.append({"id": "C1",
                    "measured": ", ".join(f"cs {k[0]}/sup {k[1]}: {v:.2f}x" for k, v in sorted(rank_medians.items(),
                                                                                             key=lambda kv: str(kv[0]))),
                    "verdict": f"FALSIFIER FIRED -- a systematic direction at {bad}" if bad else
                               f"MET -- every cell's median is between 0.5 and 2 over "
                               f"{len(rank_medians)} cell(s)"})
    if not excess_medians:
        out.append({"id": "C2", "verdict": f"REFUSED -- no cell carries two or more drawings of `erdos_renyi` "
                                           f"alongside two of `alloy1`"})
    else:
        below = [k for k, v in excess_medians.items() if v <= C2_BAR]
        out.append({"id": "C2",
                    "measured": ", ".join(f"cs {k[0]}/sup {k[1]}: {v:.2f}x" for k, v in sorted(excess_medians.items(),
                                                                                             key=lambda kv: str(kv[0]))),
                    "verdict": f"FALSIFIER FIRED -- at or below {C2_BAR:g}x at {below}" if below else
                               f"MET -- above {C2_BAR:g}x at all {len(excess_medians)} cell(s)"})
    if not spreads:
        out.append({"id": "C3", "verdict": "REFUSED -- no cell carries excess drawings for both one-side families"})
    else:
        loses = [k for k, (w, b) in spreads.items() if b >= w]
        out.append({"id": "C3",
                    "measured": f"{len(spreads) - len(loses)} of {len(spreads)} cells have the within-family spread "
                                f"larger" + (f" (not: {loses})" if loses else ""),
                    "verdict": "FALSIFIER FIRED -- the between-family difference is larger at a majority of cells"
                               if len(loses) * 2 > len(spreads) else
                               "MET -- the drawings dominate the between-family differences"})
    return sorted(out, key=lambda r: r["id"])


def report(blocks_: list[dict]) -> int:
    print("== the cells that hold drawings, and what they hold ==")
    print(f"   {'cell':>22} {'alloy1':>7} {'inalloy1':>9} {'erdos_renyi':>12}   median rank ratio   median ER/alloy1")
    for b in blocks_:
        fams = b["families"]
        n = {t: len(fams.get(t, {})) for t in ("alloy1", "inalloy1", "erdos_renyi")}
        r = ratios(fams, "alloy1", "rank", "inalloy1", "rank")
        e = ratios(fams, "erdos_renyi", "excess", "alloy1", "excess")
        cell = f"cs {b['cell'][0]}/sup {b['cell'][1]}/rho {b['cell'][2]:g}"
        print(f"   {cell:>22} {n['alloy1']:>7} {n['inalloy1']:>9} {n['erdos_renyi']:>12}   "
              + (f"{median(r):>17.2f}" if r else "                -")
              + (f"{median(e):>22.2f}" if e else "                     -"))
    print("\n   (a drawing is a distinct `rewire_seed`; two artifacts sharing one are one drawing measured twice)")
    print("\n== the registered claims, C1-C3 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(blocks_)):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    print("\n   (these are re-tests on the drawings the corpus happens to have, not a designed drawing axis)")
    return refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    blocks_ = blocks(cells(args.runs))
    if args.json_out:
        write_json(args.json_out, {"blocks": [{**b, "cell": list(b["cell"])} for b in blocks_],
                                   "claims": judge(blocks_)})
        print(f"wrote {args.json_out}")
    return report(blocks_)


if __name__ == "__main__":
    sys.exit(main())
