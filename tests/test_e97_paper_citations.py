"""The paper's citations are now read too, and the check has to count what it scanned.

`e97` asked whether every `runs/` file a *finding* cites exists, and nothing asked it of the **paper** — the
document a reader arrives at first, with 34 artifact paths and 66 finding paths in it at the time this check was
added. Two properties make the check interpretable rather than merely green:

  * **the denominators are reported beside the zeros**, because `0 missing` out of an unknown number of
    citations is indistinguishable from a check that never fired — the same discipline `e105`'s output follows;
  * and it counts **both** kinds of path, because a stale `docs/findings/` link fails a reader in exactly the way
    a stale artifact path does, and the paper cites nearly twice as many of those.
"""

from __future__ import annotations

from experiments.e97_findings_corpus_audit import check_paper


def test_the_paper_check_reports_its_denominators(tmp_path):
    paper = tmp_path / "paper.md"
    paper.write_text(
        "See `runs/one.json` and `docs/findings/a-finding.md`.\n"
        "And also `runs/two.json`.\n",
        encoding="utf-8")
    (tmp_path / "runs").mkdir()
    (tmp_path / "runs" / "one.json").write_text("{}", encoding="utf-8")
    (tmp_path / "docs" / "findings").mkdir(parents=True)
    (tmp_path / "docs" / "findings" / "a-finding.md").write_text("x", encoding="utf-8")

    import os

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        got = check_paper(tmp_path / "paper.md")
    finally:
        os.chdir(cwd)

    assert got["n_runs_cited"] == 2 and got["n_findings_cited"] == 1     # the denominators
    assert got["missing_runs"] == ["runs/two.json"]                      # and the one that is missing
    assert got["missing_findings"] == []


def test_a_paper_whose_citations_all_exist_reports_zero_missing_with_a_nonzero_denominator(tmp_path):
    paper = tmp_path / "paper.md"
    paper.write_text("`docs/findings/x.md` and `docs/findings/y.md`\n", encoding="utf-8")
    (tmp_path / "docs" / "findings").mkdir(parents=True)
    for n in ("x", "y"):
        (tmp_path / "docs" / "findings" / f"{n}.md").write_text("z", encoding="utf-8")

    import os

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        got = check_paper(tmp_path / "paper.md")
    finally:
        os.chdir(cwd)

    assert got["n_findings_cited"] == 2 and got["n_runs_cited"] == 0
    assert got["missing_findings"] == [] and got["missing_runs"] == []


def test_the_command_check_reports_the_module_and_the_flag_it_cannot_find(tmp_path):
    """A stale flag in the reproducibility table is the defect this asks about, and it must be named.

    §9's table named a superseded command once already, which prose could not see. The check compares each
    `python -m <module>` against a file on disk and each `--flag` against that module's own source, so both
    halves need a positive case -- the denominators alone would let a check that never fires look clean.
    """
    from experiments.e97_findings_corpus_audit import check_commands

    paper = tmp_path / "paper.md"
    paper.write_text(
        "`python -m experiments.e_present --a-flag --missing-flag`\n"
        "`python -m experiments.e_absent --whatever`\n",
        encoding="utf-8")
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments" / "e_present.py").write_text(
        'import argparse\np = argparse.ArgumentParser()\np.add_argument("--a-flag")\n', encoding="utf-8")

    import os

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        got = check_commands(paper)
    finally:
        os.chdir(cwd)

    assert got["n_commands"] == 2                                 # the denominator
    # only the present module's flags are checked: a module that is absent cannot be asked about its flags
    assert got["n_flags"] == 2
    assert got["modules_missing"] == ["experiments.e_absent"]
    assert got["flags_missing"] == [{"module": "experiments.e_present", "flag": "--missing-flag"}]
