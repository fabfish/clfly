"""`e442` reads the two parameters under two orders, so the tests pin both faces of the five claims and the refusal when
a roll is absent or short of the fields.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e442_the_two_parameters_under_two_orders as e442

#: the shape of the four cells: fixed true values, so a mutation under test moves one of them
BASE_SHARE = [0.2752, 0.2083]
ANCHOR_SHARE = [0.9464, 0.8996]
BUFFER_SHARE = [0.5098, 0.4427]
DRIFT = {"asbuilt": {"ewc-block": 0.6234, "replay": 0.9556},
         "rotated": {"ewc-block": 0.6027, "replay": 0.9328}}
BIAS = {"asbuilt": {"ewc-block": 1.4483, "replay": 0.8531},
        "rotated": {"ewc-block": 1.3621, "replay": 0.8030}}


def _doc(drift=None, shares=None, buffer_drift=None, reps=20, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rolls": {}, "cells": [], "shares": {}, "spans": {}}
    drift = {r: dict(v) for r, v in DRIFT.items()} if drift is None else drift
    if buffer_drift is not None:
        for label in drift:
            drift[label]["replay"] = buffer_drift
    shares = {"base": list(BASE_SHARE), "ewc-block": list(ANCHOR_SHARE), "replay": list(BUFFER_SHARE)} \
        if shares is None else shares
    cells = []
    for label in e442.ROLLS:
        for arm in (e442.ANCHOR, e442.BUFFER):
            share = shares[arm] if label == "rotated" else list(ANCHOR_SHARE)
            base_share = shares["base"] if label == "rotated" else list(BASE_SHARE)
            cells.append({"roll": label, "arm": arm, "replicates": reps,
                          "drift_ratio": drift[label][arm], "bias_ratio": BIAS[label][arm],
                          "share": list(share), "base_share": list(base_share),
                          "share_above": [s > b for s, b in zip(share, base_share)],
                          "held": drift[label][arm] < 1.0, "pushed": BIAS[label][arm] > 1.0})
    return {"ok": True, "reason": None, "rolls": {label: {} for label in e442.ROLLS}, "cells": cells,
            "shares": {"rotated": {"base": list(shares["base"]), "ewc-block": list(shares["ewc-block"]),
                                   "replay": list(shares["replay"])}},
            "spans": {"rolls": sorted(e442.ROLLS), "cells": len(cells), "replicates": [reps],
                      "orders": {"asbuilt": "as-built", "rotated": "1,0,2"},
                      "anchor_drift": {"asbuilt": drift["asbuilt"]["ewc-block"],
                                       "rotated": drift["rotated"]["ewc-block"],
                                       "move": drift["rotated"]["ewc-block"] - drift["asbuilt"]["ewc-block"]},
                      "anchor_bias": {"asbuilt": BIAS["asbuilt"]["ewc-block"],
                                      "rotated": BIAS["rotated"]["ewc-block"],
                                      "move": BIAS["rotated"]["ewc-block"] - BIAS["asbuilt"]["ewc-block"]},
                      "buffer_drift": {"asbuilt": drift["asbuilt"]["replay"],
                                       "rotated": drift["rotated"]["replay"]},
                      "buffer_bias": {"asbuilt": BIAS["asbuilt"]["replay"], "rotated": BIAS["rotated"]["replay"]},
                      "tasks": e442.SPLIT_TASKS}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e442.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the ledger carried, the anchor holding the weights about as hard under both orders
    j = _judge()
    for cid in ("BT1", "BT2", "BT3", "BT4", "BT5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BT1: thin replicates and a cell count that is not two arms per roll
    assert _judge(reps=19)["BT1"].startswith("FALSIFIER")
    short = _doc()
    short["spans"]["cells"] = 3
    assert e442.judge(short)[0]["verdict"].startswith("FALSIFIER")

    # BT2: an anchor that does not hold the weights under the rotated order, and one between the bars
    assert _judge(drift={"asbuilt": {"ewc-block": 0.6234, "replay": 0.9556},
                         "rotated": {"ewc-block": 0.9900, "replay": 0.9328}})["BT2"].startswith("FALSIFIER")
    assert _judge(drift={"asbuilt": {"ewc-block": 0.6234, "replay": 0.9556},
                         "rotated": {"ewc-block": 0.8500, "replay": 0.9328}})["BT2"].startswith("NULL")

    # BT3: a buffer that moves the weights less than the anchor
    assert _judge(buffer_drift=0.5000)["BT3"].startswith("FALSIFIER")

    # BT4: a drift ratio that moves a long way between the orders, and one between the bars
    assert _judge(drift={"asbuilt": {"ewc-block": 0.6234, "replay": 0.9556},
                         "rotated": {"ewc-block": 0.9500, "replay": 0.9328}})["BT4"].startswith("FALSIFIER")
    assert _judge(drift={"asbuilt": {"ewc-block": 0.6234, "replay": 0.9556},
                         "rotated": {"ewc-block": 0.7500, "replay": 0.9328}})["BT4"].startswith("NULL")

    # BT5: an anchor whose bias share is at or below the baseline's on one task
    assert _judge(shares={"base": list(BASE_SHARE), "ewc-block": [0.2000, 0.8996],
                          "replay": list(BUFFER_SHARE)})["BT5"].startswith("FALSIFIER")

    #: a roll absent or short of the fields refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e442.judge(_doc(ok=False)))


def test_the_rolls_and_the_thresholds_are_registered():
    #: the two rolls are the anchor's as-built one and its rotated one
    assert e442.ROLLS["asbuilt"].name == "e438_earned_label_three_arms_20reps.json"
    assert e442.ROLLS["rotated"].name == "e441_earned_label_anchor_order102_20reps.json"
    assert (e442.BASELINE, e442.ANCHOR, e442.BUFFER) == ("naive", "ewc-block", "replay")
    assert e442.ARMS == ("naive", "ewc-block", "replay")
    assert e442.DRIFT == "theta_drift" and e442.SPLIT == "whole_body"
    assert e442.MIN_REPS == 20 and e442.SPLIT_TASKS == 2
    assert (e442.HOLD, e442.HOLD_FIRES) == (0.75, 0.95)
    assert (e442.MOVES, e442.MOVES_FIRES) == (0.10, 0.20)
    assert e442.AS_BUILT_DRIFT == 0.6234, "the as-built figure BT4 is registered against"


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e442_the_two_parameters_under_two_orders.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e442.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: two rolls, two arms each and twenty replicates is structural
    assert sorted(d["rolls"]) == ["asbuilt", "rotated"], sorted(d["rolls"])
    assert len(d["cells"]) == 2 * len(d["rolls"]), d["cells"]
    for c in d["cells"]:
        assert c["replicates"] >= e442.MIN_REPS, (c["roll"], c["arm"])
        assert len(c["share"]) == e442.SPLIT_TASKS, (c["roll"], c["arm"])
    assert sorted({c["arm"] for c in d["cells"]}) == ["ewc-block", "replay"], d["cells"]
    assert d["spans"]["orders"]["rotated"] != d["spans"]["orders"]["asbuilt"], d["spans"]["orders"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
