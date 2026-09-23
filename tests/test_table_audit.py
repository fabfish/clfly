"""The table audit's two checks, on synthetic tables and a synthetic corpus.

The cases that make its answers mean something:

  * a contrast column must be verified **against the comparator its header names**, and a row whose contrast
    was computed against some *other* baseline must be reported as failing while the rows around it close --
    that is the paper's §4.2 as it stood, and reporting it is the whole point of check 1;
  * the tolerance must cover the rounding of *both* sides of a subtraction, or a printed three-decimal
    contrast at the half-unit boundary reads as a failure and the check cries wolf on a correct table;
  * `locate` must match at the precision printed and not one digit looser, because a loose match would have
    found `0.010` inside an artifact's `0.0104` and hidden the failure this script exists for.
"""

from __future__ import annotations

import pytest

from experiments.e105_table_audit import (
    ascii_token,
    audit_table,
    check_closure,
    closure_counts,
    corpus_index,
    locate,
    number_of,
    numbers_of,
    parse_tables,
    tolerance,
)


def table(header, *rows):
    """A table in the shape `parse_tables` returns: line numbers, then cells."""
    body = [(10 + i, list(r)) for i, r in enumerate(rows)]
    return {"start": 9, "end": 10 + len(rows), "header": list(header), "rows": [(9, list(header))] + body}


def artifact(name, methods):
    """A minimal run artifact: `methods` maps an arm name to its scalar fields."""
    return {"name": name, "config": {}, "payload": {"methods": methods}, "mtime": 0.0}


# --- the closure check ------------------------------------------------------------------------------

def test_a_table_whose_contrasts_close_reports_no_failure():
    t = table(["method", "mean forgetting", "vs naive"],
              ["naive", "+0.0729", "—"],
              ["ewc", "+0.0208", "-0.0521"])
    got = check_closure(t)
    verdicts = [r["verdict"] for r in got["findings"][0]["rows"]]
    assert verdicts == ["closes"]


def test_a_contrast_computed_against_a_foreign_baseline_fails_while_its_neighbours_close():
    """The paper's §4.2: two rows subtracted +0.0729 and two subtracted the table's own +0.066."""
    t = table(["method", "mean forgetting", "vs naive"],
              ["naive", "+0.066", "—"],
              ["ewc", "+0.010", "-0.056"],                     # closes: 0.010 - 0.066
              ["block — biological", "+0.0604", "-0.013"])     # fails: 0.0604 - 0.066 = -0.0056
    rows = {r["line"]: r for r in check_closure(t)["findings"][0]["rows"]}
    assert rows[11]["verdict"] == "closes"
    assert rows[12]["verdict"] == "fails"
    assert abs(rows[12]["fails"][0]["expected"] - (-0.0056)) < 1e-9
    assert abs(rows[12]["fails"][0]["difference"] - (-0.0074)) < 1e-9


def test_the_tolerance_covers_both_rounded_sides_of_the_subtraction():
    """-0.0125 printed as -0.013 must close: half a unit in each of the three printed places."""
    t = table(["method", "mean forgetting", "vs naive"],
              ["naive", "+0.0729", "—"],
              ["block", "+0.0604", "-0.013"])
    assert check_closure(t)["findings"][0]["rows"][0]["verdict"] == "closes"
    assert tolerance("-0.013", "+0.0604", "+0.0729") >= 0.0005
    assert tolerance("-0.013", "+0.0604", "+0.0729") < 0.001


def test_an_inline_contrast_must_equal_the_difference_of_two_of_its_own_row_cells():
    """§4.4's shape: `−0.0125 ± 0.0039 (−0.0854, 6.6σ)` -- no `vs` column, so check_closure cannot see it.

    The check available is internal to the row, and it is the one that was violated in §4.2 by hand: a contrast
    must be obtainable from two cells of the row that prints it.
    """
    from experiments.e105_table_audit import check_inline_contrasts

    t = table(["setting", "`naive`", "EWC, diagonal", "`replay`"],
              ["naive", "+0.0729", "+0.0208", "+0.0500"],
              ["hardened", "+0.0729", "+0.0208", "−0.0125 ± 0.0039 (−0.0854, 6.6σ)"])
    got = check_inline_contrasts(t)
    assert len(got) == 1
    assert got[0]["token"] == "-0.0854"
    assert got[0]["verdict"] == "closes"
    assert got[0]["closes"][0]["expected"] == pytest.approx(-0.0854, abs=1e-6)


