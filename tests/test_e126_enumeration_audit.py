"""`e126`'s checker must catch the defect it exists for, and must NOT fire on the four ways it almost didn't.

A count checker's only value is precision: it reports a handful of things and a human believes them. This
project's §7 heading said **"Five measurement traps"** over **four** bullets for two days, and no audit looked;
`e126` closes that gap, but only if it (a) still fires on that exact case and (b) stays silent on the four
near-misses that three earlier designs of it fired on. **Both directions are tested, because a checker that
never fires passes every silence test and a checker that always fires passes every catch test.**

Each case below is a documented failure of a previous design, named in the test so that a future edit that
reintroduces one fails here rather than in the corpus.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from experiments.e126_enumeration_audit import audit


def write(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "doc.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_it_catches_the_defect_it_exists_for(tmp_path):
    """The real §7 case: a count in a bold heading over a shorter list. This is the positive control."""
    res = audit(write(tmp_path, "**Five measurement traps, every one of which the project fell into.**\n"
                                 "- first\n- second\n- third\n- fourth\n"))
    assert res["claims_found"] == 1
    assert res["matched"] == 0
    m = res["mismatches"][0]
    assert (m["claimed"], m["actual"]) == (5, 4)


def test_a_four_item_numbered_list_reads_as_four_not_three(tmp_path):
    """Design 2's failure: two blank lines between items ended the block, so four findings read as three.

    The abstract of the paper is written this way, and the "mismatch" was the checker's and not the document's —
    the one error this script cannot afford.
    """
    res = audit(write(tmp_path, "Four findings, one of them unexpected in direction.\n\n"
                                 "1. first item\n   its wrapped tail\n\n"
                                 "2. second item\n   its wrapped tail\n\n"
                                 "3. third item\n\n"
                                 "4. fourth item\n"))
    assert res["claims_found"] == 1
    assert res["mismatches"] == []


def test_an_unindented_wrapped_tail_is_a_lazy_continuation(tmp_path):
    """Markdown's lazy-continuation rule, which the paper's item 3 relies on.

    Its tail lost the three-space indent that items 1 and 2 have, so a parser that requires indentation reads a
    four-item list as three items and reports a defect that does not exist.
    """
    res = audit(write(tmp_path, "Four findings.\n\n"
                                 "1. first\n   wrapped\n"
                                 "2. second\n   wrapped\n"
                                 "3. third\n"
                                 "its tail at column zero, which Markdown still treats as item 3\n"
                                 "4. fourth\n"))
    assert res["mismatches"] == [], res["mismatches"]


def test_a_claim_does_not_cross_a_section_heading(tmp_path):
    """Design 4's failure: "Two things do change." above a paragraph was read as the next section's claim."""
    res = audit(write(tmp_path, "Two things do change.\n\n"
                                 "A paragraph that is not a list, discussing the two things.\n\n"
                                 "## 6. Limits\n\n"
                                 "- first limit\n- second limit\n- third limit\n- fourth limit\n"))
    assert res["claims_found"] == 0, res["mismatches"]


def test_a_quantity_noun_is_not_a_list_noun(tmp_path):
    """Design 1's failure: "17 cores", "34 tests", "four points" name a thing counted, not a list's items.

    This is the case where generality was traded for precision, and the trade is only real if the checker stays
    silent here.
    """
    res = audit(write(tmp_path, "The sweep used four points.\n\n- first\n- second\n- third\n"))
    assert res["claims_found"] == 0


def test_a_mid_list_numbered_fragment_is_skipped_rather_than_misreported(tmp_path):
    """A block starting at 3 is a fragment; its length says nothing about the whole list, so no claim is read."""
    res = audit(write(tmp_path, "Three reasons.\n\n3. third\n4. fourth\n5. fifth\n"))
    assert res["claims_found"] == 0


def test_a_numbering_hole_is_reported(tmp_path):
    """The other half of numbered-list checking: a gap in `1. 2. 4.` is the document's own defect."""
    res = audit(write(tmp_path, "Three properties.\n\n1. first\n2. second\n4. fourth\n"))
    assert res["numbering_defects"], "a missing 3 must be reported"
    assert res["matched"] == 0


def test_a_ratio_is_counted_but_not_checked_as_a_length(tmp_path):
    """`seven of the eight rungs` is a claim, but not about a list's length — reported, never silently passed."""
    res = audit(write(tmp_path, "Seven of the eight rungs resolve, as eight values show.\n\n"
                                 "- first\n- second\n- third\n- fourth\n- fifth\n- sixth\n- seventh\n"))
    assert res["ratio_phrases_not_checked"] >= 1
    assert res["mismatches"] == []


def test_the_corpus_itself_is_clean_after_the_repairs():
    """And the live corpus: the paper, the plan and every finding pass, at the precision this script has."""
    paths = ([Path("docs/paper/clfly-v1.md"), Path("docs/research_plan.md")]
             + sorted(Path("docs/findings").glob("*.md")))
    total_mismatch = total_defects = found = 0
    for path in paths:
        if not path.is_file():
            continue
        res = audit(path)
        found += res["claims_found"]
        total_mismatch += len(res["mismatches"])
        total_defects += len(res["numbering_defects"])
    assert (total_mismatch, total_defects) == (0, 0)
    # the denominator: a checker that finds nothing is not a checker, so the corpus must exercise it
    assert found >= 5, f"only {found} count claims found -- the patterns may have stopped matching"
