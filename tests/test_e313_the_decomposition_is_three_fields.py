"""`e313` tests whether the matrix's cells are fields the corpus already writes, so the tests pin the cell reader,
the index join, both faces of the four claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e313_the_decomposition_is_three_fields as e313


def _rep():
    R = [[1.0, None, None], [0.9, 1.0, None], [0.8, 0.9, 1.0]]
    return {"retention": R, "learned": [1.0, 1.0, 1.0], "final_per_task": [0.8, 0.9, 1.0],
            "forgetting_per_task": [0.2, 0.1, 0.0]}


def test_the_cells_are_the_diagonal_and_the_last_row_and_a_bad_matrix_is_refused():
    c = e313.cells(_rep())
    assert c == {"reached": [1.0, 1.0, 1.0], "ended": [0.8, 0.9, 1.0], "T": 3}, c
    # a None where a number is required is not a zero: the reader refuses rather than reading one
    for bad in ({}, {"retention": []}, {"retention": [[None, None], [1.0, 1.0]]},
                {"retention": [[1.0, None], [1.0, None]]}):
        assert e313.cells(bad) is None, bad
    assert e313.close(0.1 + 0.2, 0.3) is True and e313.close(0.1, 0.2) is False


def test_the_index_join_reaches_the_payload_a_row_names(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps({"methods": {"naive": {"replicates": [
        {"learned": [1.0, 1.0]}, {"learned": [0.5, 0.5]}]}}}), encoding="utf-8")
    index = e313.by_index(tmp_path)
    assert set(index) == {("a.json", "naive", 0), ("a.json", "naive", 1)}, index
    assert index[("a.json", "naive", 1)]["learned"] == [0.5, 0.5]


def _reading(rows=6096, ok=None, ledger=None, term_rows=5581, wrong_index=0):
    ok = ok if ok is not None else {"learned": rows, "final_per_task": rows, "forgetting_per_task": rows}
    ledger = ledger if ledger is not None else {"unlearned_mean": term_rows, "shortfall_mean": term_rows,
                                                "lost_mean": term_rows}
    return {"rows": rows, "ok": ok, "carried": {}, "term_rows": term_rows, "terms": ledger,
            "wrong_index": wrong_index, "first_bad": {}}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e313.judge(_reading())}
    for cid in ("Y1", "Y2", "Y3", "Y4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # one arm where the matrix disagrees with a field is that field's falsifier
    for key, cid in (("learned", "Y1"), ("final_per_task", "Y2"), ("forgetting_per_task", "Y3")):
        bad = _reading(ok={"learned": 6096, "final_per_task": 6096, "forgetting_per_task": 6096})
        bad["ok"][key] = 6095
        assert {r["id"]: r for r in e313.judge(bad)}[cid]["verdict"].startswith("FALSIFIER FIRED"), cid
    # and one term of the split that is neither field nor complement is Y4's
    for key in ("unlearned_mean", "shortfall_mean", "lost_mean"):
        bad = _reading(ledger={"unlearned_mean": 5581, "shortfall_mean": 5581, "lost_mean": 5581})
        bad["terms"][key] = 5580
        assert e313.judge(bad)[3]["verdict"].startswith("FALSIFIER FIRED"), key
    assert e313.judge({"rows": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_is_what_the_finding_says():
    r = e313.reading()
    assert r["rows"] >= 6000 and r["wrong_index"] == 0, (r["rows"], r["wrong_index"])
    assert set(r["ok"]) == {"learned", "final_per_task", "forgetting_per_task"}, r["ok"]
    assert all(v == r["rows"] for v in r["ok"].values()), r["ok"]
    # the three fields travel with the matrix, which is what makes the split readable from either
    assert r["carried"]["learned"] >= r["rows"] and r["carried"]["retention"] >= r["rows"], r["carried"]
    assert r["term_rows"] >= 5000 and all(v == r["term_rows"] for v in r["terms"].values()), r["terms"]
    claims = {x["id"]: x["verdict"] for x in e313.judge(r)}
    for cid in ("Y1", "Y2", "Y3", "Y4"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e313_the_decomposition_is_three_fields.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert all(v == d["rows"] for v in d["ok"].values()), d["ok"]
    assert all(v == d["term_rows"] for v in d["terms"].values()), d["terms"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("Y1", "Y2", "Y3", "Y4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
