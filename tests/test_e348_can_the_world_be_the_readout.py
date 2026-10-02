"""`e348` asks what the environment's own state carries, so the tests pin the per-leak row, the four verdicts and
both faces of each claim.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e348_can_the_world_be_the_readout as e348


def _row(leak, world=0.43, state=0.81, sd=0.26, distinct=512, div=0.57):
    return {"leak": leak, "world_accuracy": world, "state_accuracy": state, "world_sd": sd,
            "world_distinct": distinct, "channel_divergence_of_peak": div, "world_mean": 0.0, "peak": 1.0,
            "world_by_symbol": [0.0, 0.1, -0.1, 0.0], "chance": 0.25}


def _reading(rows=None, carried=0.35):
    rows = rows if rows is not None else [_row(0.35), _row(1.0, world=0.41)]
    got = next((x for x in rows if abs(x["leak"] - carried) < 1e-12), None)
    instant = next((x for x in rows if abs(x["leak"] - 1.0) < 1e-12), None)
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "seed": 0, "tau": 12, "n_symbols": 4,
            "chance": 0.25, "n_train": 512, "n_test": 256, "scale": 1.0, "gain": 1.0, "noise": 1.0,
            "world_modes": 2, "leaks": [x["leak"] for x in rows], "carried_leak": carried, "rows": rows,
            "carried_accuracy": got["world_accuracy"] if got else None,
            "carried_state_accuracy": got["state_accuracy"] if got else None,
            "state_minus_world": (got["state_accuracy"] - got["world_accuracy"]) if got else None,
            "carried_minus_instant": ((got["world_accuracy"] - instant["world_accuracy"])
                                      if (got and instant) else None)}


def _judge(r):
    return {row["id"]: row for row in e348.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading())
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a world state that is constant across the symbols
    assert _judge(_reading([_row(0.35, distinct=1), _row(1.0)]))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: the world carrying nothing, and carrying something too little to call
    assert _judge(_reading([_row(0.35, world=0.26), _row(1.0)]))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading([_row(0.35, world=0.32), _row(1.0)]))["T2"]["verdict"].startswith("NULL")
    # T3: carrying the trial costing accuracy
    assert _judge(_reading([_row(0.35, world=0.33), _row(1.0, world=0.41)]))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: the world carrying something the state's own channel does not
    assert _judge(_reading([_row(0.35, state=0.35), _row(1.0)]))["T4"]["verdict"].startswith("FALSIFIER")
    # a carried leak that was not measured refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e348.judge(_reading([_row(1.0)])))


def test_the_endpoint_missing_refuses_only_t3():
    r = _reading([_row(0.35)])
    j = _judge(r)
    assert j["T3"]["verdict"].startswith("REFUSED"), j["T3"]
    assert j["T2"]["verdict"].startswith("MET") and j["T4"]["verdict"].startswith("MET"), j


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e348_can_the_world_be_the_readout.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e348.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the measurement landed; the gate regenerates it
    #: the world is one scalar and the state is the channel's own neurons, and the tables do not mix them
    assert d["readout"] == 32 and d["n_symbols"] == 4 and d["chance"] == 0.25, d
    assert [row["leak"] for row in d["rows"]] == d["leaks"], d["rows"]
    assert d["leaks"][0] == d["carried_leak"], d["leaks"]
    #: every leak's row is a measurement, and the carried one is the row the claims read
    for row in d["rows"]:
        assert 0.0 <= row["world_accuracy"] <= 1.0 and row["world_distinct"] >= 2, row
    assert d["carried_accuracy"] == d["rows"][0]["world_accuracy"], d
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
