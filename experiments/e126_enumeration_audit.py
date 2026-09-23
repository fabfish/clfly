"""E126 -- does a document list as many items as it says it does?

`docs/paper/clfly-v1.md`'s §7 carried a heading reading **"Five measurement traps"** over **four** bullets from
commit `1743573` (2026-09-22) until 2026-09-24 — born in the very commit whose message is about stale aggregate
statements. §4.3 did the mirror image: one sentence said *"all eight ladder rungs now have a measured draw sd of
their own"* and, fourteen lines later, another said the column *"is a floor, since three of its eight rungs have
no measurement of their own"*. **Both were found by counting, and neither was findable by any audit this project
had**: `e97` checks that a cited artifact exists, `e105` checks that a table's arithmetic closes, `e103` checks
that an arm executes twice — and all three read the numbers. **A count is a claim about the document itself, and
nothing here was reading it.**

    python -m experiments.e126_enumeration_audit                  # every document under docs/
    python -m experiments.e126_enumeration_audit --paths docs/paper/clfly-v1.md

## Three designs, two of them failures, and the pattern that finally works

This script exists to catch one thing, so a false alarm costs it its reason to exist: **a checker that reports
everything gets ignored, and an ignored checker is worse than none because it looks like coverage.** Each
version's failure is the next one's specification.

1. *Any `<number> <plural noun>` adjacent to a list.* Fires on "17 cores", "34 tests", "75 minutes", "12 seeds"
   — counts of something other than the list's length — and reported about forty mismatches of which **not one
   was real**. Repair: a curated lexicon of nouns that *name list items*.
2. *Then a numbered list was counted like a bulleted one*, which read the abstract's four numbered findings as
   **three**, because two blank lines separate them and a double blank line ended the block. **The bug was in
   the checker and the mismatch was manufactured.** Repair: for `1. 2. 3.` the numbering *is* the document's own
   statement of length, and a numbered block that does **not** start at 1 is a mid-list fragment — it cannot be
   compared to a claim about the whole list, so it is skipped rather than reported. (Two of the three remaining
   "numbering holes" were exactly that, in documents whose wrapped continuation lines are not indented.)
3. *Then the lookback window was widened to reach a heading*, which let a **later** line inside the window win:
   the §7 heading's own correction note says *"adding two bullets"*, so the nearest match claimed 2 over a
   six-item list. Repair, and it is the pattern that actually describes the defect: **a count is read as a claim
   about a list only when it begins a line or begins a bold run** — `Five measurement traps`, `Four findings` —
   which is what a heading-like enumeration looks like and what incidental prose does not.

What it cannot do, stated so that a zero is read correctly: it sees only counts that **open** a line or a bold
run and are followed by a list, so a stale count buried mid-sentence is invisible to it; it reads English number
words and digits and nothing else; and a claim of the form *"seven of the eight rungs"* is a **ratio**, not a
length, so it is reported as *not checked* rather than silently passed.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
}
NUMBER_ALT = "|".join(sorted(NUMBER_WORDS, key=len, reverse=True))

# Only nouns that NAME LIST ITEMS. Quantity nouns ("points", "failures", "measurements", "candidates",
# "levels", "seeds") are deliberately absent even though they sit beside lists, because they name the thing
# counted rather than the items of the list -- and admitting them is what made design 1 useless.
LIST_NOUNS = {
    "thing", "item", "reason", "attempt", "trap", "finding", "conclusion", "retraction",
    "bullet", "observation", "lesson", "caveat", "limitation", "mistake", "defect", "revision", "paper",
}
NOUN_ALT = "|".join(sorted(LIST_NOUNS))
# The count must OPEN the line, or open a bold run that opens the line, and the noun must follow within two
# words -- "Five **measurement** traps" needs the modifier slot, and only the OPENING requirement (design 3's
# repair) keeps that from matching incidental prose.
CLAIM_RE = re.compile(
    rf"^(?:\*\*)?(?P<num>{NUMBER_ALT}|\d+)[\s*_]+(?:[\w-]+[\s*_]+){{0,2}}?(?P<noun>{NOUN_ALT})s?\b",
    re.IGNORECASE)
BULLET_RE = re.compile(r"^(?P<indent>[ \t]*)(?:(?P<dash>[-*])\s+|(?P<num>\d+)[.)]\s+)(?P<rest>\S)")


def list_blocks(lines: list[str]) -> list[dict]:
    """Every maximal list block that can carry a claim about its own length.

    A block continues while lines are list items, indented continuations, or single blank lines; two blank lines
    end it. For a numbered block the length is the largest number at the block's *minimum* indent — the
    numbering is the document's own length claim — and **a numbered block not starting at 1 is skipped**, since
    it is a mid-list fragment whose length says nothing about the whole list.
    """
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        if not BULLET_RE.match(lines[i]):
            i += 1
            continue
        start, blanks = i, 0
        items: list[tuple[int, int | None]] = []
        while i < n:
            line = lines[i]
            m = BULLET_RE.match(line)
            if m:
                items.append((len(m.group("indent")), int(m.group("num")) if m.group("num") else None))
                blanks = 0
            elif not line.strip():
                blanks += 1
                if blanks > 1:
                    break
            elif line[:1] in (" ", "\t") or blanks == 0:
                # Markdown's **lazy continuation**: a non-blank line immediately after an item continues that
                # item whether or not it is indented. Without this rule the paper's abstract reads as three
                # findings rather than four, because item 3's wrapped tail lost its three-space indent -- and
                # that "mismatch" was the checker's, not the document's.
                blanks = 0
            else:
                break
            i += 1
        min_indent = min((ind for ind, _ in items), default=0)
        top = [num for ind, num in items if ind == min_indent]
        numbered = len(top) == len(items) and all(num is not None for num in top)
        if numbered and top:
            if min(top) != 1:                      # a fragment, not a list -- skip rather than misreport
                i = max(i, start + 1)
                continue
            length, gap = max(top), sorted(top) != list(range(1, max(top) + 1))
        else:
            length, gap = sum(1 for ind, _ in items if ind == min_indent), False
        if length >= 2:
            blocks.append({"start": start, "end": i - blanks, "length": length,
                           "numbered": bool(numbered), "gap": gap})
        i = max(i, start + 1)
    return blocks


def claimed_count(lines: list[str], start: int, lookback: int = 6) -> tuple[int | None, str]:
    """The count that opens a line above the block, and the phrase it came from.

    **The search stops at a heading**, which is the fourth design's repair: a claim cannot describe a list in
    another section, and without this rule a sentence like *"Two things do change."* sitting above a paragraph
    was read as the claim for the next section's `Limits` bullets — a false alarm of exactly the kind that makes
    a checker worthless.
    """
    seen = 0
    for j in range(start - 1, -1, -1):
        text = lines[j].strip()
        if text.startswith("#"):
            break
        if not text:
            continue
        seen += 1
        if seen > lookback:
            break
        m = CLAIM_RE.match(text)
        if not m:
            continue
        word = m.group("num").lower()
        value = NUMBER_WORDS.get(word, int(word) if word.isdigit() else None)
        if value is None or value < 2:
            continue
        return value, f"{word} {m.group('noun')}"
    return None, ""


def ascii_safe(text: str) -> str:
    """The console is GBK, and a document's own typography must not crash the checker."""
    return text.encode("ascii", "replace").decode("ascii")


