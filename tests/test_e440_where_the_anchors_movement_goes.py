"""`e440` reads the corpus's two parameters and its interference split on the card's world, so the tests pin both faces
of the five claims and the refusal when a roll is absent or short of the fields.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e440_where_the_anchors_movement_goes as e440

#: the shape of the four cells: fixed true values, so a mutation under test moves one of them
BASE_SHARE = [0.3776, 0.4873]


def _cell(roll, arm, anchor, drift_ratio, bias_ratio, share, reps=20):
    return {"roll": roll, "arm": arm, "anchor": anchor, "replicates": reps, "drift_ratio": drift_ratio,
            "bias_ratio": bias_ratio, "share": list(share), "base_share": list(BASE_SHARE),
            "share_above": [s > b for s, b in zip(share, BASE_SHARE)]}


def _doc(drift=None, bias=None, shares=None, reps=20, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rolls": {}, "cells": [], "by_arm": {}, "shares": {}, "spans": {}}
    drift = {"penalty.ewc-block": 0.6234, "rand.ewc-block-rand": 0.6188} if drift is None else drift
    bias = {"penalty.ewc-block": 1.4483, "rand.ewc-block-rand": 1.4622} if bias is None else bias
    shares = {"penalty.ewc-block": [0.8956, 0.9366], "rand.ewc-block-rand": [0.4900, 0.8705]} if shares is None \
        else shares
    cells = []
    for roll, anchor in e440.ANCHORS.items():
        key = f"{roll}.{anchor}"
        cells.append(_cell(roll, anchor, True, drift[key], bias[key], shares[key], reps=reps))
        cells.append(_cell(roll, e440.BUFFER, False, 0.9556, 0.8531, [0.3159, 0.4073], reps=reps))
    return {"ok": True, "reason": None, "rolls": {r: {} for r in e440.ROLLS}, "cells": cells,
            "by_arm": {}, "shares": {},
            "spans": {"cells": len(cells), "rolls": len(e440.ROLLS), "replicates": [reps],
                      "anchors": sorted(e440.ANCHORS.values()), "tasks": e440.SPLIT_TASKS}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e440.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the anchors hold the weights and push the bias, and their interference runs through the bias
    j = _judge()
    for cid in ("BR1", "BR2", "BR3", "BR4", "BR5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BR1: thin replicates and a cell count that is not two per roll
    assert _judge(reps=19)["BR1"].startswith("FALSIFIER")
    short = _doc()
    short["spans"]["cells"] = 3
    assert e440.judge(short)[0]["verdict"].startswith("FALSIFIER")

    # BR2: an anchor that does not hold the weights, and one between the bars
    assert _judge(drift={"penalty.ewc-block": 0.6234, "rand.ewc-block-rand": 0.9900})["BR2"].startswith("FALSIFIER")
    assert _judge(drift={"penalty.ewc-block": 0.6234, "rand.ewc-block-rand": 0.8500})["BR2"].startswith("NULL")

    # BR3: an anchor that does not push the bias, and one between the bars
    assert _judge(bias={"penalty.ewc-block": 1.4483, "rand.ewc-block-rand": 1.0500})["BR3"].startswith("FALSIFIER")
    assert _judge(bias={"penalty.ewc-block": 1.4483, "rand.ewc-block-rand": 1.2000})["BR3"].startswith("NULL")

    # BR4: an anchor whose bias share is at or below the baseline's on one task
    assert _judge(shares={"penalty.ewc-block": [0.8956, 0.9366],
                          "rand.ewc-block-rand": [0.3000, 0.8705]})["BR4"].startswith("FALSIFIER")

    # BR5: a buffer above the baseline on one task
    buffer_over = _doc()
    for c in buffer_over["cells"]:
        if not c["anchor"]:
            c["share"] = [0.3159, 0.5000]
            c["share_above"] = [s > b for s, b in zip(c["share"], BASE_SHARE)]
    assert e440.judge(buffer_over)[4]["verdict"].startswith("FALSIFIER")

    #: a roll absent or short of the fields refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e440.judge(_doc(ok=False)))


def test_the_rolls_and_the_thresholds_are_registered():
    #: the two rolls are the penalty's and the matched-random one, and the baseline and buffer are the corpus's
    assert str(e440.ROLLS["penalty"]).replace("\\", "/") == "runs/e438_earned_label_three_arms_20reps.json"
    assert str(e440.ROLLS["rand"]).replace("\\", "/") == "runs/e439_earned_label_rand_20reps.json"
    assert e440.BASELINE == "naive" and e440.BUFFER == "replay"
    assert e440.ANCHORS == {"penalty": "ewc-block", "rand": "ewc-block-rand"}
    assert e440.DRIFT == "theta_drift" and e440.BIAS == "bias_from_zero" and e440.SPLIT == "whole_body"
    assert e440.MIN_REPS == 20 and e440.SPLIT_TASKS == 2
    assert (e440.GEN, e440.GEN_FIRES) == (0.75, 0.95)
    assert (e440.PUSH, e440.PUSH_FLOOR) == (1.40, 1.10)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e440_where_the_anchors_movement_goes.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e440.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: two rolls, two arms each, twenty replicates and a two-entry split is structural
    assert sorted(d["rolls"]) == ["penalty", "rand"], sorted(d["rolls"])
    assert len(d["cells"]) == 2 * len(d["rolls"]), d["cells"]
    for c in d["cells"]:
        assert c["replicates"] >= e440.MIN_REPS, (c["roll"], c["arm"])
        assert len(c["share"]) == e440.SPLIT_TASKS, (c["roll"], c["arm"])
    assert sorted({c["arm"] for c in d["cells"]}) == ["ewc-block", "ewc-block-rand", "replay"], d["cells"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
