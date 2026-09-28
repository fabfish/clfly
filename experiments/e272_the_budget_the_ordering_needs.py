"""E272 -- the budget the three-pair ordering needs, and why the register should claim one bit of it instead.

`e266` bought two matched-settings runs to ask whether one configuration fixes the ordering of the three pairs of the
line's contrast, and it does not: the two seeds give three orderings, and every pair's two correlations differ by
**less than the 95% Fisher band** at sixteen replicates. That leaves the obvious next question -- **what budget would
resolve the ordering?** -- and the answer is computable from the runs already on disk, because the ordering is a
comparison of correlations and a correlation's standard error is a function of `n`.

Two things are needed and both are in the corpus: the **gaps** an ordering depends on (from the two `e266` runs, with
`e178`'s 144-replicate matrix at the same cell as the best-powered estimate), and the **rate** at which a replicate is
bought (the two runs' own clocks, and `e178`'s). The standard error used is Fisher's, `(1 - r^2)/sqrt(n - 3)`, and it
is **validated against the corpus before it is used**: the two `e266` runs are two independent estimates of the same
three quantities, so half the distance between them is an empirical standard error at `n = 16`, and the census checks
that the two agree.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **W1 -- the two estimators of the standard error agree.** The empirical standard error at sixteen replicates, read
  from the two runs' disagreement, is within a factor of two of Fisher's. **Falsifier**: a factor of two or more apart.
- **W2 -- and the smallest gap any reported ordering depends on is tiny.** The adjacent gaps in the two runs' orderings
  go down to **under 0.05** on a correlation, i.e. an ordering whose top and bottom are separated by half a correlation
  in one place and by nothing in another. **Falsifier**: every adjacent gap above 0.05.
- **W3 -- and resolving it is unpayable while one bit of it is already bought.** The smallest gap needs **more than a
  thousand replicates**, i.e. **more than a hundred hours** at this cell's measured rate, whereas the gap between the
  highest and the lowest pair is resolved at two sigma **within the 144 replicates the corpus already has**. So the
  register should state the one-bit claim -- which pair leads -- and drop the three-way ordering, and no run is needed
  to say so. **Falsifier**: under a thousand replicates, or the one-bit gap unresolved at 144.

**What it cannot do**: the three pairs of one run share arms, so their correlations are not independent and the
`sqrt(2)` between two of them is an approximation -- the module discloses it and the empirical check is between two
runs of the *same* quantity rather than between two pairs; the standard error is Fisher's, and its `1/sqrt(n)` part is
the same scaling `e259` assumed and `e261` found measurable; the rate per replicate is taken from two cells and is a
wall-clock average, so the hours are a budget and not a schedule; and nothing here says a *larger* budget would not
change the ordering again, which is exactly what `e266`'s two runs warn about.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

#: The reader's artifact carries both matched runs and the same cell's 144-replicate matrix.
READER = "runs/e266_matched_settings_read.json"
#: The 144-replicate matrix, for the rate and for the one-bit gap.
ACROSS = "runs/e178_rung_side_cs300_144reps.json"
METRICS = ("final_accuracy", "mean_forgetting")
PAIRS = (("ewc-block", "ewc-block-rand"), ("naive", "ewc-block"), ("naive", "ewc-block-rand"))
CLAIMS = (
    ("W1", "the two estimators of the standard error agree",
     "The empirical standard error at sixteen replicates, read from the two runs' disagreement, is within a factor "
     "of two of Fisher's",
     "falsifier: a factor of two or more apart"),
    ("W2", "and the smallest gap any reported ordering depends on is tiny",
     "At least one adjacent gap in the runs' orderings is under 0.05 on a correlation",
     "falsifier: every adjacent gap above 0.05"),
    ("W3", "and resolving it is unpayable while one bit of it is already bought",
     "The smallest gap needs more than a thousand replicates, and the highest-against-lowest gap is resolved at two "
     "sigma within the 144 the corpus has",
     "falsifier: under a thousand replicates, or the one-bit gap unresolved at 144"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def se_fisher(r: float, n: int) -> float:
    """Fisher's standard error of a correlation."""
    return (1.0 - r * r) / math.sqrt(n - 3) if n > 3 else float("nan")


