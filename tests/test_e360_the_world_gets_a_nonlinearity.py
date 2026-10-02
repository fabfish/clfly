"""`e360` gives the world a saturation, so the tests pin the two-artifact configuration check, the diagonal gap
against the linear coupled world and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e360_the_world_gets_a_nonlinearity as e360


def _run(nonlinear=False, diag=0.72, forget=0.38, replay_forget=0.10, channel=0.27, reps=20,
         world=e360.WORLD_READ_SHA1, coupling=e360.COUPLING_SHA1, dims=8, basis="cell_class", seed0=0, tasks=3):
    payload = {
        "config": {"loop_world_coupled": True, "loop_world_nonlinear": nonlinear, "readout_from_world": True,
                   "loop_world_dims": dims, "loop_world_leak": 0.35, "loop_world_modes": 0, "closed_loop": True,
                   "repeats": reps, "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": seed0},
        "env_draw": {"world_dims": dims, "world_drive_sha1": "d", "world_read_sha1": world,
                     "world_coupled": True, "world_coupling_sha1": coupling, "world_nonlinear": nonlinear,
                     "cue_sha1": "c", "action_sha1": "a", "feedback_sha1": "f"},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": dims} for i in range(tasks)],
        "methods": {},
    }
    for arm in e360.ARMS:
        forget_arm = forget if arm == e360.NAIVE else replay_forget
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


def _judge(linear=None, nonlinear=None):
    linear = linear if linear is not None else _run(nonlinear=False, diag=0.78)
    nonlinear = nonlinear if nonlinear is not None else _run(nonlinear=True, diag=0.70)
    return {row["id"]: row
            for row in e360.judge(e360.reading(linear_path=_write(linear), nonlinear_path=_write(nonlinear)))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a saturation asked for but not recorded, a different coupling, a different world,
    # a different seed stream, and too few replicates
    assert _judge(nonlinear=_run(nonlinear=False, diag=0.70))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(nonlinear=_run(nonlinear=True, coupling="other", diag=0.70))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(nonlinear=_run(nonlinear=True, world="other", diag=0.70))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(nonlinear=_run(nonlinear=True, seed0=9, diag=0.70))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(nonlinear=_run(nonlinear=True, reps=5, diag=0.70))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a saturating world a body cannot learn in, and one learnable too weakly to call
    assert _judge(nonlinear=_run(nonlinear=True, diag=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(nonlinear=_run(nonlinear=True, diag=0.33))["T2"]["verdict"].startswith("NULL")
    # T3: a nonlinear arm whose answer is not earned
    assert _judge(nonlinear=_run(nonlinear=True, diag=0.70, channel=0.01))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: a saturation that changes nothing, and one between the bars
    assert _judge(linear=_run(nonlinear=False, diag=0.70), nonlinear=_run(nonlinear=True, diag=0.70))["T4"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(linear=_run(nonlinear=False, diag=0.78), nonlinear=_run(nonlinear=True, diag=0.75))["T4"][
        "verdict"].startswith("NULL")
    # a saturation that moves it either way counts as not free
    assert _judge(linear=_run(nonlinear=False, diag=0.60), nonlinear=_run(nonlinear=True, diag=0.70))["T4"][
        "verdict"].startswith("MET")
    # T5: a buffer that makes the nonlinear suite worse, and one whose effect is too small to call
    assert _judge(nonlinear=_run(nonlinear=True, diag=0.70, replay_forget=0.60))["T5"]["verdict"].startswith(
        "FALSIFIER")
    assert _judge(nonlinear=_run(nonlinear=True, diag=0.70, replay_forget=0.37))["T5"]["verdict"].startswith("NULL")
    # the nonlinear run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e360.judge(e360.reading(linear_path=_write(_run(nonlinear=False)),
                                                  nonlinear_path=Path("runs/does_not_exist.json"))))


def test_the_gap_is_paired_and_the_buffer_value_is_a_within_run_contrast():
    r = e360.reading(linear_path=_write(_run(nonlinear=False, diag=0.78)),
                     nonlinear_path=_write(_run(nonlinear=True, diag=0.70, forget=0.40, replay_forget=0.10)))
    est = r["diagonal_gap"]
    assert est["n"] == 20, est
    #: the gap is the per-replicate difference of the two worlds' `naive` diagonals
    assert abs(est["delta"] - (-0.08)) < 1e-9, est
    assert all(abs(v + 0.08) < 1e-9 for v in est["vals"]), est["vals"]
    #: the buffer's value is read inside the nonlinear run
    assert r["nonlinear_buffer"]["n"] == 20, r["nonlinear_buffer"]
    assert abs(r["nonlinear_buffer"]["delta"] - (-0.30)) < 1e-9, r["nonlinear_buffer"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e360_the_world_gets_a_nonlinearity.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e360.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["facts"]["nonlinear"]["world_nonlinear"] is True, d["facts"]
    assert d["facts"]["linear"]["world_coupling_sha1"] == d["facts"]["nonlinear"]["world_coupling_sha1"], d["facts"]
    for key in (f"nonlinear_{e360.NAIVE}", f"nonlinear_{e360.REPLAY}"):
        assert d["rows"][key]["n"] == e360.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
