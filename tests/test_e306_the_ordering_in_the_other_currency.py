"""`e306` orders the five arms by the three quantities the retention matrices supply, so the tests pin the majority
edge and its margins, the cycle it must refuse, both faces of the four claims, and the live orderings.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e306_the_ordering_in_the_other_currency as e306


def _by(rows):
    """A stand-in for `pairs_by_replicate`: a list of {arm: {field: value}} dicts, keyed by index."""
    return {i: r for i, r in enumerate(rows)}


def test_the_majority_edge_counts_both_directions_and_keeps_the_margin():
    by = _by([
        {"naive": {"x": 0.1}, "ewc": {"x": 0.3}},     # lower is better, so naive wins
        {"naive": {"x": 0.1}, "ewc": {"x": 0.3}},
        {"naive": {"x": 0.5}, "ewc": {"x": 0.2}},     # ewc wins
    ])
    m = e306.majority(by, "x")
    assert m["n_edges"] == 1, m["edges"]
    e = m["edges"]["naive>ewc"]
    assert (e["winner"], e["loser"], e["n"], e["margin"], e["rate"]) == ("naive", "ewc", 3, 2, 2 / 3), e
    assert m["order"][0] == "naive", m["order"]
    # a tied pair and an absent one contribute no edge rather than a coin flip
    assert e306.majority(_by([{"naive": {"x": 1.0}, "ewc": {"x": 1.0}}]), "x")["n_edges"] == 0
    assert e306.majority(_by([{"naive": {"x": 1.0}}]), "x")["n_edges"] == 0
    # and a value the arm does not record is not a comparison
    assert e306.majority(_by([{"naive": {"x": 1.0}, "ewc": {}}]), "x")["n_edges"] == 0


def test_a_majority_cycle_is_found_rather_than_smoothed_into_an_order():
    by = _by([
        {"naive": {"x": 0.1}, "ewc": {"x": 0.2}, "ewc-block": {"x": 0.3}},   # naive > ewc > ewc-block
        {"naive": {"x": 0.3}, "ewc": {"x": 0.1}, "ewc-block": {"x": 0.2}},   # ewc > ewc-block > naive
        {"naive": {"x": 0.2}, "ewc": {"x": 0.3}, "ewc-block": {"x": 0.1}},   # ewc-block > naive > ewc
    ])
    m = e306.majority(by, "x")
    assert m["n_edges"] == 3, m["edges"]
    # a three-cycle is found once per starting point, so the count is three and the *set* is one loop
    assert len(m["cycles"]) == 3, m["cycles"]
    assert {frozenset(c) for c in m["cycles"]} == {frozenset(("naive", "ewc", "ewc-block"))}, m["cycles"]


def test_the_ranks_are_positions_and_not_values():
    assert e306.ranks(["a", "b", "c"]) == {"a": 0, "b": 1, "c": 2}
    assert e306.ranks(["c", "a", "b"]) == {"c": 0, "a": 1, "b": 2}


def _reading(lost=None, unlearned=None, shortfall=None, stored=None, rho=-0.4, agree=10):
    def field(order, edges=10, cycles=0):
        return {"order": order, "n_edges": edges, "cycles": [], "wins": {}, "edges": {}}
    lost = lost or list(e306.ARMS)
    return {"fields": {e306.LOST: field(lost), e306.UNLEARNED: field(unlearned or list(e306.ARMS)),
                       e306.SHORTFALL: field(shortfall or list(e306.ARMS)),
                       e306.STORED: field(stored or list(e306.ARMS))},
            "arm_replicates": 100, "n_pairs": 10, "stored_agrees_on": agree,
            "lost_order": lost, "unlearned_order": unlearned or list(e306.ARMS),
            "shortfall_order": shortfall or list(e306.ARMS), "lost_unlearned_rho": rho}


def test_the_four_claims_read_both_faces():
    # the default reading is the live shape: replay best, ewc second-best but worst on the shortfall
    live = _reading(lost=["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"],
                    shortfall=["replay", "naive", "ewc-block", "ewc-block-rand", "ewc"])
    j = {r["id"]: r for r in e306.judge(live)}
    for cid in ("R1", "R2", "R3", "R4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a cycle on one quantity is R1's, whether it is found once or once per starting point
    bad = _reading()
    bad["fields"][e306.LOST]["cycles"] = [["naive", "ewc", "ewc-block"]]
    assert e306.judge(bad)[0]["verdict"].startswith("FALSIFIER FIRED")
    bad = _reading()
    bad["fields"][e306.UNLEARNED]["n_edges"] = 9
    assert e306.judge(bad)[0]["verdict"].startswith("FALSIFIER FIRED")
    # the same arm worst on both is R2's
    same = _reading(lost=["a", "b", "c", "d", "e"], shortfall=["a", "b", "c", "d", "e"])
    assert e306.judge(same)[1]["verdict"].startswith("FALSIFIER FIRED")
    # a non-negative rank correlation is R3's
    assert e306.judge(_reading(rho=0.0))[2]["verdict"].startswith("FALSIFIER FIRED")
    # and a pair whose stored edge differs from the recomputed one is R4's
    assert e306.judge(_reading(agree=9))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e306.judge({})[0]["verdict"].startswith("REFUSED")


def test_the_live_orderings_are_what_the_finding_says():
    r = e306.reading()
    assert r["arm_replicates"] >= 3000, r["arm_replicates"]
    assert r["lost_order"] == r["fields"][e306.STORED]["order"], r["lost_order"]
    assert r["lost_order"] == ["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"], r["lost_order"]
    assert r["unlearned_order"] == ["naive", "replay", "ewc-block-rand", "ewc-block", "ewc"], r["unlearned_order"]
    assert r["shortfall_order"] == ["replay", "naive", "ewc-block", "ewc-block-rand", "ewc"], r["shortfall_order"]
    assert r["stored_agrees_on"] == r["n_pairs"] == 10, (r["stored_agrees_on"], r["n_pairs"])
    assert -0.5 < r["lost_unlearned_rho"] < 0, r["lost_unlearned_rho"]
    # the exhibit: `replay` beats `ewc` on the metric by a coin flip and on the shortfall decisively
    edges = r["fields"][e306.LOST]["edges"]
    assert edges["replay>ewc"]["rate"] < 0.6, edges["replay>ewc"]
    assert r["fields"][e306.SHORTFALL]["edges"]["replay>ewc"]["rate"] > 0.9, \
        r["fields"][e306.SHORTFALL]["edges"]["replay>ewc"]
    claims = {x["id"]: x["verdict"] for x in e306.judge(r)}
    for cid in ("R1", "R2", "R3", "R4"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e306_the_ordering_in_the_other_currency.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["lost_order"] == ["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"], d["lost_order"]
    assert d["shortfall_order"][-1] == "ewc" and d["shortfall_order"][1] == "naive", d["shortfall_order"]
    assert d["stored_agrees_on"] == 10 and d["lost_unlearned_rho"] < 0, d["lost_unlearned_rho"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("R1", "R2", "R3", "R4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
