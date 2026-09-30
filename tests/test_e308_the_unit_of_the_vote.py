"""`e308` asks whether the two units' arm orderings differ by population or by weighting, so the tests pin the pair
keying both readings share, the inversion set, both faces of the three claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e308_the_unit_of_the_vote as e308


def test_both_readings_are_keyed_in_the_same_pair_order():
    """A key mismatch between the two readings would read as a disagreement on every pair, so it is pinned first."""
    a = e308.artifact_edges()
    v = e308.vote_edges()
    assert set(a) == set(v), (sorted(set(a) ^ set(v)))
    assert len(a) == 10, len(a)
    # and each row carries a winner, a count and the margin the winner had
    for k, row in v.items():
        assert row["winner"] in k.split(">"), (k, row)
        assert row["comparisons"] > 0 and row["winner"] is not None, (k, row)


def test_the_inversion_set_is_the_pairs_the_two_orders_place_differently():
    one = ["naive", "ewc", "ewc-block", "ewc-block-rand", "replay"]
    two = ["ewc", "naive", "ewc-block", "ewc-block-rand", "replay"]
    assert e308.order_difference(one, two) == {"naive>ewc"}, e308.order_difference(one, two)
    # two adjacent swaps are two inversions, and the keys come out in the declared pair order rather than the order
    # the two permutations happen to list them in
    three = ["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"]
    got = e308.order_difference(
        ["ewc", "replay", "ewc-block-rand", "ewc-block", "naive"], three)
    assert got == {"ewc>replay", "ewc-block>ewc-block-rand"}, got
    assert e308.order_difference(one, one) == set()


def _reading(arm=False, vote=False, population=(), weighting=(), orders=None):
    art = orders or ["ewc", "replay", "ewc-block-rand", "ewc-block", "naive"]
    vot = ["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"]
    return {"field": "mean_forgetting", "keep": 147, "n_pairs": 10,
            "moved_by_population": list(population), "moved_by_weighting": list(weighting),
            "order_artifact": art, "order_vote": vot, "edges_artifact": {}, "edges_vote": {}}


def test_the_three_claims_read_both_faces():
    live = _reading(weighting=("ewc>replay", "ewc-block>ewc-block-rand"))
    j = {r["id"]: r for r in e308.judge(live)}
    for cid in ("V1", "V2", "V3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # an edge that moves with the population is V1's
    assert e308.judge(_reading(population=("ewc>replay",),
                              weighting=("ewc>replay", "ewc-block>ewc-block-rand")))[0]["verdict"] \
        .startswith("FALSIFIER FIRED")
    # methods that agree everywhere are V2's, and so is a disagreement outside the pairs the orders differ in
    assert e308.judge(_reading())[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e308.judge(_reading(weighting=("naive>replay", "ewc>replay", "ewc-block>ewc-block-rand")))[1]["verdict"] \
        .startswith("FALSIFIER FIRED")
    # the same arm first under both is V3's
    same = ["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"]
    assert e308.judge(_reading(orders=same, weighting=("ewc>replay", "ewc-block>ewc-block-rand")))[2]["verdict"] \
        .startswith("FALSIFIER FIRED")
    assert e308.judge({"n_pairs": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_reading_is_what_the_finding_says():
    r = e308.reading()
    assert r["n_pairs"] == 10 and r["keep"] >= 147, (r["n_pairs"], r["keep"])
    # the population moved nothing at all, on the corpus's own field and by `e297`'s own method
    assert r["moved_by_population"] == [], r["moved_by_population"]
    # and the weighting moved exactly the two pairs the two orders place differently
    assert sorted(r["moved_by_weighting"]) == ["ewc-block>ewc-block-rand", "ewc>replay"], r["moved_by_weighting"]
    assert set(r["moved_by_weighting"]) == e308.order_difference(r["order_artifact"], r["order_vote"])
    assert r["order_artifact"] == ["ewc", "replay", "ewc-block-rand", "ewc-block", "naive"], r["order_artifact"]
    assert r["order_vote"] == ["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"], r["order_vote"]
    claims = {x["id"]: x["verdict"] for x in e308.judge(r)}
    for cid in ("V1", "V2", "V3"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e308_the_unit_of_the_vote.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["moved_by_population"] == [], d["moved_by_population"]
    assert sorted(d["moved_by_weighting"]) == ["ewc-block>ewc-block-rand", "ewc>replay"], d["moved_by_weighting"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("V1", "V2", "V3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
