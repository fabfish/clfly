"""`e321` asks whether the line's strongest method contrast survives the order inversion, so the tests pin the
direction convention, the per-contrast pairing, the magnitude ratio, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e321_the_replay_contrast_survives_the_order as e321


def test_the_direction_convention_is_per_metric():
    """A delta is `replay` minus the penalty arm, so replay is ahead on a higher accuracy and a lower forgetting."""
    up = e321.paired([0.9, 0.9], [0.8, 0.8], higher_is_better=True)
    assert up["favours_replay"] is True and up["sigma"] == float("inf"), up
    down = e321.paired([0.1, 0.1], [0.2, 0.2], higher_is_better=False)
    assert down["favours_replay"] is True, down
    # the same numbers read the wrong way round on the accuracy metric are not a win for replay
    assert e321.paired([0.8, 0.8], [0.9, 0.9], higher_is_better=True)["favours_replay"] is False
    assert e321.paired([1.0], [0.5], higher_is_better=True)["delta"] is None


def _run(names, order="as-built", circuit="MB", sha="abc", gap=0.1, reps=5):
    payload = {"tasks": [{"name": n} for n in names], "circuit": circuit,
               "config": {"task_order": order}, "readout": {"subset_sha1": sha}, "methods": {}}
    for arm, bonus in ((e321.REPLAY, gap), ("ewc", 0.0), ("ewc-block", 0.0), ("ewc-block-rand", 0.0)):
        payload["methods"][arm] = {"replicates": [
            {"final_accuracy": 0.8 + bonus + 0.01 * i, "mean_forgetting": 0.10 - bonus * 0.5 + 0.002 * i,
             "seed": 100 * i} for i in range(reps)]}
    return payload


def test_the_reading_pairs_each_contrast_in_both_orders(tmp_path):
    names = ("odour_identity", "heading", "odour_input")
    fwd = tmp_path / "f.json"
    bwd = tmp_path / "b.json"
    fwd.write_text(json.dumps(_run(names, gap=0.1)), encoding="utf-8")
    bwd.write_text(json.dumps(_run(names[::-1], order="reverse", gap=0.05)), encoding="utf-8")
    r = e321.reading(fwd, bwd)
    assert r["runs"] == 2 and r["same_circuit"] and r["reversed_names"] and r["same_seeds"], r
    assert len(r["contrasts"]) == 6, sorted(r["contrasts"])
    key = f"{e321.REPLAY}-ewc/final_accuracy"
    assert abs(r["contrasts"][key]["forward"]["delta"] - 0.1) < 1e-9, r["contrasts"][key]
    assert abs(r["contrasts"][key]["ratio"] - 2.0) < 1e-9, r["contrasts"][key]
    # and a missing run refuses rather than reading one
    bwd.unlink()
    assert e321.reading(fwd, bwd)["runs"] == 0, e321.reading(fwd, bwd)


def _reading(forward_ratio=1.0, backward_ratio=1.0, forward_sigma=4.0, backward_sigma=3.0,
             forward_favours=True, backward_favours=True, reversed_names=True, same_seeds=True):
    contrasts = {}
    for other in e321.PENALTIES:
        for metric in ("final_accuracy", "mean_forgetting"):
            contrasts[f"{e321.REPLAY}-{other}/{metric}"] = {
                "forward": {"n": 5, "delta": 0.1 * forward_ratio, "sigma": forward_sigma,
                            "favours_replay": forward_favours},
                "backward": {"n": 5, "delta": 0.1 * backward_ratio, "sigma": backward_sigma,
                             "favours_replay": backward_favours},
                "ratio": forward_ratio / backward_ratio if backward_ratio else None}
    return {"runs": 2, "circuits": ["MB", "MB"], "same_circuit": True, "readout": ["abc", "abc"],
            "orders": ["as-built", "reverse"], "reversed_names": reversed_names, "same_seeds": same_seeds,
            "n": 5, "contrasts": contrasts}


def test_the_four_claims_read_both_faces():
    # the default fixture has the two orders' magnitudes within a factor of two, so T4 fires there and the
    # MET case is the one with a step
    j = {r["id"]: r for r in e321.judge(_reading(forward_ratio=3.0))}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a differing circuit, read-out or task list is T1's
    bad = _reading()
    bad["same_circuit"] = False
    assert e321.judge(bad)[0]["verdict"].startswith("FALSIFIER FIRED")
    assert e321.judge(_reading(reversed_names=False))[0]["verdict"].startswith("FALSIFIER FIRED")
    # a contrast that does not favour replay in one order is T2's or T3's
    assert e321.judge(_reading(backward_favours=False))[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e321.judge(_reading(backward_favours=False))[2]["verdict"].startswith("FALSIFIER FIRED")
    # one that is unresolved in one order is T2's too
    assert e321.judge(_reading(backward_sigma=1.0))[1]["verdict"].startswith("FALSIFIER FIRED")
    # every contrast within a factor of two is T4's falsifier, and one at three is not
    assert e321.judge(_reading(forward_ratio=1.5, backward_ratio=1.0))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e321.judge(_reading(forward_ratio=3.0))[3]["verdict"].startswith("MET")
    assert e321.judge({"runs": 0})[0]["verdict"].startswith("REFUSED")


def test_the_live_two_runs_are_what_the_finding_says():
    r = e321.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["same_circuit"] and r["reversed_names"] and r["same_seeds"], r
    assert r["orders"] == ["as-built", "reverse"], r["orders"]
    assert r["n"] >= 5 and len(r["contrasts"]) == 6, (r["n"], len(r["contrasts"]))
    for k, v in r["contrasts"].items():
        # every contrast favours replay in both orders, and the size is what moves
        assert v["forward"]["favours_replay"] is True and v["backward"]["favours_replay"] is True, (k, v)
        assert min(v["forward"]["sigma"], v["backward"]["sigma"]) >= e321.SIGMA, (k, v)
    claims = {x["id"]: x["verdict"] for x in e321.judge(r)}
    for cid in ("T1", "T2", "T3", "T4"):
        assert claims[cid].startswith("MET"), claims[cid]
    # the magnitudes: `ewc-block`'s two contrasts move by about three, the other four by about one
    moved = {k: v["ratio"] for k, v in r["contrasts"].items() if v["ratio"] and v["ratio"] >= e321.FACTOR}
    assert {k.split("/")[0] for k in moved} == {f"{e321.REPLAY}-ewc-block"}, moved


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e321_the_replay_contrast_survives_the_order.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["runs"] == 2 and len(d["contrasts"]) == 6, d
    claims = {x["id"]: x["verdict"] for x in d["claims"]}
    for cid in ("T1", "T2", "T3", "T4"):
        assert claims[cid].startswith("MET"), claims[cid]
