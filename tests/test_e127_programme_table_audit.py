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
    # check C, and its denominator: it is only a check where a row claims an experiment as its OWN, which 111 of
    # 140 rows do -- so "0 flags" here is a statement about those 111 and not about the table
    assert res["underclaims"] == []
    assert res["rows_naming_their_own_experiment_with_artifacts"] > 50


def runs_dir(tmp_path: Path, *names: str) -> Path:
    d = tmp_path / "runs"
    d.mkdir(exist_ok=True)
    for n in names:
        (d / n).write_text("{}", encoding="utf-8")
    return d


def test_check_c_fires_on_an_arm_the_row_still_calls_running(tmp_path):
    """The `e147` shape, live in the plan for two days: the first cell says the second arm is running and the
    second arm's artifact is on disk."""
    runs = runs_dir(tmp_path, "e147_r32_frozenbias_ewc_lam3e-3.json")
    p = doc(tmp_path, row("`--frozen-bias --methods ewc --lam {3e-4, 3e-3}` at read-out 32 (`e147`; the `3e-4` arm "
                          "is in, the `3e-3` arm is running)", "why", "**done for the first arm — the rest.**"))
    res = audit(p, runs)
    assert len(res["underclaims"]) == 1
    assert res["underclaims"][0]["form"] == "an arm is still described as running"
    assert res["underclaims"][0]["artifacts"] == ["e147_r32_frozenbias_ewc_lam3e-3.json"]


def test_check_c_fires_when_every_registered_arm_is_on_disk(tmp_path):
    """The `e141` shape: the running clause names no value ("the top of the sweep is running"), so the braced
    registration is what has to be compared with the disk."""
    runs = runs_dir(tmp_path, "e141_r32_ewc_lam3e-4.json", "e141_r32_ewc_lam3e-2.json", "e141_r32_ewc_lam3e-1.json")
    p = doc(tmp_path, row("`--methods ewc --lam {3e-4, 3e-2, 3e-1} --repeats 40` at read-out 32 (`e141`; the "
                          "`3e-4` arm is in, the top of the sweep is running)", "why",
                          "**done for the floor arm — the rest.**"))
    res = audit(p, runs)
    assert len(res["underclaims"]) == 1
    assert res["underclaims"][0]["form"] == "every registered arm is on disk"
    assert len(res["underclaims"][0]["artifacts"]) == 3


def test_check_c_does_not_fire_when_the_arm_it_names_is_not_on_disk(tmp_path):
    """The direction that makes it a check: `e178`'s row is genuinely in flight, and its own artifacts are absent.
    A missing arm is a row that is telling the truth."""
    runs = runs_dir(tmp_path, "e141_r32_ewc_lam3e-4.json")   # the floor arm is in, the top is not
    p = doc(tmp_path, row("`--methods ewc --lam {3e-4, 3e-2, 3e-1}` at read-out 32 (`e141`; the `3e-4` arm is in, "
                          "the top of the sweep is running)", "why", "**done for the floor arm — the rest.**"))
    assert audit(p, runs)["underclaims"] == []


def test_check_c_ignores_another_experiments_artifacts_cited_as_a_prior(tmp_path):
    """A row cites other experiments' artifacts as priors and baselines constantly -- `e178`'s row names `e10` and
    `e60` in the sentence that says its own artifacts do not exist yet. Only the row's OWN id counts, and the two
    ways it is stated are the runner it names and a parenthesised label."""
    runs = runs_dir(tmp_path, "e10_rung_side.json", "e60_side_lam0.1_16reps.json")
    p = doc(tmp_path, row("`e8_rate_network.py --circuit-size 300 --repeats 144`, against `e10` and `e60`", "why",
                          "**LAUNCHED, NOT READ — no artifact, and no number is printed.**"))
    assert audit(p, runs)["underclaims"] == []


def test_check_c_does_not_fire_on_a_row_whose_own_opening_reports_the_answer(tmp_path):
    """The measured false-positive class: `P1 HOLDS` and `READ —` are how this table announces an answer, and a
    cell that opens that way is reporting; the word "launched" three sentences later is prose about a queue."""
    runs = runs_dir(tmp_path, "e92_grid_report.json")
    p = doc(tmp_path, row("`e92_grid_profiles.py`", "why",
                          "**P1 HOLDS AND THE SWEEP IS COMPLETE**, launched when a slot freed, and the queue "
                          "cleared."))
    res = audit(p, runs)
    assert res["underclaims"] == []
    assert res["underclaims_excluded_by_a_finished_word"] == 1, "it must be counted, not silently ignored"
