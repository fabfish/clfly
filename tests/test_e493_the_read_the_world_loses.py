"""`e493` swaps the read from the world's eight numbers to the model's own thirty-two inside the episode, so the tests
pin both faces of the three claims, the one flag the draw does not move, the share's two widths, and the refusal when
a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e493_the_read_the_world_loses as e493

ARMS = e493.ARMS
#: the reading's shape: the read moved, the shares at both widths, and a recovery on two arms
DIAG = {"model": {"naive": 0.7800, "ewc-block": 0.7500, "replay": 0.7400},
        "world": {"naive": 0.2434, "ewc-block": 0.2424, "replay": 0.2333}}
LAST = {"model": {a: 0.4900 for a in ARMS}, "world": {a: 0.2507 for a in ARMS}}
MOVE = {"naive": (+0.5366, +9.10), "ewc-block": (+0.5076, +8.40), "replay": (+0.5067, +7.70)}
#: the instrument: at two trials the world's share against the model's, at one trial beside them. The synthetic
#: values put the model's share **above** the world's at two trials, which is the direction JB2 is registered in; the
#: live artifact is the other way round and its verdict is the judge re-deriving it
SHARE = {2: {"world8": (0.0377, 0.6600, 0.0571, 8), "model32": (0.3000, 4.2687, 0.0703, 32)},
         1: {"world8": (0.9144, 0.6232, 1.4673, 8), "model32": (4.2793, 4.0780, 1.0494, 32)}}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, draw_differ=None, share=None, move=None, diag=None, replicates=(20,), ok=True,
         reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "share": {}, "recovery": {}, "one_trial": {}, "spans": {}}
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    move = dict(move or MOVE)
    share = dict(share or SHARE)
    return {
        "ok": True, "reason": None, "runs": {"model": {"artifact": "m"}, "world": {"artifact": "w"}},
        "share": {str(k): {name: {"across": v[0], "within": 1e-8, "scale": v[1], "share": v[2], "width": v[3]}
                           for name, v in reads.items()} for k, reads in share.items()},
        "recovery": {a: _paired(move[a][0], move[a][1]) for a in ARMS},
        "one_trial": {"artifact": e493.ONE_TRIAL.name, "accuracy_diagonal": {a: 0.86 for a in ARMS}},
        "spans": {"arms": list(ARMS), "runs": ["model", "world"], "episode": e493.EPISODE,
                  "chance": e493.CHANCE, "replicates": list(replicates),
                  "config": {label: {"same": 55, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": {"readout_from_world": False if label == "model" else True}}
                             for label in ("model", "world")},
                  "draw": {label: {"fields": 26, "differ": list(draw_differ or [])} for label in ("model", "world")},
                  "readout": {label: {"size": 32, "draw_seed": 0, "subset_sha1": "59926518137c"}
                              for label in ("model", "world")},
                  "accuracy_diagonal": {label: dict(diag[label]) for label in diag},
                  "accuracy_last": {label: dict(LAST[label]) for label in LAST}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e493.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("JB1", "JB2", "JB3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # JB1: another config field differing, a draw field differing, and a thin run
    assert _judge(differ=["iters"])["JB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["JB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["JB1"].startswith("FALSIFIER")

    # JB2: a model share at or below the world's, and a share that is not positive
    flip = {2: {"world8": (0.0377, 0.6600, 0.0571, 8), "model32": (0.1648, 8.0000, 0.0206, 32)},
            1: SHARE[1]}
    assert _judge(share=flip)["JB2"].startswith("FALSIFIER")
    zero = {2: {"world8": (0.0, 0.6600, 0.0, 8), "model32": (0.0, 4.2687, 0.0, 32)}, 1: SHARE[1]}
    assert _judge(share=zero)["JB2"].startswith("FALSIFIER")

    # JB3: a recovery on one arm, a recovery that does not resolve, and an arm still at chance
    assert _judge(move={"naive": (+0.5366, +9.10), "ewc-block": (+0.0010, +0.30),
                        "replay": (+0.0005, +0.20)})["JB3"].startswith("FALSIFIER")
    assert _judge(move={"naive": (+0.5366, +1.20), "ewc-block": (+0.5076, +0.90),
                        "replay": (+0.5067, +1.10)})["JB3"].startswith("FALSIFIER")
    assert _judge(diag={"model": {"naive": 0.7800, "ewc-block": 0.2600, "replay": 0.7400},
                        "world": DIAG["world"]})["JB3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e493.judge(_doc(ok=False)))


def test_the_runs_the_read_and_the_bars_are_registered():
    assert e493.MODEL.name == "e493_earned_label_episode2_modelread_20reps.json"
    assert e493.WORLD.name == "e492_earned_label_episode2_boundary_20reps.json"
    assert e493.ONE_TRIAL.name == "e455_earned_label_neurons_20reps.json"
    assert e493.RUNNER.name == "e8_rate_network.py"
    assert set(e493.MOVED) == {"readout_from_world"}, e493.MOVED
    assert set(e493.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e493.EPISODE, e493.TAU, e493.SYMBOLS) == (2, 12, 4), (e493.EPISODE, e493.TAU, e493.SYMBOLS)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e493.MIN_REPS, e493.SIGMA, e493.CHANCE, e493.BAR) == (20, 2.0, 0.25, 0.10)
    assert e493._inert("readout_from_world", True, False)
    assert not e493._inert("iters", 500, 100)
    assert e493.DEFAULTS.get("readout_from_world") is False, e493.DEFAULTS.get("readout_from_world")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e493_the_read_the_world_loses.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e493.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs, the two widths and the replicate count are structural
    assert sorted(d["runs"]) == ["model", "world"], sorted(d["runs"])
    assert sorted(d["recovery"]) == sorted(ARMS), sorted(d["recovery"])
    assert sorted(int(k) for k in d["share"]) == [1, 2], sorted(d["share"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    for k in d["share"]:
        assert sorted(d["share"][k]) == ["model32", "world8"], sorted(d["share"][k])
        assert d["share"][k]["world8"]["width"] == 8 and d["share"][k]["model32"]["width"] == 32, d["share"][k]
        for name in ("world8", "model32"):
            #: the same instrument `e492` used: the cues are deterministic and the past is fixed, so the
            #: within-symbol spread is only the float's floor and what is asserted here is the shape
            assert d["share"][k][name]["within"] <= 1e-3 * d["share"][k][name]["across"], (k, name)
            assert d["share"][k][name]["across"] > 0.0, (k, name)
    for a in ARMS:
        assert d["recovery"][a]["n"] == 20, (a, d["recovery"][a])
        for label in ("model", "world"):
            assert 0.0 <= d["spans"]["accuracy_diagonal"][label][a] <= 1.0, (a, label)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
