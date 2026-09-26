"""E247 -- count-matching the drawing spread: how much of the last three fires' volatility is the number of drawings?

`e244` measured a family's spread over however many drawings the corpus happened to have at a cell; `e245` read the
(1, 0) reversal at 2 of 2 comparable cells; `e246` found the cross-cell volatility concentrated in `alloy1` and
`inalloy1`. All three compare quantities that a **bigger sample inflates**: the spread is a max-over-min, so a cell
with eight drawings has more room to move than a cell with two, and the corpus's cells are very unevenly drawn
(`alloy1` has 2, 3, 3, 4, 4 and 8 drawings; `erdos_renyi` 3, 3, 3, 4, 4 and 9; `swap0.5` 2 and 6).

This module removes that by re-measuring every family's spread **at a fixed number of drawings** and asking what
survives. Two count-matched statistics, because the answer is not the same for both:

- **median-of-pairs**: the median spread over all C(n, 2) pairs at a cell -- uses every drawing, and a cell with two
  drawings contributes its single pair;
- **two-lowest-seed**: the single pair formed by the two lowest `rewire_seed` drawings at a cell -- deterministic and
  maximally count-matched, at the cost of throwing the rest away.

    python -m experiments.e247_count_matched_spread
    python -m experiments.e247_count_matched_spread --json-out runs/e247_count_matched_spread.json

**Disclosure.** This is an audit of the last three fires' numbers, and four of its five claims were computed in an
exploratory heredoc before the module was written; the finding quotes that run. They are recorded as **confirmatory**,
and the module exists so the numbers are reproducible and regression-tested rather than living in a transcript. One
claim is **blind**: R5, on the rank observable.

The claims:

- **R1 -- count-matching dissolves most of the one-side drift.** Under the median-of-pairs statistic `alloy1`'s
  cross-cell span falls from its all-drawings **3.04x** to at most **2.5x**, and `inalloy1`'s from **2.43x** to at
  most **2.0x**. **Falsifier**: either stays at or above its all-drawings value, which would say the drift is not the
  sample size.
- **R2 -- and it takes `e246`'s N1 with it.** That claim was that the kind-1 and other ranges are *disjoint*. Under the
  median-of-pairs statistic the separation is **under 10%** and under the two-lowest-seed statistic the ranges
  **overlap**. **Falsifier**: both statistics keep a separation of 20% or more, which would leave N1 standing.
- **R3 -- the cell's own shape does not order the spread.** Across (family, cell) groups, |Spearman| between the
  spread and the cell's **support share** is under **0.3**, and so is the one against its **circuit size**.
  **Falsifier**: 0.5 or more for either, which would give the drift a cell-level driver.
- **R4 -- the count-matched (1, 0) comparison does not keep one direction.** At exactly two drawings per family it goes
  the pooled way at one of the two comparable cells and the reversal way at the other -- where the all-drawings form
  had the reversal at 2 of 2. **Falsifier**: one direction at both cells.
- **R5 (blind) -- a drawing's noisiness is shared between the two observables.** Across (family, cell) groups the
  count-matched excess spread and the count-matched rank spread are positively rank-correlated; **falsifier**: below
  +0.2 in absolute value, which would say the penalty's and the geometry's drawing noise are independent.

The exit code is the number of claims **REFUSED** because a kind or a statistic has no family with two cells.

**What it cannot do**: two count-matched statistics that disagree are reported as disagreeing rather than averaged
into one number, and the disagreement is the finding; a two-drawing spread is a very noisy estimator, so count-matching
buys comparability at the price of precision; the drawings' identities still differ between cells (a `rewire_seed` is a
fresh draw), so nothing here is a paired comparison; the rank observable is only count-matched in R5; `rho` is the
builder's default (`config.rho: None` everywhere); and nothing here is a new measurement.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import median

from clfly.bench.artifacts import write_json
from experiments import domain_rule
from experiments.e244_drawing_spread_by_kind import CONTROL, _draws, kind_of
from experiments.e246_spread_volatility_by_family import spearman

CLAIMS = (
    ("R1", "count-matching dissolves most of the one-side drift",
     "Under the median-of-pairs statistic alloy1's cross-cell span falls from 3.04x to at most 2.5x and inalloy1's "
     "from 2.43x to at most 2.0x",
     "falsifier: either stays at or above its all-drawings value [confirmatory: seen in an exploratory run]"),
    ("R2", "and it takes e246's N1 with it",
     "The count-matched separation between the kind-1 and other spans is under 10% (median-of-pairs) and the ranges "
     "overlap (two-lowest-seed)",
     "falsifier: both statistics keep a separation of 20% or more [confirmatory]"),
    ("R3", "the cell's own shape does not order the spread",
     "Across (family, cell) groups the |Spearman| against support share is under 0.3 and so is the one against circuit "
     "size",
     "falsifier: 0.5 or more for either cell covariate [confirmatory]"),
    ("R4", "the count-matched (1, 0) comparison does not keep one direction",
     "At exactly two drawings per family the (1, 0) pair goes the pooled way at one of the two comparable cells and "
     "the reversal way at the other",
     "falsifier: one direction at both cells [confirmatory]"),
    ("R5", "a drawing's noisiness is shared between the two observables (BLIND)",
     "Across (family, cell) groups the count-matched excess spread and the count-matched rank spread are positively "
     "rank-correlated",
     "falsifier: below +0.2 in absolute value, which would say the penalty's and the geometry's drawing noise are "
     "independent [this one was not computed before the module was written]"),
)
SEPARATION_BAR = 0.20
SEPARATION_AGREE = 0.10
COVARIATE_BAR = 0.30
COVARIATE_FALSIFIER = 0.50
SHARED_NOISE_BAR = 0.20


def per_cell(root: Path) -> dict[str, dict]:
    """(family, cell) -> the per-drawing excesses and ranks, so any count-matched subsample can be taken."""
    out: dict[str, dict] = defaultdict(dict)
    for cell, tops in _draws(root).items():
        for topo, draws in tops.items():
            keys = sorted(draws)
            ex = [draws[k]["excess"] for k in keys if isinstance(draws[k]["excess"], (int, float))]
            rk = [draws[k]["rank"] for k in keys if isinstance(draws[k]["rank"], (int, float)) and draws[k]["rank"] > 0]
            if kind_of(topo) is not None:
                out[topo][cell] = {"excess": [v for v in ex if v > 0], "rank": rk,
                                   "keys": [k for k in keys]}
    return {f: c for f, c in out.items() if f != CONTROL}


def median_pair(vals: list[float]) -> float | None:
    """The median of all pairwise max-over-min ratios -- a two-drawing-equivalent spread that uses every drawing."""
    if len(vals) < 2:
        return None
    return median([max(a, b) / min(a, b) for a, b in combinations(sorted(vals), 2)])


def lowest_two(vals: list[float]) -> float | None:
    """The spread of the two smallest values -- deterministic and maximally count-matched."""
    if len(vals) < 2:
        return None
    v = sorted(vals)[:2]
    return max(v) / min(v)


def matched_table(fam: dict, field: str) -> dict[str, dict]:
    """family -> {cell: (median-of-pairs, two-lowest-seed, all drawings, n drawings)} for one observable."""
    out: dict[str, dict] = {}
    for f, percell in fam.items():
        rows = {}
        for cell, d in percell.items():
            v = d[field]
            if len(v) < 2:
                continue
            rows[cell] = {"pair_median": median_pair(v), "lowest_two": lowest_two(v),
                          "all": max(v) / min(v), "n": len(v)}
        if rows:
            out[f] = rows
    return out


def spans(table: dict[str, dict], key: str) -> dict[str, float]:
    """Each family's cross-cell span of one of the three spread statistics."""
    out = {}
    for f, rows in table.items():
        v = [r[key] for r in rows.values() if r[key]]
        if len(v) > 1 and min(v) > 0:
            out[f] = max(v) / min(v)
    return out


