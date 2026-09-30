"""E300 -- the abstract's findings: the four headlines already name their comparator and their metric, where the recommendations did not.

`e298` read the paper for its **basis recommendations** and found three of them, none of which named a metric and only
one of which named a comparator; the correction applied there added the scope. That raises the question this unit asks
of the document's *most read* claims: the abstract's numbered findings. If the recommendations were unscoped while the
headlines were scoped, then the paper's scope is a property of *where a sentence sits* rather than of the claim it
makes -- and that is a fact about the audit trail worth having on the record.

Two claims, both **confirmatory** and computed in the exploration that wrote the module:

- **A1 -- the abstract states its findings as a numbered list.** **Falsifier**: no numbered finding list.
- **A2 -- and every one of them names a metric and a comparator.** The invariant `e298` registers for the
  recommendations, applied to the headlines. **Falsifier**: one finding that names no metric or no comparator.

**What the two add up to.** The abstract's four findings each carry numbers, a metric (*excess error*, *σ*, *accuracy*)
and a comparator (*the exact Kalman oracle*, *LGCL's synthetic random-rotation family*, *capacity-matched random
partitions*, *the neuron diagonal*), so the document scopes the claims a reader meets first and left the advice a
reader acts on unscoped until `e298`. That is the useful shape of this unit: **it is the same paper, and the scope is a
property of the sentence's role rather than of its content** -- a finding is written with its comparison in it because
a finding *is* a comparison, while a recommendation was written as an instruction and an instruction does not have to
say what it beats.

**What it cannot do.** *The reader takes a numbered item as one sentence*: an item's text runs several paragraphs in
places, so "names a metric" is satisfied by *any* paragraph of the item and not by its headline sentence -- which
makes A2 a weaker check than the same check on the recommendations. *The metric and comparator lists are lexical*, so
an item that names a comparison in words the lists do not carry reads as unscoped. *An item can be scoped and still be
wrong*: whether the finding's numbers hold is the business of the units that measured them (`e289`, `e293`, `e295` to
`e297`), and this unit reads only whether the scope is *stated*. *And the as-found comparison with `e298` cannot be
re-run* -- the recommendations now carry the scope that this fire's sibling added, so the three-versus-four contrast
lives in the two findings rather than in a live check.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
#: A numbered finding opens a line with a digit, a dot and a bold heading. The heading is matched non-greedily and
#: allows nested emphasis, because one of the four headlines carries `*not*` inside its bold.
FINDING = re.compile(r"^(?P<n>\d)\.\s+\*\*(?P<head>.+?)\*\*", re.M | re.S)
#: The section the findings live in: from the abstract heading to the next horizontal rule.
SECTION = re.compile(r"##\s*Abstract\s*\n(?P<body>.*?)\n---", re.S)
#: What an item has to name: the quantity it is about, and the thing it is compared with.
METRICS = ("excess", "forgetting", "accuracy", "retention", "σ", "sigma")
COMPARATORS = ("oracle", "lgcl", "random", "diagonal", "naive", "matched", "control", "synthetic", "rewired",
               "erdos", "erdős")
CLAIMS = (
    ("A1", "the abstract states its findings as a numbered list",
     "The abstract carries numbered findings",
     "falsifier: no numbered finding list"),
    ("A2", "and every one names a metric and a comparator",
     "Each finding carries the quantity it is about and the thing it is compared with",
     "falsifier: one finding that names no metric or no comparator"),
)


def findings(text: str) -> list[dict]:
    """The abstract's numbered findings, each with the text of its whole item.

    The reader works on the **abstract section** and not on the whole document: the paper carries several other
    numbered lists (§8's seven recommendations among them), and reading those as headlines was this unit's first
    mistake.
    """
    section = SECTION.search(text)
    body_text = section.group("body") if section else ""
    hits = list(FINDING.finditer(body_text))
    out = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(body_text)
        body = body_text[m.end():end]
        flat = re.sub(r"\s+", " ", body).strip()
        low = flat.lower()
        out.append({"n": int(m.group("n")), "heading": re.sub(r"\s+", " ", m.group("head")).strip(),
                    "text": flat,
                    "metrics": [x for x in METRICS if x in low],
                    "comparators": [x for x in COMPARATORS if x in low]})
    return out


def judge(r: dict) -> list[dict]:
    items = (r or {}).get("findings") or []
    if not items:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no numbered finding found"} for c in CLAIMS]

    out = [{"id": "A1", "measured": f"{len(items)} numbered findings: "
                                    + "; ".join(f"{x['n']}. {x['heading'][:56]}" for x in items),
            "verdict": "MET -- the abstract states its findings as a numbered list" if len(items) >= 2 else
                       "FALSIFIER FIRED -- one or no numbered finding"}]

    unscoped = [x for x in items if not x["metrics"] or not x["comparators"]]
    out.append({"id": "A2", "measured": f"{len(items) - len(unscoped)} of {len(items)} findings name both a metric and "
                                        f"a comparator: "
                                        + "; ".join(f"{x['n']} {x['metrics'] or 'no metric'}/"
                                                    f"{x['comparators'] or 'no comparator'}" for x in items),
                "verdict": "MET -- every headline names what it is about and what it beats" if not unscoped else
                           f"FALSIFIER FIRED -- {[x['n'] for x in unscoped]} are unscoped"})
    return out


def report(r: dict) -> int:
    print("== the abstract's numbered findings ==")
    for x in r["findings"]:
        print(f"   {x['n']}. {x['heading']}")
        print(f"      metrics {x['metrics']}  comparators {x['comparators']}")
        print(f"      {x['text'][:150]}...")

    print("\n== and the surface `e298` read, for the contrast ==")
    print("   the three basis recommendations named 0 of 3 metrics and 1 of 3 comparators as found,")
    print("   and carry the scope only because `e298` added it -- while the findings above were already scoped")

    print("\n== the registered claims, A1-A2 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (the paper scopes the claims a reader meets first and left the advice a reader acts on unscoped: the")
    print("    scope is a property of the sentence's role and not of its content)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paper", type=Path, default=PAPER)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    if not args.paper.exists():
        raise SystemExit(f"need {args.paper}")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    text = args.paper.read_text(encoding="utf-8")
    r = {"paper": str(args.paper), "metrics": list(METRICS), "comparators": list(COMPARATORS)}
    r["findings"] = findings(text)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
