"""E246 -- whose volatility is it? The spread's cross-cell movement by family, and whether the level explains it.

`e244` found that the drawing spread of the penalty is ordered by the ladder's axis **when pooled over cells** and that
its one within-cell test fires against it; `e245` bought a second cell for the no-destruction rung and found the
reversal replicates in **direction** at 2 of 2 cells and not in **size** (+2.2% and +104.4%, a factor of 47 apart),
which located the movement in the one-side rung. This module asks the two questions that reading left:

    is the cross-cell movement a property of the FAMILY or of the KIND?
    and is the whole spread story the LEVEL's story in disguise?

It reads every group `e244` builds -- the (cell, family) pairs with two or more drawings -- and answers both without a
new run.

    python -m experiments.e246_spread_volatility_by_family
    python -m experiments.e246_spread_volatility_by_family --json-out runs/e246_spread_volatility_by_family.json

**Disclosure, because the registry matters more than the gesture.** Two facts were already on screen when this module
was written, from an exploratory heredoc and from `e244`'s own tables: the per-family cross-cell spans on the excess
(`alloy1` 3.04x over six cells, `inalloy1` 2.43x over six, `swap0.5` 1.32x, `swap2` 1.36x, `signshuffle` 1.30x,
`erdos_renyi` 1.04x), and the aggregate Spearman between a group's mean excess and its spread, **-0.696** over 26
groups. **N1 and N2 therefore test what was already seen** and are recorded as confirmatory rather than blind.
**N3's split has not been computed**: the between-family and within-family halves of that -0.696 are what this module
measures, and that is the part registered blind.

Three claims:

- **N1 -- the cross-cell volatility is the one-side families' (excess).** Every kind-1 family's span of its own
  drawings' excess spread across cells exceeds **every** kind-0 and kind-2 family's span, i.e. the two ranges are
  disjoint. **Falsifier**: an overlap -- a no-destruction or two-side family that moves as much across cells as a
  one-side one.
- **N2 -- the same on the rank observable.** The same statement for each family's rank spread. **Falsifier**: overlap.
- **N3 -- the level orders the spread BETWEEN families and not within them.** (a) Across families, taking each
  family's mean level and mean spread over its cells, |Spearman| is at least **0.7**; and (b) inside families with
  **four or more** cells, the share of level-adjacent pairs whose spread falls as the level rises is at most **60%**.
  **Falsifier**: (b) at or above **80%**, which would say the level moves the spread inside a fixed construction and
  make the kind's axis a proxy, or (a) below **0.5**, which would say the level does not order the spread at all;
  **null**: exactly one clause met.

The exit code is the number of claims **REFUSED** because a kind has no family measured at two or more cells.

**What it cannot do**: the spans compare families whose cells are not the same set, so a family measured over six cells
has more room to move than one measured over two -- stated, not corrected for, and the reason N1 asks for disjoint
ranges rather than a threshold; **and `e247` shows that disjointness does not survive count-matching**, since a spread
is a max-over-min and a cell with eight drawings has more room than one with two: at a fixed two-drawing budget the
kind-1 range (1.83x to 2.36x) and the others (1.00x to 1.82x) are separated by 1.004x, so N1 stands only on the
all-drawings budget; a family's spread at a cell is itself a ratio of two or three drawings; the levels are
means over drawings whose own scatter the spread measures, so the two quantities are not independent; `rho` is 0.9
throughout (`config.rho: None` in every artifact, which every reader maps to the default); and nothing here is a new
measurement.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

from clfly.bench.artifacts import write_json
from experiments import domain_rule
from experiments.e244_drawing_spread_by_kind import KIND_NAMES, RUNS, groups as e244_groups

CLAIMS = (
    ("N1", "the cross-cell volatility is the one-side families' (excess)",
     "Every kind-1 family's span of its own drawings' excess spread across cells exceeds every kind-0 and kind-2 "
     "family's span, so the two ranges are disjoint",
     "falsifier: an overlap, a no-destruction or two-side family that moves as much across cells as a one-side one "
     "[confirmatory: the spans were on screen before this module was written]"),
    ("N2", "the same on the rank observable",
     "The same disjointness for each family's rank spread across cells",
     "falsifier: an overlap on the rank spans [confirmatory]"),
    ("N3", "the level orders the spread BETWEEN families and not within them",
     "Across families (mean level against mean spread) |Spearman| >= 0.7, and inside families with four or more cells "
     "the share of level-adjacent pairs whose spread falls as the level rises is at most 60%",
     "falsifier: the within-family share at or above 80%, or the between-family |Spearman| below 0.5; null: exactly "
     "one clause met [the split is registered blind]"),
)
MIN_CELLS = 4
WITHIN_BAR = 0.80
WITHIN_CEILING = 0.60
BETWEEN_BAR = 0.7
BETWEEN_FLOOR = 0.5


def by_family(gs: list[dict]) -> dict[str, list[dict]]:
    """Every family with a group, keyed by name, with the groups sorted by cell."""
    fam: dict[str, list[dict]] = defaultdict(list)
    for g in gs:
        if g["kind"] is not None:
            fam[g["family"]].append(g)
    return {f: sorted(rows, key=lambda g: str(g["cell"])) for f, rows in sorted(fam.items())}


def span(rows: list[dict], field: str) -> float | None:
    """How far a family's own spread moves across the cells it was measured in."""
    v = [r[field] for r in rows if r[field] is not None]
    return (max(v) / min(v)) if len(v) > 1 and min(v) > 0 else None


