"""`e356` reads the earned label at twenty replicates, so the tests pin the extraction from the runner's schema, the
paired ordering contrast and both faces of the four claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e356_the_earned_label_at_twenty_replicates as e356


def _run(reps=20, arms=e356.ARMS, readout_from_world=True, world_dims=8, fingerprint=e356.WORLD_READ_SHA1,
         base_forget=0.39, gap=-0.20, base_diag=0.80, diag_gap=0.02, channel=0.31, spread=0.002, tasks=3):
    payload = {
        "config": {"readout_from_world": readout_from_world, "loop_world_dims": world_dims, "loop_world_leak": 0.35,
                   "loop_world_modes": 0, "closed_loop": True, "repeats": reps, "circuit_size": 300,
                   "readout_size": 32},
        "env_draw": {"world_dims": world_dims, "world_drive_sha1": "d", "world_read_sha1": fingerprint},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": world_dims} for i in range(tasks)],
        "methods": {},
    }
    for a in arms:
        reps_list = []
        for r in range(reps):
            wobble = 0.001 * ((r % 5) - 2)
            forget = base_forget + wobble + (gap if a == e356.REPLAY else 0.0)
            diag = base_diag + wobble + (diag_gap if a == e356.REPLAY else 0.0)
            reps_list.append({
                "final_accuracy": diag, "mean_forgetting": forget, "learned": [diag] * tasks,
                "forgetting_per_task": [forget] * (tasks - 1), "final_per_task": [diag] * tasks,
                "retention": [[diag if i == j else None for j in range(tasks)] for i in range(tasks)],
                "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel + wobble,
                                    "without_loop": 0.5 + wobble} for j in range(tasks)]})
        payload["methods"][a] = {"final_accuracy": base_diag, "final_sem": 0.01, "mean_forgetting": base_forget,
                                 "forgetting_sem": 0.01, "learned": [base_diag] * tasks, "replicates": reps_list}
    return payload


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(payload):
    return {row["id"]: row for row in e356.judge(e356.reading(path=_write(payload)))}


def test_the_four_claims_read_both_faces():
    j = _judge(_run())
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a run that says it reads the world but does not, another world, and too few replicates
    assert _judge(_run(readout_from_world=False))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(fingerprint="other"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(reps=5))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: the ordering inverting, and a contrast too small to call
    assert _judge(_run(gap=+0.20))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(gap=+0.02))["T2"]["verdict"].startswith("NULL")
    # T3: the retention bought out of acquisition
    assert _judge(_run(diag_gap=-0.20))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(_run(diag_gap=-0.07))["T3"]["verdict"].startswith("NULL")
    # T4: an arm whose answer is not earned
    assert _judge(_run(channel=0.01))["T4"]["verdict"].startswith("FALSIFIER")
    # a missing arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e356.judge(e356.reading(path=_write(_run(arms=("naive", "replay"))))))


def test_the_ordering_contrast_is_paired_over_replicates():
    r = e356.reading(path=_write(_run(gap=-0.20)))
    est = r["forgetting_contrast"]
    assert est["n"] == 20, est
    #: the pairing is per replicate, and the per-replicate differences are what its sigma is the spread of
    assert abs(est["delta"] - (-0.20)) < 1e-9, est
    assert all(abs(x + 0.20) < 1e-9 for x in est["vals"]), est["vals"]
    #: the per-arm records carry every replicate's own number
    assert len(r["rows"][e356.NAIVE]["forgetting"]) == 20, r["rows"][e356.NAIVE]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e356_the_earned_label_at_twenty_replicates.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e356.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["readout_from_world"] and d["world_dims"], d
    assert d["replicates"] == e356.REPLICATES, d["replicates"]
    assert d["task_readout_widths"] == [int(d["world_dims"])], d["task_readout_widths"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
