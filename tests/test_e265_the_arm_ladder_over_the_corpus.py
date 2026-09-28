"""`e265` reads the arm ladder over the whole corpus, so the tests pin the scan's filters and readability rule, the
repeat-group finder, both faces of the four claims, and the live census's numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e265_the_arm_ladder_over_the_corpus as e265


def test_the_variance_and_covariance_helpers():
    xs, ys = [1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0]
    assert abs(e265.variance(xs) - 5.0 / 3.0) < 1e-12
    assert abs(e265.covariance(xs, ys) + 5.0 / 3.0) < 1e-12


def test_the_configuration_key_ignores_only_the_output_path():
    a = {"config": {"lam": 0.1, "json_out": "a.json", "seeds": 3}}
    b = {"config": {"json_out": "b.json", "seeds": 3, "lam": 0.1}}
    assert e265.config_key(a) == e265.config_key(b), "field order and the output path are not settings"


def _art(path: Path, reps: dict, binom: float, n: int = 4, extra_arm: str | None = None):
    methods = {a: {"replicates": [{"final_accuracy": v, "mean_forgetting": v} for v in vs]} for a, vs in reps.items()}
    if extra_arm:
        methods[extra_arm] = {"replicates": [{"final_accuracy": 0.5, "mean_forgetting": 0.1} for _ in range(n)]}
    payload = {"config": {"circuit_size": 800, "support": 80, "lam": 0.1, "json_out": path.name},
               "evaluation_noise": {a: {"binomial_sem": binom} for a in methods},
               "methods": methods}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_scan_builds_the_three_matrices_and_marks_readability(tmp_path):
    reps = {"naive": [0.10, 0.11, 0.90, 0.91], "ewc-block": [0.10, 0.11, 0.90, 0.91],
            "ewc-block-rand": [0.10, 0.11, 0.90, 0.91]}
    _art(tmp_path / "readable.json", reps, binom=0.01)
    _art(tmp_path / "floor_dominates.json", reps, binom=0.5)
    # an artifact missing a pair, and one with too few replicates: both invisible to the census
    _art(tmp_path / "two_arms.json", {"naive": reps["naive"], "ewc-block": reps["ewc-block"]}, binom=0.01)
    _art(tmp_path / "too_short.json", {a: vs[:2] for a, vs in reps.items()}, binom=0.01, n=2)
    rows = e265.scan(tmp_path)
    assert [r["artifact"] for r in rows] == ["floor_dominates.json", "readable.json"], rows
    good = next(r for r in rows if r["artifact"] == "readable.json")
    bad = next(r for r in rows if r["artifact"] == "floor_dominates.json")
    assert good["matrices"]["final_accuracy"]["readable"] is True, good
    assert bad["matrices"]["final_accuracy"]["readable"] is False, bad
    m = good["matrices"]["final_accuracy"]
    assert abs(m["corr"][e265.PAIRS[0]] - 1.0) < 1e-9, m["corr"]
    assert abs(m["excess"][e265.PAIRS[0]] - (m["corr"][e265.PAIRS[0]] - m["ceiling"][e265.PAIRS[0]])) < 1e-12


def test_repeat_groups_find_only_the_configurations_run_twice(tmp_path):
    reps = {"naive": [0.1, 0.2, 0.3, 0.4], "ewc-block": [0.2, 0.3, 0.4, 0.5],
            "ewc-block-rand": [0.15, 0.25, 0.35, 0.45]}
    for name in ("a.json", "b.json"):
        _art(tmp_path / name, reps, binom=0.01)
    _art(tmp_path / "c.json", reps, binom=0.01, extra_arm="replay")
    (tmp_path / "c.json").write_text(json.dumps({**json.loads((tmp_path / "c.json").read_text(encoding="utf-8")),
                                                 "config": {"circuit_size": 800, "support": 80, "lam": 1.0,
                                                            "json_out": "c.json"}}), encoding="utf-8")
    rows = e265.scan(tmp_path)
    groups = e265.repeat_groups(rows)
    assert len(groups) == 1, groups
    assert sorted(r["artifact"] for r in next(iter(groups.values()))) == ["a.json", "b.json"], groups
    assert len(rows) == 3, "the third run is still part of the census, just of another configuration"


def _row(name, corr_basis, corr_ne, corr_nr, read=True, n=40, secs=100.0, arms=("naive", "ewc-block",
                                                                               "ewc-block-rand")):
    m = {"corr": {e265.PAIRS[0]: corr_basis, e265.PAIRS[1]: corr_ne, e265.PAIRS[2]: corr_nr},
         "ceiling": {p: 0.1 for p in e265.PAIRS}, "excess": {}, "fraction": {a: 0.5 for a in arms},
         "readable": read}
    m["excess"] = {p: m["corr"][p] - m["ceiling"][p] for p in e265.PAIRS}
    return {"artifact": name, "n": n, "arms": list(arms), "key": (("lam", "0.1"),), "seconds": secs,
            "matrices": {metric: dict(m) for metric in e265.METRICS}, "replicates": {a: [1] for a in arms}}


def test_W1_fires_when_the_whole_configuration_clears_its_own_floor():
    frozen, plastic = _row(e265.FROZEN, 0.3, 0.2, 0.1), _row(e265.PLASTIC, 0.3, 0.2, 0.1)
    for r, frac in ((frozen, 2.0), (plastic, 0.5)):
        for metric in e265.METRICS:
            r["matrices"][metric]["fraction"] = {a: frac for a in r["arms"]}
    j = {x["id"]: x for x in e265.judge([frozen, plastic], {})}
    assert j["W1"]["verdict"].startswith("MET"), j["W1"]
    frozen["matrices"]["final_accuracy"]["fraction"] = {"naive": 0.8, "ewc-block": 2.0, "ewc-block-rand": 2.0}
    j = {x["id"]: x for x in e265.judge([frozen, plastic], {})}
    assert j["W1"]["verdict"].startswith("FALSIFIER FIRED"), j["W1"]
    j = {x["id"]: x for x in e265.judge([plastic], {})}
    assert j["W1"]["verdict"].startswith("REFUSED"), j["W1"]


def test_W2_counts_the_basis_pair_s_rank_and_fires_when_it_leads_throughout():
    rows = [_row("a.json", 0.5, 0.2, 0.1), _row("b.json", 0.5, 0.2, 0.1)]
    j = {x["id"]: x for x in e265.judge(rows, {})}
    assert j["W2"]["verdict"].startswith("FALSIFIER FIRED"), j["W2"]  # highest in 2 of 2
    rows = [_row("a.json", 0.1, 0.5, 0.4), _row("b.json", 0.2, 0.5, 0.4)]
    j = {x["id"]: x for x in e265.judge(rows, {})}
    assert j["W2"]["verdict"].startswith("MET"), j["W2"]
    assert "highest in 0" in j["W2"]["measured"], j["W2"]


def test_W3_and_W4_read_the_repeats_of_one_configuration():
    # one configuration, three runs: the basis pair's rank is not the same for every repeat
    rows = [_row("fb8_a.json", 0.5, 0.2, 0.1), _row("fb8_b.json", 0.1, 0.2, 0.5), _row("fb8_c.json", 0.1, 0.5, 0.4)]
    for i, r in enumerate(rows):
        r["key"] = (("lam", "0.003"),)
        r["n"] = 5
        r["replicates"] = {a: [float(i), 2.0 + i] for a in r["arms"]}
    groups = e265.repeat_groups(rows)
    assert len(groups) == 1, groups
    j = {x["id"]: x for x in e265.judge(rows, groups)}
    assert j["W3"]["verdict"].startswith("MET"), j["W3"]
    assert "fb8" in j["W3"]["measured"], j["W3"]
    assert j["W4"]["verdict"].startswith("MET"), j["W4"]  # no two runs are bit-identical
    # one bit-identical pair out of three runs is the claim; every pair being identical is its falsifier
    rows[1]["replicates"] = dict(rows[0]["replicates"])
    j = {x["id"]: x for x in e265.judge(rows, groups)}
    assert j["W4"]["verdict"].startswith("MET"), j["W4"]
    rows[2]["replicates"] = dict(rows[0]["replicates"])
    j = {x["id"]: x for x in e265.judge(rows, groups)}
    assert j["W4"]["verdict"].startswith("FALSIFIER FIRED"), j["W4"]
    assert e265.judge([], {})[0]["verdict"].startswith("REFUSED")


def test_the_live_census_reads_the_ordering_as_a_coin_flip_and_the_repeats_as_different_runs():
    """The finding's numbers on the artifact: 35 artifacts and 70 matrices of which 50 are readable, the basis pair
    leading 21 times, and the fb8 group being one configuration and several different experiments."""
    p = Path("runs/e265_the_arm_ladder_over_the_corpus.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["artifacts"]) >= 35, "the corpus grows; the census is a lower bound"
    top = middle = low = 0
    for r in d["artifacts"]:
        for metric in d["metrics"]:
            m = r["matrices"][metric]
            if not m["readable"]:
                continue
            order = sorted(m["corr"], key=lambda k: -m["corr"][k])
            rank = order.index("ewc-block/ewc-block-rand")
            top += rank == 0
            middle += rank == 1
            low += rank == 2
    assert top + middle + low >= 50, (top, middle, low)
    assert top <= (top + middle + low) / 2, "W2's claim, re-read on today's corpus"
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("W1", "W2", "W3", "W4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "naive 2.09" in claims["W1"]["measured"], claims["W1"]
    fb8 = [r for r in d["artifacts"] if "fb8" in r["artifact"]]
    key = next(r["key"] for r in d["artifacts"] if r["artifact"] == "e102_rate_fb8_rerun.json")
    fb8 = [r for r in d["artifacts"] if r["key"] == key]
    assert len(fb8) == 5 and all(r["n"] == 5 for r in fb8), [r["artifact"] for r in fb8]
    secs = sorted(r["seconds"] for r in fb8)
    assert secs[-1] / secs[0] > 3.0, secs
    assert "e102_rate_fb8_omp1.json" in claims["W4"]["measured"], claims["W4"]
