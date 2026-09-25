"""`e192` checks the one relation a reader of the paper relies on, and its two matching rules are measured classes.

The precision rule was bought with a false positive: the paper quotes `-0.0854` where the finding has `-0.08542`,
and under a substring test that counts as unsupported. The middle class -- a number present in the corpus but not in
the finding the sentence cites -- is deliberately **not** a failure, because a citation localises the claim rather
than every number in the sentence.
"""

from __future__ import annotations

from pathlib import Path

from experiments import e192_paper_numbers as e192


def build(tmp_path: Path, sentence: str, findings: dict[str, str]) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    paper = tmp_path / "paper.md"
    paper.write_text(f"The result was {sentence}\n", encoding="utf-8")
    d = tmp_path / "findings"
    d.mkdir(parents=True, exist_ok=True)
    for name, body in findings.items():
        (d / f"{name}.md").write_text(body, encoding="utf-8")
    return paper, d


def test_a_number_the_cited_finding_carries_is_supported(tmp_path):
    paper, d = build(tmp_path, "**-0.0116** (`docs/findings/a.md`).", {"a": "the gap is -0.0116 here"})
    res = e192.audit(paper, d)
    assert res["in_the_cited_finding"] == 1 and res["in_no_finding"] == 0
    assert res["numbers_checked"] == 1


def test_the_unicode_minus_is_the_same_number(tmp_path):
    paper, d = build(tmp_path, "**−0.0116** (`docs/findings/a.md`).", {"a": "the gap is -0.0116 here"})
    assert e192.audit(paper, d)["in_the_cited_finding"] == 1


def test_a_rounded_quote_is_supported_by_the_number_it_rounds(tmp_path):
    """The paper's `-0.0854` against the finding's `-0.08542`: a substring test calls this unsupported."""
    paper, d = build(tmp_path, "-0.0854 (`docs/findings/a.md`).", {"a": "measured -0.08542 at forty replicates"})
    res = e192.audit(paper, d)
    assert res["in_the_cited_finding"] == 1 and res["in_no_finding"] == 0
    # and a quote that no rounding produces is not
    paper2, d2 = build(tmp_path / "b", "-0.0855 (`docs/findings/a.md`).", {"a": "measured -0.08542"})
    assert e192.audit(paper2, d2)["in_no_finding"] == 1


def test_a_number_from_another_finding_is_its_own_class_and_not_a_failure(tmp_path):
    paper, d = build(tmp_path, "**-0.0116** (`docs/findings/a.md`).", {"a": "nothing here", "b": "-0.0116"})
    res = e192.audit(paper, d)
    assert res["in_another_finding"] == 1 and res["in_no_finding"] == 0
    assert res["elsewhere"][0]["found_in"] == "b.md"
    assert e192.report(res) == 0, "the middle class must not make the check fail"


def test_a_number_no_finding_carries_is_the_exit_code(tmp_path):
    paper, d = build(tmp_path, "**-0.9999** (`docs/findings/a.md`).", {"a": "nothing here"})
    res = e192.audit(paper, d)
    assert res["in_no_finding"] == 1 and e192.report(res) == 1


def test_the_live_paper_has_no_number_its_corpus_cannot_support():
    """The gate, with the denominator: 104 sentences and 330 numbers are what make the zero a statement."""
    res = e192.audit()
    assert res["sentences_checked"] >= 90 and res["numbers_checked"] >= 250
    assert res["in_no_finding"] == 0, res["unsupported"]
    assert res["in_the_cited_finding"] >= 250
    assert res["in_another_finding"] >= 10, "the middle class is the audit's substance; it must not be empty"


def test_the_audit_reports_which_document_it_read(capsys):
    """It is run on two documents now, and the header has to say which one -- the first version printed the counts
    with no document named, so two interleaved runs were indistinguishable."""
    paper, d = build(tmp_path := __import__("pathlib").Path.cwd() / "tmp_test_doc", "**-0.0116** (`docs/findings/a.md`).",
                     {"a": "-0.0116"})
    res = e192.audit(paper, d)
    e192.report(res)
    out = capsys.readouterr().out
    assert str(paper) in out
    paper.unlink(); (d / "a.md").unlink(); d.rmdir(); paper.parent.rmdir()


def test_the_two_documents_have_measurably_different_localisation_and_only_the_paper_is_a_gate():
    """The result: the plan's citations localise their rows rather than their numbers, three times as often as the
    paper's, and the plan's two exceptions are its own arithmetic -- so the paper's exit code is the gate."""
    paper = e192.audit(Path("docs/paper/clfly-v1.md"), Path("docs/findings"))
    plan = e192.audit(Path("docs/research_plan.md"), Path("docs/findings"))
    assert paper["numbers_checked"] >= 250 and plan["numbers_checked"] >= 600
    paper_rate = paper["in_another_finding"] / paper["numbers_checked"]
    plan_rate = plan["in_another_finding"] / plan["numbers_checked"]
    assert plan_rate > 2 * paper_rate, (paper_rate, plan_rate)
    assert paper["in_no_finding"] == 0, "the paper's gate"
    assert plan["in_no_finding"] <= 5, "the plan's class holds its own arithmetic; it is informational"
