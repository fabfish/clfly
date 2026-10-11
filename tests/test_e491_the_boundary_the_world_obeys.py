"""`e491` makes the world obey the episode's boundary, so the tests pin both faces of the three claims, the one draw
field the flag adds, the hand-driven measurement's two numbers, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e491_the_boundary_the_world_obeys as e491

ARMS = e491.ARMS
#: the reading's shape: the one flag moved, the world's rule obeying the mark, and a recovery on two arms
DIAG = {"reset": {"naive": 0.7300, "ewc-block": 0.7000, "replay": 0.6900},
        "carry": {"naive": 0.2476, "ewc-block": 0.2497, "replay": 0.2524}}
LAST = {"reset": {a: 0.4500 for a in ARMS}, "carry": {a: 0.2441 for a in ARMS}}
MOVE = {"naive": (+0.4824, +8.00), "ewc-block": (+0.4503, +7.20), "replay": (+0.4376, +6.10)}
RULE = {"carry": (0.0124, 13.21), "reset": (0.0, 0.0)}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, added=None, draw_differ=None, rule=None, move=None, diag=None, replicates=(20,), ok=True,
         reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "rule": {}, "recovery": {}, "spans": {}}
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    move = dict(move or MOVE)
    rule = dict(rule or RULE)
    rule_doc = {}
    for k, v in rule.items():
        biggest = 0.0332 if k == "carry" else (0.0 if v[0] == 0.0 else 0.02)
        rule_doc[k] = {"pairing": _paired(v[0], v[1], n=64), "largest": biggest, "scale": 0.3369, "at": 8,
                       "examples": 64}
    return {
        "ok": True, "reason": None, "runs": {"reset": {"artifact": "r"}, "carry": {"artifact": "c"}},
        "rule": rule_doc,
        "recovery": {a: _paired(move[a][0], move[a][1]) for a in ARMS},
        "spans": {"arms": list(ARMS), "runs": ["reset", "carry"], "episode": e491.EPISODE,
                  "chance": e491.CHANCE, "replicates": list(replicates),
                  "config": {label: {"same": 55, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": {"loop_episode_reset": True if label == "reset" else None}}
                             for label in ("reset", "carry")},
                  "draw": {label: {"agree": {"cue_sha1": True}, "differ": list(draw_differ or []),
                                   "added": list(added if added is not None else (["episode_reset"] if label == "reset"
                                                                                  else [])),
                                   "missing": [], "card_fields": 26} for label in ("reset", "carry")},
                  "accuracy_diagonal": {label: dict(diag[label]) for label in diag},
                  "accuracy_last": {label: dict(LAST[label]) for label in LAST}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e491.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("GB1", "GB2", "GB3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # GB1: another config field differing, the flag not moved, a draw field beyond the one the flag adds, and a thin run
    assert _judge(differ=["iters"])["GB1"].startswith("FALSIFIER")
    assert _judge(added=[])["GB1"].startswith("FALSIFIER")
    assert _judge(added=["episode_reset", "boundary_sha1"])["GB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["boundary_sha1"])["GB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["GB1"].startswith("FALSIFIER")

    # GB2: a reset that does not drop the past, and a carry that does not resolve
    assert _judge(rule={"carry": (0.0124, 13.21), "reset": (0.0010, 4.00)})["GB2"].startswith("FALSIFIER")
    assert _judge(rule={"carry": (0.0002, 0.80), "reset": (0.0, 0.0)})["GB2"].startswith("FALSIFIER")

    # GB3: a recovery on one arm, a recovery that does not resolve, and an arm still at chance
    assert _judge(move={"naive": (+0.4824, +8.00), "ewc-block": (+0.0010, +0.30),
                        "replay": (+0.0005, +0.20)})["GB3"].startswith("FALSIFIER")
    assert _judge(move={"naive": (+0.4824, +1.20), "ewc-block": (+0.4503, +0.90),
                        "replay": (+0.4376, +1.10)})["GB3"].startswith("FALSIFIER")
    assert _judge(diag={"reset": {"naive": 0.7300, "ewc-block": 0.2600, "replay": 0.6900},
                        "carry": DIAG["carry"]})["GB3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e491.judge(_doc(ok=False)))


def test_the_run_the_flag_and_the_bars_are_registered():
    assert e491.RESET.name == "e491_earned_label_episode3_boundary_reset_20reps.json"
    assert e491.CARRY.name == "e489_earned_label_episode3_boundary_20reps.json"
    assert e491.RUNNER.name == "e8_rate_network.py"
    assert set(e491.MOVED) == {"loop_episode_reset"}, e491.MOVED
    assert e491.ADDED == ("episode_reset",), e491.ADDED
    assert set(e491.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e491.EPISODE, e491.TAU) == (3, 12), (e491.EPISODE, e491.TAU)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e491.MIN_REPS, e491.SIGMA, e491.CHANCE, e491.BAR) == (20, 2.0, 0.25, 0.10)
    assert e491._inert("loop_episode_reset", None, True) and e491._inert("loop_episode_reset", False, True)
    assert not e491._inert("iters", 500, 100)
    assert e491.DEFAULTS.get("loop_episode_reset") is False, e491.DEFAULTS.get("loop_episode_reset")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e491_the_boundary_the_world_obeys.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e491.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs and the replicate count are structural; the counts that grow with the corpus are floors
    assert sorted(d["runs"]) == ["carry", "reset"], sorted(d["runs"])
    assert sorted(d["recovery"]) == sorted(ARMS), sorted(d["recovery"])
    assert sorted(d["spans"]["accuracy_diagonal"]["reset"]) == sorted(ARMS), d["spans"]["accuracy_diagonal"]
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    assert sorted(d["rule"]) == ["carry", "reset"], sorted(d["rule"])
    assert d["rule"]["reset"]["pairing"]["n"] > 0, d["rule"]["reset"]
    for a in ARMS:
        assert d["recovery"][a]["n"] == 20, (a, d["recovery"][a])
        for label in ("reset", "carry"):
            #: the accuracy is a rate, so what is asserted here is the shape and not whether the task came back
            assert 0.0 <= d["spans"]["accuracy_diagonal"][label][a] <= 1.0, (a, label)
    assert d["rule"]["carry"]["scale"] > 0.0, d["rule"]["carry"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