def test_both_inline_typographies_are_recognised_and_coverage_is_counted():
    """Coverage is presentation-dependent, so the check must recognise both and must print how many it saw.

    The arrow form was added after an edit to §4.4's table took this check's coverage from four contrasts to
    zero without failing anything -- the reason the count is printed rather than implied.
    """
    from experiments.e105_table_audit import check_inline_contrasts

    t = table(["setting", "`naive`", "EWC, diagonal", "`replay`"],
              ["naive", "+0.1062", "+0.1062", "—"],
              ["task-IL", "+0.1062", "**+0.1062 ± 0.0372 → +0.0000 (0.00σ, tie)**", "—"])
    got = check_inline_contrasts(t)
    assert [r["token"] for r in got] == ["+0.0000"]
    assert got[0]["verdict"] == "closes"


def test_an_inline_contrast_no_pair_of_its_cells_gives_is_reported():
    from experiments.e105_table_audit import check_inline_contrasts

    t = table(["setting", "`naive`", "`replay`"],
              ["naive", "+0.0729", "+0.0500"],
              ["hardened", "+0.0729", "+0.0500 (−0.0854, 6.6σ)"])   # 0.0500 - 0.0729 = -0.0229, not -0.0854
    got = check_inline_contrasts(t)
    assert got[0]["verdict"] == "no pair of its own cells gives it"
    assert got[0]["closes"] == []


def test_a_contrast_column_naming_a_comparator_the_table_does_not_have_is_reported():
    t = table(["rung", "vs the diagonal"], ["side", "+0.021"])
    got = check_closure(t)["findings"][0]
    assert got["status"] == "no row matches this comparator"
    assert got["kind"] == "missing comparator row"


def test_a_delta_column_is_not_checkable_rather_than_a_failure():
    """`delta vs X` cells ARE the differences: the reference's value is not in the table to subtract.

    §4.4's basis table is the case: four deltas against the diagonal, and the diagonal's own +0.01762 is in the
    prose below. Counting it as a failure inflated check (a)'s headline by one, which is the number a reader
    takes away -- so the two shapes are reported apart, and this one keeps its reason.
    """
    t = table(["basis", "delta vs the diagonal", "signs"],
              ["`rank4`", "+0.00472", "18/18 +"],
              ["**`eigbasis`**", "-0.00491", "18/18 -"])
    got = check_closure(t)["findings"][0]
    assert got["kind"] == "external reference"
    assert "not checkable" in got["status"]
    assert "rows" not in got


def test_the_two_shapes_are_counted_apart():
    """A defect and an uncheckable column must not land in one number: the first is the check's headline."""
    defect = check_closure(table(["rung", "vs the diagonal"], ["side", "+0.021"]))
    uncheckable = check_closure(table(["basis", "delta vs the diagonal"], ["rank4", "+0.00472"]))
    closing = check_closure(table(["method", "mean forgetting", "vs naive"],
                                  ["naive", "+0.0729", "—"],
                                  ["ewc", "+0.0208", "-0.0521"]))
    counts = closure_counts([({}, defect), ({}, uncheckable), ({}, closing)])
    assert counts == {"failures": 1, "not_checkable": 1, "rows_closed": 1, "contrast_columns": 3}


def test_a_failing_row_still_counts_as_a_failure_whatever_the_header_says():
    t = table(["method", "mean forgetting", "delta vs naive"],
              ["naive", "+0.0729", "—"],
              ["ewc", "+0.0208", "-0.0100"])          # -0.0521 is what the cells give
    counts = closure_counts([({}, check_closure(t))])
    assert counts["failures"] == 1 and counts["not_checkable"] == 0


def test_a_table_without_a_contrast_column_is_not_checked():
    assert check_closure(table(["rung", "value"], ["side", "+0.021"])) is None


# --- number handling --------------------------------------------------------------------------------

def test_a_cell_with_several_numbers_has_no_single_value():
    assert number_of("−0.0042 ± 0.0091") is None
    assert len(numbers_of("−0.0042 ± 0.0091")) == 2
    assert number_of("+0.0729") == 0.0729


def test_the_unicode_minus_is_normalised_because_the_console_cannot_print_it():
    assert ascii_token("−0.0354") == "-0.0354"
    assert number_of("−0.0354") == -0.0354


