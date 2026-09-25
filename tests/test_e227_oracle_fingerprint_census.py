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
