"""`e458` reads the neuron read-out at eight columns, so the tests pin both faces of the five claims and the refusal when
a roll is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e458_the_neuron_readout_at_eight_columns as e458

#: the shape of the three rolls: fixed true values, so a mutation under test moves one of them
ANCHOR = (0.0090, 0.70, -0.0180, 1.10)
BUFFER = {"first": 0.2400, "last": -0.0450, "over_anchor": 0.1200, "over_anchor_sigma": 8.00}
NEW_READOUT = 8
WIDE_READOUT = 32


def _doc(anchor=ANCHOR, buffer=None, new_readout=NEW_READOUT, from_world=False, same_differ=None, reps=20,
         arms=e458.ARMS, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "runs": {}, "same": {}, "readouts": {}, "contrasts": {}, "spans": {}}
    b = dict(BUFFER if buffer is None else buffer)
    run_arms = {a: {"replicates": reps} for a in arms}
    same = {f"config.{k}": True for k in ("circuit_size", "iters", "lr", "lam", "loop_world_dims")}
    same.update({"circuit": True, "task_names": True})
    if same_differ:
        same[same_differ] = False

    def _roll(size, world):
        return {"arms": run_arms, "readouts": [size] * 3, "from_world": world, "readout_size": 32}
    return {"ok": True, "reason": None,
            "runs": {"new": _roll(new_readout, from_world), "card": _roll(NEW_READOUT, True),
                     "wide": _roll(WIDE_READOUT, False)},
            "same": same,
            "readouts": {"new": {"readouts": [new_readout] * 3, "from_world": from_world, "readout_size": 32},
                         "card": {"readouts": [NEW_READOUT] * 3, "from_world": True, "readout_size": 32},
                         "wide": {"readouts": [WIDE_READOUT] * 3, "from_world": False, "readout_size": 32}},
            "contrasts": {"new": {"anchor_diagonal": {"n": reps, "mean": anchor[0], "sd": 0.05, "se": 0.01,
                                                      "sigma": anchor[1]},
                                  "anchor_last": {"n": reps, "mean": anchor[2], "sd": 0.05, "se": 0.01,
                                                  "sigma": anchor[3]},
                                  "buffer_gain": [b["first"], 0.1800, b["last"]],
                                  "buffer_diagonal": {"n": reps, "mean": 0.1500, "sd": 0.05, "se": 0.01, "sigma": 9.0},
                                  "buffer_over_anchor": {"n": reps, "mean": b["over_anchor"], "sd": 0.05, "se": 0.01,
                                                         "sigma": b["over_anchor_sigma"]},
                                  "forgetting": {"naive": 0.30, "ewc-block": 0.26, "replay": 0.08}},
                          "card": {"anchor_diagonal": {"n": reps, "mean": -0.0302, "sd": 0.05, "se": 0.01,
                                                       "sigma": -1.77},
                                   "anchor_last": {"n": reps, "mean": -0.1177, "sd": 0.05, "se": 0.01, "sigma": -3.71},
                                   "buffer_gain": [0.2896, 0.2490, -0.0604],
                                   "buffer_diagonal": {"n": reps, "mean": 0.1594, "sd": 0.05, "se": 0.01,
                                                       "sigma": 11.97},
                                   "buffer_over_anchor": {"n": reps, "mean": 0.1896, "sd": 0.05, "se": 0.01,
                                                          "sigma": 10.89},
                                   "forgetting": {"naive": 0.375, "ewc-block": 0.3276, "replay": 0.0906}},
                          "wide": {"anchor_diagonal": {"n": reps, "mean": 0.0187, "sd": 0.05, "se": 0.01,
                                                       "sigma": 1.03},
                                   "anchor_last": {"n": reps, "mean": -0.0115, "sd": 0.05, "se": 0.01, "sigma": -0.78},
                                   "buffer_gain": [0.2323, 0.1812, -0.0302],
                                   "buffer_diagonal": {"n": reps, "mean": 0.1900, "sd": 0.05, "se": 0.01,
                                                       "sigma": 9.9},
                                   "buffer_over_anchor": {"n": reps, "mean": 0.1090, "sd": 0.05, "se": 0.01,
                                                          "sigma": 7.66},
                                   "forgetting": {"naive": 0.276, "ewc-block": 0.2354, "replay": 0.0635}}},
            "spans": {"replicates": [reps], "arms": {label: len(run_arms) for label in e458.RUNS},
                      "same_fields": len(same),
                      "readout": {"new": new_readout, "card": NEW_READOUT, "wide": WIDE_READOUT,
                                  "from_world": {"new": from_world, "card": True, "wide": False}},
                      "anchor": {"standing": anchor[0], "standing_sigma": anchor[1],
                                 "price": anchor[2], "price_sigma": anchor[3]},
                      "buffer": b,
                      "known": {"card_price": e458.CARD_PRICE, "card_price_sigma": e458.CARD_PRICE_SIGMA,
                                "wide_price": e458.WIDE_PRICE, "wide_price_sigma": e458.WIDE_PRICE_SIGMA}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e458.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the source moved at the card's own width, the price still unresolved
    j = _judge()
    for cid in ("DE1", "DE2", "DE3", "DE4", "DE5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DE1: a field differing, a read-out at the wide roll's width, one still read from the world, thin replicates
    # and a short arm list
    assert _judge(same_differ="config.iters")["DE1"].startswith("FALSIFIER")
    assert _judge(new_readout=WIDE_READOUT)["DE1"].startswith("FALSIFIER")
    assert _judge(from_world=True)["DE1"].startswith("FALSIFIER")
    assert _judge(reps=19)["DE1"].startswith("FALSIFIER")
    assert _judge(arms=("naive", "replay"))["DE1"].startswith("FALSIFIER")

    # DE2: a price that returns at eight neuron columns
    assert _judge(anchor=(0.0090, 0.70, -0.1177, 3.00))["DE2"].startswith("FALSIFIER")

    # DE3: a standing that resolves at eight neuron columns, in either direction
    assert _judge(anchor=(0.0300, 2.50, -0.0180, 1.10))["DE3"].startswith("FALSIFIER")
    assert _judge(anchor=(-0.0300, -2.50, -0.0180, 1.10))["DE3"].startswith("FALSIFIER")

    # DE4: a buffer with no first-position gain, one that is not cost at the last, and one between the bars
    assert _judge(buffer={**BUFFER, "first": 0.0000})["DE4"].startswith("FALSIFIER")
    assert _judge(buffer={**BUFFER, "last": 0.1000})["DE4"].startswith("FALSIFIER")
    assert _judge(buffer={**BUFFER, "first": 0.0200})["DE4"].startswith("NULL")

    # DE5: a buffer that is not ahead of the anchor, and one that does not resolve
    assert _judge(buffer={**BUFFER, "over_anchor": -0.0500})["DE5"].startswith("FALSIFIER")
    assert _judge(buffer={**BUFFER, "over_anchor": 0.0500, "over_anchor_sigma": 1.20})["DE5"].startswith("FALSIFIER")

    #: a roll absent or carrying no arm refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e458.judge(_doc(ok=False)))


def test_the_runs_and_the_widths_are_registered():
    #: the narrowed roll is this unit's, and the two beside it are the card's and `e455`'s
    assert e458.RUNS["new"].name == "e458_earned_label_neurons8_20reps.json"
    assert e458.RUNS["card"].name == "e438_earned_label_three_arms_20reps.json"
    assert e458.RUNS["wide"].name == "e455_earned_label_neurons_20reps.json"
    assert e458.ARMS == ("naive", "ewc-block", "replay")
    assert (e458.BASELINE, e458.ANCHOR, e458.BUFFER) == ("naive", "ewc-block", "replay")
    assert (e458.CARD_WIDTH, e458.WIDE_WIDTH) == (8, 32)
    assert set(e458.IGNORED) == {"json_out", "save_theta", "methods", "readout_from_world", "readout_size"}
    assert e458.N_TASKS == 3 and e458.N_ARMS == 3 and e458.MIN_REPS == 20
    assert (e458.FIRST_BAR, e458.FIRST_FLOOR) == (0.05, 0.0)
    assert (e458.LAST_BAR, e458.LAST_FIRES) == (0.0, 0.05)
    assert e458.SIGMA == 2.0
    assert (e458.CARD_PRICE, e458.CARD_PRICE_SIGMA) == (-0.1177, 3.71)
    assert (e458.WIDE_PRICE, e458.WIDE_PRICE_SIGMA) == (-0.0115, 0.78)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e458_the_neuron_readout_at_eight_columns.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e458.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: three arms at twenty replicates on three heads is structural
    assert sorted(d["runs"]) == ["card", "new", "wide"], sorted(d["runs"])
    arms = d["runs"]["new"]["arms"]
    assert sorted(arms) == ["ewc-block", "naive", "replay"], sorted(arms)
    for arm, got in arms.items():
        assert got["replicates"] >= e458.MIN_REPS, arm
        assert len(got["final"]) == e458.N_TASKS, arm
    assert d["spans"]["readout"]["new"] == e458.CARD_WIDTH, d["spans"]["readout"]
    assert d["spans"]["readout"]["wide"] == e458.WIDE_WIDTH, d["spans"]["readout"]
    assert d["spans"]["readout"]["from_world"] == {"new": False, "card": True, "wide": False}, d["spans"]["readout"]
    assert sorted(d["contrasts"]) == ["card", "new", "wide"], sorted(d["contrasts"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
