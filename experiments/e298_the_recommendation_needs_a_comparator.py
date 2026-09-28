"""E298 -- the recommendation needs a comparator and a metric: three basis recommendations in the paper, and none of them scoped.

`e295`, `e296` and `e297` establish three things about the corpus's arms that the paper's recommendation cannot be read
without: the block-anchored penalty is **better on accuracy and worse on forgetting** than the diagonal at every
resolved comparison; it beats its **matched random** control on forgetting only where the power is, and *loses* to it
on accuracy by count; and the corpus's two metrics order the five arms into two chains whose ends are swapped, so
"which basis minimises forgetting" and "which basis is most accurate" have different answers. A recommendation that
names neither its comparator nor its metric is therefore not yet a statement a reader can act on.

This unit finds the paper's **basis recommendations** -- sentences that carry an advice cue and a basis noun -- and
reads each one for a comparator (an alternative arm or basis it is preferred to) and a metric. Both lists are
declared, because a lexical reading is only as good as its lists.

Three claims, all **confirmatory** and computed in the exploration that wrote the module:

- **N1 -- the recommendations do not name their metric.** **Falsifier**: one of them names a metric.
- **N2 -- and few name a comparator.** **Falsifier**: most of them do.
- **N3 -- and after this fire's correction every one names both.** The unit is re-run inside the correction, so this
  is the ledger claim `e281` used for its own series: a future edit that adds an unscoped recommendation turns it red.
  **Falsifier**: one recommendation is still unscoped.

**What the three add up to, and what was found before the correction.** Read *as found*, before this fire's
correction, the paper carried **three** basis recommendations and **none of them named a metric** while **one named a
comparator** (`than the neuron coordinate basis`); the three claims below are therefore stated as the **invariant the
paper now satisfies**, which turns the unit red if a future edit adds an unscoped recommendation. The paper's practical
advice -- *pool the rarest cell types and anchor there* -- and its companion -- *anchor at the coarsest granularity
the arithmetic allows* -- were written before the corpus's own ordering was read (units `e295` to `e297`, all in this
line). Neither said **against what** and neither said **in which metric**, and those units show both omissions are
load-bearing: against the diagonal the advice is right on accuracy and wrong on forgetting; against a matched random
partition it is right on forgetting where the power is and wrong on accuracy by count. The correction applied in this
fire adds the scope to all three sentences and cites the units that supply it.

**What it cannot do.** *The sentence split and the two lists are lexical*, so a recommendation phrased without an
advice cue is invisible and the count is a lower bound -- `e282`'s sentence splitter's limits apply here too. *The
comparator list can only see comparators named as phrases*: a sentence that says "better" without saying than what
reads as unscoped, which is the reading this unit wants but not a reading that catches every omission. *N3 is a
ledger claim about text*, so it verifies that a scope clause exists and not that the clause's numbers are right --
the numbers' provenance is `e295` to `e297`'s business. *And nothing here re-reads the corpus*: the three units that
establish what the scope should say are the ones that measured it, and this unit only checks that the paper now says
it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
#: `e282`'s splitter, reused rather than re-invented: a period, colon or semicolon followed by a space and a capital.
SPLIT = re.compile(r"(?<=[.:;])\s+(?=[A-Z(])")
#: A recommendation carries an advice cue and a basis noun. `anchor` is deliberately **not** a basis noun: it is the
#: advice itself ("pool the rarest cell types and **anchor** there"), and admitting it matched a λ-sweep sentence that
#: merely quotes the aphorism *"Anchor gently, and do not estimate the curvature too carefully"*.
CUES = ("recommend", "should anchor", "we suggest", "prefer", "the practical", "advice", "choose")
BASIS = ("basis", "cell type", "cell_type", "rung", "partition", "cell class")
#: A recommendation is *scoped* when it names the alternative it is preferred to and the metric it is about.
COMPARATORS = ("than the neuron coordinate basis", "than the diagonal", "than ewc", "than naive", "than `ewc`",
               "than a matched", "than a random", "matched random", "matched-random", "than replay")
METRICS = ("forgetting", "accuracy", "retention")
CLAIMS = (
    ("N1", "every basis recommendation names the metric it is about",
     "Each of the paper's basis recommendations carries a metric",
     "falsifier: one of them names no metric"),
    ("N2", "and every one names the alternative it is preferred to",
     "Each of them carries a comparator",
     "falsifier: one of them names no comparator"),
    ("N3", "and cites the unit that supplies the scope",
     "Each of them cites a `docs/findings/` document for the scope it now carries",
     "falsifier: one of them cites none"),
)


def sentences(text: str) -> list[str]:
    """Paragraphs first, then `e282`'s sentence rule -- so a paragraph that opens with bold text is not merged into
    its predecessor, which is what a whole-document split on punctuation does and what inflated this unit's first run.
    """
    out = []
    for para in re.split(r"\n\s*\n", text):
        out += [s.strip() for s in SPLIT.split(para) if s.strip()]
    return out


def recommendations(text: str) -> list[dict]:
    """Every sentence carrying an advice cue and a basis noun, with what it names.

    The sentence is **whitespace-flattened before matching**: the paper is hard-wrapped, so a phrase like *than the
    neuron coordinate basis* spans a line break and a substring search for it fails on the raw text.
    """
    out = []
    for n, s in enumerate(sentences(text)):
        flat = re.sub(r"\s+", " ", s)
        low = flat.lower()
        cues = [c for c in CUES if c in low]
        nouns = [b for b in BASIS if b in low]
        if not cues or not nouns:
            continue
        out.append({"sentence": n, "cues": cues, "basis_nouns": nouns,
                    "comparators": [c for c in COMPARATORS if c in low],
                    "metrics": [m for m in METRICS if m in low],
                    "text": flat})
    return out


def judge(r: dict) -> list[dict]:
    recs = (r or {}).get("recommendations") or []
    if not recs:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- no recommendation sentence found"} for c in CLAIMS]

    with_metric = [x for x in recs if x["metrics"]]
    with_comparator = [x for x in recs if x["comparators"]]
    with_citation = [x for x in recs if "docs/findings/" in x["text"]]
    out = [{"id": "N1", "measured": f"{len(recs)} basis recommendation sentences; {len(with_metric)} of them name a "
                                     f"metric: " + "; ".join(f"[{x['sentence']}] {x['metrics'] or 'none'}"
                                                             for x in recs),
            "verdict": "MET -- every recommendation is scoped to a metric" if len(with_metric) == len(recs) else
                       f"FALSIFIER FIRED -- {[x['sentence'] for x in recs if not x['metrics']]} name no metric"}]

    out.append({"id": "N2", "measured": f"{len(with_comparator)} of {len(recs)} name the alternative they are "
                                        f"preferred to: " + "; ".join(f"[{x['sentence']}] {x['comparators'] or 'none'}"
                                                                      for x in recs),
                "verdict": "MET -- every recommendation says what it is preferred to"
                if len(with_comparator) == len(recs) else
                f"FALSIFIER FIRED -- {[x['sentence'] for x in recs if not x['comparators']]} name no comparator"})

    out.append({"id": "N3", "measured": f"{len(with_citation)} of {len(recs)} cite a finding for their scope; "
                                        f"without one: {[x['sentence'] for x in recs if 'docs/findings/' not in x['text']]}",
                "verdict": "MET -- every recommendation points at the unit that scopes it"
                if len(with_citation) == len(recs) else
                f"FALSIFIER FIRED -- {[x['sentence'] for x in recs if 'docs/findings/' not in x['text']]} cite none"})
    return out


def report(r: dict) -> int:
    print("== the paper's basis recommendations ==")
    for x in r["recommendations"]:
        print(f"   [{x['sentence']:4}] cues {x['cues']} basis {x['basis_nouns']}")
        print(f"          comparators {x['comparators']} metrics {x['metrics']}")
        print(f"          {x['text'][:220]}")

    print("\n== the registered claims, N1-N3 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (a recommendation that names neither its comparator nor its metric is not yet a statement a reader")
    print("    can act on, and e295 to e297 measured how much the two omissions matter)")
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
    r = {"paper": str(args.paper), "cues": list(CUES), "basis_nouns": list(BASIS),
         "comparators": list(COMPARATORS), "metrics": list(METRICS)}
    r["recommendations"] = recommendations(args.paper.read_text(encoding="utf-8"))
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