def audit(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    matched, mismatches, defects, found = 0, [], [], 0
    for block in list_blocks(lines):
        if block["gap"]:
            defects.append({"line": block["start"] + 1,
                            "first_item": ascii_safe(lines[block["start"]].strip()[:80])})
        claim, phrase = claimed_count(lines, block["start"])
        if claim is None:
            continue
        found += 1
        if claim == block["length"]:
            matched += 1
        else:
            mismatches.append({"line": block["start"] + 1, "claimed": claim, "phrase": phrase,
                               "actual": block["length"], "numbered": block["numbered"],
                               "first_item": ascii_safe(lines[block["start"]].strip()[:80])})
    text = "\n".join(lines)
    ratios = len(re.findall(rf"\b(?:{NUMBER_ALT})\s+of\s+(?:the\s+)?(?:{NUMBER_ALT})\b", text,
                            re.IGNORECASE))
    return {"path": str(path), "claims_found": found, "matched": matched, "mismatches": mismatches,
            "numbering_defects": defects, "ratio_phrases_not_checked": ratios}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paths", type=Path, nargs="*", default=None,
                   help="documents to check (default: the paper, the plan and every finding)")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    paths = args.paths or ([Path("docs/paper/clfly-v1.md"), Path("docs/research_plan.md")]
                           + sorted(Path("docs/findings").glob("*.md")))
    total_found = total_matched = total_defects = 0
    rows = []
    for path in paths:
        if not path.is_file():
            continue
        res = audit(path)
        rows.append(res)
        total_found += res["claims_found"]
        total_matched += res["matched"]
        total_defects += len(res["numbering_defects"])
        if res["mismatches"] or res["numbering_defects"]:
            print(f"== {res['path']} ==")
            for m in res["mismatches"]:
                kind = "numbered" if m["numbered"] else "bulleted"
                print(f"   line {m['line']:5}: says **{m['phrase']}** ({m['claimed']}) over "
                      f"{m['actual']} {kind} items -> {m['first_item']}")
            for d in res["numbering_defects"]:
                print(f"   line {d['line']:5}: NUMBERING HOLE -> {d['first_item']}")
    print(f"\ndocuments                            : {len(rows)}")
    print(f"count claims found next to a list    : {total_found}")
    print(f"  ... that matched their list length : {total_matched}")
    print(f"  ... that did NOT                   : {total_found - total_matched}")
    print(f"list numberings with a hole          : {total_defects}")
    print(f"ratio phrases ('N of M') not checked as lengths : "
          f"{sum(r['ratio_phrases_not_checked'] for r in rows)}")
    print("NOTE: a zero above is a zero *for this narrow pattern only*, not for the corpus.")
    if args.json_out:
        from clfly.bench.artifacts import write_json
        write_json(args.json_out, {"found": total_found, "matched": total_matched,
                                   "numbering_defects": total_defects, "rows": rows})
        print(f"wrote {args.json_out}")
    return 1 if (total_found > total_matched or total_defects) else 0


if __name__ == "__main__":
    raise SystemExit(main())
