"""`e359` pairs a world with its own dynamics against the uncoupled one, so the tests pin the coupling's record, the
configuration check and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e359_the_world_gets_its_own_dynamics as e359


def _run(coupled=False, diag=0.78, forget=0.40, replay_forget=0.12, channel=0.29, reps=20,
         world=e359.WORLD_READ_SHA1, dims=8, basis="cell_class", seed0=0, tasks=3, coupling="2aa8379a9e5b"):
    payload = {
        "config": {"loop_world_coupled": coupled, "readout_from_world": True, "loop_world_dims": dims,
                   "loop_world_leak": 0.35, "loop_world_modes": 0, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": seed0},
        "env_draw": {"world_dims": dims, "world_drive_sha1": "d", "world_read_sha1": world,
                     "world_coupled": coupled, "world_coupling_sha1": (coupling if coupled else None),
                     "cue_sha1": "c", "action_sha1": "a", "feedback_sha1": "f"},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": dims} for i in range(tasks)],
        "methods": {},
    }
    for arm in e359.ARMS:
        forget_arm = forget if arm == e359.NAIVE else replay_forget
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


def _judge(plain=None, coupled=None):
    plain = plain if plain is not None else _run(coupled=False)
    coupled = coupled if coupled is not None else _run(coupled=True, diag=0.58, forget=0.30, replay_forget=0.10)
    return {row["id"]: row
            for row in e359.judge(e359.reading(plain_path=_write(plain), coupled_path=_write(coupled)))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a coupling that was asked for but not recorded, a different world, a different seed stream, fewer replicates
    assert _judge(coupled=_run(coupled=True, coupling=None))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(coupled=_run(coupled=False))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(coupled=_run(coupled=True, world="other"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(coupled=_run(coupled=True, seed0=7))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(coupled=_run(coupled=True, reps=5))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a coupled world a body cannot learn in, and one learnable too weakly to call
    assert _judge(coupled=_run(coupled=True, diag=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(coupled=_run(coupled=True, diag=0.33))["T2"]["verdict"].startswith("NULL")
    # T3: a coupled arm whose answer is not earned
    assert _judge(coupled=_run(coupled=True, channel=0.01))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: a coupled suite that holds itself
    assert _judge(coupled=_run(coupled=True, forget=0.01))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(coupled=_run(coupled=True, forget=0.03))["T4"]["verdict"].startswith("NULL")
    # T5: a buffer that makes the coupled suite worse, and one whose effect is too small to call
    assert _judge(coupled=_run(coupled=True, replay_forget=0.60))["T5"]["verdict"].startswith("FALSIFIER")
    assert _judge(coupled=_run(coupled=True, replay_forget=0.39))["T5"]["verdict"].startswith("NULL")
    # the coupled run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e359.judge(e359.reading(plain_path=_write(_run(coupled=False)),
                                                  coupled_path=Path("runs/does_not_exist.json"))))


def test_the_buffer_value_is_read_inside_the_coupled_run():
    r = e359.reading(plain_path=_write(_run(coupled=False)),
                     coupled_path=_write(_run(coupled=True, forget=0.40, replay_forget=0.10)))
    est = r["coupled_buffer"]
    assert est["n"] == 20, est
    #: the buffer's value is a within-run contrast, so its sigma is that run's own per-replicate spread
    assert abs(est["delta"] - (-0.30)) < 1e-9, est
    assert all(abs(v + 0.30) < 1e-9 for v in est["vals"]), est["vals"]
    #: and the two worlds' facts are recorded separately, which is what T1 compares
    assert r["facts"]["coupled"]["world_coupled"] is True, r["facts"]
    assert r["facts"]["plain"]["world_coupled"] is False, r["facts"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e359_the_world_gets_its_own_dynamics.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e359.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["facts"]["coupled"]["world_coupled"] and d["facts"]["coupled"]["world_coupling_sha1"], d["facts"]
    assert d["facts"]["plain"]["world_coupling_sha1"] is None, d["facts"]
    for key in (f"coupled_{e359.NAIVE}", f"coupled_{e359.REPLAY}"):
        assert d["rows"][key]["n"] == e359.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
