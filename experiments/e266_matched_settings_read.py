"""E266 -- one configuration at matched settings, twice: does the ordering reproduce, and what does the plain-EWC arm say?

`e265` found that the ordering `e264` read over the corpus -- the pair that differs only in its basis being the most
correlated of the three -- does not reproduce: it leads in 21 of the 50 readable matrices, and the five runs of the
`fb8` group, which share **every** configuration field, give it ranks 1, 0, 1, 0 and 0. `e265` read that disagreement
as an **unrecorded setting** (three of those runs name a thread count that no artifact records). The alternative is
that a correlation at sixteen replicates is simply too noisy to order three pairs, and the corpus cannot tell the two
apart because the only configuration it ever ran twice at fixed settings is `e153`/`e159`, which are bit-identical.

**So two runs were launched at matched settings and nothing else changed.** Both are `side` at cs 300 with
`readout_size` 32, `shared_head`, `fisher_batches` 32 and `lam` 1.0 -- the cell of the corpus's best-powered matrix,
`e178`, at 144 replicates -- with sixteen replicates, four arms (`naive`, `ewc`, `ewc-block`, `ewc-block-rand`) and
the environment recorded. The second differs from the first in `seed0` alone (`0` against `100`). The plain-`ewc` arm
is the one the corpus carries in only 22 artifacts and only at five replicates in this neighbourhood: a penalty with
no basis, so it shares the penalty form with both block arms and shares the basis with neither.

    runs/e266_matched_side_seed0_16reps.json and runs/e266_matched_side_seed100_16reps.json

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **M1 -- one configuration, one ordering?** The two seeds put the pair the contrast is about at the **same rank**. If
  they do not, then a correlation at sixteen replicates is too noisy to order three pairs and `e265`'s W3 needs no
  unrecorded setting to explain it. **Falsifier**: different ranks for the basis pair between the two runs.
- **M2 -- and the two runs agree within the sampling noise of a correlation.** Every pair's two correlations differ by
  less than the 95% band of the Fisher transform at n = 16. **Falsifier**: any pair outside the band either side.
- **M3 -- the plain-EWC arm separates the penalty form from the basis.** If the shared component is the penalty's
  machinery, the pair that shares the **penalty form only** (`ewc` against `ewc-block`) is more correlated than
  either naive pair, in both runs. **Falsifier**: it is at or below both naive pairs in either run.
- **M4 -- and the ceiling device applies at this cell.** Every arm's test-set floor sits below its own replicate
  spread in both runs, so the item ceiling of `e263` and `e264` can be formed. **Falsifier**: any arm at or above its
  own spread.

The exit code is the number of claims **REFUSED** because an artifact is absent, so this module reports its own
absence rather than a number -- it was written before the runs finished, which is `e190`'s pattern and the reason the
programme table's row for it names no artifact under `runs/`.

**What it cannot do**: two seeds are two draws, so M1 is a single comparison and not a distribution of orderings --
`e265`'s five-run group is the better replication and it disagrees, which is the tension this pair was bought to
relieve rather than to settle; the two runs share the machine, the torch version and the thread count, so they cannot
see an environmental change either; sixteen replicates give a correlation a standard error near 0.25, which is why M2
is a band and not a difference; and M3 is a one-directional prediction about an arm the corpus has at this cell for
the first time, so a null there is a null on one cell.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import duration_seconds, write_json

#: The two runs at matched settings, differing in `seed0` alone, and the same cell's 144-replicate matrix.
RUNS = ("runs/e266_matched_side_seed0_16reps.json", "runs/e266_matched_side_seed100_16reps.json")
ACROSS = "runs/e178_rung_side_cs300_144reps.json"
METRICS = ("final_accuracy", "mean_forgetting")
PAIRS = (("ewc-block", "ewc-block-rand"), ("naive", "ewc-block"), ("naive", "ewc-block-rand"))
PENALTY_PAIR = ("ewc", "ewc-block")
CLAIMS = (
    ("M1", "one configuration gives one ordering",
     "The two seeds put the pair the contrast is about at the same rank of the three",
     "falsifier: different ranks for that pair between the two runs"),
    ("M2", "and the two runs agree within the sampling noise of a correlation",
     "Every pair's two correlations differ by less than the 95% band of the Fisher transform at sixteen replicates",
     "falsifier: any pair outside that band"),
    ("M3", "the plain-EWC arm separates the penalty form from the basis",
     "The pair that shares the penalty form only is more correlated than either naive pair, in both runs",
     "falsifier: it is at or below both naive pairs in either run"),
    ("M4", "and the ceiling device applies at this cell",
     "Every arm's test-set floor sits below its own replicate spread in both runs",
     "falsifier: any arm at or above its own spread"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def variance(xs: list[float]) -> float:
    n = len(xs)
    mean = sum(xs) / n
    return sum((x - mean) ** 2 for x in xs) / (n - 1)


def covariance(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n - 1)


def matrix(d: dict, metric: str) -> dict:
    """Every arm's variance, every pair's correlation and item ceiling, and whether the ceiling can be formed."""
    ev = d["evaluation_noise"]
    arms = [a for a in d["methods"] if isinstance(d["methods"][a], dict) and d["methods"][a].get("replicates")]
    vals = {a: [r[metric] for r in d["methods"][a]["replicates"]] for a in arms}
    v = {a: variance(vals[a]) for a in arms}
    b = {a: ((ev.get(a) or {}).get("binomial_sem", 0.0)) ** 2 for a in arms}
    live = all(v[a] > 0 for a in arms)
    corr = {p: (covariance(vals[p[0]], vals[p[1]]) / math.sqrt(v[p[0]] * v[p[1]]) if live else float("nan"))
            for p in PAIRS + (PENALTY_PAIR,) if p[0] in arms and p[1] in arms}
    ceiling = {p: (math.sqrt(b[p[0]] * b[p[1]]) / math.sqrt(v[p[0]] * v[p[1]]) if live else float("nan"))
               for p in corr}
    return {"n": len(vals[arms[0]]), "arms": sorted(arms), "variance": v, "item_variance": b, "corr": corr,
            "ceiling": ceiling, "excess": {p: corr[p] - ceiling[p] for p in corr},
            "fraction": {a: (b[a] / v[a] if v[a] > 0 else float("inf")) for a in arms},
            "readable": live and all(b[a] < v[a] for a in arms),
            "seconds": duration_seconds(d)}


def fisher_band(n: int, r: float, z: float = 1.96) -> float:
    """The half-width of the 95% band for a correlation r estimated on n replicates, by the Fisher transform."""
    if n <= 3:
        return float("nan")
    zr = math.atanh(max(min(r, 0.999999), -0.999999))
    se = 1.0 / math.sqrt(n - 3)
    return math.tanh(zr + z * se) - math.tanh(zr - z * se)


def rank_of(m: dict, pair) -> int | None:
    """Where a pair sits among the three the contrast is about, 0 being the most correlated."""
    if not all(p in m["corr"] for p in PAIRS):
        return None
    order = sorted(PAIRS, key=lambda p: -m["corr"][p])
    return order.index(pair)


def readings() -> dict:
    out = {}
    for path in RUNS + (ACROSS,):
        d = load(path)
        if d is None or "evaluation_noise" not in d or "matched_pair" not in d:
            continue
        out[Path(path).name] = {metric: matrix(d, metric) for metric in METRICS}
    return out


def judge(rows: dict) -> list[dict]:
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- neither matched run is on disk"} for c in CLAIMS]
    names = [Path(p).name for p in RUNS if Path(p).name in rows]
    out: list[dict] = []

    if len(names) < 2:
        out.extend({"id": c[0], "measured": f"only {names} is present",
                    "verdict": "REFUSED -- the pair of matched runs is incomplete"} for c in CLAIMS)
        return out

    ranks = {n: {m: rank_of(rows[n][m], PAIRS[0]) for m in METRICS} for n in names}
    same = all(ranks[names[0]][m] == ranks[names[1]][m] for m in METRICS)
    out.append({"id": "M1", "measured": "; ".join(f"{n}: " + ", ".join(f"{m} rank {ranks[n][m]}" for m in METRICS)
                                                  for n in names),
                "verdict": "MET -- one configuration, one ordering" if same else
                           "FALSIFIER FIRED -- the same configuration orders the three pairs differently"})

    worst, lines = 0.0, []
    for m in METRICS:
        for p in PAIRS:
            a, b = rows[names[0]][m]["corr"].get(p), rows[names[1]][m]["corr"].get(p)
            if a is None or b is None:
                continue
            band = fisher_band(rows[names[0]][m]["n"], (a + b) / 2)
            delta = abs(a - b)
            worst = max(worst, delta - band)
            lines.append(f"{m} {p[0]}/{p[1]} {a:+.3f} against {b:+.3f} (delta {delta:.3f}, band {band:.3f})")
    out.append({"id": "M2", "measured": "; ".join(lines),
                "verdict": "MET -- every pair agrees inside its own band" if worst <= 0 else
                           "FALSIFIER FIRED -- a pair differs by more than its band"})

    lines, ok = [], True
    for n in names:
        for m in METRICS:
            m_ = rows[n][m]
            if PENALTY_PAIR not in m_["corr"]:
                ok = False
                lines.append(f"{n} {m}: the plain-ewc arm is absent")
                continue
            pen = m_["corr"][PENALTY_PAIR]
            naive = [m_["corr"][p] for p in PAIRS[1:]]
            lines.append(f"{n} {m}: penalty-only pair {pen:+.3f} against naive pairs "
                         + " and ".join(f"{v:+.3f}" for v in naive))
            if pen <= max(naive) - 0 or pen <= min(naive):
                ok = False
    out.append({"id": "M3", "measured": "; ".join(lines),
                "verdict": "MET -- the penalty form alone carries the correlation" if ok else
                           "FALSIFIER FIRED -- the penalty-only pair is not above both naive pairs"})

    lines, ok4 = [], True
    for n in names:
        for m in METRICS:
            m_ = rows[n][m]
            lines.append(f"{n} {m}: " + ", ".join(f"{a} {v:.2f}" for a, v in sorted(m_["fraction"].items()))
                         + f"  readable {m_['readable']}")
            if not m_["readable"]:
                ok4 = False
    out.append({"id": "M4", "measured": "; ".join(lines),
                "verdict": "MET -- every arm's floor sits below its own spread, so the ceiling can be formed" if ok4
                else "FALSIFIER FIRED -- an arm's test-set floor is at or above its own spread"})
    return out


def report(rows: dict) -> int:
    names = [Path(p).name for p in RUNS + (ACROSS,)]
    print("== the runs, by arm and pair ==")
    for n in names:
        if n not in rows:
            print(f"   {n}: absent")
            continue
        for metric in METRICS:
            m = rows[n][metric]
            print(f"\n   {n}  {metric}   n = {m['n']}  arms {m['arms']}")
            print("      variances " + ", ".join(f"{a} {v:.6f}" for a, v in sorted(m["variance"].items())))
            for pair in list(PAIRS) + [PENALTY_PAIR]:
                if pair not in m["corr"]:
                    continue
                print(f"      {pair[0]:16} against {pair[1]:16}  corr {m['corr'][pair]:+.3f}   ceiling "
                      f"{m['ceiling'][pair]:.3f}   excess {m['excess'][pair]:+.3f}")
            print(f"      test-set fractions " + ", ".join(f"{a} {v:.2f}" for a, v in sorted(m["fraction"].items())))

    print("\n== the two matched runs, side by side ==")
    present = [n for n in names[:2] if n in rows]
    if len(present) == 2:
        for metric in METRICS:
            a, b = rows[present[0]][metric], rows[present[1]][metric]
            print(f"   {metric}")
            for pair in PAIRS:
                va, vb = a["corr"].get(pair), b["corr"].get(pair)
                band = fisher_band(a["n"], (va + vb) / 2) if va is not None and vb is not None else float("nan")
                print(f"      {pair[0]:16} against {pair[1]:16}  {va:+.3f} against {vb:+.3f}   "
                      f"delta {abs((va or 0) - (vb or 0)):.3f}  95% band {band:.3f}")
    else:
        print(f"   present: {present} -- the comparison needs both")

    print("\n== the registered claims, M1-M4 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (two runs at matched settings were bought to ask whether one configuration fixes the ordering, and the")
    print("    arm the corpus carries at five replicates is here at sixteen so the penalty form can be separated)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = readings()
    if args.json_out:
        write_json(args.json_out, {"runs": list(RUNS), "across": ACROSS, "metrics": list(METRICS),
                                   "readings": {n: {m: {k: (v if not isinstance(v, dict) else
                                                            {"/".join(k2) if isinstance(k2, tuple) else k2: v2
                                                             for k2, v2 in v.items()})
                                                       for k, v in mm.items()}
                                                   for m, mm in r.items()} for n, r in rows.items()},
                                   "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
