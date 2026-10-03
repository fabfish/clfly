"""`e380` reads a probe on the trained body at the wide step, so the tests pin the faithfulness check, both faces of
the five claims and the live reading's own two-ended comparison.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e380_what_the_training_built as e380


def _reading(initial=0.70, trained=0.85, recorded=0.77, frozen=0.6602, reps=20, ok=True, reason="absent",
             head=None, frozen_present=True):
    per_task = {}
    for arm in e380.ARMS:
        per_task[arm] = {}
        for k in range(e380.N_TASKS):
            heads = [recorded] * reps if head is None else ([recorded] * (reps - 1) + [head])
            per_task[arm][k] = {"initial": [initial] * reps, "trained": [trained] * reps, "head": heads,
                                "recorded": [recorded] * reps, "sd_initial": [0.20] * reps,
                                "sd_trained": [0.22] * reps}
    arms = {}
    for arm in e380.ARMS:
        rec = (per_task[arm][0]["recorded"][0] + per_task[arm][0]["head"][0]) / 2.0 if head is not None else recorded
        arms[arm] = {"initial_probe": initial, "trained_probe": trained, "recorded": rec, "head_accuracy": rec,
                     "built": trained - initial, "readable_over_learned": trained - rec}
    return {"ok": ok, "reason": reason, "arms": arms, "present": ok, "run": "r.json", "theta_dir": "d",
            "run_settings": {"size": 952, "readout": 32, "lr": 0.003, "cue_at": 0, "replicates": reps},
            "per_task": per_task, "head_accuracy": {}, "recorded": {},
            "frozen": ({"accuracy": frozen, "world_sd": 0.2029, "artifact": "e363.json"} if frozen_present else None),
            "spread_initial": 0.20, "spread_trained": 0.22}


def _judge(**kw):
    return {row["id"]: row for row in e380.judge(_reading(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("ZA1", "ZA2", "ZA3", "ZA4", "ZA5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # ZA1: a saved head that does not reproduce the artifact, which would invalidate everything else
    assert _judge(head=0.40)["ZA1"]["verdict"].startswith("FALSIFIER")

    # ZA2: a frozen cell far from this roll, one whose gap is between the bars, and the grid absent
    assert _judge(frozen=0.40)["ZA2"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=0.55)["ZA2"]["verdict"].startswith("NULL")
    assert _judge(frozen_present=False)["ZA2"]["verdict"].startswith("REFUSED")

    # ZA3: a trained body holding nothing, and one holding too little to call
    assert _judge(trained=0.26)["ZA3"]["verdict"].startswith("FALSIFIER")
    assert _judge(trained=0.32)["ZA3"]["verdict"].startswith("NULL")

    # ZA4: a body the training did not change for a probe, and one whose gain is too small to call
    assert _judge(initial=0.70, trained=0.71)["ZA4"]["verdict"].startswith("FALSIFIER")
    assert _judge(initial=0.70, trained=0.73)["ZA4"]["verdict"].startswith("NULL")

    # ZA5: a head that reaches everything the probe reaches, and one whose shortfall is too small to call
    assert _judge(trained=0.77, recorded=0.77)["ZA5"]["verdict"].startswith("FALSIFIER")
    assert _judge(trained=0.80, recorded=0.77)["ZA5"]["verdict"].startswith("NULL")

    #: the run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e380.judge(_reading(ok=False)))


def test_the_pairing_walks_every_task_and_replicate():
    r = _reading(initial=0.70, trained=0.85, reps=20)
    p = e380._paired(r["per_task"][e380.NAIVE], "trained", "initial")
    assert p["n"] == e380.N_TASKS * 20 and abs(p["delta"] - 0.15) < 1e-9, p


def test_the_live_reading_is_the_mirror_of_the_tight_step():
    p = Path("runs/e380_what_the_training_built.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e380.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e380.judge(d)}
    #: the reconstruction claim is what the other four rest on, and it is structural
    assert verdicts["ZA1"].startswith("MET"), (verdicts["ZA1"], d["per_task"][e380.NAIVE][0]["head"][:3])
    assert d["run_settings"]["cue_at"] == 0 and d["run_settings"]["lr"] == 0.003, d["run_settings"]
    assert d["frozen"] is not None and abs(d["frozen"]["accuracy"] - 0.6602) < 1e-4, d["frozen"]
    #: both bodies were rolled for every task of every replicate, which is what makes ZA4 and ZA5 paired
    for arm in e380.ARMS:
        for k in range(e380.N_TASKS):
            cell = d["per_task"][arm][str(k)]
            assert len(cell["initial"]) == e380.REPLICATES, (arm, k)
            assert len(cell["trained"]) == e380.REPLICATES, (arm, k)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
