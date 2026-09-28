"""`e266` was written before its runs finished, so the tests pin the arithmetic, both faces of the four claims and the
refusal that keeps the module from reporting a number while the artifacts are absent.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e266_matched_settings_read as e266


def test_the_helpers_and_the_fisher_band():
    assert abs(e266.variance([1.0, 2.0, 3.0]) - 1.0) < 1e-12
    assert abs(e266.covariance([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) - 2.0) < 1e-12
    narrow = e266.fisher_band(144, 0.3)
    wide = e266.fisher_band(16, 0.3)
    assert 0.0 < narrow < wide < 1.0, (narrow, wide)
    assert math.isnan(e266.fisher_band(3, 0.3)), "two degrees of freedom is no band"
    assert e266.fisher_band(144, 0.0) < 0.35, "a near-zero correlation has a band near 2/sqrt(n)"


def _matrix(corr_basis, corr_ne, corr_nr, corr_pen, frac=0.5, n=16):
    pairs = {e266.PAIRS[0]: corr_basis, e266.PAIRS[1]: corr_ne, e266.PAIRS[2]: corr_nr,
             e266.PENALTY_PAIR: corr_pen}
    arms = ["naive", "ewc", "ewc-block", "ewc-block-rand"]
    return {"n": n, "arms": arms, "variance": {a: 0.01 for a in arms}, "item_variance": {a: 0.01 * frac for a in arms},
            "corr": pairs, "ceiling": {p: 0.1 for p in pairs},
            "excess": {p: v - 0.1 for p, v in pairs.items()}, "fraction": {a: frac for a in arms},
            "readable": frac < 1.0, "seconds": 100.0}


def _rows(corr_basis_a=0.5, corr_basis_b=0.45, corr_pen=0.4, frac=0.5):
    # keyed by the names the module looks for, so the judge's own lookup is what the test exercises
    first, second = (Path(p).name for p in e266.RUNS)
    return {first: {m: _matrix(corr_basis_a, 0.2, 0.1, corr_pen, frac) for m in e266.METRICS},
            second: {m: _matrix(corr_basis_b, 0.2, 0.1, corr_pen, frac) for m in e266.METRICS}}


def _judge(rows):
    return {r["id"]: r for r in e266.judge(rows)}


def test_the_module_refuses_while_its_runs_are_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(e266, "RUNS", (str(tmp_path / "a.json"), str(tmp_path / "b.json")))
    monkeypatch.setattr(e266, "ACROSS", str(tmp_path / "c.json"))
    assert e266.readings() == {}
    j = _judge({})
    for cid in ("M1", "M2", "M3", "M4"):
        assert j[cid]["verdict"].startswith("REFUSED"), j[cid]


def test_an_artifact_builds_its_matrix_and_marks_readability(tmp_path):
    reps = {"naive": [0.1, 0.2, 0.3, 0.4], "ewc": [0.15, 0.25, 0.35, 0.45],
            "ewc-block": [0.2, 0.3, 0.4, 0.5], "ewc-block-rand": [0.1, 0.3, 0.2, 0.4]}
    payload = {"config": {"circuit_size": 300},
               "evaluation_noise": {a: {"binomial_sem": 0.05} for a in reps},
               "methods": {a: {"replicates": [{"final_accuracy": v, "mean_forgetting": v} for v in vs]}
                           for a, vs in reps.items()}}
    p = tmp_path / "a.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    m = e266.matrix(payload, "final_accuracy")
    assert m["n"] == 4 and e266.PENALTY_PAIR in m["corr"], m["corr"]
    assert abs(m["corr"][("naive", "ewc-block")] - 1.0) < 1e-9, "these two arms are proportional"
    assert m["readable"] is True and abs(m["excess"][e266.PAIRS[0]] - (m["corr"][e266.PAIRS[0]]
                                                                      - m["ceiling"][e266.PAIRS[0]])) < 1e-12


def test_M1_and_M2_read_the_two_runs_against_each_other():
    j = _judge(_rows())
    assert j["M1"]["verdict"].startswith("MET"), j["M1"]
    assert j["M2"]["verdict"].startswith("MET"), j["M2"]
    # the same configuration ordering the pairs differently is M1's falsifier
    j = _judge(_rows(corr_basis_a=0.1, corr_basis_b=0.9))
    assert j["M1"]["verdict"].startswith("FALSIFIER FIRED"), j["M1"]
    # and a difference far outside the band is M2's
    j = _judge(_rows(corr_basis_a=0.0, corr_basis_b=0.9))
    assert j["M2"]["verdict"].startswith("FALSIFIER FIRED"), j["M2"]


def test_M3_needs_the_penalty_pair_above_both_naive_pairs():
    j = _judge(_rows(corr_pen=0.4))
    assert j["M3"]["verdict"].startswith("MET"), j["M3"]
    j = _judge(_rows(corr_pen=0.05))
    assert j["M3"]["verdict"].startswith("FALSIFIER FIRED"), j["M3"]
    rows = _rows()
    for n in rows:
        for metric in e266.METRICS:
            rows[n][metric]["corr"].pop(e266.PENALTY_PAIR)
    j = _judge(rows)
    assert j["M3"]["verdict"].startswith("FALSIFIER FIRED"), j["M3"]


def test_M4_fires_when_an_arm_sits_inside_its_own_test_set_floor():
    assert _judge(_rows(frac=0.5))["M4"]["verdict"].startswith("MET")
    assert _judge(_rows(frac=1.2))["M4"]["verdict"].startswith("FALSIFIER FIRED")
