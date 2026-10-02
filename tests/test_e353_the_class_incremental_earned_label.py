"""`e353` runs the earned-label suite class-incrementally, so the tests pin the shared head, the world fingerprint
shared with `e352`, the protocol cost and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e353_the_class_incremental_earned_label as e353


def _row(arm, diag=0.80, forget=0.35, seed=0, world="w"):
    return {"seed": seed, "arm": arm, "chance": 0.25, "diagonal_mean": diag, "mean_forgetting": forget,
            "final": [0.3, 0.5, 0.8], "n_buffer": 2 if arm == e353.REPLAY else 0, "shared_head": True,
            "retention": [[0.8, None, None], [0.4, 0.8, None], [0.3, 0.5, 0.8]],
            "world_dims": 8, "world_drive_sha1": "d", "world_read_sha1": world, "world_leak": 0.35,
            "cue_sha1": "c", "action_sha1": "a", "feedback_sha1": "f"}


def _reading(rows=None, seeds=3, cost=0.20, task_world=("w",), other=0.3333):
    if rows is None:
        rows = ([_row(e353.NAIVE, seed=i) for i in range(seeds)]
                + [_row(e353.REPLAY, diag=0.78, forget=0.09, seed=i) for i in range(seeds)])
    def mean(arm, field):
        vals = [r[field] for r in rows if r["arm"] == arm]
        return sum(vals) / len(vals) if vals else None
    this_world = sorted({r["world_read_sha1"] for r in rows})
    other_world = list(task_world) if task_world is not None else None
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "n_tasks": 3, "n_classes": 4,
            "chance": 0.25, "n_symbols": 12, "world_dims": 8, "world_leak": 0.35, "lr": 3e-3, "iters": 500,
            "batch": 32, "seeds": sorted({r["seed"] for r in rows}), "protocol": "class-incremental", "rows": rows,
            f"{e353.NAIVE}_diagonal_mean": mean(e353.NAIVE, "diagonal_mean"),
            f"{e353.REPLAY}_diagonal_mean": mean(e353.REPLAY, "diagonal_mean"),
            f"{e353.NAIVE}_mean_forgetting": mean(e353.NAIVE, "mean_forgetting"),
            f"{e353.REPLAY}_mean_forgetting": mean(e353.REPLAY, "mean_forgetting"),
            "replay_minus_naive_forgetting": (mean(e353.REPLAY, "mean_forgetting")
                                              - mean(e353.NAIVE, "mean_forgetting"))
            if mean(e353.REPLAY, "mean_forgetting") is not None
            and mean(e353.NAIVE, "mean_forgetting") is not None else None,
            "task_incremental_naive_forgetting": other, "protocol_cost": cost if other is not None else None,
            "this_world_sha1": this_world,
            "task_incremental_world_sha1": other_world,
            "same_world_as_task_incremental": (this_world == other_world) if other_world is not None else None}


def _judge(r):
    return {row["id"]: row for row in e353.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading())
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a world that is not the task-incremental suite's, and a fingerprint not shared across the arms
    assert _judge(_reading(task_world=("other",)))["T1"]["verdict"].startswith("FALSIFIER")
    rows = [_row(e353.NAIVE), _row(e353.REPLAY)]
    rows[1]["world_read_sha1"] = "other"
    assert _judge(_reading(rows))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a suite that is not learned, and one learned too weakly to call
    assert _judge(_reading([_row(e353.NAIVE, diag=0.26), _row(e353.REPLAY, diag=0.26)]))["T2"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(_reading([_row(e353.NAIVE, diag=0.33), _row(e353.REPLAY, diag=0.33)]))["T2"][
        "verdict"].startswith("NULL")
    # T3: the shared head costing nothing, costing a little, and the artifact being absent
    assert _judge(_reading(cost=0.01))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(cost=0.0208))["T3"]["verdict"].startswith("NULL")
    assert _judge(_reading(cost=0.20))["T3"]["verdict"].startswith("MET")
    assert _judge(_reading(other=None))["T3"]["verdict"].startswith("REFUSED")
    # T4: a buffer that makes it worse, and one whose effect is too small to call
    assert _judge(_reading([_row(e353.NAIVE, forget=0.10), _row(e353.REPLAY, forget=0.20)]))["T4"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(_reading([_row(e353.NAIVE, forget=0.20), _row(e353.REPLAY, forget=0.19)]))["T4"][
        "verdict"].startswith("NULL")
    # one arm alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e353.judge(_reading([_row(e353.NAIVE)])))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e353_the_class_incremental_earned_label.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e353.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the training landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the protocol is the class-incremental one, and both arms are present per seed over one shared head
    assert d["protocol"] == "class-incremental", d["protocol"]
    assert {r["arm"] for r in d["rows"]} == set(e353.ARMS), d["rows"]
    assert all(r["shared_head"] for r in d["rows"]), d["rows"]
    assert len({r["world_read_sha1"] for r in d["rows"]}) == 1, d["rows"]
    #: the buffer is the one difference, and the retention blocks are the shape the metric needs
    assert all((r["n_buffer"] > 0) == (r["arm"] == e353.REPLAY) for r in d["rows"]), d["rows"]
    assert all(len(r["retention"]) == d["n_tasks"] for r in d["rows"]), d["rows"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
