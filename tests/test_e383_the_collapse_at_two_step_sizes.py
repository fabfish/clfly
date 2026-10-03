"""`e383` compares the tight step's collapse at two step sizes, so the tests pin both faces of the five claims, the
refusal when a run or its weights are absent, and the live two-series shape.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e383_the_collapse_at_two_step_sizes as e383


def _facts(lr, iters, repeats=5):
    return {"lr": lr, "iters": iters, "repeats": repeats, "loop_cue_at": 8, "basis": "cell_class", "circuit_size": 300,
            "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True, "loop_world_dims": 8,
            "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False, "loop_carried": None,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r",
            "world_drive_sha1": "aw", "world_coupling_sha1": "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


def _series(lr, probes, initial=0.6875, head=None):
    return {str(b): {"run": "r.json", "iters": b, "lr": lr, "repeats": 5, "probe_task_0": p,
                     "initial_task_0": initial, "trained_mean": p,
                     "head_task_0": p if head is None else head[b]}
            for b, p in zip(e383.BUDGETS, probes)}


def _doc(small=(0.66, 0.66, 0.62, 0.55, 0.21), big=(0.2083, 0.2083, 0.2083, 0.2083, 0.2083), ok=True, reason="absent",
         facts=None):
    if not ok:
        return {"ok": False, "sweeps": {}, "facts": {}, "reason": reason}
    return {"ok": True, "sweeps": {str(e383.SMALL): _series(e383.SMALL, small),
                                   str(e383.BIG): _series(e383.BIG, big)},
            "facts": facts if facts is not None else {
                str(e383.SMALL): {str(b): _facts(e383.SMALL, b) for b in e383.BUDGETS},
                str(e383.BIG): {str(b): _facts(e383.BIG, b, repeats=(20 if b == 500 else 5)) for b in e383.BUDGETS}},
            "arm": e383.NAIVE, "reps": e383.SWEEP_REPS, "budgets": list(e383.BUDGETS)}


def _judge(**kw):
    return {row["id"]: row for row in e383.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("D1", "D2", "D3", "D4", "D5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # D1: a field other than the rate moved between the sweeps
    bad = {str(e383.SMALL): {str(b): _facts(e383.SMALL, b) for b in e383.BUDGETS},
           str(e383.BIG): {str(b): _facts(e383.BIG, b) for b in e383.BUDGETS}}
    bad[str(e383.SMALL)]["20"] = {**bad[str(e383.SMALL)]["20"], "basis": "neuron"}
    assert _judge(facts=bad)["D1"]["verdict"].startswith("FALSIFIER")

    # D2: a smaller rate that keeps the cue, and one whose loss is between the bars
    assert _judge(small=(0.66, 0.66, 0.66, 0.66, 0.66))["D2"]["verdict"].startswith("FALSIFIER")
    assert _judge(small=(0.66, 0.66, 0.62, 0.62, 0.60))["D2"]["verdict"].startswith("NULL")

    # D3: a first step at the corpus's rate that collapses the world too, and a gap too small to call
    assert _judge(small=(0.22, 0.22, 0.22, 0.22, 0.21))["D3"]["verdict"].startswith("FALSIFIER")
    assert _judge(small=(0.24, 0.23, 0.22, 0.22, 0.21))["D3"]["verdict"].startswith("NULL")

    # D4: a flat series at the smaller rate, and one whose total drop is too small to call
    assert _judge(small=(0.21, 0.21, 0.21, 0.21, 0.21))["D4"]["verdict"].startswith("FALSIFIER")
    assert _judge(small=(0.28, 0.28, 0.25, 0.24, 0.21))["D4"]["verdict"].startswith("NULL")

    # D5: two rates that cost the same at one step, and a gap too small to call
    assert _judge(small=(0.22, 0.22, 0.22, 0.22, 0.21))["D5"]["verdict"].startswith("FALSIFIER")
    assert _judge(small=(0.28, 0.28, 0.25, 0.24, 0.21))["D5"]["verdict"].startswith("NULL")

    #: a run or its weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e383.judge(_doc(ok=False)))


def test_the_two_series_are_read_at_the_same_budgets():
    r = _doc()
    assert [int(k) for k in r["sweeps"][str(e383.SMALL)]] == list(e383.BUDGETS)
    assert [int(k) for k in r["sweeps"][str(e383.BIG)]] == list(e383.BUDGETS)


def test_the_live_sweeps_are_the_same_cell_at_two_rates():
    p = Path("runs/e383_the_collapse_at_two_step_sizes.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e383.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: each budget of the smaller rate is this unit's own run; the larger rate's 500 point is `e379`'s
    assert d["sweeps"][str(e383.SMALL)]["500"]["run"].startswith("e383_"), d["sweeps"][str(e383.SMALL)]["500"]
    assert d["sweeps"][str(e383.BIG)]["500"]["run"].startswith("e379_"), d["sweeps"][str(e383.BIG)]["500"]
    #: and both series were read against the same connectome weights on the same examples
    for lr in (e383.SMALL, e383.BIG):
        initials = {d["sweeps"][str(lr)][str(b)]["initial_task_0"] for b in e383.BUDGETS}
        assert len(initials) == 1, (lr, initials)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
