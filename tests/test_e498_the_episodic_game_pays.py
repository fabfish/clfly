"""`e498` lets the payout run with the label at the pass's first trial, so the tests pin both faces of the four claims,
the one draw field the flag adds, the target's step under both placements, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e498_the_episodic_game_pays as e498

ARMS = e498.ARMS
#: the reading's shape: the payout moved, the target follows the label, and the world pays in the pass
ACC = {"rewarded": {"naive": 0.8299, "ewc-block": 0.8139, "replay": 0.8267},
       "unpaid": {"naive": 0.8299, "ewc-block": 0.8139, "replay": 0.8267}}
REWARD_DIAG = {"naive": -4.9000, "ewc-block": -4.9500, "replay": -5.1000}
REWARD_LAST = {"naive": -5.4000, "ewc-block": -5.4500, "replay": -5.2000}
CONTRAST = {"naive": (+0.5000, +5.40), "ewc-block": (+0.5000, +5.10), "replay": (-0.1000, -1.20)}
STEPS = {"label_first": {"target_step": 1, "label_step": 0},
         "label_last": {"target_step": 7, "label_step": 6}}
MOVES = {"label_first": {"target_largest": 0.0, "target_mean": 0.0, "world_mean": 0.4, "world_largest": 1.2,
                         "examples": 32},
         "label_last": {"target_largest": 0.31, "target_mean": 0.12, "world_mean": 0.5, "world_largest": 1.4,
                        "examples": 32}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, added=None, draw_differ=None, steps=None, moves=None, contrast=None, same=None,
         replicates=(20,), ok=True, reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "target": {}, "same": {}, "reward": {}, "spans": {}}
    contrast = dict(contrast or CONTRAST)
    same = dict(same or {a: {"learned": True, "final_per_task": True, "replicates": True} for a in ARMS})
    reference = {"learned": [list(map(float, [0.8, 0.8, 0.85])) for _ in range(20)],
                 "final_per_task": [list(map(float, [0.6, 0.6, 0.6])) for _ in range(20)]}
    return {
        "ok": True, "reason": None, "runs": {"rewarded": {"artifact": "r"}, "unpaid": {"artifact": "u"}},
        "target": {"steps": dict(steps or STEPS), "moves": dict(moves or MOVES)},
        "same": same,
        "reward": {a: _paired(contrast[a][0], contrast[a][1]) for a in ARMS},
        "spans": {"arms": list(ARMS), "runs": ["rewarded", "unpaid"], "episode": e498.EPISODE,
                  "chance": e498.CHANCE, "replicates": list(replicates),
                  "config": {label: {"same": 55, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": {"loop_reward": True if label == "rewarded" else None}}
                             for label in ("rewarded", "unpaid")},
                  "draw": {label: {"agree": {"cue_sha1": True},
                                   "added": list(added if added is not None
                                                 else (["reward_map_sha1"] if label == "rewarded" else [])),
                                   "differ": list(draw_differ or []), "missing": []}
                           for label in ("rewarded", "unpaid")},
                  "accuracy_diagonal": {label: dict(ACC[label]) for label in ACC},
                  "accuracy_last": {label: {a: 0.5900 for a in ARMS} for label in ACC},
                  "reward_diagonal": dict(REWARD_DIAG), "reward_last": dict(REWARD_LAST)},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e498.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    j = _judge()
    for cid in ("OB1", "OB2", "OB3", "OB4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # OB1: another config field differing, the flag not moved, a draw field beyond the payout's map, a thin run
    assert _judge(differ=["iters"])["OB1"].startswith("FALSIFIER")
    assert _judge(added=[])["OB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["OB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["OB1"].startswith("FALSIFIER")

    # OB2: a target step that is not the label's plus one, a label-first target that moves, and a still state
    assert _judge(steps={"label_first": {"target_step": 7, "label_step": 0},
                         "label_last": {"target_step": 7, "label_step": 6}})["OB2"].startswith("FALSIFIER")
    assert _judge(moves={**MOVES, "label_first": {"target_largest": 0.01, "target_mean": 0.01, "world_mean": 0.4,
                                                  "world_largest": 1.2, "examples": 32}})["OB2"].startswith("FALSIFIER")
    assert _judge(moves={**MOVES, "label_first": {"target_largest": 0.0, "target_mean": 0.0, "world_mean": 0.0,
                                                  "world_largest": 0.0, "examples": 32}})["OB2"].startswith("FALSIFIER")
    assert _judge(moves={**MOVES, "label_last": {"target_largest": 0.0, "target_mean": 0.0, "world_mean": 0.5,
                                                 "world_largest": 1.4, "examples": 32}})["OB2"].startswith("FALSIFIER")

    # OB3: an accuracy the two runs do not share
    assert _judge(same={**{a: {"learned": True, "final_per_task": True, "replicates": True} for a in ARMS},
                        "replay": {"learned": False, "final_per_task": True, "replicates": True}}
                  )["OB3"].startswith("FALSIFIER")

    # OB4: one arm above its last row with two sigma, and one that does not resolve
    assert _judge(contrast={"naive": (+0.5000, +5.40), "ewc-block": (-0.0100, -0.20),
                            "replay": (-0.1000, -1.20)})["OB4"].startswith("FALSIFIER")
    assert _judge(contrast={"naive": (+0.5000, +1.20), "ewc-block": (+0.5000, +0.90),
                            "replay": (-0.1000, -1.20)})["OB4"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e498.judge(_doc(ok=False)))


def test_the_runs_the_flag_and_the_bars_are_registered():
    assert e498.REWARDED.name == "e498_earned_label_episode2_labelfirst_reward_20reps.json"
    assert e498.UNPAID.name == "e495_earned_label_episode2_labelfirst_20reps.json"
    assert e498.RUNNER.name == "e8_rate_network.py"
    assert set(e498.MOVED) == {"loop_reward"}, e498.MOVED
    assert e498.ADDED == ("reward_map_sha1",), e498.ADDED
    assert set(e498.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e498.EPISODE, e498.TAU, e498.SYMBOLS) == (2, 12, 4), (e498.EPISODE, e498.TAU, e498.SYMBOLS)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e498.MIN_REPS, e498.SIGMA, e498.CHANCE) == (20, 2.0, 0.25)
    assert e498._inert("loop_reward", None, True) and e498._inert("reward_map_sha1", None, "abc")
    assert not e498._inert("iters", 500, 100)
    assert e498.DEFAULTS.get("loop_reward") is False, e498.DEFAULTS.get("loop_reward")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e498_the_episodic_game_pays.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e498.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs and the replicate count are structural
    assert sorted(d["runs"]) == ["rewarded", "unpaid"], sorted(d["runs"])
    assert sorted(d["same"]) == sorted(ARMS), sorted(d["same"])
    assert sorted(d["reward"]) == sorted(ARMS), sorted(d["reward"])
    assert sorted(d["target"]["steps"]) == ["label_first", "label_last"], sorted(d["target"]["steps"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    for name, row in d["target"]["steps"].items():
        assert row["target_step"] == row["label_step"] + 1, (name, row)
    for a in ARMS:
        assert d["reward"][a]["n"] == 20, (a, d["reward"][a])
        #: the payout is a negative squared distance, so its cells are at or below zero; whether the diagonal is
        #: above the last row is the claim's business and the artifact's verdict is the one the judge re-derives
        assert d["spans"]["reward_diagonal"][a] <= 0.0 and d["spans"]["reward_last"][a] <= 0.0, a
        assert 0.0 <= d["spans"]["accuracy_diagonal"]["rewarded"][a] <= 1.0, a
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
