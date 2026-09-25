"""E207 -- what the penalty tracks: every geometry statistic the swap family records, joined to the penalty at every circuit size.

C3 is the plan's only claim with no measurement behind it -- *"interpolating the connectome toward a random graph by
densifying cross-module edges increases forgetting monotonically"* -- and its status note says the mechanism it assumed
(task interference) was refuted and that what remains *"is not yet well enough understood to state as a testable
prediction"*. The plan also records what the penalty does **not** track: across the degree-preserving swap family the
gap moves *opposite* to task overlap.

What nobody had done is the join that the record already contains. Every topology in the swap family is written with a
``geometry`` block -- eight measured statistics of the task subspaces, including how far from orthogonal they are
(``all_pairs_alignment`` against ``chance_alignment``), the effective rank, and the share of the top eigenvalue -- and
the same artifact carries the diagonalisation penalty for that topology. So *which of the measured geometry statistics
does the penalty track?* is a question the record can answer without running anything, at every circuit size it holds.

    python -m experiments.e207_penalty_driver_join
    python -m experiments.e207_penalty_driver_join --json-out runs/e207_penalty_driver_join.json

## Why rank correlation, and why the outlier is named

The Erdős-Rényi topology is a different regime: its penalty is **7.7x** the next largest at the same circuit size and
its alignment is 3.5x the next largest, so a Pearson coefficient across a five-topology family is mostly a statement
about one point (``r = +0.97`` for alignment, against a rank correlation of ``+0.40``). Both are printed, the
rank-based one decides, and the Pearson-with-ER-removed is printed beside them so the outlier's leverage is visible
rather than argued about.

## What it cannot do

It reports an association across a family of topologies, each measured once, at three to five points per circuit size --
so the signs are descriptive and a flip is a flip and not a trend. It cannot say which statistic *causes* the penalty,
cannot separate the statistics from each other (alignment, effective rank and the top eigenvalue's share move together
along a swap axis by construction), and cannot speak for the network substrate, whose penalty is measured by a
different instrument entirely.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: the arm whose analytic penalty is the quantity under study
PENALTY_ARM = "diagonal(EWC)"
#: the topology that is a regime rather than a point on the axis, named so its leverage can be removed and shown
OUTLIER = "erdos_renyi"


def penalty_of(block: dict) -> float | None:
    """The arm's analytic ``excess_mean`` for one topology, or ``None`` when the artifact did not compute it."""
    arm = block.get(PENALTY_ARM)
    if not isinstance(arm, dict):
        return None
    analytic = arm.get("analytic")
    if not isinstance(analytic, dict):
        return None
    v = analytic.get("excess_mean")
    return float(v) if isinstance(v, (int, float)) else None


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
    """Pearson's r, or ``nan`` when either side is constant -- a constant has no association to report."""
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    da = [x - ma for x in a]
    db = [x - mb for x in b]
    sa = math.sqrt(sum(x * x for x in da))
    sb = math.sqrt(sum(x * x for x in db))
    if sa == 0 or sb == 0:
        return float("nan")
    return sum(x * y for x, y in zip(da, db)) / (sa * sb)


def spearman(a: list[float], b: list[float]) -> float:
    """The rank correlation, which is the one that decides because the family is three to five points wide."""
    return pearson(rank(a), rank(b))


