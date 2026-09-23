"""`e127` must not repeat either of the two mistakes the project has already documented for this exact check.

Rule 22 records that the programme-table check was run **by hand** three times and that one of those passes
produced *"a flag like that costs a reader more than the check saved"* — a row reported as citing a missing
artifact when the artifact was present, because the word "launched" merely appeared in later **prose**. The first
version of this script reproduced that failure exactly (9 of 9 flags were prose), and it made a second one the
project had not recorded: it split table rows on **every** `|`, so a correctly-escaped `\\|` read as a cell
separator and a well-formed row was reported as malformed.

Both directions are tested for both mistakes, because a checker that never fires passes every silence test.
"""

from __future__ import annotations

from pathlib import Path

from experiments.e127_programme_table_audit import audit

HEAD = "## Experimental programme\n\n| Script | Programme | Why | Status |\n|---|---|---|---|\n"
TAIL = "\n## Method\n"


def doc(tmp_path: Path, *rows: str) -> Path:
    p = tmp_path / "plan.md"
    p.write_text(HEAD + "\n".join(rows) + TAIL, encoding="utf-8")
    return p


def row(what: str, why: str, status: str) -> str:
    return f"| {what} | C2b | {why} | {status} |"


def test_an_escaped_pipe_is_not_a_cell_separator(tmp_path):
    """The false positive this script's first version produced: `\\|` is how a literal pipe is written."""
    res = audit(doc(tmp_path, row("`e9_x.py`", "largest \\|Δ\\| = 0.58", "done — fine")))
    assert res["unparseable"] == []
    assert res["rows"] == 1
    assert res["contradictions"] == []


def test_a_raw_pipe_in_a_cell_is_flagged_with_its_position(tmp_path):
    """The real defect, and it is not cosmetic: in a GFM table a raw `|` splits the row in two."""
    res = audit(doc(tmp_path, row("`e9_x.py`", "it correlates with `|Δf|` at r = 0.1", "done — fine")))
    assert len(res["unparseable"]) == 1
    u = res["unparseable"][0]
    assert u["n_cells"] > 4 and u["n_unescaped_pipes"] > 5
    # the context is ASCII-sanitised for the GBK console, and it must CENTRE on the offending pipe rather than on
    # the row's own trailing border -- centring on the fifth pipe was the first version's second bug
    assert "correlates with" in u["context"], u["context"]
    assert u["at_offset"] > 0


def test_a_status_cell_that_opens_open_and_reports_done_is_flagged(tmp_path):
    """The `e85`-follow-up defect: an update appended to the body while the header stayed."""
    res = audit(doc(tmp_path, row("`e9_x.py`", "reason", "**launched, prediction before the run.** done — the prediction holds")) )
    assert len(res["contradictions"]) == 1
    assert "launched" in res["contradictions"][0]["opens_with"]


def test_a_done_row_mentioning_launched_in_later_prose_is_not_flagged(tmp_path):
    """The false positive that made the original pass worse than useless -- 9 of 9 flags were this."""
    res = audit(doc(tmp_path, row("`e9_x.py`", "reason",
                                  "done — the count moved, and `e48` launched to close it")))
    assert res["contradictions"] == []
    assert res["open_words_after_done_not_flagged"] == 1, "it must still be counted, not silently ignored"


def test_a_named_artifact_that_does_not_exist_is_flagged(tmp_path):
    res = audit(doc(tmp_path, row("`e9_x.py`", "runs/definitely_not_here_xyz.json has it", "done — fine")))
    assert len(res["missing_artifacts"]) == 1
    assert res["missing_artifacts"][0]["artifact"] == "runs/definitely_not_here_xyz.json"


def test_a_duplicated_first_cell_is_flagged(tmp_path):
    res = audit(doc(tmp_path, row("`e9_x.py`", "first", "done — a"),
                    row("`e9_x.py`", "second, contradicting the first", "done — b")))
    assert len(res["duplicate_rows"]) == 1
    assert res["duplicate_rows"][0]["also_at"] < res["duplicate_rows"][0]["line"]


def test_the_live_plan_passes_at_this_check_s_precision():
    """With the denominator, so that a zero is not mistaken for coverage."""
    res = audit(Path("docs/research_plan.md"))
    assert res["rows"] > 50, "the programme table must be found"
    assert res["classifiable_status_cells"] > 50, "most status cells must carry an indicator"
    assert res["missing_artifacts"] == []
    assert res["contradictions"] == []
    assert res["duplicate_rows"] == []
    assert res["unparseable"] == []
