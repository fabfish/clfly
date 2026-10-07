"""`e453` reads the buffer over every anchor, so the tests pin both faces of the five claims and the refusal when a roll
is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e453_the_buffer_over_every_anchor as e453

#: the ten rolls: fixed true values, so a mutation under test moves one of them
CELLS = [
    ("biological", "as_built", "ewc-block", 0.1896, 10.89), ("biological", "rotated", "ewc-block", 0.1851, 10.03),
    ("biological", "env_redrawn", "ewc-block", 0.1559, 8.40), ("biological", "decoder_redrawn", "ewc-block", 0.1615, 8.27),
    ("biological", "reversed", "ewc-block", 0.1753, 8.38), ("biological", "wide_16", "ewc-block", 0.1250, 8.38),
    ("biological", "narrow_4", "ewc-block", 0.1483, 10.12),
    ("matched_random", "as_built", "ewc-block-rand", 0.1958, 15.33),
    ("matched_random", "reversed", "ewc-block-rand", 0.1861, 12.90),
    ("matched_random", "narrow_4", "ewc-block-rand", 0.1382, 9.70),
]


def _cell(family, roll, anchor, mean, sigma, reps=20):
    return {"family": family, "roll": roll, "artifact": f"{roll}.json", "anchor": anchor, "replicates": reps,
            "manipulation": {"task_order": "as-built", "loop_seed": None, "readout_seed": None,
                             "loop_world_dims": 8},
            "accuracy": {"n": reps, "mean": mean, "sd": 0.05, "se": 0.01, "sigma": sigma},
            "forgetting": {"n": reps, "mean": -0.23, "sd": 0.05, "se": 0.01, "sigma": -14.0},
            "buffer_gain": [mean, mean, mean]}


def _doc(cells=None, reps=20, drop_anchor_for=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rolls": {}, "cells": [], "spans": {}}
    spec = CELLS if cells is None else cells
    cs = [_cell(f, r, a, m, s, reps=reps) for f, r, a, m, s in spec]
    rolls = {}
    for c in cs:
        arms = {e453.BASELINE: {"replicates": c["replicates"]}, e453.BUFFER: {"replicates": c["replicates"]}}
        if c["anchor"] != drop_anchor_for:
            arms[c["anchor"]] = {"replicates": c["replicates"]}
        rolls[f"{c['family']}/{c['roll']}"] = {"artifact": c["artifact"], "anchor": c["anchor"], "arms": arms,
                                              "replicates": c["replicates"]}
    acc = [c["accuracy"]["mean"] for c in cs]
    sig = [abs(c["accuracy"]["sigma"]) for c in cs]
    return {"ok": True, "reason": None, "rolls": rolls, "cells": cs,
            "spans": {"cells": len(cs),
                      "biological": sum(1 for c in cs if c["family"] == "biological"),
                      "matched_random": sum(1 for c in cs if c["family"] == "matched_random"),
                      "replicates": sorted({c["replicates"] for c in cs}),
                      "accuracy": {f"{c['family']}/{c['roll']}": c["accuracy"]["mean"] for c in cs},
                      "sigma": {f"{c['family']}/{c['roll']}": c["accuracy"]["sigma"] for c in cs},
                      "accuracy_min": min(acc), "accuracy_max": max(acc), "span": max(acc) - min(acc),
                      "least_sigma": min(sig), "greatest_sigma": max(sig), "forgetting": {}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e453.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: ten rolls, the buffer ahead on every one, the span small
    j = _judge()
    for cid in ("CZ1", "CZ2", "CZ3", "CZ4", "CZ5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # CZ1: thin replicates and a roll whose anchor arm is not there
    assert _judge(reps=19)["CZ1"].startswith("FALSIFIER")
    assert _judge(drop_anchor_for="ewc-block")["CZ1"].startswith("FALSIFIER")

    # CZ2: a biological roll where the buffer is not ahead, and one that does not resolve
    odd = [c for c in CELLS]
    odd[0] = ("biological", "as_built", "ewc-block", -0.0200, -1.10)
    assert _judge(cells=odd)["CZ2"].startswith("FALSIFIER")
    odd = [c for c in CELLS]
    odd[0] = ("biological", "as_built", "ewc-block", 0.0010, 0.50)
    assert _judge(cells=odd)["CZ2"].startswith("FALSIFIER")

    # CZ3: a matched-random roll where the buffer is not ahead
    odd = [c for c in CELLS]
    odd[7] = ("matched_random", "as_built", "ewc-block-rand", -0.0500, -3.00)
    assert _judge(cells=odd)["CZ3"].startswith("FALSIFIER")

    # CZ4: a weakest instance under the floor, and one between the bars
    odd = [c for c in CELLS]
    odd[5] = ("biological", "wide_16", "ewc-block", 0.1250, 1.50)
    assert _judge(cells=odd)["CZ4"].startswith("FALSIFIER")
    odd = [c for c in CELLS]
    odd[5] = ("biological", "wide_16", "ewc-block", 0.1250, 3.00)
    assert _judge(cells=odd)["CZ4"].startswith("NULL")

    # CZ5: a span between the bars, and one past the falsifier
    odd = [c for c in CELLS]
    odd[0] = ("biological", "as_built", "ewc-block", 0.2600, 10.89)
    assert _judge(cells=odd)["CZ5"].startswith("NULL")
    odd = [c for c in CELLS]
    odd[0] = ("biological", "as_built", "ewc-block", 0.4000, 10.89)
    assert _judge(cells=odd)["CZ5"].startswith("FALSIFIER")

    #: a roll absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e453.judge(_doc(ok=False)))


def test_the_rolls_and_the_bars_are_registered():
    #: the seven biological rolls and the three matched-random ones, and the anchors each family carries
    assert {k: v.name for k, v in e453.BIO.items()} == {
        "as_built": "e438_earned_label_three_arms_20reps.json",
        "rotated": "e441_earned_label_anchor_order102_20reps.json",
        "env_redrawn": "e443_earned_label_worldseed1_20reps.json",
        "decoder_redrawn": "e444_earned_label_readoutseed1_20reps.json",
        "reversed": "e446_earned_label_anchor_reverse_20reps.json",
        "wide_16": "e448_earned_label_worlddims16_20reps.json",
        "narrow_4": "e449_earned_label_worlddims4_20reps.json"}
    assert {k: v.name for k, v in e453.RAND.items()} == {
        "as_built": "e439_earned_label_rand_20reps.json",
        "reversed": "e447_earned_label_rand_reverse_20reps.json",
        "narrow_4": "e451_earned_label_rand_worlddims4_20reps.json"}
    assert len(e453.BIO) + len(e453.RAND) == 10
    assert (e453.BASELINE, e453.BUFFER) == ("naive", "replay")
    assert (e453.BIO_ANCHOR, e453.RAND_ANCHOR) == ("ewc-block", "ewc-block-rand")
    assert set(e453.MANIPULATIONS) == {"task_order", "loop_seed", "readout_seed", "loop_world_dims"}
    assert e453.N_TASKS == 3 and e453.MIN_REPS == 20 and e453.SIGMA == 2.0
    assert (e453.LEAST_SIGMA, e453.LEAST_FLOOR) == (5.0, 2.0)
    assert (e453.SPAN, e453.SPAN_FIRES) == (0.10, 0.20)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e453_the_buffer_over_every_anchor.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e453.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: ten rolls, seven biological and three matched-random, twenty replicates each
    assert sorted(d["rolls"]) == sorted(f"{c['family']}/{c['roll']}" for c in d["cells"]), sorted(d["rolls"])
    assert len(d["cells"]) == 10, len(d["cells"])
    assert d["spans"]["biological"] + d["spans"]["matched_random"] == len(d["cells"])
    for c in d["cells"]:
        assert c["replicates"] >= e453.MIN_REPS, c["roll"]
        assert c["anchor"] in d["rolls"][f"{c['family']}/{c['roll']}"]["arms"], c["roll"]
    assert d["spans"]["replicates"] == [e453.MIN_REPS], d["spans"]["replicates"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
