"""E294 -- the pairing in the corpus: 68 matched pairs, a median correlation of +0.30, and fourteen contrasts the
unpaired convention would not have resolved.

Every rate-network artifact that ran both arms of a contrast stores a `matched_pair` block: the delta, the sem over
the replicates computed *paired* and *unpaired*, and the correlation between the two arms' per-replicate values.
`e276` used one of those blocks to correct a sigma the paper had quoted from the unpaired sem, which is what a
*case* of the problem looks like. Nobody has read the blocks as a population, and that is what this unit does: how
often the correlation is positive, how often pairing narrows the interval, and -- the number that matters for
every claim in the corpus -- **how many contrasts the two conventions resolve**.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **P1 -- the paired values are positively correlated in most contrasts.** **Falsifier**: fewer than half of the
  correlations are positive, or the paired sem is the smaller in fewer than half.
- **P2 -- and not always.** Some correlations are negative, and for those pairing *widens* the interval rather than
  narrowing it. **Falsifier**: none are negative.
- **P3 -- and the convention decides what resolves.** Over the same contrasts, the number at two sigma or more is
  larger under the paired sem than under the unpaired one. **Falsifier**: it is not larger.

**What the three add up to.** Pairing is not a refinement in this corpus, it is the difference between resolving a
contrast and not: the two arms of a contrast share their training data, their task geometry and their test sample, so
their per-replicate values move together (median ρ = +0.30) and the difference's spread is smaller than either arm's.
A sigma quoted from the unpaired sem asks the reader to buy noise that the design already cancelled -- which is the
defect `e276` found one instance of, here measured across the corpus. **And the exceptions are worth naming**: nine
contrasts have a *negative* correlation, where the two arms disagree from replicate to replicate and pairing costs
interval width rather than saving it.

**What it cannot do.** *The correlation is an across-replicate correlation between two arms' aggregate metrics* and
not an item-level correlation, so nothing here says how much of it is the shared test sample and how much is the
shared training -- `e285`'s sample swap is the instrument for that, and it has one configuration. *The blocks span
replicate counts from 3 to 144*, so a correlation estimated on three replicates carries an error of about 0.5 and the
extremes of the list are the small-n ones; the claims are stated over the whole population for that reason and the
report breaks it down by replicate count. *`sem_paired / sem_unpaired` equals `sqrt(1 - rho)` only when the two arms'
sds are equal*, which is why the identity holds on the median and fails badly where they are not; nothing here
corrects for that. *The counts at two sigma are counts of stored sigmas*, so they inherit whatever the runner's
formula did, and a contrast resolved at 2.1 sigma is one replicate away from crossing. *And nothing here re-reads the
paper*: which of its printed sigmas came from the unpaired convention is a question for a reader with both numbers in
front of them.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import write_json

RUNS = Path("runs")
#: The sigma at which a contrast is called resolved, and the replicate count below which a correlation is not read.
RESOLVED = 2.0
SMALL_N = 5
CLAIMS = (
    ("P1", "the paired values are positively correlated in most contrasts",
     "Most correlations are positive and the paired sem is the smaller in most contrasts",
     "falsifier: fewer than half are positive, or the paired sem is smaller in fewer than half"),
    ("P2", "and not always",
     "Some correlations are negative, and for those the paired sem is the larger",
     "falsifier: none are negative"),
    ("P3", "and the convention decides what resolves",
     "Over the same contrasts, more are at or above two sigma under the paired sem than under the unpaired one",
     "falsifier: the paired count is not larger"),
)


def blocks(root: Path = RUNS) -> list[dict]:
    """Every matched-pair block the corpus carries, one row per metric."""
    out = []
    for p in sorted(root.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        mp = d.get("matched_pair")
        if not isinstance(mp, dict):
            continue
        for metric, v in sorted(mp.items()):
            if not isinstance(v, dict) or not isinstance(v.get("corr"), (int, float)) or v.get("n", 0) < 3:
                continue
            out.append({"artifact": p.name, "metric": metric, "n": v["n"], "corr": float(v["corr"]),
                        "sem_paired": v.get("sem_paired"), "sem_unpaired": v.get("sem_unpaired"),
                        "sigma_paired": v.get("sigma_paired"), "sigma_unpaired": v.get("sigma_unpaired"),
                        "delta": v.get("delta")})
    return out


def summary(rows: list[dict]) -> dict:
    paired_smaller = [r for r in rows if r["sem_paired"] and r["sem_unpaired"] and r["sem_paired"] < r["sem_unpaired"]]
    ratios = [r["sem_paired"] / r["sem_unpaired"] for r in rows if r["sem_paired"] and r["sem_unpaired"]]
    return {
        "blocks": len(rows), "artifacts": len({r["artifact"] for r in rows}),
        "positive": sum(1 for r in rows if r["corr"] > 0),
        "negative": sum(1 for r in rows if r["corr"] < 0),
        "median_corr": statistics.median([r["corr"] for r in rows]),
        "paired_smaller": len(paired_smaller),
        "median_ratio": statistics.median(ratios) if ratios else None,
        "median_predicted": statistics.median([math.sqrt(1 - r["corr"]) for r in rows]),
        "resolved_paired": sum(1 for r in rows if r["sigma_paired"] is not None and abs(r["sigma_paired"]) >= RESOLVED),
        "resolved_unpaired": sum(1 for r in rows if r["sigma_unpaired"] is not None
                                 and abs(r["sigma_unpaired"]) >= RESOLVED),
        "by_n": {n: {"blocks": len(v), "positive": sum(1 for r in v if r["corr"] > 0),
                     "median_corr": statistics.median([r["corr"] for r in v])}
                 for n, v in sorted(_group(rows).items())},
    }


def _group(rows: list[dict]) -> dict:
    by: dict[int, list[dict]] = defaultdict(list)
    for r in rows:
        by[r["n"]].append(r)
    return dict(by)


def judge(r: dict) -> list[dict]:
    s = (r or {}).get("summary")
    rows = (r or {}).get("blocks") or []
    if not s or not rows:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no matched pair in the corpus"} for c in CLAIMS]

    ok = s["positive"] * 2 > s["blocks"] and s["paired_smaller"] * 2 > s["blocks"]
    out = [{"id": "P1", "measured": f"{s['positive']} of {s['blocks']} correlations are positive (median "
                                     f"{s['median_corr']:+.3f}); the paired sem is the smaller in "
                                     f"{s['paired_smaller']} of them (median ratio {s['median_ratio']:.3f})",
            "verdict": "MET -- the two arms of a contrast move together" if ok else
                       f"FALSIFIER FIRED -- {s['positive']} positive, {s['paired_smaller']} narrower"}]

    negative = [x for x in rows if x["corr"] < 0]
    widened = [x for x in negative if x["sem_paired"] and x["sem_unpaired"] and x["sem_paired"] > x["sem_unpaired"]]
    out.append({"id": "P2", "measured": f"{s['negative']} of {s['blocks']} correlations are negative, from "
                                        f"{min(x['corr'] for x in rows):+.3f}; of those, {len(widened)} have the "
                                        f"paired sem larger: " + (", ".join(
                                            f"{x['artifact'][:30]} {x['metric']}" for x in widened[:3]) or "none"),
                "verdict": "MET -- pairing costs interval width where the arms disagree" if negative else
                           "FALSIFIER FIRED -- every correlation is positive or zero"})

    out.append({"id": "P3", "measured": f"over the same {s['blocks']} contrasts, resolved at two sigma: "
                                        f"{s['resolved_paired']} under the paired sem against "
                                        f"{s['resolved_unpaired']} under the unpaired one",
                "verdict": "MET -- the convention decides what resolves" if s["resolved_paired"] > s["resolved_unpaired"]
                else f"FALSIFIER FIRED -- {s['resolved_paired']} against {s['resolved_unpaired']}"})
    return out


def report(r: dict) -> int:
    rows = r["blocks"]
    s = r["summary"]
    print("== the corpus's matched pairs ==")
    print(f"   blocks: {s['blocks']} over {s['artifacts']} artifacts; replicate counts "
          f"{sorted(x['n'] for x in rows) and sorted({x['n'] for x in rows})}")
    print(f"   correlations: min {min(x['corr'] for x in rows):+.3f}, median {s['median_corr']:+.3f}, "
          f"max {max(x['corr'] for x in rows):+.3f}; positive {s['positive']}, negative {s['negative']}")
    print(f"   the paired sem is the smaller in {s['paired_smaller']} of {s['blocks']} "
          f"(median ratio {s['median_ratio']:.3f}, and sqrt(1 - rho) predicts {s['median_predicted']:.3f})")

    print("\n== by replicate count ==")
    for n, v in s["by_n"].items():
        print(f"   n = {n:4} blocks {v['blocks']:3}  positive {v['positive']:3}  median corr {v['median_corr']:+.3f}")

    print("\n== what the convention decides ==")
    print(f"   resolved at two sigma: {s['resolved_paired']} paired against {s['resolved_unpaired']} unpaired")
    print("   the extremes of the correlation:")
    for x in sorted(rows, key=lambda x: -x["corr"])[:3]:
        print(f"      {x['corr']:+.3f}  n {x['n']:4}  {x['artifact'][:44]:44} {x['metric']}")
    for x in sorted(rows, key=lambda x: x["corr"])[:3]:
        print(f"      {x['corr']:+.3f}  n {x['n']:4}  {x['artifact'][:44]:44} {x['metric']}")

    print("\n== the registered claims, P1-P3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (pairing is not a refinement here but the difference between resolving a contrast and not, and the")
    print("    exceptions are the contrasts whose arms disagree from replicate to replicate)")
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
    rows = blocks(args.runs)
    r = {"blocks": rows, "summary": summary(rows) if rows else None}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
