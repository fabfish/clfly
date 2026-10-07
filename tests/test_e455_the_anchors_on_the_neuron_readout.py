"""`e455` reads the anchors on the neuron read-out, so the tests pin both faces of the five claims and the refusal when a
roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e455_the_anchors_on_the_neuron_readout as e455

#: the shape of the two rolls: fixed true values, so a mutation under test moves one of them
ANCHOR_DIAGONAL = (0.0100, 0.90)
ANCHOR_LAST = (-0.0600, 1.60)
BUFFER_OVER_ANCHOR = (0.1500, 8.00)
BUFFER_FIRST = 0.2200
NEW_READOUT = 32
CARD_READOUT = 8


def _doc(anchor_diagonal=ANCHOR_DIAGONAL, anchor_last=ANCHOR_LAST, over_anchor=BUFFER_OVER_ANCHOR,
         first=BUFFER_FIRST, new_readout=NEW_READOUT, from_world=False, same_differ=None, reps=20, arms=e455.ARMS,
         ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "readouts": {}, "contrasts": {}, "spans": {}}
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "loop_world_dims")}
    same.update({"circuit": True, "task_names": True})
    if same_differ:
        same[same_differ] = False
    return {"ok": True, "reason": None,
            "runs": {"new": {"arms": run_arms, "readouts": [new_readout] * 3, "readout_from_world": from_world},
                     "card": {"arms": run_arms, "readouts": [CARD_READOUT] * 3, "readout_from_world": True}},
            "same": same,
            "readouts": {"new": {"readouts": [new_readout] * 3, "from_world": from_world},
                         "card": {"readouts": [CARD_READOUT] * 3, "from_world": True}},
            "contrasts": {"new": {"anchor_diagonal": {"n": reps, "mean": anchor_diagonal[0], "sd": 0.05, "se": 0.01,
                                                      "sigma": anchor_diagonal[1]},
                                  "anchor_last": {"n": reps, "mean": anchor_last[0], "sd": 0.05, "se": 0.01,
                                                  "sigma": anchor_last[1]},
                                  "buffer_diagonal": {"n": reps, "mean": 0.2000, "sd": 0.05, "se": 0.01, "sigma": 9.0},
                                  "buffer_over_anchor": {"n": reps, "mean": over_anchor[0], "sd": 0.05, "se": 0.01,
                                                         "sigma": over_anchor[1]},
                                  "buffer_gain": [first, 0.1800, -0.0400],
                                  "forgetting": {"naive": 0.36, "ewc-block": 0.32, "replay": 0.10}},
                          "card": {"anchor_diagonal": {"n": reps, "mean": -0.0302, "sd": 0.05, "se": 0.01, "sigma": -1.77},
                                   "anchor_last": {"n": reps, "mean": -0.1177, "sd": 0.05, "se": 0.01, "sigma": -3.71},
                                   "buffer_diagonal": {"n": reps, "mean": 0.1594, "sd": 0.05, "se": 0.01, "sigma": 11.97},
                                   "buffer_over_anchor": {"n": reps, "mean": 0.1896, "sd": 0.05, "se": 0.01,
                                                          "sigma": 10.89},
                                   "buffer_gain": [0.2896, 0.2490, -0.0604],
                                   "forgetting": {"naive": 0.375, "ewc-block": 0.3276, "replay": 0.0906}}},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e455.RUNS},
                      "same_fields": len(same),
                      "readout": {"new": new_readout, "card": CARD_READOUT,
                                  "from_world": {"new": from_world, "card": True}},
                      "anchor": {"diagonal": anchor_diagonal[0], "sigma": anchor_diagonal[1],
                                 "last": anchor_last[0], "last_sigma": anchor_last[1],
                                 "card_diagonal": -0.0302, "card_sigma": -1.77, "card_last": -0.1177},
                      "buffer": {"over_anchor": over_anchor[0], "over_anchor_sigma": over_anchor[1],
                                 "first": first, "first_sigma": 9.0},
                      "known": {"card_first": e455.CARD_FIRST, "card_price": e455.CARD_PRICE,
                                "card_price_sigma": e455.CARD_PRICE_SIGMA}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e455.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the read-out moved to the neurons, and the anchor absent under both heads
    j = _judge()
    for cid in ("DB1", "DB2", "DB3", "DB4", "DB5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DB1: a field differing, a read-out that did not move, one still read from the world, thin replicates
    # and a short arm list
    assert _judge(same_differ="config.iters")["DB1"].startswith("FALSIFIER")
    assert _judge(new_readout=CARD_READOUT)["DB1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["DB1"].startswith("FALSIFIER")
    assert _judge(reps=19)["DB1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["DB1"].startswith("FALSIFIER")

    # DB2: a standing that resolves on the neuron read-out, in either direction
    assert _judge(anchor_diagonal=(0.0200, 2.50))["DB2"].startswith("FALSIFIER")
    assert _judge(anchor_diagonal=(-0.0200, -2.50))["DB2"].startswith("FALSIFIER")

    # DB3: a buffer that is not ahead of the anchor, and one that does not resolve
    assert _judge(over_anchor=(-0.0500, -3.00))["DB3"].startswith("FALSIFIER")
    assert _judge(over_anchor=(0.0500, 1.20))["DB3"].startswith("FALSIFIER")

    # DB4: a buffer with no first-position gain under the neuron read-out, and one between the bars
    assert _judge(first=0.0000)["DB4"].startswith("FALSIFIER")
    assert _judge(first=0.0200)["DB4"].startswith("NULL")

    # DB5: a price that resolves on the neuron read-out
    assert _judge(anchor_last=(-0.1000, -3.00))["DB5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e455.judge(_doc(ok=False)))


def test_the_runs_and_the_readouts_are_registered():
    #: the neuron read-out is this unit's run, and the earned label's roll is what it is read against
    assert e455.RUNS["new"].name == "e455_earned_label_neurons_20reps.json"
    assert e455.RUNS["card"].name == "e438_earned_label_three_arms_20reps.json"
    assert e455.ARMS == ("naive", "ewc-block", "replay")
    assert (e455.BASELINE, e455.ANCHOR, e455.BUFFER) == ("naive", "ewc-block", "replay")
    assert e455.READOUT_FIELD == "readout_from_world" and e455.READOUT_FIELD in e455.IGNORED
    assert (e455.CARD_READOUT, e455.NEURON_READOUT) == (8, 32)
    assert e455.N_TASKS == 3 and e455.N_ARMS == 3 and e455.MIN_REPS == 20
    assert (e455.FIRST_BAR, e455.FIRST_FLOOR) == (0.05, 0.0)
    assert e455.SIGMA == 2.0
    assert (e455.CARD_FIRST, e455.CARD_PRICE, e455.CARD_PRICE_SIGMA) == (0.2896, -0.1177, 3.71)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e455_the_anchors_on_the_neuron_readout.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e455.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates with the read-out moved is structural
    assert sorted(d["runs"]) == ["card", "new"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e455.MIN_REPS, arm
        assert len(got["final"]) == e455.N_TASKS, arm
    assert d["spans"]["readout"]["new"] == e455.NEURON_READOUT, d["spans"]["readout"]
    assert d["spans"]["readout"]["card"] == e455.CARD_READOUT, d["spans"]["readout"]
    assert d["spans"]["readout"]["from_world"] == {"new": False, "card": True}, d["spans"]["readout"]
    assert sorted(d["contrasts"]) == ["card", "new"], sorted(d["contrasts"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
