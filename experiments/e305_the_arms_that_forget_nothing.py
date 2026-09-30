"""E305 -- the arms that forget nothing, in the decomposition's currency.

`e299` scoped the README's front-page claim by counting the arms whose `mean_forgetting` is indistinguishable from
zero at two sigma: **55 of the corpus's 271 arms**, with eight of them at forty replicates. `e304` then showed what
that field is: **the lost half of the shortfall**, exact, and blind to the half a task that was never learned
contributes. This unit joins the two readings on `(artifact, arm)` and asks what the 55 are.

The join is exact -- all 271 of `e299`'s arms are among `e304`'s 301, on the same collapse -- so no arm is dropped
and no number here is a comparison between two different populations.

Four claims, registered before the reading below was taken:

- **C1 -- most of the arms inside the line are arms that barely learned.** More than half of the 55 have an unlearned
  share of their shortfall above a half. **Falsifier**: half or fewer.
- **C2 -- and the line separates them on the wrong axis.** The in-line arms' median unlearned share is larger than
  the out-of-line arms'. **Falsifier**: at or below it.
- **C3 -- and a substantial minority of them are worse than the corpus's typical arm.** At least a quarter of the 55
  have a shortfall above the median shortfall of all 271. **Falsifier**: fewer than a quarter.
- **C4 -- and some of them have nothing to forget.** At least five of the 55 have a **negative** lost term, i.e. they
  got *better* on the tasks they had learned. **Falsifier**: fewer than five.

**What it cannot do.** *The line is a two-sigma bound on a mean over replicates*, so an arm inside it is one whose
forgetting is smaller than its own noise and not necessarily one that does not forget; a wide-sem arm enters the
line by being noisy, which is why C3 is about the shortfall and not about the bound. *The share is computed on the
same replicates the mean is*, so the two readings are not independent measurements of the arm -- the join is a
re-description of one set of numbers and not a second experiment on it. *An arm inside the line at a low replicate
count and one at forty are treated alike*, and `e299` already reports the split; this unit names the eight but does
not weight by power. *And the corpus's arms are not independent configurations*, so a count of 55 and a count of 50
are counts of entries and not of experiments.
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e299_the_front_page_claim as e299
from experiments import e304_the_decomposition_the_block_asked_for as e304

RUNS = Path("runs")
#: The share above which a task is mostly one the arm never learned, and the minority C3 asks for.
HALF = 0.5
QUARTER = 0.25
#: How many arms inside the line C4 requires to have nothing left to forget.
FEWEST_NEGATIVE = 5
CLAIMS = (
    ("C1", "most of the arms inside the line are arms that barely learned",
     "More than half of the arms inside the zero-line have an unlearned share above a half",
     "falsifier: half or fewer"),
    ("C2", "and the line separates them on the wrong axis",
     "The in-line arms' median unlearned share is larger than the out-of-line arms'",
     "falsifier: at or below it"),
    ("C3", "and a substantial minority of them are worse than the corpus's typical arm",
     "At least a quarter of the arms inside the line have a shortfall above the median of all of them",
     "falsifier: fewer than a quarter"),
    ("C4", "and some of them have nothing to forget",
     "At least five of the arms inside the line have a negative lost term",
     "falsifier: fewer than five"),
)


def joined(root: Path = RUNS) -> tuple[list[dict], list[dict]]:
    """`e299`'s zero-line rows carrying `e304`'s decomposition, and the arms the two readings do not share."""
    zeros = e299.zeros(root)
    decomposition = {(a["artifact"], a["arm"]): a for a in e304.per_arm(e304.replicates(root)[0])}
    rows, unjoined = [], []
    for z in zeros:
        key = (z["artifact"], z["arm"])
        if key in decomposition:
            rows.append({**z, **{k: v for k, v in decomposition[key].items() if k not in ("artifact", "arm")}})
        else:
            unjoined.append({"artifact": z["artifact"], "arm": z["arm"], "why": "no readable retention matrix"})
    return rows, unjoined


def summary(rows: list[dict]) -> dict:
    inside = [r for r in rows if r["at_zero"]]
    outside = [r for r in rows if not r["at_zero"]]
    shares = [r["unlearned_share"] for r in inside if r["unlearned_share"] is not None]
    out_shares = [r["unlearned_share"] for r in outside if r["unlearned_share"] is not None]
    median_shortfall = statistics.median([r["shortfall_mean"] for r in rows]) if rows else None
    return {
        "arms": len(rows), "inside": len(inside), "outside": len(outside),
        "inside_share_above_half": sum(1 for s in shares if s > HALF),
        "inside_share_above_eight_tenths": sum(1 for s in shares if s > 0.8),
        "inside_median_share": statistics.median(shares) if shares else None,
        "outside_median_share": statistics.median(out_shares) if out_shares else None,
        "median_shortfall": median_shortfall,
        "inside_above_median_shortfall": sum(1 for r in inside if r["shortfall_mean"] > median_shortfall)
        if median_shortfall is not None else 0,
        "inside_negative_lost": sum(1 for r in inside if r["lost_mean"] < 0),
        "inside_at_forty": sum(1 for r in inside if r["n"] >= 40),
        "worst_inside": sorted(({"artifact": r["artifact"], "arm": r["arm"], "mean": r["mean"], "sem": r["sem"],
                                 "sigma": r["sigma"], "n": r["n"], "unlearned_share": r["unlearned_share"],
                                 "shortfall_mean": r["shortfall_mean"]} for r in inside),
                               key=lambda x: -x["shortfall_mean"])[:6],
    }


def judge(r: dict) -> list[dict]:
    if not r.get("inside"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm is inside the zero-line"}
                for c in CLAIMS]

    out = [{"id": "C1", "measured": f"{r['inside_share_above_half']} of {r['inside']} arms inside the line have an "
                                     f"unlearned share above a half ({r['inside_share_above_eight_tenths']} above "
                                     f"eight tenths)",
            "verdict": "MET -- a forgotten-nothing arm is usually an arm that learned little"
            if r["inside_share_above_half"] * 2 > r["inside"] else
            f"FALSIFIER FIRED -- {r['inside_share_above_half']} of {r['inside']}"}]

    out.append({"id": "C2", "measured": f"median unlearned share {r['inside_median_share']:.3f} inside the line "
                                        f"against {r['outside_median_share']:.3f} outside it",
                "verdict": "MET -- the line picks the arms that learned least"
                if r["inside_median_share"] > r["outside_median_share"] else
                f"FALSIFIER FIRED -- {r['inside_median_share']} against {r['outside_median_share']}"})

    out.append({"id": "C3", "measured": f"{r['inside_above_median_shortfall']} of {r['inside']} in-line arms "
                                        f"({r['inside_above_median_shortfall'] / r['inside']:.3f}) have a shortfall "
                                        f"above the corpus median of {r['median_shortfall']:.4f}",
                "verdict": "MET -- some of the arms that forget nothing have more left to learn than the typical arm"
                if r["inside_above_median_shortfall"] / r["inside"] >= QUARTER else
                f"FALSIFIER FIRED -- {r['inside_above_median_shortfall']} of {r['inside']}"})

    out.append({"id": "C4", "measured": f"{r['inside_negative_lost']} of {r['inside']} in-line arms have a negative "
                                        f"lost term, so they improved on what they had learned",
                "verdict": "MET -- some of the line has nothing to forget" if
                r["inside_negative_lost"] >= FEWEST_NEGATIVE else
                f"FALSIFIER FIRED -- {r['inside_negative_lost']}"})
    return out


def report(r: dict) -> int:
    print("== the arms whose forgetting is indistinguishable from zero ==")
    print(f"   {r['inside']} of {r['arms']} arms are inside the line; {r['inside_at_forty']} of them at forty "
          f"replicates or more")
    print(f"   unlearned share: median {r['inside_median_share']:.3f} inside against "
          f"{r['outside_median_share']:.3f} outside; {r['inside_share_above_half']} above a half and "
          f"{r['inside_share_above_eight_tenths']} above eight tenths")
    print(f"   shortfall above the corpus median of {r['median_shortfall']:.4f}: "
          f"{r['inside_above_median_shortfall']} arms;  negative lost term: {r['inside_negative_lost']} arms")

    print("\n== and the in-line arms with the most left to learn ==")
    print(f"   {'artifact':44} {'arm':16} {'mean_forgetting':>15} {'sem':>9} {'share':>7} {'shortfall':>10}")
    for x in r["worst_inside"]:
        print(f"   {x['artifact'][:44]:44} {x['arm']:16} {x['mean']:+15.5f} {x['sem']:9.5f} "
              f"{x['unlearned_share']:7.3f} {x['shortfall_mean']:10.4f}")

    print("\n== the registered claims, C1-C4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the front page's scoped absence is measured in a field that is the lost half of the shortfall, so")
    print("    an arm's absence of forgetting can be and often is an excess of never having learned the task)")
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

    rows, unjoined = joined(args.runs)
    r = {"unjoined": unjoined, **summary(rows)}
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