def spearman(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:                      # ties share a rank, which matters for the level and the spread alike
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = mean(rx), mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return (num / den) if den else None


def pooled(gs: list[dict]) -> tuple[float | None, int]:
    """The correlation the decomposition is a decomposition OF: every group with both a level and a spread at once."""
    pts = [(g["excess_mean"], g["excess_spread"]) for g in gs
           if g["kind"] is not None and g["excess_mean"] is not None and g["excess_spread"] is not None]
    return spearman([p[0] for p in pts], [p[1] for p in pts]), len(pts)


def between(fam: dict[str, list[dict]]) -> tuple[list[tuple[str, float, float, int]], float | None]:
    """Each family as one point: its mean level against the mean of its own spreads across cells."""
    pts = []
    for name, rows in fam.items():
        lv = [r["excess_mean"] for r in rows if r["excess_mean"] is not None]
        sp = [r["excess_spread"] for r in rows if r["excess_spread"] is not None]
        if len(sp) >= 2 and lv:
            pts.append((name, mean(lv), mean(sp), len(sp)))
    pts.sort(key=lambda p: p[1])
    return pts, spearman([p[1] for p in pts], [p[2] for p in pts])


def within(fam: dict[str, list[dict]]) -> list[tuple[str, int, int, int]]:
    """Per family with enough cells: sorted by level, how many adjacent pairs fall as the level rises.

    Holding the construction fixed is the de-confounded form of the question -- the cell varies, the family does not.
    """
    out = []
    for name, rows in fam.items():
        pts = [(r["excess_mean"], r["excess_spread"]) for r in rows
               if r["excess_mean"] is not None and r["excess_spread"] is not None]
        if len(pts) < MIN_CELLS:
            continue
        pts.sort()
        falls = sum(1 for i in range(len(pts) - 1) if pts[i + 1][1] < pts[i][1])
        out.append((name, len(pts), falls, len(pts) - 1))
    return sorted(out)


def judge(gs: list[dict]) -> list[dict]:
    fam = by_family(gs)
    out: list[dict] = []
    for cid, field in (("N1", "excess_spread"), ("N2", "rank_spread")):
        spans = {f: span(rows, field) for f, rows in fam.items()}
        kinds: dict[int, list[float]] = defaultdict(list)
        for f, s in spans.items():
            if s is not None:
                kinds[next(g["kind"] for g in fam[f] if g["kind"] is not None)].append(s)
        missing = [k for k in KIND_NAMES if not kinds.get(k)]
        if missing:
            out.append({"id": cid, "verdict": f"REFUSED -- kind(s) {missing} have no family measured at two cells"})
            continue
        one, other = kinds[1], kinds[0] + kinds[2]
        measured = (f"one-side {min(one):.2f}x-{max(one):.2f}x over {len(one)} families, "
                    f"others {min(other):.2f}x-{max(other):.2f}x over {len(other)}")
        out.append({"id": cid, "measured": measured,
                    "verdict": "MET -- the ranges are disjoint" if min(one) > max(other) else
                               "FALSIFIER FIRED -- the ranges overlap"})

    pts, rho = between(fam)
    w = within(fam)
    falls = sum(x[2] for x in w)
    pairs = sum(x[3] for x in w)
    share = (falls / pairs) if pairs else None
    if rho is None or share is None:
        out.append({"id": "N3", "verdict": "REFUSED -- not enough families with enough cells"})
    else:
        a = abs(rho) >= BETWEEN_BAR
        b = share >= WITHIN_BAR
        measured = (f"between-family Spearman(level, spread) {rho:+.3f} over {len(pts)} families; "
                    f"within-family {falls} of {pairs} level-adjacent pairs fall "
                    f"({100 * share:.0f}%) over {len(w)} families with {MIN_CELLS}+ cells")
        if b or abs(rho) < BETWEEN_FLOOR:
            verdict = "FALSIFIER FIRED -- " + ("the level moves the spread inside a fixed family" if b
                                               else "the level does not order the spread between families either")
        elif a and share <= WITHIN_CEILING:
            verdict = "MET -- ordered between families and not within them"
        else:
            verdict = f"null band -- between-family {'met' if a else 'not met'}, within-family ceiling missed"
        out.append({"id": "N3", "measured": measured, "verdict": verdict})
    return out


def report(gs: list[dict]) -> int:
    fam = by_family(gs)
    print("== each family's own spread across the cells it was measured in ==")
    print(f"   {'family':13} {'kind':>4} {'cells':>5} {'excess spread per cell':34} {'span':>6} "
          f"{'rank spread per cell':34} {'span':>6}")
    for name, rows in sorted(fam.items(), key=lambda kv: (kv[1][0]["kind"], kv[0])):
        ex = sorted(r["excess_spread"] for r in rows if r["excess_spread"] is not None)
        rk = sorted(r["rank_spread"] for r in rows if r["rank_spread"] is not None)
        s, rs = span(rows, "excess_spread"), span(rows, "rank_spread")
        fmt = lambda v: " ".join(f"{x:.2f}" for x in v)
        print(f"   {name:13} {rows[0]['kind']:>4} {len(rows):>5} {fmt(ex):34} "
              f"{(s if s is not None else float('nan')):>6.2f} {fmt(rk):34} "
              f"{(rs if rs is not None else float('nan')):>6.2f}")

    pts, rho = between(fam)
    print("\n== the level against the spread: one point per family ==")
    for name, lv, sp, n in pts:
        print(f"   {name:13} mean level {lv:.5f}   mean spread {sp:.2f}x   over {n} cells")
    print(f"   Spearman(level, spread) between families: {rho:+.3f} over {len(pts)} families"
          if rho is not None else "   not enough families")
    print("\n== and the correlation those two are the decomposition OF ==")
    pooled_rho, n_pooled = pooled(gs)
    print(f"   every group at once: Spearman(level, spread) {0 if pooled_rho is None else pooled_rho:+.3f} "
          f"over {n_pooled} groups")
    print(f"   (the between-family half above is {0 if rho is None else rho:+.3f}; the rest of the pooled figure is")
    print("    the WITHIN-family drift the section below measures -- pooling the two is what produced it)")

    print(f"\n== the same question INSIDE each family, holding the construction fixed ({MIN_CELLS}+ cells) ==")
    for name, n, falls, pairs in within(fam):
        print(f"   {name:13} {n} cells: {falls} of {pairs} level-adjacent pairs fall as the level rises")
    print("   (a family's cells differ only in circuit size, support and rho -- so this is the cell's effect on the")
    print("    spread with the construction held fixed, which is what the pooled -0.70 cannot separate)")

    print("\n== the registered claims, N1-N3 ==")
    j = judge(gs)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--domain", action="store_true",
                    help="also read every claim on the declared domain's cells only (the rule in domain_rule)")
    args = ap.parse_args(argv)
    gs, control = e244_groups()
    inside = outside = None
    if args.domain:
        inside, outside = domain_rule.corpus(RUNS)
    if args.json_out:
        payload = {"families": {f: [list(g["cell"]) for g in rows] for f, rows in by_family(gs).items()},
                   "between": between(by_family(gs))[0],
                   "pooled": pooled(gs),
                   "within": within(by_family(gs)),
                   "claims": judge(gs), "control": [c["family"] for c in control]}
        if inside is not None:
            filtered = domain_rule.filter_gs(gs, inside)
            payload["claims_domain"] = judge(filtered)
            payload["families_domain"] = {f: [list(g["cell"]) for g in rows]
                                          for f, rows in by_family(filtered).items()}
            payload["domain"] = sorted(str(c) for c in inside)
            payload["out_of_domain"] = sorted(str(c) for c in outside)
        write_json(args.json_out, payload)
        print(f"wrote {args.json_out}")
    if inside is not None:
        print("\n== the same claims, read inside the declared domain ==")
        print(domain_rule.statement(judge(gs), judge(domain_rule.filter_gs(gs, inside))))
    return report(gs)


if __name__ == "__main__":
    sys.exit(main())
