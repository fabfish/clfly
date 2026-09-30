"""E295 -- which metric selects the basis: the block penalty is ahead on accuracy in 21 of 26 comparisons and on forgetting in none of the resolved ones.

The project's question is *"which anchoring basis minimises forgetting"*, and the comparison that carries it is the
one between the two penalty arms: `ewc` anchors its Fisher in the neuron coordinate basis and `ewc-block` anchors it
in the within-group blocks of an annotated partition -- the cell-class basis the paper's recommendation is about. Both
arms ran in **26 artifacts**, with the same seeds inside each one, so every comparison is paired over replicates and
the corpus can be read as a whole for the first time here.

The two metrics pull in opposite directions, so the sign convention is stated rather than assumed: **higher is better
for `final_accuracy` and lower is better for `mean_forgetting`**, and "ahead" below means better *on that metric*.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **B1 -- on accuracy the block penalty is ahead nearly everywhere.** It is better in most of the 26 comparisons and
  in most of those resolved at two sigma. **Falsifier**: ahead in fewer than half.
- **B2 -- and on forgetting it is ahead in none of the resolved ones.** It is better on `mean_forgetting` in well
  under half of the comparisons, and **every** comparison resolved at two sigma is one where the *diagonal* arm
  forgets less. **Falsifier**: ahead in most, or ahead in one of the resolved ones.
- **B3 -- so the metrics do not select the same arm.** Over the artifacts carrying both metrics, the two disagree
  about which arm is ahead in a substantial minority. **Falsifier**: they disagree in fewer than a quarter.

**What the three add up to, and why it matters.** The corpus's headline metric is forgetting -- the paper's question
is phrased in it and the basis study is built on it -- and the block penalty **loses every resolved comparison** on
it, while winning eight of the nine resolved accuracy comparisons. So the recommendation the paper draws (anchor in
the partition's blocks) is supported by the metric the paper does *not* phrase its question in, and a reader who
takes accuracy as the objective and forgetting as the objective will select different bases from the same artifacts.
That is the same shape as `e276`'s finding one arm over (replay beats the penalty on both), and it is the first time
the corpus's own two metrics have been put side by side across the whole arm set.

**What it cannot do.** *The 26 artifacts are not 26 configurations*: the same configuration recurs, so the counts
weight whatever the corpus happens to have run more than once, and `e276`'s replay arm is not in this comparison at
all. *The arms are paired within an artifact and not across them*, so a delta measures `ewc - ewc-block` at one
configuration and the population of deltas is not a sample of anything. *A sigma below two is not evidence of
equality*: 11 of 26 accuracy comparisons and 23 of 26 forgetting comparisons are unresolved, and B3 counts
disagreements of *sign* whether or not either side is resolved. *The `mean_forgetting` of a well-trained short
sequence is a small number* -- the three resolved deltas are -0.008 to -0.027 -- so the metric that decides the
question is the one with the smaller dynamic range, and nothing here rescales it. *And the artifacts span four days of
runner changes*, including the `evaluation_noise` formula's own epochs, so an artifact from an earlier epoch
contributes a comparison of the same quantity computed by slightly different means.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: The two arms of the project's own comparison, and the sign that makes a delta "better for the block arm".
A, B = "ewc", "ewc-block"
BETTER = {"final_accuracy": 1.0, "mean_forgetting": -1.0}
RESOLVED = 2.0
#: The minimum replicates a comparison needs to be read.
MIN_REPLICATES = 3
#: The share of artifacts on which the two metrics may agree for B3 to fail.
AGREEMENT = 0.75
CLAIMS = (
    ("B1", "on accuracy the block penalty is ahead nearly everywhere",
     "It is better on final_accuracy in most of the comparisons and in most of those resolved at two sigma",
     "falsifier: ahead in fewer than half"),
    ("B2", "and on forgetting it is ahead in none of the resolved ones",
     "It is better on mean_forgetting in fewer than half, and in none of those resolved at two sigma",
     "falsifier: ahead in most, or ahead in a resolved one"),
    ("B3", "so the metrics do not select the same arm",
     "Over the artifacts carrying both metrics, the two disagree about which arm is ahead in more than a quarter",
     "falsifier: they disagree in fewer than a quarter"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def contrast(d: dict, a: str, b: str, metric: str, minimum: int = MIN_REPLICATES) -> dict | None:
    """The paired difference A minus B over the replicates the two arms share, by position."""
    xa = [r[metric] for r in d["methods"][a]["replicates"]]
    xb = [r[metric] for r in d["methods"][b]["replicates"]]
    n = min(len(xa), len(xb))
    if n < minimum:
        return None
    diffs = [xa[i] - xb[i] for i in range(n)]
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(n)
    # a sem of numerically zero is a degenerate comparison and not an infinitely resolved one
    if not sem or sem < 1e-12:
        return None
    return {"delta": mean, "sem": sem, "sigma": abs(mean) / sem, "n": n,
            "negative": sum(1 for x in diffs if x < 0),
            #: whether the *block* arm is better, which depends on the metric's direction
            "block_ahead": BETTER[metric] * mean < 0}


def comparisons(root: Path = RUNS, collapse: bool = True) -> list[dict]:
    """Every artifact that ran both arms, one row per metric.

    ``collapse`` drops the corpus's second copies of an experiment it already holds (`e301`, `corpus.repeat_paths`),
    because a census that counts files counts the same comparison twice whenever a configuration was executed
    twice -- and the second copy carries the same numbers, so it changes the denominator and never the finding.
    """
    out = []
    skip = corpus.repeat_paths(root) if collapse else set()
    for p in sorted(root.glob("*.json")):
        if p.name in skip:
            continue
        d = load(p)
        if d is None:
            continue
        meth = d.get("methods")
        if not isinstance(meth, dict) or A not in meth or B not in meth:
            continue
        cfg = d.get("config") or {}
        for metric in BETTER:
            c = contrast(d, A, B, metric)
            if c is None:
                continue
            out.append({"artifact": p.name, "metric": metric, "readout": cfg.get("readout_size"),
                        "overlap": cfg.get("input_overlap"), "frozen": bool(cfg.get("frozen_body")),
                        "lam": cfg.get("lam"), **c})
    return out


def by_metric(rows: list[dict]) -> dict:
    out = {}
    for metric in BETTER:
        sub = [r for r in rows if r["metric"] == metric]
        ahead = [r for r in sub if r["block_ahead"]]
        out[metric] = {"comparisons": len(sub), "ahead": len(ahead),
                       "rate": len(ahead) / len(sub) if sub else None,
                       "resolved": sum(1 for r in sub if r["sigma"] >= RESOLVED),
                       "resolved_ahead": sum(1 for r in sub if r["sigma"] >= RESOLVED and r["block_ahead"]),
                       "largest_ahead": max((r["sigma"] for r in ahead), default=None),
                       "largest_behind": max((r["sigma"] for r in sub if not r["block_ahead"]), default=None)}
    return out


def disagreement(rows: list[dict]) -> dict:
    """On how many artifacts do the two metrics pick different arms?"""
    by: dict[str, dict] = {}
    for r in rows:
        by.setdefault(r["artifact"], {})[r["metric"]] = r
    both = {k: v for k, v in by.items() if len(v) == len(BETTER)}
    differ = [k for k, v in both.items() if len({x["block_ahead"] for x in v.values()}) > 1]
    return {"artifacts": len(both), "differ": len(differ), "examples": sorted(differ)[:6],
            "rate": len(differ) / len(both) if both else None}


def judge(r: dict) -> list[dict]:
    rows = (r or {}).get("comparisons") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact ran both arms"} for c in CLAIMS]

    acc, fgt = r["by_metric"]["final_accuracy"], r["by_metric"]["mean_forgetting"]
    acc_res = [x for x in rows if x["metric"] == "final_accuracy" and x["sigma"] >= RESOLVED]
    out = [{"id": "B1", "measured": f"on final_accuracy the block arm is ahead in {acc['ahead']} of "
                                     f"{acc['comparisons']} comparisons ({100 * acc['rate']:.0f}%), and in "
                                     f"{acc['resolved_ahead']} of the {len(acc_res)} resolved at two sigma; the "
                                     f"largest comparison against it is {acc['largest_behind']:.2f} sigma",
            "verdict": "MET -- the block penalty wins the accuracy metric" if acc["rate"] > 0.5 and
                       acc["resolved_ahead"] * 2 > len(acc_res) else
                       f"FALSIFIER FIRED -- {acc['ahead']} of {acc['comparisons']}"}]

    fgt_res = [x for x in rows if x["metric"] == "mean_forgetting" and x["sigma"] >= RESOLVED]
    fgt_ahead_res = [x for x in fgt_res if x["block_ahead"]]
    out.append({"id": "B2", "measured": f"on mean_forgetting the block arm is ahead in {fgt['ahead']} of "
                                        f"{fgt['comparisons']} ({100 * fgt['rate']:.0f}%), and in "
                                        f"{len(fgt_ahead_res)} of the {len(fgt_res)} resolved: "
                                        + "; ".join(f"{x['artifact'][:30]} {x['delta']:+.5f} at {x['sigma']:.2f} sigma"
                                                    for x in fgt_res),
                "verdict": "MET -- the diagonal arm forgets less in every resolved comparison" if
                           fgt["rate"] < 0.5 and not fgt_ahead_res else
                           f"FALSIFIER FIRED -- {fgt['ahead']} of {fgt['comparisons']}, {len(fgt_ahead_res)} resolved"})

    d = r["disagreement"]
    out.append({"id": "B3", "measured": f"the two metrics pick different arms on {d['differ']} of the {d['artifacts']} "
                                        f"artifacts carrying both ({100 * d['rate']:.0f}%); "
                                        f"e.g. {', '.join(x[:28] for x in d['examples'][:3])}",
                "verdict": "MET -- the corpus's two metrics do not select the same arm" if d["rate"] > 1 - AGREEMENT
                else f"FALSIFIER FIRED -- they differ on {100 * d['rate']:.0f}%"})
    return out


def report(r: dict) -> int:
    print("== the project's own comparison, over every artifact that ran both arms ==")
    print(f"   A = `{A}` (the coordinate basis), B = `{B}` (the partition's blocks); delta is A minus B, and")
    print("   'ahead' means better on that metric: higher is better for final_accuracy, lower for mean_forgetting")
    for metric, s in r["by_metric"].items():
        print(f"\n   {metric:18} comparisons {s['comparisons']:3}  block ahead {s['ahead']:3} "
              f"({100 * s['rate']:3.0f}%)  resolved at two sigma {s['resolved']:3}  of those ahead "
              f"{s['resolved_ahead']:2}  largest for it {s['largest_ahead']:.2f} sigma  largest against it "
              f"{s['largest_behind']:.2f}")
    print("\n== the resolved comparisons, arm by arm ==")
    for metric in BETTER:
        for x in sorted([y for y in r["comparisons"] if y["metric"] == metric and y["sigma"] >= RESOLVED],
                        key=lambda y: -y["sigma"]):
            print(f"   {metric:18} {x['sigma']:6.2f}  delta {x['delta']:+.5f}  block ahead {str(x['block_ahead']):5} "
                  f" n {x['n']:3}  {x['artifact'][:44]}")

    print(f"\n== and where the two metrics disagree: {r['disagreement']['differ']} of "
          f"{r['disagreement']['artifacts']} artifacts ==")
    for name in r["disagreement"]["examples"]:
        print(f"   {name}")

    print("\n== the registered claims, B1-B3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the basis question is phrased in forgetting and the block anchoring loses every resolved")
    print("    comparison on it, while winning the accuracy metric -- the two objectives select different bases)")
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
    rows = comparisons(args.runs)
    r = {"comparisons": rows, "by_metric": by_metric(rows) if rows else {},
         "disagreement": disagreement(rows) if rows else {},
         "a": A, "b": B, "resolved_at": RESOLVED}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
