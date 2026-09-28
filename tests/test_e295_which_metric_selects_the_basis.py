"""`e295` reads the project's own comparison across every artifact that ran both arms, so the tests pin the sign
convention (the one place a mistake would invert the finding), the counts, the disagreement, both faces of the three
claims, and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e295_which_metric_selects_the_basis as e295


def _art(path: Path, rows=6, acc_gap=0.01, fgt_gap=0.01, arms=("ewc", "ewc-block")):
    """A stand-in artifact where the block arm is better on accuracy and worse on forgetting by the given gaps.

    The gaps are made to vary across replicates, so the paired difference has a spread rather than being a constant --
    a constant difference has a sem of zero and is not a comparison at all.
    """
    payload = {"config": {"readout_size": 32, "input_overlap": 0.0}, "methods": {}}
    for a in arms:
        reps = []
        for r in range(rows):
            base = 0.80 + 0.01 * r
            wobble = 1.0 + 0.2 * r
            reps.append({"final_accuracy": base + (acc_gap * wobble if a == "ewc-block" else 0.0),
                         "mean_forgetting": 0.10 + 0.01 * r + (fgt_gap * wobble if a == "ewc-block" else 0.0)})
        payload["methods"][a] = {"replicates": reps}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_sign_convention_is_the_one_the_metrics_mean(tmp_path):
    p = tmp_path / "a.json"
    _art(p)
    d = e295.load(p)
    acc = e295.contrast(d, "ewc", "ewc-block", "final_accuracy")
    fgt = e295.contrast(d, "ewc", "ewc-block", "mean_forgetting")
    # delta is ewc minus ewc-block: negative on accuracy when the block arm is better ...
    assert acc["delta"] < 0 and acc["block_ahead"] is True, acc
    # ... and negative on forgetting when the block arm is WORSE, because lower forgetting is better
    assert fgt["delta"] < 0 and fgt["block_ahead"] is False, fgt
    assert acc["n"] == 6 and acc["negative"] == 6, acc
    # a tie is not "ahead" for either arm
    _art(p, acc_gap=0.0, fgt_gap=0.0)
    assert e295.contrast(e295.load(p), "ewc", "ewc-block", "final_accuracy") is None      # a constant difference
    # fewer than three replicates is not a comparison
    _art(p, rows=2)
    assert e295.contrast(e295.load(p), "ewc", "ewc-block", "final_accuracy") is None


def test_the_counts_and_the_disagreement(tmp_path):
    agree, differ = tmp_path / "agree.json", tmp_path / "differ.json"
    _art(agree, acc_gap=0.01, fgt_gap=-0.01)      # block better on BOTH metrics
    _art(differ, acc_gap=0.01, fgt_gap=0.01)      # block better on accuracy, worse on forgetting
    rows = e295.comparisons(tmp_path)
    assert len(rows) == 4, rows
    s = e295.by_metric(rows)
    assert s["final_accuracy"]["ahead"] == 2 and s["mean_forgetting"]["ahead"] == 1, s
    d = e295.disagreement(rows)
    assert d["artifacts"] == 2 and d["differ"] == 1 and d["examples"] == ["differ.json"], d


def _reading(acc=None, fgt=None, differ=0.5, artifacts=4):
    base = {"comparisons": 4, "ahead": 3, "rate": 0.75, "resolved": 2, "resolved_ahead": 2,
            "largest_ahead": 4.0, "largest_behind": 1.0}
    return {"comparisons": [{"metric": "final_accuracy", "sigma": 3.0, "block_ahead": True, "delta": -0.01,
                             "n": 5, "artifact": "a.json"},
                            {"metric": "mean_forgetting", "sigma": 3.0, "block_ahead": False, "delta": -0.01,
                             "n": 5, "artifact": "a.json"}],
            "by_metric": {"final_accuracy": dict(base, **(acc or {})),
                          "mean_forgetting": dict(base, **(fgt or {"ahead": 1, "rate": 0.25, "resolved": 1,
                                                                   "resolved_ahead": 0}))},
            "disagreement": {"artifacts": artifacts, "differ": int(differ * artifacts),
                             "rate": differ, "examples": ["a.json"]}}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e295.judge(_reading())}
    for cid in ("B1", "B2", "B3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # an accuracy metric the block arm loses is B1's falsifier
    j = {r["id"]: r for r in e295.judge(_reading(acc={"ahead": 1, "rate": 0.25, "resolved_ahead": 0}))}
    assert j["B1"]["verdict"].startswith("FALSIFIER FIRED"), j["B1"]
    # a forgetting metric it wins, or a resolved comparison it wins, is B2's
    j = {r["id"]: r for r in e295.judge(_reading(fgt={"ahead": 3, "rate": 0.75, "resolved": 1, "resolved_ahead": 1}))}
    assert j["B2"]["verdict"].startswith("FALSIFIER FIRED"), j["B2"]
    j = {r["id"]: r for r in e295.judge(_reading(fgt={"ahead": 1, "rate": 0.25, "resolved": 1, "resolved_ahead": 0}))}
    assert j["B2"]["verdict"].startswith("MET"), j["B2"]
    # metrics that agree everywhere are B3's
    j = {r["id"]: r for r in e295.judge(_reading(differ=0.0))}
    assert j["B3"]["verdict"].startswith("FALSIFIER FIRED"), j["B3"]
    assert e295.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e295.judge({"comparisons": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_corpus_is_what_the_finding_says():
    rows = e295.comparisons()
    s = e295.by_metric(rows)
    assert s["final_accuracy"]["comparisons"] == 26 and s["mean_forgetting"]["comparisons"] == 26, s
    assert s["final_accuracy"]["ahead"] == 21, s["final_accuracy"]
    assert s["final_accuracy"]["resolved"] == 9 and s["final_accuracy"]["resolved_ahead"] == 8, s["final_accuracy"]
    assert s["mean_forgetting"]["ahead"] == 11, s["mean_forgetting"]
    assert s["mean_forgetting"]["resolved"] == 3 and s["mean_forgetting"]["resolved_ahead"] == 0, s["mean_forgetting"]
    d = e295.disagreement(rows)
    assert d["artifacts"] == 26 and d["differ"] == 10, d
    # every resolved forgetting comparison has the block arm behind, and one resolved accuracy comparison has it behind
    for x in rows:
        if x["metric"] == "mean_forgetting" and x["sigma"] >= 2:
            assert not x["block_ahead"], x
        if x["metric"] == "final_accuracy" and x["sigma"] >= 2 and not x["block_ahead"]:
            assert x["artifact"] == "e8_basis.json", x


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e295_which_metric_selects_the_basis.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["by_metric"]["final_accuracy"]["ahead"] == 21, d["by_metric"]
    assert d["disagreement"]["differ"] == 10, d["disagreement"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("B1", "B2", "B3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "0 of the 3 resolved" in claims["B2"]["measured"], claims["B2"]
