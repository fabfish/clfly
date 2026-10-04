"""`e413` reads the six worlds' two arms at three budgets off the runs `e405`, `e407`, `e398`, `e399`, `e401` and
`e380` wrote, so the tests pin both faces of the five claims, the refusal when a world's run is absent, and the live
re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e413_the_aid_turns_on_in_every_world as e413

#: the corpus's shape: per world, `(naive accuracy, gain, cut)` at budgets 1, 20 and 500
WORLD = {
    "card": {1: (0.2438, +0.0000, +0.0089), 20: (0.2969, -0.0045, +0.0307), 500: (0.5191, +0.1594, +0.2844)},
    "cue14": {1: (0.2674, +0.0003, +0.0083), 20: (0.3014, +0.0017, +0.0365), 500: (0.5434, +0.1535, +0.2755)},
    "cue1": {1: (0.2708, +0.0073, +0.0120), 20: (0.2969, +0.0021, +0.0135), 500: (0.5479, +0.1330, +0.2339)},
    "cue9": {1: (0.2691, -0.0174, -0.0016), 20: (0.2799, +0.0288, +0.0620), 500: (0.5323, +0.1573, +0.3073)},
    "cue6": {1: (0.2497, +0.0062, +0.0068), 20: (0.2844, +0.0365, +0.0635), 500: (0.5215, +0.1542, +0.3146)},
    "cue3": {1: (0.2653, +0.0045, +0.0026), 20: (0.2941, +0.0347, +0.0615), 500: (0.5500, +0.1490, +0.2677)},
}


def _doc(worlds=None, reps=20, configurations=1, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "budgets": list(e413.BUDGETS), "arms": list(e413.ARMS),
                "worlds": {}, "spans": {}}
    worlds = worlds if worlds is not None else {k: dict(v) for k, v in WORLD.items()}
    out = {}
    for name, by_budget in worlds.items():
        runs = {}
        for budget, (naive, gain, cut) in by_budget.items():
            runs[str(budget)] = {
                "artifact": f"{name}_iters{budget}.json",
                "arms": {"naive": {"replicates": reps, "final_accuracy": naive, "mean_forgetting": 0.5,
                                   "final": [naive] * e413.N_TASKS,
                                   "forgetting": [0.5] * e413.N_TASKS},
                         "replay": {"replicates": reps, "final_accuracy": naive + gain,
                                    "mean_forgetting": 0.5 - cut,
                                    "final": [naive + gain] * e413.N_TASKS,
                                    "forgetting": [0.5 - cut] * e413.N_TASKS}},
                "gain": gain, "cut": cut}
        out[name] = {"runs": runs, "configurations": configurations,
                     "gain_rise": runs["500"]["gain"] - runs["20"]["gain"]}
    small = [w["runs"][str(b)]["gain"] for w in out.values() for b in e413.SMALL]
    at20 = [w["runs"]["20"]["gain"] for w in out.values()]
    rises = [w["gain_rise"] for w in out.values()]
    tops = [w["runs"]["500"]["gain"] for w in out.values()]
    return {"ok": True, "reason": None, "budgets": list(e413.BUDGETS), "arms": list(e413.ARMS), "worlds": out,
            "spans": {"worlds": len(out), "small_max": max(small), "small_min": min(small),
                      "span_at_20": max(at20) - min(at20), "least_top": min(tops), "least_rise": min(rises)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e413.judge(_doc(**kw))}


def _set(world, budget, index, value):
    """A copy of the corpus with one cell's ``(naive, gain, cut)`` element replaced."""
    worlds = {k: dict(v) for k, v in WORLD.items()}
    cell = list(worlds[world][budget])
    cell[index] = value
    worlds[world][budget] = tuple(cell)
    return worlds


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the runs carried, the small budgets flat, the top a tenth and the rise clearing twice the span
    j = _judge()
    for cid in ("AY1", "AY2", "AY3", "AY4", "AY5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AY1: too few replicates, a world whose budgets disagree, and too few worlds
    assert _judge(reps=19)["AY1"].startswith("FALSIFIER")
    assert _judge(configurations=2)["AY1"].startswith("FALSIFIER")
    assert _judge(worlds={k: v for k, v in list(WORLD.items())[:4]})["AY1"].startswith("FALSIFIER")

    # AY2: a small-budget gain over the bar, and one between the bars
    assert _judge(worlds=_set("cue6", 20, 1, 0.12))["AY2"].startswith("FALSIFIER")
    assert _judge(worlds=_set("cue6", 20, 1, 0.07))["AY2"].startswith("NULL")

    # AY3: a world that gains nothing at five hundred, and one between the bars
    assert _judge(worlds=_set("cue1", 500, 1, 0.02))["AY3"].startswith("FALSIFIER")
    assert _judge(worlds=_set("cue1", 500, 1, 0.07))["AY3"].startswith("NULL")

    # AY4: a world whose rise is under the falsifier bar, and one between the bars
    assert _judge(worlds=_set("cue3", 500, 1, 0.0347 + 0.03))["AY4"].startswith("FALSIFIER")
    assert _judge(worlds=_set("cue3", 500, 1, 0.0347 + 0.07))["AY4"].startswith("NULL")

    # AY5: every world's rise inside twice the twenty-update span
    flat = {k: {b: (v[0], by[20][1] + 0.02 if b == 500 else v[1], v[2]) for b, v in by.items()}
            for k, by in WORLD.items()}
    assert _judge(worlds=flat)["AY5"].startswith("FALSIFIER")

    #: a world's run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e413.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the six worlds, each at the three budgets `e405`, `e407` and the five-hundred-update runs rolled
    assert sorted(e413.RUNS) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(e413.RUNS)
    assert e413.BUDGETS == (1, 20, 500) and e413.SMALL == (1, 20)
    for name, by_budget in e413.RUNS.items():
        assert sorted(by_budget) == [1, 20, 500], name
        assert "e405" in by_budget[1].name and "e407" in by_budget[20].name, name
        assert "iters500" in by_budget[500].name or "e380" in by_budget[500].name, name
    assert e413.RUNS["card"][500].name == "e380_earned_label_cue0_actionsource_20reps.json"
    assert e413.ARMS == ("naive", "replay") and e413.N_TASKS == 3
    assert (e413.MIN_WORLDS, e413.MIN_REPS) == (5, 20)
    assert (e413.SMALL_GAIN, e413.SMALL_FIRES) == (0.05, 0.10)
    assert (e413.TOP, e413.TOP_FIRES) == (0.10, 0.05)
    assert (e413.RISE, e413.RISE_FIRES) == (0.10, 0.05)
    assert e413.TWICE == 2.0


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e413_the_aid_turns_on_in_every_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e413.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e413.judge(d)}
    #: the runs being carried and the small budgets being flat are structural facts
    assert verdicts["AY1"].startswith("MET") and verdicts["AY2"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue6", "cue9"], sorted(d["worlds"])
    for name, w in d["worlds"].items():
        assert sorted(w["runs"]) == ["1", "20", "500"], name
        assert w["configurations"] == 1, name
        for arm in e413.ARMS:
            for b in ("1", "20", "500"):
                a = w["runs"][b]["arms"][arm]
                assert a["replicates"] >= e413.MIN_REPS, (name, b, arm)
                assert len(a["final"]) == len(a["forgetting"]) == e413.N_TASKS, (name, b, arm)
        rise = w["runs"]["500"]["gain"] - w["runs"]["20"]["gain"]
        assert abs(rise - w["gain_rise"]) < 1e-12, name
    assert d["spans"]["least_top"] >= e413.TOP, d["spans"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
