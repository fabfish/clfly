"""`e285` reads one configuration's two artifacts as a sample-swap experiment: the trained models are the same and
the held-out suite moved. The tests pin the pairing, the field census, the spread arithmetic, both faces of the three
claims and the live partition.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e285_two_runs_one_model as e285


def _art(path: Path, n_eval=144, arms=("naive",), rows=3, held=0.10, other=0.50):
    payload = {"config": {"test": n_eval // 3, "seed0": 0}, "evaluation_noise": {"n_eval": n_eval},
               "timing_s": 10.0, "methods": {}}
    # the held-out fields move with the suite and the others do not, which is the property under test
    shift = n_eval / 1e6
    for a in arms:
        payload["methods"][a] = {"replicates": [
            {"final_accuracy": held + 0.01 * i + shift, "mean_forgetting": held / 2 + 0.01 * i + shift,
             "retention": [held + shift], "final_per_task": [held + shift],
             "forgetting_per_task": [held + shift], "learned": [held + shift],
             "losses": [other, other], "theta_drift": other, "bias_norms": [other],
             "retention_loss": [other], "interference": [other], "full_train_loss": [other], "method": a}
            for i in range(rows)]}
        payload["evaluation_noise"][a] = {"binomial_sem": 0.02}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_pairing_is_by_position_within_an_arm(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _art(a, arms=("naive", "ewc"), rows=3)
    _art(b, arms=("naive", "ewc"), rows=3)
    da = json.loads(a.read_text(encoding="utf-8"))
    db = json.loads(b.read_text(encoding="utf-8"))
    ps = e285.pairs(da, db)
    assert len(ps) == 6, len(ps)
    assert [p[0] for p in ps] == ["ewc"] * 3 + ["naive"] * 3, [p[0] for p in ps]
    # an arm present in one artifact only is not paired
    _art(b, arms=("naive",), rows=3)
    db = json.loads(b.read_text(encoding="utf-8"))
    assert len(e285.pairs(da, db)) == 3


def test_the_census_splits_fields_by_whether_they_moved(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _art(a, n_eval=144)
    _art(b, n_eval=600)
    da = json.loads(a.read_text(encoding="utf-8"))
    db = json.loads(b.read_text(encoding="utf-8"))
    c = e285.field_census(da, db)
    assert set(c) == set(e285.HELD_OUT) | set(e285.NOT_HELD_OUT), sorted(c)
    for f in e285.HELD_OUT:
        assert c[f]["moved"] == c[f]["rows"] == 3, (f, c[f])
    for f in e285.NOT_HELD_OUT:
        assert c[f]["identical"] == c[f]["rows"] == 3, (f, c[f])


def test_the_spread_arithmetic(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    _art(a, n_eval=144, held=0.10)
    _art(b, n_eval=600, held=0.10)
    da = json.loads(a.read_text(encoding="utf-8"))
    db = json.loads(b.read_text(encoding="utf-8"))
    s = e285.spreads(da, db)
    assert set(s) == {"naive/final_accuracy", "naive/mean_forgetting"}, sorted(s)
    v = s["naive/final_accuracy"]
    # the fixture's two samples give the same sd, so the ratio is 1 and W3's falsifier is what that tests
    assert abs(v["sd_ratio"] - 1.0) < 1e-9, v
    assert abs(v["n_eval_ratio"] - 0.49) < 0.01, v
    assert abs(v["variance_ratio"] - 1.0) < 1e-9, v
    assert v["seconds_old"] == 10.0, v


def _reading(cfg=("test", "json_out"), spreads=None, census=None):
    by_default = {f: {"rows": 2, "moved": 2, "identical": 0} for f in e285.HELD_OUT}
    by_default.update({f: {"rows": 2, "moved": 0, "identical": 2} for f in e285.NOT_HELD_OUT})
    return {"census": census or by_default, "config_differences": {k: [1, 2] for k in cfg},
            "spreads": spreads or {"naive/final_accuracy": {"sd_ratio": 0.5}}}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e285.judge(_reading())}
    for cid in ("W1", "W2", "W3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a second substantive flag is W1's falsifier
    j = {r["id"]: r for r in e285.judge(_reading(cfg=("test", "json_out", "seed0")))}
    assert j["W1"]["verdict"].startswith("FALSIFIER FIRED"), j["W1"]
    # a held-out field that stayed, or another field that moved, is W2's
    c = {f: {"rows": 2, "moved": 2, "identical": 0} for f in e285.HELD_OUT}
    c.update({f: {"rows": 2, "moved": 0, "identical": 2} for f in e285.NOT_HELD_OUT})
    c["retention"] = {"rows": 2, "moved": 1, "identical": 1}
    j = {r["id"]: r for r in e285.judge(_reading(census=c))}
    assert j["W2"]["verdict"].startswith("FALSIFIER FIRED"), j["W2"]
    c["retention"] = {"rows": 2, "moved": 2, "identical": 0}
    c["losses"] = {"rows": 2, "moved": 2, "identical": 0}
    j = {r["id"]: r for r in e285.judge(_reading(census=c))}
    assert j["W2"]["verdict"].startswith("FALSIFIER FIRED"), j["W2"]
    # a spread that did not fall is W3's
    s = {"a/final_accuracy": {"sd_ratio": 0.5}, "b/final_accuracy": {"sd_ratio": 1.2}}
    j = {r["id"]: r for r in e285.judge(_reading(spreads=s))}
    assert j["W3"]["verdict"].startswith("FALSIFIER FIRED"), j["W3"]
    assert e285.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e285.judge({"census": None})[0]["verdict"].startswith("REFUSED")


def test_the_live_partition_and_the_live_spreads():
    a, b = e285.load(e285.OLD), e285.load(e285.NEW)
    if a is None or b is None:
        return
    c = e285.field_census(a, b)
    assert set(c) == set(e285.HELD_OUT) | set(e285.NOT_HELD_OUT), sorted(c)
    assert all(c[f]["moved"] == c[f]["rows"] == 200 for f in e285.HELD_OUT), c
    assert all(c[f]["identical"] == c[f]["rows"] == 200 for f in e285.NOT_HELD_OUT), c
    s = e285.spreads(a, b)
    assert len(s) == 10 and all(v["sd_ratio"] < 1 for v in s.values()), s
    lo, hi = min(v["sd_ratio"] for v in s.values()), max(v["sd_ratio"] for v in s.values())
    assert 0.40 <= lo <= 0.45 and 0.75 <= hi <= 0.85, (lo, hi)
    # the candidate account that goes as 1/sqrt(n_eval) is the same for every comparison
    assert all(abs(v["n_eval_ratio"] - 0.49) < 0.01 for v in s.values()), s


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e285_two_runs_one_model.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert sorted(d["config_differences"]) == ["json_out", "test"], d["config_differences"]
    assert d["n_eval_old"] == 144 and d["n_eval_new"] == 600, (d["n_eval_old"], d["n_eval_new"])
    assert d["n_old"] == d["n_new"] == 200, (d["n_old"], d["n_new"])
    for f in d["held_out"]:
        assert d["census"][f]["moved"] == 200, (f, d["census"][f])
    for f in d["not_held_out"]:
        assert d["census"][f]["identical"] == 200, (f, d["census"][f])
    assert len(d["spreads"]) == 10 and all(v["sd_ratio"] < 1 for v in d["spreads"].values()), d["spreads"]
    for cid in ("W1", "W2", "W3"):
        assert {x["id"]: x for x in d["claims"]}[cid]["verdict"].startswith("MET"), cid
