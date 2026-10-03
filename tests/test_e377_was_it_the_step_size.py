"""`e377` runs the plastic body at the tight step with the larger step size, so the tests pin the two-pair
configuration check, the curve's licence, both faces of the five claims and the live two-by-two.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e377_was_it_the_step_size as e377


def _run(lr=0.03, diag=0.60, frozen_body=False, reps=20, tasks=3, frozen_bias=False, batch=32, iters=500,
         basis="cell_class", channel=0.30, forget=0.0):
    return {
        "config": {"loop_cue_at": 8, "loop_drive_from_cue": False, "loop_world_leak": 0.35, "loop_world_coupled": True,
                   "readout_from_world": True, "loop_world_dims": 8, "loop_world_modes": 0,
                   "loop_world_nonlinear": False, "closed_loop": True, "repeats": reps, "circuit_size": 300,
                   "readout_size": 32, "basis": basis, "seed0": 0, "iters": iters, "lr": lr, "batch": batch,
                   "frozen_body": frozen_body, "frozen_bias": frozen_bias},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "aw", "world_read_sha1": "r", "world_leak": 0.35,
                     "world_coupled": True, "world_coupling_sha1": e377.COUPLING_SHA1, "world_nonlinear": False,
                     "drive_from_cue": False, "cue_at": 8, "cue_sha1": "c", "action_sha1": "a", "feedback_sha1": "f",
                     "n_cue": 12, "n_action": 8},
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


def _curve(accuracy=0.7617, world_sd=0.0478):
    cells = {f"{s}@{t}": {"accuracy": 0.70, "world_sd": 0.10} for s in ("cue", "action") for t in range(12)}
    cells["action@8"] = {"accuracy": accuracy, "world_sd": world_sd}
    return {"cells": cells}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(stepped=_run(lr=0.03, diag=0.5800, frozen_body=False),
           plastic=_run(lr=0.003, diag=0.2333, frozen_body=False),
           frozen=_run(lr=0.03, diag=0.6455, frozen_body=True), curve=_curve()):
    doc = e377.reading(stepped_path=_write(stepped) if stepped is not None else Path("runs/absent_s.json"),
                       plastic_path=_write(plastic) if plastic is not None else Path("runs/absent_p.json"),
                       frozen_path=_write(frozen) if frozen is not None else Path("runs/absent_f.json"),
                       curve=_write(curve) if curve is not None else Path("runs/absent_c.json"))
    return {row["id"]: row for row in e377.judge(doc)}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("W1", "W2", "W3", "W4", "W5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # W1: a step size that was not moved, a body frozen when it should not be, an iteration budget that moved
    assert _judge(stepped=_run(lr=0.003, diag=0.60))["W1"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.60, frozen_body=True))["W1"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.60, iters=2000))["W1"]["verdict"].startswith("FALSIFIER")
    assert _judge(plastic=None)["W1"]["verdict"].startswith("REFUSED")
    assert _judge(frozen=None)["W1"]["verdict"].startswith("REFUSED")

    # W2: a world at rest at this step, a cell at chance, and the curve absent
    assert _judge(curve=_curve(world_sd=0.0))["W2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=_curve(accuracy=0.26))["W2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=None)["W2"]["verdict"].startswith("REFUSED")

    # W3: a larger step that buys the plastic body nothing, and one whose gain is too small to call
    assert _judge(stepped=_run(lr=0.03, diag=0.2500))["W3"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.3000))["W3"]["verdict"].startswith("NULL")

    # W4: a plastic body that matches the frozen one at this step size, and one whose shortfall is too small
    assert _judge(stepped=_run(lr=0.03, diag=0.6400))["W4"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.6200))["W4"]["verdict"].startswith("NULL")

    # W5: an arm whose answer is not earned
    assert _judge(stepped=_run(lr=0.03, diag=0.60, channel=0.01))["W5"]["verdict"].startswith("FALSIFIER")

    #: the stepped run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e377.judge(e377.reading(
        stepped_path=Path("runs/absent_z.json"), plastic_path=_write(_run(lr=0.003)),
        frozen_path=_write(_run(lr=0.03, frozen_body=True)), curve=_write(_curve()))))


def test_the_live_two_by_two_holds_everything_but_the_two_knobs():
    p = Path("runs/e377_was_it_the_step_size.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e377.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e377.judge(d)}
    for cid in ("W1", "W2"):
        assert verdicts[cid].startswith("MET"), (cid, verdicts[cid])
    #: the two-by-two: two step sizes against a plastic and a frozen body, with the new run in one cell of it
    assert d["facts"]["stepped"]["lr"] == 0.03 and d["facts"]["stepped"]["frozen_body"] is False, d["facts"]["stepped"]
    assert d["facts"]["plastic"]["lr"] == 0.003 and d["facts"]["plastic"]["frozen_body"] is False, d["facts"]["plastic"]
    assert d["facts"]["frozen"]["lr"] == 0.03 and d["facts"]["frozen"]["frozen_body"] is True, d["facts"]["frozen"]
    assert abs(d["probe"]["accuracy"] - 0.7617) < 1e-4, d["probe"]
    #: and both paired comparisons are in the reading rather than in a plan row
    assert d["over_steps"] is not None and d["body_cost"] is not None, sorted(d)
    for key in (f"stepped_{e377.NAIVE}", f"stepped_{e377.REPLAY}"):
        assert d["rows"][key]["n"] == e377.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
