"""`e500` plays the paid, label-first episodic pass for the world's payout, so the tests pin both faces of the three
claims, the runner's own refusal scan, the map's movement, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e500_the_pass_plays_for_the_payout as e500

ARMS = e500.ARMS
#: the reading's shape: the map earned, the payout moved, and the pass still learned
ACC = {"earned": {"naive": 0.8200, "ewc-block": 0.8100, "replay": 0.8200},
       "meter": {"naive": 0.8299, "ewc-block": 0.8139, "replay": 0.8267}}
REWARD_DIAG = {"earned": {"naive": -4.2000, "ewc-block": -4.3000, "replay": -4.9000},
               "meter": {"naive": -6.0542, "ewc-block": -6.0070, "replay": -6.1017}}
MOVE = {"naive": {"replicates": 20, "above_zero": 20, "smallest": 4.2209, "mean": 5.0900},
        "ewc-block": {"replicates": 20, "above_zero": 20, "smallest": 4.5000, "mean": 5.2000},
        "replay": {"replicates": 20, "above_zero": 20, "smallest": 4.8000, "mean": 5.6300}}
ONE_TRIAL = {"naive": {"replicates": 20, "above_zero": 20, "smallest": 4.2209, "mean": 5.0900},
             "ewc-block": {"replicates": 20, "above_zero": 20, "smallest": 4.5000, "mean": 5.2000},
             "replay": {"replicates": 20, "above_zero": 20, "smallest": 4.8000, "mean": 5.6300}}
REFUSALS = {"messages": 16, "naming_the_ascent": ["--loop-earn needs --loop-policy"], "naming_the_pair": [],
            "pair_refused": False}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, moved=None, added=None, draw_differ=None, missing=None, refusals="keep",
         reward=None, accuracy=None, diag=None, move="keep", one_trial="keep", replicates=(20,), ok=True,
         reason="the earned run is absent, or carries no replicate to read"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "config": {}, "draw": {}, "map": {}, "reward": {},
                "accuracy": {}, "refusals": None, "spans": {}}
    reward = dict(reward or {"naive": (+1.8500, +20.00), "ewc-block": (+1.7000, +18.00),
                             "replay": (+1.2000, +14.00)})
    accuracy = dict(accuracy or {"naive": (-0.0099, -0.60), "ewc-block": (-0.0039, -0.30),
                                 "replay": (-0.0067, -0.50)})
    ref = None if refusals is None else dict(REFUSALS if refusals == "keep" else refusals)
    earned_moved = {"loop_policy": True, "loop_earn": True}
    meter_moved = {"loop_policy": False, "loop_earn": False}
    if moved is not None:
        earned_moved = dict(moved)
    return {
        "ok": True, "reason": None,
        "runs": {"earned": {"artifact": "n"}, "meter": {"artifact": "m"}},
        "config": {}, "draw": {},
        "map": {"earned": (None if move is None else dict(MOVE if move == "keep" else move)),
                "one_trial": (None if one_trial is None
                              else dict(ONE_TRIAL if one_trial == "keep" else one_trial))},
        "refusals": ref,
        "reward": {a: _paired(reward[a][0], reward[a][1]) for a in ARMS},
        "accuracy": {a: _paired(accuracy[a][0], accuracy[a][1]) for a in ARMS},
        "spans": {
            "arms": list(ARMS), "runs": ["earned", "meter"], "episode": e500.EPISODE, "chance": e500.CHANCE,
            "replicates": list(replicates),
            "config": {"earned": {"same": 55, "inert": ["loop_policy", "loop_earn"],
                                  "differ": {k: [None, 1] for k in (differ or [])}, "moved": earned_moved},
                       "meter": {"same": 55, "inert": [], "differ": {}, "moved": meter_moved}},
            "draw": {"earned": {"agree": {"cue_sha1": True, "reward_map_sha1": True},
                                "differ": list(draw_differ or []), "added": list(added or []),
                                "missing": list(missing or [])},
                     "meter": {"agree": {}, "differ": [], "added": [], "missing": []}},
            "accuracy_diagonal": {"earned": {a: (diag or ACC["earned"])[a] for a in ARMS},
                                  "meter": dict(ACC["meter"])},
            "accuracy_last": {label: {a: 0.5900 for a in ARMS} for label in ACC},
            "reward_diagonal": {label: dict(REWARD_DIAG[label]) for label in REWARD_DIAG},
            "reward_last": {label: {a: -5.4000 for a in ARMS} for label in REWARD_DIAG},
            "map_move": {}, "refusals": ref,
        },
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e500.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("QA1", "QA2", "QA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # QA1: another config field differing, the flags not moved, a draw field differing, added or missing, a thin
    # run, and the runner refusing the pair
    assert _judge(differ=["iters"])["QA1"].startswith("FALSIFIER")
    assert _judge(moved={"loop_policy": True, "loop_earn": False})["QA1"].startswith("FALSIFIER")
    assert _judge(moved={"loop_policy": False, "loop_earn": False})["QA1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["QA1"].startswith("FALSIFIER")
    assert _judge(added=["reward_map_sha1"])["QA1"].startswith("FALSIFIER")
    assert _judge(missing=["boundary_sha1"])["QA1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["QA1"].startswith("FALSIFIER")
    assert _judge(refusals={**REFUSALS, "pair_refused": True,
                            "naming_the_pair": ["--loop-earn is refused with --loop-episode"]}
                  )["QA1"].startswith("FALSIFIER")
    #: the runner's own source is an input artifact of that claim
    assert _judge(refusals=None)["QA1"].startswith("REFUSED")

    # QA2: a replicate whose map distance is zero, a run that records no movement, a contrast that does not resolve,
    # and one that is negative
    assert _judge(move={**MOVE, "replay": {"replicates": 20, "above_zero": 19, "smallest": 0.0, "mean": 5.63}}
                  )["QA2"].startswith("FALSIFIER")
    assert _judge(move={**MOVE, "naive": {"replicates": 20, "above_zero": 20, "smallest": -0.5000, "mean": 4.0}}
                  )["QA2"].startswith("FALSIFIER")
    assert _judge(move=None)["QA2"].startswith("FALSIFIER")
    assert _judge(reward={"naive": (+1.8500, +20.00), "ewc-block": (+0.1000, +1.20),
                          "replay": (+1.2000, +14.00)})["QA2"].startswith("FALSIFIER")
    assert _judge(reward={"naive": (+1.8500, +20.00), "ewc-block": (+1.7000, +18.00),
                          "replay": (-0.1000, -1.10)})["QA2"].startswith("FALSIFIER")
    #: `e488`'s own earn run is the instrument's reference and an input artifact of this claim
    assert _judge(one_trial=None)["QA2"].startswith("REFUSED")

    # QA3: one arm over the bar only, and an arm more than 0.10 under the meter run's
    assert _judge(diag=ACC["earned"])["QA3"].startswith("MET")
    thin = {"naive": 0.8200, "ewc-block": 0.3000, "replay": 0.3100}
    assert _judge(diag=thin)["QA3"].startswith("FALSIFIER")
    under = {"naive": 0.8200, "ewc-block": 0.8100, "replay": 0.6000}
    assert _judge(diag=under)["QA3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e500.judge(_doc(ok=False)))


def test_the_runs_the_flags_the_bars_and_the_refusal_scan_are_registered():
    assert e500.NEW.name == "e500_earned_label_episode2_labelfirst_reward_earn_20reps.json"
    assert e500.METER.name == "e498_earned_label_episode2_labelfirst_reward_20reps.json"
    assert e500.EARN.name == "e488_earned_label_earned_20reps.json"
    assert e500.RUNNER.name == "e8_rate_network.py"
    assert set(e500.MOVED) == {"loop_policy", "loop_earn"}, e500.MOVED
    assert set(e500.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e500.EPISODE, e500.TAU, e500.SIZE, e500.READOUT_SIZE) == (2, 12, 300, 32)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e500.MIN_REPS, e500.SIGMA, e500.CHANCE, e500.BAR, e500.TOL, e500.ARMS_NEEDED) == (20, 2.0, 0.25, 0.10,
                                                                                             0.10, 2)
    assert e500._inert("loop_policy", False, True) and e500._inert("loop_earn", False, True)
    assert not e500._inert("iters", 500, 100)
    assert e500.DEFAULTS.get("loop_policy") is False, e500.DEFAULTS.get("loop_policy")
    assert e500.DEFAULTS.get("loop_earn") is False, e500.DEFAULTS.get("loop_earn")
    #: the runner's own checks are read from its source, and this pair is not one of its refusals
    ref = e500.refusals()
    assert ref is not None and ref["pair_refused"] is False, ref
    assert any("loop-earn" in m for m in ref["naming_the_ascent"]), ref


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e500_the_pass_plays_for_the_payout.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e500.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    #: the arms, the two runs, the map and the two currencies are structural
    assert sorted(d["runs"]) == ["earned", "meter"], sorted(d["runs"])
    assert sorted(d["reward"]) == sorted(ARMS), sorted(d["reward"])
    assert sorted(d["accuracy"]) == sorted(ARMS), sorted(d["accuracy"])
    assert sorted(d["map"]) == ["earned", "one_trial"], sorted(d["map"])
    #: the counts that grow with the corpus are read as bounds
    assert d["spans"]["replicates"] == [e500.MIN_REPS], d["spans"]["replicates"]
    assert d["spans"]["config"]["earned"]["same"] >= 40, d["spans"]["config"]["earned"]["same"]
    assert len(d["spans"]["draw"]["earned"]["agree"]) >= 20, len(d["spans"]["draw"]["earned"]["agree"])
    for a in ARMS:
        assert d["reward"][a]["n"] >= e500.MIN_REPS, (a, d["reward"][a])
        #: the payout is a negative squared distance, so its cells are at or below zero; whether the earned run's
        #: diagonal is above the meter run's is the claim's business and the judge re-derives the verdict
        assert d["spans"]["reward_diagonal"]["earned"][a] <= 0.0, a
        assert d["spans"]["reward_diagonal"]["meter"][a] <= 0.0, a
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["earned"][a] <= 1.0, a
    for label in ("earned", "one_trial"):
        row = d["map"][label]
        if row is None:
            continue
        for a in ARMS:
            assert row[a]["replicates"] >= e500.MIN_REPS, (label, a)
            assert 0 <= row[a]["above_zero"] <= row[a]["replicates"], (label, a)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
