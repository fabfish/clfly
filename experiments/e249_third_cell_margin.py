"""E249 -- the (1, 0) margin at a third cell, and whether it interpolates the two already read.

The margin between the no-destruction constructions and the one-side ones -- median kind-1 spread over median kind-0
spread -- has been read five ways in the last four fires and runs from a tie to a doubling:

    cs 300/support 30   equal count 3 (`e248`)          1.008
    cs 300/support 30   `e245`'s unequal form           1.022
    cs 300/support 30   `e247`'s two-lowest-seed        0.94   (the other way)
    cs 800/support 80   all drawings                    2.044
    cs 800/support 80   two-lowest-seed                 1.107

`e247`'s R3 killed the two obvious cell-level explanations (the support share and the circuit size order nothing:
-0.074 and +0.033), and what is left is the one thing that differs between the two cells and is already measured for
every cell's families: **the cell's own rank contrast**. cs 300/support 30's kind-1 rank spreads are 2.73x and 2.08x
with a margin of 1.008; cs 800/support 80's are 14.08x and 8.02x with 2.044. **cs 800/support 20 sits between them**
(6.28x and 2.21x) and its kind-1 and kind-2 families carry **exactly two excess drawings each**, so two runs
(`e249`, `rewire_seed` 4 and 5) give a base that is **equal-count at two with no subsetting**.

    python -m experiments.e249_third_cell_margin
    python -m experiments.e249_third_cell_margin --json-out runs/e249_third_cell_margin.json

Three claims, all registered before the runs:

- **T1 -- the margin interpolates, which is the prediction.** At cs 800/support 20 with every family at two drawings,
  the margin is **above 1.10 and below 2.00**. **Falsifier**: below **1.05**, in which case the margin is not ordered
  by the rank contrast and cs 800/support 80's doubling is a cell idiosyncrasy, or above **2.50**, in which case it
  does not interpolate either. **Null**: 1.05 to 1.10, or 2.00 to 2.50.
- **T1b -- the same prediction on a consistent footing, added while the runs were in flight and before any of their
  data existed.** T1's bars are the *all-drawings* margins at the two reference cells (1.008 and 2.044) while the new
  cell is read at **two** drawings, which is a mismatch this module's own three-cell table exposed once it was written:
  on the consistent two-drawing footing the same two cells read **0.851** (cs 300/support 30) and **1.660**
  (cs 800/support 80). So the claim restated on one footing is that the new cell's margin lies **strictly inside
  (0.851, 1.660)**. **Falsifier**: outside that interval, in which case the margin is not monotone in the rank
  contrast over these three cells and the interpolation reading fails. The reference values are computed from data
  already on disk; the new cell's value is not, so this is still a blind prediction.
- **T2 -- the survivor travels.** `erdos_renyi` is the tightest of the families at this cell at two drawings, as it is
  at every cell, count and leave-one-out subset measured so far.
- **T3 -- reported, not claimed.** Each family's two excesses and spread, the cell's rank spreads beside them, and the
  margin computed on the equal-count base **and** on the corpus's larger drawings where they exist. The three cells are
  also compared on one footing: the **equal-count-two margin** at each of them, taken from each family's two lowest
  `rewire_seed` drawings.

The exit code is the number of claims **REFUSED** because the base is not equal-count.

**What it cannot do**: **prove** the rank contrast is the driver -- three cells is a trend and not a relation, and the
rank spreads and the excess spreads are read off the **same** drawings, so they are not independent variables; it is
one support at one size, so the rank contrast is confounded with whatever else cs 800/support 20 is; two drawings per
family is the corpus's noisiest count and `e247` measured that a two-drawing spread is unstable; the three kind-0
families share each run's single `rewire_seed`; `rho` is the builder's default (`config.rho: None`); and the comparison
is of spreads, not of levels.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import median

from clfly.bench.artifacts import write_json
from experiments.e244_drawing_spread_by_kind import kind_of
from experiments.e247_count_matched_spread import per_cell

CELL = (800, 20, 0.9)
COUNT = 2
KIND0 = ("swap0.5", "swap2", "signshuffle")
KIND1 = ("alloy1", "inalloy1")
FAMILIES = KIND0 + KIND1 + ("erdos_renyi",)
CELLS = ((300, 30, 0.9), CELL, (800, 80, 0.9))
CLAIMS = (
    ("T1", "the margin interpolates",
     "At cs 800/support 20 with every family at two drawings the (1, 0) margin is above 1.10 and below 2.00",
     "falsifier: below 1.05 (not ordered by the rank contrast) or above 2.50 (not interpolating either); null: "
     "1.05 to 1.10, or 2.00 to 2.50"),
    ("T1b", "the same prediction on a consistent footing",
     "The equal-count-two margin at cs 800/support 20 lies strictly inside the interval the same statistic spans at "
     "cs 300/support 30 and cs 800/support 80",
     "falsifier: outside that interval, which would make the margin not monotone in the rank contrast over three "
     "cells [registered while the runs were in flight, before any of their data existed; T1's bars came from the "
     "all-drawings form and this one from the two-drawing form, which is the mismatch its own three-cell table "
     "exposed]"),
    ("T2", "the survivor travels",
     "erdos_renyi is the tightest family at this cell at two drawings",
     "falsifier: a one-side or no-destruction family is as tight or tighter"),
)
LOW, HIGH, FALS_LOW, FALS_HIGH = 1.10, 2.00, 1.05, 2.50


def spread(vals) -> float | None:
    v = [x for x in vals if x and x > 0]
    return (max(v) / min(v)) if len(v) > 1 else None


def base(fam: dict, cell: tuple = CELL, count: int = COUNT) -> dict[str, dict]:
    """Each family's lowest-`count` drawings at the cell: equal counts by construction, else the base is short."""
    out = {}
    for f in FAMILIES:
        d = fam.get(f, {}).get(cell)
        if not d or len(d["excess"]) < count:
            continue
        out[f] = {"excess": d["excess"][:count], "rank": d["rank"][:count], "keys": d["keys"][:count]}
    return out


