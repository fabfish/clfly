"""`e357` pairs the corpus's two block arms on the earned label, so the tests pin the two-artifact configuration
check, the paired contrasts and both faces of the four claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e357_the_basis_contrast_on_the_earned_label as e357


def _run(arm, reps=20, bio_forget=0.375, rand_forget=0.38, diag=0.78, channel=0.27,
         partition=e357.PARTITION_SHA1, world=e357.WORLD_READ_SHA1, basis="cell_class", seed0=0, tasks=3):
    forget = bio_forget if arm == e357.ARM_BIO else rand_forget
    payload = {
        "config": {"readout_from_world": True, "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0,
                   "closed_loop": True, "repeats": reps, "circuit_size": 300, "readout_size": 32, "basis": basis,
                   "seed0": seed0, "methods": arm},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "d", "world_read_sha1": world},
        "partition_draw": {"matched_random_draw_seed": 0, "n_groups": 98, "fingerprint_sha1": partition},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {},
    }
    reps_list = []
    for r in range(reps):
        wobble = 0.001 * ((r % 5) - 2)
        reps_list.append({
            "final_accuracy": diag + wobble, "mean_forgetting": forget + wobble, "learned": [diag + wobble] * tasks,
            "forgetting_per_task": [forget] * (tasks - 1), "final_per_task": [diag] * tasks,
            "retention": [[diag if i == j else None for j in range(tasks)] for i in range(tasks)],
            "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel + wobble,
                                "without_loop": 0.5 + wobble} for j in range(tasks)]})
    payload["methods"][arm] = {"final_accuracy": diag, "final_sem": 0.01, "mean_forgetting": forget,
                               "forgetting_sem": 0.01, "learned": [diag] * tasks, "replicates": reps_list}
    return payload


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(bio=None, rand=None):
    bio = bio if bio is not None else _run(e357.ARM_BIO)
    rand = rand if rand is not None else _run(e357.ARM_RAND)
    return {row["id"]: row for row in e357.judge(e357.reading(bio_path=_write(bio), rand_path=_write(rand)))}


def test_the_four_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a different partition, a different world, a different basis, and too few replicates
    assert _judge(rand=_run(e357.ARM_RAND, partition="other"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(rand=_run(e357.ARM_RAND, world="other"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(rand=_run(e357.ARM_RAND, basis="cell_type"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(rand=_run(e357.ARM_RAND, reps=5))["T1"]["verdict"].startswith("FALSIFIER")
    # T2: the basis contrast resolving on forgetting, and sitting between the bars
    assert _judge(rand=_run(e357.ARM_RAND, rand_forget=0.20))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(rand=_run(e357.ARM_RAND, rand_forget=0.30))["T2"]["verdict"].startswith("NULL")
    # T3: and resolving on the diagonal
    assert _judge(rand=_run(e357.ARM_RAND, diag=0.60))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: an arm that is not learned, and one whose answer is not earned
    assert _judge(rand=_run(e357.ARM_RAND, diag=0.30))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(rand=_run(e357.ARM_RAND, channel=0.01))["T4"]["verdict"].startswith("FALSIFIER")
    # the random arm absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e357.judge(e357.reading(bio_path=_write(_run(e357.ARM_BIO)),
                                                  rand_path=Path("runs/does_not_exist.json"))))


def test_the_pairing_is_per_replicate_and_the_facts_are_read_off_both_runs():
    r = e357.reading(bio_path=_write(_run(e357.ARM_BIO, bio_forget=0.375)),
                     rand_path=_write(_run(e357.ARM_RAND, rand_forget=0.35)))
    est = r["forgetting_contrast"]
    assert est["n"] == 20, est
    #: the contrast is the per-replicate difference, so its sigma is that difference's spread
    assert abs(est["delta"] - 0.025) < 1e-9, est
    assert len(est["vals"]) == 20 and all(abs(v - 0.025) < 1e-9 for v in est["vals"]), est["vals"]
    #: the facts are per arm, and the shared ones are what T1 compares
    assert r["facts"][e357.ARM_BIO]["partition_sha1"] == e357.PARTITION_SHA1, r["facts"]
    assert r["facts"][e357.ARM_RAND]["world_read_sha1"] == e357.WORLD_READ_SHA1, r["facts"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e357_the_basis_contrast_on_the_earned_label.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e357.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    for a in (e357.ARM_BIO, e357.ARM_RAND):
        assert d["facts"][a]["partition_sha1"] == e357.PARTITION_SHA1, d["facts"][a]
        assert d["facts"][a]["replicates"] == e357.REPLICATES, d["facts"][a]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
