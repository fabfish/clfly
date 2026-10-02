"""`e349` asks whether a body can write the cue into its action, so the tests pin the two arms, the unwired read-out
and both faces of the four claims.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e349_the_body_writes_the_cue as e349


def _reading(world=0.52, state=0.99, classes=1, seeds=3, world_step=0.0, state_step=0.0):
    rows = []
    for i in range(seeds):
        w = world + world_step * (i - 1)
        s = state + state_step * (i - 1)
        rows.append({"seed": i, "same_body": True,
                     "arms": {e349.WORLD: {"n_in": 1, "wired_accuracy": w, "unwired_accuracy": 0.25,
                                           "unwired_classes": classes, "chance": 0.25},
                              e349.STATE: {"n_in": 12, "wired_accuracy": s, "unwired_accuracy": s,
                                           "unwired_classes": 4, "chance": 0.25}}})
    wm = sum(r["arms"][e349.WORLD]["wired_accuracy"] for r in rows) / seeds
    sm = sum(r["arms"][e349.STATE]["wired_accuracy"] for r in rows) / seeds
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "n_symbols": 4, "chance": 0.25, "n_train": 96,
            "n_test": 48, "scale": 1.0, "world_leak": 0.35, "world_modes": 2, "lr": 3e-3, "iters": 500, "batch": 32,
            "seeds": list(range(seeds)), "rows": rows, "world_mean": wm, "world_sem": 0.02,
            "state_mean": sm, "state_sem": 0.004, "world_above_chance": wm - 0.25, "state_minus_world": sm - wm}


def _judge(r):
    return {row["id"]: row for row in e349.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading())
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T2: a body that cannot write the cue at all, and one that writes it too weakly to call
    assert _judge(_reading(world=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(world=0.32))["T2"]["verdict"].startswith("NULL")
    # T3: an unwired read-out that still separates the examples is a leak, not a result
    assert _judge(_reading(classes=3))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: the world arm ahead of the state arm is the surprising side
    assert _judge(_reading(world=0.99, state=0.90))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(world=0.99, state=0.95))["T4"]["verdict"].startswith("MET")
    # fewer than two seeds refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e349.judge(_reading(seeds=1)))


def test_a_constant_world_is_read_as_one_class():
    #: the unwired reading is the head's own constant prediction: the world at rest, the same input on every example
    r = _reading(classes=1)
    assert r["rows"][0]["arms"][e349.WORLD]["unwired_classes"] == 1, r["rows"][0]
    assert _judge(r)["T3"]["verdict"].startswith("MET"), _judge(r)["T3"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e349_the_body_writes_the_cue.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e349.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the training landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the two arms read one number and twelve, and everything else is shared by construction
    assert d["rows"][0]["arms"][e349.WORLD]["n_in"] == 1, d["rows"][0]
    assert d["rows"][0]["arms"][e349.STATE]["n_in"] > 1, d["rows"][0]
    assert len(d["rows"]) >= 3, len(d["rows"])
    #: every unwired reading is a single class, and the means are the rows' own
    assert all(r["arms"][e349.WORLD]["unwired_classes"] == 1 for r in d["rows"]), d["rows"]
    assert abs(d["world_mean"] - sum(r["arms"][e349.WORLD]["wired_accuracy"] for r in d["rows"])
               / len(d["rows"])) < 1e-12, d["world_mean"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
