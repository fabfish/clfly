"""`e355` reads the earned label out of the corpus's own runner, so the tests pin the extraction from the runner's
schema, the paired channel reading and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e355_the_earned_label_through_the_runner as e355


def _run(arms=e355.ARMS, reps=3, world_dims=8, readout_from_world=True, closed=True, diagonal=0.80, forget=0.35,
         channel=(0.30, 0.04), tasks=3, n_classes=4, widths=None, buffer=-0.25):
    payload = {
        "config": {"readout_from_world": readout_from_world, "loop_world_dims": world_dims,
                   "loop_world_leak": 0.35, "loop_world_modes": 0, "closed_loop": closed, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32},
        "env_draw": {"world_dims": world_dims, "world_drive_sha1": "d", "world_read_sha1": "r"},
        "tasks": [{"name": f"loop_t{i}", "n_classes": n_classes,
                   "n_readout": (world_dims if widths is None else widths[i])} for i in range(tasks)],
        "methods": {},
    }
    for a in arms:
        reps_list = []
        for r in range(reps):
            wobble = (r % 3) - 1
            d = diagonal + 0.01 * wobble
            f = forget + 0.01 * wobble + (0.0 if a != e355.REPLAY else buffer - 0.02 * wobble)
            reps_list.append({
                "final_accuracy": d, "mean_forgetting": f, "learned": [d] * tasks,
                "forgetting_per_task": [f] * (tasks - 1), "final_per_task": [d] * tasks,
                "retention": [[d if i == j else None for j in range(tasks)] for i in range(tasks)],
                "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel[0] + 0.01 * wobble,
                                    "without_loop": 0.5 - channel[1]} for j in range(tasks)],
            })
        payload["methods"][a] = {"final_accuracy": diagonal, "final_sem": 0.01, "mean_forgetting": forget,
                                 "forgetting_sem": 0.01, "learned": [diagonal] * tasks, "replicates": reps_list}
    return payload


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(payload):
    return {row["id"]: row for row in e355.judge(e355.reading(path=_write(payload)))}


def test_the_five_claims_read_both_faces():
    j = _judge(_run())
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a run that says it reads the world but does not, and one whose tasks disagree with the flag
    assert _judge(_run(readout_from_world=False))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(world_dims=0))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(widths=[8, 32, 8]))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a suite the runner cannot learn, and one learned too weakly to call
    assert _judge(_run(diagonal=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(diagonal=0.33))["T2"]["verdict"].startswith("NULL")
    # T3: a suite that holds the world by itself
    assert _judge(_run(forget=0.01))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(forget=0.03))["T3"]["verdict"].startswith("NULL")
    # T4: a buffer that makes forgetting worse, and one whose effect is too small to call
    assert _judge(_run(buffer=0.20))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(buffer=-0.03))["T4"]["verdict"].startswith("NULL")
    # T5: a reading that is not positive, and one that is not resolved
    assert _judge(_run(channel=(0.0, 0.0)))["T5"]["verdict"].startswith("FALSIFIER")
    # a missing arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e355.judge(e355.reading(path=_write(_run(arms=("naive", "replay"))))))


def test_the_channel_reading_is_paired_over_tasks_then_replicates():
    r = e355.reading(path=_write(_run(channel=(0.30, 0.04))))
    row = r["rows"]["naive"]
    assert row["ok"] and row["n"] == 3 and row["n_tasks"] == 3, row
    #: the difference is with minus without, averaged over the tasks inside a replicate; the first replicate's
    #: wobble is -1, so the fixture's own arithmetic gives channel[0] + channel[1] - 0.01
    assert abs(row["channel_by_replicate"][0] - (0.30 + 0.04 - 0.01)) < 1e-9, row["channel_by_replicate"]
    assert row["paired"]["n"] == 3, row["paired"]
    #: and the four arms' readings are all in the record
    assert set(r["rows"]) == set(e355.ARMS), r["rows"]


def test_the_live_artifact_carries_the_same_reading():
    r = e355.reading()
    if not Path(e355.RUN).exists():
        return
    p = Path("runs/e355_the_earned_label_through_the_runner.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e355.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["readout_from_world"] and d["world_dims"], d
    assert d["task_readout_widths"] == [int(d["world_dims"])], d["task_readout_widths"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