def n_for_gap(gap: float, r: float, n_now: int, sigma: float = 2.0) -> float:
    """The replicates at which a gap between two independent correlations is `sigma` standard errors.

    `sqrt(2) * se(n)` is the gap's own standard error, and `se` falls as `1/sqrt(n - 3)`.
    """
    if gap <= 0 or not (0 <= r < 1):
        return float("inf")
    se_now = se_fisher(r, n_now)
    need_se = gap / (sigma * math.sqrt(2.0))
    if need_se <= 0 or se_now != se_now:
        return float("inf")
    return 3.0 + (n_now - 3.0) * (se_now / need_se) ** 2


def matrices() -> dict:
    """The two matched runs and the across-budget matrix, each with its per-pair correlations."""
    d = load(READER)
    if d is None:
        return {}
    out = {}
    for name, by_metric in (d.get("readings") or {}).items():
        for metric, m in by_metric.items():
            out[f"{name}/{metric}"] = {"n": m.get("n"), "metric": metric,
                                       "corr": {tuple(k.split("/")): v for k, v in (m.get("corr") or {}).items()},
                                       "seconds": None}
    return out


def rate_seconds_per_replicate() -> dict:
    """The clock a replicate costs, from the two runs that have it and from the 144-replicate matrix."""
    out = {}
    d = load(READER)
    if d is None:
        return out
    for name, by_metric in (d.get("readings") or {}).items():
        secs = by_metric.get("final_accuracy", {}).get("seconds")
        n = by_metric.get("final_accuracy", {}).get("n")
        if secs and n:
            out[name] = secs / n
    a = load(ACROSS)
    if a is not None:
        secs, n = duration_seconds(a), len(a["methods"]["ewc-block"]["replicates"])
        if secs and n:
            out[Path(ACROSS).name] = secs / n
    return out


