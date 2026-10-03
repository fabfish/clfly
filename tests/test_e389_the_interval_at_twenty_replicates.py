"""`e389` re-rolls the wide step's interval at twenty replicates, so the tests pin both faces of the five claims,
the refusal when a run is absent, the band's own arithmetic, and the live artifact whose series the unit exists to
decide.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e389_the_interval_at_twenty_replicates as e389


def _facts(lr=0.003, iters=1, repeats=20):
    return {"lr": lr, "batch": 32, "iters": iters, "repeats": repeats, "loop_cue_at": 0, "basis": "cell_class",
            "circuit_size": 300, "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True,
            "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r",
            "world_drive_sha1": "aw", "world_coupling_sha1": "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


#: a series that turns strictly inside (5, 20): down to 8, up the rest of the way
GOOD = {1: 0.68, 2: 0.59, 3: 0.575, 4: 0.565, 5: 0.57, 6: 0.55, 8: 0.53, 11: 0.55, 14: 0.565, 17: 0.58, 20: 0.595}
#: and the standard errors the twenty replicates would have to show
GOOD_SEM = {1: 0.019, 2: 0.018, 3: 0.016, 4: 0.020, 5: 0.022, 6: 0.012, 8: 0.025, 11: 0.025, 14: 0.021, 17: 0.024,
            20: 0.022}
FIVE_REP = {"6": 0.0232, "8": 0.0546, "11": 0.0541, "14": 0.0409, "17": 0.0538}


def _doc(probe=GOOD, sem=GOOD_SEM, ok=True, reason="absent", facts=None):
    if not ok:
        #: `reading` refuses the whole unit when a run's weights are absent, since the series is the measurement
        return {"ok": False, "budgets": {}, "facts": {}, "previous": None, "reason": reason}
    budgets = {str(b): {"run": "r.json", "iters": b, "repeats": 20, "probe_task_0": v,
                        "per_rep_task_0": [v] * 20, "sem_task_0": sem[b], "initial_task_0": 0.6875,
                        "head_task_0": 0.20} for b, v in probe.items()}
    window = {b: v for b, v in probe.items() if e389.LOW <= b <= e389.HIGH}
    worst = max(sem[b] for b in window)
    return {"ok": True, "budgets": budgets,
            "facts": facts if facts is not None else {str(b): _facts(iters=b) for b in e389.BUDGETS},
            "previous": {"artifact": "e388.json", "reps": 5, "sems": FIVE_REP, "readings": {},
                         "band": {"worst_sem": 0.0546, "span": 0.0583}, "facts": {"1": _facts(iters=1, repeats=5)}},
            "band": {"budgets": sorted(window), "low": min(window.values()), "high": max(window.values()),
                     "span": max(window.values()) - min(window.values()),
                     "min_budget": min(window, key=lambda b: window[b]),
                     "sems": {str(b): sem[b] for b in window}, "worst_sem": worst, "five_rep_worst": 0.0546},
            "arm": e389.NAIVE, "reps": e389.REPS}


def _judge(**kw):
    return {row["id"]: row for row in e389.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: a resolved interval that turns: the shape this unit exists to either find or rule out
    j = _judge()
    for cid in ("J1", "J2", "J3", "J4", "J5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # J1: a field other than the budget and the replicates moved
    bad = {str(b): _facts(iters=b) for b in e389.BUDGETS}
    bad["8"] = {**bad["8"], "lr": 0.03}
    assert _judge(facts=bad)["J1"]["verdict"].startswith("FALSIFIER")

    # J2: an error above the bar, and one between the bars
    assert _judge(sem={**GOOD_SEM, 8: 0.040})["J2"]["verdict"].startswith("FALSIFIER")
    assert _judge(sem={**GOOD_SEM, 8: 0.032})["J2"]["verdict"].startswith("NULL")

    # J3: an interval still flat within the instrument, and one between the bars
    assert _judge(sem={b: 0.045 for b in GOOD_SEM})["J3"]["verdict"].startswith("FALSIFIER")
    assert _judge(sem={b: 0.036 for b in GOOD_SEM})["J3"]["verdict"].startswith("NULL")

    # J4: a rise on the way in, a fall on the way out, a plateau, and a floor at an end
    assert _judge(probe={**GOOD, 8: 0.52})["J4"]["verdict"].startswith("MET")
    assert _judge(probe={**GOOD, 11: 0.53})["J4"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 14: 0.50})["J4"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 6: 0.53, 8: 0.53, 11: 0.535})["J4"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 5: 0.50})["J4"]["verdict"].startswith("FALSIFIER")

    # J5: a floor within the falsifier's bar of five, and one between the bars
    assert _judge(probe={**GOOD, 5: 0.535, 6: 0.53, 8: 0.527})["J5"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe={**GOOD, 5: 0.538, 6: 0.53, 8: 0.525, 11: 0.538})["J5"]["verdict"].startswith("NULL")

    #: a run's weights absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e389.judge(_doc(ok=False)))


def test_the_band_is_the_arithmetic_of_the_series():
    r = _doc()
    band = r["band"]
    assert band["span"] == 0.595 - 0.53, band
    assert band["min_budget"] == 8, band
    #: the widest standard error is over the interval only, and the five-replicate bar is carried through
    assert band["worst_sem"] == 0.025, band
    assert band["five_rep_worst"] == 0.0546, band
    #: a standard deviation over identical replicates is zero, not an error
    assert e389._series(r, "readings")[8] == 0.53
    assert statistics.stdev([0.5] * 20) == 0.0


def test_the_live_reading_decides_the_interval_and_carries_no_counted_keys():
    p = Path("runs/e389_the_interval_at_twenty_replicates.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e389.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e389.judge(d)}
    #: the configuration is structural, and every budget was rolled at this unit's own replicate count
    assert verdicts["J1"].startswith("MET"), (verdicts["J1"], d["budgets"].keys())
    assert all(v["repeats"] == e389.REPS for v in d["budgets"].values()), d["budgets"].keys()
    #: the interval is sampled at more than five budgets and every one of them carries its own standard error
    window = [b for b in e389._series(d, "readings") if e389.LOW <= b <= e389.HIGH]
    assert len(window) >= 5, window
    assert len(d["band"]["sems"]) == len(window), (d["band"]["sems"], window)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
