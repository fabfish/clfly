"""`e385` resolves the wide step's valley to three more budgets, so the tests pin both faces of the five claims, the
refusal when a run or the previous series is absent, and the live shape's own overlap.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e385_the_valleys_shape as e385


def _facts(lr=0.003, iters=1, repeats=5):
    return {"lr": lr, "batch": 32, "iters": iters, "repeats": repeats, "loop_cue_at": 0, "basis": "cell_class",
            "circuit_size": 300, "readout_size": 32, "seed0": 0, "closed_loop": True, "readout_from_world": True,
            "loop_world_dims": 8, "loop_world_leak": 0.35, "loop_world_modes": 0, "loop_world_nonlinear": False,
            "task_names": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "task_readout_widths": [8],
            "cue_sha1": "c", "feedback_sha1": "f", "action_sha1": "a", "world_read_sha1": "r",
            "world_drive_sha1": "aw", "world_coupling_sha1": "5326f4a0edb4", "n_cue": 12, "n_action": 8,
            "drive_from_cue": False, "loop_drive_from_cue": False}


def _doc(probe=(0.68, 0.59, 0.575, 0.5625, 0.55), head=(0.08, 0.10, 0.15, 0.18, 0.2083), ok=True, reason="absent",
         previous=True, overlap=0.0, facts=None):
    if not ok or not previous:
        #: `reading` refuses the whole unit when the previous series is absent, since that is half the trajectory
        return {"ok": False, "budgets": {}, "facts": {}, "previous": None, "reason": reason}
    budgets = {str(b): {"run": "r.json", "iters": b, "probe_task_0": p, "initial_task_0": 0.6875,
                        "head_task_0": h} for b, p, h in zip(e385.NEW, probe, head)}
    return {"ok": True, "budgets": budgets,
            "facts": facts if facts is not None else {str(b): _facts(iters=b) for b in e385.NEW},
            "previous": ({"artifact": "e384.json",
                          "readings": {"1": probe[0] + overlap, "5": probe[4] + overlap,
                                       "20": 0.5875, "100": 0.70, "500": 0.7792},
                          "heads": {"1": 0.0833, "5": 0.2083, "20": 0.25, "100": 0.3333, "500": 0.75},
                          "facts": {"1": _facts(iters=1)}}),
            "arm": e385.NAIVE, "reps": e385.SWEEP_REPS}


def _judge(**kw):
    return {row["id"]: row for row in e385.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape the corpus has: the dip does not turn inside the first five updates, so F2 and F4 fire
    j = _judge()
    for cid in ("F1", "F3", "F5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    for cid in ("F2", "F4"):
        assert j[cid]["verdict"].startswith("FALSIFIER"), j[cid]

    #: and a series with an interior minimum turns: the other face of F2, F3 and F4 together
    turned = dict(probe=(0.68, 0.60, 0.575, 0.55, 0.60), head=(0.08, 0.10, 0.15, 0.18, 0.30))
    j2 = _judge(**turned)
    for cid in ("F1", "F2", "F3", "F4", "F5"):
        assert j2[cid]["verdict"].startswith("MET"), (cid, j2[cid])

    # F1: a field other than the budget moved, and an overlap that does not reproduce
    bad = {str(b): _facts(iters=b) for b in e385.NEW}
    bad["3"] = {**bad["3"], "lr": 0.03}
    assert _judge(facts=bad)["F1"]["verdict"].startswith("FALSIFIER")
    assert _judge(overlap=0.20)["F1"]["verdict"].startswith("FALSIFIER")

    # F2: a plateau at the minimum rather than a turn
    assert _judge(probe=(0.68, 0.60, 0.60, 0.60, 0.62), head=(0.08, 0.10, 0.15, 0.18, 0.30))["F2"][
        "verdict"].startswith("FALSIFIER")

    # F3: a dip within the falsifier's bar, and one between the bars
    assert _judge(probe=(0.68, 0.66, 0.655, 0.65, 0.64))["F3"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe=(0.68, 0.63, 0.62, 0.61, 0.60))["F3"]["verdict"].startswith("NULL")

    # F4: a dip still deepening at the last budget, and one whose recovery is too small to call
    assert _judge(probe=(0.68, 0.59, 0.575, 0.5625, 0.55))["F4"]["verdict"].startswith("FALSIFIER")
    assert _judge(probe=(0.68, 0.60, 0.58, 0.56, 0.575), head=(0.08, 0.10, 0.15, 0.18, 0.30))["F4"][
        "verdict"].startswith("NULL")

    # F5: a head already steering where the world sits lowest
    assert _judge(probe=(0.68, 0.60, 0.575, 0.55, 0.60), head=(0.08, 0.10, 0.15, 0.80, 0.30))["F5"][
        "verdict"].startswith("FALSIFIER")

    #: a run or the previous series absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e385.judge(_doc(ok=False)))
    assert all(row["verdict"].startswith("REFUSED") for row in e385.judge(_doc(previous=False)))


def test_the_series_joins_the_two_sources_of_budgets():
    r = _doc()
    series = e385._series(r)
    assert sorted(series) == [1, 2, 3, 4, 5, 20, 100, 500], sorted(series)
    #: the new unit's own rolls win where the two overlap, so the overlap check has something to compare
    assert series[1] == r["budgets"]["1"]["probe_task_0"]


def test_the_live_reading_resolves_the_valley_and_reproduces_the_previous_series():
    p = Path("runs/e385_the_valleys_shape.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e385.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e385.judge(d)}
    #: the configuration and the overlap are structural facts about two units rolling one instrument
    assert verdicts["F1"].startswith("MET"), (verdicts["F1"], d["budgets"].keys())
    #: and this unit's rolls of the previous series' budgets reproduce that series
    for b in e385.SHARED_WITH:
        here = d["budgets"][str(b)]["probe_task_0"]
        there = d["previous"]["readings"][str(b)]
        assert abs(here - there) < e385.SAME, (b, here, there)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
