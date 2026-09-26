"""E253 -- a second drawing at `rho` 0.95 and 0.98: is the "late advantage" a cell's or a drawing's?

This record's headline reading of the ladder's mechanism is that the two-side advantage is **late rather than
high-`rho`**: "Erdos-Renyi over `alloy1` is **1.91x** at `rho` 0.95, **5.53x** at 0.98 and **14.77x** at 0.99". `e251`
decomposed the third of those three points by drawing and found it is **one drawing's arithmetic** -- the quoted 14.77x
is the corpus's seed-0 drawing, two more drawings at the same cell and the same `rho` give **2.22x**, and the three
pooled give 2.91x.

**The first two points rest on one drawing each as well and nobody has looked:**

    rho 0.95   alloy1 0.06927  erdos_renyi 0.13223  ->  1.91x   (rewire_seed 0, one drawing)
    rho 0.98   alloy1 0.01674  erdos_renyi 0.09253  ->  5.53x   (rewire_seed 0, one drawing)

Two runs (`e253`, all six topologies, `rewire_seed` 1 at each `rho`) add a second drawing to every family at both
cells -- the first decomposition of both points.

    python -m experiments.e253_two_drawings_at_high_rho
    python -m experiments.e253_two_drawings_at_high_rho --json-out runs/e253_two_drawings_at_high_rho.json

Four registered claims:

- **W1 -- the discriminating one: is the quoted figure a drawing's?** At `rho` 0.98 the top step on the new drawing
  differs from the quoted **5.53x** by a factor of at least **1.5** in either direction. **Falsifier**: within **+-10%**
  -- the quoted value is typical of its cell and the 0.99 swing is peculiar to 0.99; **null**: a factor between 1.1 and
  1.5.
- **W2 -- the trend's sign survives one more drawing.** On the new drawings the top step at `rho` 0.98 is still
  **above** the one at 0.95, as the quoted pair is. **Falsifier**: the order reverses, which would leave the "late"
  reading with no support at the drawing level either.
- **W3 -- reported.** Both new drawings' six families at both cells: excesses, top steps, one-side levels, beside what
  the corpus's own drawings read there.
- **W4 -- reported.** What the two cells do to `e252`'s declared domain.

The exit code is the number of claims **REFUSED** because a cell has no second drawing yet.

**What it cannot do**: give a distribution -- two drawings per cell is one difference, and `e251` measured a
two-drawing spread to be the corpus's noisiest statistic, so a swing here is evidence about that pair and not a
variance; it does not re-test `rho` 0.99; `rho` 0.95 and 0.98 are different task **geometries** as well as different
scalars, so the two runs are not a controlled contrast; one run per `rho` means the kind-0 families have one drawing
each, so no (1, 0) margin is computable at these cells and this unit says nothing about it; and the corpus's own
drawings are `rewire_seed` 0 while the new ones are seed 1 -- the same unequal drawing earlier bases had.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e247_count_matched_spread import per_cell
from experiments.e252_spread_domain import T, cell_scatters, domain

CELLS = ((300, 30, 0.95), (300, 30, 0.98))
FAMILIES = ("swap0.5", "swap2", "signshuffle", "alloy1", "inalloy1", "erdos_renyi")
ONE_SIDE = ("alloy1", "inalloy1")
QUOTED = {0.95: 1.91, 0.98: 5.53, 0.99: 14.77}
CLAIMS = (
    ("W1", "is the quoted figure a drawing's?",
     "At rho 0.98 the top step on the new drawing differs from the quoted 5.53x by a factor of at least 1.5 in either "
     "direction",
     "falsifier: within +-10%, so the quoted value is typical of its cell and the 0.99 swing is peculiar to 0.99; "
     "null: a factor between 1.1 and 1.5"),
    ("W2", "the trend's sign survives one more drawing",
     "On the new drawings the top step at rho 0.98 is still above the one at rho 0.95",
     "falsifier: the order reverses, leaving the 'late' reading with no support at the drawing level either"),
)
SHARE = 1.5
TYPICAL = 1.10


def top_step(fam: dict, cell: tuple, key: int) -> float | None:
    """Erdos-Renyi over alloy1 on one named drawing."""
    a = fam.get("alloy1", {}).get(cell, {})
    e = fam.get("erdos_renyi", {}).get(cell, {})
    try:
        i = a["keys"].index(key)
        j = e["keys"].index(key)
    except (KeyError, ValueError):
        return None
    av, ev = a["excess"][i], e["excess"][j]
    return (ev / av) if av and av > 0 else None


def drawing_keys(fam: dict, cell: tuple) -> list[int]:
    return sorted(fam.get("alloy1", {}).get(cell, {}).get("keys", []))


def levels(fam: dict, cell: tuple) -> dict[str, float | None]:
    out = {}
    for f in FAMILIES:
        e = fam.get(f, {}).get(cell, {}).get("excess") or []
        out[f] = (sum(e) / len(e)) if e else None
    return out


def share(a: float, b: float) -> float:
    return max(a, b) / min(a, b) if a and b else float("nan")


def judge(fam: dict) -> list[dict]:
    out: list[dict] = []
    keys = {c: drawing_keys(fam, c) for c in CELLS}
    if any(len(keys[c]) < 2 or 1 not in keys[c] for c in CELLS):
        return [{"id": cid, "verdict": f"REFUSED -- a cell has no second drawing yet ({ {str(c): keys[c] for c in CELLS} })"}
                for cid, *_ in CLAIMS]

    tops = {(c, k): top_step(fam, c, k) for c in CELLS for k in keys[c]}
    q98, n98 = tops.get(((300, 30, 0.98), 0)), tops.get(((300, 30, 0.98), 1))
    q95, n95 = tops.get(((300, 30, 0.95), 0)), tops.get(((300, 30, 0.95), 1))

    if not q98 or not n98:
        out.append({"id": "W1", "verdict": "REFUSED -- the rho-0.98 top step is not computable"})
    else:
        s = share(q98, n98)
        measured = (f"rho 0.98 top step: corpus's seed-0 drawing {q98:.2f}x against the new drawing {n98:.2f}x "
                    f"(a factor of {s:.2f}); the quoted value is {QUOTED[0.98]:.2f}x")
        if s <= TYPICAL:
            verdict = "FALSIFIER FIRED -- the new drawing agrees within +-10%, so the quoted value is typical"
        elif s >= SHARE:
            verdict = "MET -- the quoted figure is one drawing's, as it was at rho 0.99"
        else:
            verdict = "null band -- a factor between 1.1 and 1.5"
        out.append({"id": "W1", "measured": measured, "verdict": verdict})

    if None in (n98, n95):
        out.append({"id": "W2", "verdict": "REFUSED -- a new drawing has no computable top step"})
    else:
        keeps = n98 > n95
        out.append({"id": "W2", "measured": f"on the new drawings: rho 0.98 {n98:.2f}x against rho 0.95 {n95:.2f}x "
                                           f"(the corpus's own pair is {q98:.2f}x against {q95:.2f}x)",
                    "verdict": "MET -- the trend's sign survives" if keeps else
                               "FALSIFIER FIRED -- the new pair reverses the order"})
    return out


def report(fam: dict) -> int:
    print("== a second drawing at rho 0.95 and 0.98: the top step on each drawing ==")
    keys = {c: drawing_keys(fam, c) for c in CELLS}
    if any(len(keys[c]) < 2 for c in CELLS):
        print(f"   {[f'cs {c[0]}/sup {c[1]}/rho {c[2]:g}: keys {keys[c]}' for c in CELLS]}")
        print("   the new drawings have not landed")
        return len(CLAIMS)

    print(f"   {'cell':>22} {'drawing':>8} {'alloy1':>9} {'inalloy1':>9} {'erdos_renyi':>12} {'top step':>9}")
    for cell in CELLS:
        a = fam["alloy1"][cell]
        i = fam["inalloy1"][cell]
        e = fam["erdos_renyi"][cell]
        for k in keys[cell]:
            ts = top_step(fam, cell, k)
            print(f"   cs {cell[0]:>3}/sup {cell[1]:>3}/rho {cell[2]:<5} {k:>8} "
                  f"{a['excess'][a['keys'].index(k)]:>9.5f} {i['excess'][i['keys'].index(k)]:>9.5f} "
                  f"{e['excess'][e['keys'].index(k)]:>12.5f} {(ts if ts else float('nan')):>9.2f}"
                  + ("   <- the quoted figure" if k == 0 and cell[2] in QUOTED else ""))

    print("\n== the two points, decomposed ==")
    for cell in CELLS:
        q, n = top_step(fam, cell, 0), top_step(fam, cell, 1)
        print(f"   rho {cell[2]:<5} quoted {QUOTED.get(cell[2], float('nan')):>6.2f}x   corpus drawing {q:>6.2f}x   "
              f"new drawing {n:>6.2f}x   factor {share(q, n):>5.2f}   pooled of two "
              f"{('%.2f' % ((q + n) / 2)) if q and n else 'nan'}x")

    print("\n== the one-side levels, so the collapse is visible beside the top step ==")
    for cell in CELLS:
        lv = levels(fam, cell)
        print(f"   cs {cell[0]}/sup {cell[1]}/rho {cell[2]:<5} " +
              "  ".join(f"{f} {lv[f]:.5f}" for f in FAMILIES if lv[f] is not None))

    print("\n== what the two cells do to e252's declared domain ==")
    cells = cell_scatters(fam)
    inside, outside = domain(cells, T)
    for cell in CELLS:
        if cell in cells:
            mx = max(cells[cell].values())
            print(f"   cs {cell[0]}/sup {cell[1]}/rho {cell[2]:<5} max family scatter {mx:>7.2f}  "
                  f"{'in' if cell in inside else 'OUT of the domain'}")

    print("\n== the registered claims, W1-W2 ==")
    j = judge(fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (two drawings per cell is one difference and not a distribution, and rho 0.95 and 0.98 are different")
    print("    task geometries as well as different scalars -- so this decomposes the two quoted points and nothing more)")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    fam = per_cell(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": [list(c) for c in CELLS], "quoted": {str(k): v for k, v in QUOTED.items()},
                                   "top_steps": {f"{c[2]:g}": {str(k): top_step(fam, c, k)
                                                               for k in drawing_keys(fam, c)} for c in CELLS},
                                   "levels": {f"{c[2]:g}": levels(fam, c) for c in CELLS},
                                   "claims": judge(fam)})
        print(f"wrote {args.json_out}")
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
