"""E254 -- a census of the record's quoted figures by how many drawings they rest on.

Four times this session a headline figure turned out to be a single drawing's: the `rho`-0.99 top step of 14.77x
(`e251`), the "late advantage" at 0.95 and 0.98 (`e253`), and `e230`'s cs-300 rank contrasts, whose withdrawal had to
be written into the paper. Each was found by accident, by a run that was looking at something else. This module is the
instrument that should have existed: **every quoted figure the record carries, with the cells and families it draws
on, and how many drawings each of those inputs has.**

    python -m experiments.e254_quoted_figure_census
    python -m experiments.e254_quoted_figure_census --json-out runs/e254_quoted_figure_census.json

The registry below is the hand-made part -- twelve of the figures this session's fires quote, each with the exact
(cell, family) inputs its arithmetic uses, and a flag for whether a fire has since compared that figure across more
drawings. Everything else is read from the corpus: a figure is

- **SAFE** when every input it names has two or more drawings at its cell;
- **DECOMPOSED** when it was exposed (an input with one drawing) and a fire has since drawn that cell again, so the
  input now has two or more -- the list of what has been checked;
- **STILL EXPOSED** when an input still has exactly one drawing -- the list that matters.

**Extended 2026-09-26 19:20** with the three cs-800 figures the registry had not named, which is the blind spot
`e255` left: `e255` closed the low-`rho` thinness at cs 300 and noted that cs 800's `rho` cells carry three families at
one drawing each, but the registry named no figure resting on them, so the census could not see whether that thinness
mattered. It does: the extension exposes **two more figures**, both at cs 800.

Claims, and their provenance. **C1**, **C2** and **C3** were registered before their run. **E1** to **E3** were added
with the extension above and were computed in the same minute, so they are **confirmatory** and their value is as a
**regression**: they pin the coverage so a future registry edit that silently drops a cs-800 figure fires.

Registered claims:

- **C1 -- the census finds at least three figures still exposed.** **Falsifier**: fewer than three, which would make
  the instrument a bookkeeping exercise rather than a map of what is unchecked.
- **C2 -- the exposure is concentrated, not spread.** Every still-exposed figure is exposed through either a cell at
  `rho` other than 0.9 or the weak-swap rungs of a well-drawn cell (`swap0.1`, `swap4`, `swap8`, `swap16`, `swap32`,
  `swap64`, the degrees of the axis whose analytic arm was never run). **Falsifier**: an exposed figure whose
  single-drawing input is a well-drawn family at `rho` 0.9.
- **C3 -- reported.** The per-cell table: for each cell, how many families it carries and the minimum drawings among
  them, so the corpus's own unevenness is visible beside the figures that depend on it.

The exit code is the number of claims **REFUSED** because the registry names a cell or family the corpus does not
have.

**What it cannot do**: the registry is **hand-made** and finite -- it covers the figures this session's fires quote
and no others, so a figure missing from it is invisible to the census; "how many drawings an input has" is not the
same as "how well that input is known", since `e247` measured that a two-drawing spread is already the corpus's
noisiest statistic, so SAFE here means "two or more" and not "resolved"; the DECOMPOSED flag records that a fire
compared the figure across drawings, not that the comparison agreed with the quoted form (`e253`'s `rho`-0.98
decomposition moved the top step by a factor of 4.47); and nothing here is a new measurement.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e247_count_matched_spread import per_cell

# (name, what the record says, [(cell, family), ...], decomposed-by-a-fire?)
REGISTRY = (
    ("ladder-levels-at-the-convention-cell", "the three levels 0.10067 / 0.05208 / 0.14897",
     [((800, 80, 0.9), "alloy1"), ((800, 80, 0.9), "inalloy1"), ((800, 80, 0.9), "erdos_renyi")], False),
    ("the-top-step-2.76x-and-3.02x", "Erdos-Renyi over alloy1 and over inalloy1 at the convention cell",
     [((800, 80, 0.9), "erdos_renyi"), ((800, 80, 0.9), "alloy1"), ((800, 80, 0.9), "inalloy1")], True),
    ("the-7x-top-step-is-cs-800-s", "the top step at cs 300, 400 and 800",
     [((300, 30, 0.9), "alloy1"), ((300, 30, 0.9), "erdos_renyi"),
      ((400, 40, 0.9), "alloy1"), ((400, 40, 0.9), "erdos_renyi"),
      ((800, 80, 0.9), "alloy1"), ((800, 80, 0.9), "erdos_renyi")], False),
    ("the-one-side-level-rises-as-the-circuit-shrinks", "0.047 at cs 800 against 0.122 at cs 300",
     [((800, 80, 0.9), "alloy1"), ((300, 30, 0.9), "alloy1")], False),
    ("the-two-side-level-is-nearly-flat", "0.142 / 0.150 / 0.157 at cs 800, 400 and 300",
     [((800, 80, 0.9), "erdos_renyi"), ((400, 40, 0.9), "erdos_renyi"), ((300, 30, 0.9), "erdos_renyi")], False),
    ("the-late-advantage", "1.91x at rho 0.95, 5.53x at 0.98 and 14.77x at 0.99",
     [((300, 30, 0.95), "alloy1"), ((300, 30, 0.95), "erdos_renyi"),
      ((300, 30, 0.98), "alloy1"), ((300, 30, 0.98), "erdos_renyi"),
      ((300, 30, 0.99), "alloy1"), ((300, 30, 0.99), "erdos_renyi")], True),
    ("the-rank-curve-falls-monotonically-in-rho", "every family's effective rank falls over the rho grid",
     [((300, 30, r), f) for r in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99)
      for f in ("alloy1", "erdos_renyi")], True),   # e255 drew the low-rho end: the fall survived, 1.00x to 1.10x
    ("erdos-renyi-does-not-collapse", "it plateaus at 3.18 while the one-side families reach 1.0",
     [((300, 30, 0.99), "erdos_renyi"), ((300, 30, 0.99), "alloy1"), ((300, 30, 0.99), "inalloy1")], False),
    ("the-one-zero-margin-across-cells", "0.787 / 0.851 / 0.935 / 1.660 at four cells",
     [((400, 40, 0.9), f) for f in ("swap0.5", "swap2", "signshuffle", "alloy1", "inalloy1")] +
     [((300, 30, 0.9), f) for f in ("swap0.5", "swap2", "signshuffle", "alloy1", "inalloy1")] +
     [((800, 20, 0.9), f) for f in ("swap0.5", "swap2", "signshuffle", "alloy1", "inalloy1")] +
     [((800, 80, 0.9), f) for f in ("swap0.5", "swap2", "signshuffle", "alloy1", "inalloy1")], True),
    ("alloy1-s-own-spread-3.34x", "the family's spread across its drawings at the convention cell",
     [((800, 80, 0.9), "alloy1")], True),
    ("the-cs-300-rank-contrasts-resolve", "7.68x to 25.25x against the families' own scatters",
     [((300, 30, r), f) for r in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99)
      for f in ("alloy1", "inalloy1")], True),
    ("the-floor-s-level", "swap0.5 and swap2 at 0.012 to 0.023",
     [((800, 80, 0.9), "swap0.5"), ((800, 80, 0.9), "swap2")], False),
    # added 2026-09-26 19:20: the three cs 800 figures this registry did not name, which is the blind spot e255 left
    ("the-rank-curve-at-cs-800", "the same fall as cs 300's, over the same rho grid at the other size",
     [((800, 80, r), f) for r in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99)
      for f in ("alloy1", "erdos_renyi")], False),
    ("the-size-effect-changes-sign-with-rho", "cs 800 over cs 300 reads 1.13x at rho 0.5, 2.14x at 0.9 and 0.06x at 0.99",
     [((800, 80, r), f) for r in (0.5, 0.9, 0.99) for f in ("alloy1", "erdos_renyi")] +
     [((300, 30, r), f) for r in (0.5, 0.9, 0.99) for f in ("alloy1", "erdos_renyi")], False),
    ("the-two-side-level-is-flat-across-sizes", "Erdos-Renyi at cs 800 and at cs 300, both at rho 0.9",
     [((800, 80, 0.9), "erdos_renyi"), ((300, 30, 0.9), "erdos_renyi")], False),
)
WEAK_SWAPS = ("swap0.1", "swap4", "swap8", "swap16", "swap32", "swap64", "swap256", "swap1024")
CLAIMS = (
    ("C1", "the census finds at least three figures still exposed",
     "At least three registered figures name an input that still has exactly one drawing",
     "falsifier: fewer than three, which would make the instrument bookkeeping rather than a map"),
    ("E1", "the extension exposes at least two more figures",
     "Naming the cs-800 figures brings at least two of them out as exposed",
     "falsifier: none, i.e. no quoted figure rests on cs 800's one-drawing rho cells [confirmatory, added with the "
     "extension: it is a coverage regression, not a blind test]"),
    ("E2", "every new exposure is a cs-800 rho cell",
     "The newly exposed figures are exposed through cs 800's rho grid and nowhere else",
     "falsifier: an exposure elsewhere in the corpus [confirmatory]"),
    ("E3", "the cs-800 rank curve is thin at most of its rho values",
     "The cs-800 rank curve names single-drawing inputs at more than four of its seven rho values",
     "falsifier: four or fewer, which would leave the cs-800 curve mostly drawn [confirmatory]"),
    ("C2", "the exposure is concentrated, not spread",
     "Every still-exposed figure is exposed through a cell at rho other than 0.9 or through a weak-swap rung of an "
     "otherwise well-drawn cell",
     "falsifier: an exposed figure whose single-drawing input is a well-drawn family at rho 0.9"),
)


def counts(fam: dict) -> dict:
    """(cell, family) -> how many positive excess drawings that input has."""
    out = {}
    for f, cells in fam.items():
        for cell, d in cells.items():
            if d["excess"]:
                out[(cell, f)] = len(d["excess"])
    return out


def classify(fam: dict) -> list[dict]:
    """Every registered figure as SAFE, DECOMPOSED or STILL EXPOSED, with the input that decides it."""
    n = counts(fam)
    out = []
    for name, says, inputs, drawn in REGISTRY:
        rows = [(cell, f, n.get((cell, f))) for cell, f in inputs]
        missing = [(cell, f) for cell, f, k in rows if k is None]
        thin = [(cell, f, k) for cell, f, k in rows if k is not None and k < 2]
        if missing:
            verdict = f"REFUSED -- the corpus has no {missing[0][1]} at {missing[0][0]}"
        elif not thin:
            verdict = "DECOMPOSED" if drawn else "SAFE"
        else:
            verdict = "STILL EXPOSED"
        out.append({"name": name, "says": says, "n_inputs": len(inputs), "thin": thin,
                    "decomposed_by_a_fire": drawn, "verdict": verdict,
                    "weak_swap": any(f in WEAK_SWAPS for _, f, _ in thin),
                    "off_rho_09": any(c[2] != 0.9 for c, _, _ in thin)})
    return out


def judge(fam: dict) -> list[dict]:
    rows = classify(fam)
    refused = [r for r in rows if r["verdict"].startswith("REFUSED")]
    if refused:
        return [{"id": cid, "verdict": f"REFUSED -- {refused[0]['verdict'][11:]}"} for cid, *_ in CLAIMS]
    exposed = [r for r in rows if r["verdict"] == "STILL EXPOSED"]
    out = [{"id": "C1", "measured": f"{len(exposed)} of {len(rows)} registered figures still name an input with one "
                                     f"drawing: {', '.join(r['name'] for r in exposed)}",
            "verdict": "MET -- at least three are still exposed" if len(exposed) >= 3 else
                       "FALSIFIER FIRED -- fewer than three remain exposed"}]
    stray = [r for r in exposed if not (r["weak_swap"] or r["off_rho_09"])]
    out.append({"id": "C2",
                "measured": "; ".join(f"{r['name']}: " + ", ".join(f"{f} at cs {c[0]}/sup {c[1]}/rho {c[2]:g} ({k})"
                                                                  for c, f, k in r["thin"]) for r in exposed)
                            or "no figure is exposed",
                "verdict": "MET -- every exposure is a rho cell or a weak-swap rung" if not stray else
                           f"FALSIFIER FIRED -- {[r['name'] for r in stray]} is exposed through a drawn family"})
    cs800 = ("the-rank-curve-at-cs-800", "the-size-effect-changes-sign-with-rho",
             "the-two-side-level-is-flat-across-sizes")
    if not all(any(r["name"] == n for r in rows) for n in cs800):
        return out + [{"id": cid, "verdict": f"REFUSED -- {cs800[0]} is not in the registry"} for cid in
                      ("E1", "E2", "E3")]
    e_rows = [r for r in rows if r["name"] in cs800]
    newly = [r for r in e_rows if r["verdict"] == "STILL EXPOSED"]
    out.append({"id": "E1", "measured": f"{len(newly)} of the {len(e_rows)} cs-800 figures the extension named are "
                                        f"exposed: {', '.join(r['name'] for r in newly) or 'none'}",
                "verdict": "MET -- at least two are" if len(newly) >= 2 else
                           "FALSIFIER FIRED -- the cs-800 thinness feeds fewer than two quoted figures"})
    off = [r["name"] for r in newly if not all(c[0] == 800 for c, _, _ in r["thin"])]
    out.append({"id": "E2", "measured": "; ".join(f"{r['name']}: " + ", ".join(f"cs {c[0]}/rho {c[2]:g}" for c, _, _ in r["thin"])
                                                   for r in newly) or "nothing new is exposed",
                "verdict": "MET -- every new exposure is a cs-800 rho cell" if not off else
                           f"FALSIFIER FIRED -- {off} is exposed elsewhere"})
    curve = [r for r in rows if r["name"] == "the-rank-curve-at-cs-800"][0]
    rhos = {c[2] for c, _, _ in curve["thin"]}
    out.append({"id": "E3", "measured": f"the cs-800 rank curve names single-drawing inputs at {len(rhos)} of its 7 rho "
                                        f"values ({sorted(rhos)})",
                "verdict": "MET -- more than four" if len(rhos) > 4 else
                           "FALSIFIER FIRED -- four or fewer"})

    return out


def report(fam: dict) -> int:
    n = counts(fam)
    rows = classify(fam)
    print("== the record's quoted figures, by how many drawings their inputs have ==")
    print(f"   {'figure':48} {'inputs':>6} {'verdict':>14}  thinnest input")
    for r in sorted(rows, key=lambda r: (r["verdict"] != "STILL EXPOSED", r["name"])):
        thin = r["thin"][0] if r["thin"] else None
        where = (f"{thin[1]} at cs {thin[0][0]}/sup {thin[0][1]}/rho {thin[0][2]:g} has {thin[2]} drawing "
                 f"({thin[2] and 'SINGLE' or ''})".strip()
                 if thin else "every input has 2 or more")
        print(f"   {r['name']:48} {r['n_inputs']:>6} {r['verdict']:>14}  {where}")

    print("\n== the ones that matter: still exposed, and whether a fire has looked ==")
    for r in rows:
        if r["verdict"] == "STILL EXPOSED":
            print(f"   {r['name']}")
            print(f"      the record says: {r['says']}")
            for c, f, k in r["thin"]:
                print(f"      single-drawing input: {f} at cs {c[0]}/sup {c[1]}/rho {c[2]:g} ({k} drawing)")

    print("\n== the corpus's own unevenness: every cell, by its thinnest family ==")
    cells: dict = {}
    for (cell, f), k in n.items():
        cells.setdefault(cell, {})[f] = k
    for cell in sorted(cells, key=lambda c: (min(cells[c].values()), c[0], c[1], c[2])):
        v = cells[cell]
        thin = [f for f, k in sorted(v.items()) if k == min(v.values())]
        print(f"   cs {cell[0]:>3}/sup {cell[1]:>3}/rho {cell[2]:<5} {len(v):>2} families, minimum "
              f"{min(v.values())} drawing(s) ({', '.join(thin)})")
    print(f"   ({sum(1 for c in cells if min(cells[c].values()) == 1)} of {len(cells)} cells carry a family with a "
          f"single drawing)")

    print("\n== the registered claims, C1-C2 ==")
    j = judge(fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the registry is hand-made and finite; SAFE means 'two or more drawings' and not 'resolved', since e247")
    print("    measured a two-drawing spread to be the corpus's noisiest statistic)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    fam = per_cell(args.runs)
    if args.json_out:
        write_json(args.json_out, {"counts": {f"{c[0]}/{c[1]}/{c[2]}/{f}": k for (c, f), k in counts(fam).items()},
                                   "figures": classify(fam), "claims": judge(fam)})
        print(f"wrote {args.json_out}")
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