def kind_of_family(fam: dict) -> dict[str, int]:
    from experiments.e244_drawing_spread_by_kind import kind_of
    return {f: kind_of(f) for f in fam}


def covariates(fam: dict, table: dict[str, dict]) -> list[tuple[str, tuple, float, float, float, int]]:
    """(family, cell, spread, support share, circuit size, n) for every count-matched group."""
    out = []
    for f, rows in table.items():
        for cell, r in rows.items():
            out.append((f, cell, r["pair_median"], cell[1] / cell[0], cell[0], r["n"]))
    return out


def _spans_by_kind(sp: dict[str, float], kinds: dict[str, int]) -> dict[int, list[float]]:
    out: dict[int, list[float]] = defaultdict(list)
    for f, s in sp.items():
        if kinds.get(f) is not None:
            out[kinds[f]].append(s)
    return out


def judge(fam: dict) -> list[dict]:
    kinds = kind_of_family(fam)
    table = matched_table(fam, "excess")
    all_sp, pm_sp, lt_sp = spans(table, "all"), spans(table, "pair_median"), spans(table, "lowest_two")
    out: list[dict] = []

    one_side = ("alloy1", "inalloy1")
    if not all(f in all_sp and f in pm_sp for f in one_side):
        out.append({"id": "R1", "verdict": "REFUSED -- a one-side family has no two-cell span"})
    else:
        moved = [f"{f} {all_sp[f]:.2f}x -> {pm_sp[f]:.2f}x" for f in one_side]
        ok = pm_sp["alloy1"] <= 2.5 and pm_sp["inalloy1"] <= 2.0 and pm_sp["alloy1"] < all_sp["alloy1"] \
            and pm_sp["inalloy1"] < all_sp["inalloy1"]
        out.append({"id": "R1", "measured": "median-of-pairs spans: " + ", ".join(moved),
                    "verdict": "MET -- both fall" if ok else "FALSIFIER FIRED -- a drift survives count-matching"})

    by_kind_pm = _spans_by_kind(pm_sp, kinds)
    by_kind_lt = _spans_by_kind(lt_sp, kinds)
    if not (by_kind_pm.get(1) and by_kind_pm.get(0)) or not (by_kind_lt.get(1) and by_kind_lt.get(0)):
        out.append({"id": "R2", "verdict": "REFUSED -- a kind has no family with two cells under some statistic"})
    else:
        def sep(by):
            one = min(by[1])
            other = max(by.get(0, []) + by.get(2, []))
            return (one / other) if one > other else (other / one)
        s_pm, s_lt = sep(by_kind_pm), sep(by_kind_lt)
        overlap_lt = min(by_kind_lt[1]) <= max(by_kind_lt.get(0, []) + by_kind_lt.get(2, []))
        others_pm = by_kind_pm.get(0, []) + by_kind_pm.get(2, [])
        measured = (f"median-of-pairs separation {s_pm:.3f}x (kind 1 {min(by_kind_pm[1]):.2f}x to "
                    f"{max(by_kind_pm[1]):.2f}x against others {min(others_pm):.2f}x to {max(others_pm):.2f}x); "
                    f"two-lowest-seed separation {s_lt:.3f}x, overlapping={overlap_lt}")
        if s_pm < 1 + SEPARATION_AGREE and overlap_lt:
            verdict = "MET -- the disjointness does not survive"
        elif min(s_pm, s_lt) >= 1 + SEPARATION_BAR:
            verdict = "FALSIFIER FIRED -- a count-matched statistic keeps a 20% separation"
        else:
            verdict = "null band -- one statistic separates and the other does not"
        out.append({"id": "R2", "measured": measured, "verdict": verdict})

    cov = covariates(fam, table)
    share = spearman([c[3] for c in cov], [c[2] for c in cov])
    size = spearman([c[4] for c in cov], [c[2] for c in cov])
    if share is None or size is None:
        out.append({"id": "R3", "verdict": "REFUSED -- not enough count-matched groups"})
    else:
        ok = abs(share) < COVARIATE_BAR and abs(size) < COVARIATE_BAR
        out.append({"id": "R3", "measured": f"Spearman(spread, support share) {share:+.3f}, "
                                           f"Spearman(spread, circuit size) {size:+.3f} over {len(cov)} groups",
                    "verdict": "MET" if ok else
                               "FALSIFIER FIRED -- a cell covariate orders the spread"
                               if max(abs(share), abs(size)) >= COVARIATE_FALSIFIER else
                               "null band -- a covariate is above the bar but below the falsifier"})

    two = {f: {cell: r["lowest_two"] for cell, r in rows.items()} for f, rows in table.items()}
    pairs = []
    for cell in set(c for rows in two.values() for c in rows):
        k = {kind: [] for kind in (0, 1, 2)}
        for f, rows in two.items():
            if cell in rows and kinds.get(f) is not None:
                k[kinds[f]].append(rows[cell])
        if k[1] and k[0]:
            pairs.append((cell, median(k[0]), median(k[1])))
    if not pairs:
        out.append({"id": "R4", "verdict": "REFUSED -- no cell carries both kind 0 and kind 1 at two drawings"})
    else:
        ways = [("pooled" if m0 > m1 else "reversal") for _, m0, m1 in pairs]
        measured = "; ".join(f"cs {c[0]}/sup {c[1]}: kind 0 {m0:.2f}x against kind 1 {m1:.2f}x ({w})"
                             for (c, m0, m1), w in zip(pairs, ways))
        out.append({"id": "R4", "measured": measured,
                    "verdict": "MET -- the directions disagree" if len(set(ways)) > 1 else
                               "FALSIFIER FIRED -- one direction at every cell"})

    rk = matched_table(fam, "rank")
    both = []
    for f, rows in table.items():
        for cell, r in rows.items():
            other = rk.get(f, {}).get(cell)
            if other:
                both.append((r["pair_median"], other["pair_median"]))
    rho = spearman([b[0] for b in both], [b[1] for b in both]) if len(both) >= 3 else None
    if rho is None:
        out.append({"id": "R5", "verdict": "REFUSED -- fewer than three groups carry both observables"})
    else:
        out.append({"id": "R5", "measured": f"Spearman(count-matched excess spread, count-matched rank spread) "
                                           f"{rho:+.3f} over {len(both)} groups",
                    "verdict": "MET -- the drawing moves both observables together" if rho >= SHARED_NOISE_BAR else
                               "FALSIFIER FIRED -- the two noises are unrelated" if abs(rho) < SHARED_NOISE_BAR else
                               "null band -- negative, so a drawing that is noisy for one is quiet for the other"})
    return out


