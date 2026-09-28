"""`e272` prices the ordering claim, so the tests pin the standard-error arithmetic, the gap scan, both faces of the
three claims and the live numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e272_the_budget_the_ordering_needs as e272


def test_the_fisher_standard_error_and_the_replicates_a_gap_needs():
    assert abs(e272.se_fisher(0.0, 16) - 1.0 / math.sqrt(13)) < 1e-12
    assert abs(e272.se_fisher(0.5, 19) - (1 - 0.25) / 4.0) < 1e-12
    assert math.isnan(e272.se_fisher(0.5, 3)), "two degrees of freedom is no standard error"
    small = e272.n_for_gap(0.30, 0.4, 16)
    big = e272.n_for_gap(0.03, 0.4, 16)
    assert big > small > 16, (small, big)
    assert e272.n_for_gap(0.0, 0.4, 16) == float("inf")
    # a hundredfold gap needs a hundredth of the error, which is a hundred-squaredth of the replicates
    a, b = e272.n_for_gap(0.10, 0.4, 16), e272.n_for_gap(0.01, 0.4, 16)
    assert abs(b / a - 100.0) < 1.0, (a, b)


#: The two live runs' three contrast correlations, per metric: the second metric is where the 0.030 gap lives.
LIVE = {"a": {"final_accuracy": (0.596, 0.473, 0.409), "mean_forgetting": (0.562, 0.394, 0.364)},
        "b": {"final_accuracy": (0.589, 0.090, -0.168), "mean_forgetting": (0.573, 0.026, -0.303)}}


def _rows(n=16, bases=None):
    """Two runs at one budget with different orderings of the three contrast pairs, plus a powered matrix."""
    out = {}
    for run in ("a", "b"):
        for metric in e272.METRICS:
            corrs = bases if bases is not None else LIVE[run][metric]
            out[f"{run}/{metric}"] = {"n": n, "metric": metric, "seconds": None,
                                      "corr": dict(zip(e272.PAIRS, corrs))}
    out["across/final_accuracy"] = {"n": 144, "metric": "final_accuracy", "seconds": None,
                                    "corr": dict(zip(e272.PAIRS, (0.317, 0.118, 0.140)))}
    return out


def test_the_three_claims_read_both_faces():
    rows = _rows()
    j = {r["id"]: r for r in e272.judge(rows, {"r1": 205.0})}
    assert j["W1"]["verdict"].startswith("MET"), j["W1"]
    assert j["W2"]["verdict"].startswith("MET") and "0.030" in j["W2"]["measured"], j["W2"]
    assert j["W3"]["verdict"].startswith("MET"), j["W3"]
    assert "needs " in j["W3"]["measured"] and "hours" in j["W3"]["measured"], j["W3"]
    assert "within the 144" in j["W3"]["measured"], j["W3"]  # the one-bit reading is already bought
    # two runs whose orderings agree up to a wide gap are not W2's case
    j = {r["id"]: r for r in e272.judge(_rows(bases=(0.9, 0.5, 0.1)), {"r1": 205.0})}
    assert j["W2"]["verdict"].startswith("FALSIFIER FIRED"), j["W2"]
    # a wide smallest gap is not W3's either, and the estimators are compared only where two runs exist
    j = {r["id"]: r for r in e272.judge({k: v for k, v in _rows().items() if not k.startswith("b/")},
                                        {"r1": 205.0})}
    assert j["W1"]["verdict"].startswith("REFUSED"), j["W1"]
    assert e272.judge({}, {})[0]["verdict"].startswith("REFUSED")


def test_the_live_read_prices_the_ordering_beyond_what_the_line_can_buy():
    """The finding's numbers on the artifact: Fisher's standard error against the empirical one, a 0.030 gap as the
    smallest the ordering rests on, and thousands of replicates — hundreds of hours — to resolve it."""
    p = Path("runs/e272_the_budget_the_ordering_needs.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["matrices"]) >= 6, sorted(d["matrices"])
    assert d["matrices"]["e266_matched_side_seed0_16reps.json/final_accuracy"]["n"] == 16
    assert d["matrices"]["e178_rung_side_cs300_144reps.json/final_accuracy"]["n"] == 144
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("W1", "W2", "W3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "factor of 1.28" in claims["W1"]["measured"], claims["W1"]
    assert "0.030" in claims["W2"]["measured"], claims["W2"]
    assert "6446" in claims["W3"]["measured"] and "367 hours" in claims["W3"]["measured"], claims["W3"]
