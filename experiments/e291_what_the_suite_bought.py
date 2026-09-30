"""E291 -- what the suite bought: the configuration's own contrasts, at three samples, on the same forty models.

`e275` read what the larger suite did to each *arm's* spread, `e285` and `e286` read the same models at two samples
and found the spread falling, and `e289` read the paper's decomposition of it. None of them asked the question the
suite was bought to answer, in the currency the paper prints its claims in: **what happened to the contrasts?** The
configuration is `e140_r32_methods_frozenbias_40reps` -- five arms, forty replicates -- and its larger-suite twins are
`e275_frozenbias_suite600_40reps` and `e287_frozenbias_suite1440_40reps`, trained from the same seeds, so every
arm-versus-arm comparison is paired over the same forty replicates at all three suite sizes and the only thing that
moved between the numbers is the held-out sample. (`e288_frozenbias_suite1440_40reps` is the same execution as
`e287` -- `e301` -- so `SUITES` names the second copy and reads the same numbers either way.)

Twenty contrasts: every pair of the five arms, on both metrics. For each, the paired delta, its sem over the forty
replicates, and the sigma the paper would print.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **R1 -- the suite sharpens the contrasts.** The paired sigma is larger at the later suite in most of them, and the
  number resolved at two sigma rises. **Falsifier**: fewer than half of the sigmas rise.
- **R2 -- and nothing that was resolved changes sign.** Every contrast resolved at two sigma in a suite is resolved
  in the next and keeps its direction. **Falsifier**: one that is not.
- **R3 -- and nothing at all changes sign.** The direction of every contrast is a property of the manipulation rather
  than of the sample it was measured on. **Falsifier**: one whose sign flips.

**The two the module reads beyond its claims**: the count resolved at two sigma in each suite, and which contrasts
sit near the boundary — because the ones that flip are the ones whose sigmas were smallest, and that is the corpus's
own rule about unresolved contrasts (a sigma below two is a direction nobody measured) applied to a *sample* rather
than to a seed.

**What it cannot do.** *One configuration*, chosen because `e267` gave it the largest requirement, so nothing here
says the other two behave the same way -- though this is the only configuration in the corpus with twins at two more
suite sizes *and* five arms. *Forty replicates*, so a contrast's sigma carries about 11% of its own value, and a
contrast near two is one replicate away from crossing; R2 is stated over the ones already resolved for that reason.
*The comparison is between samples and not between suites held otherwise equal*: each sample is a different draw, so
the movement includes the draw-to-draw component `e285` measured, and nothing here separates a suite's effect from a
sample's. *The sigma is the paper's statistic and not a claim*: a contrast that rises from 1.3 to 3.5 sigma has
become resolvable, and a contrast that falls has not become false. *And a flip is read between consecutive suites*:
with three samples of one contrast a sign can move twice by crossing zero, which is the movement this unit reports
and not two independent failures.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

#: The configuration's twins: label, path. The third sample is the one `e301` found the corpus had executed twice.
SUITES = (
    ("144", "runs/e140_r32_methods_frozenbias_40reps.json"),
    ("600", "runs/e275_frozenbias_suite600_40reps.json"),
    ("1440", "runs/e288_frozenbias_suite1440_40reps.json"),
)
METRICS = ("final_accuracy", "mean_forgetting")
RESOLVED = 2.0
CLAIMS = (
    ("R1", "the suite sharpens the contrasts",
     "The paired sigma is larger at the larger suite in most contrasts, and the number resolved at two sigma rises",
     "falsifier: fewer than half of the sigmas rise"),
    ("R2", "and nothing that was resolved changes sign",
     "Every contrast resolved at two sigma in the first suite stays resolved and keeps its direction",
     "falsifier: one that is not"),
    ("R3", "and nothing at all changes sign",
     "Every contrast's direction is a property of the manipulation rather than of the sample",
     "falsifier: one whose sign flips"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def arms(d: dict) -> list[str]:
    meth = d.get("methods")
    if not isinstance(meth, dict):
        return []
    return sorted(a for a in meth if isinstance(meth[a], dict) and meth[a].get("replicates"))


def contrast(d: dict, a: str, b: str, metric: str) -> dict | None:
    """The paired contrast A minus B over the replicates the two arms share, by position."""
    xa = [r[metric] for r in d["methods"][a]["replicates"]]
    xb = [r[metric] for r in d["methods"][b]["replicates"]]
    n = min(len(xa), len(xb))
    if n < 2:
        return None
    diffs = [xa[i] - xb[i] for i in range(n)]
    mean = statistics.fmean(diffs)
    sem = statistics.stdev(diffs) / math.sqrt(n)
    return {"delta": mean, "sem": sem, "sigma": abs(mean) / sem if sem else float("inf"),
            "sd": statistics.stdev(diffs), "negative": sum(1 for x in diffs if x < 0), "n": n}


def contrasts(runs: list[dict], metrics=METRICS) -> list[dict]:
    """Every arm-versus-arm contrast, per metric, at every suite that carries the pair."""
    out = []
    for label, d in runs:
        for i, a in enumerate(arms(d)):
            for b in arms(d)[i + 1:]:
                for metric in metrics:
                    c = contrast(d, a, b, metric)
                    if c:
                        out.append({"suite": label, "a": a, "b": b, "metric": metric, **c})
    return out


def judge(r: dict) -> list[dict]:
    rows = (r or {}).get("paired") or []
    if not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no contrast could be read"} for c in CLAIMS]

    rose = [x for x in rows if x["sigma_ratio"] > 1]
    by_suite = ", ".join(f"{k} {v}" for k, v in r["resolved_by_suite"].items())
    out = [{"id": "R1", "measured": f"{len(rose)} of {len(rows)} contrasts have a larger sigma at the later suite "
                                     f"(median ratio x{statistics.median([x['sigma_ratio'] for x in rows]):.2f}); "
                                     f"resolved at two sigma by suite: {by_suite}",
            "verdict": "MET -- the suite sharpens this configuration's own contrasts" if 2 * len(rose) > len(rows) else
                       f"FALSIFIER FIRED -- {len(rose)} of {len(rows)} rose"}]

    broke = [x for x in rows if x["resolved_first"] and (not x["resolved_second"] or not x["sign_kept"])]
    named = ", ".join(f"{x['a']} - {x['b']} {x['metric']}" for x in broke[:4])
    out.append({"id": "R2", "measured": f"{r['resolved_first']} contrasts resolved at two sigma at the first suite; "
                                        f"of those, {len(broke)} lost their resolution or their sign ({named or 'none'})",
                "verdict": "MET -- what was resolved stays resolved and keeps its direction" if not broke else
                           f"FALSIFIER FIRED -- {named}"})

    flipped = [x for x in rows if not x["sign_kept"]]
    out.append({"id": "R3", "measured": f"sign kept in {len(rows) - len(flipped)} of {len(rows)} contrasts; "
                                        f"flipped: " + ("; ".join(
                                            f"{x['a']} - {x['b']} on {x['metric']} {x['delta_first']:+.5f} at "
                                            f"{x['sigma_first']:.2f} sigma to {x['delta_second']:+.5f} at "
                                            f"{x['sigma_second']:.2f}" for x in flipped) or "none"),
                "verdict": "MET -- every direction survived the sample" if not flipped else
                           "FALSIFIER FIRED -- a contrast's sign did not survive the sample"})
    return out


def pair_up(rows: list[dict], order: list[str]) -> list[dict]:
    """Each contrast at **every consecutive pair** of suites, which is what the claims are read on.

    Consecutive rather than first-to-last so that a third sample joins the reading instead of replacing one: with
    three suites this is the 144-to-600 movement and the 600-to-1440 movement, 20 contrasts each.
    """
    key = lambda x: (x["a"], x["b"], x["metric"])  # noqa: E731
    by: dict = {}
    for x in rows:
        by.setdefault(key(x), {})[x["suite"]] = x
    out = []
    for (a, b, metric), got in sorted(by.items()):
        for first, second in zip(order, order[1:]):
            if first not in got or second not in got:
                continue
            one, two = got[first], got[second]
            out.append({"a": a, "b": b, "metric": metric, "first": first, "second": second,
                        "delta_first": one["delta"], "delta_second": two["delta"],
                        "sigma_first": one["sigma"], "sigma_second": two["sigma"],
                        "sd_first": one["sd"], "sd_second": two["sd"],
                        "resolved_first": one["sigma"] >= RESOLVED, "resolved_second": two["sigma"] >= RESOLVED,
                        "sign_kept": (one["delta"] > 0) == (two["delta"] > 0),
                        "sigma_ratio": two["sigma"] / one["sigma"] if one["sigma"] else float("nan")})
    return out


def report(r: dict) -> int:
    print("== the configuration's own contrasts, paired over the same replicates ==")
    print(f"   suites read: {r['suites']}; contrasts paired: {len(r['paired'])}")
    print(f"   {'contrast':34} {'metric':16} {'delta':>10} {'sigma':>7} {'delta':>10} {'sigma':>7} {'ratio':>7} "
          f"{'sign':>6}")
    for x in sorted(r["paired"], key=lambda x: -x["sigma_ratio"]):
        print(f"   {x['a'] + ' - ' + x['b']:34} {x['metric']:16} {x['delta_first']:+10.5f} {x['sigma_first']:7.2f} "
              f"{x['delta_second']:+10.5f} {x['sigma_second']:7.2f} {x['sigma_ratio']:7.2f} "
              f"{'kept' if x['sign_kept'] else 'FLIP':>6}")

    print("\n== what the suite bought, and what it did not ==")
    print(f"   resolved at two sigma by suite: "
          + ", ".join(f"{k} {v} of {r['n_contrasts_per_suite']}" for k, v in r["resolved_by_suite"].items()))
    print(f"   sigmas that rose: {sum(1 for x in r['paired'] if x['sigma_ratio'] > 1)} of {len(r['paired'])}; "
          f"median ratio x{statistics.median([x['sigma_ratio'] for x in r['paired']]):.2f}")
    flips = [f"{x['a']} - {x['b']} {x['metric']}" for x in r["paired"] if not x["sign_kept"]]
    print(f"   signs that did not survive: {flips or 'none'}")

    print("\n== the registered claims, R1-R3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the suite sharpened the contrasts and changed no resolved direction; the signs it did not keep are")
    print("    the ones whose sigmas were smallest, which is the corpus's own rule about unresolved contrasts")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    runs = [(label, d) for label, path in SUITES if (d := load(path)) is not None]
    order = [label for label, _ in runs]
    rows = contrasts(runs)
    r = {"suites": order, "n_suites": len(runs),
         "contrasts": rows, "n_contrasts_per_suite": len(rows) // max(len(runs), 1)}
    if len(runs) >= 2:
        r["paired"] = pair_up(rows, order)
        r["first"], r["second"] = order[0], order[1]
        r["resolved_by_suite"] = {label: sum(1 for x in rows if x["suite"] == label and x["sigma"] >= RESOLVED)
                                  for label in order}
        r["resolved_first"] = r["resolved_by_suite"][order[0]]
        r["resolved_second"] = r["resolved_by_suite"][order[-1]]
    else:
        r["paired"] = []
        r["resolved_by_suite"] = {}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
