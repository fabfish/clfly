"""`e350` asks whether the earned label's price was the carrier's width, so the tests pin the three arms, the
shared-field check and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e350_the_world_gets_a_dimension as e350


def _reading(w1=0.52, w8=0.99, state=1.00, seeds=3, shared=None):
    rows = []
    for i in range(seeds):
        rows.append({"seed": i, "chance": 0.25,
                     "shared": shared if shared is not None else
                     {"cue_sha1": 1, "action_sha1": 1, "feedback_sha1": 1, "world_leak": 1},
                     "arms": {e350.W1: {"n_in": 1, "wired_accuracy": w1, "unwired_accuracy": 0.25,
                                        "unwired_classes": 1},
                              e350.W8: {"n_in": 8, "wired_accuracy": w8, "unwired_accuracy": 0.25,
                                        "unwired_classes": 1},
                              e350.STATE: {"n_in": 12, "wired_accuracy": state, "unwired_accuracy": state,
                                           "unwired_classes": 4}}})
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "n_symbols": 4, "chance": 0.25, "n_train": 96,
            "n_test": 48, "world_leak": 0.35, "lr": 3e-3, "iters": 500, "batch": 32, "world_dims": 8,
            "seeds": list(range(seeds)), "rows": rows,
            f"{e350.W1}_mean": w1, f"{e350.W1}_sem": 0.02,
            f"{e350.W8}_mean": w8, f"{e350.W8}_sem": 0.005,
            f"{e350.STATE}_mean": state, f"{e350.STATE}_sem": 0.004,
            "w8_above_chance": w8 - 0.25, "w8_minus_w1": w8 - w1, "state_minus_w8": state - w8}


def _judge(r):
    return {row["id"]: row for row in e350.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading())
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a population fingerprint that is not shared across the arms
    assert _judge(_reading(shared={"cue_sha1": 2, "action_sha1": 1, "feedback_sha1": 1,
                                   "world_leak": 1}))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a vector world that is not learnable, and one that is too weak to call
    assert _judge(_reading(w8=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(w8=0.32))["T2"]["verdict"].startswith("NULL")
    # T3: the dimension buying nothing, and buying too little to call
    assert _judge(_reading(w1=0.52, w8=0.53))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(w1=0.52, w8=0.56))["T3"]["verdict"].startswith("NULL")
    # T4: eight numbers that do not close it, and a lead too small to call either
    assert _judge(_reading(w1=0.50, w8=0.70, state=1.00))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(w1=0.50, w8=0.90, state=1.00))["T4"]["verdict"].startswith("NULL")
    # fewer than two seeds refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e350.judge(_reading(seeds=1)))


def test_the_shared_fields_are_read_off_the_arms():
    #: the record carries the four fields T1 rests on, and one distinct value each means one world
    r = _reading()
    assert set(r["rows"][0]["shared"]) == {"cue_sha1", "action_sha1", "feedback_sha1", "world_leak"}, r["rows"][0]
    assert all(v == 1 for v in r["rows"][0]["shared"].values()), r["rows"][0]
    assert _judge(r)["T1"]["verdict"].startswith("MET"), _judge(r)["T1"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e350_the_world_gets_a_dimension.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e350.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the training landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the three arms read one, eight and twelve numbers, and the vector world is the one with a drive map
    a = d["rows"][0]["arms"]
    assert a[e350.W1]["n_in"] == 1 and a[e350.W8]["n_in"] == d["world_dims"], a
    assert a[e350.W1]["world_drive_sha1"] is None, a[e350.W1]
    assert a[e350.W8]["world_drive_sha1"] and a[e350.W8]["world_read_sha1"], a[e350.W8]
    #: every arm's unwired world read-out is a single class, and the means are the rows' own
    assert all(r["arms"][e350.W8]["unwired_classes"] == 1 for r in d["rows"]), d["rows"]
    assert abs(d[f"{e350.W8}_mean"] - sum(r["arms"][e350.W8]["wired_accuracy"] for r in d["rows"])
               / len(d["rows"])) < 1e-12, d[f"{e350.W8}_mean"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