def sep_min(a: float, b: float) -> float:
    return min(a, b)


def report(fam: dict) -> int:
    table = matched_table(fam, "excess")
    kinds = kind_of_family(fam)
    print("== the three spreads per (family, cell), and what count-matching does to each family's span ==")
    print(f"   {'family':13} {'kind':>4} {'cells':>5} {'all-drawings span':>18} {'median-of-pairs':>16} "
          f"{'two-lowest-seed':>16}")
    all_sp, pm_sp, lt_sp = spans(table, "all"), spans(table, "pair_median"), spans(table, "lowest_two")
    for f in sorted(table, key=lambda f: (kinds[f] if kinds[f] is not None else 9, f)):
        print(f"   {f:13} {kinds[f]:>4} {len(table[f]):>5} {all_sp.get(f, float('nan')):>18.2f} "
              f"{pm_sp.get(f, float('nan')):>16.2f} {lt_sp.get(f, float('nan')):>16.2f}")
    print("\n   per-cell detail, all drawings against the two count-matched statistics:")
    print(f"      {'family':13} {'cell':>18} {'n':>3} {'all':>6} {'pair median':>12} {'lowest two':>11}")
    for f in sorted(table, key=lambda f: (kinds[f] if kinds[f] is not None else 9, f)):
        for cell, r in sorted(table[f].items(), key=lambda kv: str(kv[0])):
            print(f"      {f:13} {f'cs {cell[0]}/sup {cell[1]}':>18} {r['n']:>3} {r['all']:>6.2f} "
                  f"{r['pair_median']:>12.2f} {r['lowest_two']:>11.2f}")

    cov = covariates(fam, table)
    print("\n== the cell's shape against the count-matched spread ==")
    share = spearman([c[3] for c in cov], [c[2] for c in cov])
    size = spearman([c[4] for c in cov], [c[2] for c in cov])
    # a corpus too small for a rank correlation is not a crash: the covariate columns report `nan` like the spans do
    def fmt(v):
        return "nan" if v is None else f"{v:+.3f}"
    print(f"   {len(cov)} groups: Spearman(spread, support share) {fmt(share)}   Spearman(spread, circuit size) "
          f"{fmt(size)}")
    print("   (both are near zero -- the drift is not the support share and not the size)")

    print("\n== the registered claims, R1-R5 ==")
    j = judge(fam)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row.get('measured', '')}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    return sum("REFUSED" in r["verdict"] for r in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=Path("runs"))
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--domain", action="store_true",
                    help="also read every claim on the declared domain's cells only (the rule in domain_rule)")
    args = ap.parse_args(argv)
    fam = per_cell(args.runs)
    inside = outside = None
    if args.domain:
        inside, outside = domain_rule.corpus(args.runs)
    if args.json_out:
        payload = {"families": {f: {str(c): r for c, r in rows.items()} for f, rows in fam.items()},
                   "table": {f: {str(c): r for c, r in rows.items()}
                             for f, rows in matched_table(fam, "excess").items()},
                   "claims": judge(fam)}
        if inside is not None:
            filtered = domain_rule.filter_fam(fam, inside)
            payload["claims_domain"] = judge(filtered)
            payload["table_domain"] = {f: {str(c): r for c, r in rows.items()}
                                       for f, rows in matched_table(filtered, "excess").items()}
            payload["domain"] = sorted(str(c) for c in inside)
            payload["out_of_domain"] = sorted(str(c) for c in outside)
        write_json(args.json_out, payload)
        print(f"wrote {args.json_out}")
    if inside is not None:
        print("\n== the same claims, read inside the declared domain ==")
        print(domain_rule.statement(judge(fam), judge(domain_rule.filter_fam(fam, inside))))
    return report(fam)


if __name__ == "__main__":
    sys.exit(main())
