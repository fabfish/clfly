"""`e182` compares a row's stated command with its artifact's `config`, and its error rate was dominated by
attribution rather than by parsing.

Every test here is one of the false positives the script actually produced while it was being written, because the
failures it has to be protected against are not "it cannot parse a flag" but "it compared the right flag with the
wrong artifact and called it a finding":

- the tokeniser swallowed a whole code span and reported **no flags in 136 of 138 rows** -- a clean table;
- a runner's file name (`e5_anisotropy_axis.py`) was read as the label `e5` and compared with `e5_anisotropy.json`;
- an artifact named as a **comparison partner** ("... against `e133`'s overlap-0.0") was treated as the row's own;
- a label resolving to four files (`e140`) was silently reduced to one of them;
- the prose **quoting** a command's differing fields ("the derived command differs ... three fields,
  `--circuit-size` (1500 -> 300)") was read as a second command in the same cell.
"""

from __future__ import annotations

from pathlib import Path

from experiments import e182_command_prose_audit as e182

HEADER = ("# plan\n\n## Experimental programme\n\n"
          "| W | 类 | 为何注册 | 状态 |\n|---|---|---|---|\n")
FOOTER = "\n## Method\n\nnothing here\n"


def build(tmp_path: Path, rows: str, artifacts: dict[str, dict]) -> tuple[Path, Path]:
    plan = tmp_path / "plan.md"
    plan.write_text(HEADER + rows + FOOTER, encoding="utf-8")
    runs = tmp_path / "runs"
    runs.mkdir(exist_ok=True)
    for name, config in artifacts.items():
        (runs / name).write_text(e182.json.dumps({"config": config}), encoding="utf-8")
    return plan, runs


def test_a_code_span_is_not_one_token_so_a_command_inside_it_is_still_read(tmp_path):
    """The 136-of-138 failure: `` `--lam 1.0` `` matched as a single token found no flags at all."""
    index = e182.artifact_names(tmp_path / "empty")
    toks, _lost, _flags = e182.command_tokens("`--lam 1.0 --repeats 40` at read-out 32", index)
    assert e182.flag_pairs(toks) == [("lam", "1.0"), ("repeats", "40")]


def test_a_runner_name_is_not_a_label(tmp_path):
    """`e5_anisotropy_axis.py` is not `e5`: the first version compared its `--seeds 12` with `e5_anisotropy.json`'s
    `3` and called a mismatch, on a row whose artifact is written somewhere else entirely."""
    plan, runs = build(tmp_path,
                       "| `e5_anisotropy_axis.py --seeds 12` | C2b | why | done |\n",
                       {"e5_anisotropy.json": {"seeds": 3}})
    res = e182.audit(plan, runs)
    assert res["n_checks"] == 0 and res["n_mismatches"] == 0
    assert res["skips"]["first cell names no artifact it can resolve"] == 1


def test_a_comparison_partner_is_not_the_rows_own_artifact(tmp_path):
    """L1097's shape: the row's command is measured *against* a baseline artifact, and comparing the two is the
    row's point -- so the baseline's config is not a source of truth about the command."""
    plan, runs = build(tmp_path,
                       "| `--input-overlap 1.0 --repeats 40` against `e133`'s overlap-0.0 `naive` | C2b | why | "
                       "done |\n",
                       {"e133_r32_naive_ewc_40reps.json": {"input_overlap": 0.0, "repeats": 40}})
    res = e182.audit(plan, runs)
    assert res["n_checks"] == 0
    assert res["skips"]["first cell names an artifact only as a comparison partner"] == 1


def test_a_label_that_identifies_several_files_makes_the_row_unattributable(tmp_path):
    """L1094 named `e140`, which is four artifacts; keeping one of them compared a five-method command with the
    one file that happened to survive, and reported three mismatches."""
    plan, runs = build(tmp_path,
                       "| `--methods naive,ewc --replay-batch 8` in both arms, plus two extra draws "
                       "(`e140`, `e146`) | C2b | why | done |\n",
                       {"e140_a.json": {"methods": "naive"}, "e140_b.json": {"methods": "naive"},
                        "e146_frozen.json": {"methods": "naive"}})
    res = e182.audit(plan, runs)
    assert res["n_checks"] == 0
    assert res["skips"]["first cell names a label that identifies several files"] == 1


def test_the_command_ends_where_the_cell_first_names_its_artifact(tmp_path):
    """L1046: nine flags are stated, three of which the cell then *quotes* as the fields a derived command
    differs in. Without the cut, `--circuit-size` was read as both 300 and 1500 and both were reported."""
    cell = ("| `e3 --circuit-size 300 --support 30` the ladder, its artifact to be written as `e181_ladder.json` "
            "under `runs/`, and the derived command differs in `--circuit-size` (1500 -> 300) | C2b | why | done |\n")
    plan, runs = build(tmp_path, cell, {"e181_ladder.json": {"circuit_size": 300, "support": 30}})
    res = e182.audit(plan, runs)
    assert res["n_checks"] == 2 and res["n_mismatches"] == 0
    assert {c["flag"] for c in res["checks"]} == {"circuit-size", "support"}
    # and the tokens the cut threw away are reported, because a convention is not a guarantee
    assert res["tokens_discarded_after_the_cell_named_its_artifact"] > 0
    assert res["flags_in_the_discarded_part_never_checked"] == 1


def test_a_list_valued_config_agrees_with_a_member_and_says_so(tmp_path):
    cell = "| `e3 --topologies real` the ladder, artifact `e181_ladder.json` | C2b | why | done |\n"
    plan, runs = build(tmp_path, cell, {"e181_ladder.json": {"topologies": ["real"]}})
    res = e182.audit(plan, runs)
    assert res["n_mismatches"] == 0
    assert res["checks"][0]["verdict"] == "match (a member of the config's list)"


