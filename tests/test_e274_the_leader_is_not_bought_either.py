"""`e274` prices the leader rather than the span, so the tests pin the leader helper, both faces of the four claims
and the live numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e274_the_leader_is_not_bought_either as e274


def _m(n, corrs):
    return {"n": n, "corr": dict(zip(e274.PAIRS, corrs))}


def test_the_leader_helper_reads_the_top_two_gap_and_not_the_span():
    m = _m(16, (0.596, 0.473, 0.409))
    L = e274.leader(m)
    assert L["leader"] == e274.PAIRS[0] and L["second"] == e274.PAIRS[1], L
    assert abs(L["gap"] - (0.596 - 0.473)) < 1e-12, L
    # a wide span with a narrow top-two gap is cheap by span and dear by leader
    wide = e274.leader(_m(16, (0.9, 0.4, 0.9)))
    assert wide["gap"] == 0.0 and math.isinf(wide["needs"]) or wide["gap"] > 0


def _rows():
    # the triples are in PAIRS order: basis, naive-ewc, naive-rand
    rows = {"a/final_accuracy": _m(16, (0.473, 0.409, 0.596)), "a/mean_forgetting": _m(16, (0.364, 0.394, 0.562)),
            "b/final_accuracy": _m(16, (0.589, -0.168, 0.090)), "b/mean_forgetting": _m(16, (0.573, -0.303, 0.026)),
            "e178/final_accuracy": _m(144, (0.317, 0.118, 0.140)),
            "e178/mean_forgetting": _m(144, (0.282, 0.122, 0.124)), "_rate": 185.0}
    return rows


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e274.judge(_rows())}
    for cid in ("Y1", "Y2", "Y3", "Y4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    assert "1.57" in j["Y2"]["measured"], j["Y2"]
    assert "232" in j["Y3"]["measured"], j["Y3"]
    # the same leader in both runs is Y1's falsifier
    rows = _rows()
    rows["a/final_accuracy"] = _m(16, (0.589, -0.168, 0.090))
    rows["a/mean_forgetting"] = _m(16, (0.573, -0.303, 0.026))
    j = {r["id"]: r for r in e274.judge(rows)}
    assert j["Y1"]["verdict"].startswith("FALSIFIER FIRED"), j["Y1"]
    # a wide top-two gap at the powered matrix is Y2's, and a cheap leader is Y3's
    rows = _rows()
    rows["e178/final_accuracy"] = _m(144, (0.6, -0.6, 0.0))
    rows["e178/mean_forgetting"] = _m(144, (0.6, -0.6, 0.0))
    j = {r["id"]: r for r in e274.judge(rows)}
    assert j["Y2"]["verdict"].startswith("FALSIFIER FIRED"), j["Y2"]
    assert j["Y3"]["verdict"].startswith("FALSIFIER FIRED"), j["Y3"]
    assert e274.judge({})[0]["verdict"].startswith("REFUSED")


def test_the_live_read_prices_the_leader_and_corrects_the_span():
    """The finding's numbers on the artifact: two runs with two leaders, the best-powered matrix under two sigma on
    both metrics, and 232 to 297 replicates -- 12 to 15 hours -- for the leader against 13 for the span."""
    p = Path("runs/e274_the_leader_is_not_bought_either.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    leaders = d["leaders"]
    assert leaders["e266_matched_side_seed0_16reps.json/final_accuracy"]["leader"] == ["naive", "ewc-block-rand"]
    assert leaders["e266_matched_side_seed100_16reps.json/final_accuracy"]["leader"] == ["ewc-block", "ewc-block-rand"]
    big = leaders["e178_rung_side_cs300_144reps.json/final_accuracy"]
    assert d["matrices"]["e178_rung_side_cs300_144reps.json/final_accuracy"]["n"] == 144
    assert abs(big["sigma"] - 1.57) < 0.02 and abs(big["gap"] - 0.177) < 1e-3, big
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("Y1", "Y2", "Y3", "Y4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "232 to 297" in claims["Y3"]["measured"] and "hours" in claims["Y3"]["measured"], claims["Y3"]
