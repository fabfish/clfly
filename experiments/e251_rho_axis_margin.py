"""E251 -- the same cell at a different `rho`: the (1, 0) margin on the axis that holds size and support fixed.

The margin is monotone in the cell's kind-1 rank contrast across four cells on two footings (`e250`), but every one of
those cells varies **size, support and identity at once** and the driver is computed from **the same drawings** as the
quantity it would explain. `rho` -- the assembly geometry's target spectral radius -- is the one axis that holds
everything else fixed, and the corpus already has **eight** of its cells at cs 300/support 30 (0.5, 0.7, 0.8, 0.9,
0.95, 0.98, 0.99). But **the ladder families carry exactly one drawing at every `rho` except 0.9**, so no spread is
computable there, and **the kind-0 rung has never been drawn off `rho` 0.9 at all**.

Two runs (`e251`, seeds 3 and 4, all six families) give two drawings each at the same size and support as `e248`'s
base, and therefore a margin on the same **count-two** footing as four existing readings (0.771, 0.851, 0.935, 1.660).

    python -m experiments.e251_rho_axis_margin
    python -m experiments.e251_rho_axis_margin --json-out runs/e251_rho_axis_margin.json

**And it is the first base in this line that is equally DRAWN as well as equally counted**: every family's two
drawings are the same two `rewire_seed` values (3 and 4), where every earlier base took each family's first two
drawings whenever they happened to exist. That removes the "equal-count but not equally drawn" caveat this record has
repeated since `e248` -- for the new cell. The **reference** cell's margin is still the unequally-drawn one, so the two
margins being compared are not built the same way, and that is stated rather than hidden.

Four registered claims, three of them before the runs and one added mid-flight while they were in flight:

- **V1 -- the margin moves with `rho` the way the relation says.** The count-two (1, 0) margin at `rho` 0.99 is
  **above 0.851**, the value at the same cell with `rho` 0.9. **Falsifier**: at or below it; **null**: above 0.851 but
  below 0.90.
- **V1b -- the same claim on the equally-drawn pair, added while the runs were in flight.** The margin computed from
  **each family's two newest drawings** -- this fire's seeds 3 and 4 for all six families -- is also **above 0.851**.
  **Falsifier**: at or below it. Registered after the module's own table exposed that the new cell can be read on a
  footing no earlier base could, and before any artifact of the runs existed.
- **V2 -- the driver moves too.** The cell's kind-1 rank spreads are **above** the 2.73x and 2.08x they read at
  `rho` 0.9. **Falsifier**: below either, in which case driver and margin move in opposite directions along this axis.
- **V3 -- the survivor.** `erdos_renyi` is the tightest of the six families at `rho` 0.99.

The exit code is the number of claims **REFUSED** because the base is not equal-count.

**What it cannot do**: make the driver independent of the margin -- both are computed from **the same** drawings, so
the same-drawings objection survives this design and only a second instrument (the geometry's noise read from the
connectome side rather than the task side) would remove it; separate `rho` from the near-critical regime, since 0.99 is
also where the one-side level collapses 18x past its peak; speak for the three- or four-drawing footings; give more
than **one** new `rho` point, so a monotone-in-`rho` claim would rest on a single axis step; or fix the reference's own
unequal drawing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from statistics import median

from clfly.bench.artifacts import write_json
from experiments.e244_drawing_spread_by_kind import kind_of
from experiments.e247_count_matched_spread import per_cell
from experiments.e248_equal_count_base import COUNT as _COUNT3, FAMILIES, spread
from experiments.e249_third_cell_margin import KIND0, KIND1, margin, rank_contrast

CELL = (300, 30, 0.99)
REF = (300, 30, 0.9)
COUNT = 2
REF_MARGIN = 0.851
NULL_CEILING = 0.90
CLAIMS = (
    ("V1", "the margin moves with rho the way the relation says",
     "The count-two (1, 0) margin at rho 0.99 is above 0.851, the value at the same cell with rho 0.9",
     "falsifier: at or below it, so the margin does not move with the one axis that holds everything else fixed; "
     "null: above 0.851 but below 0.90"),
    ("V1b", "the same claim on the equally-drawn pair",
     "The margin computed from each family's two NEWEST drawings -- this fire's seeds 3 and 4 for all six families -- "
     "is also above 0.851",
     "falsifier: at or below it [registered while the runs were in flight, before any artifact existed, after the "
     "module's own table exposed that this cell can be read equally drawn]"),
    ("V2", "the driver moves too",
     "The cell's kind-1 rank spreads are above the 2.73x and 2.08x they read at rho 0.9",
     "falsifier: below either, so driver and margin move in opposite directions along this axis"),
    ("V3", "the survivor travels",
     "erdos_renyi is the tightest of the six families at rho 0.99",
     "falsifier: another family is as tight or tighter"),
)


def base(fam: dict, cell: tuple = CELL, count: int = COUNT, newest: bool = False) -> dict[str, dict]:
    """Each family's `count` drawings at the cell, the FIRST ones by seed or the NEWEST ones."""
    out = {}
    for f in FAMILIES:
        d = fam.get(f, {}).get(cell)
        if not d or len(d["excess"]) < count:
            continue
        if newest:
            out[f] = {k: v[-count:] for k, v in d.items()}
        else:
            out[f] = {k: v[:count] for k, v in d.items()}
    return out


