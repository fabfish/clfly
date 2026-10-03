"""`e388` samples five budgets inside the interval `e385` registered as holding the wide step's floor, so the tests
pin both faces of the five claims, the refusal when a run or the previous series is absent, and the live series
whose minimum the unit exists to locate.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e388_the_floor_between_five_and_twenty as e388


def _facts(lr=0.003, iters=1, repeats=5):
    return {"lr": lr, "batch": 32, "iters": iters, "repeats": repeats, "loop_cue_at": 0, "basis": "cell_class",
            "circuit_size": 300, "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True,
            "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r",
            "world_drive_sha1": "aw", "world_coupling_sha1": "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


#: the series the corpus has: falling to five, a floor inside (5, 20), recovered by twenty
GOOD = (0.55, 0.53, 0.555, 0.565, 0.575)
GOOD_HEAD = (0.20, 0.19, 0.22, 0.23, 0.24)


def _doc(probe=GOOD, head=GOOD_HEAD, ok=True, reason="absent", previous=True, facts=None, prev=None):
    if not ok or not previous:
        #: `reading` refuses the whole unit when a run or the previous series is absent, since it is half the series
        return {"ok": False, "budgets": {}, "facts": {}, "previous": None, "reason": reason}
    budgets = {str(b): {"run": "r.json", "iters": b, "probe_task_0": p, "initial_task_0": 0.6875,
                        "head_task_0": h} for b, p, h in zip(e388.NEW, probe, head)}
    readings = {"1": 0.6792, "5": 0.55, "20": 0.5875, "100": 0.70, "500": 0.7792}
    if prev:
        readings.update(prev)
    return {"ok": True, "budgets": budgets,
            "facts": facts if facts is not None else {str(b): _facts(iters=b) for b in e388.NEW},
            "previous": {"artifact": "e385.json", "readings": readings,
                         "heads": {"1": 0.0833, "5": 0.2083, "20": 0.25, "100": 0.3333, "500": 0.75},
                         "initials": {str(b): 0.6875 for b in (1, 5, 20, 100, 500)},
                         "facts": {"1": _facts(iters=1)}},
            "arm": e388.NAIVE, "reps": e388.SWEEP_REPS}


def _judge(**kw):
    return {row["id"]: row for row in e388.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape the corpus has at these budgets: an interior floor below five and recovered by twenty
    j = _judge()
    for cid in ("I1", "I2", "I3", "I4", "I5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])
    assert "8" in j["I2"]["measured"], j["I2"]

    # I1: a field other than the budget moved
    bad = {str(b): _facts(iters=b) for b in e388.NEW}
    bad["11"] = {**bad["11"], "lr": 0.03}
    assert _judge(facts=bad)["I1"]["verdict"].startswith("FALSIFIER")

    # I2: a floor at the low end, a floor at the high end, and a plateau rather than a turn
    assert _judge(prev={"5": 0.50}, probe=(0.60, 0.59, 0.58, 0.57, 0.56))["I2"]["verdict"].startswith("FALSIFIER")
    assert _judge(prev={"5": 0.60}, probe=(0.60, 0.60, 0.598, 0.595, 0.592))["I2"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe=(0.55, 0.55, 0.55, 0.56, 0.58))["I2"]["verdict"].startswith("FALSIFIER")
    #: and the corpus's own shape turns, which is the face this unit exists to find
    assert _judge()["I2"]["verdict"].startswith("MET")

    # I3: the dip does not continue past five, and one between the bars
    assert _judge(probe=(0.545, 0.544, 0.55, 0.56, 0.575))["I3"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe=(0.535, 0.534, 0.55, 0.56, 0.575))["I3"]["verdict"].startswith("NULL")

    # I4: the valley still deepening at twenty, and one whose recovery is too small to call
    assert _judge(prev={"20": 0.548}, probe=(0.552, 0.55, 0.549, 0.546, 0.547))["I4"]["verdict"].startswith("FALSIFIER")
    assert _judge(prev={"20": 0.558}, probe=(0.552, 0.55, 0.549, 0.546, 0.547))["I4"]["verdict"].startswith("NULL")

    # I5: a head already steering where the world sits lowest
    assert _judge(head=(0.20, 0.80, 0.22, 0.23, 0.24))["I5"]["verdict"].startswith("FALSIFIER")

    #: a run or the previous series absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e388.judge(_doc(ok=False)))
    assert all(row["verdict"].startswith("REFUSED") for row in e388.judge(_doc(previous=False)))


def test_the_series_joins_the_previous_artifact_and_the_new_runs():
    r = _doc()
    series = e388._series(r, "readings")
    assert sorted(series) == [1, 5, 6, 8, 11, 14, 17, 20, 100, 500], sorted(series)
    assert series[8] == r["budgets"]["8"]["probe_task_0"]
    assert series[20] == r["previous"]["readings"]["20"]
    heads = e388._series(r, "heads")
    assert heads[8] == r["budgets"]["8"]["head_task_0"]
    assert heads[5] == r["previous"]["heads"]["5"]


def test_the_live_reading_locates_the_floor_and_carries_no_counted_keys():
    p = Path("runs/e388_the_floor_between_five_and_twenty.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e388.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e388.judge(d)}
    #: the configuration is structural: one cell, the budget the only thing that moved
    assert verdicts["I1"].startswith("MET"), (verdicts["I1"], d["budgets"].keys())
    #: and the new samples join the series `e385` read, so the interval holds at least seven readings
    series = e388._series(d, "readings")
    window = {b: v for b, v in series.items() if e388.LOW <= b <= e388.HIGH}
    assert len(window) >= 7, sorted(window)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
