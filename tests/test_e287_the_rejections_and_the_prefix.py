"""`e287` reads what `e286`'s pairing rule discarded and corrects one sentence of its prose, so the tests pin the
key comparison, the prefix rule, the interval arithmetic, both faces of the three claims, and the live table.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e286_the_fall_is_not_the_samples_size as e286
from experiments import e287_the_rejections_and_the_prefix as e287


def _art(path: Path, n_eval=144, rows=5, shift=0.0, losses=(1.0, 0.5), shape=None):
    payload = {"config": dict({"circuit_size": 800, "train": 96, "seed0": 0, "methods": "naive"}, **(shape or {})),
               "evaluation_noise": {"n_eval": n_eval}, "timing_s": 1.0, "methods": {}}
    payload["methods"]["naive"] = {"replicates": [
        {"final_accuracy": 0.9 + 0.01 * i + shift, "mean_forgetting": 0.02 + 0.001 * i + shift,
         "losses": list(losses), "theta_drift": 0.5, "bias_norms": [0.5], "retention_loss": [0.5],
         "interference": [0.5], "full_train_loss": [0.5], "method": "naive"}
        for i in range(rows)]}
    payload["evaluation_noise"]["naive"] = {"binomial_sem": 0.02}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_key_comparison_splits_recorded_from_unrecorded(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _art(a, shape={"repeats": 5})
    _art(b, shape={"repeats": 40, "support_seed": 0})
    d = e287.differing_keys(e286.load(a), e286.load(b))
    assert d["recorded"] == ["repeats"] and d["unrecorded"] == ["support_seed"], d
    # the manipulation and the output path are not differences
    _art(b, shape={"repeats": 5, "test": 200, "json_out": "runs/x.json"})
    assert e287.differing_keys(e286.load(a), e286.load(b)) == {"recorded": [], "unrecorded": []}


def test_the_prefix_pairs_what_the_full_list_refuses(tmp_path):
    a, b = tmp_path / "five.json", tmp_path / "forty.json"
    _art(a, rows=5)
    _art(b, n_eval=1440, rows=40, shift=0.01)
    da, db = e286.load(a), e286.load(b)
    # the full-list rule refuses a length mismatch ...
    assert all(not t["identical"] for t in e286.training_identical(da, db).values())
    # ... and the prefix rule pairs the five that line up
    pre = e287.prefix_identical(da, db)
    assert pre["naive"] == {"prefix": 5, "identical": True, "len_old": 5, "len_new": 40}, pre
    _art(b, rows=40, shift=0.01, losses=(1.0, 0.4))
    assert e287.prefix_identical(da, e286.load(b))["naive"]["identical"] is False


def test_the_interval_arithmetic():
    lo, hi = e287.f_interval(1.0, 4)
    assert lo < 1 < hi, (lo, hi)
    assert abs(hi / lo - 9.60452988472286 ** 2) < 1e-3, (lo, hi)
    # a variance ratio of one is never resolved; a big fall resolves with few replicates and a mild one needs many
    assert e287.replicates_for(1.0) is None
    assert e287.replicates_for(0.64) == 80, e287.replicates_for(0.64)
    assert e287.replicates_for(0.01) < e287.replicates_for(0.64), e287.replicates_for(0.01)


def _reading(keys=None, prefix_pairs=1, comparisons=None):
    comparisons = comparisons or [{"pair": "a -> b", "arm": "naive", "metric": "final_accuracy", "prefix": 5,
                                   "size_ratio": 10.0, "variance_ratio": 0.9, "sd_ratio": 0.95,
                                   "interval": [0.09, 8.6], "resolved": False}]
    return {"n_candidates": 28, "n_swaps": 3, "n_rejected": 25,
            "rejection_keys": keys if keys is not None else {"repeats": 24, "readout_seed": 4},
            "prefix_pairs": [{"old": f"o{i}.json", "new": "n.json", "comparisons": comparisons}
                             for i in range(prefix_pairs)],
            "prefix_comparisons": comparisons, "f_critical_df4": 9.6045}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e287.judge(_reading())}
    for cid in ("Y1", "Y2", "Y3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # repeats in a minority is Y1's falsifier
    j = {r["id"]: r for r in e287.judge(_reading(keys={"repeats": 4, "readout_seed": 21}))}
    assert j["Y1"]["verdict"].startswith("FALSIFIER FIRED"), j["Y1"]
    # no prefix pair is Y2's
    j = {r["id"]: r for r in e287.judge(_reading(prefix_pairs=0))}
    assert j["Y2"]["verdict"].startswith("FALSIFIER FIRED"), j["Y2"]
    # a resolved comparison is Y3's
    c = [dict(x) for x in _reading()["prefix_comparisons"]]
    c[0]["resolved"], c[0]["interval"] = True, [1.2, 8.6]
    j = {r["id"]: r for r in e287.judge(_reading(comparisons=c))}
    assert j["Y3"]["verdict"].startswith("FALSIFIER FIRED"), j["Y3"]
    assert e287.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e287.judge({"rejection_keys": {}})[0]["verdict"].startswith("REFUSED")


def test_the_live_rejections_and_prefixes_are_what_the_finding_says():
    r = e287.reading(minimum_replicates=5)
    assert (r["n_candidates"], r["n_swaps"], r["n_rejected"]) == (28, 3, 25), (r["n_candidates"], r["n_swaps"])
    assert r["rejection_keys"]["repeats"] == 24, r["rejection_keys"]
    assert len(r["prefix_pairs"]) == 3, [p["old"] for p in r["prefix_pairs"]]
    assert all(p["prefix"] == 5 and p["size_ratio"] == 10.0 for p in r["prefix_pairs"]), r["prefix_pairs"]
    rows = r["prefix_comparisons"]
    assert len(rows) == 6 and all(not x["resolved"] for x in rows), rows
    assert all(x["interval"][0] < 1 < x["interval"][1] for x in rows), rows
    assert abs(r["f_critical_df4"] - 9.6045) < 1e-3 and r["needed_for_the_measured_fall"] == 80, r


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e287_the_rejections_and_the_prefix.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["n_rejected"] == 25 and d["rejection_keys"]["repeats"] == 24, d["rejection_keys"]
    assert len(d["prefix_pairs"]) == 3 and len(d["prefix_comparisons"]) == 6, len(d["prefix_comparisons"])
    assert all(not x["resolved"] for x in d["prefix_comparisons"]), d["prefix_comparisons"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("Y1", "Y2", "Y3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