def test_the_rows_own_label_resolves_and_a_number_is_a_number(tmp_path):
    """`3e-3` in the table and `0.003` in the config are the same value, and saying otherwise would have been the
    fourth misreport in a row."""
    plan, runs = build(tmp_path,
                       "| `--lam 3e-3 --repeats 40` at read-out 32 (`e133`) | C2b | why | done |\n",
                       {"e133_r32_naive_ewc_40reps.json": {"lam": 0.003, "repeats": 40}})
    res = e182.audit(plan, runs)
    assert res["n_checks"] == 2 and res["n_mismatches"] == 0
    assert e182.same("3e-3", 0.003) and e182.same("40", 40.0) and not e182.same("40", 41)
    assert not e182.same("real", ["real"])          # the list case belongs to the audit, which labels the verdict


def test_parts_of_a_command_that_are_not_literal_values_are_counted_not_compared(tmp_path):
    """`--control-draws K` and `--repeats {8,16}`: two shapes the hand pass compared anyway, and each is now a skip
    with its own reason rather than a mismatch."""
    plan, runs = build(tmp_path,
                       "| `e3 --control-draws K --repeats {8,16} --seeds 18` artifact `e13_control3.json` | "
                       "C2b | why | done |\n",
                       {"e13_control3.json": {"repeats": 16, "seeds": 18}})
    res = e182.audit(plan, runs)
    assert res["n_mismatches"] == 0
    assert res["flag_skips"]["value is a placeholder rather than a literal"] == 2
    assert {c["flag"] for c in res["checks"]} == {"seeds"}


def test_a_store_true_flag_given_a_value_is_a_real_finding(tmp_path):
    """`--extra-bases` is a `store_true` flag in `e3_basis_selection`, read from `e172`'s registry rather than
    guessed, so a value after it is the one shape that is a finding on its own terms rather than a comparison."""
    plan, runs = build(tmp_path,
                       "| `e3 --extra-bases 5` artifact `e13_control3.json` | C2b | why | done |\n",
                       {"e13_control3.json": {"seeds": 18}})
    res = e182.audit(plan, runs)
    assert res["n_mismatches"] == 1
    assert res["mismatches"][0]["verdict"] == "mismatch: store_true flag given a value"
    # and with no value after it there is nothing to compare, so it is a skip rather than a pass
    toks, _lost, _flags = e182.command_tokens("`--extra-bases --seeds 18`", e182.artifact_names(runs))
    assert e182.flag_pairs(toks) == [("extra-bases", None), ("seeds", "18")]


def test_the_readout_census_says_which_values_are_the_whole_state_and_whose_meaning_is_lost(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "a.json").write_text(e182.json.dumps(
        {"config": {"readout_size": 0}, "circuit": "mb+cx@n1307", "readout": {"size": 1307}}), encoding="utf-8")
    (runs / "b.json").write_text(e182.json.dumps(
        {"config": {"readout_size": 1307}, "circuit": "mb+cx@n1307", "readout": {"size": 1307}}), encoding="utf-8")
    (runs / "c.json").write_text(e182.json.dumps(
        {"config": {"readout_size": 32}, "circuit": "mb+cx@n1307", "readout": {"size": 32}}), encoding="utf-8")
    (runs / "d.json").write_text(e182.json.dumps(
        {"config": {"readout_size": 32}, "readout": {"size": 32}}), encoding="utf-8")
    census = e182.readout_census(runs)
    assert census["classes"] == {"the whole state": 2, "a draw of this size": 1,
                                "achieved count not recorded": 1}
    assert census["spellings"]["0"] == 1
    assert census["spellings"]["the achieved count itself"] == 1
    assert census["spellings"]["a literal below the achieved count"] == 1
    assert census["spellings"]["a literal, with no achieved count to compare it to"] == 1
    assert census["readout_block_contradicts_the_rule"] == []
    # the denominator, not just the zero: `d` has no block to check and no `circuit` name, so 3 of the 4 are
    # checkable here, and the count is asserted rather than the zero alone
    assert census["n_artifacts_with_a_readout_block_to_check"] == 3
    # a value at or above the achieved count is the whole state, so a `readout` block recording a SMALLER size is
    # the one shape that would mean a runner rewrote the field -- which is the hypothesis this census refutes
    (runs / "e.json").write_text(e182.json.dumps(
        {"config": {"readout_size": 1307}, "circuit": "mb+cx@n1307", "readout": {"size": 32}}), encoding="utf-8")
    assert len(e182.readout_census(runs)["readout_block_contradicts_the_rule"]) == 1
    assert e182.readout_census(runs)["n_artifacts_with_a_readout_block_to_check"] == 4


def test_the_plan_itself_states_no_command_that_contradicts_its_artifact():
    """The gate, on the real table. A lower bound on the checks rather than a pinned count: the table grows, and a
    test that pinned how many of its rows are checkable would fail every time a row is added."""
    res = e182.audit()
    assert res["n_mismatches"] == 0, res["mismatches"]
    assert res["rows"] >= 130 and res["n_checks"] >= 20
    assert res["unparseable"] == 0
    # the two ledgers are separate accounts: rows that could not be attributed, and flags inside a row that was
    # attributed. Adding them was a defect -- 140 "rows" from a table that has 138.
    assert res["rows_accounted_for"] == res["rows"]
    assert res["checked_rows"] + sum(res["skips"].values()) == res["rows"]
    assert all(c["verdict"].startswith("match") for c in res["checks"])
