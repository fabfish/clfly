"""E234 -- does the PENALTY follow the task geometry? The excess curve against `e231`'s rank curve, at the same grid.

`e233` registered two claims before its runs and this is their reader:

- **E1**: at every step of `rho` in {0.7, 0.8, 0.9, 0.95, 0.98, 0.99} the analytic excess and `e231`'s
  `effective_rank` for the same (circuit size, topology) **both fall or both rise**;
- **E2**: at cs 300 the Erdős–Rényi ÷ `alloy1` excess ratio is **above 3×** at `rho` in {0.95, 0.98, 0.99}.

Three things make this reader more than a table. First, the two quantities come from **different instruments** --
the excess from the benchmark runner's analytic arm (minutes per cell), the rank from `e231`'s task-build-only
measurement -- so the merge is by (size, topology, `rho`) and every missing combination is a refusal rather than a
guess. Second, the rank exists at **nine** `rho` values and the excess at fewer, so the co-movement test runs on the
`rho` values where both are present, and says which those were. Third, the corpus's `rho = 0.9` cells are not one
artifact family: at cs 800 `alloy1` comes from `e212`/`e213`, `inalloy1` from `e216`, and `real`/`erdos_renyi` from
`e208`, so a per-family reference is assembled rather than assumed.

    python -m experiments.e234_read_penalty_curve
    python -m experiments.e234_read_penalty_curve --json-out runs/e234_read_penalty_curve.json

The exit code is the number of claims **REFUSED**, which is the honest state while the grid is partial: a verdict is
reported only where both instruments have measured the same cell.

**What it cannot do**: one drawing per cell for the excess (`e232` is measuring the rank's drawing scatter, and its
cs-300 lesson applies here too); a set of same-sign comparisons is not a regression and a shared direction is not a
shared cause; and the excess and the rank are both functions of `rho`, which moves depth and weight scale together.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments.e230_rank_draw_census import rows_of as corpus_geometry_rows

RUNS = Path("runs")
ONE_SIDE = ("alloy1", "inalloy1")
TOPOLOGIES = ("real", "alloy1", "inalloy1", "erdos_renyi")
#: the `rho` values the design is about, and the three E2 turns on
GRID = (0.7, 0.8, 0.9, 0.95, 0.98, 0.99)
E2_RHOS = (0.95, 0.98, 0.99)
E2_BAR = 3.0
#: E1's null band: same-sign everywhere but with the two quantities' relative changes differing by more than this
SCALE_FACTOR = 3.0

CLAIMS = (
    ("E1", "the penalty against the geometry",
     "At every step of rho the excess and the rank both fall or both rise, for every topology at both sizes",
     "falsifier: any step where one rises and the other falls; null: same-sign everywhere but with relative changes "
     "differing by more than 3x at some step (a shared direction without a shared scale)"),
    ("E2", "the two-side advantage at high rho",
     "At cs 300 the Erdos-Renyi over alloy1 excess ratio is above 3x at rho in {0.95, 0.98, 0.99}",
     "falsifier: any of the three points at or below 3x, which would make the advantage a one-point effect; null: "
     "above at some and below at others"),
)


def excess_of(block: dict) -> float | None:
    v = ((block.get("diagonal(EWC)") or {}).get("analytic") or {}).get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


def read(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None


def family_of(block: dict) -> str:
    """Which analytic implementation produced this block, read off the base names -- `e225`'s reading.

    It matters here because the `real` cell of the pooling runner and the `real` cell of the topology-gap runner are
    two QUANTITIES (`e225` declared the cross-family pair rather than counting it), and both carry
    `circuit_size 300, support 30, seeds 3, seed0 0, q 0.02` in their config, so a merge by config alone puts them in
    one cell.
    """
    names = set(block)
    if "bio:cell_class" in names:
        return "cell_class"
    if any(n.startswith("bio:pool") for n in names):
        return "pooling"
    return "unknown"


def excess_rows(root: Path = RUNS) -> list[dict]:
    """Every (size, topology, rho) the benchmark runner has an analytic excess for, with the artifact that has it."""
    out = []
    for p in sorted(glob.glob(str(root / "*.json"))):
        d = read(Path(p))
        if not d or not isinstance(d.get("config"), dict):
            continue
        cfg = d["config"]
        rho = cfg.get("rho", 0.9)
        rho = 0.9 if rho is None else float(rho)
        for topo, block in (d.get("topologies") or {}).items():
            v = excess_of(block) if isinstance(block, dict) else None
            if v is None:
                continue
            rw = cfg.get("rewire_seed")
            out.append({"size": cfg.get("circuit_size"), "topology": topo, "rho": rho, "excess": v,
                        "support": cfg.get("support"), "seeds": cfg.get("seeds"), "seed0": cfg.get("seed0"),
                        "q": cfg.get("q"), "rewire_seed": 0 if rw is None else int(rw),
                        "family": family_of(block), "artifact": Path(p).name})
    return out


def rank_rows(root: Path = RUNS) -> list[dict]:
    """Every (size, topology, rho) the geometry has a rank for: the corpus's blocks and `e231`'s own artifacts."""
    out = [{"size": r["circuit_size"], "topology": r["topology"], "rho": round(r["rho"], 4), "rank": r["rank"],
            "artifact": r["artifact"]} for r in corpus_geometry_rows(root)]
    for p in sorted(glob.glob(str(root / "e231_*.json"))):
        d = read(Path(p))
        if not d or "rows" not in d:
            continue
        for row in d["rows"]:
            for topo, cell in (row.get("topologies") or {}).items():
                rank = cell.get("effective_rank")
                if isinstance(rank, (int, float)):
                    out.append({"size": row.get("size"), "topology": topo, "rho": round(row.get("rho"), 4),
                                "rank": float(rank), "artifact": Path(p).name})
    return out


def curves(root: Path = RUNS) -> dict:
    """The two curves merged by (size, topology, rho), with every source named and every gap left as a gap."""
    merged: dict[tuple, dict] = {}
    by_cell: dict[tuple, list[dict]] = {}
    for r in excess_rows(root):
        by_cell.setdefault((r["size"], r["topology"], round(r["rho"], 4)), []).append(r)
    for key, rows in by_cell.items():
        # ONE CELL, ONE FAMILY, ONE DRAWING. Three ways this merge could quote something that is not the cell:
        # a second FAMILY under the same config (`e225`'s declared cross-family pair), a second DRAWING (the
        # `e219`/`e232` runs), and the last file winning by accident. The cell-class family and the seed0 drawing are
        # taken, and everything else is counted and printed rather than dropped.
        fam = [r for r in rows if r["family"] == "cell_class"] or rows
        seed0 = [r for r in fam if r["rewire_seed"] == 0]
        chosen = sorted(seed0 or fam, key=lambda r: r["artifact"])[0]
        merged[key] = {"size": chosen["size"], "topology": chosen["topology"], "rho": chosen["rho"],
                       "excess": chosen["excess"], "excess_from": chosen["artifact"],
                       "family": chosen["family"], "excess_drawings": len(rows),
                       "other_families": sorted({r["family"] for r in rows} - {chosen["family"]}),
                       "other_drawings": sorted(round(r["excess"], 6) for r in rows if r is not chosen)}
    for r in rank_rows(root):
        key = (r["size"], r["topology"], round(r["rho"], 4))
        merged.setdefault(key, {"size": r["size"], "topology": r["topology"], "rho": round(r["rho"], 4)})
        merged[key]["rank"] = r["rank"]
        merged[key]["rank_from"] = r["artifact"]
    return merged


def steps(merged: dict, size: int, topo: str, rhos=GRID) -> list[dict]:
    """The steps of the REGISTERED grid where both instruments measured this (size, topology).

    Restricted to `rhos` on purpose: the claim is about `rho` in {0.7 … 0.99} because the corpus already contains a
    sign disagreement at 0.5 to 0.9, so pairing the nearest available cells — which is what this function did first —
    judges the claim on a step it was written to exclude.
    """
    cells = [c for c in merged.values()
             if c["size"] == size and c["topology"] == topo and "rank" in c and "excess" in c
             and round(c["rho"], 4) in [round(r, 4) for r in rhos]]
    cells.sort(key=lambda c: c["rho"])
    out = []
    for a, b in zip(cells, cells[1:]):
        d_rank = b["rank"] - a["rank"]
        d_ex = b["excess"] - a["excess"]
        out.append({"from": a["rho"], "to": b["rho"],
                    "rank": (a["rank"], b["rank"]), "excess": (a["excess"], b["excess"]),
                    "rank_direction": (d_rank > 0) - (d_rank < 0),
                    "excess_direction": (d_ex > 0) - (d_ex < 0),
                    "rank_rel": abs(d_rank) / abs(a["rank"]) if a["rank"] else None,
                    "excess_rel": abs(d_ex) / abs(a["excess"]) if a["excess"] else None})
    return out


def judge(merged: dict) -> list[dict]:
    """E1-E2 as verdicts, REFUSED per claim while the cells that claim needs are absent."""
    out = []
    # E1: every (size, topology) needs at least two rho values carrying BOTH quantities
    per_family = {}
    for size in sorted({c["size"] for c in merged.values() if c["size"] in (300, 400, 800)}):
        for topo in TOPOLOGIES:
            st = steps(merged, size, topo)
            if st:
                per_family[(size, topo)] = st
    complete = {k: v for k, v in per_family.items() if len(v) == len(GRID) - 1}
    pending = {k: len(v) + 1 for k, v in per_family.items() if k not in complete}
    if not complete:
        out.append({"id": "E1", "verdict": "REFUSED -- no family covers the registered grid yet ("
                                           + ", ".join(f"{s}/{t} {n}/{len(GRID)} points"
                                                       for (s, t), n in sorted(pending.items(),
                                                                               key=lambda kv: (str(kv[0][0]),
                                                                                               kv[0][1]))[:6])
                                           + ")"})
        per_family = {}
    else:
        disagreements, scale_breaks, tested = [], [], []
        for (size, topo), st in sorted(per_family.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
            tested.append(f"{size}/{topo} ({len(st) + 1} points)")
            for s in st:
                if s["rank_direction"] and s["excess_direction"] and s["rank_direction"] != s["excess_direction"]:
                    disagreements.append(f"{size}/{topo} {s['from']} to {s['to']}")
                if s["rank_rel"] is not None and s["excess_rel"] and s["rank_rel"]:
                    ratio = max(s["rank_rel"], s["excess_rel"]) / max(min(s["rank_rel"], s["excess_rel"]), 1e-12)
                    if ratio > SCALE_FACTOR:
                        scale_breaks.append(f"{size}/{topo} {s['from']} to {s['to']} ({ratio:.1f}x)")
        verdict = (f"FALSIFIER FIRED -- the signs disagree at {disagreements}" if disagreements else
                   f"null band -- same sign everywhere but the scales differ by more than {SCALE_FACTOR:g}x at "
                   f"{scale_breaks}" if scale_breaks else "MET -- same sign and compatible scale at every step")
        out.append({"id": "E1", "measured": f"families with a step: {len(per_family)} ({', '.join(tested[:6])}"
                                            f"{' ...' if len(tested) > 6 else ''})",
                    "verdict": verdict})
    # E2: the ER/alloy1 excess ratio at the three high-rho points at cs 300
    ratios, missing = {}, []
    for rho in E2_RHOS:
        er = merged.get((300, "erdos_renyi", round(rho, 4)), {}).get("excess")
        al = merged.get((300, "alloy1", round(rho, 4)), {}).get("excess")
        if er is None or al in (None, 0):
            missing.append(rho)
        else:
            ratios[rho] = er / al
    if missing:
        out.append({"id": "E2", "verdict": f"REFUSED -- the excess is missing at cs 300 for rho {missing}"})
    else:
        below = [rho for rho, r in ratios.items() if r <= E2_BAR]
        verdict = (f"FALSIFIER FIRED -- at or below {E2_BAR:g}x at rho {below}" if below else
                   f"MET -- {min(ratios.values()):.1f}x to {max(ratios.values()):.1f}x, all above {E2_BAR:g}x")
        out.append({"id": "E2", "measured": ", ".join(f"{rho}: {r:.2f}x" for rho, r in sorted(ratios.items())),
                    "verdict": verdict})
    return out


def report(merged: dict) -> int:
    print("== the excess (benchmark runner) and the rank (e231), by (size, topology, rho) ==")
    for size in sorted({c["size"] for c in merged.values() if c["size"] in (300, 400, 800)}):
        print(f"\n   cs {size}")
        print(f"      {'topology':12} " + " ".join(f"{rho:>7.4g}" for rho in GRID))
        for topo in TOPOLOGIES:
            ranks, excesses = [], []
            for rho in GRID:
                c = merged.get((size, topo, round(rho, 4)), {})
                ranks.append(c.get("rank"))
                excesses.append(c.get("excess"))
            fmt = lambda v, w: " " * (w - 1) + "-" if v is None else f"{v:>{w}.4f}"
            print(f"      {topo:12} rank   " + " ".join(fmt(v, 7) for v in ranks))
            print(f"      {topo:12} excess " + " ".join(fmt(v, 7) for v in excesses))
    print("\n== the registered claims, E1-E2 ==")
    refused = 0
    for c, row in zip(CLAIMS, judge(merged)):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
        if "REFUSED" in row["verdict"]:
            refused += 1
    print("\n   (the two quantities come from different instruments and are merged by cell; a gap is printed as a")
    print("    gap, and one drawing per cell means a step can be a drawing's step as much as a rho's)")
    return refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    merged = curves(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": [merged[k] for k in sorted(merged, key=lambda k: (str(k[0]), k[1], k[2]))],
                                   "claims": judge(merged)})
        print(f"wrote {args.json_out}")
    return report(merged)


if __name__ == "__main__":
    sys.exit(main())
