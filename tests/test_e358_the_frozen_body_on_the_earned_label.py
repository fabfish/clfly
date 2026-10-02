"""`e358` pairs a frozen body against the plastic arms on the earned label, so the tests pin the two-artifact
configuration check and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e358_the_frozen_body_on_the_earned_label as e358


def _body(frozen=False, diag=0.78, forget=0.40, replay_forget=0.12, channel=0.29, reps=20,
          world=e358.WORLD_READ_SHA1, partition=e358.PARTITION_SHA1, basis="cell_class", seed0=0, tasks=3):
    payload = {
        "config": {"frozen_body": frozen, "readout_from_world": True, "loop_world_dims": 8, "loop_world_leak": 0.35,
                   "loop_world_modes": 0, "closed_loop": True, "repeats": reps, "circuit_size": 300,
                   "readout_size": 32, "basis": basis, "seed0": seed0},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "d", "world_read_sha1": world},
        "partition_draw": {"matched_random_draw_seed": 0, "n_groups": 98, "fingerprint_sha1": partition},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {},
    }
    for arm in e358.ARMS:
        forget_arm = forget if arm == e358.NAIVE else replay_forget
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


def _judge(plastic=None, frozen=None):
    plastic = plastic if plastic is not None else _body(frozen=False)
    frozen = frozen if frozen is not None else _body(frozen=True, diag=0.72, forget=0.30, replay_forget=0.10)
    return {row["id"]: row
            for row in e358.judge(e358.reading(plastic_path=_write(plastic), frozen_path=_write(frozen)))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a frozen run that is not frozen, a different world, an extra field differing, and too few replicates
    assert _judge(frozen=_body(frozen=False))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, world="other"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, partition="other"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, basis="cell_type"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, reps=5))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a frozen body that cannot learn, and one that learns too weakly to call
    assert _judge(frozen=_body(frozen=True, diag=0.30, forget=0.10))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, diag=0.33))["T2"]["verdict"].startswith("NULL")
    # T3: the frozen arm at least as good as the plastic one, and a difference too small to call
    assert _judge(frozen=_body(frozen=True, diag=0.85))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, diag=0.78))["T3"]["verdict"].startswith("NULL")
    # T4: a frozen suite that holds the world by itself
    assert _judge(frozen=_body(frozen=True, forget=0.01))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, forget=0.03))["T4"]["verdict"].startswith("NULL")
    # T5: a buffer that makes the frozen suite worse, and one whose effect is too small to call
    assert _judge(frozen=_body(frozen=True, replay_forget=0.50))["T5"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_body(frozen=True, replay_forget=0.39))["T5"]["verdict"].startswith("NULL")
    # the frozen run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e358.judge(e358.reading(plastic_path=_write(_body(frozen=False)),
                                                  frozen_path=Path("runs/does_not_exist.json"))))


def test_the_diagonal_gap_is_paired_over_replicates():
    r = e358.reading(plastic_path=_write(_body(frozen=False, diag=0.78)),
                     frozen_path=_write(_body(frozen=True, diag=0.68)))
    est = r["diagonal_gap"]
    assert est["n"] == 20, est
    #: the gap is the per-replicate difference of the two bodies' `naive` diagonals
    assert abs(est["delta"] - 0.10) < 1e-9, est
    assert all(abs(v - 0.10) < 1e-9 for v in est["vals"]), est["vals"]
    #: and the buffer value is read inside the frozen run, not across the two
    assert r["frozen_buffer"]["n"] == 20, r["frozen_buffer"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e358_the_frozen_body_on_the_earned_label.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e358.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    t1 = d["claims"][0]["verdict"]
    assert t1.startswith(("MET", "FALSIFIER")), t1
    if t1.startswith("FALSIFIER"):
        #: the one field beyond `frozen_body` that differs is the partition record, which the frozen run has no
        #: block arm to use
        assert "partition" in t1, t1
    assert d["facts"]["frozen"]["frozen_body"] and not d["facts"]["plastic"]["frozen_body"], d["facts"]
    for key in (f"plastic_{e358.NAIVE}", f"frozen_{e358.NAIVE}"):
        assert d["rows"][key]["n"] == e358.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
