"""E248 -- the equal-count base: six families at three drawings each, at one cell, so the spread comparison is not a
sample-size comparison.

`e247` ended this line's spread story in bands. Every spread it, `e244`, `e245` and `e246` compared is a max-over-min
over however many drawings a cell happened to have -- `alloy1` at cs 800/support 80 has eight, `swap0.5` at cs
300/support 30 had two -- so the cross-family comparison was also a comparison of sample sizes, and count-matching
post hoc left bands resting on the corpus's two-drawing cells.

This module reads a base that does not have that problem, because the cell was chosen for it: at **cs 300/support 30**
the three kind-1 and kind-2 families already carried three drawings each (`rewire_seed` 0, 1, 2), and **one run**
(`e248`, `rewire_seed` 5) gave the three kind-0 families their third. Six families, **three drawings each, 18 groups**,
no post-hoc subsetting.

    python -m experiments.e248_equal_count_base
    python -m experiments.e248_equal_count_base --json-out runs/e248_equal_count_base.json

Three registered claims, all made before the run:

- **S1 -- the (1, 0) question at equal count, which is why the run exists.** The kind-0 families' **median** spread is
  **below** the kind-1 families' median: the pooled ordering holds inside the cell once the sample sizes are equal.
  **Falsifier**: kind 0 at or above kind 1, the reversal at equal count; **null**: the medians within **10%**. Two
  earlier readings of this cell point opposite ways and neither was taken at equal count --- `e245`'s all-drawings
  form read kind 0 1.39x against kind 1 1.42x (+2.2%, its own null band) and `e247`'s two-drawing form read 1.39x
  against 1.26x (the pooled way) --- so what the third kind-0 drawing does is the measurement.
- **S2 -- the two-side rung at equal count.** `erdos_renyi`'s spread is below **both** kind-1 families'. **Falsifier**:
  at or above either.
- **S3 -- the reading is stable to which drawing is dropped.** `erdos_renyi` is the tightest of the six families under
  **every** leave-one-out subset of the base, i.e. under each of the three two-drawing subsets. **Falsifier**: a
  subset in which another family is tighter, which would make "the tightest family" one drawing's property.

The exit code is the number of claims **REFUSED** because the base is not equal-count.

**What it cannot do**: three drawings is a range and not a distribution, so this **narrows** the band `e247` left rather
than closing it; the three kind-0 families share the run's single `rewire_seed`, so their third drawings are not
independent of one another; the kind-1 and kind-2 drawings come from `e217`/`e219` rather than from this design, so the
base is equal-**count** and not equally **drawn**, and no count can fix that; one cell at one size and one `rho` (the
builder's default, `config.rho: None`); and it compares spreads, saying nothing about the levels, which differ by 2x to
5x between the kinds at this cell (`e245`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import median

from clfly.bench.artifacts import write_json
from experiments.e244_drawing_spread_by_kind import kind_of
from experiments.e247_count_matched_spread import per_cell

CELL = (300, 30, 0.9)
COUNT = 3
FAMILIES = ("swap0.5", "swap2", "signshuffle", "alloy1", "inalloy1", "erdos_renyi")
CLAIMS = (
    ("S1", "the (1, 0) question at equal count",
     "At three drawings per family the kind-0 families' median spread is below the kind-1 families' median",
     "falsifier: kind 0 at or above kind 1, the reversal at equal count; null: the medians within 10%"),
    ("S2", "the two-side rung at equal count",
     "erdos_renyi's spread is below both kind-1 families' spreads",
     "falsifier: at or above either"),
    ("S3", "the reading is stable to which drawing is dropped",
     "erdos_renyi is the tightest of the six families under every leave-one-out subset of the base",
     "falsifier: a subset in which another family is tighter"),
)
TIE_BAND = 0.10


def base(fam: dict, cell: tuple = CELL, count: int = COUNT) -> dict[str, dict]:
    """Each family's first `count` drawings at the cell -- equal counts by construction, else the base is refused."""
    out = {}
    for f in FAMILIES:
        d = fam.get(f, {}).get(cell)
        if not d or len(d["excess"]) < count:
            continue
        out[f] = {"excess": d["excess"][:count], "rank": d["rank"][:count], "keys": d["keys"][:count]}
    return out


def spread(vals) -> float | None:
    v = [x for x in vals if x and x > 0]
    return (max(v) / min(v)) if len(v) > 1 else None


def kind_medians(spreads: dict[str, float]) -> dict[int, float]:
    by: dict[int, list[float]] = {}
    for f, s in spreads.items():
        k = kind_of(f)
        if k is not None and s is not None:
            by.setdefault(k, []).append(s)
    return {k: median(v) for k, v in by.items()}


def leave_one_out(b: dict[str, dict]) -> list[dict[str, float]]:
    """One column per dropped drawing: every family's spread on the two that remain."""
    out = []
    for i in range(COUNT):
        col = {}
        for f, d in b.items():
            keep = [v for j, v in enumerate(d["excess"]) if j != i]
            col[f] = spread(keep)
        out.append(col)
    return out


