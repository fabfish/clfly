"""E264 -- the third arm: the shared component `e263` found is the penalty's, not the task's.

`e263` measured that the two arms of the network line's central contrast share far more of their run-to-run variance
than the benchmark's own noise decomposition can explain, and that on the forgetting metric the shared-training
component is the larger half of the pairing's benefit. It could not say **what** that component is, because the two
arms differ only in their basis and everything else -- the task, the data order, the initialisation, the test set --
is common to both.

**The artifacts carry a third arm, and it is the control that separates the two candidates.** Every run of this
contrast trained `naive` beside `ewc-block` and `ewc-block-rand`: the naive arm shares the task, the order, the
initialisation and the test set with both, and shares neither the Fisher nor the penalty. So:

    if the shared component were the TASK, all three pairwise correlations would rise together;
    if it is the PENALTY'S MACHINERY, the two EWC arms rise together and the naive arm stays apart.

The item ceiling of `e263` is reused as the reference each pair is measured against: a pair's **excess** is its
correlation minus the largest value a perfectly shared test set could give it, so a positive excess is a lower bound on
that pair's shared-training correlation.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **T1 -- the naive arm separates them on the accuracy metric.** The EWC pair's excess is positive in **two of the
  three runs** (+0.168 and +0.085) while **neither** naive pair has a positive excess in any run (they run from -0.078
  to -0.454). **Falsifier**: fewer than two runs in which the EWC excess is positive and both naive excesses are not.
- **T2 -- and the largest budget says it twice as loudly.** In the corpus's largest run (144 replicates) the EWC pair
  exceeds **both** naive pairs by more than a factor of 1.5 on **both** metrics: 0.282 against 0.124 and 0.122 on
  forgetting, 0.317 against 0.118 and 0.140 on accuracy -- factors of 2.27 to 2.69. **Falsifier**: any factor below
  1.5.
- **T3 -- so the shared component is not the task.** At that budget the EWC pair's excess is an order of magnitude
  above both naive pairs on forgetting (**0.175** against 0.013 and 0.007) while the two naive pairs sit within 0.03
  of each other on both metrics. **Falsifier**: a naive pair's excess at or above the EWC pair's in the largest run.

**What it cannot do**: the ranking across the four sixteen-replicate matrices is **not** stable -- `naive` against
`ewc-block-rand` leads on the forgetting metric in both of the small runs and the 144-replicate run does not support
it -- so T1 and T2 are statements about which pair correlates more and the small-run ordering is itself a draw; the
excess is a bound rather than an estimate, since a positive item covariance would lower it and nothing here measures
that covariance directly; the naive arm is not a *penalty* control in the strict sense (it also has no Fisher), so
"the penalty's machinery" is the reading and not a decomposition of which part; and only the three artifacts carrying
`naive` beside both EWC arms with an `evaluation_noise` block can be read at all.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: The three runs that carry `naive` beside both EWC arms, with an `evaluation_noise` block.
ARTS = ("runs/e60_side_lam0.1_16reps.json", "runs/e46_c2b_powered.json", "runs/e178_rung_side_cs300_144reps.json")
METRICS = ("final_accuracy", "mean_forgetting")
ARMS = ("naive", "ewc-block", "ewc-block-rand")
#: The pair the line's contrast is about, and the two pairs the third arm brings.
PAIR = ("ewc-block", "ewc-block-rand")
NAIVE_PAIRS = (("naive", "ewc-block"), ("naive", "ewc-block-rand"))
CLAIMS = (
    ("T1", "the naive arm separates the two candidates on the accuracy metric",
     "The EWC pair's excess over its item ceiling is positive in at least two runs while neither naive pair's excess "
     "is positive in any",
     "falsifier: fewer than two runs in which the EWC excess is positive and both naive excesses are not"),
    ("T2", "and the largest budget says it twice as loudly",
     "In the largest run the EWC pair exceeds both naive pairs by more than a factor of 1.5 on both metrics",
     "falsifier: any factor below 1.5"),
    ("T3", "so the shared component is not the task",
     "At the largest budget the EWC pair's excess is at least five times either naive pair's on forgetting, while "
     "the two naive pairs sit within 0.03 of each other on both metrics",
     "falsifier: a naive pair's excess at or above the EWC pair's in the largest run"),
)


def load(path) -> dict | None:
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
    """The three arms' full correlation matrix, each pair's item ceiling, and each pair's excess."""
    ev = d["evaluation_noise"]
    vals = {a: [r[metric] for r in d["methods"][a]["replicates"]] for a in ARMS}
    v = {a: variance(vals[a]) for a in ARMS}
    b = {a: ev[a]["binomial_sem"] ** 2 for a in ARMS}
    corr, ceiling = {}, {}
    for i, x in enumerate(ARMS):
        for y in ARMS[i:]:
            key = (x, y)
            corr[key] = covariance(vals[x], vals[y]) / math.sqrt(v[x] * v[y])
            #: the most a perfectly shared test set can contribute to this pair
            ceiling[key] = math.sqrt(b[x] * b[y]) / math.sqrt(v[x] * v[y])
    excess = {k: corr[k] - ceiling[k] for k in corr}
    return {"n": len(vals[ARMS[0]]), "variance": v, "item_variance": b, "corr": corr, "ceiling": ceiling,
            "excess": excess, "reported_pair_corr": (d.get("matched_pair") or {}).get(metric, {}).get("corr")}


