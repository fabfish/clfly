"""E312 -- the shortfall is the accuracy: the third quantity `e306` ordered is the corpus's own first one.

`e304` splits the shortfall `1 - R[T-1][j]` into a **lost** term and an **unlearned** term, and `e306` ordered the
five arms by all three. This unit tests what the first of those three actually is, and finds that it is not a new
quantity:

    shortfall_mean = mean_j (1 - R[T-1][j]) = 1 - mean_j R[T-1][j] = 1 - final_accuracy

because `R[T-1]` **is** the per-task final accuracy, and the corpus's `final_accuracy` is its mean over tasks. The
identity holds in every arm-replicate of the corpus, so:

- **the shortfall ordering is the accuracy ordering**, best-to-worst, and
- **`e306`'s R2 is `e297`'s A2**: "the arm second on the forgetting metric is the arm with the most left to learn" is
  the same sentence as "the diagonal is the last arm on accuracy and the first on forgetting", which `e297` wrote
  three fires earlier.

Three claims, registered before the reading below was taken:

- **X1 -- the identity holds.** `shortfall_mean` equals `1 - final_accuracy` for every arm-replicate that carries
  both. **Falsifier**: one that differs.
- **X2 -- and so the two orderings are one.** Read with each quantity's own direction, the shortfall's majority edge
  is the accuracy's majority edge on all ten pairs. **Falsifier**: one pair that differs.
- **X3 -- and `e306`'s R2 is `e297`'s A2.** The arm `e306` ranked worst on the shortfall is the arm `e297` ranked
  worst on accuracy, and the arm `e306` ranked second on the forgetting term is the one `e297` ranked first.
  **Falsifier**: a different arm at either end.

**What this corrects, and what it leaves standing.** `e306`'s R1 (three chains, no cycle each) is arithmetically
true and now known to be a statement about two of the corpus's own fields and their difference. **R4 is untouched**
and is what makes that knowable: it showed the recomputed lost term is the stored `mean_forgetting` on all ten edges.
**R3 is a genuine third quantity**: the lost ordering against the unlearned ordering is the forgetting against the
level a task reached *when it was learned*, which is neither the accuracy nor the forgetting and which `e310` then
measured as a position effect. **And R2 is withdrawn as a finding**: it is `e297`'s cross-metric reversal, and the
unit that established it is `e297`.

**What it cannot do.** *The identity is arithmetic*, so X1 checks a definition and not a result. *`e297` reads the
same field on a different population*, so "the same arm at the end" is a claim about the ordering and not about the
numbers, which is `e308`'s subject. *The decomposition's three terms are linearly dependent by construction*, so
nothing here says which two of them a benchmark should report -- it says that two of them are the fields the corpus
already has.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e297_the_ordering_of_the_arms as e297
from experiments import e304_the_decomposition_the_block_asked_for as e304
from experiments import e306_the_ordering_in_the_other_currency as e306

RUNS = Path("runs")
#: What counts as the same number between a recomputed term and a stored field.
TOLERANCE = 1e-9
#: The two arms `e297`'s A2 names, and the two `e306`'s R2 named; X3 is the claim that they are the same pair.
A2_WORST_ON_ACCURACY = "ewc"
A2_BEST_ON_FORGETTING = "ewc"
CLAIMS = (
    ("X1", "the identity holds",
     "`shortfall_mean` equals `1 - final_accuracy` for every arm-replicate that carries both",
     "falsifier: one that differs"),
    ("X2", "and so the two orderings are one",
     "Read with each quantity's own direction, the shortfall's majority edge is the accuracy's on all ten pairs",
     "falsifier: one pair that differs"),
    ("X3", "and `e306`'s R2 is `e297`'s A2",
     "The arm ranked worst on the shortfall is the arm ranked worst on accuracy, and the arm ranked second on the "
     "forgetting term is the one ranked first",
     "falsifier: a different arm at either end"),
)


def accuracies(root: Path = RUNS) -> dict:
    """`(artifact, replicate index, arm) -> final_accuracy`, read from the payloads rather than recomputed."""
    out = {}
    for p in sorted(Path(root).glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        methods = d.get("methods")
        if not isinstance(methods, dict):
            continue
        for arm, entry in methods.items():
            if not isinstance(entry, dict):
                continue
            for i, rep in enumerate(entry.get("replicates") or []):
                if isinstance(rep, dict) and isinstance(rep.get("final_accuracy"), (int, float)):
                    out[(p.name, i, arm)] = rep["final_accuracy"]
    return out


def rows_with_accuracy(root: Path = RUNS) -> tuple[list[dict], int]:
    """`e304`'s rows joined to the stored accuracy, and how many rows the join could not reach."""
    acc = accuracies(root)
    rows, _ = e304.replicates(root)
    joined, missed = [], 0
    for r in rows:
        a = acc.get((r["artifact"], r["replicate"], r["arm"]))
        if a is None:
            missed += 1
            continue
        joined.append({**r, "accuracy": a})
    return joined, missed


def majority(rows: list[dict], field: str, higher_is_better: bool) -> dict:
    """The majority edge of each pair over the joined rows, with each quantity read in its own direction."""
    by: dict = {}
    for r in rows:
        by.setdefault((r["artifact"], r["replicate"]), {})[r["arm"]] = r
    out = {}
    for a, b in itertools.combinations(e306.ARMS, 2):
        aw = bw = 0
        for arms in by.values():
            if a not in arms or b not in arms:
                continue
            va, vb = arms[a].get(field), arms[b].get(field)
            if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
                continue
            if va == vb:
                continue
            a_better = (va > vb) if higher_is_better else (va < vb)
            aw += a_better
            bw += not a_better
        out[f"{a}>{b}"] = {"winner": a if aw > bw else (b if bw > aw else None), "n": aw + bw}
    return out