def judge(b: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    if len(b) != len(FAMILIES) or any(len(d["excess"]) != COUNT for d in b.values()):
        missing = sorted(set(FAMILIES) - set(b))
        return [{"id": cid, "verdict": f"REFUSED -- the base is not equal-count (missing {missing})"}
                for cid, *_ in CLAIMS]

    spreads = {f: spread(d["excess"]) for f, d in b.items()}
    med = kind_medians(spreads)
    detail = ", ".join(f"{f} {spreads[f]:.2f}x" for f in FAMILIES)
    if 0 not in med or 1 not in med:
        out.append({"id": "S1", "verdict": "REFUSED -- a kind is missing from the equal-count base"})
    else:
        gap = abs(med[1] - med[0]) / min(med[0], med[1])
        if gap <= TIE_BAND:
            verdict = f"null band -- the medians are within {100 * gap:.1f}%, inside the 10% band"
        elif med[0] < med[1]:
            verdict = "MET -- kind 0 is the tighter, so the pooled ordering holds at equal count"
        else:
            verdict = "FALSIFIER FIRED -- the reversal holds at equal count"
        out.append({"id": "S1", "measured": f"kind 0 {med[0]:.3f}x against kind 1 {med[1]:.3f}x "
                                           f"({100 * (med[1] / med[0] - 1):+.1f}%); {detail}", "verdict": verdict})

    ones = [spreads[f] for f in ("alloy1", "inalloy1") if spreads.get(f)]
    er = spreads.get("erdos_renyi")
    if er is None or not ones:
        out.append({"id": "S2", "verdict": "REFUSED -- kind 2 or kind 1 is missing"})
    else:
        out.append({"id": "S2", "measured": f"erdos_renyi {er:.3f}x against alloy1 and inalloy1 "
                                           f"{', '.join(f'{o:.3f}x' for o in ones)}",
                    "verdict": "MET -- the two-side family is the tighter" if er < min(ones) else
                               "FALSIFIER FIRED -- a one-side family is as tight or tighter"})

    cols = leave_one_out(b)
    beaten = [i for i, col in enumerate(cols)
              if col.get("erdos_renyi") is None or any(col.get(f) and col[f] < col["erdos_renyi"]
                                                       for f in FAMILIES if f != "erdos_renyi")]
    measured = "; ".join("drop " + str(i) + ": " + ", ".join(f"{f} {col[f]:.2f}x" for f in FAMILIES
                                                             if col.get(f)) for i, col in enumerate(cols))
    out.append({"id": "S3", "measured": measured,
                "verdict": "MET -- the two-side family is the tightest under every subset" if not beaten else
                           f"FALSIFIER FIRED -- another family is tighter when drawing {beaten} is dropped"})
    return out


def report(b: dict[str, dict]) -> int:
    print(f"== the equal-count base: cs {CELL[0]}/support {CELL[1]}/rho {CELL[2]:g}, {COUNT} drawings per family ==")
    if not b:
        print("   the base is empty -- the run has not landed")
        return len(CLAIMS)
    print(f"   {'family':13} {'kind':>4} {'excesses':34} {'spread':>7} {'ranks':28} {'rank spread':>11}")
    for f in FAMILIES:
        d = b.get(f)
        if not d:
            print(f"   {f:13} MISSING")
            continue
        rk = [round(v, 2) for v in d["rank"]]
        print(f"   {f:13} {kind_of(f):>4} {str([round(v, 5) for v in d['excess']]):34} "
              f"{(spread(d['excess']) or float('nan')):>7.3f} {str(rk):28} "
              f"{(spread(rk) or float('nan')):>11.2f}")
    spreads = {f: spread(d["excess"]) for f, d in b.items()}
    med = kind_medians(spreads)
    print("\n== the kind medians at equal count ==")
    for k in sorted(med):
        print(f"   kind {k}: median {med[k]:.3f}x over {[f for f in FAMILIES if kind_of(f) == k]}")
    print("\n== which drawings carry the spread (the run's own third drawing is key 5) ==")
    for f in FAMILIES:
        if f in b:
            print(f"   {f:13} keys {b[f]['keys']}  excesses {[round(v, 5) for v in b[f]['excess']]}")
    print("\n== the registered claims, S1-S3 ==")
    j = judge(b)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the base is equal-count and not equally drawn: kind 1 and 2's drawings come from `e217`/`e219`, kind 0's")
    print("    from `e245` and this run, and no count can make those the same drawings)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    b = base(per_cell(args.runs))
    if args.json_out:
        write_json(args.json_out, {"cell": list(CELL), "count": COUNT,
                                   "families": {f: {**d} for f, d in b.items()},
                                   "spreads": {f: spread(d["excess"]) for f, d in b.items()},
                                   "kind_medians": {str(k): v for k, v in kind_medians(
                                       {f: spread(d["excess"]) for f, d in b.items()}).items()},
                                   "leave_one_out": leave_one_out(b),
                                   "claims": judge(b)})
        print(f"wrote {args.json_out}")
    return report(b)


if __name__ == "__main__":
    sys.exit(main())
