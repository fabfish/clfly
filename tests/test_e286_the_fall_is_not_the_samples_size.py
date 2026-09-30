"""`e286` extends `e285` by finding the other two sample swaps the corpus held and using the three as a designed test,
so the tests pin the weak rule's over-admission, the strong rule's selection, both faces of the four claims, and the
live ordering that refutes the sample-size account.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e286_the_fall_is_not_the_samples_size as e286


def _art(path: Path, n_eval=144, arms=("naive",), rows=6, held=0.10, shift=0.0, losses=(1.0, 0.5), shape=None):
    payload = {"config": dict({"circuit_size": 800, "train": 96, "seed0": 0, "methods": "naive"}, **(shape or {})),
               "evaluation_noise": {"n_eval": n_eval}, "timing_s": 10.0,
               "readout": {"subset_sha1": "abc"}, "methods": {}}
    for a in arms:
        payload["methods"][a] = {"replicates": [
            {"final_accuracy": held + 0.01 * i + shift, "mean_forgetting": held / 2 + 0.01 * i + shift,
             "losses": list(losses), "theta_drift": 0.5, "bias_norms": [0.5], "retention_loss": [0.5],
             "interference": [0.5], "full_train_loss": [0.5], "method": a}
            for i in range(rows)]}
        payload["evaluation_noise"][a] = {"binomial_sem": 0.02}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_shape_key_ignores_a_flag_one_side_does_not_have(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _art(a, shape={"support_seed": 0})
    _art(b, shape={})
    da, db = e286.load(a), e286.load(b)
    assert e286.shape_of(da) == e286.shape_of(db), e286.shape_of(da)
    # ... and reports it rather than hiding it
    assert e286.unrecorded_blocks(da, db)["config_keys"] == ["support_seed"], e286.unrecorded_blocks(da, db)
    # a shape field that differs is not tolerated
    _art(b, shape={"circuit_size": 300})
    assert e286.shape_of(da) != e286.shape_of(e286.load(b))


def test_the_weak_rule_admits_and_the_strong_one_selects(tmp_path):
    a, b, c = tmp_path / "small.json", tmp_path / "big.json", tmp_path / "other.json"
    _art(a, n_eval=144)
    _art(b, n_eval=1440, shift=0.001)          # the same training, a different sample: a swap
    _art(c, n_eval=1440, shift=0.001, losses=(1.0, 0.4))   # the training moved: not a swap
    cands = e286.candidates(tmp_path, minimum_replicates=5)
    assert len(cands) == 2, [(x["old"], x["new"]) for x in cands]
    swaps = [x for x in cands if x["swap"]]
    assert len(swaps) == 1 and swaps[0]["new"].endswith("big.json"), swaps
    assert swaps[0]["replicates"] == 6 and swaps[0]["size_ratio"] == 10.0, swaps[0]
    assert len(e286.comparisons(swaps[0])) == 2, e286.comparisons(swaps[0])
    assert e286.training_identical(e286.load(a), e286.load(b))["naive"]["identical"] is True
    assert e286.training_identical(e286.load(a), e286.load(c))["naive"]["identical"] is False


def _reading(cands=28, pairs=3, comparisons=None, corr=None):
    comparisons = comparisons or [
        {"pair": "a -> b", "arm": "naive", "metric": "final_accuracy", "n_old": 144, "n_new": 1440,
         "size_ratio": 10.0, "sd_old": 0.02, "sd_new": 0.017, "mean_old": 0.9, "mean_new": 0.91,
         "observed": 0.85, "sample_prediction": 0.316, "ceiling_prediction": 1.05},
        {"pair": "a -> c", "arm": "naive", "metric": "final_accuracy", "n_old": 144, "n_new": 600,
         "size_ratio": 4.17, "sd_old": 0.02, "sd_new": 0.011, "mean_old": 0.9, "mean_new": 0.92,
         "observed": 0.55, "sample_prediction": 0.490, "ceiling_prediction": 0.93},
        {"pair": "a -> c", "arm": "ewc", "metric": "mean_forgetting", "n_old": 144, "n_new": 600,
         "size_ratio": 4.17, "sd_old": 0.02, "sd_new": 0.012, "mean_old": 0.01, "mean_new": 0.02,
         "observed": 0.60, "sample_prediction": 0.490, "ceiling_prediction": 1.30},
    ]
    return {"n_candidates": cands, "pairs": [{}] * pairs, "comparisons": comparisons}


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e286.judge(_reading())}
    for cid in ("X1", "X2", "X3", "X4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a weak rule that admits nothing the strong rule rejects is X1's falsifier
    j = {r["id"]: r for r in e286.judge(_reading(cands=3, pairs=3))}
    assert j["X1"]["verdict"].startswith("FALSIFIER FIRED"), j["X1"]
    # an sd that did not fall is X2's
    c = _reading()["comparisons"]
    c[0]["observed"] = 1.2
    j = {r["id"]: r for r in e286.judge(_reading(comparisons=c))}
    assert j["X2"]["verdict"].startswith("FALSIFIER FIRED"), j["X2"]
    # the ten-times pairs falling FURTHER than the account predicts is what X3 tests for, so a set where they fall
    # less -- a positive correlation between prediction and observation -- is X3's falsifier
    c = _reading()["comparisons"]
    c[0]["observed"], c[1]["observed"], c[2]["observed"] = 0.2, 0.6, 0.7
    assert e286.correlation([x["sample_prediction"] for x in c], [x["observed"] for x in c]) > 0
    j = {r["id"]: r for r in e286.judge(_reading(comparisons=c))}
    assert j["X3"]["verdict"].startswith("FALSIFIER FIRED"), j["X3"]
    # a spread that rose where p(1-p) rose is X4's
    c[2]["observed"] = 1.1
    j = {r["id"]: r for r in e286.judge(_reading(comparisons=c))}
    assert j["X4"]["verdict"].startswith("FALSIFIER FIRED"), j["X4"]
    assert e286.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e286.judge({"comparisons": []})[0]["verdict"].startswith("REFUSED")
    # an undefined ceiling prediction (a metric whose mean crosses zero) is not a signed case
    j = {r["id"]: r for r in e286.judge(_reading(comparisons=[dict(_reading()["comparisons"][2],
                                                                   ceiling_prediction=None)]))}
    assert j["X4"]["verdict"].startswith("FALSIFIER FIRED"), j["X4"]


def test_the_live_pairs_and_the_account_the_third_suite_refuted():
    cands = e286.candidates(minimum_replicates=5)
    swaps = [c for c in cands if c["swap"]]
    assert len(swaps) >= 5, [(Path(c["old"]).name, Path(c["new"]).name) for c in swaps]
    assert len(cands) > len(swaps), "the weak rule over-admits, which is X1"
    names = {(Path(c["old"]).name, Path(c["new"]).name) for c in swaps}
    assert ("e115_r300_40reps.json", "e119_r300_test480.json") in names, names
    assert ("e116_r128_40reps.json", "e119_r128_test480.json") in names, names
    assert ("e140_r32_methods_frozenbias_40reps.json", "e275_frozenbias_suite600_40reps.json") in names, names
    # the third suite of that configuration is the same experiment one step further out, and not a second copy of
    # `e275`: `e301` drops the corpus's second executions and keeps both suite sizes
    assert ("e140_r32_methods_frozenbias_40reps.json", "e287_frozenbias_suite1440_40reps.json") in names, names
    assert all(c["replicates"] == 40 for c in swaps), [c["replicates"] for c in swaps]
    rows = [x for c in swaps for x in e286.comparisons(c)]
    assert len(rows) >= 34 and max(x["observed"] for x in rows) < 1.2, len(rows)
    # the ten-times pairs no longer move the least: the observation now tracks the 1/sqrt(n_eval) account, which is
    # X3's registered falsifier, and one comparison at the third suite rises -- X2's
    pred = [x["sample_prediction"] for x in rows]
    obs = [x["observed"] for x in rows]
    assert e286.correlation(pred, obs) >= 0, e286.correlation(pred, obs)
    assert any(x["observed"] > 1 for x in rows), [round(x["observed"], 3) for x in rows]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e286_the_fall_is_not_the_samples_size.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["n_candidates"] > len(d["pairs"]) >= 5, (d["n_candidates"], len(d["pairs"]))
    assert len(d["comparisons"]) >= 34, len(d["comparisons"])
    assert all(c["observed"] < 1.2 for c in d["comparisons"]), d["comparisons"]
    signed = [c for c in d["comparisons"] if (c["ceiling_prediction"] or 0) > 1]
    assert len(signed) >= 6, signed
    claims = {x["id"]: x for x in d["claims"]}
    assert claims["X1"]["verdict"].startswith("MET"), claims["X1"]
    for cid in ("X2", "X3", "X4"):
        assert claims[cid]["verdict"].startswith("FALSIFIER FIRED"), claims[cid]
