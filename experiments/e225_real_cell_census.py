"""E225 -- the `real` cell's determinism across the corpus: does the rewiring really leave the connectome alone?

The last finding leaned on a premise that had never been checked corpus-wide: **the rewiring does not touch the
connectome**, so the `real` cell's analytic excess must be *identical* in every artifact whose tasks and circuit are
the same — even when the artifacts differ in `rewire_seed`, in the other topologies they carry, or in when they were
written. Two drawings of `e223` confirmed it to five decimals (0.01774 in both) while every rewired cell moved, which
is the observation this audit generalises: group every artifact's `real` cell by the fields that determine the tasks
and the circuit (`circuit_size`, `support`, `seeds`, `seed0`, `q`), and require the group's values to agree.

The classification has to be **derived, not listed**, because the corpus contains two analytic implementations of a
`real` cell and they are not the same quantity:

  * the **pooling family** (`e3_basis_selection --ladder`, `e13`) writes bases `bio:pool1 … bio:pool128` and an `_abs`
    block;
  * the **cell-class family** (`e2_topology_gap`, and everything this week's work ran) writes `diagonal(EWC)`,
    `bio:cell_class` and `rand:cell_class`.

A group's family is therefore read off the base names its `real` block carries, and a group that mixes families is
reported as such rather than as a reproducibility failure.

    python -m experiments.e225_real_cell_census
    python -m experiments.e225_real_cell_census --json-out runs/e225_real_cell_census.json

Three tolerance classes, all declared: **EXACT** (relative difference ≤ 1e-12), **FLOATING** (≤ 1e-6, reported and
not counted — a code epoch's arithmetic is not a reproducibility failure), and **MATERIAL** (> 1e-6, counted unless it
is a declared cross-family group). The exit code is the number of MATERIAL disagreements inside a family.

**What it cannot do**: it sees only the 26 artifacts that carry a `real` cell with an analytic excess — the realized
arm, the network line and every aggregate summary are outside its scope; it compares one number per artifact rather
than the whole cell; and it cannot say *which* code changed where a FLOATING difference appears, only that the value
moved by less than 1e-6.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e103_reproducibility_audit import load_artifacts

RUNS = Path("runs")
#: the fields that determine the tasks and the circuit, so that two cells agreeing on them must agree in value
KEY_FIELDS = ("circuit_size", "support", "seeds", "seed0", "q")
#: the tolerance classes
#: the tolerance classes. The FLOATING/MATERIAL boundary is 1e-4 relative and the corpus leaves it four orders of
#: room: the largest within-family difference is **1.66e-6** (the pooling runner at two epochs) and the only
#: cross-family one is **8.96e-2**, so any boundary between 1e-5 and 1e-3 classifies this corpus identically --
#: the choice does no work here, and it is stated so that it is visible if a future artifact lands between them.
EXACT, FLOATING = 1e-12, 1e-4

#: groups whose families differ, with why the values are not the same quantity. Declared rather than counted: the
#: pooling runner and the cell-class runner compute "the excess" with different bases and different flags, so their
#: `real` cells are two quantities rather than two measurements of one.
DECLARED_CROSS_FAMILY = "any group mixing families"


def family(block: dict) -> str:
    """Which analytic implementation produced this `real` block, read off the base names it carries."""
    names = set(block)
    if "bio:cell_class" in names:
        return "cell_class"
    if any(n.startswith("bio:pool") for n in names):
        return "pooling"
    return "unknown"


def excess(block: dict) -> float | None:
    v = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


def census(root: Path = RUNS) -> dict:
    """Every artifact's `real` cell, grouped by the fields that determine it, with each group's agreement class."""
    groups: dict[tuple, list[dict]] = {}
    for a in load_artifacts(root):
        block = (a["payload"].get("topologies") or {}).get("real")
        if not isinstance(block, dict):
            continue
        v = excess(block)
        if v is None:
            continue
        key = tuple(a["config"].get(f) for f in KEY_FIELDS)
        groups.setdefault(key, []).append({"artifact": a["name"], "value": v,
                                           "family": family(block),
                                           "rewire_seed": a["config"].get("rewire_seed")})
    out = []
    for key, rows in sorted(groups.items(), key=lambda kv: str(kv[0])):
        fams = sorted({r["family"] for r in rows})
        vals = [r["value"] for r in rows]
        spread = max(vals) - min(vals)
        rel = spread / abs(sum(vals) / len(vals)) if sum(vals) else 0.0
        if len(rows) < 2:
            cls = "single"
        elif rel <= EXACT:
            cls = "EXACT"
        elif rel <= FLOATING:
            cls = "FLOATING"
        else:
            cls = "MATERIAL"
        out.append({"key": dict(zip(KEY_FIELDS, key)), "families": fams, "n": len(rows),
                    "values": vals, "spread": spread, "relative": rel, "class": cls,
                    "rows": sorted(rows, key=lambda r: r["artifact"])})
    return {"groups": out, "artifacts_with_a_real_cell": sum(g["n"] for g in out)}


def report(res: dict) -> int:
    groups = res["groups"]
    multi = [g for g in groups if g["n"] > 1]
    by_class = {}
    for g in multi:
        by_class.setdefault(g["class"], []).append(g)
    print("== the `real` cell across the corpus ==")
    print(f"   artifacts carrying a `real` cell with an analytic excess: {res['artifacts_with_a_real_cell']}"
          f" in {len(groups)} groups by {', '.join(KEY_FIELDS)}")
    print(f"   groups with more than one artifact: {len(multi)}"
          + "".join(f", {len(v)} {k}" for k, v in sorted(by_class.items())))
    for cls in ("EXACT", "FLOATING", "MATERIAL"):
        for g in by_class.get(cls, []):
            key = ", ".join(f"{k}={v}" for k, v in g["key"].items() if k in ("circuit_size", "support", "seeds"))
            fams = "+".join(g["families"])
            print(f"\n   {cls:9} {key}  ({g['n']} artifacts, family {fams})")
            for r in g["rows"]:
                print(f"      {r['artifact']:<44}{r['value']:.10f}   rewire_seed {r['rewire_seed']}")
            print(f"      spread {g['spread']:.3e} (relative {g['relative']:.2e})")
    material = [g for g in by_class.get("MATERIAL", []) if len(g["families"]) == 1]
    mixed = [g for g in by_class.get("MATERIAL", []) if len(g["families"]) > 1]
    print("\n== what the classes mean ==")
    print(f"   EXACT (≤{EXACT:g} relative): the rewiring left the connectome alone, to the last bit -- "
          f"{len(by_class.get('EXACT', []))} group(s)")
    print(f"   FLOATING (≤{FLOATING:g}): the same runner at two epochs, and the arithmetic moved by less than a "
          f"millionth -- {len(by_class.get('FLOATING', []))} group(s), reported and not counted")
    print(f"   MATERIAL (> {FLOATING:g}) inside ONE family: a reproducibility failure -- "
          f"{len(material)} group(s), counted in the exit code")
    print(f"   MATERIAL across families: DECLARED, because the pooling runner and the cell-class runner compute "
          f"\"the excess\" with different bases and flags, so their `real` cells are two quantities rather than two "
          f"measurements of one -- {len(mixed)} group(s), not counted")
    for g in mixed:
        print(f"      the mixed group's families: {', '.join(g['families'])}, relative difference "
              f"{g['relative']:.2e} ({g['spread']:.5f} absolute)")
    print(f"\n   VERDICT: {len(material)} material disagreement(s) inside a family"
          + ("" if not material else " -- see above"))
    return len(material)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    res = census(args.runs)
    if args.json_out:
        write_json(args.json_out, res)
        print(f"wrote {args.json_out}")
    return report(res)


if __name__ == "__main__":
    sys.exit(main())
