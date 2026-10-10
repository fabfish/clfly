"""`e485` reads the first runner artifact that carries a reward, so the tests pin both faces of the four claims, the
draw the flag adds, and the refusal when the run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e485_the_benchmark_pays_a_reward as e485
from experiments.e172_parser_registry import parser_keys

ARMS = e485.ARMS


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, flags=(None, True), draw_differ=None, reward=None, sigma=None, accuracy=None,
         first_identical=True, ok=True, reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "inert": {}, "draw": {}, "diagonal": {},
                "order": {}, "first": {}, "spans": {}}
    #: the shape: the buffer leads on both currencies, so the two orderings agree
    reward = dict(reward or {"naive": 1.20, "ewc-block": 0.80, "replay": 2.10})
    sigma = dict(sigma or {"naive": 4.0, "ewc-block": 3.0, "replay": 5.0})
    accuracy = dict(accuracy or {"naive": 0.60, "ewc-block": 0.50, "replay": 0.72})
    draw_differ = list(draw_differ or [])
    order = sorted(ARMS, key=lambda a: accuracy[a], reverse=True)
    rorder = sorted(ARMS, key=lambda a: reward[a], reverse=True)
    return {
        "ok": True, "reason": None,
        "runs": {"reward": {"artifact": e485.NEW.name}, "card": {"artifact": e485.BASE.name, "flag": None}},
        "same": {k: [1, 2] for k in (differ or [])},
        "inert": {"loop_reward": [None, True], "loop_holdout": [None, False]},
        "draw": {k: True for k in ("cue_sha1", "world_read_sha1")},
        "diagonal": {a: {"reward": _paired(reward[a], sigma[a]), "accuracy_diagonal": accuracy[a]} for a in ARMS},
        "order": {"accuracy": order, "reward": rorder, "agrees": order == rorder},
        "first": {"by_arm": {a: [[1.0, None, None]] * 20 for a in ARMS}, "identical": first_identical},
        "spans": {"arms": list(ARMS), "same_fields": 51, "differ": sorted(differ or []),
                  "inert": ["loop_holdout", "loop_reward"], "flags": list(flags),
                  "draw_fields": 18, "draw_differ": sorted(draw_differ), "payout_field": e485.PAYOUT_FIELD,
                  "replicates": [20],
                  "reward_diagonal": {a: reward[a] for a in ARMS},
                  "reward_last": {a: -1.0 for a in ARMS}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e485.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one config field moved, the reward keeps its diagonal, the currencies agree, and task 0 is shared
    j = _judge()
    for cid in ("RA1", "RA2", "RA3", "RA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # RA1: another config field differing, a draw field differing, and a flag that did not move
    assert _judge(differ=["iters"])["RA1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["world_read_sha1"])["RA1"].startswith("FALSIFIER")
    assert _judge(flags=(True, True))["RA1"].startswith("FALSIFIER")

    # RA2: an arm whose reward diagonal does not exceed its last row, and one that is unresolved
    assert _judge(reward={"naive": 0.10, "ewc-block": 0.80, "replay": 2.10})["RA2"].startswith("FALSIFIER")
    assert _judge(sigma={"naive": 1.20, "ewc-block": 3.0, "replay": 5.0})["RA2"].startswith("FALSIFIER")
    assert _judge(sigma={"naive": 2.10, "ewc-block": 3.0, "replay": 5.0})["RA2"].startswith("MET")

    # RA3: a reward that orders the arms differently from the accuracy
    assert _judge(accuracy={"naive": 0.72, "ewc-block": 0.50, "replay": 0.60},
                  reward={"naive": 1.20, "ewc-block": 0.80, "replay": 2.10})["RA3"].startswith("FALSIFIER")

    # RA4: first rows that differ across the arms
    assert _judge(first_identical=False)["RA4"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e485.judge(_doc(ok=False)))


def test_the_runs_the_flag_and_the_bars_are_registered():
    assert e485.NEW.name == "e485_earned_label_reward_20reps.json"
    assert e485.BASE.name == "e438_earned_label_three_arms_20reps.json"
    assert e485.RUNNER.name == "e8_rate_network.py"
    assert e485.FLAG == "loop_reward" and set(e485.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e485.PAYOUT_FIELD == "reward_map_sha1"
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e485.SIGMA, e485.BAR, e485.FLOOR) == (2.0, 0.50, 0.20)
    #: the runner's own syntax tree carries the flag, and it is a `store_true` so its default is False
    assert e485.FLAG in parser_keys(e485.RUNNER), "the runner does not define --loop-reward"
    assert e485.DEFAULTS.get(e485.FLAG) is False, e485.DEFAULTS.get(e485.FLAG)
    assert e485._inert("loop_reward", None, True) and e485._inert("json_out", "a", "b")
    assert not e485._inert("iters", 500, 100)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e485_the_benchmark_pays_a_reward.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e485.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms and the replicate count are structural; the counts that grow with the corpus are floors
    assert sorted(d["diagonal"]) == sorted(ARMS), sorted(d["diagonal"])
    assert d["spans"]["flags"] == [None, True], d["spans"]["flags"]
    assert not d["spans"]["differ"] and not d["spans"]["draw_differ"], d["spans"]
    assert sorted(d["spans"]["reward_diagonal"]) == sorted(ARMS), sorted(d["spans"]["reward_diagonal"])
    for a in ARMS:
        assert d["diagonal"][a]["reward"]["n"] == 20, (a, d["diagonal"][a])
        assert len(d["first"]["by_arm"][a]) == 20, a
    assert d["first"]["identical"] is True, d["first"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
