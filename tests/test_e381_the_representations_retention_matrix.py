"""`e381` reads the retention matrix off the bodies `e379` and `e380` saved, so the tests pin both faces of the five
claims, the refusal when a reader or the weights are absent, and the live matrices' own shape.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e381_the_representations_retention_matrix as e381


def _entry(cue_at=0, reps=20, diagonal=(0.77, 0.78, 0.81), initial=(0.69, 0.63, 0.71),
           head_drop=(0.30, 0.20, 0.15), recorded=0.78, last_drop=0.24, replay_last_drop=0.06):
    """A run's entry: the matrix cells per checkpoint and task, and the head's own rows."""
    arms = {}
    for arm in e381.ARMS:
        last = last_drop if arm == e381.NAIVE or replay_last_drop is None else replay_last_drop
        cells = {}
        for k in range(e381.N_TASKS):
            cells[f"initial|{k}"] = [initial[k]] * reps
            cells[f"after_task_0|{k}"] = [diagonal[0] if k == 0 else initial[k]] * reps
            cells[f"after_task_1|{k}"] = [diagonal[1] if k == 1 else initial[k]] * reps
            cells[f"after_task_2|{k}"] = [diagonal[k] - (0.0 if k == 2 else last)] * reps
        arms[arm] = cells
    head_rows = {}
    for arm in e381.ARMS:
        drops = head_drop if arm == e381.NAIVE else tuple(d * 0.3 for d in head_drop)
        rows = []
        for j in range(e381.N_TASKS):
            rows.append([[None] * e381.N_TASKS for _ in range(reps)])
        for k in range(e381.N_TASKS):
            for i in range(reps):
                rows[k][i][k] = diagonal[k]
                rows[2][i][k] = diagonal[k] - drops[k]
        head_rows[arm] = rows
    return {"cue_at": cue_at, "run": "r.json", "reader": "d.json", "replicates": reps, "arms": arms,
            "head": {e381.NAIVE: [[diagonal[k] for k in range(e381.N_TASKS)]] * e381.N_TASKS}, "head_rows": head_rows,
            "recorded": {"naive": recorded, "replay": recorded}}


def _judge(wide=None, tight=None, ok=True, reason="absent"):
    if not ok:
        return {row["id"]: row for row in e381.judge({"ok": False, "reason": reason, "runs": {}})}
    return {row["id"]: row for row in e381.judge(
        {"ok": True, "runs": {"wide": wide or _entry(cue_at=0), "tight": tight or _entry(cue_at=8, diagonal=(0.21, 0.21, 0.29), initial=(0.69, 0.65, 0.65), recorded=0.2361, last_drop=0.0, head_drop=(0.0, 0.0, 0.0))}})}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("R1", "R2", "R3", "R4", "R5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # R1: a diagonal that is not what the units recorded, and a null between the bars
    assert _judge(wide=_entry(recorded=0.60))["R1"]["verdict"].startswith("FALSIFIER")
    assert _judge(wide=_entry(recorded=0.74))["R1"]["verdict"].startswith("NULL")

    # R2: a representation that keeps its task, and one whose loss is too small to call
    assert _judge(wide=_entry(last_drop=0.01))["R2"]["verdict"].startswith("FALSIFIER")
    assert _judge(wide=_entry(last_drop=0.07))["R2"]["verdict"].startswith("NULL")

    # R3: a world whose drop is far below the head's, and one that is only slightly below
    assert _judge(wide=_entry(last_drop=0.10))["R3"]["verdict"].startswith("FALSIFIER")
    assert _judge(wide=_entry(last_drop=0.18))["R3"]["verdict"].startswith("NULL")

    # R4: a tight step that still moves its task-0 representation
    assert _judge(tight=_entry(cue_at=8, diagonal=(0.21, 0.21, 0.29), last_drop=0.30))["R4"][
        "verdict"].startswith("FALSIFIER")

    # R5: a buffer that makes the world forget more
    assert _judge(wide=_entry(last_drop=0.24, replay_last_drop=0.40))["R5"]["verdict"].startswith("FALSIFIER")

    #: the runs or their weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e381.judge({"ok": False, "runs": {}}))


def test_the_head_drop_is_keyed_by_arm():
    """The bug this unit's first reading had: a per-arm field written without a key leaves the last arm behind."""
    wide = _entry(head_drop=(0.30, 0.20, 0.15))
    assert abs(e381.statistics.fmean(e381._head_drop(wide, e381.NAIVE, 0)) - 0.30) < 1e-9
    assert abs(e381.statistics.fmean(e381._head_drop(wide, e381.REPLAY, 0)) - 0.09) < 1e-9
    #: and the two arms' drops are not the same list
    assert e381._head_drop(wide, e381.NAIVE, 0) != e381._head_drop(wide, e381.REPLAY, 0)


def test_the_live_matrices_have_the_shape_the_line_measured():
    p = Path("runs/e381_the_representations_retention_matrix.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e381.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e381.judge(d)}
    for cid in ("R1", "R2", "R4", "R5"):
        assert verdicts[cid].startswith("MET"), (cid, verdicts[cid])
    assert verdicts["R3"].startswith("FALSIFIER"), verdicts["R3"]
    #: the wide step's diagonal rises as its off-diagonal falls, and the tight step's matrix is frozen
    wide, tight = d["runs"]["wide"], d["runs"]["tight"]
    diag = [round(e381.statistics.fmean(wide["arms"][e381.NAIVE][f"after_task_{k}|{k}"]), 4) for k in range(3)]
    assert diag[0] < diag[2], diag
    t0 = [round(e381.statistics.fmean(tight["arms"][e381.NAIVE][f"{c}|0"]), 4)
          for c in ("after_task_0", "after_task_1", "after_task_2")]
    assert t0[0] == t0[1] == t0[2], t0
    #: the head's rows are keyed by arm and not shared
    assert set(d["runs"]["wide"]["head_rows"]) == set(e381.ARMS), sorted(d["runs"]["wide"]["head_rows"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