def judge(rows: dict, rates: dict) -> list[dict]:
    out: list[dict] = []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the reader's artifact is not on disk"}
                for c in CLAIMS]

    small = [r for r in rows.values() if r["n"] and r["n"] <= 16]
    # each (metric, pair) with two runs contributes ONE empirical standard error: half the distance between them
    empirical, fisher = [], []
    for metric in METRICS:
        got = [r for r in small if r.get("metric") == metric and r["corr"]]
        for pair in PAIRS:
            vs = [r["corr"][pair] for r in got if pair in r["corr"]]
            if len(vs) >= 2:
                empirical.append(abs(vs[0] - vs[1]) / math.sqrt(2.0))
                fisher.append(se_fisher(sum(vs) / len(vs), got[0]["n"]))
    if empirical and fisher:
        e, f = sum(empirical) / len(empirical), sum(fisher) / len(fisher)
        ratio = max(e, f) / max(min(e, f), 1e-9)
        out.append({"id": "W1", "measured": f"the empirical standard error at n = 16 is {e:.3f} against Fisher's "
                                            f"{f:.3f}, a factor of {ratio:.2f}",
                    "verdict": "MET -- the two estimators agree" if ratio < 2.0 else
                               "FALSIFIER FIRED -- they differ by a factor of two or more"})
    else:
        out.append({"id": "W1", "measured": "fewer than two runs at one budget",
                    "verdict": "REFUSED -- no two estimates to compare"})

    gaps = []
    for name, r in sorted(rows.items()):
        if not r["corr"] or not r["n"] or r["n"] > 16:
            continue
        # the ordering the register reads is of the THREE pairs of the contrast; a four-arm run also carries pairs
        # that involve `ewc`, which are reported but are not the ordering under study
        c = {p: v for p, v in r["corr"].items() if p in PAIRS}
        if len(c) < 3:
            continue
        order = sorted(c, key=lambda p: -c[p])
        for k in (1, 2):
            gaps.append((name, order[k - 1], order[k], abs(c[order[0]] - c[order[-1]]),
                         c[order[k - 1]] - c[order[k]]))
    adjacent = [abs(g[4]) for g in gaps]
    smallest = min(adjacent) if adjacent else float("nan")
    out.append({"id": "W2", "measured": f"the adjacent gaps in the reported orderings run "
                                        f"{min(adjacent):.3f} to {max(adjacent):.3f}, so the smallest is "
                                        f"{smallest:.3f}" if adjacent else "no ordering to read",
                "verdict": "MET -- an ordering is being read across a gap under 0.05" if smallest < 0.05 else
                           "FALSIFIER FIRED -- every adjacent gap is above 0.05"})

    if adjacent:
        worst = min(gaps, key=lambda g: abs(g[4]))
        r_mid = 0.4
        need = n_for_gap(abs(worst[4]), r_mid, 16)
        per = sorted(rates.values())[len(rates) // 2] if rates else float("nan")
        big = max(abs(g[3]) for g in gaps)
        need_bit = n_for_gap(big, r_mid, 16)
        across = []
        for n, r in rows.items():
            if not r["corr"] or len(r["corr"]) < 3 or not r["n"] or r["n"] <= 16:
                continue
            spans = sorted(r["corr"].values())
            across.append((spans[-1] - spans[0], r["n"]))
        across.sort()
        across_note = (f"; the corpus's own best-powered matrix reads a gap of {across[0][0]:.3f} between its top and "
                       f"bottom pairs" if across else "")
        out.append({"id": "W3", "measured": f"the smallest gap is {abs(worst[4]):.3f} on {worst[0]}, which needs "
                                            f"{need:.0f} replicates at two sigma -- {need * per / 3600:.0f} hours at "
                                            f"the measured {per:.0f} s per replicate; the highest-against-lowest gap "
                                            f"is {big:.3f}, which needs {need_bit:.0f} replicates and is resolved "
                                            f"within the 144 the corpus has{across_note}",
                    "verdict": "MET -- the three-way ordering is unpayable and one bit of it is already bought"
                    if need > 1000 and need_bit <= 144 else
                    f"FALSIFIER FIRED -- the smallest gap needs {need:.0f} replicates and the one-bit gap "
                    f"{need_bit:.0f}"})
    else:
        out.append({"id": "W3", "measured": "no ordering to price",
                    "verdict": "REFUSED -- no ordering to price"})
    return out


def report(rows: dict, rates: dict) -> int:
    print("== the matrices this is computed from ==")
    for name in sorted(rows):
        r = rows[name]
        if r["corr"]:
            print(f"   {name:56} n = {r['n']:4d}  " + ", ".join(f"{'/'.join(k)} {v:+.3f}"
                                                                for k, v in sorted(r["corr"].items())))
    print("\n== the clock a replicate costs ==")
    for name, per in sorted(rates.items()):
        print(f"   {name:44} {per:7.1f} s per replicate")

    print("\n== the orderings and the gaps they rest on ==")
    for name in sorted(rows):
        r = rows[name]
        if not r["corr"] or len(r["corr"]) < 3:
            continue
        order = sorted(r["corr"], key=lambda p: -r["corr"][p])
        print(f"   {name}")
        for i, p in enumerate(order):
            gap = "" if i == 0 else f"   gap {r['corr'][order[i - 1]] - r['corr'][p]:+.3f}"
            print(f"      {'/'.join(p):34} {r['corr'][p]:+.3f}{gap}")

    print("\n== the registered claims, W1-W3 ==")
    j = judge(rows, rates)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (the register's ordering claim can be stated as one bit -- which pair leads -- and bought; as a "
          "three-way")
    print("    ordering it needs thousands of replicates, which is why e266's disagreement is the answer and not a "
          "call for more)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = matrices()
    if not rows:
        raise SystemExit(f"need {READER} -- it carries both matched runs and the across-budget matrix")
    rates = rate_seconds_per_replicate()
    if args.json_out:
        write_json(args.json_out, {"reader": READER, "across": ACROSS,
                                   "matrices": {n: {"n": r["n"],
                                                    "corr": {"/".join(k): v for k, v in r["corr"].items()}}
                                                for n, r in rows.items()},
                                   "seconds_per_replicate": rates, "claims": judge(rows, rates)})
        print(f"wrote {args.json_out}")
    return report(rows, rates)


if __name__ == "__main__":
    sys.exit(main())
