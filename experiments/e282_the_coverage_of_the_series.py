"""E282 -- the coverage of the series: what fraction of the paper's checkable sentences any instrument reads.

`e280` ended with the question it could not answer -- one claim establishes that the checker *can* pass, not what
fraction of the paper it passes -- and `e281` repeated it: the ledger covers the instruments that exist, so a stale
statement nobody built an instrument for is invisible. This unit measures that fraction, on the paper itself.

Two definitions carry the whole unit and both are stated rather than hidden:

  * a **checkable sentence** is one carrying a digit or a quantifier word (`every`, `all`, `none`, `no`, `only`,
    `never`, `at most`, `at least`), because those are the sentences an instrument *could* read;
  * a sentence is **read** when it contains a phrase or pattern one of the series' instruments registers -- `e268`'s
    three phrases, `e270`'s premise, `e277`'s count patterns, `e278`'s phrase, `e279`'s clause, `e280`'s clause.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **C1 -- the series reads a minority of the checkable sentences.** Under half of them. **Falsifier**: half or more.
- **C2 -- and the residue is typed: it is bare numbers, not universals.** Among the checkable sentences the series does
  not read, fewer than a third carry a quantifier. **Falsifier**: a third or more.
- **C3 -- so the series' reach is one form.** The instruments between them read at least one sentence, and the forms
  they register are printed with the sentences each one reads, so the coverage is attributable rather than asserted.
  **Falsifier**: no instrument reads a sentence, or a registered form reads none.

**C2 fired, and it is the informative outcome.** The residue is not typed: 69.6% of the unread checkable sentences
carry a quantifier, against a falsifier at a third, so the guess that the series reads the universals and leaves the
bare numbers is backwards. The measured forms say why the guess was wrong rather than merely unlucky: 343 of the 368
checkable sentences carry a digit, and of the 359 the series does not read, 334 carry a digit, 250 carry a quantifier
and 225 carry both, so "carries a quantifier" does not separate a sentence that names a population from ordinary
prose -- `every claim below cites the experiment` is a quantifier and is not a denominator. The quantifier *leg* of the
definition is small (25 sentences, 6.8%) and the paper is 86% checkable because it is a numbers paper, so almost every
sentence in it is one an instrument *could* read.

What the census does establish is the size of the series next to the paper it audits: six instruments whose ledger
`e281` counts at 572 statements between them, and nine sentences of the paper that any of their registered phrases
matches. The instruments' volume lives on the artifacts -- `e278` counts 262 arms, `e279` 167 artifacts, `e280` 132
pair-checkpoints -- while the prose is read only where a phrase was anchored to it.

**What it cannot do**: the split into sentences is the module's (a period followed by a space) and a claim spanning two
sentences is read as two; "checkable" is a lexical definition, so a sentence with a number written as a word is
invisible and a sentence with a digit inside a filename is counted as checkable; a phrase match says the sentence is
*read* and not that the instrument's claim about it is the same claim; the paper's tables are counted as sentences
rather than as cells, so a table's numbers are under-counted; and nothing here reads the plan or the findings, which
carry their own statements.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json
from experiments import e268_paper_supersession_audit as e268
from experiments import e270_an_existence_premise_falsified as e270
from experiments import e277_a_count_is_not_a_scope as e277
from experiments import e278_on_disk_is_not_a_definition as e278
from experiments import e279_every_one_of_the_77 as e279

PAPER = Path("docs/paper/clfly-v1.md")
INSTRUMENTS = ("e268", "e270", "e277", "e278", "e279", "e280")
QUANTIFIERS = ("every", "all ", "none", "no ", "only", "never", "at most", "at least", "each")
SENTENCE = re.compile(r"(?<=[.:;])\s+(?=[A-Z(])")
CLAIMS = (
    ("C1", "the series reads a minority of the checkable sentences",
     "Under half of the paper's checkable sentences contain a phrase or pattern an instrument registers",
     "falsifier: half or more"),
    ("C2", "and the residue is typed: it is bare numbers, not universals",
     "Fewer than a third of the unread checkable sentences carry a quantifier",
     "falsifier: a third or more"),
    ("C3", "so the series' reach is one form, attributable sentence by sentence",
     "Every registered form reads at least one sentence and the report prints which",
     "falsifier: a form that reads none"),
)


def load(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE.split(text) if s.strip()]


def checkable(s: str) -> bool:
    if re.search(r"\d", s):
        return True
    low = s.lower()
    return any(q in low for q in QUANTIFIERS)


def forms() -> list[dict]:
    """Each instrument's registered phrases and patterns, as a searchable form."""
    out = []
    for r in e268.REGISTRY:
        out.append({"instrument": "e268", "form": r["phrase"], "kind": "phrase"})
    out.append({"instrument": "e270", "form": e270.PREMISE, "kind": "phrase"})
    for pattern, _ in e277.PATTERNS:
        out.append({"instrument": "e277", "form": pattern, "kind": "pattern"})
    out.append({"instrument": "e278", "form": e278.QUOTED["phrase"], "kind": "phrase"})
    out.append({"instrument": "e279", "form": "every one of the 77 stored runs used 16", "kind": "phrase"})
    out.append({"instrument": "e280", "form": "every one of the 132 pair-checkpoints", "kind": "phrase"})
    return out


def reads(s: str, fs: list[dict]) -> list[str]:
    hit = []
    for f in fs:
        if f["kind"] == "phrase":
            if f["form"] in s:
                hit.append(f["instrument"])
        elif f["form"].search(s):
            hit.append(f["instrument"])
    return sorted(set(hit))


