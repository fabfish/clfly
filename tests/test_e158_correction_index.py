"""`e158`'s index is two string operations, and both have a failure mode this project has already paid for.

The first is **attribution**: a `§N` inside a finding usually means *that finding's* section N, so a rule that
attributes every one of them to the paper invents corrections that do not exist — the first version of this
scanner attributed nine, six of them wrong. The second is **the marker list**: a correction written in a convention
not on the list is invisible, so the list is asserted here as a set of the conventions the corpus actually uses.
"""

from __future__ import annotations

from pathlib import Path

from experiments import e158_correction_index as e158


def test_a_section_is_attributed_to_the_paper_only_when_the_sentence_says_paper(tmp_path):
    (tmp_path / "a.md").write_text(
        "Something was CORRECTED in the paper's §4.7 sentence, which now reads differently.\n\n"
        "In my own §6 above I described what was wrong with the earlier reading of that material.\n",
        encoding="utf-8")
    rows = e158.scan(tmp_path)
    assert len(rows) == 2
    by_sentence = {r["sentence"][:12]: r for r in rows}
    first = next(r for r in rows if "paper" in r["sentence"])
    second = next(r for r in rows if "paper" not in r["sentence"])
    assert first["sections"] == ["4.7"] and first["self_sections"] == []
    assert second["sections"] == [] and second["self_sections"] == ["6"]
    assert by_sentence and len(by_sentence) == 2


def test_a_marker_in_a_short_line_is_not_a_correction(tmp_path):
    (tmp_path / "b.md").write_text("## CORRECTED\n\nNothing here.\n", encoding="utf-8")
    assert e158.scan(tmp_path) == []


def test_the_marker_list_is_the_conventions_the_corpus_uses_and_is_not_empty():
    assert len(e158.MARKERS) >= 8
    assert "CORRECTED" in e158.MARKERS and "corrected in place" in e158.MARKERS
    assert "was wrong" in e158.MARKERS


def test_the_real_corpus_scans_and_the_paper_carries_its_own_markers():
    rows = e158.scan()
    assert len(rows) > 20, "the corpus should carry more than twenty marked corrections"
    assert all(r["marker"] and r["finding"] and r["sentence"] for r in rows)
    # the paper's own markers, under the SAME conventions: the other half of the index, and it must not be empty.
    # The looser "any occurrence of the word" count is much larger -- 24 against 8 -- and the difference is prose.
    paper = Path("docs/paper/clfly-v1.md").read_text(encoding="utf-8")
    assert sum(paper.count(m) for m in e158.MARKERS) >= 3