def levels(fam: dict, cell: tuple) -> dict[str, float]:
    out = {}
    for f in FAMILIES:
        d = fam.get(f, {}).get(cell)
        if d and d["excess"]:
            out[f] = sum(d["excess"]) / len(d["excess"])
    return out


def judge(fam: dict) -> list[dict]:
    b, newest = base(fam), base(fam, newest=True)
    ref = base(fam, REF, COUNT)
    out: list[dict] = []
    if len(b) != len(FAMILIES) or len(ref) != len(FAMILIES):
        return [{"id": cid, "verdict": f"REFUSED -- the base is not equal-count (new {sorted(set(FAMILIES) - set(b))}, "
                                       f"reference {sorted(set(FAMILIES) - set(ref))})"}
                for cid, *_ in CLAIMS]

    m, r = margin(b), margin(ref)
    detail = ", ".join(f"{f} {spread(b[f]['excess']):.3f}x" for f in FAMILIES)
    if m is None:
        out.append({"id": "V1", "verdict": "REFUSED -- the margin is not computable"})
    elif m <= REF_MARGIN:
        out.append({"id": "V1", "measured": f"margin {m:.3f} against rho 0.9's {r:.3f} at the same cell; {detail}",
                    "verdict": "FALSIFIER FIRED -- the margin does not rise with rho"})
    elif m < NULL_CEILING:
        out.append({"id": "V1", "measured": f"margin {m:.3f} against rho 0.9's {r:.3f}; {detail}",
                    "verdict": "null band -- a rise inside the noise for two-drawing spreads"})
    else:
        out.append({"id": "V1", "measured": f"margin {m:.3f} against rho 0.9's {r:.3f} at the same cell; {detail}",
                    "verdict": "MET -- the margin rises with rho, holding size and support fixed"})

    mn = margin(newest) if len(newest) == len(FAMILIES) else None
    if mn is None:
        out.append({"id": "V1b", "verdict": "REFUSED -- the equally-drawn base is not complete"})
    else:
        out.append({"id": "V1b", "measured": f"equally-drawn margin {mn:.3f} over the seeds "
                                            f"{sorted({k for d in newest.values() for k in d['keys']})}",
                    "verdict": "MET -- above the reference's 0.851" if mn > REF_MARGIN else
                               "FALSIFIER FIRED -- at or below the reference's 0.851"})

    rc_now, rc_ref = rank_contrast(fam, CELL), rank_contrast(fam, REF)
    if any(rc_now.get(f) is None for f in KIND1) or any(rc_ref.get(f) is None for f in KIND1):
        out.append({"id": "V2", "verdict": "REFUSED -- a kind-1 family has no rank spread at one of the cells"})
    else:
        pairs = ", ".join(f"{f} {rc_now[f]:.2f}x against {rc_ref[f]:.2f}x" for f in KIND1)
        rises = all(rc_now[f] > rc_ref[f] for f in KIND1)
        out.append({"id": "V2", "measured": f"kind-1 rank spreads at rho 0.99 against rho 0.9: {pairs}",
                    "verdict": "MET -- the driver rises with rho too" if rises else
                               "FALSIFIER FIRED -- a kind-1 rank spread falls while the margin rises"})

    spreads = {f: spread(b[f]["excess"]) for f in FAMILIES}
    er = spreads.get("erdos_renyi")
    others = [v for f, v in spreads.items() if f != "erdos_renyi" and v]
    if er is None or not others:
        out.append({"id": "V3", "verdict": "REFUSED -- kind 2 or the rest is missing"})
    else:
        out.append({"id": "V3", "measured": f"erdos_renyi {er:.3f}x against {min(others):.3f}x to {max(others):.3f}x",
                    "verdict": "MET -- the two-side family is the tightest" if er < min(others) else
                               "FALSIFIER FIRED -- another family is as tight or tighter"})
    return out