def margin(b: dict[str, dict]) -> float | None:
    """Median kind-1 spread over median kind-0 spread -- the quantity the last four fires have been reading."""
    s0 = [spread(b[f]["excess"]) for f in KIND0 if f in b]
    s1 = [spread(b[f]["excess"]) for f in KIND1 if f in b]
    s0 = [v for v in s0 if v]
    s1 = [v for v in s1 if v]
    if not s0 or not s1:
        return None
    return median(s1) / median(s0)


def rank_contrast(fam: dict, cell: tuple) -> dict[str, float | None]:
    """The kind-1 families' own rank spreads at a cell -- the candidate driver."""
    return {f: spread(fam.get(f, {}).get(cell, {}).get("rank", [])) for f in KIND1}


def judge(b: dict[str, dict], fam: dict) -> list[dict]:
    out: list[dict] = []
    short = sorted(set(FAMILIES) - set(b))
    if short:
        return [{"id": cid, "verdict": f"REFUSED -- the base is not equal-count (missing {short})"}
                for cid, *_ in CLAIMS]

    m = margin(b)
    contrasts = rank_contrast(fam, CELL)
    detail = ", ".join(f"{f} {spread(b[f]['excess']):.3f}x" for f in FAMILIES if f in b)
    if m is None:
        out.append({"id": "T1", "verdict": "REFUSED -- a kind is missing from the base"})
    else:
        if FALS_LOW < m < LOW or HIGH < m < FALS_HIGH:
            verdict = f"null band -- the margin {m:.3f} is between the bar and the falsifier"
        elif m <= FALS_LOW:
            verdict = "FALSIFIER FIRED -- the margin is a tie, so it is not ordered by the rank contrast"
        elif m >= FALS_HIGH:
            verdict = "FALSIFIER FIRED -- the margin is at least as large as cs 800/support 80's"
        else:
            verdict = "MET -- the margin interpolates the two cells already read"
        out.append({"id": "T1", "measured": f"margin {m:.3f} at cs 800/support 20 (kind-1 rank spreads "
                                           f"{', '.join(f'{v:.2f}x' for v in contrasts.values() if v)}); {detail}",
                    "verdict": verdict})

    spreads = {f: spread(b[f]["excess"]) for f in FAMILIES if f in b}
    er = spreads.get("erdos_renyi")
    others = [v for f, v in spreads.items() if f != "erdos_renyi" and v]
    if er is None or not others:
        out.append({"id": "T2", "verdict": "REFUSED -- kind 2 or the rest is missing"})
    else:
        out.append({"id": "T2", "measured": f"erdos_renyi {er:.3f}x against {min(others):.3f}x to {max(others):.3f}x",
                    "verdict": "MET -- the two-side family is the tightest" if er < min(others) else
                               "FALSIFIER FIRED -- another family is as tight or tighter"})

    refs = {cell: margin(base(fam, cell, COUNT)) for cell in CELLS}
    if m is None or any(v is None for c, v in refs.items() if c != CELL):
        out.append({"id": "T1b", "verdict": "REFUSED -- a reference cell has no equal-count-two margin"})
    else:
        lo, hi = sorted(v for c, v in refs.items() if c != CELL)
        inside = lo < m < hi
        out.append({"id": "T1b",
                    "measured": f"margin {m:.3f} against the same statistic's {lo:.3f} at cs 300/support 30 and "
                                f"{hi:.3f} at cs 800/support 80",
                    "verdict": "MET -- the margin sits inside the interval the rank contrast spans" if inside else
                               "FALSIFIER FIRED -- the margin is not monotone in the rank contrast"})
    return out


