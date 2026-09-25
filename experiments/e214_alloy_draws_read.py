"""E214 -- the alloy draws read: is the penalty's driver the fraction, or the alignment the fraction happens to produce?

`e212` put penalties inside the alignment hole for the first time and its two `alloy1` drawings disagreed by a factor
2.44x (+0.10067 at alignment 0.14179 against +0.04130 at 0.12815) while the Erdős–Rényi family spans 1.05x across
nine drawings. `e213` is the reply the registration names
(`docs/findings/2026-09-26-registered-five-drawings-at-two-alloy-fractions.md`): ten cells, full analytic mode, five
drawings at each of two fractions, so the penalty can be regressed on each drawing's MEASURED alignment rather than on
its requested fraction.

    python -m experiments.e214_alloy_draws_read
    python -m experiments.e214_alloy_draws_read --json-out runs/e214_alloy_draws_read.json

Three registered claims, quoted rather than restated:

  * **W1** -- at least three of the ten cells have alignment inside `[0.09101, 0.27135]`; falsifier fewer than three,
    which would say the top of this family scatters around the band's floor and reaching the interior needs a THIRD
    construction;
  * **W2** -- the two fractions' five-drawing means differ by at least **1.5x** the larger within-fraction range;
    falsifier a difference **smaller than** that range, i.e. the requested fraction tells you nothing once the drawing
    is accounted for, which would make the alloy a good instrument for PLACING alignment and a poor one for measuring
    its consequence;
  * **W3** -- the Spearman rank correlation between the ten cells' measured alignment and their penalty is at least
    **+0.5**; falsifier at or below **0**, which would say the regime structure is a property of the constructions'
    NAMES rather than of the alignment they produce.

The three are read together on purpose: **W2 and W3 can disagree, and that disagreement is the interesting outcome** --
a fraction effect smaller than the drawing noise with a strong alignment correlation says the *alignment* is the
variable to index by and the fraction is only a means of producing it.

**What it cannot do**: separate alignment from `top_eig_share` and `effective_rank` (the alloy moves all three),
reach the upper half of the hole `[0.20, 0.271]` (`alloy1` is this family's ceiling), give a distribution (five
drawings per fraction are a range and not an sd), or speak for other circuit sizes and task draws.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
PREFIX = "e213_alloy_draws_rs"
#: the registered size of the design and the hole it is stated against
EXPECTED_CELLS = 10
BAND = (0.09101, 0.27135)
W2_RATIO_BAR = 1.5
W3_RHO_BAR = 0.5

CLAIMS = (
    ("W1", "the band is populated",
     "At least three of the ten cells have alignment inside [0.09101, 0.27135]",
     "falsifier: fewer than three, which would say the top of this family scatters around the band's floor and that "
     "reaching the interior needs the third construction; null: exactly two"),
    ("W2", "the fraction effect is larger than the drawing effect",
     "The mean excess of the five alloy1 drawings differs from the mean of the five alloy0.9 drawings by at least 1.5x "
     "the larger of the two within-fraction ranges",
     "falsifier: a difference SMALLER than the larger within-fraction range, i.e. the requested fraction tells you "
     "nothing once the drawing is accounted for; null: 1.0-1.5x the range"),
    ("W3", "the penalty tracks measured alignment across drawings",
     "The Spearman rank correlation between the ten cells' measured `all_pairs_alignment` and their analytic excess is "
     "at least +0.5",
     "falsifier: at or below 0, which would say the two quantities are unrelated across drawings and that the regime "
     "structure is a property of the constructions' names rather than of the alignment they produce; null: 0 to +0.5"),
)


def fraction_of(topology: str) -> float | None:
    """The alloy fraction a topology name carries, or ``None`` for one that names none."""
    m = re.fullmatch(r"alloy([0-9.]+)", topology)
    return float(m.group(1)) if m else None


def rank(values: list[float]) -> list[float]:
    """Average ranks, so a tie cannot manufacture an ordering."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def pearson(a: list[float], b: list[float]) -> float:
    """Pearson's r, or ``nan`` when either side is constant."""
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    sa = sum(x * x for x in da) ** 0.5
    sb = sum(x * x for x in db) ** 0.5
    if sa == 0 or sb == 0:
        return float("nan")
    return sum(x * y for x, y in zip(da, db)) / (sa * sb)


