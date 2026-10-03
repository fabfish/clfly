"""`e384` sweeps the wide step's training budget and asks whether its series rises where the tight one falls, so the
tests pin both faces of the five claims, the refusal when a run or the tight artifact is absent, and the live shape.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e384_the_other_end_of_the_window as e384


def _facts(lr=0.003, iters=1, repeats=5, cue=0):
    return {"lr": lr, "batch": 32, "iters": iters, "repeats": repeats, "loop_cue_at": cue, "basis": "cell_class",
            "circuit_size": 300, "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True,
            "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r",
            "world_drive_sha1": "aw", "world_coupling_sha1": "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


def _doc(probes=(0.66, 0.69, 0.72, 0.75, 0.79), initial=0.6875, tight=0.2083, ok=True, reason="absent", facts=None,
         tight_present=True):
    if not ok:
        return {"ok": False, "budgets": {}, "facts": {}, "tight": None, "reason": reason}
    budgets = {str(b): {"run": "r.json", "iters": b, "lr": 0.003, "repeats": (20 if b == 500 else 5),
                        "probe_task_0": p, "initial_task_0": initial, "probe_mean": p, "head_task_0": p}
               for b, p in zip(e384.BUDGETS, probes)}
    return {"ok": True, "budgets": budgets,
            "facts": facts if facts is not None else {
                str(b): _facts(iters=b, repeats=(20 if b == 500 else 5)) for b in e384.BUDGETS},
            "tight": ({"artifact": "e383.json", "budget_1": tight, "budget_500": 0.2292} if tight_present else None),
            "arm": e384.NAIVE, "reps": e384.SWEEP_REPS}


def _judge(**kw):
    return {row["id"]: row for row in e384.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("E1", "E2", "E3", "E4", "E5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # E1: a field other than the budget moved
    bad = {str(b): _facts(iters=b, repeats=(20 if b == 500 else 5)) for b in e384.BUDGETS}
    bad["20"] = {**bad["20"], "lr": 0.03}
    assert _judge(facts=bad)["E1"]["verdict"].startswith("FALSIFIER")

    # E2: a series that does not rise, and one whose rise is too small to call
    assert _judge(probes=(0.70, 0.70, 0.70, 0.70, 0.70))["E2"]["verdict"].startswith("FALSIFIER")
    assert _judge(probes=(0.70, 0.70, 0.70, 0.70, 0.72))["E2"]["verdict"].startswith("NULL")

    # E3: a first update that empties the wide end too, and one whose margin is too small to call
    assert _judge(probes=(0.26, 0.69, 0.72, 0.75, 0.79))["E3"]["verdict"].startswith("FALSIFIER")
    assert _judge(probes=(0.32, 0.69, 0.72, 0.75, 0.79))["E3"]["verdict"].startswith("NULL")

    # E4: two ends that one update empties equally, and a gap too small to call
    assert _judge(probes=(0.24, 0.69, 0.72, 0.75, 0.79))["E4"]["verdict"].startswith("FALSIFIER")
    assert _judge(probes=(0.28, 0.69, 0.72, 0.75, 0.79))["E4"]["verdict"].startswith("NULL")
    assert _judge(tight_present=False)["E4"]["verdict"].startswith("REFUSED")

    # E5: a training that adds nothing to the world, and one whose gain is too small to call
    assert _judge(probes=(0.66, 0.66, 0.66, 0.66, 0.66))["E5"]["verdict"].startswith("FALSIFIER")
    assert _judge(probes=(0.66, 0.66, 0.66, 0.66, 0.72))["E5"]["verdict"].startswith("NULL")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e384.judge(_doc(ok=False)))


def test_the_field_list_holds_the_knobs_the_claim_names():
    """`e383`'s first reading compared two sweeps over a list without the rate; here it is in the list."""
    r = _doc()
    assert "lr" in r["facts"]["1"] and "batch" in r["facts"]["1"]


def test_the_live_sweep_is_the_mirror_of_the_tight_one():
    p = Path("runs/e384_the_other_end_of_the_window.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e384.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the 500 point is `e380`'s own run and the tight comparison comes from `e383`'s artifact
    assert d["budgets"]["500"]["run"].startswith("e380_"), d["budgets"]["500"]["run"]
    assert d["tight"] is not None and d["tight"]["artifact"].startswith("e383_"), d["tight"]
    #: and the connectome's own weights read the same on every budget, which is the roll's internal check
    initials = {d["budgets"][str(b)]["initial_task_0"] for b in e384.BUDGETS}
    assert len(initials) == 1, initials
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
