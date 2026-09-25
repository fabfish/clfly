"""E218 -- the ladder read at three circuit sizes: does the shape survive, and does the top step?

`e216` completed the four-construction ladder at cs 800: **the diagonalisation penalty follows how many of the graph's
two degree sequences a null destroys** — 0 destroyed ≈0.02 (`swap*`, `signshuffle`), 1 destroyed ≈0.045 by **two
independent routes** (`alloy1` 0.051, `inalloy1` 0.047), 2 destroyed ≈0.145 (`erdos_renyi`) — while the tasks'
alignment is decoupled from it. `e217` re-runs the ladder's three levels at **cs 300 and cs 400**, because every cell
of the original was cs 800 with `seed0` 0 and this project's standard after C1 is that a claim must hold at more than
one circuit size before it is quoted as a property of the substrate.

    python -m experiments.e218_ladder_replication_read
    python -m experiments.e218_ladder_replication_read --json-out runs/e218_ladder_replication_read.json

Three claims, registered **for each size separately**
(`docs/findings/2026-09-26-registered-does-the-ladder-survive-at-another-circuit-size.md`):

  * **Z1 — the top step**: `erdos_renyi` exceeds the **larger** of the two one-side nulls by at least **1.5x**
    (cs 800: 2.76x and 3.02x); falsifier within **1.25x**; null 1.25-1.5x.
  * **Z2 — the middle is ONE level**: the two one-side nulls differ by at most **2x** (cs 800: 1.09); falsifier more
    than **2x**, which would say the two sides are not interchangeable and the ladder's middle is two levels while
    its ends stay put; null 1.5-2x.
  * **Z3 — the floor**: `real` is below **both** one-side nulls; falsifier `real` at or above either.

**What it cannot do**: give a circuit-size *trend* (three points, no relation), separate the ladder from the support
size (held at the 10%-of-circuit convention), replicate the top step's tightness or the middle level's spread (one
realization per cell at each new size, and the alloy's own spread at cs 800 was 3.34x), or speak for the sign pattern
or for the network substrate.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the two sizes the replication runs, and the one the ladder was found at
REPLICATION_PREFIX = "e217_ladder_cs"
REFERENCE_SIZE = 800
#: the levels, in the ladder's own terms
LEVELS = {"real": 0, "alloy1": 1, "inalloy1": 1, "erdos_renyi": 2}
#: Z1's and Z2's registered boundaries
Z1_BARS = (1.5, 1.25)
Z2_BARS = (2.0, 1.5)

CLAIMS = (
    ("Z1", "the top step",
     "At each size, `erdos_renyi` analytic excess exceeds the LARGER of the two one-side nulls by at least 1.5x",
     "falsifier: within 1.25x at either size, i.e. no top step at that size and the ladder is cs-800-specific; "
     "null: 1.25-1.5x"),
    ("Z2", "the middle is ONE level",
     "At each size, the two one-side nulls' excesses differ by at most 2x",
     "falsifier: more than 2x apart at either size, which would say the two sides are not interchangeable and the "
     "ladder's middle is two levels rather than one; null: 1.5-2x"),
    ("Z3", "the floor",
     "At each size, `real` analytic excess is below BOTH one-side nulls",
     "falsifier: `real` at or above either one-side null at either size, which would say destroying one side can "
     "lower the penalty below the intact substrate's"),
)

#: the cs 800 reference: the levels' values as `e2_analytic`, `e213` and `e216` measured them
REFERENCE = {
    "real": ("e2_analytic.json", 0.01830),
    "alloy1": ("e213_alloy_draws_rs0..4.json (five drawings)", 0.05136),
    "inalloy1": ("e216_inalloy_rs0..2.json (three drawings)", 0.04668),
    "erdos_renyi": ("e2_analytic.json", 0.14187),
}


def penalty(block: dict) -> float | None:
    """The analytic diagonalisation excess of one topology block, or ``None`` where it was not computed."""
    v = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


def ladder(path: Path) -> dict:
    """One size's ladder: the four cells' penalties and the quantities the three claims turn on."""
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    tops = d.get("topologies") or {}
    vals = {t: penalty(b) for t, b in tops.items() if isinstance(b, dict)}
    vals = {t: v for t, v in vals.items() if v is not None and t in LEVELS}
    if set(vals) != set(LEVELS):
        return {}
    ones = [vals["alloy1"], vals["inalloy1"]]
    lo, hi = min(ones), max(ones)
    return {"artifact": path.name, "circuit_size": (d.get("config") or {}).get("circuit_size"),
            "penalties": vals, "one_side_ratio": hi / lo if lo else float("nan"),
            "top_step": vals["erdos_renyi"] / hi if hi else float("nan"),
            "floor_above": [name for name in ("alloy1", "inalloy1") if vals["real"] >= vals[name]]}


def sizes(directory: Path = RUNS) -> dict[int, dict]:
    """Every replication size whose artifact carries all four levels, keyed by circuit size."""
    out = {}
    for path in sorted(directory.glob(f"{REPLICATION_PREFIX}*.json")):
        m = re.search(r"cs(\d+)", path.name)
        row = ladder(path)
        if row and m:
            out[int(m.group(1))] = row
    return dict(sorted(out.items()))


def judge(rows: dict[int, dict]) -> list[dict]:
    """Z1-Z3 as verdicts, refused rather than guessed when a size the claims name is absent."""
    if not rows:
        return [{"id": c[0], "verdict": f"REFUSED -- no {REPLICATION_PREFIX}*.json artifact carries all four levels"}
                for c in CLAIMS]
    out = []
    tops = {s: r["top_step"] for s, r in rows.items()}
    met = [s for s, v in tops.items() if v >= Z1_BARS[0]]
    fired = [s for s, v in tops.items() if v < Z1_BARS[1]]
    out.append({"id": "Z1", "measured": ", ".join(f"cs{s} {v:.2f}x" for s, v in tops.items()),
                "verdict": "MET" if len(met) == len(tops) else
                           f"FALSIFIER FIRED at cs {fired[0]}" if fired else "null band"})
    mid = {s: r["one_side_ratio"] for s, r in rows.items()}
    # the registration named THREE outcomes for Z2 (MET within 2x, falsifier above it, and a null band between
    # Z2_BARS), and the first version of this judge implemented two of them -- the same defect the P1 reader was
    # fixed for, where a two-outcome reader calls a registered null a fired falsifier
    fired2 = [s for s, v in mid.items() if v >= Z2_BARS[0]]
    loose = [s for s, v in mid.items() if Z2_BARS[1] <= v < Z2_BARS[0]]
    out.append({"id": "Z2", "measured": ", ".join(f"cs{s} {v:.2f}x" for s, v in mid.items()),
                "verdict": "MET" if not fired2 and not loose else
                           f"FALSIFIER FIRED at cs {fired2[0]}" if fired2 else
                           f"null band at cs {loose[0]}"})
    bad = {s: r["floor_above"] for s, r in rows.items() if r["floor_above"]}
    out.append({"id": "Z3", "measured": f"real below both one-side nulls at "
                                        f"{len(rows) - len(bad)} of {len(rows)} size(s)",
                "verdict": "MET" if not bad else f"FALSIFIER FIRED at cs {sorted(bad)[0]}"})
    return out


def report(rows: dict[int, dict]) -> int:
    print("== the ladder at each circuit size ==")
    print(f"   {'level':<14}{'destroyed':>10}" + "".join(f"{'cs ' + str(s):>16}" for s in rows))
    for name in ("real", "alloy1", "inalloy1", "erdos_renyi"):
        cells = "".join(f"{rows[s]['penalties'][name]:>16.5f}" for s in rows)
        print(f"   {name:<14}{LEVELS[name]:>10}{cells}")
    print("\n   and the ladder the reference size measured (cs 800, quoted from its artifacts):")
    for name in ("real", "alloy1", "inalloy1", "erdos_renyi"):
        src, val = REFERENCE[name]
        print(f"   {name:<14}{LEVELS[name]:>10}{val:>16.5f}   {src}")
    print("\n   the two quantities the claims turn on:")
    for s, r in rows.items():
        print(f"      cs {s}: top step {r['top_step']:.2f}x (ER against the larger one-side null), "
              f"middle ratio {r['one_side_ratio']:.2f}x (the two one-side nulls), "
              f"floor {'ordered' if not r['floor_above'] else 'BROKEN by ' + ', '.join(r['floor_above'])}")
    print("\n== the registered claims, Z1-Z3 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(rows)):
        print(f"        {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"             the claim was: {c[2]}")
        print(f"             and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    return refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = sizes(args.runs)
    if args.json_out:
        write_json(args.json_out, {"sizes": rows, "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
