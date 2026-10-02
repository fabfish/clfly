"""`e347` asks whether the one family that disagrees resolves, so the tests pin the field diff, the family band,
and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e347_the_family_that_disagrees as e347


def _est(delta, sigma, n=20):
    return {"n": n, "delta": delta, "sem": abs(delta) / sigma if sigma else 0.0, "sigma": sigma}


def _run(acc, sigma=4.0, forget=None, fsigma=4.0, circ=300, repeats=20):
    return {"artifact": "e347_fb8_at_cs300.json", "circuit_size": circ, "readout_size": 32, "overlap": 0.0,
            "frozen_bias": False, "closed_loop": False, "n_tasks": 3, "repeats": repeats,
            "final_accuracy": _est(acc, sigma, repeats),
            "mean_forgetting": _est(forget if forget is not None else -acc, fsigma, repeats)}


def _reading(new, fam=(0.0, 0.0), diff=None):
    rows = [{"artifact": f"f{i}.json", "circuit_size": 800, "readout_size": 32, "overlap": 0.0,
             "frozen_bias": False, "closed_loop": False, "n_tasks": 3, "repeats": 5,
             "final_accuracy": _est(d, 1.0), "mean_forgetting": _est(-d, 1.0)} for i, d in enumerate(fam)]
    return {"new": new, "family": rows, "source": "e101_rate_fb8.json",
            "moved": {k: list(v) for k, v in e347.MOVED.items()},
            "field_diff": diff if diff is not None else {"circuit_size": [800, 300], "repeats": [5, 20]},
            "family_accuracy": e347.across(rows, e347.ACC),
            "family_forgetting": e347.across(rows, e347.FORGET)}


def _judge(r):
    return {row["id"]: row for row in e347.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading(_run(0.02, sigma=8.0, forget=-0.02, fsigma=8.0), fam=(0.01, 0.01)))
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: an unintended field moving, and an intended one that did not
    assert _judge(_reading(_run(0.05), diff={"circuit_size": [800, 300], "repeats": [5, 20],
                                             "lam": [0.003, 0.01]}))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(_run(0.05), diff={"circuit_size": [800, 800], "repeats": [5, 20]}))["T1"][
        "verdict"].startswith("FALSIFIER")
    # T2: the ordering resolving against replay, and an unresolved run
    assert _judge(_reading(_run(-0.05)))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(_run(0.01, sigma=1.0)))["T2"]["verdict"].startswith("NULL")
    # T3: the family's band -- inside, between, and apart
    assert _judge(_reading(_run(0.02), fam=(0.0, 0.0)))["T3"]["verdict"].startswith("MET")
    assert _judge(_reading(_run(0.04), fam=(0.0, 0.0)))["T3"]["verdict"].startswith("NULL")
    assert _judge(_reading(_run(0.07), fam=(0.0, 0.0)))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: replay forgetting more is the wrong side
    assert _judge(_reading(_run(0.05, forget=0.05)))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(_run(0.05, forget=0.001, fsigma=1.0)))["T4"]["verdict"].startswith("NULL")
    # a missing run or a one-member family refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e347.judge({"new": None, "family": []}))
    assert all(row["verdict"].startswith("REFUSED") for row in e347.judge(_reading(_run(0.05), fam=(0.0,))))


def test_the_field_diff_reads_only_the_shared_keys():
    src = {"config": {"circuit_size": 800, "repeats": 5, "lam": 0.003, "only_in_source": 1}}
    new = {"config": {"circuit_size": 300, "repeats": 20, "lam": 0.003, "only_in_new": 2}}
    d = e347.field_diff(src, new)
    assert d == {"circuit_size": [800, 300], "repeats": [5, 20]}, d
    #: a key only one side carries is not a difference: the derivation cannot set what the source never recorded
    assert "only_in_source" not in d and "only_in_new" not in d, d
    assert e347.field_diff(src, src) == {}, e347.field_diff(src, src)


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e347_the_family_that_disagrees.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e347.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    t1 = d["claims"][0]["verdict"]
    assert t1.startswith(("MET", "FALSIFIER")), t1
    if t1.startswith("FALSIFIER"):
        #: the one field the derivation set that this run moved on purpose is the arm list, narrowed to the two arms
        #: the contrast is about; everything else that differs is the budget and the replicate count
        assert "methods" in t1, t1
    assert d["new"]["circuit_size"] == 300 and d["new"]["repeats"] == 20, d["new"]
    assert set(d["field_diff"]) <= set(e347.ALLOWED) | {"methods"}, d["field_diff"]
    assert d["field_diff"]["circuit_size"] == [800, 300], d["field_diff"]
    assert d["field_diff"]["repeats"] == [5, 20], d["field_diff"]
    #: the family is the corpus's, it spans both budgets, and the run left the one its members mostly sit at
    assert len(d["family"]) >= 8, len(d["family"])
    assert {row["circuit_size"] for row in d["family"]} == {300, 800}, [r["circuit_size"] for r in d["family"]]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
