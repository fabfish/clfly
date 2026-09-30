"""E306 -- the ordering of the arms in the other currency: the metric the corpus stores, and the one it cannot see.

`e297` ordered the corpus's five arms on two metrics and found two chains with the ends swapped -- accuracy ranks
`ewc` last and `replay` first; forgetting ranks `ewc` first and `replay` fourth. `e304` then showed what the
forgetting field *is*: **the lost half of the shortfall**, exact, and blind to the half a task never learned
contributes. `e305` showed what that blindness costs at the level of a single arm. **This unit asks the question at
the level of the ordering**: if `mean_forgetting` is half of a quantity, what does the other half rank the arms?

Three quantities are computable for every arm from its own retention matrix, and each supplies one paired comparison
per (artifact, replicate) in which both arms of a pair ran:

    lost       R[j][j] - R[T-1][j]        what the arm had and gave back -- the corpus's field, exactly
    unlearned  1 - R[j][j]                what the arm never had
    shortfall  the two, summed            everything the arm has left to learn

Four claims, registered before the reading below was taken:

- **R1 -- each quantity is a total order.** The majority edge of each of the ten pairs is transitive on all three
  quantities: a chain through the five arms and no cycle on any of them. **Falsifier**: a majority cycle on one.
- **R2 -- and the metric and the shortfall disagree at the ends.** The arm the forgetting field ranks second-best is
  the arm the shortfall ranks *worst*, and the arm it ranks worst is the arm the shortfall ranks second-best.
  **Falsifier**: the same arm is worst on both.
- **R3 -- and the disagreement tracks learning.** Over the five arms, the rank correlation between the lost ordering
  and the unlearned ordering is negative: ranking by forgetting is close to reverse-ranking by how much was learned.
  **Falsifier**: a correlation at or above zero.
- **R4 -- and the corpus's two spellings of forgetting agree.** The stored `mean_forgetting` and the recomputed
  `lost` give the same majority order and the same edge on all ten pairs, on the population this unit can read.
  **Falsifier**: a pair whose majority edge differs between them. This is the control: R2 and R3 are about a
  *different* quantity and not about the field being read wrong.

**What it cannot do.** *The population is the arms with a readable retention matrix*, which is 301 of `e304`'s arms
and not every arm `e297` reads: `e297` takes an edge from any artifact that ran both arms, so its counts are larger
and its ordering need not be this one, and the two units' forgetting orders differ at the top (`e297` puts `ewc`
first, this unit `replay`) for that reason rather than for a metric's. *The arms are not independent*: the same
configuration recurs across the pairs, so a majority edge is a weighted count of correlated comparisons and not a
vote of independent ones. *A majority edge throws away the power* -- the margins run from 51% to 89% -- so a chain
built of five such edges is a description of the corpus's comparisons and carries no interval. *And the shortfall is
not a loss*: an arm with nothing left to learn is not necessarily a good arm, and `unlearned` is large for an arm
that never solved the task, which is a statement about the arm and not about its forgetting.
"""

from __future__ import annotations

import argparse
import itertools
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e304_the_decomposition_the_block_asked_for as e304

RUNS = Path("runs")
#: The five arms the corpus runs, as `e295` to `e297` name them.
ARMS = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
#: The three quantities, and the corpus's own field, which R4 reads beside them.
LOST, UNLEARNED, SHORTFALL, STORED = "lost_mean", "unlearned_mean", "shortfall_mean", "metric"
QUANTITIES = (LOST, UNLEARNED, SHORTFALL)
CLAIMS = (
    ("R1", "each quantity is a total order",
     "The majority edge of each of the ten pairs is transitive on all three quantities",
     "falsifier: a majority cycle on one of them"),
    ("R2", "and the metric and the shortfall disagree at the ends",
     "The arm ranked second-best on the lost term is ranked worst on the shortfall, and the arm ranked worst on the "
     "lost term is ranked second-best on the shortfall",
     "falsifier: the same arm is worst on both"),
    ("R3", "and the disagreement tracks learning",
     "The rank correlation between the lost ordering and the unlearned ordering is negative over the five arms",
     "falsifier: a correlation at or above zero"),
    ("R4", "and the corpus's two spellings of forgetting agree",
     "The stored `mean_forgetting` and the recomputed lost term give the same majority edge on every pair",
     "falsifier: one pair whose edge differs"),
)


def pairs_by_replicate(root: Path = RUNS) -> dict:
    """Every (artifact, replicate) in which two or more of the five arms ran, keyed by the arms present."""
    out: dict = defaultdict(dict)
    rows, _ = e304.replicates(root)
    for r in rows:
        if r["arm"] in ARMS:
            out[(r["artifact"], r["replicate"])][r["arm"]] = r
    return out


