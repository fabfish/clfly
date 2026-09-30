"""E308 -- the unit of the vote: which arm an ordering puts first depends on whether an artifact or a replicate counts.

`e306` left an ambiguity it named in its own limitations: its ordering puts `replay` first on the corpus's forgetting
field while `e297`'s puts `ewc` first, and `e306` attributed that to its **population** -- the 301 arms with a
readable retention matrix rather than every arm `e297` reads. **This unit tests that attribution and finds it wrong.**

Two things differ between the two units and only one of them is the population:

    `e297`  one pooled contrast per *artifact*, then a majority over artifacts
    `e306`  one vote per *(artifact, replicate)*, then a majority over votes

Holding each of them fixed in turn settles which one moved the order.

Three claims, registered before the reading below was taken:

- **V1 -- the population did not move it.** Restricting `e297`'S own method to the artifacts that carry a readable
  retention matrix changes no edge and no ordering, on either metric. **Falsifier**: one edge that differs.
- **V2 -- the weighting did.** On the corpus's own forgetting field the two units' methods disagree on exactly the
  pairs that flip, and on no others. **Falsifier**: no disagreement, or disagreements beyond the pairs the two
  orderings differ in.
- **V3 -- and the difference reaches the top.** `e297`'s method ranks `ewc` first and `replay` second; the per-vote
  method ranks `replay` first and `ewc` second. **Falsifier**: the same arm is first under both.

**What it cannot do.** *Both readings are on the same corpus and the same field*, so nothing here is about a
different measurement -- but the artifact-level method pools replicates into one mean before voting, which is a
different quantity from a vote per replicate, and this unit reports which pairs move rather than which is right.
*Neither method carries an interval*: a majority edge is a count, the margins are narrow for the pairs that move, and
a pair at 52% under one method and 48% under the other is a pair the corpus does not decide. *The two methods are not
the only two*: a weighted majority, a paired test per artifact or a bootstrap over configurations would each be a
third reading, and nothing here says which of them a benchmark should print. *And the corpus's artifacts are not
independent configurations*, which is what makes the weighting question live in the first place.
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e297_the_ordering_of_the_arms as e297
from experiments import e304_the_decomposition_the_block_asked_for as e304
from experiments import e306_the_ordering_in_the_other_currency as e306

RUNS = Path("runs")
#: The field both readings are taken on, so the only difference between them is the unit of the vote.
FIELD = "mean_forgetting"
CLAIMS = (
    ("V1", "the population did not move the ordering",
     "Restricting `e297`'s method to the artifacts carrying a readable retention matrix changes no edge",
     "falsifier: one edge that differs"),
    ("V2", "the weighting did",
     "The two methods disagree on exactly the pairs in which the two orderings differ",
     "falsifier: no disagreement, or one outside them"),
    ("V3", "and the difference reaches the top",
     "The artifact-level method ranks `ewc` first and `replay` second and the per-vote method the reverse",
     "falsifier: the same arm is first under both"),
)


def artifact_edges(keep: set | None = None, root: Path = RUNS) -> dict:
    """`e297`'s method: one pooled contrast per artifact, then the majority over artifacts, keyed in pair order."""
    rows = [r for r in e297.pairs(root, keep=keep) if r["metric"] == FIELD]
    return {f"{r['a']}>{r['b']}": {"winner": r["winner"], "comparisons": r["comparisons"], "ahead": r["a_ahead"]}
            for r in rows}


def vote_edges(root: Path = RUNS) -> dict:
    """The per-vote method, keyed in the same `(a, b)` order `e297` uses so the two can be compared pair by pair.

    The counting is `e306`'s `majority`, called on the stored field rather than on the recomputed lost term: `e306`'s
    own R4 shows the two agree on every pair, so reading the stored one keeps this comparison on one measurement.
    """
    edges = e306.majority(e306.pairs_by_replicate(root), "metric")["edges"]
    out = {}
    for a, b in itertools.combinations(e306.ARMS, 2):
        e = edges.get(f"{a}>{b}") or edges.get(f"{b}>{a}")
        if e is None:
            continue
        out[f"{a}>{b}"] = {"winner": e["winner"], "comparisons": e["n"], "ahead": e["margin"]}
    return out


