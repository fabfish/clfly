"""`e400` puts five near geometries against the four measured outcomes, so the tests pin both faces of the five
claims, the monotonicity test the claim's word asks for, and the live lead the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e400_five_candidates_for_the_one as e400


def _world(seed, d, gain, initial=0.6875):
    return {"cueseed": seed, "artifact": "r.json", "cue_to_action": d, "initial_task_0": initial,
            "body_task_0": initial + gain, "gain": gain}


#: the corpus's shape: one recovering world, four failures, and the path weight the only property out of range
GOOD_WORLDS = {"card": _world(None, 2, 0.0854), "cue3": _world(3, 2, -0.1635), "cue9": _world(9, 2, -0.2250),
               "cue14": _world(14, 2, -0.1479), "cue1": _world(1, 1, -0.1813)}


def _props(order, values=None, orders=None, inside=None):
    values = values if values is not None else {
        "fan_out": {"cue9": 171, "cue1": 174, "cue3": 206, "cue14": 150, "card": 184},
        "two_hop_frontier": {"cue9": 597, "cue1": 648, "cue3": 666, "cue14": 646, "card": 675},
        "action_overlap": {"cue9": 5, "cue1": 5, "cue3": 5, "cue14": 7, "card": 7},
        "cue_out_degree": {"cue9": 209, "cue1": 226, "cue3": 239, "cue14": 174, "card": 199},
        "path_weight": {"cue9": 28.8, "cue1": 42.2, "cue3": 48.8, "cue14": 42.8, "card": 77.3}}
    orders = orders if orders is not None else {p: False for p in e400.PROPERTIES}
    inside = inside if inside is not None else {"fan_out": True, "two_hop_frontier": False, "action_overlap": True,
                                                "cue_out_degree": True, "path_weight": False}
    return {p: {"values": values[p], "rank_correlation_with_the_gain": 0.0, "strictly_orders": orders[p],
                "card_inside_the_losers": inside[p]} for p in e400.PROPERTIES}


def _doc(worlds=None, properties=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when the corpus or a run is absent
        return {"ok": False, "worlds": {}, "properties": {}, "order": None, "reason": reason}
    worlds = worlds if worlds is not None else {k: v for k, v in GOOD_WORLDS.items()}
    order = sorted(worlds, key=lambda n: worlds[n]["gain"])
    return {"ok": True, "circuit": "mb+cx+al@n952", "edges": 20079, "worlds": worlds,
            "properties": properties if properties is not None else _props(order), "order": order}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e400.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the distance takes two values, no property is monotone, and the path weight is out of the losers' range
    j = _judge()
    for cid in ("X1", "X2", "X3", "X4"):
        assert j[cid].startswith("MET"), (cid, j[cid])
    assert j["X5"].startswith("FALSIFIER"), j["X5"]

    # X1: five distinct distances, which would make the question the distance's
    assert _judge(worlds={**GOOD_WORLDS, "cue3": _world(3, 3, -0.1635), "cue9": _world(9, 4, -0.2250),
                          "cue14": _world(14, 5, -0.1479)})["X1"].startswith("FALSIFIER")

    # X2: a property that is strictly monotone in the readings
    assert _judge(properties=_props(None, orders={**{p: False for p in e400.PROPERTIES}, "path_weight": True}))[
        "X2"].startswith("FALSIFIER")
    #: and a corpus too narrow for the bound
    narrow = {k: v for k, v in GOOD_WORLDS.items() if k in ("card", "cue3", "cue9", "cue14")}
    assert _judge(worlds=narrow)["X2"].startswith("FALSIFIER")

    # X3: every property constant across the worlds
    flat = {p: {n: 1 for n in GOOD_WORLDS} for p in e400.PROPERTIES}
    assert _judge(properties=_props(None, values=flat))["X3"].startswith("FALSIFIER")

    # X4: a failing world whose gain is inside the bar, and the card's world not gaining
    assert _judge(worlds={**GOOD_WORLDS, "cue14": _world(14, 2, -0.05)})["X4"].startswith("FALSIFIER")
    assert _judge(worlds={**GOOD_WORLDS, "card": _world(None, 2, -0.02)})["X4"].startswith("FALSIFIER")

    # X5: every property putting the card's world inside the losers' range
    assert _judge(properties=_props(None, inside={p: True for p in e400.PROPERTIES}))["X5"].startswith("MET")

    #: the corpus or a run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e400.judge(_doc(ok=False)))


def test_the_test_is_monotonicity_and_not_a_correlation():
    #: a property with a tie cannot order the worlds it ties, and `action_overlap` is the corpus's example
    assert e400.strictly_orders([1.0, 2.0, 3.0]), "increasing"
    assert e400.strictly_orders([3.0, 2.0, 1.0]), "decreasing"
    assert not e400.strictly_orders([5.0, 5.0, 5.0, 7.0, 7.0]), "the corpus's action overlap"
    assert not e400.strictly_orders([28.8, 42.2, 48.8, 42.8, 77.3]), "the corpus's path weight"
    #: and a rank correlation with ties is the tie-breaking's, which is why the claim's word is the test
    #: and it is **0.9999999999999998**, which is why the first version's `abs(rho) == 1.0` passed it by float
    #: error rather than by principle -- the claim's word is monotone and this is the test of it
    assert abs(e400._spearman([5.0, 5.0, 5.0, 7.0, 7.0], [0.0, 1.0, 2.0, 3.0, 4.0]) - 1.0) < 1e-12
    assert set(e400.PROPERTIES) == {"fan_out", "two_hop_frontier", "action_overlap", "cue_out_degree",
                                    "path_weight"}, e400.PROPERTIES


def test_the_live_lead_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e400_five_candidates_for_the_one.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e400.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e400.judge(d)}
    #: the control and the published readings are structural facts
    assert verdicts["X1"].startswith("MET") and verdicts["X4"].startswith("MET"), verdicts
    assert sorted(d["worlds"]) == ["card", "cue1", "cue14", "cue3", "cue9"], sorted(d["worlds"])
    assert sorted(d["properties"]) == sorted(e400.PROPERTIES), sorted(d["properties"])
    #: the order the properties are read in is the readings' order, worst first
    assert d["order"][0] == "cue9" and d["order"][-1] == "card", d["order"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