def cells(directory: Path = RUNS) -> list[dict]:
    """Every (artifact, topology) pair carrying both a geometry block and an analytic penalty."""
    out = []
    for path in sorted(directory.glob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        tops = d.get("topologies")
        if not isinstance(tops, dict):
            continue
        cfg = d.get("config") or {}
        for name, block in tops.items():
            if not isinstance(block, dict):
                continue
            geom = block.get("geometry")
            p = penalty_of(block)
            if not isinstance(geom, dict) or p is None:
                continue
            out.append({"artifact": path.name, "topology": name, "penalty": p,
                        "circuit_size": cfg.get("circuit_size"), "geometry": geom})
    return out


def by_artifact(rows: list[dict]) -> dict[str, list[dict]]:
    """The cells grouped by the artifact that computed them, in the order the artifacts were written."""
    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(r["artifact"], []).append(r)
    return groups


def associations(group: list[dict]) -> dict:
    """Per geometry statistic, its rank and linear association with the penalty inside one artifact's family."""
    stats = sorted({k for r in group for k in r["geometry"]})
    pen = [r["penalty"] for r in group]
    out: dict[str, dict] = {}
    for s in stats:
        vals = [r["geometry"].get(s) for r in group]
        if any(not isinstance(v, (int, float)) for v in vals):
            continue
        keep = [i for i, v in enumerate(vals) if isinstance(v, (int, float))]
        xs = [vals[i] for i in keep]
        ys = [pen[i] for i in keep]
        without = [i for i in keep if group[i]["topology"] != OUTLIER]
        out[s] = {"rho": spearman(xs, ys), "r": pearson(xs, ys),
                  "r_without_outlier": (pearson([vals[i] for i in without], [pen[i] for i in without])
                                        if len(without) >= 3 else float("nan")),
                  "values": xs, "penalty": ys, "n": len(xs),
                  "topologies": [group[i]["topology"] for i in keep],
                  "constant": len(set(xs)) == 1}
    return out


def regime(rows: list[dict], statistic: str = "all_pairs_alignment") -> list[dict]:
    """Every cell as (alignment, penalty), sorted -- the view a threshold shows up in and a correlation hides.

    A graded association and a threshold look the same to a correlation over four points; they do not look the same
    sorted, which is why this table is printed beside the coefficients.
    """
    out = []
    for r in rows:
        v = r["geometry"].get(statistic)
        if isinstance(v, (int, float)):
            out.append({"alignment": float(v), "penalty": r["penalty"], "topology": r["topology"],
                        "artifact": r["artifact"], "chance": r["geometry"].get("chance_alignment")})
    return sorted(out, key=lambda x: x["alignment"])


def report(rows: list[dict]) -> int:
    if not rows:
        print("   no (artifact, topology) cell carries both a geometry block and an analytic penalty -- refused")
        return 0
    groups = by_artifact(rows)
    sizes = sorted({r["circuit_size"] for r in rows if r["circuit_size"] is not None})
    print("== the join ==")
    print(f"   artifacts carrying both: {len(groups)}; cells: {len(rows)}; circuit sizes: {sizes}")
    print(f"   topologies per artifact: "
          + ", ".join(f"{a} {len(g)}" for a, g in groups.items()))

    print("\n== does the penalty track the geometry? rank association inside each artifact's family ==")
    tally: dict[str, list[float]] = {}
    for art, group in groups.items():
        assoc = associations(group)
        kept = [s for s, a in assoc.items() if not a["constant"] and not math.isnan(a["rho"])]
        print(f"\n   {art} (cs {group[0]['circuit_size']}, {len(group)} topologies: "
              f"{', '.join(r['topology'] for r in group)})")
        for s in kept:
            a = assoc[s]
            tally.setdefault(s, []).append(a["rho"])
            print(f"      {s:<22} rho {a['rho']:+.3f}   r {a['r']:+.3f}   (r without {OUTLIER}: "
                  f"{a['r_without_outlier']:+.3f})")
        const = [s for s, a in assoc.items() if a["constant"]]
        if const:
            print(f"      constant across the family (no association to report): {', '.join(const)}")

    print("\n== the tally across artifacts: how many families agree in sign ==")
    print(f"   {'statistic':<24}{'families':>9}{'positive':>10}{'negative':>10}   signs")
    for s, rhos in sorted(tally.items(), key=lambda kv: -len(kv[1])):
        pos = sum(1 for x in rhos if x > 0)
        neg = sum(1 for x in rhos if x < 0)
        print(f"   {s:<24}{len(rhos):>9}{pos:>10}{neg:>10}   " + " ".join(f"{x:+.1f}" for x in rhos))

    print("\n== the same cells, sorted by alignment: a threshold is invisible to a correlation ==")
    reg = regime(rows)
    flat = [c for c in reg if c["alignment"] < 0.12]
    high = [c for c in reg if c["alignment"] >= 0.12]
    print(f"   {'alignment':>11}{'x chance':>10}{'penalty':>10}  topology (artifact)")
    for c in reg:
        ratio = (c["alignment"] / c["chance"]) if c["chance"] else float("nan")
        print(f"   {c['alignment']:>11.5f}{ratio:>10.2f}{c['penalty']:>10.5f}  {c['topology']} ({c['artifact']})")
    if flat and high:
        print(f"\n   below alignment 0.12: {len(flat)} cells, penalty {min(c['penalty'] for c in flat):.5f}-"
              f"{max(c['penalty'] for c in flat):.5f} (span {max(c['penalty'] for c in flat) - min(c['penalty'] for c in flat):.5f})")
        print(f"   at or above 0.12:     {len(high)} cells, penalty "
              f"{min(c['penalty'] for c in high):.5f}-{max(c['penalty'] for c in high):.5f} "
              f"(span {max(c['penalty'] for c in high) - min(c['penalty'] for c in high):.5f})")
        print(f"   the gap between the two ranges: {min(c['penalty'] for c in high) - max(c['penalty'] for c in flat):.5f}")
        biggest_in = max(c["alignment"] for c in flat)
        smallest_high = min(c["alignment"] for c in high)
        print(f"   and the alignment HOLE between them: the largest in-axis cell is {biggest_in:.5f}, the smallest "
              f"high-regime cell {smallest_high:.5f} -- a factor {smallest_high / biggest_in:.1f}, with "
              f"{smallest_high - biggest_in:.5f} of alignment and no cell in it")

    disagree = [s for s, rhos in tally.items() if len(rhos) > 1 and len(set(x > 0 for x in rhos)) > 1]
    print(f"\n   VERDICT: {len(disagree)} of {len(tally)} statistics change sign across circuit sizes "
          f"({', '.join(disagree) if disagree else 'none'}) -- so no geometry statistic here tracks the penalty "
          f"with a consistent sign, and the sorted table is where the shape that survives lives.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = cells(args.runs)
    if args.json_out:
        write_json(args.json_out, {"cells": rows, "by_artifact": {k: len(v) for k, v in by_artifact(rows).items()}})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
