"""E296 -- the matched-random control: what the biological partition buys over a random one of the same size.

`e295` read the project's own comparison -- the block-anchored penalty against the diagonal -- across every artifact
that ran both arms, and found the block arm ahead on accuracy in 21 of 26 comparisons and behind on forgetting in all
three of the resolved ones. But that comparison is between *anchoring structures*, and the corpus's design has a
control for the biological part of it: **`ewc-block-rand`**, the same penalty on a **matched random partition** with
the same group sizes. If the biological grouping carries the effect, the block arm should beat its own random control;
if grouping at all is what matters, it should not. Forty artifacts ran both arms.

Three claims, all **confirmatory** and computed in the exploration that wrote the module. The sign convention is
stated rather than assumed: delta is `ewc-block` minus `ewc-block-rand`, and "ahead" means better on that metric --
higher for `final_accuracy`, **lower** for `mean_forgetting`.

- **C1 -- on accuracy the biological partition is ahead in most comparisons.** **Falsifier**: ahead in fewer than
  half.
- **C2 -- and on forgetting it is ahead in about half.** The control does not separate the two arms on the metric the
  project's question is phrased in. **Falsifier**: ahead in two thirds or more.
- **C3 -- and no resolved comparison with forty replicates favours it.** The resolved comparisons that go its way rest
  on three or sixteen replicates, and the only resolved one at forty goes the other way. **Falsifier**: one resolved
  comparison with forty or more replicates favours the biological block.

**What the three add up to, and the direction the data took.** The claims above were registered in the direction the
mechanism suggests -- that the biological grouping is what carries the effect -- and **two of the three fired**:

  * **on accuracy the biological partition is ahead in only 15 of the 40 comparisons (38%)**, so a random partition of
    matched size is the more accurate arm by count; the single largest resolved accuracy comparison (4.35 sigma,
    `e102_rate_fb8_omp1`) does favour the biological partition, and it is one of only 5 resolved;
  * **on forgetting the biological partition is ahead in 18 of 40 (45%)**, and **both** comparisons resolved at two
    sigma with forty replicates favour it (`e140_r32_methods_plastic_40reps` at 2.08 and `e275_frozenbias_suite600_40reps`
    at 2.19) -- so where the power is, the biological grouping does buy forgetting against a random one.

**Set beside `e295`, the corpus's three penalty arms form a cycle rather than an order**: the block penalty beats the
diagonal on accuracy and loses to it on forgetting; it beats its matched random control on forgetting and loses to it
on accuracy by count. So *"which anchoring basis minimises forgetting"* has no answer without saying **against what**
and **in which metric**, and the two comparisons the paper leans on point in opposite directions on both metrics.

**What it cannot do.** *The two arms differ in the partition and in nothing else only if the runner's control is what
it says it is*, and this unit reads the artifacts' own `basis` field rather than re-deriving the matched partition;
`e266`'s two seeds and `e144`'s draw pairs are the corpus's own controls for that. *The matched random partition is
one draw per artifact*, so the control comparison carries the random partition's own draw error, which `e286` showed
can move a spread by 1.6x to 5.5x -- and the corpus records the random draw's seed without having measured its
spread. *Forty comparisons are not forty configurations*: the same configuration recurs and the counts weight whatever
was run more than once. *A sigma below two is not equality*, and most of the resolved comparisons rest on three
replicates, where a paired sem carries about half its own value -- which is why C3 is stated at forty and not at five.
*And the `e102` artifacts carrying the largest accuracy comparison are batch-count variants* whose sign the corpus's
own plan row already reports as unstable, so the largest resolved accuracy comparison is the least stable one.

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
#: The biological partition and its matched random control.
A, B = "ewc-block", "ewc-block-rand"
#: Whether a **larger** value is better, per metric. `ahead` below then means **A** is better than B, which is the
#: opposite convention to `e295`'s -- there the field was named for the second arm. Getting this backwards inverts
#: every count in the unit, so it is a named constant and the tests assert it against a fixture built the other way.
HIGHER_IS_BETTER = {"final_accuracy": True, "mean_forgetting": False}
#: The comparison `e295` read, for the magnitudes the report puts beside these.
DIAGONAL = ("ewc", "ewc-block")
RESOLVED = 2.0
MIN_REPLICATES = 3
#: The replicate count above which a resolved comparison is called well powered, and the rate C2 allows.
POWERED = 40
MAJORITY = 2 / 3
CLAIMS = (
    ("C1", "on accuracy the biological partition is ahead in most comparisons",
     "It is better on final_accuracy in more than half of them",
     "falsifier: ahead in fewer than half"),
    ("C2", "and on forgetting it is ahead in about half",
     "It is better on mean_forgetting in fewer than two thirds",
     "falsifier: ahead in two thirds or more"),
    ("C3", "and no resolved comparison with forty replicates favours it",
     f"No comparison resolved at {RESOLVED} sigma with {POWERED} or more replicates has it ahead",
     "falsifier: one does"),
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
    if not sem or sem < 1e-12:
        return None
    return {"delta": mean, "sem": sem, "sigma": abs(mean) / sem, "n": n,
            "ahead": (mean > 0) if HIGHER_IS_BETTER[metric] else (mean < 0)}


def comparisons(root: Path = RUNS, pair=(A, B), collapse: bool = True) -> list[dict]:
    """Every artifact that ran both arms of `pair`, one row per metric.

    ``collapse`` drops the corpus's second copies of an experiment it already holds (`e301`), so that a
    configuration executed twice does not cast two votes in a count. The second copy carries the first copy's
    numbers, so the count moves and the rate does not.
    """
    a, b = pair
    out = []
    skip = corpus.repeat_paths(root) if collapse else set()
    for p in sorted(root.glob("*.json")):
        if p.name in skip:
            continue
        d = load(p)
        if d is None:
            continue
        meth = d.get("methods")
        if not isinstance(meth, dict) or a not in meth or b not in meth:
            continue
        #: An entry without `replicates` is not an arm: an analysis artifact reusing the key is not a run
        if any(not isinstance(meth.get(k), dict) or not isinstance(meth[k].get("replicates"), list)
               for k in (a, b)):
            continue
        cfg = d.get("config") or {}
        for metric in HIGHER_IS_BETTER:
            c = contrast(d, a, b, metric)
            if c is None:
                continue
            out.append({"artifact": p.name, "metric": metric, "readout": cfg.get("readout_size"),
                        "overlap": cfg.get("input_overlap"), "basis": cfg.get("basis"),
                        "fisher_batches": cfg.get("fisher_batches"), **c})
    return out


def by_metric(rows: list[dict]) -> dict:
    out = {}
    for metric in HIGHER_IS_BETTER:
        sub = [r for r in rows if r["metric"] == metric]
        resolved = [r for r in sub if r["sigma"] >= RESOLVED]
        out[metric] = {
            "comparisons": len(sub), "ahead": sum(1 for r in sub if r["ahead"]),
            "rate": (sum(1 for r in sub if r["ahead"]) / len(sub)) if sub else None,
            "resolved": len(resolved), "resolved_ahead": sum(1 for r in resolved if r["ahead"]),
            "resolved_ahead_replicates": sorted(r["n"] for r in resolved if r["ahead"]),
            "resolved_against_replicates": sorted(r["n"] for r in resolved if not r["ahead"]),
            "largest": max((r["sigma"] for r in sub), default=None),
            "largest_ahead": max((r["sigma"] for r in sub if r["ahead"]), default=None),
            "largest_against": max((r["sigma"] for r in sub if not r["ahead"]), default=None),
        }
    return out


def judge(r: dict) -> list[dict]:
    rows = (r or {}).get("comparisons") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no artifact ran both arms"} for c in CLAIMS]

    acc = r["by_metric"]["final_accuracy"]
    fgt = r["by_metric"]["mean_forgetting"]
    out = [{"id": "C1", "measured": f"on final_accuracy the biological partition is ahead in {acc['ahead']} of "
                                     f"{acc['comparisons']} ({100 * acc['rate']:.0f}%), {acc['resolved_ahead']} of "
                                     f"{acc['resolved']} resolved; largest for it {acc['largest_ahead']:.2f}, against "
                                     f"it {acc['largest_against']:.2f}",
            "verdict": "MET -- the control shows an accuracy effect for the biological partition" if
                       acc["rate"] > 0.5 else f"FALSIFIER FIRED -- {acc['ahead']} of {acc['comparisons']}"}]

    out.append({"id": "C2", "measured": f"on mean_forgetting it is ahead in {fgt['ahead']} of {fgt['comparisons']} "
                                        f"({100 * fgt['rate']:.0f}%), {fgt['resolved_ahead']} of {fgt['resolved']} "
                                        f"resolved; largest for it {fgt['largest_ahead']:.2f}, against it "
                                        f"{fgt['largest_against']:.2f}",
                "verdict": "MET -- the control does not separate the arms on the metric the question is phrased in"
                if fgt["rate"] < MAJORITY else f"FALSIFIER FIRED -- {100 * fgt['rate']:.0f}% ahead"})

    powered = [x for x in rows if x["sigma"] >= RESOLVED and x["n"] >= POWERED]
    favouring = [x for x in powered if x["ahead"]]
    against = [x for x in powered if not x["ahead"]]
    named = "; ".join(f"{x['artifact'][:34]} {x['metric']} n {x['n']} {x['delta']:+.5f} at {x['sigma']:.2f}"
                      for x in powered)
    out.append({"id": "C3", "measured": f"{len(powered)} comparison(s) resolved at {RESOLVED} sigma with {POWERED} or "
                                        f"more replicates, of which {len(favouring)} favour the biological partition: "
                                        f"{named or 'none'}",
                "verdict": "MET -- the well-powered resolved comparison goes against the biological partition"
                if powered and not favouring else
                (f"FALSIFIER FIRED -- {len(favouring)} of {len(powered)} favour it" if powered
                 else "FALSIFIER FIRED -- no comparison resolved at that power")})
    return out


def report(r: dict) -> int:
    print("== the biological partition against its matched random control ==")
    print(f"   A = `{A}`, B = `{B}`; delta is A minus B, and ahead means better on that metric")
    for metric, s in r["by_metric"].items():
        print(f"\n   {metric:18} comparisons {s['comparisons']:3}  A ahead {s['ahead']:3} ({100 * s['rate']:3.0f}%)  "
              f"resolved {s['resolved']:2}  ahead {s['resolved_ahead']:2}")
        print(f"      replicates of the resolved ones that favour A: {s['resolved_ahead_replicates']};  "
              f"against A: {s['resolved_against_replicates']}")

    print("\n== the resolved comparisons ==")
    for x in sorted([y for y in r["comparisons"] if y["sigma"] >= RESOLVED], key=lambda y: -y["sigma"]):
        print(f"   {x['metric']:18} {x['sigma']:6.2f}  delta {x['delta']:+.5f}  ahead {str(x['ahead']):5}  n {x['n']:3}  "
              f"readout {str(x['readout']):5}  basis {str(x['basis']):22}  {x['artifact'][:34]}")

    print("\n== and the same artifacts' diagonal comparison, for the magnitudes ==")
    diag = comparisons(pair=DIAGONAL)
    for metric, s in by_metric(diag).items():
        print(f"   {metric:18} comparisons {s['comparisons']:3}  resolved {s['resolved']:2}  "
              f"largest {s['largest']:.2f} sigma  (that is `{DIAGONAL[0]}` against `{DIAGONAL[1]}`)")

    print("\n== the registered claims, C1-C3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the three penalty arms form a cycle rather than an order: the block penalty beats the diagonal on")
    print("    accuracy and loses to it on forgetting, and beats its random control on forgetting while losing to it")
    print("    on accuracy by count -- so the basis question has no answer without naming the comparator and the metric)")
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
    diag = by_metric(comparisons(args.runs, pair=DIAGONAL))
    r = {"comparisons": rows, "by_metric": by_metric(rows) if rows else {},
         "a": A, "b": B, "resolved_at": RESOLVED, "powered": POWERED,
         "diagonal": {"pair": list(DIAGONAL), "by_metric": diag}}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
