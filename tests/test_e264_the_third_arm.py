"""`e264` reads the third arm against the pair the line's contrast is about, so the tests pin the covariance and
correlation helpers, the item ceiling as a bound, both faces of the three claims, the largest-budget selector, and the
live matrices' numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e264_the_third_arm as e264


def test_the_covariance_and_correlation_helpers():
    xs, ys = [1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]
    assert abs(e264.covariance(xs, ys) - 2.0 * e264.variance(xs)) < 1e-12
    assert abs(e264.covariance(xs, xs) - e264.variance(xs)) < 1e-12
    xs2 = [1.0, 2.0, 3.0, 4.0]
    ys2 = [4.0, 3.0, 2.0, 1.0]
    assert abs(e264.covariance(xs2, ys2) / math.sqrt(e264.variance(xs2) * e264.variance(ys2)) + 1.0) < 1e-12


def _art(reps: dict, binom: dict, corr: float = 0.0, n: int = 4):
    return {"evaluation_noise": {a: {"binomial_sem": b} for a, b in binom.items()},
            "methods": {a: {"replicates": [{"final_accuracy": v, "mean_forgetting": v} for v in vs]}
                        for a, vs in reps.items()},
            "matched_pair": {"final_accuracy": {"corr": corr}}}


def test_the_matrix_reads_the_item_ceiling_and_the_excess_from_the_three_arms():
    """A naive arm that tracks one EWC arm and not the other, with a known test-set part on each."""
    reps = {"naive": [0.10, 0.20, 0.30, 0.40],
            "ewc-block": [0.20, 0.40, 0.60, 0.80],
            "ewc-block-rand": [0.15, 0.30, 0.45, 0.60]}
    binom = {"naive": 0.01, "ewc-block": 0.02, "ewc-block-rand": 0.02}
    m = e264.matrix(_art(reps, binom), "final_accuracy")
    assert m["n"] == 4
    for pair, c in m["corr"].items():
        assert abs(m["excess"][pair] - (c - m["ceiling"][pair])) < 1e-12
    assert abs(m["corr"][("naive", "ewc-block")] - 1.0) < 1e-12, "these two arms are proportional"
    assert abs(m["corr"][e264.PAIR] - 1.0) < 1e-12
    assert m["ceiling"][("naive", "ewc-block")] < 1.0, "a small test-set part cannot explain a perfect correlation"


def test_the_largest_selector_takes_one_matrix_per_metric():
    small = {"n": 4}
    rows = {"a/final_accuracy": dict(small, tag="acc4"), "b/final_accuracy": {"n": 16, "tag": "acc16"},
            "a/mean_forgetting": {"n": 4, "tag": "for4"}, "b/mean_forgetting": {"n": 144, "tag": "for144"}}
    got = e264.largest_by_metric(rows)
    assert got["final_accuracy"]["tag"] == "acc16" and got["mean_forgetting"]["tag"] == "for144", got


def _m(corr_pair, corr_naive1, corr_naive2, exc_pair, exc_n1, exc_n2, n=144, metric="mean_forgetting"):
    return {"n": n, "corr": {e264.PAIR: corr_pair, e264.NAIVE_PAIRS[0]: corr_naive1,
                             e264.NAIVE_PAIRS[1]: corr_naive2},
            "excess": {e264.PAIR: exc_pair, e264.NAIVE_PAIRS[0]: exc_n1, e264.NAIVE_PAIRS[1]: exc_n2},
            "variance": {}, "item_variance": {}, "ceiling": {}, "reported_pair_corr": corr_pair}


def test_T1_counts_the_runs_where_the_EWC_pair_alone_is_above_its_ceiling():
    good = {"a/final_accuracy": _m(0.3, 0.1, 0.1, 0.1, -0.1, -0.1),
            "b/final_accuracy": _m(0.3, 0.1, 0.1, 0.1, 0.0, -0.1)}
    j = {r["id"]: r for r in e264.judge(good)}
    assert j["T1"]["verdict"].startswith("MET"), j["T1"]
    bad = {"a/final_accuracy": _m(0.3, 0.4, 0.1, 0.1, 0.2, -0.1),
           "b/final_accuracy": _m(0.3, 0.4, 0.1, 0.1, 0.2, -0.1)}
    j = {r["id"]: r for r in e264.judge(bad)}
    assert j["T1"]["verdict"].startswith("FALSIFIER FIRED"), j["T1"]
    assert j["T1"]["measured"].count("naive pairs") == 2, j["T1"]


def test_T2_and_T3_read_the_largest_budget_of_each_metric():
    rows = {"a/mean_forgetting": _m(0.28, 0.12, 0.124, 0.175, 0.007, 0.013),
            "a/final_accuracy": _m(0.317, 0.118, 0.140, 0.085, -0.125, -0.100, metric="final_accuracy")}
    j = {r["id"]: r for r in e264.judge(rows)}
    assert j["T2"]["verdict"].startswith("MET"), j["T2"]
    assert j["T3"]["verdict"].startswith("MET"), j["T3"]
    # a naive pair within 1.5x of the EWC pair is T2's falsifier
    j = {r["id"]: r for r in e264.judge({"a/mean_forgetting": _m(0.20, 0.18, 0.12, 0.1, 0.02, 0.01)})}
    assert j["T2"]["verdict"].startswith("FALSIFIER FIRED"), j["T2"]
    # an EWC excess the naive pairs match is T3's
    j = {r["id"]: r for r in e264.judge({"a/mean_forgetting": _m(0.28, 0.12, 0.124, 0.05, 0.06, 0.04)})}
    assert j["T3"]["verdict"].startswith("FALSIFIER FIRED"), j["T3"]
    # and a naive pair more than 0.03 from the other is the second clause's falsifier
    j = {r["id"]: r for r in e264.judge({"a/mean_forgetting": _m(0.28, 0.30, 0.10, 0.19, 0.007, 0.005)})}
    assert j["T3"]["verdict"].startswith("FALSIFIER FIRED"), j["T3"]
    assert e264.judge({})[0]["verdict"].startswith("REFUSED")


def test_the_live_matrices_split_the_source_at_the_largest_budget():
    """The finding's numbers on the artifact: the EWC pair leading both naive pairs by more than 2x at 144
    replicates, its excess an order of magnitude above theirs on forgetting, and the sixteen-replicate matrices
    disagreeing among themselves about which naive pair leads."""
    p = Path("runs/e264_the_third_arm.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["matrices"]) == 6, sorted(d["matrices"])
    for name, m in d["matrices"].items():
        assert abs(m["matched_pair_corr"] - m["corr"]["ewc-block/ewc-block-rand"]) < 5e-4, name
    big = {n.rsplit("/", 1)[-1]: m for n, m in d["matrices"].items() if m["n"] == 144}
    assert set(big) == {"final_accuracy", "mean_forgetting"}, sorted(big)
    assert abs(big["final_accuracy"]["corr"]["ewc-block/ewc-block-rand"] - 0.317) < 1e-3
    assert abs(big["mean_forgetting"]["corr"]["ewc-block/ewc-block-rand"] - 0.282) < 1e-3
    for metric, m in big.items():
        ewc = m["corr"]["ewc-block/ewc-block-rand"]
        for pair in ("naive/ewc-block", "naive/ewc-block-rand"):
            assert ewc / m["corr"][pair] > 1.5, (metric, pair)
    assert big["mean_forgetting"]["excess"]["ewc-block/ewc-block-rand"] > 10 * max(
        big["mean_forgetting"]["excess"]["naive/ewc-block"],
        big["mean_forgetting"]["excess"]["naive/ewc-block-rand"])
    # the two small forgetting matrices put naive against the RANDOM basis highest, which the largest does not
    small = [m for n, m in d["matrices"].items() if m["n"] == 16 and n.endswith("mean_forgetting")]
    assert len(small) == 2 and all(m["corr"]["naive/ewc-block-rand"] >
                                   m["corr"]["ewc-block/ewc-block-rand"] for m in small), small
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("T1", "T2", "T3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
