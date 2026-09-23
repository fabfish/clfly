"""`e132` must catch a wrong derivation and stay silent on the four ways prose nearly made it useless.

The corpus this checker runs on yields **one** live derivation and it is correct, so the corpus cannot test
whether the checker *works* — it can only test that it is silent. **Both directions are therefore synthetic**: a
fabricated wrong claim must be flagged, and each of the three ways prose defeated an earlier version must stay
silent. That distinction is the whole reason this file exists — a checker with no failing case in its corpus is a
checker whose arithmetic has never been exercised.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from experiments.e132_derivation_audit import (audit, implied_draw_sd, paragraphs, share_sd_fall)

HEAD = "## Section\n\n"


def doc(tmp_path: Path, *paras: str) -> Path:
    p = tmp_path / "doc.md"
    p.write_text(HEAD + "\n\n".join(paras) + "\n", encoding="utf-8")
    return p


def test_a_wrong_share_to_fall_claim_is_flagged(tmp_path):
    """The `e128` defect: 85% does not predict a 2.6x fall, it predicts 2.07x."""
    res = audit(doc(tmp_path, "measured, not argued: 85% predicted a 2.6× fall and the fall was 1.47×."))
    assert len(res["checks"]) == 1
    c = res["checks"][0]
    assert not c["agrees"]
    assert c["claimed"] == pytest.approx(2.6)
    assert c["expected"] == pytest.approx(share_sd_fall(0.85), abs=1e-9)


def test_a_correct_share_to_fall_claim_is_not_flagged(tmp_path):
    res = audit(doc(tmp_path, "from the 85% a tenfold test set gives 85% predicted a 2.07× fall."))
    assert len(res["checks"]) == 1 and res["checks"][0]["agrees"]


def test_a_wrapped_draw_sd_derivation_is_found_across_two_lines(tmp_path):
    """The checker's only live subject wraps, and a per-line regex found nothing to check because of it."""
    p = tmp_path / "doc.md"
    p.write_text(HEAD + "for `side`, 15.53σ → 4.47σ at a seed sem of 0.00031 implies an assumed draw sd of\n"
                        "**1.028e-3**, which is what the interpolation gives.\n", encoding="utf-8")
    res = audit(p)
    assert len(res["checks"]) == 1, res
    c = res["checks"][0]
    assert c["family"] == "sigma reduction -> draw sd"
    assert c["agrees"], (c["claimed"], c["expected"])
    assert c["expected"] == pytest.approx(implied_draw_sd(15.53, 4.47, 0.00031), rel=1e-9)


def test_a_wrong_draw_sd_derivation_is_flagged(tmp_path):
    res = audit(doc(tmp_path, "15.53σ → 4.47σ at a seed sem of 0.00031 implies an assumed draw sd of **9.9e-4**."))
    assert len(res["checks"]) == 1 and not res["checks"][0]["agrees"]


def test_a_correction_in_the_next_blockquote_skips_the_quotation(tmp_path):
    """The convention: leave the wrong sentence standing, correct it in a blockquote immediately after."""
    res = audit(doc(tmp_path, 'he wrote "85% predicted a 2.6× fall".',
                    "> **Corrected 2026-09-24.** 2.6× needs 94.7% and the 85% gives 2.07×."))
    assert res["checks"] == []
    assert len(res["skipped_as_corrected"]) == 1


def test_a_marker_FIVE_paragraphs_later_does_not_skip_a_correct_derivation(tmp_path):
    """The false-negative that cost the checker its only real subject, now pinned as a test.

    A section can contain the word "corrected" about some *other* figure. A lookahead wide enough to reach it
    skipped a correct derivation silently -- and silence is indistinguishable from having nothing to check.
    """
    res = audit(doc(tmp_path,
                    "15.53σ → 4.47σ at a seed sem of 0.00031 implies an assumed draw sd of **1.028e-3**.",
                    "An unrelated paragraph.", "Another one.", "A third one.",
                    "### 4.1 table can now be corrected, because four of its five draw sds are known."))
    assert len(res["checks"]) == 1, "the derivation must still be checked"
    assert res["checks"][0]["agrees"]


def test_a_paragraph_that_is_itself_a_correction_note_is_skipped(tmp_path):
    res = audit(doc(tmp_path, "> **Corrected.** The sentence said 85% predicted a 2.6× fall, which was wrong."))
    assert res["checks"] == []


def test_the_formula_is_the_one_that_is_printed(tmp_path):
    """The two helpers are the claim; if either changes, every verdict changes with it.

    **And this test's own first version had the defect it guards against**: it asserted 2.074 for a share of
    0.85, which gives 2.063 — 2.074 is what the *measured* share **0.8528** gives, and the two differ in the
    second decimal. A round number in the prose and the measured value in the artifact are two numbers, and the
    formula uses one of them.
    """
    assert share_sd_fall(0.0) == pytest.approx(1.0)                    # nothing removable, no fall
    assert share_sd_fall(0.85) == pytest.approx(2.063, abs=0.001)      # the round number in the prose
    assert share_sd_fall(0.8528) == pytest.approx(2.074, abs=0.001)    # the value in the artifact
    assert share_sd_fall(1.0) == pytest.approx(10 ** 0.5, rel=1e-9)    # all removable -> the full sqrt(10)
    assert implied_draw_sd(15.53, 4.47, 0.00031) == pytest.approx(1.0314e-3, rel=1e-3)
    assert implied_draw_sd(2.0, 1.0, 0.001) == pytest.approx(0.001 * 3 ** 0.5, rel=1e-9)


def test_a_summary_table_quoting_a_claim_beside_its_verdict_is_skipped(tmp_path):
    """The fourth false-positive class, found the moment this fire summarised its own findings in a table.

    A row that quotes a claim and prints the correct value beside the word "wrong" carries no dated marker at
    all. The exclusion set is therefore empirical, and each addition is also a wider evasion route — which is
    why the script prints how many candidates it skipped.
    """
    res = audit(doc(tmp_path, "| instance | claimed | the formula gives | verdict |",
                    "|---|---|---|---|",
                    "| §4.2's `85% predicted a 2.6× fall` | 2.6 | **2.07** | **wrong** — `e128` |"))
    assert res["checks"] == [], res["checks"]
    assert len(res["skipped_as_corrected"]) == 1


def test_the_live_corpus_is_clean_and_the_checker_has_a_subject():
    """With the denominator: one live derivation, and it agrees. A zero with no denominator is not a check."""
    total_checked = total_failed = total_skipped = 0
    paths = ([Path("docs/paper/clfly-v1.md"), Path("docs/research_plan.md")]
             + sorted(Path("docs/findings").glob("*.md")))
    for path in paths:
        if not path.is_file():
            continue
        res = audit(path)
        total_checked += len(res["checks"])
        total_failed += sum(1 for c in res["checks"] if not c["agrees"])
        total_skipped += len(res["skipped_as_corrected"])
    assert total_failed == 0
    assert total_skipped >= 3, "the four corrected quotations must be recognised, not silently checked"
    assert total_checked >= 1, (
        f"only {total_checked} live derivations found -- if the pattern stopped matching, the checker has "
        f"silently lost its subject")
