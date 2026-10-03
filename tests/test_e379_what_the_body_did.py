"""`e379` reads a probe on the trained body, so the tests pin the faithfulness check, both faces of the five claims
and the live reading's own reconstruction.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e379_what_the_body_did as e379


def _reading(initial=0.75, trained=0.55, recorded=0.24, curve=0.7617, reps=20, ok=True, reason="absent",
             head=None, curve_present=True):
    per_task = {}
    for arm in e379.ARMS:
        per_task[arm] = {}
        for k in range(e379.N_TASKS):
            heads = [recorded] * reps if head is None else ([recorded] * (reps - 1) + [head])
            per_task[arm][k] = {"initial": [initial] * reps, "trained": [trained] * reps,
                                "head": heads, "recorded": [recorded] * reps,
                                "sd_initial": [0.0478] * reps, "sd_trained": [0.02] * reps}
    arms = {}
    for arm in e379.ARMS:
        rec = (per_task[arm][0]["recorded"][0] + per_task[arm][0]["head"][0]) / 2.0 if head is not None else recorded
        arms[arm] = {"initial_probe": initial, "trained_probe": trained, "head_accuracy": rec, "recorded": rec,
                     "degradation": initial - trained, "readable_over_learned": trained - rec}
    return {"ok": ok, "reason": reason, "arms": arms, "present": ok, "run": "r.json", "theta_dir": "d",
            "run_settings": {"size": 952, "readout": 32, "lr": 0.03, "cue_at": 8, "replicates": reps},
            "per_task": per_task, "head_accuracy": {}, "recorded": {},
            "curve": ({"artifact": "e368.json", "accuracy": curve, "world_sd": 0.0478} if curve_present else None),
            "spread_initial": 0.0478, "spread_trained": 0.02}


def _judge(**kw):
    return {row["id"]: row for row in e379.judge(_reading(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("Z1", "Z2", "Z3", "Z4", "Z5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # Z1: a saved head that does not reproduce the artifact, which would invalidate everything else
    assert _judge(head=0.40)["Z1"]["verdict"].startswith("FALSIFIER")

    # Z2: a curve far from this roll, one whose gap is between the bars, and the curve absent
    assert _judge(curve=0.50)["Z2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=0.62)["Z2"]["verdict"].startswith("NULL")
    assert _judge(curve_present=False)["Z2"]["verdict"].startswith("REFUSED")

    # Z3: a trained body holding nothing, and one holding too little to call
    assert _judge(trained=0.26)["Z3"]["verdict"].startswith("FALSIFIER")
    assert _judge(trained=0.32)["Z3"]["verdict"].startswith("NULL")

    # Z4: a body whose content barely moved, and one whose loss is too small to call
    assert _judge(trained=0.74)["Z4"]["verdict"].startswith("FALSIFIER")
    assert _judge(trained=0.72)["Z4"]["verdict"].startswith("NULL")

    # Z5: a trained body with nothing readable left for the head to have missed, and one too close to call
    assert _judge(trained=0.24, recorded=0.24)["Z5"]["verdict"].startswith("FALSIFIER")
    assert _judge(trained=0.29, recorded=0.24)["Z5"]["verdict"].startswith("NULL")

    #: the run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e379.judge(_reading(ok=False)))


def test_the_pairing_walks_every_task_and_replicate():
    r = _reading(initial=0.75, trained=0.55, reps=20)
    p = e379._paired(r["per_task"][e379.NAIVE], "initial", "trained")
    assert p["n"] == e379.N_TASKS * 20, p
    assert abs(p["delta"] - 0.20) < 1e-9, p
    #: and a difference that varies across replicate-tasks is what gives the sem its size
    r["per_task"][e379.NAIVE][0]["trained"] = [0.10] * 20
    q = e379._paired(r["per_task"][e379.NAIVE], "initial", "trained")
    assert q["delta"] > p["delta"] and q["sem"] > 0, q


def test_the_live_reading_reconstructs_the_trained_head():
    p = Path("runs/e379_what_the_body_did.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e379.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e379.judge(d)}
    #: the reconstruction claim is what the other four rest on, and it is structural
    assert verdicts["Z1"].startswith("MET"), (verdicts["Z1"], d["per_task"][e379.NAIVE][0]["head"][:3])
    #: and on this run the trained body holds nothing: the probe is at chance and the head reads the same
    assert verdicts["Z4"].startswith("MET"), verdicts["Z4"]
    for cid in ("Z3", "Z5"):
        assert verdicts[cid].startswith("FALSIFIER"), (cid, verdicts[cid])
    naive = d["arms"][e379.NAIVE]
    assert naive["trained_probe"] < 0.25 and abs(naive["readable_over_learned"]) < 0.05, naive
    assert naive["initial_probe"] > naive["trained_probe"] + 0.10, naive
    #: the world got larger while it lost the label, which is the mechanism and not a detail
    assert d["spread_trained"] > d["spread_initial"], (d["spread_initial"], d["spread_trained"])
    assert d["run_settings"]["lr"] == 0.03 and d["run_settings"]["cue_at"] == 8, d["run_settings"]
    assert d["curve"] is None or abs(d["curve"]["accuracy"] - 0.7617) < 1e-4, d["curve"]
    #: both bodies were rolled for every task of every replicate, which is what makes Z4 and Z5 paired
    for arm in e379.ARMS:
        for k in range(e379.N_TASKS):
            cell = d["per_task"][arm][str(k)]
            assert len(cell["initial"]) == e379.REPLICATES, (arm, k)
            assert len(cell["trained"]) == e379.REPLICATES, (arm, k)
            assert len(cell["recorded"]) == e379.REPLICATES, (arm, k)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "env" not in d and "tasks" not in d and "config" not in d, sorted(d)
