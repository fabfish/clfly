"""`e494` takes the loop out of the episode, so the tests pin both faces of the three claims, the one flag the draw
does not move, the two shares at one width, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e494_the_episode_without_the_world as e494

ARMS = e494.ARMS
#: the reading's shape: the loop moved, the unwired share above the wired one, and a recovery on two arms
DIAG = {"unwired": {"naive": 0.7300, "ewc-block": 0.7000, "replay": 0.6900},
        "wired": {"naive": 0.3104, "ewc-block": 0.2944, "replay": 0.3031}}
LAST = {"unwired": {a: 0.4700 for a in ARMS}, "wired": {a: 0.2896 for a in ARMS}}
MOVE = {"naive": (+0.4196, +8.20), "ewc-block": (+0.4056, +7.60), "replay": (+0.3869, +6.90)}
#: the instrument: one width, two worlds
SHARE = {"wired": (0.1648, 4.2687, 0.0386, 32), "unwired": (0.6000, 4.1000, 0.1463, 32)}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, draw_differ=None, share=None, move=None, diag=None, replicates=(20,), ok=True,
         reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    move = dict(move or MOVE)
    share = dict(share or SHARE)
    return {
        "ok": True, "reason": None, "runs": {"unwired": {"artifact": "n"}, "wired": {"artifact": "w"}},
        "share": {name: {"across": v[0], "within": 1e-8, "scale": v[1], "share": v[2], "width": v[3]}
                  for name, v in share.items()},
        "recovery": {a: _paired(move[a][0], move[a][1]) for a in ARMS},
        "spans": {"arms": list(ARMS), "runs": ["unwired", "wired"], "episode": e494.EPISODE,
                  "chance": e494.CHANCE, "replicates": list(replicates),
                  "config": {label: {"same": 55, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": {"no_feedback": True if label == "unwired" else False}}
                             for label in ("unwired", "wired")},
                  "draw": {label: {"fields": 26, "differ": list(draw_differ or [])} for label in ("unwired", "wired")},
                  "accuracy_diagonal": {label: dict(diag[label]) for label in diag},
                  "accuracy_last": {label: dict(LAST[label]) for label in LAST}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e494.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("KB1", "KB2", "KB3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # KB1: another config field differing, a draw field differing, and a thin run
    assert _judge(differ=["iters"])["KB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["KB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["KB1"].startswith("FALSIFIER")

    # KB2: an unwired read that carries no more of the label, and a share that is not positive
    assert _judge(share={"wired": SHARE["wired"], "unwired": (0.1000, 4.1000, 0.0244, 32)})["KB2"].startswith("FALSIFIER")
    assert _judge(share={"wired": (0.0, 4.2687, 0.0, 32), "unwired": (0.0, 4.1000, 0.0, 32)})["KB2"].startswith("FALSIFIER")

    # KB3: a recovery on one arm, a recovery that does not resolve, and an arm still at chance
    assert _judge(move={"naive": (+0.4196, +8.20), "ewc-block": (+0.0010, +0.30),
                        "replay": (+0.0005, +0.20)})["KB3"].startswith("FALSIFIER")
    assert _judge(move={"naive": (+0.4196, +1.20), "ewc-block": (+0.4056, +0.90),
                        "replay": (+0.3869, +1.10)})["KB3"].startswith("FALSIFIER")
    assert _judge(diag={"unwired": {"naive": 0.7300, "ewc-block": 0.2600, "replay": 0.6900},
                        "wired": DIAG["wired"]})["KB3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e494.judge(_doc(ok=False)))


def test_the_runs_the_flag_and_the_bars_are_registered():
    assert e494.NOWORLD.name == "e494_earned_label_episode2_noworld_20reps.json"
    assert e494.WIRED.name == "e493_earned_label_episode2_modelread_20reps.json"
    assert e494.RUNNER.name == "e8_rate_network.py"
    assert set(e494.MOVED) == {"no_feedback"}, e494.MOVED
    assert set(e494.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e494.EPISODE, e494.TAU, e494.SYMBOLS) == (2, 12, 4), (e494.EPISODE, e494.TAU, e494.SYMBOLS)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e494.MIN_REPS, e494.SIGMA, e494.CHANCE, e494.BAR) == (20, 2.0, 0.25, 0.10)
    assert e494._inert("no_feedback", False, True)
    assert not e494._inert("iters", 500, 100)
    assert e494.DEFAULTS.get("no_feedback") is False, e494.DEFAULTS.get("no_feedback")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e494_the_episode_without_the_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e494.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs and the replicate count are structural
    assert sorted(d["runs"]) == ["unwired", "wired"], sorted(d["runs"])
    assert sorted(d["recovery"]) == sorted(ARMS), sorted(d["recovery"])
    assert sorted(d["share"]) == ["unwired", "wired"], sorted(d["share"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    for name in d["share"]:
        #: one width, two worlds: the model's own thirty-two columns in both
        assert d["share"][name]["width"] == 32, (name, d["share"][name])
        #: the cues are deterministic in the instrument and the past is fixed, so the within-symbol spread is only
        #: the float's floor and what is asserted here is the shape
        assert d["share"][name]["within"] <= 1e-3 * d["share"][name]["across"], (name, d["share"][name])
        assert d["share"][name]["across"] > 0.0, (name, d["share"][name])
    for a in ARMS:
        assert d["recovery"][a]["n"] == 20, (a, d["recovery"][a])
        for label in ("unwired", "wired"):
            assert 0.0 <= d["spans"]["accuracy_diagonal"][label][a] <= 1.0, (a, label)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
