"""`e263` reads the benchmark's own two blocks against each other, so the tests pin the variance helper, the
decomposition on a synthetic artifact whose covariance is known by construction, both faces of all four claims, and
the live table's numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e263_what_the_pairing_shares as e263


def test_the_variance_helper_is_the_sample_variance():
    assert abs(e263.variance([1.0, 2.0, 3.0]) - 1.0) < 1e-12
    assert e263.variance([2.0, 2.0, 2.0]) == 0.0


def _artifact(common: list[float], a_extra: list[float], b_extra: list[float], binom: tuple[float, float]):
    """Two arms that share `common` and differ by their own extras, with the matched pair computed from them."""
    a = [c + e for c, e in zip(common, a_extra)]
    b = [c + e for c, e in zip(common, b_extra)]
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = sum(d) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in d) / (n - 1))
    va, vb = e263.variance(a), e263.variance(b)
    cov = (va + vb - sd ** 2) / 2
    corr = cov / math.sqrt(va * vb)
    reps = lambda vs: [{"final_accuracy": v, "mean_forgetting": v} for v in vs]
    return {"evaluation_noise": {"ewc-block": {"binomial_sem": binom[0]}, "ewc-block-rand": {"binomial_sem": binom[1]}},
            "methods": {"ewc-block": {"replicates": reps(a)}, "ewc-block-rand": {"replicates": reps(b)}},
            "matched_pair": {"final_accuracy": {"corr": corr, "replicate_sd": sd, "sem_paired": sd / math.sqrt(n),
                                                "sem_unpaired": math.sqrt((va + vb) / n), "n": n}}}


def test_the_decomposition_recovers_the_correlation_it_was_built_from():
    art = _artifact([0.80, 0.78, 0.82, 0.76, 0.84, 0.74, 0.86, 0.72],
                    [0.010, -0.010, 0.005, -0.005, 0.008, -0.008, 0.003, -0.003],
                    [-0.004, 0.004, -0.009, 0.009, -0.002, 0.002, -0.007, 0.007],
                    (0.03, 0.03))
    r = e263.reading(art, "final_accuracy")
    assert abs(r["corr_from_cov"] - r["corr_reported"]) < 1e-9, r
    assert r["cov"] > 0 and r["corr_reported"] > 0.5, r
    assert abs(r["v_difference"] - (r["v"]["ewc-block"] + r["v"]["ewc-block-rand"] - 2 * r["cov"])) < 1e-12
    assert r["advantage"] > 1.3, r["advantage"]
    # a test-set term the arms fully share is the ceiling on what items can explain
    assert abs(r["cov_items"] - 0.03 * 0.03) < 1e-9, r["cov_items"]
    assert r["corr_items"] < r["corr_reported"], "the synthetic covariance is bigger than the item term"


def _row(metric="final_accuracy", corr=0.5, items=0.3, train=0.25, adv=1.4, adv_wo=1.1):
    arm = "ewc-block"
    return {"metric": metric, "corr_reported": corr, "corr_items": items, "corr_train": train,
            "advantage": adv, "advantage_without_items": adv_wo, "cov": 1.0,
            "v": {arm: 2.0, "ewc-block-rand": 1.0}, "cov_over_var": {arm: 0.5, "ewc-block-rand": 1.0}}


def test_the_claims_read_both_faces():
    good = {"a/final_accuracy": _row(), "b/mean_forgetting": _row(metric="mean_forgetting", items=0.1, train=0.4)}
    j = {r["id"]: r for r in e263.judge(good)}
    for cid in ("C1", "C2", "C3", "C4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # C1: an uncorrelated reading
    j = {r["id"]: r for r in e263.judge({"a/final_accuracy": dict(_row(), corr_reported=0.08)})}
    assert j["C1"]["verdict"].startswith("FALSIFIER FIRED"), j["C1"]
    # C2: the items explain everything
    j = {r["id"]: r for r in e263.judge({"a/final_accuracy": _row(items=0.52)})}
    assert j["C2"]["verdict"].startswith("FALSIFIER FIRED"), j["C2"]
    # C3: an advantage that does not fall
    j = {r["id"]: r for r in e263.judge({"a/final_accuracy": _row(adv_wo=1.45)})}
    assert j["C3"]["verdict"].startswith("FALSIFIER FIRED"), j["C3"]
    # C4: forgetting's training bound below its item bound
    j = {r["id"]: r for r in e263.judge({"b/mean_forgetting": _row(metric="mean_forgetting", items=0.4, train=0.1)})}
    assert j["C4"]["verdict"].startswith("FALSIFIER FIRED"), j["C4"]
    # and nothing on disk to read
    assert e263.judge({})[0]["verdict"].startswith("REFUSED")


def test_reading_skips_an_artifact_without_both_blocks(tmp_path, monkeypatch):
    (tmp_path / "only_methods.json").write_text(json.dumps(
        {"methods": {"ewc-block": {"replicates": [{"final_accuracy": 0.5}]}}}), encoding="utf-8")
    monkeypatch.setattr(e263, "ARTS", (str(tmp_path / "only_methods.json"), str(tmp_path / "absent.json")))
    assert e263.readings() == {}


def test_the_live_table_splits_the_correlation_by_metric():
    """The finding's numbers on the artifact: six readings whose algebra reproduces the reported correlation, the
    item ceiling short in five, and the pairing's advantage falling everywhere."""
    p = Path("runs/e263_what_the_pairing_shares.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["readings"]
    assert len(rows) == 6, sorted(rows)
    for name, r in rows.items():
        assert abs(r["corr_from_cov"] - r["corr_reported"]) < 5e-4, name
        assert 0.25 < r["corr_reported"] < 0.60, (name, r["corr_reported"])
        assert r["advantage_without_items"] < r["advantage"], name
        assert r["corr_items"] <= 0.40, name
    worst = rows["e60_side_lam0.1_16reps.json/final_accuracy"]
    assert abs(worst["corr_reported"] - 0.542) < 1e-3 and abs(worst["advantage"] - 1.468) < 1e-3, worst
    cc = rows["e46_c2b_powered.json/final_accuracy"]
    assert cc["advantage_without_items"] < 1.0, "that reading's whole pairing benefit is the shared test set"
    forget = [r for n, r in rows.items() if n.endswith("mean_forgetting")]
    assert len(forget) == 3 and all(r["corr_train"] > r["corr_items"] for r in forget), forget
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("C1", "C2", "C3", "C4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
