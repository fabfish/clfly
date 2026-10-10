"""`e487` redraws the world under the payout, so the tests pin both faces of the four claims, the fields the two runs
move, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e487_the_reward_in_a_second_world as e487

ARMS = e487.ARMS
#: the shape: the reward's diagonal below its last row, the accuracy's above, and the orderings reversed
REWARD_DIAG = {"naive": -6.70, "ewc-block": -6.60, "replay": -6.65}
REWARD_LAST = {"naive": -6.40, "ewc-block": -6.30, "replay": -6.50}
CONTRAST = {"naive": (-0.3000, -4.20), "ewc-block": (-0.3200, -4.50), "replay": (-0.1500, -3.10)}
ACC_DIAG = {"naive": 0.7400, "ewc-block": 0.6900, "replay": 0.7200}
ACC_LAST = {"naive": 0.5000, "ewc-block": 0.4700, "replay": 0.6600}
MOVED = {"w1_reward": {"loop_seed": 1, "loop_reward": True}, "w1": {"loop_seed": 1, "loop_reward": None},
         "w0_reward": {"loop_seed": None, "loop_reward": True}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, draw_differ=None, contrast=None, moved=None, acc_same=None, order_agree=False,
         replicates=(20,), ok=True, reason="a run is absent or carries no reward matrix"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "inert": {}, "draw": {}, "reward": {},
                "accuracy_same": {}, "order": {}, "spans": {}}
    contrast = dict(contrast or CONTRAST)
    acc_same = dict(acc_same or {a: {"learned": True, "final_per_task": True, "replicates": True} for a in ARMS})
    acc_order = sorted(ARMS, key=lambda a: ACC_DIAG[a], reverse=True)
    rew_order = sorted(ARMS, key=lambda a: REWARD_DIAG[a], reverse=True)
    return {
        "ok": True, "reason": None, "runs": {"w1_reward": {}, "w1": {}, "w0_reward": {}},
        "same": {k: [1, 2] for k in (differ or [])},
        "inert": {"w1_reward.loop_seed": [None, 1], "w1_reward.loop_reward": [None, True]},
        "draw": {"cue_sha1": True, "world_read_sha1": True},
        "reward": {a: _paired(contrast[a][0], contrast[a][1]) for a in ARMS},
        "accuracy_same": acc_same,
        "order": {"accuracy": acc_order, "reward": rew_order, "agrees": order_agree},
        "spans": {"arms": list(ARMS), "runs": ["w1_reward", "w1", "w0_reward"], "same_fields": 51,
                  "differ": sorted(differ or []), "inert": ["w1_reward.loop_seed", "w1_reward.loop_reward"],
                  "moved": dict(moved or MOVED), "draw_fields": 22, "draw_differ": sorted(draw_differ or []),
                  "payout_field": e487.PAYOUT_FIELD, "replicates": list(replicates),
                  "reward_diagonal": {a: REWARD_DIAG[a] for a in ARMS},
                  "reward_last": {a: REWARD_LAST[a] for a in ARMS},
                  "accuracy_diagonal": {a: ACC_DIAG[a] for a in ARMS},
                  "accuracy_last": {a: ACC_LAST[a] for a in ARMS}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e487.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one configuration across the three runs, the reward's shape in the second world, the payout not
    #: touching the accuracy, and the currencies disagreeing there too
    j = _judge()
    for cid in ("RA1", "RA2", "RA3", "RA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # RA1: another config field differing, a draw field differing, a wrong moved field, and a thin run
    assert _judge(differ=["iters"])["RA1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["world_read_sha1"])["RA1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["RA1"].startswith("FALSIFIER")
    bad_moved = {**MOVED, "w1": {"loop_seed": 1, "loop_reward": True}}
    assert _judge(moved=bad_moved)["RA1"].startswith("FALSIFIER")
    bad_seed = {**MOVED, "w0_reward": {"loop_seed": 2, "loop_reward": True}}
    assert _judge(moved=bad_seed)["RA1"].startswith("FALSIFIER")

    # RA2: an arm whose reward contrast does not resolve, and one whose diagonal is at or above its last row
    assert _judge(contrast={"naive": (-0.30, -4.2), "ewc-block": (-0.32, -4.5),
                            "replay": (-0.15, -1.20)})["RA2"].startswith("FALSIFIER")
    assert _judge(contrast={"naive": (+0.05, +0.60), "ewc-block": (-0.32, -4.5),
                            "replay": (-0.15, -3.1)})["RA2"].startswith("FALSIFIER")

    # RA3: an accuracy the two world-1 runs do not share
    assert _judge(acc_same={**{a: {"learned": True, "final_per_task": True, "replicates": True} for a in ARMS},
                            "replay": {"learned": False, "final_per_task": True, "replicates": True}
                            })["RA3"].startswith("FALSIFIER")

    # RA4: orderings that agree
    assert _judge(order_agree=True)["RA4"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e487.judge(_doc(ok=False)))


def test_the_runs_the_flags_and_the_bars_are_registered():
    assert e487.W1R.name == "e487_earned_label_worldseed1_reward_20reps.json"
    assert e487.W1.name == "e443_earned_label_worldseed1_20reps.json"
    assert e487.W0R.name == "e485_earned_label_reward_20reps.json"
    assert e487.RUNNER.name == "e8_rate_network.py"
    assert set(e487.MOVED) == {"loop_seed", "loop_reward"}, e487.MOVED
    assert set(e487.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e487.PAYOUT_FIELD == "reward_map_sha1"
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e487.SIGMA, e487.MIN_REPS) == (2.0, 20)
    assert e487._inert("loop_seed", None, 1) and e487._inert("loop_reward", None, True)
    assert not e487._inert("iters", 500, 100)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e487_the_reward_in_a_second_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e487.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms and the replicate count are structural; the counts that grow with the corpus are floors
    assert sorted(d["reward"]) == sorted(ARMS), sorted(d["reward"])
    assert sorted(d["accuracy_same"]) == sorted(ARMS), sorted(d["accuracy_same"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    assert not d["spans"]["differ"] and not d["spans"]["draw_differ"], d["spans"]
    assert sorted(d["spans"]["reward_diagonal"]) == sorted(ARMS), sorted(d["spans"]["reward_diagonal"])
    for a in ARMS:
        assert d["reward"][a]["n"] == 20, (a, d["reward"][a])
        #: whether the reward's diagonal sits below its last row is the claim's business and the artifact's verdict
        #: is the one the judge re-derives, so what is asserted here is the shape and not the outcome
        assert d["spans"]["reward_diagonal"][a] < 0.0 and d["spans"]["reward_last"][a] < 0.0, a
        assert d["spans"]["accuracy_diagonal"][a] > d["spans"]["accuracy_last"][a], a
    assert d["order"]["agrees"] is False, d["order"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
