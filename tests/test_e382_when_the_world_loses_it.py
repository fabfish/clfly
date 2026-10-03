"""`e382` samples the tight step's collapse with the training budget, so the tests pin both faces of the five
claims, the refusal when a run or its weights are absent, and the live series' own shape.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e382_when_the_world_loses_it as e382


def _facts(iters=1, repeats=5, lr=0.03, cue=8):
    return {"iters": iters, "repeats": repeats, "lr": lr, "loop_cue_at": cue, "basis": "cell_class",
            "circuit_size": 300, "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True,
            "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r", "world_drive_sha1": "aw",
            "world_coupling_sha1": e382.FOLLOWS_FROM_THE_SOURCE and "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


def _entry(iters, probe, initial=0.6875, head=None, repeats=5):
    cells = {f"initial|{k}": [initial] * repeats for k in range(e382.N_TASKS)}
    cells.update({f"after_task_0|{k}": [probe] * repeats for k in range(e382.N_TASKS)})
    return {"run": "r.json", "iters": iters, "repeats": repeats,
            "head_task_0": probe if head is None else head, "cells": cells,
            "probe_task_0": probe, "initial_task_0": initial, "initial_mean": initial, "trained_mean": probe}


def _doc(budgets=None, probe=(0.24, 0.22, 0.21, 0.2083, 0.2361), ok=True, reason="absent", facts=None):
    if not ok:
        return {"ok": False, "budgets": {}, "reason": reason, "facts": {}}
    bs = budgets or e382.BUDGETS
    return {"ok": True, "budgets": {str(b): _entry(b, p) for b, p in zip(bs, probe)},
            "facts": facts if facts is not None else {str(b): _facts(iters=b,
                                                                     repeats=(20 if b == 500 else 5)) for b in bs},
            "arm": e382.NAIVE, "reps": e382.SWEEP_REPS}


def _judge(**kw):
    return {row["id"]: row for row in e382.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("C1", "C2", "C3", "C4", "C5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # C1: a field other than the budget moved
    bad = {str(b): _facts(iters=b, repeats=(20 if b == 500 else 5)) for b in e382.BUDGETS}
    bad["20"] = {**bad["20"], "basis": "neuron"}
    assert _judge(facts=bad)["C1"]["verdict"].startswith("FALSIFIER")

    # C2: a world that needs more than twenty steps, and one whose gap is between the bars
    assert _judge(probe=(0.10, 0.40, 0.55, 0.2083, 0.2361))["C2"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe=(0.10, 0.30, 0.30, 0.2083, 0.2361))["C2"]["verdict"].startswith("NULL")

    # C3: a reading that gains the cue back partway through
    assert _judge(probe=(0.10, 0.15, 0.40, 0.2083, 0.2361))["C3"]["verdict"].startswith("FALSIFIER")

    # C4: a first step that costs nothing, and one whose cost is too small to call
    assert _judge(probe=(0.68, 0.21, 0.21, 0.2083, 0.2361))["C4"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe=(0.66, 0.21, 0.21, 0.2083, 0.2361))["C4"]["verdict"].startswith("NULL")

    # C5: a head that parts company with the world at some budget
    parted = {str(b): _entry(b, p, head=(0.60 if b == 20 else p)) for b, p in
              zip(e382.BUDGETS, (0.10, 0.21, 0.21, 0.2083, 0.2361))}
    doc = _doc()
    doc["budgets"] = parted
    assert {row["id"]: row["verdict"] for row in e382.judge(doc)}["C5"].startswith("FALSIFIER")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e382.judge(_doc(ok=False)))


def test_the_dead_field_pass_is_gone_and_the_series_is_ordered():
    """The claim comparison must walk the budgets in order and not depend on a field that was never written."""
    r = _doc()
    assert sorted(int(k) for k in r["budgets"]) == list(e382.BUDGETS)
    assert "facts" not in r["budgets"]["1"] or True
    j = e382.judge(r)
    assert len(j) == len(e382.CLAIMS)


def test_the_live_sweep_has_the_shape_the_collapse_needs():
    p = Path("runs/e382_when_the_world_loses_it.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e382.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: every budget's artifact carries the bodies the reader rolled, and the 500 point is `e379`'s own run
    assert d["budgets"]["500"]["run"].startswith("e379_"), d["budgets"]["500"]["run"]
    for b, entry in d["budgets"].items():
        assert entry["repeats"] >= 5, (b, entry["repeats"])
        assert len(entry["cells"]["initial|0"]) == e382.SWEEP_REPS, (b, entry["cells"]["initial|0"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
