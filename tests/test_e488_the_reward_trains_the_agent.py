"""`e488` trains the agent's map by ascent on the world's payout, so the tests pin both faces of the four claims, the
field the two runs move, the bar the earning is registered against, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e488_the_reward_trains_the_agent as e488

ARMS = e488.ARMS
#: the reading's shape: two runs one field apart, the paid map moving on every replicate, and the paid run's reward
#: diagonal above the task-loss run's on two of the three arms with the accuracy unmoved
EARNED = {"naive": (+0.4000, +3.00), "ewc-block": (+0.3000, +2.50), "replay": (-0.1000, -0.80)}
ACCURACY = {"naive": (-0.0200, -0.50), "ewc-block": (+0.0100, +0.40), "replay": (-0.0300, -1.00)}
MOVED = {"paid": {"loop_earn": True}, "loss": {"loop_earn": None}}
REWARD_DIAGONAL = {"paid": {a: -6.3000 for a in ARMS}, "loss": {a: -6.9000 for a in ARMS}}
ACC_DIAGONAL = {"paid": {a: 0.7000 for a in ARMS}, "loss": {a: 0.7000 for a in ARMS}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.1, "se": 0.05, "sigma": sigma}


def _move(replicates=20, above=None, smallest=6.0, mean=7.0):
    above = dict(above or {a: replicates for a in ARMS})
    return {"paid": {a: {"replicates": replicates, "above_zero": above[a], "smallest": smallest, "mean": mean}
                     for a in ARMS},
            "loss": {a: {"replicates": replicates, "above_zero": replicates, "smallest": 6.0, "mean": 7.0}
                     for a in ARMS}}


def _doc(differ=None, draw_differ=None, earned=None, accuracy=None, move=None, moved=None, replicates=(20,),
         ok=True, reason="a run is absent, or carries no reward matrix or no policy movement"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "inert": {}, "draw": {}, "earning": {},
                "accuracy": {}, "move": {}, "spans": {}}
    earned = dict(earned or EARNED)
    accuracy = dict(accuracy or ACCURACY)
    return {
        "ok": True, "reason": None, "runs": {"paid": {}, "loss": {}},
        "same": {k: [1, 2] for k in (differ or [])},
        "inert": {"loop_earn": [False, True]},
        "draw": {"cue_sha1": True, "world_read_sha1": True, "reward_map_sha1": True},
        "earning": {a: _paired(earned[a][0], earned[a][1]) for a in ARMS},
        "accuracy": {a: _paired(accuracy[a][0], accuracy[a][1]) for a in ARMS},
        "move": move or _move(),
        "spans": {"arms": list(ARMS), "runs": ["paid", "loss"], "same_fields": 57,
                  "differ": sorted(differ or []), "inert": ["loop_earn"],
                  "moved": dict(moved or MOVED), "draw_fields": 23, "draw_differ": sorted(draw_differ or []),
                  "replicates": list(replicates),
                  "reward_diagonal": REWARD_DIAGONAL, "reward_last": REWARD_DIAGONAL,
                  "accuracy_diagonal": ACC_DIAGONAL, "accuracy_last": ACC_DIAGONAL},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e488.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one configuration, the paid map moving everywhere, the earning on two arms, the accuracy unmoved
    j = _judge()
    for cid in ("XB1", "XB2", "XB3", "XB4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # XB1: another config field differing, a draw field differing, a thin run, and the flag not moved
    assert _judge(differ=["iters"])["XB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["reward_map_sha1"])["XB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["XB1"].startswith("FALSIFIER")
    assert _judge(moved={"paid": {"loop_earn": None}, "loss": {"loop_earn": None}})["XB1"].startswith("FALSIFIER")

    # XB2: a replicate whose map did not move, and one whose smallest movement is zero
    assert _judge(move=_move(above={"naive": 19, "ewc-block": 20, "replay": 20}))["XB2"].startswith("FALSIFIER")
    assert _judge(move=_move(smallest=0.0))["XB2"].startswith("FALSIFIER")

    # XB3: one arm clearing the bar and the two-sigma bar, a gap under the bar, and a gap at or below zero
    assert _judge(earned={"naive": (+0.40, 3.00), "ewc-block": (-0.10, -0.80),
                          "replay": (+0.05, +0.30)})["XB3"].startswith("FALSIFIER")
    assert _judge(earned={"naive": (+0.20, +3.00), "ewc-block": (+0.05, +2.50),
                          "replay": (-0.10, -0.80)})["XB3"].startswith("FALSIFIER")
    assert _judge(earned={"naive": (-0.30, -2.60), "ewc-block": (-0.20, -2.10),
                          "replay": (-0.10, -0.80)})["XB3"].startswith("FALSIFIER")

    # XB4: an accuracy that rises at two sigma
    assert _judge(accuracy={"naive": (+0.05, +2.50), "ewc-block": (+0.01, +0.40),
                            "replay": (-0.03, -1.00)})["XB4"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e488.judge(_doc(ok=False)))


def test_the_runs_the_flags_and_the_bars_are_registered():
    assert e488.PAID.name == "e488_earned_label_earned_20reps.json"
    assert e488.LOSS.name == "e488_earned_label_policy_reward_20reps.json"
    assert e488.RUNNER.name == "e8_rate_network.py"
    assert set(e488.MOVED) == {"loop_earn"}, e488.MOVED
    assert set(e488.BOOKKEEPING) == {"json_out", "save_theta"}
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e488.MIN_REPS, e488.SIGMA, e488.BAR, e488.ARMS_NEEDED) == (20, 2.0, 0.25, 2)
    assert e488._inert("loop_earn", False, True) and e488._inert("loop_earn", None, True)
    assert not e488._inert("iters", 500, 100)
    assert e488.DEFAULTS.get("loop_earn") is False, e488.DEFAULTS.get("loop_earn")


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e488_the_reward_trains_the_agent.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e488.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs and the replicate count are structural; the counts that grow with the corpus are floors
    assert sorted(d["runs"]) == ["loss", "paid"], sorted(d["runs"])
    assert sorted(d["earning"]) == sorted(ARMS), sorted(d["earning"])
    assert sorted(d["accuracy"]) == sorted(ARMS), sorted(d["accuracy"])
    assert sorted(d["move"]["paid"]) == sorted(ARMS), sorted(d["move"]["paid"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    assert d["spans"]["draw_fields"] > 0, d["spans"]["draw_fields"]
    for a in ARMS:
        assert d["earning"][a]["n"] == 20, (a, d["earning"][a])
        assert d["accuracy"][a]["n"] == 20, (a, d["accuracy"][a])
        assert d["move"]["paid"][a]["replicates"] == 20, (a, d["move"]["paid"][a])
        #: the payout is a negative squared distance, so its cells are at or below zero and the accuracy is a rate:
        #: what is asserted here is the shape, and whether the earning resolved is the judge's business
        assert d["spans"]["reward_diagonal"]["paid"][a] <= 0.0, a
        assert d["spans"]["reward_diagonal"]["loss"][a] <= 0.0, a
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["paid"][a] <= 1.0, a
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["loss"][a] <= 1.0, a
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
