"""`e501` plays the paid, label-first episodic pass at three trials, so the tests pin both faces of the three claims,
the map's movement beside `e500`'s two-trial figure, and the refusal when a run is absent.

The falsifier test drives `judge` on synthetic readings rather than on the artifact, so a claim's outcome is never
asserted as the artifact's shape: what is pinned is that each registered falsifier does fire, and that the three
claims read both faces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e501_the_pass_plays_at_three_trials as e501

ARMS = e501.ARMS
#: the reading's shape: the pass still learned, the payout moved, and the map earned
ACC = {"earned": {"naive": 0.8500, "ewc-block": 0.8400, "replay": 0.8600},
       "meter": {"naive": 0.8538, "ewc-block": 0.8392, "replay": 0.8580}}
REWARD_DIAG = {"earned": {"naive": -4.0000, "ewc-block": -4.1000, "replay": -4.7000},
               "meter": {"naive": -5.5000, "ewc-block": -5.6000, "replay": -5.8000}}
MOVE = {"naive": {"replicates": 20, "above_zero": 20, "smallest": 3.1000, "mean": 4.9000},
        "ewc-block": {"replicates": 20, "above_zero": 20, "smallest": 3.4000, "mean": 5.1000},
        "replay": {"replicates": 20, "above_zero": 20, "smallest": 3.7000, "mean": 5.5000}}
TWO_TRIAL = {"naive": {"replicates": 20, "above_zero": 20, "smallest": 4.4082, "mean": 5.8133},
             "ewc-block": {"replicates": 20, "above_zero": 20, "smallest": 3.9475, "mean": 5.2579},
             "replay": {"replicates": 20, "above_zero": 20, "smallest": 5.4594, "mean": 6.7272}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, moved=None, added=None, draw_differ=None, missing=None, reward=None, accuracy=None,
         diag=None, meter_diag=None, move="keep", two_trial="keep", replicates=(20,), loop_episode=None,
         episode_len=None, ok=True, reason="the earned run is absent, or carries no replicate to read"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "map": {}, "reward": {}, "accuracy": {}, "shape": {},
                "spans": {}}
    reward = dict(reward or {"naive": (+1.2000, +18.00), "ewc-block": (+1.1000, +16.00), "replay": (+0.9000, +12.00)})
    accuracy = dict(accuracy or {"naive": (-0.0038, -0.40), "ewc-block": (+0.0008, +0.10), "replay": (+0.0020, +0.30)})
    earned_moved = {"loop_policy": True, "loop_earn": True}
    meter_moved = {"loop_policy": False, "loop_earn": False}
    if moved is not None:
        earned_moved = dict(moved)
    ep = {"earned": 3, "meter": 3}
    if loop_episode is not None:
        ep = dict(loop_episode)
    elen = {"earned": 3, "meter": 3}
    if episode_len is not None:
        elen = dict(episode_len)
    return {
        "ok": True, "reason": None,
        "runs": {"earned": {"artifact": "n"}, "meter": {"artifact": "m"}},
        "map": {"earned": (None if move is None else dict(MOVE if move == "keep" else move)),
                "two_trial": (None if two_trial is None else dict(TWO_TRIAL if two_trial == "keep" else two_trial))},
        "reward": {a: _paired(reward[a][0], reward[a][1]) for a in ARMS},
        "accuracy": {a: _paired(accuracy[a][0], accuracy[a][1]) for a in ARMS},
        "shape": {label: {a: _paired(0.3, 5.0) for a in ARMS} for label in ("earned", "meter")},
        "spans": {
            "arms": list(ARMS), "runs": ["earned", "meter"], "episode": e501.EPISODE, "chance": e501.CHANCE,
            "bar": e501.BAR, "tol": e501.TOL, "sigma": e501.SIGMA, "arms_needed": e501.ARMS_NEEDED,
            "replicates": list(replicates),
            "loop_episode": ep, "episode_len": elen,
            "config": {"earned": {"same": 55, "inert": ["loop_policy", "loop_earn"],
                                  "differ": {k: [None, 1] for k in (differ or [])}, "moved": earned_moved},
                       "meter": {"same": 55, "inert": [], "differ": {}, "moved": meter_moved}},
            "draw": {"earned": {"agree": {"cue_sha1": True, "reward_map_sha1": True},
                                "differ": list(draw_differ or []), "added": list(added or []),
                                "missing": list(missing or [])},
                     "meter": {"agree": {}, "differ": [], "added": [], "missing": []}},
            "accuracy_diagonal": {"earned": {a: (diag or ACC["earned"])[a] for a in ARMS},
                                  "meter": {a: (meter_diag or ACC["meter"])[a] for a in ARMS}},
            "accuracy_last": {label: {a: 0.6100 for a in ARMS} for label in ("earned", "meter")},
            "reward_diagonal": {label: dict(REWARD_DIAG[label]) for label in REWARD_DIAG},
            "reward_last": {label: {a: -5.0000 for a in ARMS} for label in REWARD_DIAG},
            "reward_shape": {},
            "map_move": {"earned": dict(MOVE), "two_trial": dict(TWO_TRIAL)},
        },
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e501.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("RA1", "RA2", "RA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # RA1: another config field differing, the flags not moved, a draw field differing, added or missing, a thin run,
    # and a pass that is not the three-trial one
    assert _judge(differ=["iters"])["RA1"].startswith("FALSIFIER")
    assert _judge(moved={"loop_policy": True, "loop_earn": False})["RA1"].startswith("FALSIFIER")
    assert _judge(moved={"loop_policy": False, "loop_earn": False})["RA1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["RA1"].startswith("FALSIFIER")
    assert _judge(added=["reward_map_sha1"])["RA1"].startswith("FALSIFIER")
    assert _judge(missing=["boundary_sha1"])["RA1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["RA1"].startswith("FALSIFIER")
    assert _judge(loop_episode={"earned": 3, "meter": 2})["RA1"].startswith("FALSIFIER")
    assert _judge(episode_len={"earned": 4, "meter": 4})["RA1"].startswith("FALSIFIER")

    # RA2: a replicate whose map distance is not positive, a run that records no movement, and fewer than two arms
    # resolving upward at two sigma
    assert _judge(move={**MOVE, "replay": {"replicates": 20, "above_zero": 19, "smallest": 0.0, "mean": 5.63}}
                  )["RA2"].startswith("FALSIFIER")
    assert _judge(move={**MOVE, "naive": {"replicates": 20, "above_zero": 20, "smallest": -0.5000, "mean": 4.0}}
                  )["RA2"].startswith("FALSIFIER")
    assert _judge(move=None)["RA2"].startswith("FALSIFIER")
    assert _judge(reward={"naive": (+1.2000, +18.00), "ewc-block": (+0.1000, +1.20),
                          "replay": (-0.1000, -1.10)})["RA2"].startswith("FALSIFIER")

    # RA3: one arm over the bar only, and an arm more than 0.10 under the meter run's
    thin = {"naive": 0.8500, "ewc-block": 0.3000, "replay": 0.3100}
    assert _judge(diag=thin)["RA3"].startswith("FALSIFIER")
    under = {"naive": 0.8500, "ewc-block": 0.8400, "replay": 0.6000}
    assert _judge(diag=under)["RA3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e501.judge(_doc(ok=False)))


def test_the_runs_the_flags_the_bars_and_the_refusal_are_registered():
    assert e501.NEW.name == "e501_earned_label_episode3_labelfirst_reward_earn_20reps.json"
    assert e501.METER.name == "e501_earned_label_episode3_labelfirst_reward_20reps.json"
    assert e501.TWO.name == "e500_earned_label_episode2_labelfirst_reward_earn_20reps.json"
    assert e501.RUNNER.name == "e8_rate_network.py"
    assert set(e501.MOVED) == {"loop_policy", "loop_earn"}, e501.MOVED
    assert set(e501.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e501.EPISODE == 3 and e501.CHANCE == 0.25
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e501.MIN_REPS, e501.SIGMA, e501.BAR, e501.TOL, e501.ARMS_NEEDED) == (20, 2.0, 0.10, 0.10, 2)
    assert e501._inert("loop_policy", False, True) and e501._inert("loop_earn", False, True)
    assert not e501._inert("iters", 500, 100)
    assert e501.DEFAULTS.get("loop_policy") is False, e501.DEFAULTS.get("loop_policy")
    assert e501.DEFAULTS.get("loop_earn") is False, e501.DEFAULTS.get("loop_earn")
    #: the three claims are registered with their falsifiers beside them
    assert [c[0] for c in e501.CLAIMS] == ["RA1", "RA2", "RA3"]
    assert all("falsifier:" in c[3] for c in e501.CLAIMS)


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e501_the_pass_plays_at_three_trials.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e501.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    #: the arms, the two runs, both currencies and the map at the two rungs are structural
    assert sorted(d["runs"]) == ["earned", "meter"], sorted(d["runs"])
    assert sorted(d["reward"]) == sorted(ARMS), sorted(d["reward"])
    assert sorted(d["accuracy"]) == sorted(ARMS), sorted(d["accuracy"])
    assert sorted(d["map"]) == ["earned", "two_trial"], sorted(d["map"])
    #: the counts that grow with the corpus are read as bounds, so a longer artifact does not break the test
    assert d["spans"]["replicates"] == [e501.MIN_REPS], d["spans"]["replicates"]
    assert d["spans"]["config"]["earned"]["same"] >= 40, d["spans"]["config"]["earned"]["same"]
    assert len(d["spans"]["draw"]["earned"]["agree"]) >= 20, len(d["spans"]["draw"]["earned"]["agree"])
    for a in ARMS:
        assert d["reward"][a]["n"] >= e501.MIN_REPS, (a, d["reward"][a])
        #: the payout is a negative squared distance, so its cells are at or below zero; whether the earned run's
        #: diagonal is above the meter run's is the claim's business and the judge re-derives the verdict
        assert d["spans"]["reward_diagonal"]["earned"][a] <= 0.0, a
        assert d["spans"]["reward_diagonal"]["meter"][a] <= 0.0, a
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["earned"][a] <= 1.0, a
    for label in ("earned", "two_trial"):
        row = d["map"][label]
        if row is None:
            continue
        for a in ARMS:
            assert row[a]["replicates"] >= e501.MIN_REPS, (label, a)
            assert 0 <= row[a]["above_zero"] <= row[a]["replicates"], (label, a)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