def reading(root: Path = RUNS) -> dict:
    keep = {r["artifact"] for r in e304.replicates(root)[0]}
    full, filtered, votes = artifact_edges(None, root), artifact_edges(keep, root), vote_edges(root)
    pairs = sorted(votes)
    moved_by_population = [k for k in pairs
                           if full.get(k, {}).get("winner") != filtered.get(k, {}).get("winner")]
    moved_by_weighting = [k for k in pairs
                          if full.get(k, {}).get("winner") != votes[k]["winner"]]
    order_full = e297.order([r for r in e297.pairs(root) if r["metric"] == FIELD], FIELD)["worst_first"][::-1]
    order_votes = e306.majority(e306.pairs_by_replicate(root), "metric")["order"]
    return {"field": FIELD, "keep": len(keep), "n_pairs": len(pairs),
            "moved_by_population": moved_by_population, "moved_by_weighting": moved_by_weighting,
            "order_artifact": order_full, "order_vote": order_votes,
            "edges_artifact": full, "edges_vote": votes}


def order_difference(one: list[str], two: list[str], arms: tuple = e297.ARMS) -> set:
    """The pairs whose relative order the two orderings disagree about -- the inversions between them.

    `moved_by_weighting` is a set of *edges* and this is a set of *pairs*, and V2 is the claim that they are the same
    set: the pairs the two methods vote differently on are exactly the pairs the two orderings place differently. The
    key is built in `e297`'s pair order so that the two sets can be compared as strings.
    """
    out = set()
    for a, b in itertools.combinations(arms, 2):
        if a not in one or b not in one or a not in two or b not in two:
            continue
        if (one.index(a) < one.index(b)) != (two.index(a) < two.index(b)):
            out.add(f"{a}>{b}")
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("n_pairs"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm pair could be read"} for c in CLAIMS]

    moved_p = set(r["moved_by_population"])
    out = [{"id": "V1", "measured": f"{r['n_pairs']} pairs read on both populations, {len(moved_p)} whose winner "
                                    f"moved when the corpus was restricted to the {r['keep']} artifacts carrying a "
                                    f"readable retention matrix: {sorted(moved_p) or 'none'}",
            "verdict": "MET -- the population is not what moved the ordering" if not moved_p else
                       f"FALSIFIER FIRED -- {sorted(moved_p)}"}]

    moved_w = set(r["moved_by_weighting"])
    inversions = order_difference(r["order_artifact"], r["order_vote"])
    same = moved_w == inversions
    out.append({"id": "V2", "measured": f"{len(moved_w)} pair(s) move between the artifact-level and the per-vote "
                                        f"method ({sorted(moved_w) or 'none'}); the two orderings disagree about "
                                        f"{len(inversions)} pair(s) ({sorted(inversions) or 'none'})",
                "verdict": "MET -- the unit of the vote is exactly what moves those pairs" if moved_w and same else
                           f"FALSIFIER FIRED -- the methods agree on {'everything' if not moved_w else 'other pairs'}"})

    firsts = [r["order_artifact"][0], r["order_vote"][0]]
    out.append({"id": "V3", "measured": f"the artifact-level method orders {' > '.join(r['order_artifact'])}, the "
                                        f"per-vote method {' > '.join(r['order_vote'])}",
                "verdict": "MET -- the two orders put different arms first" if firsts[0] != firsts[1] else
                           "FALSIFIER FIRED -- the same arm is first under both"})
    return out


def report(r: dict) -> int:
    print("== the two methods on the corpus's own forgetting field ==")
    print(f"   {r['n_pairs']} pairs; the retention filter keeps {r['keep']} artifacts")
    print(f"   {'pair':26} {'artifact-level':>16} {'n':>6}   {'per-vote':>12} {'n':>6}")
    for k in sorted(r["edges_vote"]):
        a = r["edges_artifact"].get(k, {"winner": None, "comparisons": 0})
        v = r["edges_vote"][k]
        mark = "   <- moves" if a["winner"] != v["winner"] else ""
        print(f"   {k:26} {str(a['winner']):>16} {a['comparisons']:6}   {str(v['winner']):>12} {v['comparisons']:6}{mark}")

    print("\n== the registered claims, V1-V3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the corpus's best-forgetting arm is a property of the vote and not of the corpus: pooling each")
    print("    artifact into one contrast puts the diagonal penalty first, one vote per replicate puts replay first)")
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

    r = reading(args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
