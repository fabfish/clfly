"""`e390` samples the wide step's recovery between `e389`'s twenty updates and `e380`'s five hundred, so the tests
pin both faces of the five claims, the refusal when a run or an end is absent, and the live climb the unit exists to
put a shape on.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e390_where_the_climb_starts as e390


def _facts(lr=0.003, iters=1, repeats=20):
    return {"lr": lr, "batch": 32, "iters": iters, "repeats": repeats, "loop_cue_at": 0, "basis": "cell_class",
            "circuit_size": 300, "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True,
            "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r",
            "world_drive_sha1": "aw", "world_coupling_sha1": "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


#: the climb the corpus has: flat at twenty, climbing through the samples, recovered by five hundred
GOOD = {20: 0.574, 30: 0.60, 45: 0.63, 65: 0.66, 85: 0.68, 100: 0.70, 500: 0.7792}
GOOD_SEM = {20: 0.024, 30: 0.021, 45: 0.027, 65: 0.022, 85: 0.025, 100: 0.023, 500: 0.021}


def _doc(probe=GOOD, sem=GOOD_SEM, ok=True, reason="absent", facts=None):
    if not ok:
        #: `reading` refuses the whole unit when a run's weights or one of the two ends is absent
        return {"ok": False, "budgets": {}, "facts": {}, "ends": {}, "reason": reason}
    budgets = {str(b): {"run": "r.json", "iters": b, "repeats": 20, "probe_task_0": probe[b],
                        "per_rep_task_0": [probe[b]] * 20, "sem_task_0": sem[b], "head_task_0": 0.20}
               for b in e390.NEW}
    ends = {str(b): {"source": "e389.json" if b == e390.NEAR_AT else "e380.json", "probe_task_0": probe[b],
                     "sem_task_0": sem[b], "head_task_0": 0.25} for b in (e390.NEAR_AT, e390.FAR_AT)}
    window = {b: v for b, v in probe.items() if e390.NEAR_AT <= b <= 100}
    return {"ok": True, "budgets": budgets, "ends": ends,
            "facts": facts if facts is not None else {str(b): _facts(iters=b) for b in list(e390.NEW) + [e390.FAR_AT]},
            "reference": {"artifact": "e389.json", "facts": {"1": _facts(iters=1, repeats=5)}},
            "climb": {"budgets": sorted(window), "low": min(window.values()), "high": max(window.values()),
                      "span": max(window.values()) - min(window.values()),
                      "sems": {str(b): sem[b] for b in window},
                      "worst_sem": max(sem[b] for b in window)},
            "arm": e390.NAIVE, "reps": e390.REPS}


def _judge(**kw):
    return {row["id"]: row for row in e390.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: flat at twenty, climbing through the samples, recovered by five hundred: the shape this unit exists to find
    j = _judge()
    for cid in ("K1", "K2", "K3", "K4", "K5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # K1: a field other than the budget moved, on a new run and on the far end
    bad = {str(b): _facts(iters=b) for b in list(e390.NEW) + [e390.FAR_AT]}
    bad["45"] = {**bad["45"], "lr": 0.03}
    assert _judge(facts=bad)["K1"]["verdict"].startswith("FALSIFIER")
    bad2 = {str(b): _facts(iters=b) for b in list(e390.NEW) + [e390.FAR_AT]}
    bad2[str(e390.FAR_AT)] = {**bad2[str(e390.FAR_AT)], "batch": 16}
    assert _judge(facts=bad2)["K1"]["verdict"].startswith("FALSIFIER")

    # K2: a far end that is not above the near end, and one between the bars
    assert _judge(probe={**GOOD, 500: 0.60})["K2"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 500: 0.65})["K2"]["verdict"].startswith("NULL")

    # K3: a hundred still on the floor, and a lift between the bars
    assert _judge(probe={**GOOD, 100: 0.56})["K3"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 100: 0.58})["K3"]["verdict"].startswith("NULL")

    # K4: a budget below its predecessor, and one only equal to it
    assert _judge(probe={**GOOD, 65: 0.61})["K4"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 45: 0.60})["K4"]["verdict"].startswith("FALSIFIER")

    # K5: a climb inside the measurement, and one between the bars
    assert _judge(sem={b: 0.07 for b in GOOD_SEM})["K5"]["verdict"].startswith("FALSIFIER")
    assert _judge(sem={b: 0.05 for b in GOOD_SEM})["K5"]["verdict"].startswith("NULL")

    #: a run's weights or one of the two ends absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e390.judge(_doc(ok=False)))


def test_the_series_is_the_two_ends_and_the_new_budgets():
    r = _doc()
    series = e390._series(r)
    assert sorted(series) == [20, 30, 45, 65, 85, 100, 500], sorted(series)
    assert series[20] == r["ends"]["20"]["probe_task_0"]
    assert series[500] == r["ends"]["500"]["probe_task_0"]
    assert series[45] == r["budgets"]["45"]["probe_task_0"]
    #: the standard error of an end comes from the artifact that measured it, and of a new budget from this unit
    assert e390._sem(r, 20) == r["ends"]["20"]["sem_task_0"]
    assert e390._sem(r, 45) == r["budgets"]["45"]["sem_task_0"]


def test_the_live_climb_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e390_where_the_climb_starts.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e390.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e390.judge(d)}
    #: the configuration is structural, and the two ends come from the units that measured them
    assert verdicts["K1"].startswith("MET"), (verdicts["K1"], d["budgets"].keys())
    assert d["ends"]["20"]["source"].startswith("e389")
    assert d["ends"]["500"]["source"].startswith("e380")
    #: the climb is sampled at more than three budgets and the ends bound it
    series = e390._series(d)
    window = [b for b in series if e390.NEAR_AT <= b <= 100]
    assert len(window) >= 5, window
    assert max(series) == e390.FAR_AT, series
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
