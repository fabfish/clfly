"""E255 -- the census's own work list: a second drawing at cs 300/support 30 with `rho` 0.5, 0.7 and 0.8.

`e254` classified the record's twelve quoted figures by how many drawings their inputs have and found **two still
exposed, both through these three cells** -- cs 300/support 30 at `rho` 0.5, 0.7 and 0.8, one drawing per family:

    the rank curve falls monotonically in rho          (its low end rests on those three cells)
    the cs-300 rank contrasts resolve 7.68x to 25.25x  (withdrawn by e253 for rho >= 0.95; the low end unchecked)

Three runs of the ladder families (`e255`, `rewire_seed` 1 at each `rho`, ~5 min apiece) add a second drawing to each
and close the census's work list.

    python -m experiments.e255_low_rho_cells
    python -m experiments.e255_low_rho_cells --json-out runs/e255_low_rho_cells.json

The corpus's single drawings there, against a **ceiling** at the 30-neuron support:

| `rho` | `alloy1` rank | `inalloy1` rank | `erdos_renyi` rank |
|---|---|---|---|
| 0.5 | 26.52 | 25.82 | 26.75 |
| 0.7 | 22.96 | 22.86 | 25.23 |
| 0.8 | 17.54 | 19.77 | 23.08 |

At `rho` 0.5 a rank of 26.52 has little room above it, so the drawing noise there can only go down -- which is why R1
asks for a difference in either direction rather than a rise.

Four registered claims:

- **R1 -- the low-`rho` end has drawing noise too, or it does not.** At **at least one** of the three cells the new
  drawing's `alloy1` rank differs from the corpus's single-drawing value by a factor of **1.5 or more**, either way.
  **Falsifier**: all three within **+-10%**, so the low-`rho` levels are stable and the census's flag was a count
  rather than a risk; **null**: every cell between 1.1 and 1.5.
- **R2 -- the monotone fall survives one more drawing.** On the new drawings rank(0.5) > rank(0.8) > rank(0.9), the
  last being the three-drawing `rho`-0.9 cell's mean. **Falsifier**: a reversal.
- **R3 -- reported.** Both drawings' ranks and excesses at all three cells, the low end's decomposition, and the
  spreads the second drawing buys.
- **R4 -- reported.** `e254` re-run: whether the two exposed figures become DECOMPOSED.

The exit code is the number of claims **REFUSED** because a cell has no second drawing yet.

**What it cannot do**: two drawings per cell is one difference and not a distribution, and `e247` measured a
two-drawing spread to be the corpus's noisiest statistic; it does not touch the kind-0 families, which are not drawn at
those `rho` values at all, so the (1, 0) margin's low-`rho` behaviour stays unmeasured; `rho` cannot be separated from
the task geometry it sets; the ceiling at `rho` 0.5 makes the noise one-sided there, so a small factor at that cell is
not evidence of stability; and it closes only **one** of the corpus's two thin regions, since cs 800's `rho` 0.5, 0.7
and 0.8 cells also carry three families at one drawing each.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e254_quoted_figure_census as e254
from experiments.e247_count_matched_spread import per_cell

CELLS = ((300, 30, 0.5), (300, 30, 0.7), (300, 30, 0.8))
REF = (300, 30, 0.9)
FAMILIES = ("alloy1", "inalloy1", "erdos_renyi")
CLAIMS = (
    ("R1", "the low-rho end has drawing noise too, or it does not",
     "At at least one of the three cells the new drawing's alloy1 rank differs from the corpus's single-drawing value "
     "by a factor of 1.5 or more, either way",
     "falsifier: all three within +-10%, so the low-rho levels are stable and the census's flag was a count rather "
     "than a risk; null: every cell between 1.1 and 1.5"),
    ("R2", "the monotone fall survives one more drawing",
     "On the new drawings rank(0.5) > rank(0.8) > rank(0.9), the last being the three-drawing rho-0.9 cell's mean",
     "falsifier: a reversal"),
)
BAR = 1.5
STABLE = 1.10


def series(fam: dict, cell: tuple, f: str, field: str) -> list[float]:
    d = fam.get(f, {}).get(cell) or {}
    return d.get(field) or []


def factor(a: float, b: float) -> float:
    return max(a, b) / min(a, b) if a and b else float("nan")


def judge(fam: dict) -> list[dict]:
    out: list[dict] = []
    keys = {c: sorted(fam.get("alloy1", {}).get(c, {}).get("keys", [])) for c in CELLS}
    if any(len(keys[c]) < 2 or 1 not in keys[c] for c in CELLS):
        return [{"id": cid, "verdict": f"REFUSED -- a cell has no second drawing yet ({ {str(c): keys[c] for c in CELLS} })"}
                for cid, *_ in CLAIMS]

    rows = []
    for c in CELLS:
        rk = series(fam, c, "alloy1", "rank")
        rows.append((c, rk[0], rk[1], factor(rk[0], rk[1])))
    measured = "; ".join(f"rho {c[2]:g}: {q:.2f} against {n:.2f} (a factor of {s:.2f})" for c, q, n, s in rows)
    big = [c for c, _, _, s in rows if s >= BAR]
    if big:
        verdict = "MET -- the low-rho ranks move with the drawing by 1.5x or more"
    elif all(s <= STABLE for _, _, _, s in rows):
        verdict = "FALSIFIER FIRED -- all three agree within +-10%, so the low end is stable"
    else:
        verdict = "null band -- every cell between 1.1 and 1.5"
    out.append({"id": "R1", "measured": measured, "verdict": verdict})

    new = {c[2]: series(fam, c, "alloy1", "rank")[1] for c in CELLS}
    ref = series(fam, REF, "alloy1", "rank")
    ref_mean = sum(ref) / len(ref) if ref else None
    if ref_mean is None:
        out.append({"id": "R2", "verdict": "REFUSED -- the rho-0.9 cell has no alloy1 rank"})
    else:
        holds = new[0.5] > new[0.8] > ref_mean
        out.append({"id": "R2", "measured": f"on the new drawings: 0.5 {new[0.5]:.2f} > 0.8 {new[0.8]:.2f} > "
                                           f"0.9 {ref_mean:.2f} (the rho-0.9 mean of {len(ref)} drawings)",
                    "verdict": "MET -- the fall survives" if holds else "FALSIFIER FIRED -- the new drawings reverse it"})
    return out


def report(fam: dict) -> int:
    print("== the low-rho cells: rho 0.5, 0.7 and 0.8 at cs 300/support 30, one new drawing each ==")
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

    print("\n== the rank curve's low end, decomposed ==")
    ref = series(fam, REF, "alloy1", "rank")
    print(f"   rho 0.9 (reference, {len(ref)} drawings): alloy1 rank {['%.2f' % v for v in ref]}, mean "
          f"{sum(ref) / len(ref):.2f}")
    for c in CELLS:
        rk = series(fam, c, "alloy1", "rank")
        ex = series(fam, c, "alloy1", "excess")
        print(f"   rho {c[2]:<5} alloy1 rank {rk[0]:.2f} -> {rk[1]:.2f} (factor {factor(rk[0], rk[1]):.2f}); "
              f"excess {ex[0]:.5f} -> {ex[1]:.5f} (factor {factor(ex[0], ex[1]):.2f}); "
              f"spread now {max(ex) / min(ex):.3f}x")

    print("\n== R4: the census re-run ==")
    rows = e254.classify(fam)
    exposed = [r for r in rows if r["verdict"] == "STILL EXPOSED"]
    print(f"   {len(exposed)} of {len(rows)} registered figures still exposed"
          + (": " + ", ".join(r["name"] for r in exposed) if exposed else " -- the work list is closed"))

    print("\n== the registered claims, R1-R2 ==")
    j = judge(fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (two drawings is one difference and not a distribution; the kind-0 families are not drawn at these rho")
    print("    values at all, so the (1,0) margin's low-rho behaviour stays unmeasured)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    fam = per_cell(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": [list(c) for c in CELLS], "reference": list(REF),
                                   "series": {f"{c[2]:g}/{f}/{field}": series(fam, c, f, field)
                                              for c in CELLS for f in FAMILIES for field in ("rank", "excess")},
                                   "census_after": [{"name": r["name"], "verdict": r["verdict"]}
                                                    for r in e254.classify(fam)],
                                   "claims": judge(fam)})
        print(f"wrote {args.json_out}")
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
