"""`e365` trains the cell where the frozen probe saw signal, so the tests pin the two-artifact configuration check,
the probe comparison and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e365_the_interface_knob_as_a_task as e365


def _run(cue_step=10, diag=0.90, forget=0.35, replay_forget=0.09, channel=0.30, reps=20,
         coupling=e365.COUPLING_SHA1, seed0=0, tasks=3, drive_from_cue=True):
    payload = {
        "config": {"loop_cue_at": cue_step, "loop_drive_from_cue": drive_from_cue, "loop_world_leak": 0.35,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": 8,
                   "loop_world_modes": 0, "closed_loop": True, "repeats": reps, "circuit_size": 300,
                   "readout_size": 32, "basis": "cell_class", "seed0": seed0},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "d", "world_read_sha1": "r", "world_leak": 0.35,
                     "world_coupled": True, "world_coupling_sha1": coupling, "world_nonlinear": False,
                     "drive_from_cue": drive_from_cue, "cue_at": cue_step,
                     "cue_sha1": "c", "action_sha1": "c" if drive_from_cue else "a", "feedback_sha1": "f"},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {},
    }
    for arm in e365.ARMS:
        forget_arm = forget if arm == e365.NAIVE else replay_forget
        reps_list = []
        for r in range(reps):
            wobble = 0.001 * ((r % 5) - 2)
            reps_list.append({
                "final_accuracy": diag + wobble, "mean_forgetting": forget_arm + wobble,
                "learned": [diag + wobble] * tasks, "forgetting_per_task": [forget_arm] * (tasks - 1),
                "final_per_task": [diag] * tasks,
                "retention": [[diag if i == j else None for j in range(tasks)] for i in range(tasks)],
                "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel + wobble,
                                    "without_loop": 0.5 + wobble} for j in range(tasks)]})
        payload["methods"][arm] = {"final_accuracy": diag, "final_sem": 0.01, "mean_forgetting": forget_arm,
                                   "forgetting_sem": 0.01, "learned": [diag] * tasks, "replicates": reps_list}
    return payload


def _frozen(accuracy=0.8555, source="cue", step=10):
    return {"cells": [{"source": source, "cue_at": step, "accuracy": accuracy, "chance": 0.25},
                      {"source": source, "cue_at": 11, "accuracy": 0.2578, "chance": 0.25}]}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(read=None, ten=None, frozen=None):
    read = read if read is not None else _run(cue_step=11, diag=0.23)
    ten = ten if ten is not None else _run(cue_step=10, diag=0.90)
    frozen = frozen if frozen is not None else _frozen(0.8555)
    return {row["id"]: row
            for row in e365.judge(e365.reading(read_path=_write(read), ten_path=_write(ten),
                                               frozen_path=_write(frozen)))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a cue step that was not moved, a different coupling, a different drive source, fewer replicates
    assert _judge(ten=_run(cue_step=11, diag=0.90))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(ten=_run(cue_step=10, coupling="other", diag=0.90))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(ten=_run(cue_step=10, drive_from_cue=False, diag=0.90))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(ten=_run(cue_step=10, reps=5, diag=0.90))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a knob a trained body cannot use, and one it uses too weakly to call
    assert _judge(ten=_run(cue_step=10, diag=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(ten=_run(cue_step=10, diag=0.33))["T2"]["verdict"].startswith("NULL")
    # T3: an arm whose answer is not earned
    assert _judge(ten=_run(cue_step=10, diag=0.90, channel=0.01))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: training that threw away what the probe read
    assert _judge(ten=_run(cue_step=10, diag=0.60), frozen=_frozen(0.8555))["T4"]["verdict"].startswith("FALSIFIER")
    # T5: a buffer that makes the cue-at-ten suite worse, and one whose effect is too small to call
    assert _judge(ten=_run(cue_step=10, diag=0.90, replay_forget=0.60))["T5"]["verdict"].startswith("FALSIFIER")
    assert _judge(ten=_run(cue_step=10, diag=0.90, replay_forget=0.36))["T5"]["verdict"].startswith("NULL")
    # the cue-at-ten run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e365.judge(e365.reading(read_path=_write(_run(cue_step=11)),
                                                  ten_path=Path("runs/does_not_exist.json"),
                                                  frozen_path=_write(_frozen()))))


def test_the_frozen_cell_is_read_off_its_own_artifact():
    cell = e365.frozen_cell(_write(_frozen(0.8555, source="cue", step=10)))
    assert cell and abs(cell["accuracy"] - 0.8555) < 1e-12, cell
    #: another step of the same source is a different cell, and another source is not this configuration
    assert e365.frozen_cell(_write(_frozen(0.2578, source="cue", step=11))) is None
    assert e365.frozen_cell(_write(_frozen(0.66, source="action", step=10))) is None
    assert e365.frozen_cell(Path("runs/does_not_exist.json")) is None


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e365_the_interface_knob_as_a_task.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e365.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["facts"]["ten"]["loop_cue_at"] == e365.CUE_STEP, d["facts"]
    assert d["facts"]["read"]["loop_cue_at"] == e365.CUE_STEP + 1, d["facts"]
    #: both runs are cue-source, so the drive maps have the same width and the couplings agree
    assert d["facts"]["ten"]["world_coupling_sha1"] == d["facts"]["read"]["world_coupling_sha1"], d["facts"]
    for key in (f"ten_{e365.NAIVE}", f"ten_{e365.REPLAY}"):
        assert d["rows"][key]["n"] == e365.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
