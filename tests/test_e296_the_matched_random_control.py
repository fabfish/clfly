"""`e296` reads the biological partition against its matched random control, so the tests pin the sign convention, the
resolved-and-powered reading, both faces of the three claims, and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e296_the_matched_random_control as e296


def _art(path: Path, rows=5, acc_gap=0.01, fgt_gap=0.01):
    """A stand-in artifact where the biological block arm is better on accuracy and worse on forgetting."""
    payload = {"config": {"readout_size": 32, "basis": "cell_class"}, "methods": {}}
    for a in e296.A, e296.B:
        reps = []
        for r in range(rows):
            wobble = 1.0 + 0.2 * r
            block = a == e296.A
            reps.append({"final_accuracy": 0.80 + 0.01 * r + (acc_gap * wobble if block else 0.0),
                         "mean_forgetting": 0.10 + 0.01 * r + (fgt_gap * wobble if block else 0.0)})
        payload["methods"][a] = {"replicates": reps}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_sign_convention_against_the_control(tmp_path):
    p = tmp_path / "a.json"
    _art(p)
    d = e296.load(p)
    acc = e296.contrast(d, e296.A, e296.B, "final_accuracy")
    fgt = e296.contrast(d, e296.A, e296.B, "mean_forgetting")
    # delta is the biological arm minus the random one: it is better on accuracy when the delta is POSITIVE ...
    assert acc["delta"] > 0 and acc["ahead"] is True, acc
    # ... and worse on forgetting when the delta is positive, because lower forgetting is better
    assert fgt["delta"] > 0 and fgt["ahead"] is False, fgt
    assert acc["n"] == 5 and fgt["n"] == 5, (acc, fgt)
    # a constant difference has a sem of zero and is not a comparison
    _art(p, acc_gap=0.0, fgt_gap=0.0)
    assert e296.contrast(e296.load(p), e296.A, e296.B, "final_accuracy") is None
    # fewer than three replicates is not a comparison either
    _art(p, rows=2)
    assert e296.contrast(e296.load(p), e296.A, e296.B, "final_accuracy") is None


def test_the_counts_and_the_replicates_of_the_resolved_ones(tmp_path):
    small, big = tmp_path / "small.json", tmp_path / "big.json"
    _art(small, rows=5)
    _art(big, rows=40)
    rows = e296.comparisons(tmp_path)
    assert len(rows) == 4, rows
    s = e296.by_metric(rows)
    assert s["final_accuracy"]["comparisons"] == 2 and s["final_accuracy"]["ahead"] == 2, s["final_accuracy"]
    assert s["mean_forgetting"]["ahead"] == 0, s["mean_forgetting"]
    assert s["mean_forgetting"]["resolved"] == 2, s["mean_forgetting"]
    assert s["mean_forgetting"]["resolved_against_replicates"] == [5, 40], s["mean_forgetting"]


def _reading(acc=None, fgt=None, rows=None):
    base = {"comparisons": 40, "ahead": 25, "rate": 0.625, "resolved": 5, "resolved_ahead": 4,
            "resolved_ahead_replicates": [3, 3, 3, 16], "resolved_against_replicates": [5],
            "largest": 4.35, "largest_ahead": 3.88, "largest_against": 4.35}
    fbase = {"comparisons": 40, "ahead": 22, "rate": 0.55, "resolved": 7, "resolved_ahead": 4,
             "resolved_ahead_replicates": [3, 3, 3, 16], "resolved_against_replicates": [5, 40, 40],
             "largest": 2.97, "largest_ahead": 2.97, "largest_against": 2.19}
    return {"comparisons": rows if rows is not None else [
        {"artifact": "a.json", "metric": "mean_forgetting", "sigma": 2.19, "n": 40, "delta": -0.004,
         "ahead": False, "readout": 32, "overlap": 0.0, "basis": "cell_class"},
        {"artifact": "b.json", "metric": "mean_forgetting", "sigma": 2.97, "n": 3, "delta": 0.108,
         "ahead": True, "readout": None, "overlap": None, "basis": "cell_class"}],
        "by_metric": {"final_accuracy": dict(base, **(acc or {})),
                      "mean_forgetting": dict(fbase, **(fgt or {}))}}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e296.judge(_reading())}
    for cid in ("C1", "C2", "C3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # an accuracy metric the biological arm loses is C1's falsifier
    j = {r["id"]: r for r in e296.judge(_reading(acc={"ahead": 18, "rate": 0.45}))}
    assert j["C1"]["verdict"].startswith("FALSIFIER FIRED"), j["C1"]
    # two thirds ahead on forgetting is C2's
    j = {r["id"]: r for r in e296.judge(_reading(fgt={"ahead": 28, "rate": 0.70}))}
    assert j["C2"]["verdict"].startswith("FALSIFIER FIRED"), j["C2"]
    # a powered resolved comparison favouring the biological arm is C3's
    rows = _reading()["comparisons"]
    rows[0]["ahead"] = True
    j = {r["id"]: r for r in e296.judge(_reading(rows=rows))}
    assert j["C3"]["verdict"].startswith("FALSIFIER FIRED"), j["C3"]
    # and a corpus with nothing that well powered cannot support the claim either
    rows = [{"artifact": "a.json", "metric": "mean_forgetting", "sigma": 2.5, "n": 5, "delta": -0.03,
             "ahead": False, "readout": 32, "overlap": 0.0, "basis": "cell_class"}]
    j = {r["id"]: r for r in e296.judge(_reading(rows=rows))}
    assert j["C3"]["verdict"].startswith("FALSIFIER FIRED"), j["C3"]
    assert e296.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e296.judge({"comparisons": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_control_is_what_the_finding_says():
    rows = e296.comparisons()
    s = e296.by_metric(rows)
    assert s["final_accuracy"]["comparisons"] == 40 and s["mean_forgetting"]["comparisons"] == 40, s
    # on accuracy a random partition of matched size is the better arm by count ...
    assert s["final_accuracy"]["ahead"] == 15, s["final_accuracy"]
    assert s["final_accuracy"]["resolved"] == 5 and s["final_accuracy"]["resolved_ahead"] == 1, s["final_accuracy"]
    # ... but the largest resolved accuracy comparison favours the biological partition
    assert s["final_accuracy"]["largest_ahead"] > s["final_accuracy"]["largest_against"], s["final_accuracy"]
    # on forgetting the biological partition wins where the power is, and loses the count
    assert s["mean_forgetting"]["ahead"] == 18, s["mean_forgetting"]
    assert s["mean_forgetting"]["resolved"] == 7 and s["mean_forgetting"]["resolved_ahead"] == 3, s["mean_forgetting"]
    # every resolved comparison that favours it rests on 5, 40 or 40 replicates, never on three or sixteen
    assert s["mean_forgetting"]["resolved_ahead_replicates"] == [5, 40, 40], s["mean_forgetting"]
    assert all(n in (3, 16) for n in s["mean_forgetting"]["resolved_against_replicates"]), s["mean_forgetting"]
    # and both powered resolved comparisons favour the biological partition, which is C3's falsifier
    powered = [x for x in rows if x["sigma"] >= 2 and x["n"] >= 40]
    assert len(powered) == 2 and all(x["ahead"] for x in powered), powered
    assert {x["artifact"] for x in powered} == {"e140_r32_methods_plastic_40reps.json",
                                               "e275_frozenbias_suite600_40reps.json"}, powered


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e296_the_matched_random_control.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["by_metric"]["final_accuracy"]["ahead"] == 15, d["by_metric"]
    assert d["by_metric"]["mean_forgetting"]["ahead"] == 18, d["by_metric"]
    claims = {x["id"]: x for x in d["claims"]}
    assert claims["C1"]["verdict"].startswith("FALSIFIER FIRED"), claims["C1"]
    assert claims["C2"]["verdict"].startswith("MET"), claims["C2"]
    assert claims["C3"]["verdict"].startswith("FALSIFIER FIRED"), claims["C3"]
    assert "2 favour the biological partition" in claims["C3"]["measured"], claims["C3"]
