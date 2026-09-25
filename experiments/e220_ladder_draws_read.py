"""E220 -- the ladder's levels read drawing by drawing, because a single drawing is not a level.

`e217` ran the ladder at cs 300 and cs 400 with **one drawing per cell** and reported that its top step is a cs-800
property (1.28x at cs 300, 1.08x at cs 400, against 2.76x/3.02x) while its middle level and floor replicate. The
asymmetry that verdict carried is the reason for this design and for this reader: **cs 800's levels are five- and
three-drawing means** (`alloy1` from `e213`, `inalloy1` from `e216`) **while cs 300 and cs 400 are one drawing each**,
and the alloy's own five-drawing spread at cs 800 was **3.34x** — so a single drawing's ratio could be a drawing.

`e219` re-runs the three levels the ratios need at **three realizations per size**, and this reader decides the two
registered claims per size and reports the spread:

    python -m experiments.e220_ladder_draws_read
    python -m experiments.e220_ladder_draws_read --json-out runs/e220_ladder_draws_read.json

  * **R1 -- the cs-800 top step is absent at both sizes, drawing by drawing**: at each size the **mean** top step over
    the three drawings is below **1.5x** and **no single drawing reaches 2.0x**. Falsifier: a mean at or above 1.5x or
    any drawing at or above 2.0x, which would mean the top step IS present at these sizes and `e217`'s verdict was a
    drawing artifact. Null: a mean below 1.5x with one drawing between 1.5x and 2.0x.
  * **R2 -- the middle level's agreement is per-drawing**: at each size, in **every** drawing the two one-side nulls
    agree within **2x**. Falsifier: any drawing beyond 2x. Null: a mean within 2x with one drawing beyond it.
  * **R3 -- reported**: at each size the three drawings' **range** for each level and for the top step, beside cs
    800's own spreads, since the spread is what this design exists to measure.

**What it cannot do**: separate the support fraction from the circuit size (held at the 10%-of-circuit convention),
give a quoted sd (three drawings are a range), give cs 800 equal treatment (its levels have five and three drawings
from other designs rather than three from this one), or speak for the sign pattern and the network substrate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
PREFIX = "e219_draws_cs"
#: the three levels the ratios need, and the two one-side ones
LEVELS = ("alloy1", "inalloy1", "erdos_renyi")
ONE_SIDE = ("alloy1", "inalloy1")
#: how many drawings per size the design registered
EXPECTED_DRAWINGS = 3
#: R1's and R2's registered boundaries
R1_BARS = (1.5, 2.0)
R2_BAR = 2.0
#: cs 800's levels and spreads, quoted from the artifacts that measured them
REFERENCE = {
    "levels": {"alloy1": 0.05136, "inalloy1": 0.04668, "erdos_renyi": 0.14187},
    "spreads": {"alloy1": "3.34x over five drawings", "inalloy1": "1.24x over three",
                "erdos_renyi": "1.05x over nine"},
    "top_step": "2.76x / 3.02x",
}

CLAIMS = (
    ("R1", "the cs-800 top step is absent at both sizes, drawing by drawing",
     "At each size, the mean top step over the three drawings is below 1.5x and no single drawing reaches 2.0x",
     "falsifier: a mean at or above 1.5x or any drawing at or above 2.0x, which would mean the top step IS present "
     "at these sizes and e217's verdict was a drawing artifact; null: a mean below 1.5x with one drawing between "
     "1.5x and 2.0x"),
    ("R2", "the middle level's agreement is per-drawing",
     "At each size, in every drawing the two one-side nulls agree within 2x",
     "falsifier: any drawing more than 2x apart, which would say the one-level middle is a mean artifact and the two "
     "sides are not interchangeable at every drawing; null: a mean within 2x with one drawing beyond it"),
)


def penalty(block: dict) -> float | None:
    """The analytic diagonalisation excess of one topology block, or ``None`` when it was not computed."""
    v = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


def drawings(directory: Path = RUNS) -> dict[int, list[dict]]:
    """Every drawing, grouped by circuit size, each with its levels and its two ratios."""
    out: dict[int, list[dict]] = {}
    for path in sorted(directory.glob(f"{PREFIX}*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        cs = (d.get("config") or {}).get("circuit_size")
        vals = {t: penalty(b) for t, b in (d.get("topologies") or {}).items() if isinstance(b, dict)}
        vals = {t: v for t, v in vals.items() if v is not None and t in LEVELS}
        if cs is None or set(vals) != set(LEVELS):
            continue
        ones = [vals[t] for t in ONE_SIDE]
        hi = max(ones)
        out.setdefault(int(cs), []).append(
            {"artifact": path.name, "rewire_seed": (d.get("config") or {}).get("rewire_seed"),
             "levels": vals, "top_step": vals["erdos_renyi"] / hi if hi else float("nan"),
             "middle_ratio": hi / min(ones) if min(ones) else float("nan")})
    return dict(sorted(out.items()))


def judge(by_size: dict[int, list[dict]]) -> list[dict]:
    """R1-R2 as verdicts, refused rather than guessed when a size the claims name is short of its three drawings."""
    if not by_size:
        return [{"id": c[0], "verdict": f"REFUSED -- no {PREFIX}*.json artifact carries all three levels"}
                for c in CLAIMS]
    short = {s: len(d) for s, d in by_size.items() if len(d) < EXPECTED_DRAWINGS}
    if short:
        return [{"id": c[0], "verdict": f"REFUSED -- the design registers {EXPECTED_DRAWINGS} drawings per size and "
                                        f"cs {sorted(short)[0]} has {short[sorted(short)[0]]}"} for c in CLAIMS]
    out = []
    means = {s: sum(d["top_step"] for d in rows) / len(rows) for s, rows in by_size.items()}
    worst = {s: max(d["top_step"] for d in rows) for s, rows in by_size.items()}
    high = [s for s in means if means[s] >= R1_BARS[0] or worst[s] >= R1_BARS[1]]
    loose = [s for s in means if not (means[s] >= R1_BARS[0] or worst[s] >= R1_BARS[1]) and worst[s] >= R1_BARS[0]]
    out.append({"id": "R1",
                "measured": ", ".join(f"cs{s} mean {means[s]:.2f}x worst {worst[s]:.2f}x" for s in by_size),
                "verdict": "MET" if not high and not loose else
                           f"FALSIFIER FIRED at cs {high[0]}" if high else f"null band at cs {loose[0]}"})
    mmeans = {s: sum(d["middle_ratio"] for d in rows) / len(rows) for s, rows in by_size.items()}
    mworst = {s: max(d["middle_ratio"] for d in rows) for s, rows in by_size.items()}
    fired = [s for s in mworst if mworst[s] > R2_BAR]
    out.append({"id": "R2",
                "measured": ", ".join(f"cs{s} mean {mmeans[s]:.2f}x worst {mworst[s]:.2f}x" for s in by_size),
                "verdict": "MET" if not fired else f"FALSIFIER FIRED at cs {fired[0]}"})
    return out


def report(by_size: dict[int, list[dict]]) -> int:
    print("== the ladder's levels, drawing by drawing ==")
    for cs, rows in by_size.items():
        print(f"   cs {cs}:")
        for d in sorted(rows, key=lambda r: r["rewire_seed"] if r["rewire_seed"] is not None else -1):
            lv = d["levels"]
            print(f"      seed {d['rewire_seed']}: alloy1 {lv['alloy1']:.5f}  inalloy1 {lv['inalloy1']:.5f}  "
                  f"erdos_renyi {lv['erdos_renyi']:.5f}   top step {d['top_step']:.2f}x  "
                  f"middle {d['middle_ratio']:.2f}x")
        for name in LEVELS:
            vals = [d["levels"][name] for d in rows]
            print(f"      {name:<12} range {min(vals):.5f}-{max(vals):.5f} "
                  f"(span {max(vals) - min(vals):.5f}, ratio {max(vals) / max(min(vals), 1e-12):.2f}x)")
        tops = [d["top_step"] for d in rows]
        print(f"      top step     range {min(tops):.2f}x-{max(tops):.2f}x")
    print(f"\n   and the reference size (cs 800), quoted from the artifacts that measured it: "
          f"top step {REFERENCE['top_step']}, levels " +
          ", ".join(f"{k} {v:.5f}" for k, v in REFERENCE["levels"].items()))
    print("   spreads there: " + "; ".join(f"{k} {v}" for k, v in REFERENCE["spreads"].items()))
    print("\n== the registered claims, R1-R2 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(by_size)):
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
    got = drawings(args.runs)
    if args.json_out:
        write_json(args.json_out, {"sizes": {str(k): v for k, v in got.items()}, "claims": judge(got)})
        print(f"wrote {args.json_out}")
    return report(got)


if __name__ == "__main__":
    sys.exit(main())
