"""`e378` runs the cue source at the tight step with the larger step size, so the tests pin the two-comparison
configuration check, the curve's licence, both faces of the five claims and the live row's four artifacts.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e378_the_cue_source_at_the_tight_step as e378


def _run(lr=0.03, diag=0.60, cue_step=8, reps=20, tasks=3, drive_from_cue=True, batch=32, iters=500,
         basis="cell_class", channel=0.30, forget=0.05):
    coupling = e378.COUPLING_SHA1 if drive_from_cue else "5326f4a0edb4"
    return {
        "config": {"loop_cue_at": cue_step, "loop_drive_from_cue": drive_from_cue, "loop_world_leak": 0.35,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": 8,
                   "loop_world_modes": 0, "loop_world_nonlinear": False, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": 0, "iters": iters, "lr": lr,
                   "batch": batch},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "cw" if drive_from_cue else "aw",
                     "world_read_sha1": "cr" if drive_from_cue else "r", "world_leak": 0.35, "world_coupled": True,
                     "world_coupling_sha1": coupling, "world_nonlinear": False, "drive_from_cue": drive_from_cue,
                     "cue_at": cue_step, "cue_sha1": "c", "action_sha1": "c" if drive_from_cue else "a",
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


def _curve(cue8=0.8906, world_sd=0.0600):
    cells = {f"{s}@{t}": {"accuracy": 0.70, "world_sd": 0.10} for s in ("cue", "action") for t in range(12)}
    cells["cue@8"] = {"accuracy": cue8, "world_sd": world_sd}
    return {"cells": cells}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _judge(stepped=_run(lr=0.03, diag=0.6000), base=_run(lr=0.003, diag=0.4368),
           wide=_run(lr=0.003, diag=0.8399, cue_step=0), curve=_curve()):
    doc = e378.reading(stepped_path=_write(stepped) if stepped is not None else Path("runs/absent_s.json"),
                       base_path=_write(base) if base is not None else Path("runs/absent_b.json"),
                       wide_path=_write(wide) if wide is not None else Path("runs/absent_w.json"),
                       curve=_write(curve) if curve is not None else Path("runs/absent_c.json"))
    return {row["id"]: row for row in e378.judge(doc)}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("Y1", "Y2", "Y3", "Y4", "Y5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # Y1: a step size that was not moved, a source that is not this one, an iteration budget that moved
    assert _judge(stepped=_run(lr=0.003, diag=0.60))["Y1"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.60, drive_from_cue=False))["Y1"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.60, iters=2000))["Y1"]["verdict"].startswith("FALSIFIER")
    assert _judge(base=None)["Y1"]["verdict"].startswith("REFUSED")
    assert _judge(wide=None)["Y1"]["verdict"].startswith("REFUSED")

    # Y2: a world at rest at this step, a cell at chance, and the curve absent
    assert _judge(curve=_curve(world_sd=0.0))["Y2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=_curve(cue8=0.26))["Y2"]["verdict"].startswith("FALSIFIER")
    assert _judge(curve=None)["Y2"]["verdict"].startswith("REFUSED")

    # Y3: a larger step that buys this source nothing, and one whose gain is too small to call
    assert _judge(stepped=_run(lr=0.03, diag=0.4500))["Y3"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.4700))["Y3"]["verdict"].startswith("NULL")

    # Y4: a tight step that costs nothing at all, and one whose shortfall is too small to call
    assert _judge(stepped=_run(lr=0.03, diag=0.8200))["Y4"]["verdict"].startswith("FALSIFIER")
    assert _judge(stepped=_run(lr=0.03, diag=0.7700))["Y4"]["verdict"].startswith("NULL")

    # Y5: an arm whose answer is not earned
    assert _judge(stepped=_run(lr=0.03, diag=0.60, channel=0.01))["Y5"]["verdict"].startswith("FALSIFIER")

    #: the stepped run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e378.judge(e378.reading(
        stepped_path=Path("runs/absent_q.json"), base_path=_write(_run(lr=0.003)),
        wide_path=_write(_run(lr=0.003, cue_step=0)), curve=_write(_curve()))))


def test_the_live_row_holds_the_source_and_moves_the_two_knobs():
    p = Path("runs/e378_the_cue_source_at_the_tight_step.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e378.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e378.judge(d)}
    for cid in ("Y1", "Y2"):
        assert verdicts[cid].startswith("MET"), (cid, verdicts[cid])
    #: one source, two steps, two step sizes, and nothing else moving
    assert d["facts"]["stepped"]["lr"] == 0.03 and d["facts"]["stepped"]["loop_cue_at"] == 8, d["facts"]["stepped"]
    assert d["facts"]["base"]["lr"] == 0.003 and d["facts"]["base"]["loop_cue_at"] == 8, d["facts"]["base"]
    assert d["facts"]["wide"]["loop_cue_at"] == 0, d["facts"]["wide"]
    assert d["facts"]["stepped"]["world_coupling_sha1"] == e378.COUPLING_SHA1, d["facts"]["stepped"]
    assert abs(d["probe"]["accuracy"] - 0.8906) < 1e-4, d["probe"]
    assert d["gain"] is not None and d["shortfall"] is not None, sorted(d)
    for key in (f"stepped_{e378.NAIVE}", f"stepped_{e378.REPLAY}"):
        assert d["rows"][key]["n"] == e378.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