def test_parse_tables_skips_the_separator_row_and_keeps_the_header():
    text = "# t\n\n| a | b |\n|---|---|\n| 1.0 | 2.0 |\n\nprose\n"
    tables = parse_tables(text)
    assert len(tables) == 1
    assert tables[0]["header"] == ["a", "b"]
    assert tables[0]["rows"] == [(3, ["a", "b"]), (5, ["1.0", "2.0"])]


# --- the location check -----------------------------------------------------------------------------

def test_locate_matches_at_the_printed_precision_and_not_one_digit_looser():
    """The real case: the paper printed +0.010 where every artifact holds at least +0.0208.

    A tolerance one decimal place looser would have located 0.010 inside 0.0208, which is the failure this
    script exists for. (0.0104 *does* round to 0.010, so that is not the example: 0.010417 against the token
    0.010 matches, correctly.)
    """
    index = corpus_index([artifact("r.json", {"ewc-block": {"mean_forgetting": 0.020833}})])
    assert locate(index, "0.010") == []
    assert locate(index, "0.066") == []
    assert locate(index, "0.0208") == [["mean_forgetting", "r.json:ewc-block"]]
    assert locate(index, "0.021") == [["mean_forgetting", "r.json:ewc-block"]]


def test_locate_reports_where_a_number_came_from():
    index = corpus_index([artifact("e8.json", {"naive": {"final_accuracy": 0.913889,
                                                         "mean_forgetting": 0.072917}})])
    assert locate(index, "0.9139") == [["final_accuracy", "e8.json:naive"]]
    assert locate(index, "0.0729") == [["mean_forgetting", "e8.json:naive"]]


def test_audit_table_counts_located_and_unlocated_per_row():
    index = corpus_index([artifact("e8.json", {"naive": {"mean_forgetting": 0.072917}})])
    t = table(["method", "mean forgetting", "vs naive"],
              ["naive", "+0.0729", "—"],
              ["ewc", "+0.0271", "-0.0458"])
    got = audit_table(t, index)
    assert got["verdict"] == "mixed"
    assert got["matched"] == 1                       # the naive row's own +0.0729
    assert got["unmatched"] == 2                     # the diagonal's cell and its derived contrast
    assert got["rows"][1]["unmatched_tokens"] == ["+0.0271", "-0.0458"]


# --- two shapes that made the corpus check cry wolf --------------------------------------------------

def test_a_blocked_table_is_checked_against_the_comparator_in_its_own_block():
    """A table of several settings has one comparator row per block, and pairing them all with the first
    made every row after the first block look like it failed. §4.4's own table spans three settings."""
    t = table(["setting", "method", "mean forgetting", "vs naive"],
              ["task-IL", "naive", "+0.101", "—"],
              ["", "ewc", "+0.128", "+0.027"],
              ["class-IL", "naive", "+0.059", "—"],
              ["", "ewc", "+0.063", "+0.004"])
    verdicts = [r["verdict"] for r in check_closure(t)["findings"][0]["rows"]]
    assert verdicts == ["closes", "closes"]


def test_a_correlation_column_is_skipped_rather_than_read_as_a_difference():
    """"Spearman vs X" is a correlation, not a subtraction, and its comparator row holds 1.000.

    Reading it as a difference reported a correlation matrix as failing -- a false positive that appeared in a
    real findings document and would have been the only closure failure in the corpus.
    """
    t = table(["candidate", "vs measured sd", "vs concentration"],
              ["absolute", "+0.412", "+0.160"],
              ["concentration", "+0.832", "+1.000"])
    got = {f["comparator"]: f for f in check_closure(t)["findings"]}
    assert got["concentration"]["status"].startswith("skipped")
    assert "correlation diagonal" in got["concentration"]["status"]


def test_the_scan_reports_zero_when_there_is_nothing_to_report(tmp_path):
    """The corpus check's own denominator: `scan_findings` must count documents, not just findings."""
    from experiments.e105_table_audit import scan_findings

    (tmp_path / "a.md").write_text("| method | mean forgetting | vs naive |\n|---|---|---|\n"
                                   "| naive | +0.0729 | — |\n| ewc | +0.0208 | −0.0521 |\n",
                                   encoding="utf-8")
    got = scan_findings(tmp_path, [], 0.25)
    assert got["n_documents"] == 1
    assert got["with_closure_failures"] == []
