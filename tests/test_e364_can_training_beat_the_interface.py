"""`e364` asks whether a trained body can beat the interface, so the tests pin the two-artifact configuration check,
the frozen-cell comparison and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e364_can_training_beat_the_interface as e364


def _run(drive_from_cue=False, diag=0.26, forget=-0.02, replay_forget=-0.01, channel=0.001, reps=20,
         cue_step=11, coupling=e364.COUPLING_SHA1, seed0=0, tasks=3):
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
    for arm in e364.ARMS:
        forget_arm = forget if arm == e364.NAIVE else replay_forget
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


def _frozen(accuracy=0.2578, source="cue", step=11):
    return {"cells": [{"source": source, "cue_at": step, "accuracy": accuracy, "chance": 0.25},
                      {"source": source, "cue_at": 0, "accuracy": 0.79, "chance": 0.25}]}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(action=None, cue=None, frozen=None):
    action = action if action is not None else _run(drive_from_cue=False)
    cue = cue if cue is not None else _run(drive_from_cue=True)
    frozen = frozen if frozen is not None else _frozen(0.26)
    return {row["id"]: row
            for row in e364.judge(e364.reading(action_path=_write(action), cue_path=_write(cue),
                                               frozen_path=_write(frozen)))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a run that does not flip the drive, a different cue step, a different coupling, fewer replicates
    assert _judge(cue=_run(drive_from_cue=False))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(cue=_run(drive_from_cue=True, cue_step=10))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(cue=_run(drive_from_cue=True, coupling="other"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(cue=_run(drive_from_cue=True, reps=5))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a trained body that learns it after all, and one that gets part of the way
    assert _judge(cue=_run(drive_from_cue=True, diag=0.60))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(cue=_run(drive_from_cue=True, diag=0.33))["T2"]["verdict"].startswith("NULL")
    # T3: an arm whose answer depends on the loop
    assert _judge(cue=_run(drive_from_cue=True, channel=0.20))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: a trained run that moved the cell the probe read at chance
    assert _judge(cue=_run(drive_from_cue=True, diag=0.60), frozen=_frozen(0.26))["T4"][
        "verdict"].startswith("FALSIFIER")
    # T5: a buffer that does something in a task nobody can learn
    assert _judge(cue=_run(drive_from_cue=True, replay_forget=-0.30))["T5"]["verdict"].startswith("FALSIFIER")
    # the cue-source run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e364.judge(e364.reading(action_path=_write(_run(drive_from_cue=False)),
                                                  cue_path=Path("runs/does_not_exist.json"),
                                                  frozen_path=_write(_frozen()))))


def test_the_frozen_cell_is_read_off_its_own_artifact():
    #: the comparison T4 makes is against `e363`'s own recorded cell, not against a restated number
    cell = e364.frozen_cell(_write(_frozen(0.4411, source="cue", step=11)))
    assert cell and abs(cell["accuracy"] - 0.4411) < 1e-12, cell
    assert e364.frozen_cell(_write(_frozen(0.3, source="action", step=11))) is None, "another source is not it"
    assert e364.frozen_cell(Path("runs/does_not_exist.json")) is None


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e364_can_training_beat_the_interface.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e364.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    t1 = d["claims"][0]["verdict"]
    assert t1.startswith(("MET", "FALSIFIER")), t1
    if t1.startswith("FALSIFIER"):
        #: the two runs differ beyond the drive's source: the drive map's width follows the population it reads, so
        #: the coupling draw lands differently too -- named by the verdict rather than excused
        assert "coupling" in t1, t1
    assert d["facts"]["cue"]["drive_from_cue"] is True, d["facts"]
    assert d["facts"]["action"]["action_sha1"] != d["facts"]["action"]["cue_sha1"], d["facts"]
    for key in (f"cue_{e364.NAIVE}", f"cue_{e364.REPLAY}"):
        assert d["rows"][key]["n"] == e364.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
