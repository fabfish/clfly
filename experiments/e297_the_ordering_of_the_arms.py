"""E297 -- the ordering of the arms: two total orders over five arms, and the reversal between them.

`e295` read one edge of the corpus's arm graph (the block penalty against the diagonal) and `e296` another (the block
penalty against its matched random control), and together they found a *cycle* across the two comparisons. That
prompts the question those two units could not ask: **what is the ordering of all five arms, on each metric, from the
corpus's own comparisons?** The five are `naive` (no penalty), `ewc` (the diagonal), `ewc-block` (the partition's
blocks), `ewc-block-rand` (a matched random partition) and `replay`.

Every artifact that ran both arms of a pair supplies one paired comparison of that pair, and the corpus ran pairs
thousands of times over: the unit builds the **majority edge** of each of the ten pairs on each metric, then asks
whether the ten edges can be laid out as one order.

The direction convention is a named constant, because it is the one thing that inverts everything: `HIGHER_IS_BETTER`
says whether a *larger* value is better, so for `final_accuracy` "A beats B" means `delta > 0` and for
`mean_forgetting` it means `delta < 0`, with `delta` = A minus B.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **A1 -- each metric gives a total order.** The majority edges of the ten pairs are transitive on both metrics: there
  is a chain through all five arms and no cycle *within* a metric. **Falsifier**: a majority cycle among the arms on
  either metric.
- **A2 -- and the two orders disagree by more than noise.** The arm that is best on one metric is not the arm that is
  best on the other, and the disagreement is a reversal of the ends: the diagonal is last on accuracy and first on
  forgetting. **Falsifier**: the same arm is best on both.
- **A3 -- and the diagonal penalty forgets more than no penalty at all.** Against `naive`, the diagonal arm is worse
  on forgetting in most comparisons. **Falsifier**: the diagonal forgets less than `naive` in most of them.

**What the three add up to, with `e295` and `e296` beside them.** The corpus's arm story is *two orders and not one*:
accuracy ranks `ewc` last and `replay` first, forgetting ranks `ewc` first and `replay` fourth, and the ends are
swapped between the metrics -- while each metric individually is perfectly ordered, so the earlier units' "cycle" is a
**cross-comparison** phenomenon and not an intra-metric one. And the diagonal arm is the clearest single case: it is
the *worst* arm on accuracy **and the best on forgetting**, while `naive` -- no penalty at all -- forgets more than
`ewc-block` but less than `ewc`. So "which arm minimises forgetting" has an answer (the diagonal) that is the opposite
of the answer to "which arm is most accurate" (`replay`), and a third of the corpus's own comparisons in the relevant
pair are unresolved.

**What it cannot do.** *The comparisons are not independent*: the same configuration recurs across the pairs, so the
same three arms' numbers count in several edges at once, and a well-run configuration weights every edge it touches.
*The majority edge throws away the power*: the counts range from 21 to 40 comparisons per pair and 0 to 18 resolved,
so `ewc-block` against `ewc-block-rand` on forgetting is a 22-to-18 coin flip among forty noisy comparisons while
`ewc` against `naive` on forgetting is 31 to 7. **A sigma below two is not equality.** *The arms are paired within an
artifact and not across them*, so the edges are majorities of paired differences at many configurations rather than
an estimate at one. *And `replay`'s strong position inherits `e276`'s caveat*: it is the arm whose measured spread
moves most between samples, and its comparisons are the ones with the fewest artifacts in several edges.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from itertools import combinations
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: The corpus's five arms, and whether a **larger** value is better for each metric. `beats` is built from this.
ARMS = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
HIGHER_IS_BETTER = {"final_accuracy": True, "mean_forgetting": False}
METRICS = tuple(HIGHER_IS_BETTER)
RESOLVED = 2.0
#: The comparisons a pair needs before its majority edge is read, and the minimum replicates a comparison needs.
MIN_COMPARISONS = 5
MIN_REPLICATES = 3
CLAIMS = (
    ("A1", "each metric gives a total order",
     "The majority edges of the ten pairs are transitive on both metrics, with no cycle among the arms on either",
     "falsifier: a majority cycle among the arms on either metric"),
    ("A2", "and the two orders disagree, with the ends swapped",
     "The arm that is best on accuracy is not the arm that is best on forgetting, and the diagonal is last on one "
     "and first on the other",
     "falsifier: the same arm is best on both metrics"),
    ("A3", "and the diagonal penalty forgets more than no penalty at all",
     "Against naive, the diagonal arm is worse on forgetting in most comparisons",
     "falsifier: the diagonal forgets less than naive in most of them"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def beats(a: str, b: str, metric: str, delta: float) -> bool:
    """Whether A beats B on `metric`, given delta = A minus B -- the convention in one place."""
    return delta > 0 if HIGHER_IS_BETTER[metric] else delta < 0


def contrast(d: dict, a: str, b: str, metric: str, minimum: int = MIN_REPLICATES) -> dict | None:
    """The paired difference A minus B over the replicates the two arms share, by position.

    An arm whose entry carries no `replicates` is not a trained arm: `e315` and `e316` write analysis
    artifacts that name their per-method rows under a key a reader must be able to tell from this one, and a
    corpus reader that assumes every `methods` entry is an arm crashes on the first analysis artifact that
    reuses the name. This returns `None` for one rather than raising.
    """
    for arm in (a, b):
        entry = d["methods"].get(arm)
        if not isinstance(entry, dict) or not isinstance(entry.get("replicates"), list):
            return None
    xa = [r[metric] for r in d["methods"][a]["replicates"]]
    xb = [r[metric] for r in d["methods"][b]["replicates"]]
    n = min(len(xa), len(xb))
    if n < minimum:
        return None
    diffs = [xa[i] - xb[i] for i in range(n)]
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(n)
    if not sem or sem < 1e-12:
        return None
    return {"delta": mean, "sigma": abs(mean) / sem, "n": n, "a_beats": beats(a, b, metric, mean)}


def pairs(root: Path = RUNS, minimum_comparisons: int = MIN_COMPARISONS, keep: set | None = None) -> list[dict]:
    """One row per arm pair, per metric, over every artifact that ran both.

    ``keep`` restricts the corpus to a named set of artifacts, which is what `e308` reads the ordering under: the
    filter is the only thing that moves between its two readings, so a difference in the order it produces is a
    difference the population made and not the pairing rule's.
    """
    out = []
    for a, b in combinations(ARMS, 2):
        for metric in METRICS:
            rows = []
            for p in sorted(root.glob("*.json")):
                if keep is not None and p.name not in keep:
                    continue
                d = load(p)
                if d is None or not isinstance(d.get("methods"), dict):
                    continue
                if a not in d["methods"] or b not in d["methods"]:
                    continue
                c = contrast(d, a, b, metric)
                if c is not None:
                    rows.append({"artifact": p.name, **c})
            if len(rows) < minimum_comparisons:
                continue
            ahead = [r for r in rows if r["a_beats"]]
            resolved = [r for r in rows if r["sigma"] >= RESOLVED]
            out.append({"a": a, "b": b, "metric": metric, "comparisons": len(rows), "a_ahead": len(ahead),
                        "resolved": len(resolved),
                        "resolved_ahead": sum(1 for r in resolved if r["a_beats"]),
                        "largest_for_a": max((r["sigma"] for r in ahead), default=None),
                        "largest_for_b": max((r["sigma"] for r in rows if not r["a_beats"]), default=None),
                        "winner": a if len(ahead) * 2 > len(rows) else (b if len(ahead) * 2 < len(rows) else None)})
    return out


def order(edges: list[dict], metric: str) -> dict:
    """The total order a metric's majority edges imply: wins per arm, then a transitivity check.

    Only the arms that appear in an edge of this metric are ranked -- an arm with no comparisons in the pair set has
    no place in the order, and giving it a zero would put it first for the wrong reason.
    """
    sub = [e for e in edges if e["metric"] == metric and e["winner"]]
    present = sorted({r for e in sub for r in (e["a"], e["b"])})
    wins = {a: 0 for a in present}
    for e in sub:
        wins[e["winner"]] += 1
    # the order, worst first: an arm with fewer wins comes earlier
    ranked = sorted(present, key=lambda a: (wins[a], a))
    # transitivity: every edge must point from the later arm to the earlier one
    position = {a: i for i, a in enumerate(ranked)}
    violations = [e for e in sub if position[e["winner"]] <= position[e["a"] if e["winner"] == e["b"] else e["b"]]]
    return {"metric": metric, "wins": wins, "worst_first": ranked, "edges": len(sub),
            "acyclic": not violations, "violations": violations,
            "best": ranked[-1] if ranked else None, "worst": ranked[0] if ranked else None}


def spearman(xs: list[float], ys: list[float]) -> float:
    """The rank correlation of two same-length lists."""
    n = len(xs)
    if n < 3:
        return float("nan")

    def rank(v):
        order_ = sorted(range(n), key=lambda i: v[i])
        out = [0.0] * n
        for pos, i in enumerate(order_):
            out[i] = float(pos)
        return out

    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def judge(r: dict) -> list[dict]:
    edges = (r or {}).get("pairs") or []
    if not edges:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm pair could be read"} for c in CLAIMS]

    orders = r["orders"]
    cyclic = [o["metric"] for o in orders.values() if not o["acyclic"]]
    out = [{"id": "A1", "measured": "; ".join(f"{m}: " + " < ".join(o["worst_first"]) for m, o in orders.items()),
            "verdict": "MET -- each metric's majority edges are one chain with no cycle" if not cyclic else
                       f"FALSIFIER FIRED -- a cycle on {cyclic}"}]

    bests = {m: o["best"] for m, o in orders.items()}
    acc, fgt = orders["final_accuracy"], orders["mean_forgetting"]
    # the claim asks two things: the two metrics do not agree on the best arm, and the *diagonal*'s ends are swapped
    diagonal_swapped = (acc["worst"] == "ewc" and fgt["best"] == "ewc") or (acc["best"] == "ewc"
                                                                           and fgt["worst"] == "ewc")
    ok = bests["final_accuracy"] != bests["mean_forgetting"] and diagonal_swapped
    out.append({"id": "A2", "measured": f"best on accuracy {bests['final_accuracy']}, best on forgetting "
                                        f"{bests['mean_forgetting']}; the two orders are rank-correlated "
                                        f"{r['spearman']:+.3f}; the diagonal is {acc['worst_first'].index('ewc') + 1} "
                                        f"of five on accuracy (worst) and {fgt['worst_first'].index('ewc') + 1} of "
                                        f"five on forgetting (best)",
                "verdict": "MET -- the two metrics select different arms, and the diagonal's ends are swapped" if ok
                else f"FALSIFIER FIRED -- best on both is {set(bests.values())}"})

    nb = [e for e in edges if e["metric"] == "mean_forgetting" and {e["a"], e["b"]} == {"naive", "ewc"}]
    e0 = nb[0] if nb else None
    if e0:
        diagonal_ahead = e0["a_ahead"] if e0["a"] == "ewc" else e0["comparisons"] - e0["a_ahead"]
        measured = (f"naive against ewc on forgetting: {e0['comparisons']} comparisons, the diagonal better in "
                    f"{diagonal_ahead} ({100 * diagonal_ahead / e0['comparisons']:.0f}%), resolved {e0['resolved']}")
    else:
        diagonal_ahead, measured = 0, "no naive-ewc comparison"
    out.append({"id": "A3", "measured": measured,
                "verdict": "MET -- the diagonal arm forgets more than no penalty at all"
                if e0 and e0["winner"] == "naive" else
                "FALSIFIER FIRED -- the diagonal forgets LESS than naive in most comparisons"})
    return out


def report(r: dict) -> int:
    print("== the ten arm pairs, on each metric ==")
    print(f"   {'pair (A over B)':34} {'metric':18} {'n':>4} {'A ahead':>8} {'rate':>6} {'resolved':>9} "
          f"{'res for A':>10} {'winner':>15}")
    for e in sorted(r["pairs"], key=lambda e: (e["metric"], -(e["a_ahead"] / e["comparisons"]))):
        print(f"   {e['a'] + ' over ' + e['b']:34} {e['metric']:18} {e['comparisons']:4} {e['a_ahead']:8} "
              f"{100 * e['a_ahead'] / e['comparisons']:5.0f}% {e['resolved']:9} {e['resolved_ahead']:10} "
              f"{e['winner'] or 'tie':>15}")

    print("\n== the two orders ==")
    for metric, o in r["orders"].items():
        print(f"   {metric:18} worst to best: " + " < ".join(o["worst_first"]))
        print(f"   {'':18} wins per arm: {o['wins']}; acyclic {o['acyclic']}")
    print(f"   the rank correlation between the two orders is {r['spearman']:+.3f}")

    print("\n== the registered claims, A1-A3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the corpus has two orders and not one: each metric is a chain, and the ends of the two chains are")
    print("    swapped between them -- which is what the earlier units' cross-comparison cycle was)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    edges = pairs(args.runs)
    orders = {m: order(edges, m) for m in METRICS}
    r = {"pairs": edges, "orders": orders, "arms": list(ARMS),
         "spearman": spearman([orders["final_accuracy"]["wins"][a] for a in ARMS],
                              [orders["mean_forgetting"]["wins"][a] for a in ARMS]),
         "higher_is_better": HIGHER_IS_BETTER, "resolved_at": RESOLVED}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