def cells(directory: Path = RUNS) -> list[dict]:
    """Every (artifact, topology) cell the design wrote, with its measured alignment and its penalty."""
    out = []
    for path in sorted(directory.glob(f"{PREFIX}*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        seed = (d.get("config") or {}).get("rewire_seed")
        for topology, block in (d.get("topologies") or {}).items():
            if not isinstance(block, dict):
                continue
            geom = block.get("geometry") or {}
            arm = ((block.get("diagonal(EWC)") or {}).get("analytic")) or {}
            a = geom.get("all_pairs_alignment")
            p = arm.get("excess_mean")
            if a is None or p is None:
                continue
            chance = geom.get("chance_alignment") or float("nan")
            out.append({"artifact": path.name, "rewire_seed": seed, "topology": topology,
                        "fraction": fraction_of(topology), "alignment": float(a), "chance": float(chance),
                        "ratio": float(a) / float(chance) if chance else float("nan"),
                        "excess": float(p), "sem": arm.get("excess_sem"),
                        "top_eig_share": geom.get("top_eig_share"),
                        "effective_rank": geom.get("effective_rank")})
    return out


def by_fraction(rows: list[dict]) -> dict[float, list[dict]]:
    groups: dict[float, list[dict]] = {}
    for r in rows:
        if r["fraction"] is not None:
            groups.setdefault(r["fraction"], []).append(r)
    return dict(sorted(groups.items()))


def judge(rows: list[dict]) -> list[dict]:
    """W1-W3 as verdicts, refused rather than guessed when the cells a sentence names are absent."""
    if not rows:
        return [{"id": c[0], "verdict": f"REFUSED -- no {PREFIX}*.json cell carries both an alignment and a penalty"}
                for c in CLAIMS]
    if len(rows) < EXPECTED_CELLS:
        return [{"id": c[0], "verdict": f"REFUSED -- the design is registered at {EXPECTED_CELLS} cells and "
                                        f"{len(rows)} are on disk, so a verdict now would be about a partial design"}
                for c in CLAIMS]
    out: list[dict] = []
    inside = [r for r in rows if BAND[0] <= r["alignment"] <= BAND[1]]
    out.append({"id": "W1", "measured": f"{len(inside)} of {len(rows)} cells inside [{BAND[0]}, {BAND[1]}]",
                "verdict": "MET" if len(inside) >= 3 else "FALSIFIER FIRED"})
    groups = by_fraction(rows)
    if len(groups) != 2 or any(len(g) < 2 for g in groups.values()):
        out.append({"id": "W2", "verdict": "REFUSED -- the claim names two fractions with five drawings each"})
    else:
        means = {f: sum(r["excess"] for r in g) / len(g) for f, g in groups.items()}
        ranges = {f: max(r["excess"] for r in g) - min(r["excess"] for r in g) for f, g in groups.items()}
        lo, hi = sorted(means)
        diff = means[hi] - means[lo]
        wider = max(ranges.values())
        worst = max(ranges, key=lambda f: ranges[f])
        out.append({"id": "W2",
                    "measured": f"means {means[hi]:.5f} (alloy{hi:g}) against {means[lo]:.5f} (alloy{lo:g}), "
                                f"difference {diff:.5f} = {diff / wider:.2f}x the wider range "
                                f"({wider:.5f}, alloy{worst:g})",
                    "verdict": "MET" if diff >= W2_RATIO_BAR * wider else
                               "FALSIFIER FIRED" if diff < wider else "null band"})
    a = [r["alignment"] for r in rows]
    p = [r["excess"] for r in rows]
    rho = pearson(rank(a), rank(p))
    out.append({"id": "W3", "measured": f"Spearman(alignment, excess) = {rho:+.3f} over {len(rows)} cells",
                "verdict": "MET" if rho >= W3_RHO_BAR else "FALSIFIER FIRED" if rho <= 0 else "null band"})
    return out


def report(rows: list[dict]) -> int:
    if not rows:
        for c in CLAIMS:
            print(f"   {c[0]}: REFUSED -- no {PREFIX}*.json cell carries both an alignment and a penalty")
        return 0
    print("== the ten alloy cells: measured alignment against penalty ==")
    print(f"   {'drawing':<28}{'cell':<11}{'alignment':>10}{'x chance':>10}{'excess':>10}{'sem':>9}"
          f"{'top_eig':>9}{'eff rank':>9}")
    for r in sorted(rows, key=lambda r: r["alignment"]):
        print(f"   {r['artifact']:<28}{r['topology']:<11}{r['alignment']:>10.5f}{r['ratio']:>9.2f}x"
              f"{r['excess']:>+10.5f}{(r['sem'] or float('nan')):>9.5f}"
              f"{(r['top_eig_share'] or float('nan')):>9.3f}{(r['effective_rank'] or float('nan')):>9.2f}")
    for f, g in by_fraction(rows).items():
        ex = [r["excess"] for r in g]
        al = [r["alignment"] for r in g]
        print(f"   alloy{f:<5g} n={len(g)}  excess mean {sum(ex) / len(ex):.5f} range "
              f"{min(ex):.5f}-{max(ex):.5f} (span {max(ex) - min(ex):.5f}, ratio "
              f"{max(ex) / max(min(ex), 1e-12):.2f}x)  alignment {min(al):.5f}-{max(al):.5f} "
              f"({min(al) / max(al):.2f}x)")
    print("\n== the registered claims, W1-W3 ==")
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
    rows = cells(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": rows, "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
