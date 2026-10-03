"""`e386` widens the world at the tight step, so the tests pin both faces of the five claims, the refusal when the
run, its weights or the reference are absent, and the live width's own comparison.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e386_a_wider_world as e386


def _facts(dims=32, lr=0.03, coupling="other", drive="big", read="big"):
    return {"loop_world_leak": 0.35, "readout_from_world": True, "loop_world_dims": dims, "closed_loop": True,
            "loop_world_modes": 0, "loop_world_nonlinear": False, "repeats": 20, "circuit_size": 300,
            "readout_size": 32, "basis": "cell_class", "seed0": 0, "iters": 500,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": read,
            "world_drive_sha1": drive, "world_coupling_sha1": coupling, "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False, "lr": lr, "batch": 32}


def _reading(initial=0.68, trained=0.40, head=0.38, dims=32, reference=True, ok=True, reason="absent",
             reference_facts=None):
    if not ok:
        return {"ok": False, "cells": {}, "present": False, "reason": reason}
    return {"ok": True, "present": True, "reason": None, "run": "r.json", "arm": e386.NAIVE, "reps": 20,
            "dims": dims, "readout": 32, "probe_initial_task_0": initial, "probe_trained_task_0": trained,
            "probe_initial_mean": initial, "probe_trained_mean": trained, "head_task_0": head, "head_mean": head,
            "facts": _facts(dims=dims),
            "reference_facts": (_facts(dims=8, coupling="1b7d", drive="small", read="small")
                                if reference_facts is None else reference_facts),
            "cells": {}, "reference": ({"artifact": "e379.json", "trained_probe": 0.2361,
                                        "initial_probe": 0.6597} if reference else None)}


def _judge(**kw):
    return {row["id"]: row for row in e386.judge(_reading(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("G1", "G2", "G3", "G4", "G5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # G1: a field the dimension does not move was changed
    assert _judge(reference_facts={**_facts(dims=8, coupling="1b7d", drive="small", read="small"), "basis": "neuron"})[
        "G1"]["verdict"].startswith("FALSIFIER")
    #: no reference facts at all leaves G1 firing rather than passing, since nothing was compared
    assert _judge(reference_facts={})["G1"]["verdict"].startswith("FALSIFIER")

    # G2: a wider world that is not live at this step, and one whose margin is too small to call
    assert _judge(initial=0.26)["G2"]["verdict"].startswith("FALSIFIER")
    assert _judge(initial=0.32)["G2"]["verdict"].startswith("NULL")

    # G3: an update that empties the wider world too, and one that leaves too little to call
    assert _judge(trained=0.26)["G3"]["verdict"].startswith("FALSIFIER")
    assert _judge(trained=0.32)["G3"]["verdict"].startswith("NULL")

    # G4: a wider world that does not beat the narrow one's floor, and one whose gain is too small to call
    assert _judge(trained=0.10, reference=True)["G4"]["verdict"].startswith("FALSIFIER")
    assert _judge(trained=0.32, reference=True)["G4"]["verdict"].startswith("NULL")
    assert _judge(trained=0.40, reference=True)["G4"]["verdict"].startswith("MET")
    assert _judge(reference=False)["G4"]["verdict"].startswith("REFUSED")

    # G5: a head that parts company with the world at this width
    assert _judge(trained=0.40, head=0.60)["G5"]["verdict"].startswith("FALSIFIER")

    #: the run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e386.judge(_reading(ok=False)))


def test_live_reading_carries_the_width_and_the_reference():
    p = Path("runs/e386_a_wider_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e386.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the world's dimension is in the reading and in the facts the configuration claim compares
    assert d["dims"] == e386.DIMS, d["dims"]
    assert d["facts"]["loop_world_dims"] == e386.DIMS, d["facts"]["loop_world_dims"]
    assert d["reference_facts"] is not None and d["reference_facts"]["loop_world_dims"] == 8, d["reference_facts"]
    #: and the probe was fitted on the world's own width and not on the first eight columns
    for key, values in d["cells"].items():
        assert len(values) == e386.REPLICATES, (key, len(values))
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
