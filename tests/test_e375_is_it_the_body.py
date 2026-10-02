"""`e375` freezes the body and asks whether the plastic one's training is what loses the reading, so the tests pin
the one-field configuration check, the curve's licence, both faces of the five claims and the live triple.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e375_is_it_the_body as e375


def _run(frozen_body=False, diag=0.70, reps=20, tasks=3, basis="cell_class", iters=500, channel=0.30, forget=0.35,
         frozen_bias=False, source_step=8):
    return {
        "config": {"loop_cue_at": source_step, "loop_drive_from_cue": False, "loop_world_leak": 0.35,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": 8,
                   "loop_world_modes": 0, "loop_world_nonlinear": False, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": 0, "iters": iters,
                   "frozen_body": frozen_body, "frozen_bias": frozen_bias},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "aw", "world_read_sha1": "r", "world_leak": 0.35,
                     "world_coupled": True, "world_coupling_sha1": e375.COUPLING_SHA1, "world_nonlinear": False,
                     "drive_from_cue": False, "cue_at": source_step, "cue_sha1": "c", "action_sha1": "a",
                     "feedback_sha1": "f", "n_cue": 12, "n_action": 8},
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
    cells = {f"cue@{s}": {"accuracy": 0.80, "world_sd": 0.10, "trial_range": 0.5} for s in range(12)}
    cells.update({f"action@{s}": {"accuracy": 0.70, "world_sd": 0.10, "trial_range": 0.5} for s in range(12)})
    cells["action@8"] = {"accuracy": accuracy, "world_sd": world_sd, "trial_range": 0.02}
    return {"cells": cells}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(frozen=_run(frozen_body=True, diag=0.70), plastic=_run(frozen_body=False, diag=0.2333), curve=_curve()):
    doc = e375.reading(frozen_path=_write(frozen) if frozen is not None else Path("runs/absent_frozen.json"),
                       plastic_path=_write(plastic) if plastic is not None else Path("runs/absent_plastic.json"),
                       curve=_write(curve) if curve is not None else Path("runs/absent_curve.json"))
    return {row["id"]: row for row in e375.judge(doc)}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("U1", "U2", "U3", "U4", "U5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # U1: a body that was not frozen, a shared field moved, a bias frozen as well, and the control absent
    assert _judge(frozen=_run(frozen_body=False, diag=0.70))["U1"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_run(frozen_body=True, diag=0.70, basis="neuron"))["U1"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_run(frozen_body=True, diag=0.70, frozen_bias=True))["U1"]["verdict"].startswith("FALSIFIER")
    assert _judge(plastic=None)["U1"]["verdict"].startswith("REFUSED")

    # U2: a world at rest at this step, a cell at chance, and the curve absent
    assert _judge(curve=_curve(world_sd=0.0))["U2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=_curve(accuracy=0.26))["U2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=None)["U2"]["verdict"].startswith("REFUSED")

    # U3: a frozen body that does not train either, which is the refutation the claim names
    assert _judge(frozen=_run(frozen_body=True, diag=0.26))["U3"]["verdict"].startswith("FALSIFIER")

    # U4: a frozen body that recovers nothing, and one whose gain is too small to call
    assert _judge(frozen=_run(frozen_body=True, diag=0.28))["U4"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_run(frozen_body=True, diag=0.30))["U4"]["verdict"].startswith("NULL")

    # U5: an arm whose answer is not earned with the body frozen
    assert _judge(frozen=_run(frozen_body=True, diag=0.70, channel=0.01))["U5"]["verdict"].startswith("FALSIFIER")

    #: the frozen run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e375.judge(e375.reading(
        frozen_path=Path("runs/absent_x.json"), plastic_path=_write(_run(frozen_body=False)),
        curve=_write(_curve()))))


def test_the_probe_cell_is_read_by_source_and_step():
    cell = e375.probe_cell(_write(_curve()), "action", 8)
    assert cell and abs(cell["accuracy"] - 0.7617) < 1e-12 and abs(cell["world_sd"] - 0.0478) < 1e-12, cell
    #: another source or another step of the same curve is a different cell
    assert e375.probe_cell(_write(_curve()), "cue", 8)["accuracy"] != cell["accuracy"]
    assert e375.probe_cell(_write(_curve()), "action", 9)["accuracy"] == 0.70
    assert e375.probe_cell(Path("runs/does_not_exist.json")) is None


def test_the_live_reading_freezes_one_field_and_pairs_the_two_bodies():
    p = Path("runs/e375_is_it_the_body.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e375.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e375.judge(d)}
    #: the manipulation and the licence are structural facts about the two runs and the curve
    for cid in ("U1", "U2"):
        assert verdicts[cid].startswith("MET"), (cid, verdicts[cid])
    assert d["facts"]["frozen"]["frozen_body"] is True, d["facts"]["frozen"]
    assert d["facts"]["plastic"]["frozen_body"] is False, d["facts"]["plastic"]
    #: and the three numbers the account needed are all in the reading
    assert abs(d["probe"]["accuracy"] - 0.7617) < 1e-4, d["probe"]
    assert d["recovery"] is not None and d["recovery"]["n"] == e375.REPLICATES, d["recovery"]
    for key in (f"frozen_{e375.NAIVE}", f"frozen_{e375.REPLAY}"):
        assert d["rows"][key]["n"] == e375.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
