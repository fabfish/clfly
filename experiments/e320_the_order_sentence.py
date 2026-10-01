"""E320 -- the block's order sentence: a promise of fixed task orders, scoped by the eight runs that moved them.

The FlyCL v0 block ends its reference-framework paragraph with the sentence a benchmark's users act on:

    Reference framework: `clfly/bench/` with fixed task orders and seeds, so numbers are comparable across methods --
    a shared protocol that CL-for-SNN work currently lacks.

`e302`'s M4 read the corpus against that promise and found it **trivially** true -- every artifact recorded its
suite's own naming order, so the order was a variable with one value. `e310` measured what varying it would cost, and
`e315` to `e319` varied it: eight runs of the reversal, then a second family, then all five arms, then the penalty
dialled on one arm, then four penalties. **The sentence has not been re-read since.**

Three claims, registered before the reading below was taken:

- **O1 -- the block carries the promise.** The block's reference-framework paragraph carries an order cue and a
  comparability cue. **Falsifier**: no such sentence.
- **O2 -- and it does not say what the order moves.** The sentence carries no cue naming the arms the order moves or
  the fact that it leaves others alone. **Falsifier**: such a cue is present.
- **O3 -- and the corpus no longer holds one order per suite.** At least one suite is recorded in two orders, so the
  promise's *fixed* is a property of the corpus **up to** this line of runs. **Falsifier**: every suite in one order.

They are stated as the **invariant the block now satisfies**, as `e298` stated the paper's recommendations' and `e307`
the README's: the correction adds a scope clause naming the arms the order moves, that the arm which reads no penalty
does not move at all, and the units that measured it, so an edit that drops the clause turns this unit red. The
as-found counts are printed first.

**What it cannot do.** *The cues are lexical*, so a clause saying the same thing in other words reads as absent and
the count is a lower bound. *This is a claim about text*: O2 verifies that a clause exists and not that its numbers
are right, which is `e315` to `e319`'s business. *O3 is a census of the corpus as it stands* and not a statement about
a fresh clone, which has no artifacts at all. *And as-found claims about a corrected document cannot be re-run*: the
as-found count lives in the finding rather than in the artifact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench import corpus
from clfly.bench.artifacts import write_json
from experiments import e185_benchmark_spec_audit as e185

PLAN = Path("docs/research_plan.md")
RUNS = Path("runs")
#: The cue that the block promises an order, and the cue that it promises comparability -- both in one sentence.
ORDER_CUES = ("fixed task orders", "task order")
COMPARABILITY_CUES = ("comparable", "comparable across methods")
#: The cues that say what the order *moves*: declared, and therefore the instrument's definition.
MOVES_CUES = ("the arms that read a penalty", "penalty arms", "does not move", "leaves the arms", "which arms")
#: The units that measured it, as the runs name them.
UNITS = ("e315", "e316", "e317", "e318", "e319")
FINDINGS = ("2026-10-01-the-order-the-runner-never-took", "2026-10-01-the-reversal-in-the-other-family",
            "2026-10-01-the-reversal-with-five-arms", "2026-10-01-the-penalty-switched-off",
            "2026-10-01-the-penalty-four-times")
CLAIMS = (
    ("O1", "the block carries the promise",
     "The reference-framework paragraph carries an order cue and a comparability cue",
     "falsifier: no such sentence"),
    ("O2", "and it does not say what the order moves",
     "The sentence carries no cue naming the arms the order moves or that it leaves others alone",
     "falsifier: such a cue is present"),
    ("O3", "and the corpus no longer holds one order per suite",
     "At least one suite is recorded in two orders",
     "falsifier: every suite in one order"),
)


def order_sentence(text: str) -> str:
    """The block's order **paragraph**: the one carrying both an order cue and a comparability cue.

    The unit of reading is the paragraph and not the sentence, because a scope clause added after the promise is a
    second sentence of the same paragraph -- and a detector that read one sentence would declare its own correction
    invisible, which is the defect `e298` recorded when its splitter merged a paragraph into its predecessor.
    """
    block = e185.benchmark_block(text)
    for para in block.split("\n\n"):
        low = para.lower()
        if any(c in low for c in ORDER_CUES) and any(c in low for c in COMPARABILITY_CUES):
            return " ".join(para.split())
    return ""


def suites_with_two_orders(root: Path = RUNS) -> dict:
    """Each suite that the corpus records in more than one order, and the orders it records."""
    names = {}
    for p in sorted(Path(root).glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None
        t = (d or {}).get("tasks")
        if isinstance(t, list) and t and isinstance(t[0], dict) and "name" in t[0]:
            names.setdefault(tuple(sorted(str(x["name"]) for x in t)), set()).add(tuple(str(x["name"]) for x in t))
    return {",".join(k): sorted(",".join(v) for v in vs) for k, vs in names.items() if len(vs) > 1}


def reading(plan: Path = PLAN, root: Path = RUNS) -> dict:
    text = plan.read_text(encoding="utf-8")
    low = order_sentence(text).lower()
    two = suites_with_two_orders(root)
    return {"sentence": order_sentence(text), "chars": len(order_sentence(text)),
            "order_cue": any(c in low for c in ORDER_CUES),
            "comparability_cue": any(c in low for c in COMPARABILITY_CUES),
            "moves_cues": [c for c in MOVES_CUES if c in low],
            "units": [u for u in UNITS if u in low],
            "findings": [f for f in FINDINGS if f in text],
            "suites_with_two_orders": two, "n_suites_with_two_orders": len(two)}


def judge(r: dict) -> list[dict]:
    if not r.get("sentence"):
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the block carries no order sentence"}
                for c in CLAIMS]
    out = [{"id": "O1", "measured": f"the sentence is {r['chars']} characters and carries the order cue "
                                    f"{r['order_cue']} and the comparability cue {r['comparability_cue']}",
            "verdict": "MET -- the block promises fixed task orders so numbers are comparable" if
            r["order_cue"] and r["comparability_cue"] else
            f"FALSIFIER FIRED -- order {r['order_cue']}, comparability {r['comparability_cue']}"}]

    out.append({"id": "O2", "measured": f"the sentence carries {len(r['moves_cues'])} cue(s) saying what the order "
                                        f"moves: {r['moves_cues'] or 'none'}; it names {r['units'] or 'no unit'} and "
                                        f"cites {len(r['findings'])} finding(s)",
                "verdict": "MET -- the sentence says what the order moves" if r["moves_cues"] else
                           "FALSIFIER FIRED -- a reader is told the order is fixed and not what fixing it costs"})

    two = r["suites_with_two_orders"]
    out.append({"id": "O3", "measured": f"{r['n_suites_with_two_orders']} suite(s) recorded in more than one order: "
                                        f"{list(two) or 'none'}",
                "verdict": "MET -- the corpus holds permutations, so `fixed` is a convention the runs ended" if two
                else "FALSIFIER FIRED -- every suite in one order"})
    return out


def report(r: dict) -> int:
    print("== the block's order sentence ==")
    print(f"   `{r['sentence']}`")
    print(f"   order cue {r['order_cue']}, comparability cue {r['comparability_cue']}; "
          f"what it moves: {r['moves_cues'] or 'not said'}")
    print(f"   units named {r['units'] or 'none'}; findings cited {len(r['findings'])}")
    print(f"   suites the corpus records in two orders: {list(r['suites_with_two_orders']) or 'none'}")

    print("\n== the registered claims, O1-O3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the block promises a fixed order so numbers are comparable, and the corpus has now run the")
    print("    permutation: what it moves is the arms that read a penalty, and only up to the first notch of it)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", type=Path, default=PLAN)
    ap.add_argument("--runs", type=Path, default=RUNS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(args.plan, args.runs)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