def matrices() -> dict[str, dict]:
    out = {}
    for path in ARTS:
        d = load(path)
        if d is None or "evaluation_noise" not in d:
            continue
        for metric in METRICS:
            out[f"{Path(path).name}/{metric}"] = matrix(d, metric)
    return out


def _factor(m: dict, pair) -> float:
    return m["corr"][pair] / max(m["corr"][p] for p in NAIVE_PAIRS) if m["corr"][pair] > 0 else float("nan")


def largest_by_metric(rows: dict) -> dict:
    """The biggest matrix for each metric -- the one the sixteen-replicate ordering is checked against."""
    out: dict = {}
    for n, m in rows.items():
        metric = n.rsplit("/", 1)[-1]
        if metric not in out or m["n"] > out[metric]["n"]:
            out[metric] = m
    return out


def judge(rows: dict) -> list[dict]:
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact carries the third arm"} for c in CLAIMS]
    out: list[dict] = []

    acc = {n: m for n, m in rows.items() if n.endswith("final_accuracy")}
    good = [n for n, m in acc.items() if m["excess"][PAIR] > 0
            and all(m["excess"][p] <= 0 for p in NAIVE_PAIRS)]
    out.append({"id": "T1", "measured": "; ".join(
        f"{n}: EWC pair {m['excess'][PAIR]:+.3f}, naive pairs "
        + "/".join(f"{m['excess'][p]:+.3f}" for p in NAIVE_PAIRS) for n, m in sorted(acc.items())),
        "verdict": f"MET -- {len(good)} of {len(acc)} accuracy runs have the EWC pair alone above its ceiling"
        if len(good) >= 2 else f"FALSIFIER FIRED -- only {len(good)} accuracy run separates them"})

    big = largest_by_metric(rows)
    if not big:
        out.append({"id": "T2", "measured": "", "verdict": "REFUSED -- no matrix to rank"})
        out.append({"id": "T3", "measured": "", "verdict": "REFUSED -- no matrix to rank"})
        return out

    lines: list[str] = []
    ok2 = True
    for metric, m in sorted(big.items()):
        base = {p: m["corr"][p] for p in NAIVE_PAIRS}
        if min(base.values()) <= 0 or m["corr"][PAIR] <= 1.5 * max(base.values()):
            ok2 = False
        lines.append(f"{metric} at n = {m['n']}: the EWC pair {m['corr'][PAIR]:.3f} against "
                     + " and ".join(f"{p[0]}/{p[1]} {v:.3f} (factor {m['corr'][PAIR] / v:.2f})"
                                    for p, v in base.items())
                     if min(base.values()) > 0 else f"{metric} at n = {m['n']}: a naive pair is not positive")
    out.append({"id": "T2", "measured": "; ".join(lines),
                "verdict": "MET -- at the largest budget of each metric the EWC pair leads both naive pairs by more "
                           "than 1.5x" if ok2 else
                           "FALSIFIER FIRED -- a naive pair is within 1.5x of the EWC pair"})

    lines, ok3 = [], True
    for metric, m in sorted(big.items()):
        e = m["excess"][PAIR]
        naive_ex = {p: m["excess"][p] for p in NAIVE_PAIRS}
        spread = abs(m["corr"][NAIVE_PAIRS[0]] - m["corr"][NAIVE_PAIRS[1]])
        if not all(e > v for v in naive_ex.values()):
            ok3 = False
        if metric == "mean_forgetting" and not e >= 5.0 * max(naive_ex.values()):
            ok3 = False
        if not spread < 0.03:
            ok3 = False
        lines.append(f"{metric}: the EWC excess {e:+.3f} against "
                     + " and ".join(f"{p[0]}/{p[1]} {v:+.3f}" for p, v in naive_ex.items())
                     + f"; the two naive correlations sit {spread:.3f} apart")
    out.append({"id": "T3", "measured": "; ".join(lines),
                "verdict": "MET -- the shared component belongs to the penalty and not to the task"
                if ok3 else "FALSIFIER FIRED -- a naive pair's excess is not below the EWC pair's"})
    return out


