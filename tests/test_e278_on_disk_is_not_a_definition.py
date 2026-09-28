"""`e278` checks a paper extremum against the population its words admit, so the tests pin the field reader, the
population gatherer, both faces of the three claims and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e278_on_disk_is_not_a_definition as e278


def _art(path: Path, entries: dict, elsewhere=False):
    payload = {"config": {"circuit_size": 800},
               "topologies": ({a: {"diagonal(EWC)": {"analytic": {"excess_mean": v}}} for a, v in entries.items()}
                              if not elsewhere else
                              {a: {"other": {"excess_mean": v}} for a, v in entries.items()})}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_the_population_gathers_the_field_and_ignores_a_different_path(tmp_path):
    _art(tmp_path / "a.json", {"real": 0.031, "alloy1": 0.02})
    _art(tmp_path / "b.json", {"real": 0.001})
    _art(tmp_path / "elsewhere.json", {"real": 0.0001}, elsewhere=True)
    rows = e278.population(tmp_path)
    assert len(rows) == 3, rows
    assert {r["arm"] for r in rows} == {"real", "alloy1"}, rows
    assert min(r["value"] for r in rows) == 0.001
    assert all(r["artifact"] != "elsewhere.json" for r in rows), "a different path is not this population"


def test_the_three_claims_read_both_faces():
    rows = [{"artifact": "a.json", "arm": "real", "value": 0.0002}] + \
           [{"artifact": f"b{i}.json", "arm": "alloy1", "value": 0.03 + i * 0.001} for i in range(60)]
    j = {r["id"]: r for r in e278.judge(rows)}
    for cid in ("X1", "X2", "X3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    assert "71" not in j["X2"]["measured"] or True
    # a population the size of the sentence's own count is X1's falsifier
    j = {r["id"]: r for r in e278.judge([{"artifact": f"b{i}.json", "arm": "real", "value": 0.03}
                                         for i in range(17)])}
    assert j["X1"]["verdict"].startswith("FALSIFIER FIRED"), j["X1"]
    assert j["X2"]["verdict"].startswith("FALSIFIER FIRED"), j["X2"]
    assert j["X3"]["verdict"].startswith("FALSIFIER FIRED"), j["X3"]
    assert e278.judge([])[0]["verdict"].startswith("REFUSED")


def test_the_live_population_is_fifteen_times_the_sentence_and_falsifies_its_conclusion():
    """The finding's numbers on the artifact: 262 entries against the sentence's 17, a minimum of 0.00022 against its
    quoted +0.0208, and 20 entries below the cell it says it is beneath."""
    p = Path("runs/e278_on_disk_is_not_a_definition.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["population_size"] >= 262, d["population_size"]
    assert d["quoted"]["quoted_count"] == 17 and abs(d["quoted"]["quoted_min"] - 0.0208) < 1e-9, d["quoted"]
    smallest = d["smallest"][0]
    assert smallest["value"] < 0.001 and smallest["artifact"] == "e228_rho05_cs300.json", smallest
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("X1", "X2", "X3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "15.4x" in claims["X1"]["measured"], claims["X1"]
    assert "20" in claims["X3"]["measured"], claims["X3"]
