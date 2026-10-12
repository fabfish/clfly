"""`e497` puts a second distractor in the label-first pass, so the tests pin both faces of the three claims, the one
field the draw moves, the label's share inside the factor, and the refusal when a run is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e497_the_label_first_at_three_trials as e497

ARMS = e497.ARMS
#: the reading's shape: the split moved, the share inside the factor, and the pass still learned
DIAG = {"three": {"naive": 0.8100, "ewc-block": 0.8000, "replay": 0.8050},
        "two": {"naive": 0.8299, "ewc-block": 0.8139, "replay": 0.8267}}
LAST = {"three": {a: 0.5600 for a in ARMS}, "two": {a: 0.5900 for a in ARMS}}
MOVE = {"naive": (-0.0199, -1.20), "ewc-block": (-0.0139, -0.90), "replay": (-0.0217, -1.30)}
#: the instrument: one width, one read, one placement, two splits
SHARE = {"two": (4.2967, 4.0724, 1.0551, 32), "three": (3.6000, 4.1000, 0.8780, 32)}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(differ=None, draw_differ=None, draw_moved=None, share=None, move=None, diag=None, replicates=(20,), ok=True,
         reason="a run is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "share": {}, "recovery": {}, "spans": {}}
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    move = dict(move or MOVE)
    share = dict(share or SHARE)
    return {
        "ok": True, "reason": None, "runs": {"three": {"artifact": "t"}, "two": {"artifact": "w"}},
        "share": {name: {"trials": 3 if name == "three" else 2, "across": v[0], "within": 1e-8, "scale": v[1],
                         "share": v[2], "width": v[3]} for name, v in share.items()},
        "recovery": {a: _paired(move[a][0], move[a][1]) for a in ARMS},
        "spans": {"arms": list(ARMS), "runs": ["three", "two"], "chance": e497.CHANCE, "factor": e497.FACTOR,
                  "replicates": list(replicates),
                  "config": {label: {"same": 55, "inert": ["loop_earn"], "differ": {k: [None, 1] for k in (differ or [])},
                                     "moved": {"loop_episode": 3 if label == "three" else 2}}
                             for label in ("three", "two")},
                  "draw": {label: {"fields": 25, "differ": list(draw_differ or []),
                                   "moved": dict(draw_moved or {"episode_len": [2, 3]})}
                           for label in ("three", "two")},
                  "accuracy_diagonal": {label: dict(diag[label]) for label in diag},
                  "accuracy_last": {label: dict(LAST[label]) for label in LAST}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e497.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    j = _judge()
    for cid in ("NB1", "NB2", "NB3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # NB1: another config field differing, a draw field differing past episode_len, the split not moved, a thin run
    assert _judge(differ=["iters"])["NB1"].startswith("FALSIFIER")
    assert _judge(draw_differ=["boundary_sha1"])["NB1"].startswith("FALSIFIER")
    assert _judge(draw_moved={"episode_len": [2, 2]})["NB1"].startswith("FALSIFIER")
    assert _judge(replicates=(19,))["NB1"].startswith("FALSIFIER")

    # NB2: a share that collapses under the second cue, one that is not positive, and one above the factor
    assert _judge(share={"two": SHARE["two"], "three": (1.0000, 4.1000, 0.2439, 32)})["NB2"].startswith("FALSIFIER")
    assert _judge(share={"two": (0.0, 4.0724, 0.0, 32), "three": (0.0, 4.1000, 0.0, 32)})["NB2"].startswith("FALSIFIER")
    assert _judge(share={"two": SHARE["two"], "three": (9.0000, 4.1000, 2.1951, 32)})["NB2"].startswith("FALSIFIER")

    # NB3: two arms short of the two-trial run by more than the bar, and an arm within 0.05 of chance
    assert _judge(diag={"three": {"naive": 0.4000, "ewc-block": 0.7000, "replay": 0.8050},
                        "two": DIAG["two"]})["NB3"].startswith("FALSIFIER")
    assert _judge(diag={"three": {"naive": 0.8100, "ewc-block": 0.2600, "replay": 0.8050},
                        "two": DIAG["two"]})["NB3"].startswith("FALSIFIER")

    #: a run that is absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e497.judge(_doc(ok=False)))


def test_the_runs_the_split_and_the_bars_are_registered():
    assert e497.THREE.name == "e497_earned_label_episode3_labelfirst_20reps.json"
    assert e497.TWO.name == "e495_earned_label_episode2_labelfirst_20reps.json"
    assert e497.RUNNER.name == "e8_rate_network.py"
    assert set(e497.MOVED) == {"loop_episode"}, e497.MOVED
    assert e497.DRAW_MOVED == ("episode_len",), e497.DRAW_MOVED
    assert set(e497.BOOKKEEPING) == {"json_out", "save_theta"}
    assert (e497.TAU, e497.SYMBOLS) == (12, 4), (e497.TAU, e497.SYMBOLS)
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e497.MIN_REPS, e497.SIGMA, e497.CHANCE, e497.BAR, e497.FACTOR) == (20, 2.0, 0.25, 0.10, 2.0)
    assert e497._inert("loop_episode", 2, 3) and e497._inert("episode_len", 2, 3)
    assert not e497._inert("iters", 500, 100)
    assert e497.DEFAULTS.get("loop_episode") == 1, e497.DEFAULTS.get("loop_episode")


def test_the_live_reading_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e497_the_label_first_at_three_trials.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e497.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the two runs, the two splits and the replicate count are structural
    assert sorted(d["runs"]) == ["three", "two"], sorted(d["runs"])
    assert sorted(d["recovery"]) == sorted(ARMS), sorted(d["recovery"])
    assert sorted(d["share"]) == ["three", "two"], sorted(d["share"])
    assert d["spans"]["replicates"] == [20], d["spans"]["replicates"]
    for name in d["share"]:
        #: one width and one read: the model's own thirty-two columns at both splits
        assert d["share"][name]["width"] == 32, (name, d["share"][name])
        #: the cues are deterministic in the instrument, so the within-symbol spread is only the float's floor
        assert d["share"][name]["within"] <= 1e-3 * d["share"][name]["across"], (name, d["share"][name])
        assert d["share"][name]["across"] > 0.0, (name, d["share"][name])
    assert d["share"]["three"]["trials"] == 3 and d["share"]["two"]["trials"] == 2, d["share"]
    for a in ARMS:
        assert d["recovery"][a]["n"] == 20, (a, d["recovery"][a])
        for label in ("three", "two"):
            assert 0.0 <= d["spans"]["accuracy_diagonal"][label][a] <= 1.0, (a, label)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
