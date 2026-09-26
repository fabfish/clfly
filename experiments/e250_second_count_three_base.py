"""E250 -- the second equal-count-three base, at the corpus's flattest kind-1 geometry.

`e248` built an equal-count-three base at cs 300/support 30 (six families, three drawings each) and read its (1, 0)
margin as 1.008 -- a tie. `e249` put the same quantity at two more cells and found it rises with the cell's kind-1
**rank contrast** (0.851, 0.935, 1.660 against 2.4x, 3.4x, 11x) while noting the margin moves 1.95x where the contrast
moves 5.16x. The relation had no point at the bottom of its range.

**cs 400/support 40 is that point and is on the same footing**: its kind-1 and kind-2 families carry **exactly three
excess drawings each** (`rewire_seed` 0, 1, 2) and it has **no kind-0 family at all**, so three runs (`e250`, seeds 3,
4, 5) give a base that is **equal-count-three like `e248`'s**, and its kind-1 rank spreads are **1.53x and 1.59x** --
the smallest in the corpus against cs 300/support 30's 2.73x and 2.08x.

    python -m experiments.e250_second_count_three_base
    python -m experiments.e250_second_count_three_base --json-out runs/e250_second_count_three_base.json

Four registered claims:

- **U1 -- the prediction.** At cs 400/support 40 with three drawings per family the (1, 0) margin is **below** the
  1.008 the same statistic takes at cs 300/support 30 on the same footing, and specifically **below 1**. **Falsifier**:
  at or above **1.10**, a reversal at the flattest kind-1 geometry in the corpus, which would break the relation rather
  than extend it; **null**: between the cs-300 value and 1.10.
- **U2 -- the survivor.** `erdos_renyi` is the tightest family at this cell at three drawings.
- **U3 -- reported.** The three kinds' levels, so the confound sits beside the result.
- **U4 -- reported.** The two count-three bases side by side: margins, kind-1 rank contrasts, and every family's three
  drawings.

The exit code is the number of claims **REFUSED** because a base is not equal-count.

**What it cannot do**: turn a three-point trend into a relation -- four points with a **simulated** driver read off
**the same drawings** as the quantity it would explain, so the correlation is not a mechanism; fix the level confound
(kind 0 near the floor against kind 1 at 0.12 to 0.14 here); speak for any cell whose kind-0 rung is unmeasured; avoid
the corpus's noisiest regime, since each base is a single cell at one `rho`; or make the base equally **drawn**, its
kind-1 and kind-2 drawings coming from `e217`/`e219` and its kind-0 drawings from these runs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import median

from clfly.bench.artifacts import write_json
from experiments.e244_drawing_spread_by_kind import kind_of
from experiments.e247_count_matched_spread import per_cell
from experiments.e248_equal_count_base import COUNT, FAMILIES, base, leave_one_out, spread
from experiments.e249_third_cell_margin import KIND0, KIND1, margin
from experiments.e249_third_cell_margin import rank_contrast

CELL = (400, 40, 0.9)
REF = (300, 30, 0.9)
CLAIMS = (
    ("U1", "the flatter geometry gives the smaller margin",
     "At cs 400/support 40 with three drawings per family the (1, 0) margin is below the 1.008 the same statistic "
     "takes at cs 300/support 30 on the same footing, and below 1",
     "falsifier: at or above 1.10, a reversal at the flattest kind-1 geometry in the corpus; null: between the cs-300 "
     "value and 1.10"),
    ("U2", "the survivor travels",
     "erdos_renyi is the tightest family at this cell at three drawings",
     "falsifier: another family is as tight or tighter"),
)
FALSIFIER = 1.10


def levels(fam: dict, cell: tuple) -> dict[str, float | None]:
    """Each family's mean excess at the cell -- the confound, reported beside the spread."""
    out = {}
    for f in FAMILIES:
        d = fam.get(f, {}).get(cell)
        if d and d["excess"]:
            out[f] = sum(d["excess"]) / len(d["excess"])
    return out