def report(rows: dict) -> int:
    print("== the three arms' correlation matrix, each pair against the most a shared test set can explain ==")
    for n in sorted(rows):
        m = rows[n]
        print(f"\n   {n}   n = {m['n']}")
        print(f"      variances (biological arm first among the arms that differ only in the basis): "
              + ", ".join(f"{a} {m['variance'][a]:.6f}" for a in ARMS))
        for pair in (PAIR,) + NAIVE_PAIRS:
            x, y = pair
            print(f"      {x:16} against {y:16}  corr {m['corr'][pair]:+.3f}   item ceiling "
                  f"{m['ceiling'][pair]:.3f}   excess {m['excess'][pair]:+.3f}")
        rep = m["reported_pair_corr"]
        if rep is not None:
            print(f"      the artifact's own matched_pair correlation for {PAIR[0]} against {PAIR[1]}: {rep:+.3f} "
                  f"({'agrees' if abs(rep - m['corr'][PAIR]) < 5e-4 else 'DISAGREES'})")

    print("\n== the largest budget of each metric, where the small runs are checked ==")
    for metric, m in sorted(largest_by_metric(rows).items()):
        print(f"   {metric} at n = {m['n']}")
        for pair in (PAIR,) + NAIVE_PAIRS:
            print(f"      {pair[0]:16} against {pair[1]:16}  corr {m['corr'][pair]:+.3f}  "
                  f"excess {m['excess'][pair]:+.3f}")

    print("\n== the registered claims, T1-T3 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (all three arms share the task, the data order, the initialisation and the test set; only the two EWC")
    print("    arms share the Fisher and the penalty, which is why the third arm can say which one it is)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    rows = matrices()
    if not rows:
        raise SystemExit("need the C2b artifacts -- they are what carry the third arm")
    if args.json_out:
        write_json(args.json_out, {"arms": list(ARMS), "pair": list(PAIR),
                                   "artifact": list(ARTS),
                                   "matrices": {n: {"n": m["n"], "variance": m["variance"],
                                                    "item_variance": m["item_variance"],
                                                    "corr": {"/".join(k): v for k, v in m["corr"].items()},
                                                    "ceiling": {"/".join(k): v for k, v in m["ceiling"].items()},
                                                    "excess": {"/".join(k): v for k, v in m["excess"].items()},
                                                    "matched_pair_corr": m["reported_pair_corr"]}
                                                for n, m in rows.items()},
                                   "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
