"""`e184` asks the reverse of `e97`, and its whole content is that a literal scan answers it wrongly.

The naive version -- "is this file's name a substring of the corpus?" -- reports 156 of the corpus's 376 files as
never named. The two corrections that reduce it to 1 are the classes this test file pins:

- **brace shorthand**, the class that matters: `e74_drawsd_min{8,16,128}.json` names three files and a substring
  test sees none of them;
- **the sibling test**, which is deliberately weaker and is reported as its own class.

And the exit code asks about **runs**, not about files: an un-named audit report is explained by its plan row
naming the script, while an un-named run is a result nobody has written up. A check that mixed the two would fire
on its own output.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e184_artifact_citation_census as e184


def build(tmp_path: Path, docs: str, artifacts: dict[str, dict | None]) -> tuple[Path, Path]:
    runs = tmp_path / "runs"
    docs_dir = tmp_path / "docs"
    runs.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "a.md").write_text(docs, encoding="utf-8")
    for name, payload in artifacts.items():
        (runs / name).write_text(json.dumps(payload if payload is not None else {"summary": 1}), encoding="utf-8")
    return runs, docs_dir


AUDIT = lambda runs, docs: e184.audit(runs, docs_globs=(str(docs / "*.md"),))


def test_a_file_named_outright_is_cited_by_full_name(tmp_path):
    runs, docs = build(tmp_path, "see `runs/e9_a.json` for it",
                       {"e9_a.json": {"config": {"seeds": 3}}})
    res = AUDIT(runs, docs)
    assert res["cited_by_full_name"] == 1 and res["cited_only_by_a_shorthand"] == 0


def test_a_brace_shorthand_names_files_a_substring_test_cannot_see(tmp_path):
    """The measured class: `min{8,16,128}` is one citation and three files, and the naive scan calls all three
    uncited -- which is why the naive count is printed beside the corrected one."""
    runs, docs = build(tmp_path, "see `runs/e74_drawsd_min{8,16,128}.json` for the three rungs",
                       {"e74_drawsd_min8.json": {"config": {"min_size": 8}},
                        "e74_drawsd_min16.json": {"config": {"min_size": 16}},
                        "e74_drawsd_min128.json": {"config": {"min_size": 128}}})
    res = AUDIT(runs, docs)
    assert res["cited_by_full_name"] == 0
    assert res["cited_only_by_a_shorthand"] == 3
    assert res["uncited_before_expanding_shorthands"] == 3, "the naive count must be reported, not hidden"
    assert res["no_file_cited_at_all"] == 0


def test_the_shorthand_pattern_does_not_match_a_member_that_is_not_listed(tmp_path):
    """`min{8,16}` does not name `min128`."""
    runs, docs = build(tmp_path, "see `runs/e74_drawsd_min{8,16}.json`",
                       {"e74_drawsd_min128.json": {"config": {"min_size": 128}},
                        "e74_drawsd_min16.json": {"config": {"min_size": 16}}})
    res = AUDIT(runs, docs)
    assert res["cited_only_by_a_shorthand"] == 1
    assert res["no_file_cited_but_a_sibling_is"] == 1, "min128 is not named by that shorthand, but e74 is"
    assert res["no_file_cited_at_all"] == 0


def test_a_sibling_citation_is_its_own_weaker_class(tmp_path):
    runs, docs = build(tmp_path, "see `runs/e104_report.json`",
                       {"e104_report.json": {"summary": 1},
                        "e104_a.json": {"config": {"arm": "a"}},
                        "e104_b.json": {"config": {"arm": "b"}}})
    res = AUDIT(runs, docs)
    assert res["cited_by_full_name"] == 1
    assert res["no_file_cited_but_a_sibling_is"] == 2
    assert res["no_file_cited_at_all"] == 0


def test_the_exit_code_asks_about_runs_and_not_about_report_files(tmp_path):
    """An un-named run is a result nobody wrote up; an un-named audit report is explained by its plan row naming
    the script. Mixed into one count, this check would fire on its own output."""
    runs, docs = build(tmp_path, "nothing here names either file",
                       {"e9_run.json": {"config": {"seeds": 1}}, "e9_audit.json": {"summary": 1}})
    res = AUDIT(runs, docs)
    assert res["no_file_cited_at_all"] == 2
    assert res["unnamed_with_a_config"] == ["e9_run.json"]
    assert e184.report(res) == 1
    assert e184.report(AUDIT(*build(tmp_path / "b", "nothing names it", {"e9_audit.json": {"summary": 1}}))) == 0


def test_an_un_named_run_that_duplicates_a_named_one_is_sharpened_out(tmp_path):
    """The weakest class, second order: two files with the SAME configuration (minus `json_out`) are one run written
    twice, and a citation of either covers both -- which is not true of a configuration no named file carries."""
    runs, docs = build(tmp_path, "see `runs/e9_dup_a.json`",
                       {"e9_dup_a.json": {"config": {"seeds": 1, "json_out": "runs/e9_dup_a.json"}},
                        "e9_dup_b.json": {"config": {"seeds": 1, "json_out": "runs/e9_dup_b.json"}},
                        "e9_other.json": {"config": {"seeds": 2}}})
    res = AUDIT(runs, docs)
    assert res["sibling_runs_with_a_named_identical_twin"] == ["e9_dup_b.json"]
    assert res["sibling_runs_with_distinct_configurations"] == 1


def test_the_live_corpus_names_every_run_and_the_robustness_switch_does_not_change_it():
    """The gate, with lower bounds rather than pinned counts: the corpus grows."""
    res = e184.audit(Path("runs"))
    assert res["artifacts"] >= 300 and res["documents_scanned"] >= 200
    assert res["cited_by_full_name"] >= 150
    assert res["no_file_cited_at_all"] <= 5, res["unnamed"]
    assert res["unnamed_with_a_config"] == [], "an un-named run is a result nobody wrote up"
    # the two counted classes, so that a pass here is not mistaken for "the corpus cites everything": the naive
    # scan is wrong by at least 20 files, and the aggregate-report form covers more than fifty
    assert res["cited_only_by_a_shorthand"] >= 20
    assert res["no_file_cited_but_a_sibling_is"] >= 50
    with_code = e184.audit(Path("runs"), include_code=True)
    assert with_code["no_file_cited_at_all"] <= res["no_file_cited_at_all"], "code can only add citations"
