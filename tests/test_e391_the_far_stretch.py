"""`e391` samples the four hundred updates `e390` left unmeasured, so the tests pin both faces of the five claims,
the refusal when a run or an end is absent, and the live stretch whose gain the unit exists to place.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e391_the_far_stretch as e391


def _facts(lr=0.003, iters=1, repeats=20):
    return {"lr": lr, "batch": 32, "iters": iters, "repeats": repeats, "loop_cue_at": 0, "basis": "cell_class",
            "circuit_size": 300, "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True,
            "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r",
            "world_drive_sha1": "aw", "world_coupling_sha1": "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


#: the stretch the corpus has: a hundred at 0.6385, climbing through the samples, five hundred at 0.7729
GOOD = {100: 0.6385, 150: 0.67, 275: 0.71, 425: 0.75, 500: 0.7729}
GOOD_SEM = {100: 0.0188, 150: 0.021, 275: 0.023, 425: 0.022, 500: 0.0153}


def _doc(probe=GOOD, sem=GOOD_SEM, ok=True, reason="absent", facts=None):
    if not ok:
        #: `reading` refuses the whole unit when a run's weights or one of the two ends is absent
        return {"ok": False, "budgets": {}, "facts": {}, "ends": {}, "reason": reason}
    budgets = {str(b): {"run": "r.json", "iters": b, "repeats": 20, "probe_task_0": probe[b],
                        "per_rep_task_0": [probe[b]] * 20, "sem_task_0": sem[b], "head_task_0": 0.40}
               for b in e391.NEW}
    ends = {str(b): {"source": "e390.json" if b == e391.NEAR_LOW else "e380.json", "probe_task_0": probe[b],
                     "sem_task_0": sem[b], "head_task_0": 0.33} for b in (e391.NEAR_LOW, e391.NEAR_HIGH)}
    window = {b: v for b, v in probe.items() if e391.NEAR_LOW <= b <= e391.NEAR_HIGH}
    return {"ok": True, "budgets": budgets, "ends": ends,
            "facts": facts if facts is not None else {str(b): _facts(iters=b)
                                                      for b in list(e391.NEW) + [e391.NEAR_HIGH]},
            "reference": {"artifact": "e390.json", "facts": {"1": _facts(iters=1, repeats=5)}},
            "stretch": {"budgets": sorted(window), "low": min(window.values()), "high": max(window.values()),
                        "span": max(window.values()) - min(window.values()),
                        "sems": {str(b): sem[b] for b in window},
                        "worst_sem": max(sem[b] for b in window),
                        "gain": probe[e391.NEAR_HIGH] - probe[e391.NEAR_LOW],
                        "whole": probe[e391.NEAR_HIGH] - e391.FLOOR,
                        "front_loaded": probe[e391.NEAR_LOW] - e391.FLOOR},
            "arm": e391.NAIVE, "reps": e391.REPS}


def _judge(**kw):
    return {row["id"]: row for row in e391.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: a hundred at 0.6385, climbing through the samples, five hundred at 0.7729: the shape this unit exists to find
    j = _judge()
    for cid in ("L1", "L2", "L3", "L4", "L5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # L1: a field other than the budget moved, on a new run and on the far end
    bad = {str(b): _facts(iters=b) for b in list(e391.NEW) + [e391.NEAR_HIGH]}
    bad["275"] = {**bad["275"], "lr": 0.03}
    assert _judge(facts=bad)["L1"]["verdict"].startswith("FALSIFIER")
    bad2 = {str(b): _facts(iters=b) for b in list(e391.NEW) + [e391.NEAR_HIGH]}
    bad2[str(e391.NEAR_HIGH)] = {**bad2[str(e391.NEAR_HIGH)], "batch": 16}
    assert _judge(facts=bad2)["L1"]["verdict"].startswith("FALSIFIER")

    # L2: a far end that buys nothing, and one between the bars
    assert _judge(probe={**GOOD, 500: 0.64})["L2"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 500: 0.67})["L2"]["verdict"].startswith("NULL")

    # L3: a budget below its predecessor, and one only equal to it
    assert _judge(probe={**GOOD, 275: 0.66})["L3"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 150: 0.6385})["L3"]["verdict"].startswith("FALSIFIER")

    # L4: a stretch inside the measurement, and one between the bars
    assert _judge(sem={b: 0.09 for b in GOOD_SEM})["L4"]["verdict"].startswith("FALSIFIER")
    assert _judge(sem={b: 0.06 for b in GOOD_SEM})["L4"]["verdict"].startswith("NULL")

    # L5: a recovery front-loaded on the floor-to-hundred leg
    assert _judge(probe={**GOOD, 100: 0.70})["L5"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 100: 0.68})["L5"]["verdict"].startswith("FALSIFIER")

    #: a run's weights or one of the two ends absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e391.judge(_doc(ok=False)))


def test_the_series_is_the_two_ends_and_the_new_budgets():
    r = _doc()
    series = e391._series(r)
    assert sorted(series) == [100, 150, 275, 425, 500], sorted(series)
    assert series[100] == r["ends"]["100"]["probe_task_0"]
    assert series[500] == r["ends"]["500"]["probe_task_0"]
    assert series[275] == r["budgets"]["275"]["probe_task_0"]
    assert e391._sem(r, 100) == r["ends"]["100"]["sem_task_0"]
    assert e391._sem(r, 425) == r["budgets"]["425"]["sem_task_0"]


def test_the_live_stretch_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e391_the_far_stretch.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e391.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e391.judge(d)}
    #: the configuration is structural, and the two ends come from the units that measured them
    assert verdicts["L1"].startswith("MET"), (verdicts["L1"], d["budgets"].keys())
    assert d["ends"]["100"]["source"].startswith("e390")
    assert d["ends"]["500"]["source"].startswith("e380")
    #: the stretch is sampled at more than three budgets and the ends bound it
    series = e391._series(d)
    window = [b for b in series if e391.NEAR_LOW <= b <= e391.NEAR_HIGH]
    assert len(window) >= 5, window
    assert max(series) == e391.NEAR_HIGH, series
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
