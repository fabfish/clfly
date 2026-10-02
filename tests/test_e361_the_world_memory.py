"""`e361` takes the world's memory away, so the tests pin the two-artifact configuration check, the paired diagonal
gap against the memoried world and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e361_the_world_memory as e361


def _run(leak=0.35, diag=0.77, forget=0.375, replay_forget=0.09, channel=0.26, reps=20,
         world=e361.WORLD_READ_SHA1, coupling=e361.COUPLING_SHA1, dims=8, basis="cell_class", seed0=0, tasks=3):
    payload = {
        "config": {"loop_world_leak": leak, "loop_world_coupled": True, "readout_from_world": True,
                   "loop_world_dims": dims, "loop_world_modes": 0, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": seed0},
        "env_draw": {"world_dims": dims, "world_drive_sha1": "d", "world_read_sha1": world, "world_leak": leak,
                     "world_coupled": True, "world_coupling_sha1": coupling, "world_nonlinear": False,
                     "cue_sha1": "c", "action_sha1": "a", "feedback_sha1": "f"},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": dims} for i in range(tasks)],
        "methods": {},
    }
    for arm in e361.ARMS:
        forget_arm = forget if arm == e361.NAIVE else replay_forget
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


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(memory=None, instant=None):
    memory = memory if memory is not None else _run(leak=0.35, diag=0.77)
    instant = instant if instant is not None else _run(leak=1.0, diag=0.60)
    return {row["id"]: row
            for row in e361.judge(e361.reading(memory_path=_write(memory), instant_path=_write(instant)))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a leak that was not moved, a different coupling, a different world, and too few replicates
    assert _judge(instant=_run(leak=0.35, diag=0.60))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(instant=_run(leak=1.0, coupling="other", diag=0.60))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(instant=_run(leak=1.0, world="other", diag=0.60))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(instant=_run(leak=1.0, seed0=9, diag=0.60))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(instant=_run(leak=1.0, reps=5, diag=0.60))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: an instant world a body cannot learn in, and one learnable too weakly to call
    assert _judge(instant=_run(leak=1.0, diag=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(instant=_run(leak=1.0, diag=0.33))["T2"]["verdict"].startswith("NULL")
    # T3: an instant arm whose answer is not earned
    assert _judge(instant=_run(leak=1.0, diag=0.60, channel=0.01))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: a world whose memory is worth nothing, and one between the bars
    assert _judge(memory=_run(leak=0.35, diag=0.61), instant=_run(leak=1.0, diag=0.60))["T4"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(memory=_run(leak=0.35, diag=0.63), instant=_run(leak=1.0, diag=0.60))["T4"][
        "verdict"].startswith("NULL")
    # T5: a buffer that makes the instant suite worse, and one whose effect is too small to call
    assert _judge(instant=_run(leak=1.0, diag=0.60, replay_forget=0.60))["T5"]["verdict"].startswith("FALSIFIER")
    assert _judge(instant=_run(leak=1.0, diag=0.60, replay_forget=0.36))["T5"]["verdict"].startswith("NULL")
    # the no-memory run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e361.judge(e361.reading(memory_path=_write(_run(leak=0.35)),
                                                  instant_path=Path("runs/does_not_exist.json"))))


def test_the_gap_is_paired_and_the_buffer_value_is_a_within_run_contrast():
    r = e361.reading(memory_path=_write(_run(leak=0.35, diag=0.77)),
                     instant_path=_write(_run(leak=1.0, diag=0.60, forget=0.40, replay_forget=0.10)))
    est = r["diagonal_gap"]
    assert est["n"] == 20, est
    #: the memory's value is the per-replicate difference of the two worlds' `naive` diagonals
    assert abs(est["delta"] - 0.17) < 1e-9, est
    assert all(abs(v - 0.17) < 1e-9 for v in est["vals"]), est["vals"]
    #: the buffer's value is read inside the instant run
    assert r["instant_buffer"]["n"] == 20, r["instant_buffer"]
    assert abs(r["instant_buffer"]["delta"] - (-0.30)) < 1e-9, r["instant_buffer"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e361_the_world_memory.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e361.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["facts"]["instant"]["loop_world_leak"] == e361.INSTANT_LEAK, d["facts"]
    assert d["facts"]["memory"]["loop_world_leak"] == e361.MEMORY_LEAK, d["facts"]
    assert d["facts"]["instant"]["world_coupling_sha1"] == d["facts"]["memory"]["world_coupling_sha1"], d["facts"]
    for key in (f"instant_{e361.NAIVE}", f"instant_{e361.REPLAY}"):
        assert d["rows"][key]["n"] == e361.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
