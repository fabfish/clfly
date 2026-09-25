"""`e226` asserts on the plan's Claims section the relation `e192` asserts on the paper, and its three rule
differences are each a measured class rather than a style choice.

- a **number token**, not a substring: the looser arm carries 592 of the section's 593 distinct numbers, and the one
  it adds is carried **vacuously** -- `556` occurs inside longer numbers such as `0.5563`;
- integers from **three digits**: one- and two-digit integers here are ladder indices and section numbers;
- a **scientific notation's exponent counts** in the quoted precision, without which `7.6e-4` is unsupportable by
  the `0.00076` a finding carries -- the difference between one and two unsupported numbers on the live section.

The `DECLARED` table is the one place a number may live without a finding, and each entry is a measurement to be
re-run: its column, rule and prefix are re-counted against the annotation by `--annotation-counts`.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from experiments import e226_plan_claims_numbers as e226

PLAN_HEAD = "## Claims\n\nA claim: the population is {body}.\n\n## Experimental programme\n\nthe table follows\n"


def build(tmp_path: Path, body: str, findings: dict[str, str] | None = None) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_HEAD.format(body=body), encoding="utf-8")
    d = tmp_path / "findings"
    d.mkdir(parents=True, exist_ok=True)
    for name, text in (findings or {}).items():
        (d / f"{name}.md").write_text(text, encoding="utf-8")
    return plan, d


def test_a_number_the_corpus_carries_is_supported(tmp_path):
    plan, d = build(tmp_path, "`{cell_class=LH}` (556 neurons)", {"a": "the population is 556 neurons"})
    res = e226.audit(plan, d)
    assert res["distinct_numbers"] == 1 and res["unsupported"] == []


def test_a_declared_annotation_count_is_not_a_failure_but_an_undeclared_one_is(tmp_path):
    """Both members of the live class are annotation counts; a count no measurement carries is the exit code."""
    plan, d = build(tmp_path, "556 neurons, and 4321 elsewhere", {})
    res = e226.audit(plan, d)
    assert [r["number"] for r in res["declared"]] == ["556"]
    assert [r["number"] for r in res["unsupported"]] == ["4321"]
    assert e226.report(res) == 1


def test_the_precision_rule_carries_a_rounded_quote_and_only_a_rounded_one(tmp_path):
    plan, d = build(tmp_path, "-0.0854 in the note", {"a": "measured -0.08542"})
    assert e226.audit(plan, d)["unsupported"] == []
    plan2, d2 = build(tmp_path / "b", "-0.0855 in the note", {"a": "measured -0.08542"})
    assert e226.audit(plan2, d2)["unsupported"] != []


def test_a_scientific_notation_counts_its_exponent_in_the_quoted_precision(tmp_path):
    """`7.6e-4` is stated to the fifth decimal; reading the decimals off the string's first `.` -- e192's rule --
    makes it unsupportable by the `0.00076` the finding carries, and that is this section's third rule change."""
    plan, d = build(tmp_path, "`cost = 28 x G + 7.6e-4 x sum_g s_g^2`", {"a": "the coefficient is 0.00076"})
    assert e226.quoted_precision("7.6e-4") == 5
    assert e226.quoted_precision("-0.0854") == 4
    assert e226.audit(plan, d)["unsupported"] == []


def test_the_looser_arm_carries_a_digit_run_inside_a_longer_number(tmp_path):
    """The measured reason the match is a token: `4321` is `in` `0.43213`, so e192's first arm supports a count that
    nothing computed -- on the live section that arm's one extra member is `556` inside longer numbers."""
    plan, d = build(tmp_path, "4321 neurons", {"a": "the excess is 0.43213 at this size"})
    assert [r["number"] for r in e226.audit(plan, d, substring_arm=False)["unsupported"]] == ["4321"]
    res = e226.audit(plan, d, substring_arm=True)
    assert res["unsupported"] == [] and res["supported_under_the_substring_arm"] == 1


def test_the_floor_is_three_digits_so_ladder_indices_are_not_claims(tmp_path):
    plan, d = build(tmp_path, "rung 4 of 42, then 421 cells", {})
    assert e226.audit(plan, d)["distinct_numbers"] == 1


def test_the_section_stops_at_the_programme_table(tmp_path):
    """The region is the Claims section and the benchmark block after it, and nothing below the programme heading."""
    plan, d = build(tmp_path, "556 neurons", {})
    plan.write_text(plan.read_text(encoding="utf-8") + "| 4321 | a row |\n", encoding="utf-8")
    res = e226.audit(plan, d)
    assert res["unsupported"] == [] and [r["number"] for r in res["declared"]] == ["556"]


def test_the_live_plan_has_no_number_its_corpus_cannot_support():
    """The gate, with the denominator: 898 tokens and 593 distinct numbers are what make the zero a statement."""
    res = e226.audit()
    assert res["number_tokens"] >= 850 and res["distinct_numbers"] >= 580
    assert res["unsupported"] == [], res["unsupported"]
    assert [r["number"] for r in res["declared"]] == ["556", "6114"], res["declared"]
    assert res["declared_without_measurement"] == [], "a declaration nothing reaches is dead text"
    assert res["supported_under_the_substring_arm"] >= res["distinct_numbers"] - 1


def test_the_declarations_are_a_state_not_an_exemption_and_the_witness_is_the_finding_that_measured_them():
    """A declaration is printed whether or not the corpus carries its number. This audit's own finding is the
    witness for both counts; with it excluded from a copy of the corpus, both entries lose their witness and `556`
    keeps a **vacuous** one -- the measured reason the match is a token rather than a digit run."""
    res = e226.audit()
    assert all(r["carried_by_the_findings_corpus"] for r in res["declared"]), res["declared"]

    tmp = Path(tempfile.mkdtemp())
    for p in Path("docs/findings").glob("*.md"):
        if p.name != "2026-09-26-the-plans-claims-section-has-a-number-check.md":
            (tmp / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    without = e226.audit(findings_dir=tmp)
    assert [r["number"] for r in without["declared"]] == ["556", "6114"], without["declared"]
    assert not any(r["carried_by_the_findings_corpus"] for r in without["declared"])
    assert [r["number"] for r in without["loose_arm_only"]] == ["556"], without["loose_arm_only"]
    shutil.rmtree(tmp)


def test_the_declarations_rerun_on_the_annotation():
    """A declaration is a measurement, not an exemption: each entry's column, rule and prefix is re-counted."""
    res = e226.audit()
    counts = e226.annotation_counts(res["declared"])
    assert [c["count"] for c in counts] == [int(r["number"]) for r in res["declared"]], counts
    assert all(c["matches_claim"] for c in counts), counts
