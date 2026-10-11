"""`e492` shortens the episode to two trials, so the tests pin both faces of the three claims, the one field the draw
moves, the label-share instrument's own zero within-symbol spread, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e492_the_episode_at_two_trials as e492

ARMS = e492.ARMS
#: the reading's shape: the split moved, the label's share larger at two trials, and a recovery on two arms
DIAG = {"two": {"naive": 0.7000, "ewc-block": 0.6800, "replay": 0.6600},
        "three": {"naive": 0.2476, "ewc-block": 0.2497, "replay": 0.2524}}
LAST = {"two": {a: 0.4300 for a in ARMS}, "three": {a: 0.2441 for a in ARMS}}
MOVE = {"naive": (+0.4524, +7.40), "ewc-block": (+0.4303, +6.90), "replay": (+0.4076, +5.80)}
SHARE = {1: (0.2100, 0.0, 1.40), 2: (0.1200, 0.0, 0.95), 3: (0.0450, 0.0, 0.78)}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, draw_differ=None, draw_moved=None, share=None, move=None, diag=None, replicates=(20,),
         ok=True, reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    move = dict(move or MOVE)
    share = dict(share or SHARE)
    return {
        "ok": True, "reason": None, "runs": {"two": {"artifact": "t"}, "three": {"artifact": "h"}},
        "share": {k: {"across": v[0], "within": v[1], "state_scale": v[2], "examples": 48}
                  for k, v in share.items()},
        "recovery": {a: _paired(move[a][0], move[a][1]) for a in ARMS},
        "spans": {"arms": list(ARMS), "runs": ["two", "three"], "chance": e492.CHANCE, "symbols": e492.SYMBOLS,
                  "replicates": list(replicates),
                  "config": {label: {"same": 55, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": {"loop_episode": 2 if label == "two" else 3}}
                             for label in ("two", "three")},
                  "draw": {label: {"fields": 25, "differ": list(draw_differ or []),
                                   "moved": dict(draw_moved or {"episode_len": [3, 2]})}
                           for label in ("two", "three")},
                  "accuracy_diagonal": {label: dict(diag[label]) for label in diag},
                  "accuracy_last": {label: dict(LAST[label]) for label in LAST}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e492.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("HB1", "HB2", "HB3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # HB1: another config field differing, a draw field differing past episode_len, the split not moved, and a thin run
    assert _judge(differ=["iters"])["HB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["boundary_sha1"])["HB1"].startswith("FALSIFIER")
    assert _judge(draw_moved={"episode_len": [3, 3]})["HB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["HB1"].startswith("FALSIFIER")

    # HB2: a share that does not grow with the trial, and a within-symbol spread that is not zero
    assert _judge(share={1: (0.21, 0.0, 1.4), 2: (0.02, 0.0, 0.8), 3: (0.045, 0.0, 0.78)})["HB2"].startswith("FALSIFIER")
    assert _judge(share={1: (0.21, 0.0, 1.4), 2: (0.12, 0.0, 0.95), 3: (0.045, 0.01, 0.78)})["HB2"].startswith("FALSIFIER")
    assert _judge(share={1: (0.0, 0.0, 1.4), 2: (0.12, 0.0, 0.95), 3: (0.045, 0.0, 0.78)})["HB2"].startswith("FALSIFIER")

    # HB3: a recovery on one arm, a recovery that does not resolve, and an arm still at chance
    assert _judge(move={"naive": (+0.4524, +7.40), "ewc-block": (+0.0010, +0.30),
                        "replay": (+0.0005, +0.20)})["HB3"].startswith("FALSIFIER")
    assert _judge(move={"naive": (+0.4524, +1.20), "ewc-block": (+0.4303, +0.90),
                        "replay": (+0.4076, +1.10)})["HB3"].startswith("FALSIFIER")
    assert _judge(diag={"two": {"naive": 0.7000, "ewc-block": 0.2600, "replay": 0.6600},
                        "three": DIAG["three"]})["HB3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e492.judge(_doc(ok=False)))


def test_the_runs_the_split_and_the_bars_are_registered():
    assert e492.TWO.name == "e492_earned_label_episode2_boundary_20reps.json"
    assert e492.THREE.name == "e489_earned_label_episode3_boundary_20reps.json"
    assert e492.CARD.name == "e438_earned_label_three_arms_20reps.json"
    assert e492.RUNNER.name == "e8_rate_network.py"
    assert set(e492.MOVED) == {"loop_episode"}, e492.MOVED
    assert e492.DRAW_MOVED == ("episode_len",), e492.DRAW_MOVED
    assert set(e492.BOOKKEEPING) == {"json_out", "save_theta"}
    assert e492.SPLITS == (1, 2, 3), e492.SPLITS
    assert (e492.TAU, e492.SYMBOLS) == (12, 4), (e492.TAU, e492.SYMBOLS)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e492.MIN_REPS, e492.SIGMA, e492.CHANCE, e492.BAR) == (20, 2.0, 0.25, 0.10)
    assert e492._inert("loop_episode", 3, 2) and e492._inert("episode_len", 3, 2)
    assert not e492._inert("iters", 500, 100)
    assert e492.DEFAULTS.get("loop_episode") == 1, e492.DEFAULTS.get("loop_episode")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e492_the_episode_at_two_trials.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e492.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs, the splits and the replicate count are structural
    assert sorted(d["runs"]) == ["three", "two"], sorted(d["runs"])
    assert sorted(d["recovery"]) == sorted(ARMS), sorted(d["recovery"])
    assert sorted(int(k) for k in d["share"]) == [1, 2, 3], sorted(d["share"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    for k in d["share"]:
        #: the cues are deterministic in the instrument and the past is fixed, so the within-symbol spread is only
        #: the float's floor
        assert d["share"][k]["within"] <= 1e-3 * d["share"][k]["across"], (k, d["share"][k])
        assert d["share"][k]["across"] > 0.0, (k, d["share"][k])
    for a in ARMS:
        assert d["recovery"][a]["n"] == 20, (a, d["recovery"][a])
        for label in ("two", "three"):
            assert 0.0 <= d["spans"]["accuracy_diagonal"][label][a] <= 1.0, (a, label)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
