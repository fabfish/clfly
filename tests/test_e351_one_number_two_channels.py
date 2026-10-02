"""`e351` asks whether `e350`'s gain was the world's dimension or its channel's shape, so the tests pin the three
arms, the shared-field check and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e351_one_number_two_channels as e351


def _reading(scalar=0.52, dim1=0.58, dim8=0.99, seeds=3, shared=None, classes=None):
    rows = []
    for i in range(seeds):
        rows.append({"seed": i, "chance": 0.25,
                     "shared": shared if shared is not None else
                     {"cue_sha1": 1, "action_sha1": 1, "feedback_sha1": 1, "world_leak": 1},
                     "arms": {a: {"n_in": 1 if a != e351.DIM8 else 8, "wired_accuracy": v,
                                  "unwired_accuracy": 0.25, "unwired_classes": (classes or {}).get(a, 1)}
                              for a, v in ((e351.SCALAR, scalar), (e351.DIM1, dim1), (e351.DIM8, dim8))}})
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "n_symbols": 4, "chance": 0.25, "n_train": 96,
            "n_test": 48, "world_leak": 0.35, "lr": 3e-3, "iters": 500, "batch": 32,
            "dims": {e351.SCALAR: 0, e351.DIM1: 1, e351.DIM8: 8}, "seeds": list(range(seeds)), "rows": rows,
            f"{e351.SCALAR}_mean": scalar, f"{e351.SCALAR}_sem": 0.02,
            f"{e351.DIM1}_mean": dim1, f"{e351.DIM1}_sem": 0.03,
            f"{e351.DIM8}_mean": dim8, f"{e351.DIM8}_sem": 0.005,
            "dim1_minus_scalar": dim1 - scalar,
            "width_buys": dim8 - max(scalar, dim1),
            "above_chance": {a: v - 0.25 for a, v in ((e351.SCALAR, scalar), (e351.DIM1, dim1),
                                                      (e351.DIM8, dim8))}}


def _judge(r):
    return {row["id"]: row for row in e351.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading(dim1=0.55))
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a population fingerprint that is not shared across the arms
    assert _judge(_reading(dim1=0.55, shared={"cue_sha1": 2, "action_sha1": 1, "feedback_sha1": 1,
                                              "world_leak": 1}))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a shape that buys 0.10 or more would make the width incidental, and one between is unresolved
    assert _judge(_reading(scalar=0.50, dim1=0.65))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(scalar=0.50, dim1=0.58))["T2"]["verdict"].startswith("NULL")
    # T3: the width buying nothing, and buying too little to call
    assert _judge(_reading(dim1=0.99, dim8=0.99))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(scalar=0.50, dim1=0.50, dim8=0.54))["T3"]["verdict"].startswith("NULL")
    # T4: an arm at chance, and an unwired read-out that still separates the examples
    assert _judge(_reading(scalar=0.26))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(dim1=0.55, classes={e351.DIM1: 3}))["T4"]["verdict"].startswith("FALSIFIER")
    # fewer than two seeds refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e351.judge(_reading(seeds=1)))


def test_the_two_one_number_arms_differ_only_in_the_channel():
    #: the record carries the four fields T1 rests on for every arm, and one distinct value each means one world
    r = _reading()
    assert set(r["rows"][0]["shared"]) == {"cue_sha1", "action_sha1", "feedback_sha1", "world_leak"}, r["rows"][0]
    assert all(v == 1 for v in r["rows"][0]["shared"].values()), r["rows"][0]
    assert _judge(r)["T1"]["verdict"].startswith("MET"), _judge(r)["T1"]
    #: the width buys against the BETTER one-number arm, which is what the claim says
    better = _reading(scalar=0.40, dim1=0.60, dim8=0.70)["width_buys"]
    assert abs(better - 0.10) < 1e-12, better


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e351_one_number_two_channels.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e351.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the training landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the three arms are one, one and eight numbers, over worlds of zero, one and eight dimensions
    for arm, dims in d["dims"].items():
        for row in d["rows"]:
            assert row["arms"][arm]["world_dims"] == dims, (arm, row["arms"][arm])
    assert d["rows"][0]["arms"][e351.SCALAR]["world_drive_sha1"] is None, d["rows"][0]
    assert d["rows"][0]["arms"][e351.DIM1]["world_drive_sha1"], d["rows"][0]
    #: every arm's unwired world read-out is a single class, and the means are the rows' own
    assert all(r["arms"][a]["unwired_classes"] == 1 for r in d["rows"] for a in e351.ARMS), d["rows"]
    assert abs(d[f"{e351.DIM8}_mean"] - sum(r["arms"][e351.DIM8]["wired_accuracy"] for r in d["rows"])
               / len(d["rows"])) < 1e-12, d[f"{e351.DIM8}_mean"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