def order(edges: dict) -> list[str]:
    """Best to worst, from the majority edges."""
    wins = {a: 0 for a in e306.ARMS}
    for e in edges.values():
        if e["winner"]:
            wins[e["winner"]] += 1
    return sorted(e306.ARMS, key=lambda a: -wins[a])


def reading(root: Path = RUNS) -> dict:
    rows, missed = rows_with_accuracy(root)
    bad = [r for r in rows if abs(r["shortfall_mean"] - (1 - r["accuracy"])) > TOLERANCE]
    shortfall = majority(rows, "shortfall_mean", higher_is_better=False)
    accuracy = majority(rows, "accuracy", higher_is_better=True)
    differing = [k for k in shortfall if shortfall[k]["winner"] != accuracy.get(k, {}).get("winner")]
    sf_order = order(shortfall)
    lost_order = e306.majority(e306.pairs_by_replicate(root), "lost_mean")["order"]
    linear = [r for r in rows if abs(r["shortfall_mean"] - (r["lost_mean"] + r["unlearned_mean"])) > TOLERANCE]
    return {"rows": len(rows), "missed": missed, "identity_violations": len(bad),
            "shortfall_order": sf_order, "accuracy_order": order(accuracy), "lost_order": lost_order,
            "differing_pairs": differing, "n_pairs": len(shortfall),
            "linear_violations": len(linear),
            #: `e297`'s own orderings on its own population, read here so X3 is a cross-unit check rather than a
            #: constant: `e308` showed the unit of the vote moves the top, so the two units' first arms differ and
            #: what X3 turns on is that the arm `e306` ranks second on the forgetting term is the arm `e297` ranks
            #: first there, and that the arm worst on the shortfall is the one `e297` ranks last on accuracy.
            "e297_forgetting": e297.order([x for x in e297.pairs(root) if x["metric"] == "mean_forgetting"],
                                          "mean_forgetting")["worst_first"][::-1],
            "e297_accuracy": e297.order([x for x in e297.pairs(root) if x["metric"] == "final_accuracy"],
                                        "final_accuracy")["worst_first"][::-1],
            "worst_on_shortfall": sf_order[-1], "worst_on_accuracy": order(accuracy)[-1],
            "second_on_forgetting": lost_order[1], "best_on_forgetting": lost_order[0]}


def judge(r: dict) -> list[dict]:
    if not r.get("rows"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no arm carries both an accuracy and a matrix"}
                for c in CLAIMS]

    out = [{"id": "X1", "measured": f"{r['identity_violations']} of {r['rows']} arm-replicates where "
                                    f"`shortfall_mean` differs from `1 - final_accuracy`; {r['missed']} row(s) "
                                    f"without a stored accuracy were not read",
            "verdict": "MET -- the shortfall is the accuracy's complement and not a second quantity" if
            not r["identity_violations"] else f"FALSIFIER FIRED -- {r['identity_violations']} differ"}]

    out.append({"id": "X2", "measured": f"the shortfall orders {r['shortfall_order']} and the accuracy "
                                        f"{r['accuracy_order']}; the majority edge differs on "
                                        f"{len(r['differing_pairs'])} of {r['n_pairs']} pairs "
                                        f"{r['differing_pairs'] or ''}".strip(),
                "verdict": "MET -- the two quantities order the arms identically when each is read its own way" if
                not r["differing_pairs"] and r["shortfall_order"] == r["accuracy_order"] and
                r["linear_violations"] == 0 else
                f"FALSIFIER FIRED -- {r['differing_pairs']}"})

    forget297 = r.get("e297_forgetting") or []
    acc297 = r.get("e297_accuracy") or []
    ends = (bool(forget297) and bool(acc297) and
            r["worst_on_shortfall"] == r["worst_on_accuracy"] == acc297[-1] and
            r["second_on_forgetting"] == forget297[0])
    out.append({"id": "X3", "measured": f"this unit ranks `{r['worst_on_shortfall']}` worst on the shortfall and "
                                        f"`{r['second_on_forgetting']}` second on the forgetting term; `e297` on "
                                        f"its own population ranks {acc297[-1] if acc297 else '?'} last on accuracy "
                                        f"and {forget297[0] if forget297 else '?'} first on forgetting",
                "verdict": "MET -- the same arm sits at the crosses of both sentences, so `e306`'s R2 is `e297`'s A2"
                if ends else f"FALSIFIER FIRED -- {r['worst_on_shortfall']}, {r['second_on_forgetting']}"})
    return out


def report(r: dict) -> int:
    print("== what the shortfall is ==")
    print(f"   {r['rows']} arm-replicates carry both a retention matrix and a stored accuracy "
          f"({r['missed']} could not be joined)")
    print(f"   `shortfall_mean` equals `1 - final_accuracy` in {r['rows'] - r['identity_violations']} of them, and "
          f"`lost + unlearned` equals it in {r['rows'] - r['linear_violations']}")
    print(f"   the shortfall orders {' > '.join(r['shortfall_order'])}")
    print(f"   the accuracy  orders {' > '.join(r['accuracy_order'])}")
    print(f"   the edges differ on {len(r['differing_pairs'])} of {r['n_pairs']} pairs")

    print("\n== the registered claims, X1-X3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the third quantity `e306` ordered is the corpus's own accuracy, so the disagreement it found")
    print("    between the metric and the shortfall is the cross-metric reversal `e297` had already measured)")
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
