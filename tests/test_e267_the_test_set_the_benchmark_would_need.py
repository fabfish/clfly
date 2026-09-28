"""`e267` turns the benchmark's own noise block into a suite size, so the tests pin the census's filters, the
arithmetic, both faces of the three claims, and the live numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e267_the_test_set_the_benchmark_would_need as e267


def test_the_variance_helper_and_the_arm_filter():
    assert abs(e267.variance([1.0, 2.0, 3.0]) - 1.0) < 1e-12
    assert e267.arms_of({"methods": {"naive": {"replicates": [{}]}, "ewc": {"replicates": []}, "x": 1}}) == ["naive"]
    assert e267.arms_of({"methods": [1, 2]}) == []


def _art(path: Path, reps: dict, binom, n_eval=144):
    payload = {"config": {"circuit_size": 300}, "methods": {},
               "evaluation_noise": {"n_eval": n_eval}}
    for a, xs in reps.items():
        payload["methods"][a] = {"replicates": [{"final_accuracy": v, "mean_forgetting": v} for v in xs]}
        payload["evaluation_noise"][a] = {"binomial_sem": binom[a]}
    path.write_text(json.dumps(payload), encoding="utf-8")


SPREAD = [0.10, 0.20, 0.30, 0.40]


def test_the_census_reads_a_fraction_and_the_suite_it_implies(tmp_path):
    # one and a half times the arm's own sd, so the floor is 2.25 of its variance
    _art(tmp_path / "over.json", {"naive": SPREAD, "ewc": SPREAD},
         {"naive": 1.5 * math.sqrt(e267.variance(SPREAD)), "ewc": 0.01})
    _art(tmp_path / "under.json", {"naive": SPREAD, "ewc": SPREAD}, {"naive": 0.01, "ewc": 0.01})
    # neither a single-arm artifact nor one with no block belongs in the census
    _art(tmp_path / "alone.json", {"naive": SPREAD}, {"naive": 0.01})
    (tmp_path / "no_block.json").write_text(json.dumps(
        {"config": {}, "methods": {"naive": {"replicates": [{"final_accuracy": 0.5}] * 4},
                                   "ewc": {"replicates": [{"final_accuracy": 0.5}] * 4}}}), encoding="utf-8")
    rows = e267.census(tmp_path)
    assert sorted({r["artifact"] for r in rows}) == ["over.json", "under.json"], rows
    over = next(r for r in rows if r["artifact"] == "over.json" and r["metric"] == "final_accuracy")
    assert abs(over["fraction"]["naive"] - 2.25) < 1e-9, over["fraction"]
    assert abs(over["fraction"]["ewc"] - 0.01 ** 2 / e267.variance(SPREAD)) < 1e-12, over["fraction"]
    assert over["any_over"] and not over["all_over"], over
    assert abs(over["needed"] - 144.0 * 2.25) < 1e-9, over["needed"]
    under = next(r for r in rows if r["artifact"] == "under.json" and r["metric"] == "final_accuracy")
    assert not under["any_over"] and under["needed"] < 144.0, under


def test_the_census_skips_an_artifact_with_a_dead_arm(tmp_path):
    _art(tmp_path / "flat.json", {"naive": [0.5] * 4, "ewc": SPREAD}, {"naive": 0.01, "ewc": 0.01})
    assert e267.census(tmp_path) == [], "an arm that does not move has no fraction to form"


def _row(worst, all_over, needed, n_eval=144, artifact="a.json", metric="final_accuracy"):
    return {"artifact": artifact, "metric": metric, "n": 40, "n_eval": n_eval, "worst": worst,
            "worst_arm": "naive", "all_over": all_over, "any_over": worst >= 1.0, "needed": needed,
            "fraction": {"naive": worst}, "arms": ["naive", "ewc"]}


def test_the_three_claims_read_both_faces():
    rows = [_row(0.5, False, 72.0), _row(1.5, True, 216.0, artifact="b.json"), _row(2.0, True, 300.0, artifact="c.json")]
    j = {r["id"]: r for r in e267.judge(rows)}
    assert j["S1"]["verdict"].startswith("MET"), j["S1"]
    assert j["S2"]["verdict"].startswith("MET") and "b.json" in j["S2"]["measured"], j["S2"]
    assert j["S3"]["verdict"].startswith("MET"), j["S3"]
    # a fifth of the matrices is S1's floor: one of five is at it, one of ten is under
    j = {r["id"]: r for r in e267.judge([_row(0.5, False, 72.0)] * 4 + [_row(1.5, True, 216.0)])}
    assert j["S1"]["verdict"].startswith("MET"), j["S1"]
    j = {r["id"]: r for r in e267.judge([_row(0.5, False, 72.0)] * 9 + [_row(1.5, True, 216.0)])}
    assert j["S1"]["verdict"].startswith("FALSIFIER FIRED"), j["S1"]
    # five whole configurations is S2's falsifier, and none refuses S3
    j = {r["id"]: r for r in e267.judge([_row(1.5, True, 216.0, artifact=f"{i}.json") for i in range(5)])}
    assert j["S2"]["verdict"].startswith("FALSIFIER FIRED"), j["S2"]
    j = {r["id"]: r for r in e267.judge([_row(0.5, False, 72.0)])}
    assert j["S2"]["verdict"].startswith("FALSIFIER FIRED") and j["S3"]["verdict"].startswith("REFUSED"), j
    # twenty times the suite is S3's ceiling
    j = {r["id"]: r for r in e267.judge([_row(25.0, True, 25 * 144.0)])}
    assert j["S3"]["verdict"].startswith("FALSIFIER FIRED"), j["S3"]
    assert e267.judge([])[0]["verdict"].startswith("REFUSED")


def test_the_live_census_prices_the_three_configurations_that_cannot_see_themselves():
    """The finding's numbers on the artifact: 98 matrices at 144 items, a third of them with an arm inside its own
    floor, three with every arm inside, and the largest implied suite 7.6 times the one in use."""
    p = Path("runs/e267_the_test_set_the_benchmark_would_need.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["matrices"]
    assert len(rows) >= 98, "the corpus grows; the census is a lower bound"
    assert {r["n_eval"] for r in rows} == {144}, "the corpus reads one suite size"
    assert sum(1 for r in rows if r["any_over"]) >= 31, "the count grows with the corpus"
    assert sum(1 for r in rows if r["any_over"]) / len(rows) >= 0.2, "S1's share, re-read today"
    whole = sorted((r for r in rows if r["all_over"]), key=lambda r: -r["needed"])
    assert [r["artifact"] for r in whole] == ["e84_replay96_taskIL_5reps.json",
                                              "e140_r32_methods_frozenbias_40reps.json",
                                              "e167_r32_noise2.0_lam3e-4.json"], whole
    assert [round(r["needed"]) for r in whole] == [1096, 300, 165], [r["needed"] for r in whole]
    assert max(r["needed"] for r in whole) / 144 > 7.0
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("S1", "S2", "S3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "31 of " in claims["S1"]["measured"], claims["S1"]  # the denominator grows with the corpus
