"""`e352` puts the earned-label task in a sequence, so the tests pin the two arms' shared world, the retention
matrix's shape, the forgetting arithmetic and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e352_the_earned_label_suite as e352


def _row(arm, diag=0.80, forget=0.33, seed=0, world_dims=8):
    return {"seed": seed, "arm": arm, "chance": 0.25, "diagonal_mean": diag, "mean_forgetting": forget,
            "final": [0.5, 0.6, 0.8], "n_buffer": 2 if arm == e352.REPLAY else 0,
            "retention": [[0.8, None, None], [0.4, 0.8, None], [0.3, 0.5, 0.8]],
            "world_dims": world_dims, "world_drive_sha1": "d", "world_read_sha1": "r", "world_leak": 0.35,
            "cue_sha1": "c", "action_sha1": "a", "feedback_sha1": "f"}


def _reading(rows, seeds=3):
    rows = rows if rows is not None else ([_row(e352.NAIVE, seed=i) for i in range(seeds)]
                                          + [_row(e352.REPLAY, diag=0.78, forget=0.11, seed=i) for i in range(seeds)])
    def mean(arm, field):
        vals = [r[field] for r in rows if r["arm"] == arm]
        return sum(vals) / len(vals) if vals else None
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "n_tasks": 3, "n_classes": 4,
            "chance": 0.25, "n_train": 96, "n_test": 48, "world_dims": 8, "world_leak": 0.35, "lr": 3e-3,
            "iters": 500, "batch": 32, "seeds": sorted({r["seed"] for r in rows}), "rows": rows,
            f"{e352.NAIVE}_diagonal_mean": mean(e352.NAIVE, "diagonal_mean"),
            f"{e352.REPLAY}_diagonal_mean": mean(e352.REPLAY, "diagonal_mean"),
            f"{e352.NAIVE}_mean_forgetting": mean(e352.NAIVE, "mean_forgetting"),
            f"{e352.NAIVE}_mean_forgetting_sem": 0.0575,
            f"{e352.REPLAY}_mean_forgetting": mean(e352.REPLAY, "mean_forgetting"),
            f"{e352.REPLAY}_mean_forgetting_sem": 0.0397,
            "replay_minus_naive_forgetting": (
                (mean(e352.REPLAY, "mean_forgetting") - mean(e352.NAIVE, "mean_forgetting"))
                if mean(e352.REPLAY, "mean_forgetting") is not None
                and mean(e352.NAIVE, "mean_forgetting") is not None else None)}


def _judge(r):
    return {row["id"]: row for row in e352.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading(None))
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a world fingerprint that is not shared across the arms
    rows = [_row(e352.NAIVE), _row(e352.REPLAY)]
    rows[1]["world_read_sha1"] = "other"
    assert _judge(_reading(rows))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a suite that is not learned, and one learned too weakly to call
    assert _judge(_reading([_row(e352.NAIVE, diag=0.26, forget=0.33), _row(e352.REPLAY, diag=0.26,
                                                                           forget=0.11)]))["T2"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(_reading([_row(e352.NAIVE, diag=0.33, forget=0.33), _row(e352.REPLAY, diag=0.33,
                                                                           forget=0.11)]))["T2"][
        "verdict"].startswith("NULL")
    # T3: a suite that holds the world by itself has nothing to fix, and one between the bars is unresolved
    assert _judge(_reading([_row(e352.NAIVE, forget=0.01), _row(e352.REPLAY, forget=0.0)]))["T3"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(_reading([_row(e352.NAIVE, forget=0.03), _row(e352.REPLAY, forget=0.03)]))["T3"][
        "verdict"].startswith("NULL")
    # T4: a buffer that makes forgetting worse, and one whose effect is too small to call
    assert _judge(_reading([_row(e352.NAIVE, forget=0.10), _row(e352.REPLAY, forget=0.20)]))["T4"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(_reading([_row(e352.NAIVE, forget=0.20), _row(e352.REPLAY, forget=0.19)]))["T4"][
        "verdict"].startswith("NULL")
    # one arm alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e352.judge(_reading([_row(e352.NAIVE)])))


def test_the_retention_matrix_is_the_shape_the_metric_needs():
    #: the diagonal is learned and the lower-left block is the forgetting the last row measures
    r = _reading(None)
    ret = r["rows"][0]["retention"]
    assert len(ret) == e352.N_TASKS and all(len(row) == e352.N_TASKS for row in ret), ret
    assert all(ret[i][i] is not None for i in range(e352.N_TASKS)), ret
    #: above the diagonal is not measured, which is what a sequential run gives
    assert ret[0][1] is None and ret[0][2] is None and ret[1][2] is None, ret


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e352_the_earned_label_suite.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e352.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the training landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: both arms are present per seed, and the world is one world across them
    assert {r["arm"] for r in d["rows"]} == set(e352.ARMS), d["rows"]
    assert len({r["world_read_sha1"] for r in d["rows"]}) == 1, d["rows"]
    assert all(len(r["retention"]) == d["n_tasks"] for r in d["rows"]), d["rows"]
    #: the buffer is the one difference, and the arms' diagonal means are the rows' own
    assert all((r["n_buffer"] > 0) == (r["arm"] == e352.REPLAY) for r in d["rows"]), d["rows"]
    assert abs(d[f"{e352.NAIVE}_diagonal_mean"]
               - sum(r["diagonal_mean"] for r in d["rows"] if r["arm"] == e352.NAIVE)
               / len(d["seeds"])) < 1e-12, d
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