def matched_two_margins(fam: dict) -> list[tuple[tuple, float | None, dict[str, float | None]]]:
    """The three cells on one footing: each family's two lowest drawings, then the margin and the rank contrast."""
    out = []
    for cell in CELLS:
        b = base(fam, cell, COUNT)
        out.append((cell, margin(b) if len(b) == len(FAMILIES) else None, rank_contrast(fam, cell)))
    return out


def report(fam: dict) -> int:
    b = base(fam)
    print(f"== the third cell: cs {CELL[0]}/support {CELL[1]}/rho {CELL[2]:g}, {COUNT} drawings per family ==")
    if not b:
        print("   the base is empty -- the runs have not landed")
        return len(CLAIMS)
    print(f"   {'family':13} {'kind':>4} {'keys':>10} {'excesses':32} {'spread':>7} {'rank spread':>11}")
    for f in FAMILIES:
        d = b.get(f)
        if not d:
            print(f"   {f:13} MISSING")
            continue
        print(f"   {f:13} {kind_of(f):>4} {str(d['keys']):>10} {str([round(v, 5) for v in d['excess']]):32} "
              f"{(spread(d['excess']) or float('nan')):>7.3f} {(spread(d['rank']) or float('nan')):>11.2f}")
    m = margin(b)
    print(f"\n   the (1, 0) margin here: {m:.3f}" if m else "\n   the margin is not computable yet")

    print("\n== the three cells on one footing: each family's two lowest drawings ==")
    print(f"   {'cell':>22} {'margin':>7}   kind-1 rank spreads")
    for cell, mm, contrasts in matched_two_margins(fam):
        label = f"cs {cell[0]}/sup {cell[1]}"
        print(f"   {label:>22} {(mm if mm is not None else float('nan')):>7.3f}   "
              + ", ".join(f"{f} {v:.2f}x" for f, v in contrasts.items() if v))
    print("   (cs 800/support 80's is the cell whose all-drawings margin is 2.044; cs 300/support 30's equal-count-three")
    print("    margin is 1.008. If the margin follows the rank contrast, this cell sits between them.)")

    print("\n== the registered claims, T1-T2 ==")
    j = judge(b, fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (three cells is a trend and not a relation, and the rank and excess spreads are read off the SAME")
    print("    drawings -- so nothing here makes the rank contrast the driver, only ordered with it)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    fam = per_cell(args.runs)
    if args.json_out:
        b = base(fam)
        write_json(args.json_out, {"cell": list(CELL), "count": COUNT,
                                   "families": {f: {**d} for f, d in b.items()},
                                   "spreads": {f: spread(d["excess"]) for f, d in b.items()},
                                   "margin": margin(b),
                                   "matched_two": [[list(c), m, r] for c, m, r in matched_two_margins(fam)],
                                   "claims": judge(b, fam)})
        print(f"wrote {args.json_out}")
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