def judge(fam: dict) -> list[dict]:
    b, r = base(fam, CELL, COUNT), base(fam, REF, COUNT)
    out: list[dict] = []
    if len(b) != len(FAMILIES) or len(r) != len(FAMILIES):
        return [{"id": cid, "verdict": f"REFUSED -- a base is not equal-count (new {sorted(set(FAMILIES) - set(b))}, "
                                       f"reference {sorted(set(FAMILIES) - set(r))})"}
                for cid, *_ in CLAIMS]

    m, ref = margin(b), margin(r)
    detail = ", ".join(f"{f} {spread(b[f]['excess']):.3f}x" for f in FAMILIES)
    if m is None or ref is None:
        out.append({"id": "U1", "verdict": "REFUSED -- a margin is not computable"})
    elif m >= FALSIFIER:
        out.append({"id": "U1", "measured": f"margin {m:.3f} against the reference's {ref:.3f}; {detail}",
                    "verdict": "FALSIFIER FIRED -- the flattest geometry reverses the pair"})
    elif m < ref and m < 1.0:
        out.append({"id": "U1", "measured": f"margin {m:.3f} against the reference's {ref:.3f}; {detail}",
                    "verdict": "MET -- the flatter geometry gives the smaller margin, with the no-destruction rung "
                               "the looser"})
    else:
        out.append({"id": "U1", "measured": f"margin {m:.3f} against the reference's {ref:.3f}; {detail}",
                    "verdict": "null band -- between the cs-300 value and the falsifier"})

    spreads = {f: spread(b[f]["excess"]) for f in FAMILIES}
    er = spreads.get("erdos_renyi")
    others = [v for f, v in spreads.items() if f != "erdos_renyi" and v]
    if er is None or not others:
        out.append({"id": "U2", "verdict": "REFUSED -- kind 2 or the rest is missing"})
    else:
        out.append({"id": "U2", "measured": f"erdos_renyi {er:.3f}x against {min(others):.3f}x to {max(others):.3f}x",
                    "verdict": "MET -- the two-side family is the tightest" if er < min(others) else
                               "FALSIFIER FIRED -- another family is as tight or tighter"})
    return out


def report(fam: dict) -> int:
    b, r = base(fam, CELL, COUNT), base(fam, REF, COUNT)
    print(f"== the second count-three base: cs {CELL[0]}/support {CELL[1]}/rho {CELL[2]:g}, {COUNT} drawings each ==")
    if not b:
        print("   the base is empty -- the runs have not landed")
        return len(CLAIMS)
    for label, cell, bb in (("NEW", CELL, b), ("REF", REF, r)):
        if not bb:
            print(f"   {label} cs {cell[0]}/support {cell[1]}: the base is short")
            continue
        print(f"   {label}  cs {cell[0]}/support {cell[1]}")
        print(f"      {'family':13} {'kind':>4} {'excesses':34} {'spread':>7} {'level':>9}")
        for f in FAMILIES:
            if f not in bb:
                continue
            e = bb[f]["excess"]
            print(f"      {f:13} {kind_of(f):>4} {str([round(v, 5) for v in e]):34} "
                  f"{(spread(e) or float('nan')):>7.3f} {sum(e) / len(e):>9.5f}")
        mm = margin(bb)
        print(f"      -> margin {(mm if mm is not None else float('nan')):.3f}")

    print("\n== the two count-three bases side by side (the low end of the relation) ==")
    print(f"   {'cell':>22} {'margin':>7}   kind-1 rank spreads")
    for cell, bb in ((REF, r), (CELL, b)):
        if bb:
            rc = rank_contrast(fam, cell)
            cm = margin(bb)
            print(f"   {f'cs {cell[0]}/sup {cell[1]}':>22} {(cm if cm is not None else float('nan')):>7.3f}   "
                  + ", ".join(f"{f} {v:.2f}x" for f, v in rc.items() if v))

    print("\n== the registered claims, U1-U2 ==")
    j = judge(fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the driver is read off the same drawings as the quantity it would explain, so ordering is not")
    print("    mechanism; and kind 0 sits near the floor against kind 1's 0.12 to 0.14, which no count can fix)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    fam = per_cell(args.runs)
    if args.json_out:
        b, r = base(fam, CELL, COUNT), base(fam, REF, COUNT)
        write_json(args.json_out, {"cell": list(CELL), "reference": list(REF), "count": COUNT,
                                   "families": {f: {**d} for f, d in b.items()},
                                   "spreads": {f: spread(d["excess"]) for f, d in b.items()},
                                   "margin": margin(b), "reference_margin": margin(r),
                                   "levels": levels(fam, CELL),
                                   "rank_contrasts": {str(c): rank_contrast(fam, c) for c in (REF, CELL)},
                                   "leave_one_out": leave_one_out(b),
                                   "claims": judge(fam)})
        print(f"wrote {args.json_out}")
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