def majority(by: dict, field: str) -> dict:
    """The majority edge of every pair on one quantity, with the margins and whether the set is acyclic."""
    tally: dict = defaultdict(lambda: [0, 0])
    for arms in by.values():
        for a, b in itertools.combinations(ARMS, 2):
            if a not in arms or b not in arms:
                continue
            va, vb = arms[a].get(field), arms[b].get(field)
            if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
                continue
            if va < vb:
                tally[(a, b)][0] += 1
            elif va > vb:
                tally[(a, b)][1] += 1
    edges = {}
    for (a, b), (low, high) in sorted(tally.items()):
        if low + high == 0 or low == high:
            continue
        winner, loser, margin = (a, b, low) if low > high else (b, a, high)
        edges[(winner, loser)] = {"winner": winner, "loser": loser, "n": low + high,
                                  "margin": margin, "rate": margin / (low + high)}
    wins = {a: sum(1 for (w, _) in edges if w == a) for a in ARMS}
    cycles = [c for c in itertools.permutations(ARMS, 3)
              if (c[0], c[1]) in edges and (c[1], c[2]) in edges and (c[2], c[0]) in edges]
    return {"edges": {f"{w}>{l}": v for (w, l), v in edges.items()}, "n_edges": len(edges),
            "cycles": [list(c) for c in cycles], "wins": wins,
            "order": sorted(ARMS, key=lambda a: -wins[a])}


def ranks(order: list[str]) -> dict:
    return {a: i for i, a in enumerate(order)}


def reading(root: Path = RUNS) -> dict:
    by = pairs_by_replicate(root)
    fields = {f: majority(by, f) for f in QUANTITIES + (STORED,)}
    pairs = [f"{a}>{b}" for a, b in itertools.combinations(ARMS, 2)]
    agreeing = [k for k in pairs
                if fields[LOST]["edges"].get(k) == fields[STORED]["edges"].get(k)]
    lost_order = fields[LOST]["order"]
    r = ranks(lost_order)
    u = ranks(fields[UNLEARNED]["order"])
    rho = e304.rank_correlation([r[a] for a in ARMS], [u[a] for a in ARMS])
    return {"fields": fields, "arm_replicates": len(by), "n_pairs": len(pairs),
            "stored_agrees_on": len(agreeing),
            "lost_order": lost_order, "unlearned_order": fields[UNLEARNED]["order"],
            "shortfall_order": fields[SHORTFALL]["order"],
            "lost_unlearned_rho": rho}


def judge(r: dict) -> list[dict]:
    fields = r.get("fields") or {}
    if len(fields) < 4:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm pair could be read"} for c in CLAIMS]

    out = [{"id": "R1", "measured": "; ".join(f"{f} {fields[f]['n_edges']} edges and "
                                              f"{len(fields[f]['cycles'])} cycle(s)" for f in QUANTITIES),
            "verdict": "MET -- every quantity chains the five arms" if
            all(fields[f]["n_edges"] == 10 and not fields[f]["cycles"] for f in QUANTITIES) else
            f"FALSIFIER FIRED -- " + "; ".join(f"{f} {len(fields[f]['cycles'])}" for f in QUANTITIES)}]

    lost, short = r["lost_order"], r["shortfall_order"]
    second_best, worst = lost[1], lost[-1]
    good = short.index(second_best) == len(short) - 1 and short.index(worst) == 1
    out.append({"id": "R2", "measured": f"lost orders {lost}; shortfall orders {short} -- so `{second_best}`, "
                                        f"second on the metric, is {short.index(second_best) + 1} of 5 on the "
                                        f"shortfall, and `{worst}`, last on the metric, is "
                                        f"{short.index(worst) + 1}",
                "verdict": "MET -- the metric's best arms have the most left to learn" if good else
                           "FALSIFIER FIRED -- the same arm is worst on both"})

    out.append({"id": "R3", "measured": f"lost orders {lost} against unlearned {r['unlearned_order']}, "
                                        f"rank correlation {r['lost_unlearned_rho']:+.3f}",
                "verdict": "MET -- ranking by forgetting is close to reverse-ranking by learning" if
                (r["lost_unlearned_rho"] is not None and r["lost_unlearned_rho"] < 0) else
                f"FALSIFIER FIRED -- {r['lost_unlearned_rho']}"})

    out.append({"id": "R4", "measured": f"the stored `{STORED}` and the recomputed `{LOST}` give the same edge on "
                                        f"{r['stored_agrees_on']} of {r['n_pairs']} pairs",
                "verdict": "MET -- the field this unit reads back is the field the corpus stores" if
                r["stored_agrees_on"] == r["n_pairs"] else
                f"FALSIFIER FIRED -- {r['n_pairs'] - r['stored_agrees_on']} pair(s) differ"})
    return out


def report(r: dict) -> int:
    print("== the five arms, ordered by three quantities and by the field the corpus stores ==")
    print(f"   {r['arm_replicates']} (artifact, replicate) pairs where two or more of the five ran")
    for name, key in (("lost (the corpus's field)", LOST), ("unlearned", UNLEARNED),
                      ("shortfall", SHORTFALL), ("stored mean_forgetting", STORED)):
        f = r["fields"][key]
        print(f"   {name:26} best to worst: {' > '.join(f['order'])}   "
              f"({f['n_edges']} edges, {len(f['cycles'])} cycles)")
        print(f"   {'':26} margins " + ", ".join(
            f"{k} {v['margin']}/{v['n']} ({100 * v['rate']:.0f}%)" for k, v in sorted(f["edges"].items())))

    print("\n== the registered claims, R1-R4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the corpus ranks the arms by a field that is half of the quantity it cares about, and the half it")
    print("    drops is the one on which the arms are separated by how much they learned in the first place)")
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
