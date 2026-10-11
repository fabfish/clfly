"""`e495` moves the episode's label from its last trial to its first, so the tests pin both faces of the three claims,
the one draw field the flag adds, the two shares at one width, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e495_the_label_first as e495

ARMS = e495.ARMS
#: the reading's shape: the placement moved, the label-first share above the label-last one, and a recovery on two arms
DIAG = {"first": {"naive": 0.7000, "ewc-block": 0.6800, "replay": 0.6700},
        "last": {"naive": 0.3104, "ewc-block": 0.2944, "replay": 0.3031}}
LAST = {"first": {a: 0.4400 for a in ARMS}, "last": {a: 0.2896 for a in ARMS}}
MOVE = {"naive": (+0.3896, +7.80), "ewc-block": (+0.3856, +7.10), "replay": (+0.3669, +6.60)}
#: the instrument: one width, one world, two placements
SHARE = {"last": (0.1648, 4.2687, 0.0386, 32), "first": (0.5000, 4.1000, 0.1220, 32)}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, added=None, draw_differ=None, share=None, move=None, diag=None, replicates=(20,), ok=True,
         reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    move = dict(move or MOVE)
    share = dict(share or SHARE)
    return {
        "ok": True, "reason": None, "runs": {"first": {"artifact": "f"}, "last": {"artifact": "l"}},
        "share": {name: {"across": v[0], "within": 1e-8, "scale": v[1], "share": v[2], "width": v[3]}
                  for name, v in share.items()},
        "recovery": {a: _paired(move[a][0], move[a][1]) for a in ARMS},
        "spans": {"arms": list(ARMS), "runs": ["first", "last"], "episode": e495.EPISODE,
                  "chance": e495.CHANCE, "replicates": list(replicates),
                  "config": {label: {"same": 55, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": {"loop_label_first": True if label == "first" else False}}
                             for label in ("first", "last")},
                  "draw": {label: {"agree": {"cue_sha1": True},
                                   "added": list(added if added is not None else (["label_first"] if label == "first"
                                                                                  else [])),
                                   "differ": list(draw_differ or []), "missing": []}
                           for label in ("first", "last")},
                  "accuracy_diagonal": {label: dict(diag[label]) for label in diag},
                  "accuracy_last": {label: dict(LAST[label]) for label in LAST}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e495.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("LB1", "LB2", "LB3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # LB1: another config field differing, the flag not moved, a draw field beyond the one it adds, and a thin run
    assert _judge(differ=["iters"])["LB1"].startswith("FALSIFIER")
    assert _judge(added=[])["LB1"].startswith("FALSIFIER")
    assert _judge(added=["label_first", "episode_len"])["LB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["cue_sha1"])["LB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["LB1"].startswith("FALSIFIER")

    # LB2: a label-first read that carries no more of the label, and a share that is not positive
    assert _judge(share={"last": SHARE["last"], "first": (0.1000, 4.1000, 0.0244, 32)})["LB2"].startswith("FALSIFIER")
    assert _judge(share={"last": (0.0, 4.2687, 0.0, 32), "first": (0.0, 4.1000, 0.0, 32)})["LB2"].startswith("FALSIFIER")

    # LB3: a recovery on one arm, a recovery that does not resolve, and an arm still at chance
    assert _judge(move={"naive": (+0.3896, +7.80), "ewc-block": (+0.0010, +0.30),
                        "replay": (+0.0005, +0.20)})["LB3"].startswith("FALSIFIER")
    assert _judge(move={"naive": (+0.3896, +1.20), "ewc-block": (+0.3856, +0.90),
                        "replay": (+0.3669, +1.10)})["LB3"].startswith("FALSIFIER")
    assert _judge(diag={"first": {"naive": 0.7000, "ewc-block": 0.2600, "replay": 0.6700},
                        "last": DIAG["last"]})["LB3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e495.judge(_doc(ok=False)))


def test_the_runs_the_flag_and_the_bars_are_registered():
    assert e495.FIRST.name == "e495_earned_label_episode2_labelfirst_20reps.json"
    assert e495.LAST.name == "e493_earned_label_episode2_modelread_20reps.json"
    assert e495.RUNNER.name == "e8_rate_network.py"
    assert set(e495.MOVED) == {"loop_label_first"}, e495.MOVED
    assert e495.ADDED == ("label_first",), e495.ADDED
    assert set(e495.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e495.EPISODE, e495.TAU, e495.SYMBOLS) == (2, 12, 4), (e495.EPISODE, e495.TAU, e495.SYMBOLS)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e495.MIN_REPS, e495.SIGMA, e495.CHANCE, e495.BAR) == (20, 2.0, 0.25, 0.10)
    assert e495._inert("loop_label_first", None, True) and e495._inert("label_first", None, True)
    assert not e495._inert("iters", 500, 100)
    assert e495.DEFAULTS.get("loop_label_first") is False, e495.DEFAULTS.get("loop_label_first")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e495_the_label_first.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e495.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs and the replicate count are structural
    assert sorted(d["runs"]) == ["first", "last"], sorted(d["runs"])
    assert sorted(d["recovery"]) == sorted(ARMS), sorted(d["recovery"])
    assert sorted(d["share"]) == ["first", "last"], sorted(d["share"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    for name in d["share"]:
        #: one width and one world: the model's own thirty-two columns in both placements
        assert d["share"][name]["width"] == 32, (name, d["share"][name])
        #: the cues are deterministic in the instrument, so the within-symbol spread is only the float's floor
        assert d["share"][name]["within"] <= 1e-3 * d["share"][name]["across"], (name, d["share"][name])
        assert d["share"][name]["across"] > 0.0, (name, d["share"][name])
    for a in ARMS:
        assert d["recovery"][a]["n"] == 20, (a, d["recovery"][a])
        for label in ("first", "last"):
            assert 0.0 <= d["spans"]["accuracy_diagonal"][label][a] <= 1.0, (a, label)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
