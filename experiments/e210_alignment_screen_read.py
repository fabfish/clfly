"""E210 -- the alignment screen's three claims, read from the cells it wrote and from nothing else.

`e208` left C3's transition in [0.09101, 0.27135] with one cell at its bottom edge, and showed why adding swap
strengths cannot fill that interval: its three new levels are not ordered in alignment, because alignment at a FIXED
strength spreads 2.60x across realizations at `swap2`. The registered answer
(`docs/findings/2026-09-26-registered-screening-by-alignment-then-paying-for-the-band.md`) is a two-stage design --
**screen by alignment, then pay for the cells that land in the band** -- and `e209` is its first stage: twenty cells
of (swap strength x realization), each measured in the runner's `--geometry-only` mode, which writes the `geometry`
block and skips all three arms.

    python -m experiments.e210_alignment_screen_read
    python -m experiments.e210_alignment_screen_read --json-out runs/e210_alignment_screen_read.json

This reader holds the three registered sentences and decides them:

  * **S1** -- every screen cell has an alignment and NO arm, and the twenty together cost under 45 min;
  * **S2** -- at least one cell's alignment lies in **`[0.09101, 0.27135]`**; its falsifier is *none does*, which
    would say the alignment distribution of the swap family at high strength sits **below** the Erdos-Renyi family's
    and the transition must be approached by mixing topologies rather than by rewiring further;
  * **S3** -- at a fixed strength the alignment span is at least **1.5x** in ratio for at least two of the four
    strengths (`swap2`'s ratio is 2.60x); its falsifier is *no strength above 1.5x*, which would rehabilitate the
    strength axis as an x-axis.

**What it cannot do**: the screen has no arms, so nothing here is a penalty -- the band cells it names are a
SHOPPING LIST for stage 2, which pays 225 s per cell for a full analytic measurement. It also cannot separate
alignment from `top_eig_share` and `effective_rank`, which move with the swap operation by construction, or speak for
task draws other than `seed0`'s or circuit sizes other than the one the screen ran at.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

RUNS = Path("runs")
#: the screen's artifact family, one file per swap realization
PREFIX = "e209_screen_rs"
#: the hole, quoted from the registration, as its two measured edges rather than a round figure
BAND = (0.09101, 0.27135)
#: S3's bar
SPREAD_BAR = 1.5
#: S1's registered ceiling, in seconds
SCREEN_BUDGET_S = 45 * 60
#: the registered size of the screen: four strengths x five realizations. The claims are stated over the WHOLE
#: screen, so a partial read is refused -- reading 8 of 20 cells as if they were 20 is the neighbouring-subject
#: defect this project keeps finding, and it is the one thing a reader can get wrong while every number is right.
EXPECTED_CELLS = 20

#: (id, subject, the registered sentence, the falsifier) -- quoted, never restated
CLAIMS = (
    ("S1", "the screen is affordable and lands where it says",
     "Every screen cell has `geometry.all_pairs_alignment` written and no `analytic` arm; the twenty cells together "
     "cost under 45 min",
     "falsifier: a cell carrying an arm (which would make it a stage-2 measurement, not a screen), a cell with no "
     "alignment, or a total above the registered ceiling"),
    ("S2", "the band is reachable by the swap operation at cs 800",
     "At least one of the twenty cells has alignment in [0.09101, 0.27135]",
     "falsifier: none does, which would say the swap family's alignment distribution at high strength sits BELOW the "
     "Erdos-Renyi family's (0.27135-0.29039) and the band cannot be sampled this way at all"),
    ("S3", "the spread at high strength is the same order as at swap2",
     "Across the five realizations at a fixed strength, the alignment span is at least 1.5x in ratio for at least two "
     "of the four strengths",
     "falsifier: no strength has a ratio above 1.5x, which would say the spread is a property of the LOW end of the "
     "family and that one realization per strength is adequate at the high end"),
)


def strength_of(topology: str) -> float | None:
    """The strength a `swapN` topology names, or ``None`` for one that names no strength."""
    rest = topology[4:] if topology.startswith("swap") else ""
    try:
        return float(rest)
    except ValueError:
        return None


def screen_cells(directory: Path = RUNS) -> list[dict]:
    """Every (artifact, topology) cell the screen wrote, with the arm presence that S1 turns on."""
    out = []
    for path in sorted(directory.glob(f"{PREFIX}*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for topology, block in (d.get("topologies") or {}).items():
            if not isinstance(block, dict):
                continue
            geom = block.get("geometry") or {}
            alignment = geom.get("all_pairs_alignment")
            if alignment is None:
                continue
            chance = geom.get("chance_alignment") or float("nan")
            out.append({"artifact": path.name, "topology": topology, "strength": strength_of(topology),
                        "artifact_seconds": duration_seconds(d),   # through the helper: `e205` reads every raw duration key in the tree
                        "alignment": float(alignment), "chance": float(chance),
                        "ratio": float(alignment) / float(chance) if chance else float("nan"),
                        "top_eig_share": geom.get("top_eig_share"),
                        "effective_rank": geom.get("effective_rank"),
                        "has_arm": any(isinstance(block.get(k), dict) for k in
                                       ("diagonal(EWC)", "bio:cell_class", "rand:cell_class"))})
    return out


def by_strength(rows: list[dict]) -> dict[float, list[dict]]:
    """The cells grouped by swap strength, in ascending strength order."""
    groups: dict[float, list[dict]] = {}
    for r in rows:
        if r["strength"] is not None:
            groups.setdefault(r["strength"], []).append(r)
    return dict(sorted(groups.items()))


def judge(rows: list[dict], budget_s: float | None = None) -> list[dict]:
    """S1-S3 as verdicts, refused rather than guessed when the cells a sentence names are absent."""
    if not rows:
        return [{"id": c[0], "verdict": f"REFUSED -- no {PREFIX}*.json cell carries a geometry block"} for c in CLAIMS]
    if len(rows) < EXPECTED_CELLS:
        return [{"id": c[0], "verdict": f"REFUSED -- the screen is registered at {EXPECTED_CELLS} cells and "
                                        f"{len(rows)} are on disk, so a verdict now would be about a partial design"}
                for c in CLAIMS]
    out: list[dict] = []
    armed = [r for r in rows if r["has_arm"]]
    spent = sum(v for v in {r["artifact"]: r.get("artifact_seconds") or 0.0 for r in rows}.values())
    over = budget_s is not None and spent > budget_s
    out.append({"id": "S1", "measured": f"{len(rows)} cells, {len(armed)} carrying an arm, "
                                        f"{spent / 60:.1f} min of run time" if spent else
                                        f"{len(rows)} cells, {len(armed)} carrying an arm",
                "verdict": ("MET" if not armed and not over else
                            f"FALSIFIER FIRED -- {len(armed)} cell(s) carry an arm" if armed else
                            f"FALSIFIER FIRED -- {spent:.0f} s above the registered {budget_s:.0f} s")})
    inside = [r for r in rows if BAND[0] <= r["alignment"] <= BAND[1]]
    out.append({"id": "S2", "measured": f"{len(inside)} cell(s) in [{BAND[0]}, {BAND[1]}]",
                "verdict": "MET" if inside else "FALSIFIER FIRED"})
    groups = by_strength(rows)
    wide = {s: (max(r["alignment"] for r in g) / min(r["alignment"] for r in g)) for s, g in groups.items()}
    enough = [s for s, ratio in wide.items() if ratio >= SPREAD_BAR]
    out.append({"id": "S3",
                "measured": "ratios: " + ", ".join(f"swap{s:g} {v:.2f}x" for s, v in wide.items()),
                "verdict": ("MET" if len(enough) >= 2 else "FALSIFIER FIRED")
                if len(groups) == 4 and all(len(g) >= 2 for g in groups.values()) else
                f"REFUSED -- {len(groups)} strength(s) with all realizations present, and the claim is over four"})
    return out


def report(rows: list[dict], budget_s: float | None = None) -> int:
    if not rows:
        for c in CLAIMS:
            print(f"   {c[0]}: REFUSED -- no {PREFIX}*.json cell carries a geometry block (an absent artifact is not "
                  f"a fired falsifier)")
        return 0
    print("== the screen: alignment by (strength x realization) ==")
    for s, group in by_strength(rows).items():
        alignments = ", ".join(f"{r['alignment']:.5f}" for r in sorted(group, key=lambda x: x["artifact"]))
        ratio = max(r["alignment"] for r in group) / max(min(r["alignment"] for r in group), 1e-12)
        print(f"   swap{s:<4g} n={len(group):<2} {alignments}   span {ratio:.2f}x")
    print(f"   and {len([r for r in rows if r['strength'] is None])} cell(s) naming no strength")
    print("\n== the band, and the stage-2 shopping list ==")
    print(f"   the hole is [{BAND[0]}, {BAND[1]}] (the largest in-axis alignment and the smallest high-regime one)")
    inside = [r for r in rows if BAND[0] <= r["alignment"] <= BAND[1]]
    for r in sorted(inside, key=lambda x: x["alignment"]):
        print(f"      IN BAND  {r['artifact']:<28}{r['topology']:<10}{r['alignment']:.5f} "
              f"({r['ratio']:.2f}x chance)  top_eig {r['top_eig_share']:.3f}  rank {r['effective_rank']:.2f}")
    if not inside:
        print("      none -- S2's falsifier; the transition cannot be sampled by rewiring further at this circuit size")
    print("\n== the screen's registered claims, S1-S3 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(rows, budget_s)):
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
    rows = screen_cells(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": rows, "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