def report(fam: dict) -> int:
    b = base(fam)
    print(f"== the rho axis at cs {CELL[0]}/support {CELL[1]}: rho {CELL[2]:g} against rho {REF[2]:g} ==")
    if not b:
        print("   the base is empty -- the runs have not landed")
        return len(CLAIMS)
    for label, cell in (("NEW rho 0.99", CELL), ("REF rho 0.90", REF)):
        bb = base(fam, cell, COUNT)
        print(f"   {label}: {'complete' if len(bb) == len(FAMILIES) else 'INCOMPLETE'} "
              f"({len(bb)} of {len(FAMILIES)} families with {COUNT} drawings)")
        if len(bb) != len(FAMILIES):
            continue
        lv = levels(fam, cell)
        for f in FAMILIES:
            e, rk = bb[f]["excess"], bb[f]["rank"]
            print(f"      {f:13} {kind_of(f)}  excesses {str([round(v, 5) for v in e]):26} "
                  f"spread {(spread(e) or float('nan')):>6.3f}  level {lv[f]:.5f}  "
                  f"rank spread {(spread(rk) or float('nan')):>6.2f}")
        print(f"      -> margin {margin(bb):.3f}")

    print("\n== the equally-drawn pair (each family's two NEWEST drawings) ==")
    newest = base(fam, CELL, COUNT, newest=True)
    if len(newest) == len(FAMILIES):
        for f in FAMILIES:
            print(f"   {f:13} keys {newest[f]['keys']}  excesses {[round(v, 5) for v in newest[f]['excess']]}  "
                  f"spread {spread(newest[f]['excess']):.3f}")
        print(f"   -> margin {margin(newest):.3f}")

    print("\n== the registered claims, V1-V3 ==")
    j = judge(fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (both quantities -- the margin and the rank spread that would drive it -- come from the same drawings,")
    print("    so this axis tests the relation's consistency and not its mechanism)")
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
        write_json(args.json_out, {"cell": list(CELL), "reference": list(REF), "count": COUNT,
                                   "families": {f: {**d} for f, d in b.items()},
                                   "spreads": {f: spread(d["excess"]) for f, d in b.items()},
                                   "levels": levels(fam, CELL),
                                   "margin": margin(b),
                                   "reference_margin": margin(base(fam, REF, COUNT)),
                                   "equally_drawn": {f: {**d} for f, d in base(fam, CELL, COUNT, True).items()},
                                   "equally_drawn_margin": margin(base(fam, CELL, COUNT, True)),
                                   "rank_contrasts": {str(c): rank_contrast(fam, c) for c in (REF, CELL)},
                                   "claims": judge(fam)})
        print(f"wrote {args.json_out}")
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
