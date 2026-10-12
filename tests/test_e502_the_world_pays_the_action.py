"""`e502` reads the world's payout on the agent's own action, so the tests pin both faces of the three claims, the
config and draw comparison against `e500`'s carried-state run, the map's movement, and the refusal when a run is
absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e502_the_world_pays_the_action as e502

ARMS = e502.ARMS
#: the reading's shape: the flag moves the payout, the action's currency is alive, and the pass is still learned
ACC = {"earned": {"naive": 0.8200, "ewc-block": 0.8100, "replay": 0.8200},
       "meter": {"naive": 0.8299, "ewc-block": 0.8139, "replay": 0.8267},
       "carried": {"naive": 0.8281, "ewc-block": 0.8153, "replay": 0.8247}}
REWARD = {"earned": {"naive": -4.2000, "ewc-block": -4.3000, "replay": -4.9000},
          "meter": {"naive": -6.0542, "ewc-block": -6.0070, "replay": -6.1017},
          "carried": {"naive": -4.5457, "ewc-block": -4.5947, "replay": -5.0295}}
MOVE = {"naive": {"replicates": 20, "above_zero": 20, "smallest": 4.2209, "mean": 5.0900},
        "ewc-block": {"replicates": 20, "above_zero": 20, "smallest": 4.5000, "mean": 5.2000},
        "replay": {"replicates": 20, "above_zero": 20, "smallest": 4.8000, "mean": 5.6300}}
CARRIED_MOVE = {"naive": {"mean": 5.0935}, "ewc-block": {"mean": 5.3670}, "replay": {"mean": 5.6252}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, moved=None, theirs_moved="keep", added=None, draw_differ=None, missing=None,
         reward=None, accuracy=None, diag=None, move="keep", config="keep", replicates=(20,), ok=True,
         reason="the earned run is absent, or carries no replicate to read"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "map": {}, "reward": {}, "accuracy": {},
                "shape": {}, "spans": {}}
    reward = dict(reward or {"naive": (+1.2000, +14.00), "ewc-block": (+1.5000, +18.00),
                             "replay": (+1.0500, +12.00)})
    accuracy = dict(accuracy or {"naive": (+0.0010, +0.20), "ewc-block": (-0.0020, -0.30),
                                 "replay": (+0.0030, +0.50)})
    earned_moved = {"loop_reward_on_action": True}
    if moved is not None:
        earned_moved = dict(moved)
    if theirs_moved == "keep":
        theirs_moved = {"loop_reward_on_action": None}
    against = None if config is None else {
        "same": 57, "inert": ["json_out", "loop_reward_on_action"],
        "differ": {k: [None, 1] for k in (differ or [])}, "moved": earned_moved, "theirs_moved": theirs_moved}
    draw = None if config is None else {"agree": {"cue_sha1": True, "reward_map_sha1": True},
                                        "differ": list(draw_differ or []), "added": list(added or []),
                                        "missing": list(missing or [])}
    got_map = (None if move is None else dict(MOVE if move == "keep" else move))
    return {
        "ok": True, "reason": None,
        "runs": {"earned": {"artifact": "n"}, "meter": {"artifact": "m"}, "carried": {"artifact": "c"}},
        "map": {"earned": got_map, "carried": dict(CARRIED_MOVE)},
        "reward": {a: _paired(reward[a][0], reward[a][1]) for a in ARMS},
        "accuracy": {a: _paired(accuracy[a][0], accuracy[a][1]) for a in ARMS},
        "shape": {"earned": {a: _paired(+0.60, +13.0) for a in ARMS},
                  "meter": {a: _paired(+0.02, +0.30) for a in ARMS}},
        "spans": {
            "arms": list(ARMS), "runs": ["earned", "meter", "carried"], "episode": e502.EPISODE,
            "chance": e502.CHANCE, "replicates": list(replicates),
            "config": {"earned": against}, "draw": {"earned": draw},
            "accuracy_diagonal": {"earned": {a: (diag or ACC["earned"])[a] for a in ARMS},
                                  "meter": dict(ACC["meter"]), "carried": dict(ACC["carried"])},
            "accuracy_last": {label: {a: 0.5900 for a in ARMS} for label in ACC},
            "reward_diagonal": {label: dict(REWARD[label]) for label in REWARD},
            "reward_last": {label: {a: -5.4000 for a in ARMS} for label in REWARD},
            "reward_shape": {},
            "map_move": {"earned": got_map, "carried": dict(CARRIED_MOVE)},
        },
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e502.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("TA1", "TA2", "TA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # TA1: another config field differing, the flag not moved, a draw field differing, added or missing, a thin run,
    # and the carried-state run itself absent
    assert _judge(differ=["iters"])["TA1"].startswith("FALSIFIER")
    assert _judge(moved={"loop_reward_on_action": False})["TA1"].startswith("FALSIFIER")
    assert _judge(moved={"loop_reward_on_action": None})["TA1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["TA1"].startswith("FALSIFIER")
    assert _judge(added=["reward_map_sha1"])["TA1"].startswith("FALSIFIER")
    assert _judge(missing=["boundary_sha1"])["TA1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["TA1"].startswith("FALSIFIER")
    assert _judge(config=None)["TA1"].startswith("REFUSED")

    # TA2: a replicate whose map distance is zero, one that is negative, a run that records no movement, a reward
    # contrast that does not resolve on two arms, and one that is negative
    assert _judge(move={**MOVE, "replay": {"replicates": 20, "above_zero": 19, "smallest": 0.0, "mean": 5.63}}
                  )["TA2"].startswith("FALSIFIER")
    assert _judge(move={**MOVE, "naive": {"replicates": 20, "above_zero": 20, "smallest": -0.5000, "mean": 4.0}}
                  )["TA2"].startswith("FALSIFIER")
    assert _judge(move=None)["TA2"].startswith("REFUSED")
    assert _judge(reward={"naive": (+1.2000, +14.00), "ewc-block": (+0.1000, +1.20),
                          "replay": (+0.0500, +0.80)})["TA2"].startswith("FALSIFIER")
    assert _judge(reward={"naive": (+1.2000, +14.00), "ewc-block": (-0.5000, -3.00),
                          "replay": (+0.0500, +0.80)})["TA2"].startswith("FALSIFIER")

    # TA3: one arm over the bar only, and an arm more than 0.10 under the meter run's
    assert _judge(diag=ACC["earned"])["TA3"].startswith("MET")
    thin = {"naive": 0.8200, "ewc-block": 0.3000, "replay": 0.3100}
    assert _judge(diag=thin)["TA3"].startswith("FALSIFIER")
    under = {"naive": 0.8200, "ewc-block": 0.8100, "replay": 0.6000}
    assert _judge(diag=under)["TA3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e502.judge(_doc(ok=False)))


def test_the_runs_the_flag_the_bars_and_the_rule_are_registered():
    assert e502.NEW.name == "e502_reward_on_action_episode2_labelfirst_reward_earn_20reps.json"
    assert e502.METER.name == "e502_reward_on_action_episode2_labelfirst_reward_20reps.json"
    assert e502.CARRIED.name == "e500_earned_label_episode2_labelfirst_reward_earn_20reps.json"
    assert e502.RUNNER.name == "e8_rate_network.py"
    assert set(e502.MOVED) == {"loop_reward_on_action"}, e502.MOVED
    assert set(e502.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e502.EPISODE, e502.CHANCE, e502.MIN_REPS) == (2, 0.25, 20)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e502.SIGMA, e502.BAR, e502.TOL, e502.ARMS_NEEDED) == (2.0, 0.10, 0.10, 2)
    assert e502._inert("loop_reward_on_action", False, True)
    assert not e502._inert("iters", 500, 100)
    assert e502.DEFAULTS.get("loop_reward_on_action") is False, e502.DEFAULTS.get("loop_reward_on_action")
    assert callable(e502.load) and callable(e502._roll) and callable(e502._against)


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e502_the_world_pays_the_action.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e502.judge(d)} == {row["id"]: row["verdict"]
                                                                    for row in d["claims"]}
    #: the arms, the three runs, the map and the two currencies are structural
    assert sorted(d["runs"]) == ["carried", "earned", "meter"], sorted(d["runs"])
    assert sorted(d["reward"]) == sorted(ARMS), sorted(d["reward"])
    assert sorted(d["accuracy"]) == sorted(ARMS), sorted(d["accuracy"])
    assert sorted(d["map"]) == ["carried", "earned"], sorted(d["map"])
    #: the counts that grow with the corpus are read as bounds
    assert d["spans"]["replicates"] == [e502.MIN_REPS], d["spans"]["replicates"]
    assert d["spans"]["config"]["earned"]["same"] >= 40, d["spans"]["config"]["earned"]["same"]
    assert len(d["spans"]["draw"]["earned"]["agree"]) >= 20, len(d["spans"]["draw"]["earned"]["agree"])
    for a in ARMS:
        assert d["reward"][a]["n"] >= e502.MIN_REPS, (a, d["reward"][a])
        #: the payout is a negative squared distance, so both currencies' cells are at or below zero; whether the
        #: action's is above the meter run's is the claim's business and the judge re-derives the verdict
        assert d["spans"]["reward_diagonal"]["earned"][a] <= 0.0, a
        assert d["spans"]["reward_diagonal"]["meter"][a] <= 0.0, a
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["earned"][a] <= 1.0, a
    for label in ("earned", "carried"):
        row = d["map"][label]
        if row is None:
            continue
        for a in ARMS:
            assert row[a]["replicates"] >= e502.MIN_REPS, (label, a)
            assert 0 <= row[a]["above_zero"] <= row[a]["replicates"], (label, a)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
