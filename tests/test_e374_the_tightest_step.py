"""`e374` trains the last step where both channels are live, so the tests pin the four-run configuration check, the
curve's licence, both faces of the five claims and the live pair's own price.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e374_the_tightest_step as e374


def _run(source, step, diag=0.80, reps=20, tasks=3, coupling=None, basis="cell_class", iters=500, channel=0.30,
         forget=0.35):
    drive_from_cue = source == "cue"
    coupling = (e374.CUE_COUPLING if drive_from_cue else e374.ACTION_COUPLING) if coupling is None else coupling
    return {
        "config": {"loop_cue_at": step, "loop_drive_from_cue": drive_from_cue, "loop_world_leak": 0.35,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": 8,
                   "loop_world_modes": 0, "loop_world_nonlinear": False, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": 0, "iters": iters},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "cw" if drive_from_cue else "aw",
                     "world_read_sha1": "cr" if drive_from_cue else "r", "world_leak": 0.35, "world_coupled": True,
                     "world_coupling_sha1": coupling, "world_nonlinear": False, "drive_from_cue": drive_from_cue,
                     "cue_at": step, "cue_sha1": "c", "action_sha1": "c" if drive_from_cue else "a",
                     "feedback_sha1": "f", "n_cue": 12, "n_action": 12 if drive_from_cue else 8},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {arm: {"final_accuracy": diag, "mean_forgetting": forget, "learned": [diag] * tasks,
                          "replicates": [{"final_accuracy": diag, "mean_forgetting": forget, "learned": [diag] * tasks,
                                          "retention": [[diag if i == j else None for j in range(tasks)]
                                                        for i in range(tasks)],
                                          "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel,
                                                              "without_loop": 0.5} for j in range(tasks)]}
                                         for _ in range(reps)]}
                    for arm in ("naive", "replay")},
    }


def _curve(cue8=0.8906, action8=0.7617, action_sd=0.0478, cue_sd=0.0600):
    cells = {f"cue@{s}": {"accuracy": 0.80, "world_sd": 0.10, "trial_range": 0.5} for s in range(12)}
    cells.update({f"action@{s}": {"accuracy": 0.70, "world_sd": 0.10, "trial_range": 0.5} for s in range(12)})
    cells["cue@8"] = {"accuracy": cue8, "world_sd": cue_sd, "trial_range": 0.30}
    cells["action@8"] = {"accuracy": action8, "world_sd": action_sd, "trial_range": 0.02}
    cells["action@9"] = {"accuracy": 0.2578, "world_sd": 0.0, "trial_range": 0.0}
    return {"cells": cells}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(cue8=_run("cue", 8, diag=0.8800), action8=_run("action", 8, diag=0.7000),
           cue0=_run("cue", 0, diag=0.8399), action0=_run("action", 0, diag=0.7691), curve=_curve(), absent=False):
    tight = (Path("runs/absent_tight.json"), Path("runs/absent_tight.json")) if absent else (_write(cue8),
                                                                                             _write(action8))
    doc = e374.reading(tight=tight, wide=(_write(cue0), _write(action0)),
                       curve=_write(curve) if curve is not None else Path("runs/absent_curve.json"))
    return {row["id"]: row for row in e374.judge(doc)}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a source that is not the one it claims, a shared field moved between the steps, and a shared field moved
    # between the sources
    assert _judge(action8=_run("action", 8, diag=0.70, coupling=e374.CUE_COUPLING))["T1"]["verdict"].startswith(
        "FALSIFIER")
    assert _judge(cue8=_run("cue", 8, diag=0.88, basis="neuron"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(action0=_run("action", 0, diag=0.7691, iters=400))["T1"]["verdict"].startswith("FALSIFIER")

    # T2: the action world at rest at this step, a cue cell at chance, and the curve absent
    assert _judge(curve=_curve(action_sd=0.0))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=_curve(cue8=0.26))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=None)["T2"]["verdict"].startswith("REFUSED")

    # T3: one of the two games not learnable at this step
    assert _judge(action8=_run("action", 8, diag=0.26))["T3"]["verdict"].startswith("FALSIFIER")

    # T4: a price that does not move with the margin, and one that moves too little to call
    assert _judge(action8=_run("action", 8, diag=0.8000))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(action8=_run("action", 8, diag=0.7800))["T4"]["verdict"].startswith("NULL")

    # T5: a source whose answer is not earned at this step
    assert _judge(action8=_run("action", 8, diag=0.70, channel=0.01))["T5"]["verdict"].startswith("FALSIFIER")

    #: the tight pair absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e374.judge(e374.reading(
        tight=(Path("runs/absent_a.json"), Path("runs/absent_b.json")),
        wide=(_write(_run("cue", 0)), _write(_run("action", 0))), curve=_write(_curve()))))


def test_the_curve_is_read_by_source_and_step():
    cells = e374.curve_cells(_write(_curve()))
    assert abs(cells[("action", 8)]["accuracy"] - 0.7617) < 1e-12
    assert cells[("action", 9)]["world_sd"] == 0.0
    #: a step the curve does not hold is absent rather than zero
    assert ("cue", 99) not in cells
    assert e374.curve_cells(Path("runs/does_not_exist.json")) == {}


def test_the_live_reading_has_a_boundary_one_step_above_it():
    p = Path("runs/e374_the_tightest_step.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e374.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: on this draw the cue source learns at the tight step and the action source does not, which is what the
    #: registered thresholds return and what the unit is for
    verdicts = {row["id"]: row["verdict"] for row in e374.judge(d)}
    for cid in ("T1", "T2", "T4"):
        assert verdicts[cid].startswith("MET"), (cid, verdicts[cid])
    for cid in ("T3", "T5"):
        assert verdicts[cid].startswith("FALSIFIER"), (cid, verdicts[cid])
    #: the licence is that this step is inside the window, and e368's curve says the next step is not
    assert d["frozen"]["action@8"]["world_sd"] > 0.0, d["frozen"]["action@8"]
    cells = e374.curve_cells()
    assert cells[("action", 9)]["world_sd"] == 0.0, cells[("action", 9)]
    #: and the price here is larger than at the widest step
    assert d["cost"]["8"]["delta"] > d["cost"]["0"]["delta"], d["cost"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
