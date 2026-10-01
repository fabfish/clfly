"""`e312` tests what `e306`'s third quantity is, so the tests pin the accuracy join, the direction each quantity is
read in, the ordering, both faces of the three claims, and the live reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e312_the_shortfall_is_the_accuracy as e312


def test_the_accuracy_is_joined_from_the_payload_and_not_recomputed(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps({"methods": {"naive": {"replicates": [
        {"final_accuracy": 0.8}, {"final_accuracy": 0.9}]}}}), encoding="utf-8")
    acc = e312.accuracies(tmp_path)
    assert acc == {("a.json", 0, "naive"): 0.8, ("a.json", 1, "naive"): 0.9}, acc
    # a replicate with no stored accuracy is not a row, rather than a row with a zero in it
    (tmp_path / "b.json").write_text(json.dumps({"methods": {"ewc": {"replicates": [{"losses": [1.0]}]}}}),
                                     encoding="utf-8")
    assert set(e312.accuracies(tmp_path)) == set(acc), e312.accuracies(tmp_path)


def test_the_majority_edge_is_read_in_each_quantity_own_direction():
    rows = []
    for i, (sf, ac) in enumerate(((0.1, 0.9), (0.2, 0.8), (0.3, 0.7))):
        rows.append({"artifact": "a.json", "replicate": i, "arm": "naive", "shortfall_mean": sf, "accuracy": ac})
        rows.append({"artifact": "a.json", "replicate": i, "arm": "ewc", "shortfall_mean": sf + 0.05,
                     "accuracy": ac - 0.05})
    # the lower shortfall wins, and the higher accuracy wins: the same arm either way
    sf = e312.majority(rows, "shortfall_mean", higher_is_better=False)
    ac = e312.majority(rows, "accuracy", higher_is_better=True)
    assert sf["naive>ewc"]["winner"] == ac["naive>ewc"]["winner"] == "naive", (sf, ac)
    # read the accuracy the wrong way and the winner flips, which is the whole of X2
    flipped = e312.majority(rows, "accuracy", higher_is_better=False)
    assert flipped["naive>ewc"]["winner"] == "ewc", flipped
    assert e312.order(sf)[0] == "naive" and e312.order(sf)[1] == "ewc", e312.order(sf)


def _reading(rows=5581, violations=0, missed=0, differing=(), linear=0,
             sf_order=None, ac_order=None, lost=None, e297f=None, e297a=None, drop_e297=False):
    sf_order = sf_order or ["replay", "naive", "ewc-block", "ewc-block-rand", "ewc"]
    ac_order = ac_order or list(sf_order)
    lost = lost or ["replay", "ewc", "ewc-block", "ewc-block-rand", "naive"]
    return {"rows": rows, "missed": missed, "identity_violations": violations,
            "shortfall_order": sf_order, "accuracy_order": ac_order, "lost_order": lost,
            "differing_pairs": list(differing), "n_pairs": 10, "linear_violations": linear,
            "e297_forgetting": [] if drop_e297 else (e297f or ["ewc", "replay", "ewc-block-rand",
                                                               "ewc-block", "naive"]),
            "e297_accuracy": [] if drop_e297 else (e297a or ["replay", "ewc-block-rand", "ewc-block",
                                                             "naive", "ewc"]),
            "worst_on_shortfall": sf_order[-1], "worst_on_accuracy": ac_order[-1],
            "second_on_forgetting": lost[1], "best_on_forgetting": lost[0]}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e312.judge(_reading())}
    for cid in ("X1", "X2", "X3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a row where the identity fails is X1's, and one where the edges differ is X2's
    assert e312.judge(_reading(violations=1))[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e312.judge(_reading(differing=("naive>ewc",)))[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e312.judge(_reading(linear=1))[1]["verdict"].startswith("FALSIFIER FIRED")
    # a different arm at either end of the two sentences is X3's, and so is a missing e297 reading
    assert e312.judge(_reading(sf_order=["replay", "naive", "ewc-block", "ewc", "ewc-block-rand"]))[2][
        "verdict"].startswith("FALSIFIER FIRED")
    assert e312.judge(_reading(e297f=["replay", "ewc", "ewc-block-rand", "ewc-block", "naive"]))[2][
        "verdict"].startswith("FALSIFIER FIRED")
    assert e312.judge(_reading(e297a=["replay", "ewc-block", "ewc-block", "ewc", "naive"]))[2][
        "verdict"].startswith("FALSIFIER FIRED")
    assert e312.judge(_reading(drop_e297=True))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e312.judge({"rows": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_reading_is_what_the_finding_says():
    r = e312.reading()
    assert r["rows"] >= 5000 and r["missed"] == 0, (r["rows"], r["missed"])
    assert r["identity_violations"] == 0 and r["linear_violations"] == 0, r
    assert r["differing_pairs"] == [], r["differing_pairs"]
    assert r["shortfall_order"] == r["accuracy_order"], (r["shortfall_order"], r["accuracy_order"])
    # and the ends are the ones e306 and e297 each named
    assert r["worst_on_shortfall"] == r["worst_on_accuracy"] == e312.A2_WORST_ON_ACCURACY, r
    assert r["e297_accuracy"][-1] == e312.A2_WORST_ON_ACCURACY, r["e297_accuracy"]
    claims = {x["id"]: x["verdict"] for x in e312.judge(r)}
    assert claims["X1"].startswith("MET") and claims["X2"].startswith("MET"), claims
    # X3 fired once the corpus grew: `e297` now puts `replay` first on forgetting, where it put `ewc`
    assert claims["X3"].startswith("FALSIFIER FIRED"), claims["X3"]
    assert r["e297_forgetting"][0] == "replay", r["e297_forgetting"]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e312_the_shortfall_is_the_accuracy.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["identity_violations"] == 0 and d["differing_pairs"] == [], d
    assert d["shortfall_order"] == d["accuracy_order"], d
    claims = {x["id"]: x for x in d["claims"]}
    assert claims["X1"]["verdict"].startswith("MET"), claims["X1"]
    assert claims["X2"]["verdict"].startswith("MET"), claims["X2"]
    assert claims["X3"]["verdict"].startswith("FALSIFIER FIRED"), claims["X3"]
