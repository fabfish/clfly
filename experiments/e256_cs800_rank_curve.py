"""E256 -- the cs-800 rank curve's second drawing: does the profile of the drawing noise in `rho` hold at the other size?

The censuses of the last three fires measured a **profile of the drawing noise in `rho`** at cs 300/support 30:

    rho 0.5 to 0.8   alloy1's rank moves 0.4% to 9.8% between two drawings   STABLE   (e255)
    rho 0.95, 0.98   the top step moves by factors of 1.54 and 4.47          EXPLODES (e253)
    rho 0.99         alloy1's excess spans 32.04x over three drawings        EXPLODES (e251)

and then, extending its registry, found that **the same rank curve at cs 800/support 80 is one-drawing at six of its
seven `rho` values** -- the counterpart claim, unchecked:

    cs 800/support 80 single-drawing alloy1 ranks: 63.14 (0.5), 45.83 (0.7), 32.78 (0.8), 22.09 (0.95), 21.24 (0.98), 21.01 (0.99)

Six runs (`e256`, the ladder families, `rewire_seed` 1 at each `rho`, ~4 min apiece) add a second drawing at each.

    python -m experiments.e256_cs800_rank_curve
    python -m experiments.e256_cs800_rank_curve --json-out runs/e256_cs800_rank_curve.json

Four registered claims:

- **F1 -- the low-`rho` end is stable at cs 800 too, which is what the profile predicts.** At each of `rho` 0.5, 0.7 and
  0.8 the new `alloy1` rank is within **±20%** of the corpus's single-drawing value. **Falsifier**: any of the three
  moves by **1.5x or more**, which would make `e255`'s low-`rho` stability a property of cs 300 rather than of the
  regime and put the profile in doubt; **null**: a factor between 1.2 and 1.5 at any of them.
- **F2 -- the high-`rho` end moves, the profile's other half.** At `rho` 0.95, 0.98 or 0.99 the new `alloy1` rank
  differs from the corpus's value by a factor of **1.5 or more**. **Falsifier**: all three within **±10%**, which would
  say the high-`rho` volatility is the excess side's alone and the geometry stays put; **null**: every high-`rho` cell
  between 1.1 and 1.5.
- **F3 -- the cs-800 fall survives one more drawing.** On the new drawings rank(0.5) > rank(0.8) > rank(0.99).
  **Falsifier**: a reversal.
- **F4 -- reported.** Both drawings' ranks and excesses at all six cells, the cs-300 profile beside the cs-800 one, and
  `e254` re-run: whether the two newly exposed figures become DECOMPOSED.

The exit code is the number of claims **REFUSED** because a cell has no second drawing yet.

**What it cannot do**: two drawings per cell is one difference and not a distribution, and `e247` measured a
two-drawing spread to be the corpus's noisiest statistic; it cannot separate `rho` from the task geometry it sets or
from the **size**, since the profile's two halves come from two different sizes; one run per `rho` leaves the kind-0
families with a single drawing, so no (1, 0) margin is computable there; it does not test the excess side's high-`rho`
behaviour, which `e251`/`e253` did at cs 300; and the corpus's own drawings at these cells are `rewire_seed` 0 while the
new ones are seed 1.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e254_quoted_figure_census as e254
from experiments.e247_count_matched_spread import per_cell

LOW = (0.5, 0.7, 0.8)
HIGH = (0.95, 0.98, 0.99)
CELLS = tuple((800, 80, r) for r in LOW + HIGH)
CS300 = tuple((300, 30, r) for r in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99))
FAMILIES = ("alloy1", "inalloy1", "erdos_renyi")
CLAIMS = (
    ("F1", "the low-rho end is stable at cs 800 too",
     "At each of rho 0.5, 0.7 and 0.8 the new alloy1 rank is within +-20% of the corpus's single-drawing value",
     "falsifier: any of the three moves by 1.5x or more, making the low-rho stability a property of cs 300 rather "
     "than of the regime; null: a factor between 1.2 and 1.5 at any of them"),
    ("F2", "the high-rho end moves, the profile's other half",
     "At rho 0.95, 0.98 or 0.99 the new alloy1 rank differs from the corpus's value by a factor of 1.5 or more",
     "falsifier: all three within +-10%, so the high-rho volatility is the excess side's alone; null: every high-rho "
     "cell between 1.1 and 1.5"),
    ("F3", "the cs-800 fall survives one more drawing",
     "On the new drawings rank(0.5) > rank(0.8) > rank(0.99)",
     "falsifier: a reversal"),
)
STABLE_BAR, FALS_LOW, TYPICAL_HIGH = 1.20, 1.50, 1.10


def series(fam: dict, cell: tuple, f: str, field: str) -> list[float]:
    d = fam.get(f, {}).get(cell) or {}
    return d.get(field) or []


def factor(a: float, b: float) -> float:
    return max(a, b) / min(a, b) if a and b else float("nan")


def judge(fam: dict) -> list[dict]:
    out: list[dict] = []
    keys = {c: sorted(fam.get("alloy1", {}).get(c, {}).get("keys", [])) for c in CELLS}
    missing = [c for c in CELLS if len(keys[c]) < 2 or 1 not in keys[c]]
    if missing:
        return [{"id": cid, "verdict": f"REFUSED -- {len(missing)} cell(s) have no second drawing yet "
                                       f"({[f'rho {c[2]:g}: {keys[c]}' for c in missing]})"}
                for cid, *_ in CLAIMS]

    rows = {c[2]: (series(fam, c, "alloy1", "rank")[0], series(fam, c, "alloy1", "rank")[1]) for c in CELLS}
    low = {r: factor(*rows[r]) for r in LOW}
    high = {r: factor(*rows[r]) for r in HIGH}

    measured = "; ".join(f"rho {r:g}: {rows[r][0]:.2f} against {rows[r][1]:.2f} ({low[r]:.2f})" for r in LOW)
    if all(v <= STABLE_BAR for v in low.values()):
        verdict = "MET -- the low-rho end is stable at cs 800 too"
    elif any(v >= FALS_LOW for v in low.values()):
        verdict = "FALSIFIER FIRED -- the low-rho end moves at cs 800, so the stability was cs 300's"
    else:
        verdict = "null band -- a factor between 1.2 and 1.5 at some low-rho cell"
    out.append({"id": "F1", "measured": measured, "verdict": verdict})

    measured = "; ".join(f"rho {r:g}: {rows[r][0]:.2f} against {rows[r][1]:.2f} ({high[r]:.2f})" for r in HIGH)
    if any(v >= FALS_LOW for v in high.values()):
        verdict = "MET -- the high-rho end moves at cs 800 as it does at cs 300"
    elif all(v <= TYPICAL_HIGH for v in high.values()):
        verdict = "FALSIFIER FIRED -- the high-rho rank stays put, so that volatility is the excess side's alone"
    else:
        verdict = "null band -- every high-rho cell between 1.1 and 1.5"
    out.append({"id": "F2", "measured": measured, "verdict": verdict})

    new = {r: rows[r][1] for r in LOW + HIGH}
    holds = new[0.5] > new[0.8] > new[0.99]
    out.append({"id": "F3",
                "measured": f"on the new drawings: 0.5 {new[0.5]:.2f} > 0.8 {new[0.8]:.2f} > 0.99 {new[0.99]:.2f}",
                "verdict": "MET -- the fall survives" if holds else "FALSIFIER FIRED -- the new drawings reverse it"})
    return out


def report(fam: dict) -> int:
    print("== the cs-800 rank curve's second drawing: six rho values at cs 800/support 80 ==")
    keys = {c: sorted(fam.get("alloy1", {}).get(c, {}).get("keys", [])) for c in CELLS}
    if any(len(keys[c]) < 2 for c in CELLS):
        print(f"   {[f'rho {c[2]:g}: keys {keys[c]}' for c in CELLS]}")
        print("   the new drawings have not landed")
        return len(CLAIMS)

    print(f"   {'rho':>5} {'drawing':>8} {'alloy1 rank':>12} {'inalloy1':>10} {'erdos':>8} "
          f"{'alloy1 excess':>14} {'erdos excess':>13}")
    for c in CELLS:
        for k in keys[c]:
            vals = {}
            for f in FAMILIES:
                d = fam[f][c]
                i = d["keys"].index(k)
                vals[f] = (d["rank"][i], d["excess"][i])
            print(f"   {c[2]:>5g} {k:>8} {vals['alloy1'][0]:>12.2f} {vals['inalloy1'][0]:>10.2f} "
                  f"{vals['erdos_renyi'][0]:>8.2f} {vals['alloy1'][1]:>14.5f} {vals['erdos_renyi'][1]:>13.5f}"
                  + ("   <- the corpus's own" if k == 0 else ""))

    print("\n== both sizes' profiles: alloy1's rank factor between two drawings, per rho ==")
    print(f"   {'rho':>5} {'cs 800 (new)':>14} {'cs 300 (e255/e253)':>20}")
    c300 = {}
    for cell in CS300:
        rk = series(fam, cell, "alloy1", "rank")
        c300[cell[2]] = factor(*rk[:2]) if len(rk) >= 2 else float("nan")
    for r in LOW + HIGH + (0.9,):
        cs8 = factor(*series(fam, (800, 80, r), "alloy1", "rank")[:2]) if len(series(fam, (800, 80, r), "alloy1", "rank")) >= 2 else float("nan")
        print(f"   {r:>5g} {cs8:>14.2f} {c300.get(r, float('nan')):>20.2f}")

    print("\n== F4: the census re-run ==")
    rows = e254.classify(fam)
    exposed = [r for r in rows if r["verdict"] == "STILL EXPOSED"]
    print(f"   {len(exposed)} of {len(rows)} registered figures still exposed"
          + (": " + ", ".join(r["name"] for r in exposed) if exposed else " -- the cs-800 exposure is closed"))

    print("\n== the registered claims, F1-F3 ==")
    j = judge(fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (two drawings is one difference and not a distribution; the low- and high-rho halves of the profile come")
    print("    from two different SIZES, so size and rho are confounded in the comparison)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    fam = per_cell(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": [list(c) for c in CELLS],
                                   "series": {f"{c[2]:g}/{f}/{field}": series(fam, c, f, field)
                                              for c in CELLS for f in FAMILIES for field in ("rank", "excess")},
                                   "census_after": [{"name": r["name"], "verdict": r["verdict"]}
                                                    for r in e254.classify(fam)],
                                   "claims": judge(fam)})
        print(f"wrote {args.json_out}")
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
