"""`e227` reads the `real` cell's basis-independent fingerprint and separates "the inputs moved" from "the method
moved".

The premise is checked rather than assumed -- **0 of the 26 artifacts** carry more than one `oracle_mean` across their
own bases -- and the classification is in **ulps**, because a 1-ulp spread and a 5e-7 spread are different findings.
Two groups drift: one is attributed to the thread class the module measures itself (`--thread-sweep`), the other is
declared **OPEN** with its candidates, since the honest reading there is that the deviation is 100x the measured
arithmetic class and nothing else in the code or the data has been shown to move.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from experiments import e227_oracle_fingerprint_census as e227


def artifact(name: str, config: dict, oracle: float, bases: int = 2, excess: float = 0.01) -> dict:
    block = {"diagonal(EWC)": {"analytic": {"excess_mean": excess, "oracle_mean": oracle}}}
    for i in range(bases - 1):
        block[f"bio:pool{2 ** i}"] = {"analytic": {"oracle_mean": oracle}}
    return {"name": name, "config": config, "payload": {"topologies": {"real": block}}, "mtime": 0.0}


CFG = {"circuit_size": 800, "support": 80, "seeds": 3, "seed0": 0, "q": 0.02}


def write(tmp_path: Path, rows: list[dict]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for r in rows:
        (tmp_path / r["name"]).write_text(json.dumps({"config": r["config"], "topologies": r["payload"]["topologies"],
                                                      "timing": {"total_s": 1.0}}), encoding="utf-8")
    return tmp_path


def test_a_group_that_shares_its_tasks_has_a_bit_identical_fingerprint(tmp_path):
    root = write(tmp_path, [artifact("a.json", CFG, 0.5), artifact("b.json", CFG, 0.5)])
    res = e227.census(root)
    assert len(res["groups"]) == 1 and res["groups"][0]["ulp_spread"] == 0
    assert res["drifts"] == [] and e227.report(res) == 0


def test_ulps_not_ratios_separate_a_one_ulp_drift_from_a_measured_one(tmp_path):
    """The class matters: a fingerprint that moved by one bit and one that moved by 3e-7 relative are two findings."""
    a, b = 0.5, 0.5 + 2 ** -53  # one ulp apart
    root = write(tmp_path, [artifact("a.json", CFG, a), artifact("b.json", CFG, b)])
    g = e227.census(root)["groups"][0]
    assert g["ulp_spread"] == 1 and g["rel_spread"] < 1e-15


def test_a_drift_no_declaration_covers_is_the_exit_code(tmp_path):
    root = write(tmp_path, [artifact("a.json", CFG, 0.5), artifact("b.json", CFG, 0.5001)])
    res = e227.census(root)
    assert [g["key"] for g in res["undeclared_drifts"]] == [res["groups"][0]["key"]]
    assert e227.report(res) == 1


def test_a_declared_drift_is_reported_by_name_and_by_status(tmp_path, capsys):
    """The table's keys have to be the keys the census builds, or a declared drift silently fails to be declared."""
    parsed = {f: ast.literal_eval(v)
              for f, v in (p.split("=", 1) for p in sorted(e227.DECLARED_DRIFT)[0].split(", "))}
    root = write(tmp_path, [artifact("a.json", parsed, 0.5), artifact("b.json", parsed, 0.5001)])
    res = e227.census(root)
    assert res["groups"][0]["key"] in e227.DECLARED_DRIFT
    assert res["undeclared_drifts"] == []
    assert e227.report(res) == 0
    out = capsys.readouterr().out
    assert f"DECLARED [{e227.DECLARED_DRIFT[res['groups'][0]['key']]['status']}]" in out


def test_a_groups_own_bases_must_agree_because_the_oracle_sees_no_basis():
    """The premise, on the live corpus: this is what licenses reading the number as a fingerprint of the tasks."""
    res = e227.census()
    disagreeing = [g for g in res["groups"] if g["artifacts_with_more_than_one_oracle_in_their_own_bases"]]
    assert disagreeing == [], disagreeing
    assert res["artifacts"] >= 20


def test_the_live_corpus_has_four_bit_exact_groups_and_two_declared_drifts():
    """The census with its denominators: 6 multi-artifact groups, 4 of them exact to the last bit."""
    res = e227.census()
    multi = [g for g in res["groups"] if g["n"] > 1]
    assert len(multi) == 6, [g["key"] for g in multi]
    exact = [g for g in multi if g["ulp_spread"] == 0]
    assert len(exact) == 4, [g["key"] for g in exact]
    assert sorted(g["key"] for g in res["drifts"]) == sorted(e227.DECLARED_DRIFT)
    assert e227.report(res) == 0, "both drifts are declared; one of them is declared OPEN rather than attributed"
    statuses = {e227.DECLARED_DRIFT[g["key"]]["status"] for g in res["drifts"]}
    assert statuses == {"attributed", "OPEN -- not attributed"}, statuses


def test_the_excess_amplifies_the_fingerprints_own_spread(tmp_path):
    """The arithmetic reason the excess is the wrong instrument: it is a difference of two larger numbers."""
    root = write(tmp_path, [artifact("a.json", CFG, 0.5, excess=0.0100),
                            artifact("b.json", CFG, 0.500001, excess=0.0105)])
    g = e227.census(root)["groups"][0]
    assert (max(g["excess_values"]) - min(g["excess_values"])) / g["excess_values"][0] > 10 * g["rel_spread"]


def test_the_task_builder_child_mode_reports_the_circuit_the_jacobians_and_both_numbers(capsys):
    """The step above the oracle: a child that fingerprints `build_tasks` itself, so a drawn circuit or a
    thread-dependent weight transform cannot hide behind the oracle sweep."""
    assert e227.main(["--tasks-at", "--circuit-size", "300", "--support", "3", "--seeds", "1"]) == 0
    row = json.loads([ln for ln in capsys.readouterr().out.splitlines() if ln.startswith("{")][-1])
    assert row["n_neurons"] > 0 and len(row["neuron_sha1"]) == 12 and len(row["j_sha1"]) >= 1
    assert isinstance(row["oracle_mean"], float) and isinstance(row["ewc_mean"], float)


def test_the_neighbour_sweep_rules_out_the_window_it_measures(capsys):
    """A deviant that no neighbouring configuration reproduces is not a transcription error *within the window* --
    which is what makes the remaining candidate the run rather than the record. A tiny window keeps the test cheap;
    the rebuilds are real (cs 300, one seed, support 3)."""
    group = {"artifacts": ["deviant.json", "reproducible.json"], "oracle_values": [0.5, 0.6]}
    assert e227.neighbour_sweep((4,), (1,), (0.03,), 300, 3, 1, 0.02, group) == 0
    out = capsys.readouterr().out
    assert "the deviant value is" in out
    assert ("no neighbouring configuration in this window reproduces the deviant's value" in out
            or "IS a neighbouring configuration's" in out)


def test_the_neighbour_sweep_refuses_a_configuration_the_corpus_does_not_carry():
    """The deviant's value comes from the corpus, so a key the corpus does not carry must stop rather than guess."""
    with pytest.raises(SystemExit):
        e227.main(["--neighbour-sweep", "--circuit-size", "999", "--support", "3", "--seeds", "1"])
