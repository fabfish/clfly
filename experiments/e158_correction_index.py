"""E158 -- the corrections index: every finding that corrects something, and where the correction lands.

This project corrects in place and says so, which means the record's *true* state is spread between the paper,
the plan and **55 findings that carry a correction marker**. A reader arriving fresh cannot tell from the paper
alone which of its sentences has since been qualified, and the audits that exist cover tables (`e105`),
enumerations (`e126`), derivations (`e132`) and the programme table (`e127`) -- **none of them covers
corrections**.

This is not that checker, and the reason is worth stating: matching a correction to the place it was applied
requires deciding whether two sentences say the same thing, and a scanner that guesses wrong is worse than no
scanner (rule 22). **What can be done exactly is the index**: find every sentence that carries a correction
marker, extract the paper sections it names, and list them so that a reader can check the short list by hand
instead of re-reading 200 findings. The one verdict it does print is a **count of how many name no section at
all**, because those are exactly the corrections no reader will ever find.

    python -m experiments.e158_correction_index
    python -m experiments.e158_correction_index --json-out runs/e158_corrections_index.json

Reads only documents; runs nothing. ASCII output only.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from clfly.bench.artifacts import write_json

FINDINGS = Path("docs/findings")
PAPER = Path("docs/paper/clfly-v1.md")
#: the markers this project uses when it corrects *its own record* -- as opposed to reporting that a hypothesis
#: failed, which is a result. Kept explicit so the index cannot silently miss one: a new convention means editing
#: this list, which is a change someone reviews.
MARKERS = ("CORRECTED", "corrected in place", "must be corrected", "is withdrawn", "was wrong", "is REFUTED",
           "was REFUTED", "this sentence used to say", "read here until 2026-")
#: a sentence break that keeps the marker with the text it corrects
SENTENCE = re.compile(r"(?<=[.!?])\s+")
SECTION = re.compile(r"§\s?(\d+(?:\.\d+)?)")
#: the last page this project ever finds a correction on
LONG = 400


def ascii_safe(text: str) -> str:
    """Every printed string goes through this: the console is GBK and a sigma or a Unicode minus kills the run."""
    return text.encode("ascii", "replace").decode("ascii")


def scan(findings: Path = FINDINGS) -> list[dict]:
    out = []
    for path in sorted(findings.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for para in text.split("\n\n"):
            for sentence in SENTENCE.split(para):
                hit = next((m for m in MARKERS if m in sentence), None)
                if not hit:
                    continue
                sections = sorted(set(SECTION.findall(sentence)))
                flat = " ".join(sentence.split())
                if len(flat) < 40:                      # a marker in a two-word line is a heading, not a correction
                    continue
                # A `§N` inside a finding is usually the FINDING's own section N, so a section is only attributed
                # to the paper when the sentence says so. The JSON keeps both, so a reader can see the difference.
                names_paper = "paper" in sentence.lower()
                out.append({"finding": path.stem, "marker": hit,
                            "sections": sections if names_paper else [],
                            "self_sections": [] if names_paper else sections,
                            "sentence": flat[:LONG] + (" ..." if len(flat) > LONG else "")})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    rows = scan()
    paper = PAPER.read_text(encoding="utf-8")
    # the paper's own markers, counted with the SAME convention list -- the comparable number. The looser count
    # (any occurrence of "corrected", "withdrawn", "used to say") is printed beside it because the difference is
    # the whole point: a phrase like "has been corrected" is prose, and only the conventions are markers.
    paper_marked = sum(paper.count(m) for m in MARKERS)
    paper_loose = len(re.findall("corrected|CORRECTED|withdrawn|used to say", paper))
    by_section: dict[str, list[dict]] = defaultdict(list)
    unnamed = []
    for r in rows:
        if r["sections"]:
            for s in r["sections"]:
                by_section[s].append(r)
        else:
            unnamed.append(r)

    print(f"== {len(rows)} correction sentences in {len({r['finding'] for r in rows})} findings ==")
    print(f"   {len(rows) - len(unnamed)} name a paper or plan section; {len(unnamed)} name none")
    print(f"   the paper carries {paper_marked} markers under the SAME conventions "
          f"(and {paper_loose} occurrences of the words, the rest being prose like 'has been corrected')")
    print("\n== by section, the ones a reader should check first ==")
    for section in sorted(by_section, key=lambda s: (len(s), s)):
        rows_s = by_section[section]
        if len(section) > 2:                            # a numbered item rather than a section
            continue
        print(f"   section {section}: {len(rows_s)} correction sentence(s)")
        for r in rows_s[:3]:
            print(f"      {ascii_safe(r['finding'][:52]):<54} [{r['marker']}]")
        if len(rows_s) > 3:
            print(f"      ... and {len(rows_s) - 3} more")
    print("\n== and the corrections that name no section, which no reader will find ==")
    for r in unnamed[:10]:
        print(f"   {ascii_safe(r['finding'][:50]):<52} [{r['marker']}] {ascii_safe(r['sentence'][:90])}")
    if len(unnamed) > 10:
        print(f"   ... and {len(unnamed) - 10} more (the JSON artifact holds all of them)")

    print("\n== reading ==")
    print("   This is an INDEX and not a checker: it makes the short list a reader can verify by hand, and it")
    print("   deliberately prints no 'applied / not applied' verdict, because that decision needs semantics and a")
    print("   scanner that guesses is worse than none (rule 22). What it does count exactly is the unnamed ones.")
    print(f"   The paper's own markers ({paper_marked}) are the other half of the index: a reader can search the")
    print("   paper for the same nine conventions.")

    if args.json_out:
        write_json(args.json_out, {"rows": rows, "by_section": {k: v for k, v in by_section.items()},
                                   "unnamed": unnamed})
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
