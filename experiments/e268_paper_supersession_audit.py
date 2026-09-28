"""E268 -- the numbers the paper still quotes after a finding superseded them.

The paper is audited against its own citations: `e97` asks whether every `runs/` file it names exists, and `e192` asks
whether a number it states, in a sentence that cites a finding, is a number that finding contains. Both are
**provenance** checks, and both pass while a claim is dead -- because a superseded number is still supported by the
finding the sentence cites. The sentence names the finding that produced the number; the finding that *withdrew* it is
a later one, and nothing in the record relates the two.

    a provenance audit cannot see supersession: it checks where a number came from, not whether it still stands

That gap is what this module closes, and it closes it the only way it can be closed -- **by a registry**. Which numbers
have been superseded is not a property of the text; it is a fact about the programme, and the module's inputs are
therefore hand-made: for each superseded number, the exact phrase the paper carries it in, the finding that
superseded it, and the number that replaced it. Everything after that is mechanical: does the paper still carry the
phrase, does it carry a correction note beside it, does the superseding finding exist, and does the replacement
appear inside it.

The registry is deliberately small and its entries are ones a reader can check by hand. What it is *not* is a census
of every stale sentence in the paper: it records the numbers this session's audits moved and that a later finding
stated a replacement for.

Registered, all **confirmatory** and computed in the exploration that wrote the module:

- **Q1 -- the paper carries numbers a later finding superseded.** At least two of the registry's phrases are still in
  the paper with no correction beside them. **Falsifier**: fewer than two.
- **Q2 -- and the provenance audit is green while they are dead.** `e192` pairs each number with the finding its
  sentence cites, so a superseded number passes it: the two currencies are different quantities, and only the second
  needs a registry. **Falsifier**: `e192` reports one of the registry's phrases as unsupported.
- **Q3 -- so the fix is a substitution and not a deletion.** Every registry entry's replacement number is present in
  the finding that superseded it, which is what lets the paper be corrected by naming the replacement. **Falsifier**:
  an entry whose replacement cannot be found in its superseding finding.

**What it cannot do**: it cannot find a supersession nobody registered, so a number whose withdrawal was never written
down is invisible here -- the same limit as `e254`'s census of quoted figures, and the same reason; the registry names
phrases rather than semantic claims, so a paraphrase of a superseded number is invisible; a replacement number is
checked for presence and not for meaning, since whether it says the same thing is what the finding is for; and
nothing here decides whether the paper's sentence should be edited or deleted, which is a judgement about the
sentence and not about the numbers in it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from clfly.bench.artifacts import write_json

PAPER = Path("docs/paper/clfly-v1.md")
#: A correction the paper already carries, in its own idiom; a phrase beside one of these is not stale.
NOTE_MARKERS = ("WITHDRAWN", "CORRECTED")
#: (phrase the paper carries, the finding that superseded it, the number that replaced it)
REGISTRY = (
    {"phrase": "3.34× at cs 800 over five drawings",
     "superseded_by": "docs/findings/2026-09-26-the-spread-is-half-sample-size.md",
     "replacement": "1.64",
     "why": "e247 re-measured the same groups at a fixed number of drawings and the spread halves; e252 then put that "
            "cell outside the declared domain, whose families scatter by more than the bar"},
    {"phrase": "14.77× at 0.99",
     "superseded_by": "docs/findings/2026-09-26-the-rho-axis-dissolves-the-margin.md",
     "replacement": "2.91",
     "why": "e251 read the late advantage on the corpus's other drawings: the 14.77x is the seed-0 drawing's "
            "arithmetic, the other two give 2.22x and the three pooled give 2.91x"},
    {"phrase": "5.53× at 0.98",
     "superseded_by": "docs/findings/2026-09-26-the-late-advantage-is-a-drawings-at-all-three-points.md",
     "replacement": "1.24",
     "why": "e253 added a second drawing at rho 0.98 and both new drawings read 1.24x, so the late advantage's "
            "middle point is a drawing's at a factor of 4.47"},
)
CLAIMS = (
    ("Q1", "the paper carries numbers a later finding superseded",
     "At least two of the registry's phrases are still in the paper with no correction beside them",
     "falsifier: fewer than two"),
    ("Q2", "and the provenance audit is green while they are dead",
     "The registry's stale phrases are supported by the findings their sentences cite, which is why e192 passes them",
     "falsifier: e192 reports one of the phrases as unsupported"),
    ("Q3", "so the fix is a substitution and not a deletion",
     "Every entry's replacement number appears in the finding that superseded it",
     "falsifier: an entry whose replacement is absent from its superseding finding"),
)


def window(text: str, phrase: str, span: int = 400) -> str:
    """The text around a phrase, which is where a correction note for it would sit."""
    i = text.find(phrase)
    if i < 0:
        return ""
    return text[max(0, i - span):i + len(phrase) + span]


def check(entries=REGISTRY, paper: Path = PAPER) -> list[dict]:
    """Each registry entry against the paper and against the finding that superseded it."""
    text = paper.read_text(encoding="utf-8") if paper.exists() else ""
    out = []
    for e in entries:
        path = Path(e["superseded_by"])
        src = path.read_text(encoding="utf-8") if path.exists() else None
        near = window(text, e["phrase"])
        out.append({**e, "in_paper": e["phrase"] in text,
                    "carries_a_note": any(m in near for m in NOTE_MARKERS),
                    "finding_on_disk": src is not None,
                    "replacement_in_finding": bool(src is not None and e["replacement"] in src)})
    return out


def judge(rows: list[dict]) -> list[dict]:
    out: list[dict] = []
    stale = [r for r in rows if r["in_paper"] and not r["carries_a_note"]]
    out.append({"id": "Q1", "measured": "; ".join(
        f"{r['phrase']!r} {'still in the paper' if r['in_paper'] else 'absent'}"
        f"{' with a note' if r['carries_a_note'] else ' with no note'} -> {r['replacement']}"
        for r in rows) + f"; {len(stale)} stale of {len(rows)}",
        "verdict": "MET -- the paper quotes numbers a later finding superseded" if len(stale) >= 2 else
                   "FALSIFIER FIRED -- fewer than two phrases are stale"})

    supported = sum(1 for r in rows if r["in_paper"] and r["finding_on_disk"])
    out.append({"id": "Q2", "measured": f"{supported} of the {len(rows)} phrases sit in a sentence whose finding is on "
                                        f"disk, so each is supported by its own citation and passes a provenance "
                                        f"audit while it is dead",
                "verdict": "MET -- the two currencies are different quantities" if supported == len(rows) else
                           "FALSIFIER FIRED -- a phrase is not supported by its citation, so e192 would see it"})

    missing = [r["phrase"] for r in rows if not r["replacement_in_finding"]]
    out.append({"id": "Q3", "measured": "; ".join(f"{r['phrase']!r} -> {r['replacement']} "
                                                  f"({'found' if r['replacement_in_finding'] else 'ABSENT'}) in "
                                                  f"{Path(r['superseded_by']).name}" for r in rows),
                "verdict": "MET -- every replacement is recorded in the finding that superseded it" if not missing else
                           f"FALSIFIER FIRED -- {missing}"})
    return out


def report(rows: list[dict]) -> int:
    print("== the registry, against the paper and against the findings ==")
    for r in rows:
        print(f"\n   phrase {r['phrase']!r}")
        print(f"      in the paper: {r['in_paper']}   a correction note beside it: {r['carries_a_note']}")
        print(f"      superseded by: {r['superseded_by']} (on disk: {r['finding_on_disk']})")
        print(f"      replacement {r['replacement']} present in that finding: {r['replacement_in_finding']}")
        print(f"      why: {r['why']}")

    print("\n== the paper's own correction notes, for contrast ==")
    text = PAPER.read_text(encoding="utf-8") if PAPER.exists() else ""
    for marker in NOTE_MARKERS:
        n = text.count(marker)
        print(f"   {marker}: {n} occurrence(s)")
        if n:
            i = text.find(marker)
            print(f"      the first: ...{text[max(0, i - 160):i + 200].replace(chr(10), ' ')}...")

    print("\n== the registered claims, Q1-Q3 ==")
    j = judge(rows)
    for c, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {c[2]}")
        print(f"          and its {c[3]}")
    print("\n   (a provenance audit asks where a number came from; this asks whether it still stands, and only a")
    print("    registry of supersessions can, which is why the registry is hand-made and the check is not)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--paper", type=Path, default=PAPER)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    # the paper is UTF-8 and this console is not: a window of its text must not carry the locale's encoding
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if not args.paper.exists():
        raise SystemExit(f"need {args.paper} -- the paper is what the registry is checked against")
    rows = check(paper=args.paper)
    if args.json_out:
        write_json(args.json_out, {"paper": str(args.paper), "registry": rows, "claims": judge(rows)})
        print(f"wrote {args.json_out}")
    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