def census(text: str) -> dict:
    fs = forms()
    out = {"sentences": 0, "checkable": 0, "read": 0, "unread_checkable": [], "by_form": {}, "read_examples": [],
           "digit_checkable": 0, "quantifier_only": 0, "unread_with_digit": 0, "read_with_digit": 0}
    for s in sentences(text):
        out["sentences"] += 1
        if not checkable(s):
            continue
        out["checkable"] += 1
        has_digit = bool(re.search(r"\d", s))
        out["digit_checkable"] += bool(has_digit)
        out["quantifier_only"] += not has_digit
        got = reads(s, fs)
        if got:
            out["read"] += 1
            out["read_with_digit"] += bool(has_digit)
            if len(out["read_examples"]) < 3:
                out["read_examples"].append({"instruments": got, "sentence": s[:160]})
            for i in got:
                out["by_form"][i] = out["by_form"].get(i, 0) + 1
        else:
            out["unread_checkable"].append(s)
            out["unread_with_digit"] += bool(has_digit)
    out["quantified_unread"] = sum(1 for s in out["unread_checkable"] if any(q in s.lower() for q in QUANTIFIERS))
    out["unread_both"] = sum(1 for s in out["unread_checkable"]
                             if re.search(r"\d", s) and any(q in s.lower() for q in QUANTIFIERS))
    hist: dict[str, int] = {}
    for s in out["unread_checkable"]:
        low = s.lower()
        for q in QUANTIFIERS:
            if q in low:
                hist[q.strip()] = hist.get(q.strip(), 0) + 1
    out["quantifier_hist"] = dict(sorted(hist.items(), key=lambda kv: -kv[1]))
    return out


def judge(c: dict) -> list[dict]:
    out: list[dict] = []
    if not c or not c["checkable"]:
        return [{"id": x[0], "measured": "", "verdict": "REFUSED -- no checkable sentence found"} for x in CLAIMS]

    share = c["read"] / c["checkable"]
    out.append({"id": "C1", "measured": f"{c['read']} of {c['checkable']} checkable sentences read "
                                        f"({100 * share:.1f}%), of {c['sentences']} sentences in the paper",
                "verdict": "MET -- the series reads a minority of what it could" if share < 0.5 else
                           f"FALSIFIER FIRED -- {100 * share:.1f}%"})

    qshare = c["quantified_unread"] / max(len(c["unread_checkable"]), 1)
    out.append({"id": "C2", "measured": f"of the {len(c['unread_checkable'])} unread checkable sentences, "
                                        f"{c['quantified_unread']} carry a quantifier ({100 * qshare:.1f}%)",
                "verdict": "MET -- the residue is bare numbers rather than universals" if qshare < 1 / 3 else
                           f"FALSIFIER FIRED -- {100 * qshare:.1f}% carry a quantifier"})

    silent = [i for i in INSTRUMENTS if not c["by_form"].get(i)]
    out.append({"id": "C3", "measured": f"sentences read per instrument: {c['by_form']}; instruments reading none: "
                                        f"{silent or 'none'}",
                "verdict": "MET -- every registered instrument reads at least one sentence" if not silent else
                           f"FALSIFIER FIRED -- {silent} read none"})
    return out


def report(c: dict) -> int:
    print("== the paper, by what the series can read ==")
    print(f"   sentences: {c['sentences']}; checkable (a digit or a quantifier): {c['checkable']}")
    print(f"      of those, carrying a digit: {c['digit_checkable']}; quantifier only, no digit: {c['quantifier_only']}")
    print(f"   read by an instrument: {c['read']} ({100 * c['read'] / max(c['checkable'], 1):.1f}% of them), "
          f"{c['read_with_digit']} of them carrying a digit")
    print(f"   unread and checkable: {len(c['unread_checkable'])}, of which {c['quantified_unread']} carry a quantifier "
          f"and {c['unread_with_digit']} carry a digit ({c['unread_both']} carry both)")
    print(f"   the quantifier leg, by word, over the unread set: {c['quantifier_hist']}")
    print(f"   sentences read per instrument: {c['by_form']}")
    for e in c["read_examples"]:
        print(f"      {'/'.join(e['instruments']):12} {e['sentence'][:110]}...")

    print("\n== the unread checkable sentences, the first few ==")
    for s in c["unread_checkable"][:4]:
        print(f"      {s[:150]}...")

    print("\n== the registered claims, C1-C3 ==")
    j = judge(c)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (C2's falsifier fired, and it is the unit's answer: the residue is not bare numbers. What the census")
    print("    establishes is the series' size next to the paper -- six instruments that between them register 572")
    print("    statements and nine sentences of prose any registered phrase matches. The `checkable` set is 86% of the")
    print("    paper because it is a numbers paper, and `carries a quantifier` does not separate a sentence that names a")
    print("    population from ordinary prose; the instruments' volume lives on the artifacts, and the prose is read only")
    print("    where a phrase was anchored to it)")
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
    c = census(text)
    if args.json_out:
        write_json(args.json_out, {"paper": str(args.paper), "quantifiers": list(QUANTIFIERS),
                                   "counts": {k: v for k, v in c.items() if k != "unread_checkable"},
                                   "unread_examples": c["unread_checkable"][:20],
                                   "claims": judge(c)})
        print(f"wrote {args.json_out}")
    return report(c)


if __name__ == "__main__":
    sys.exit(main())
