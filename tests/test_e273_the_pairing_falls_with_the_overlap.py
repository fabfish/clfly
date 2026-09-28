"""`e273` reads the pairing's gain along the overlap axis, so the tests pin the correlation helper, the configuration
check, the leave-one-out rule, both faces of the four claims and the live numbers -- including X4's fired falsifier.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e273_the_pairing_falls_with_the_overlap as e273


def test_the_pearson_helper_and_the_leave_one_out_rule():
    assert abs(e273.pearson([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) - 1.0) < 1e-12
    assert abs(e273.pearson([1.0, 2.0, 3.0], [6.0, 4.0, 2.0]) + 1.0) < 1e-12
    # one replicate can carry the sign: drop the outlier and the correlation turns
    a = [1.0, 2.0, 3.0, 4.0]
    b = [1.0, 2.0, 3.0, -10.0]
    full = e273.pearson(a, b)
    loo = [e273.pearson(a[:i] + a[i + 1:], b[:i] + b[i + 1:]) for i in range(len(a))]
    assert full < 0 < loo[3], (full, loo)
    assert any((x < 0) != (full < 0) for x in loo), (full, loo)


def _art(path: Path, corrs=(0.257, 0.265), n=4, overlap=0.25, arms=("naive", "ewc-block", "ewc-block-rand")):
    a = [0.1, 0.2, 0.3, 0.4][:n]
    payload = {"config": {"input_overlap": overlap, "json_out": path.name, "lam": 1.0, "methods": ",".join(arms)},
               "methods": {x: {"replicates": [{"final_accuracy": v, "mean_forgetting": v} for v in a]}
                           for x in arms},
               "matched_pair": {}}
    for i, metric in enumerate(e273.METRICS):
        payload["matched_pair"][metric] = {"corr": corrs[i], "sem_unpaired": 0.02, "sem_paired": 0.017,
                                          "delta": 0.001}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_the_configuration_check_ignores_the_fields_the_axis_moves(tmp_path):
    one, two = tmp_path / "one.json", tmp_path / "two.json"
    _art(one, overlap=0.25)
    _art(two, overlap=0.75)
    a, b = json.loads(one.read_text(encoding="utf-8")), json.loads(two.read_text(encoding="utf-8"))
    assert e273.config_diff(a, b) == [], "the overlap and the arm list are the axis, not a difference"
    b["config"]["lam"] = 0.1
    assert [k for k, _, _ in e273.config_diff(a, b)] == ["lam"]


def test_the_reading_computes_the_correlation_the_ratio_and_the_leave_one_out(tmp_path):
    p = tmp_path / "a.json"
    _art(p, n=4)
    d = json.loads(p.read_text(encoding="utf-8"))
    r = e273.reading(d, "final_accuracy")
    assert r["n"] == 4 and abs(r["corr"] - 1.0) < 1e-12, r
    assert abs(r["ratio"] - 0.02 / 0.017) < 1e-9, r
    assert not r["loo_flips"] and r["closest_to_zero"] >= 0.0, r


def _rows(vals):
    """Three controlled points plus a fourth, from the three correlations each."""
    out = {}
    for overlap, triple in vals.items():
        out[overlap] = {"artifact": f"{overlap}.json", "diffs": [],
                        "metrics": {m: {"n": 40, "corr": c, "ratio": 1.1, "loo_min": c - 0.1, "loo_max": c + 0.1,
                                       "loo_flips": False, "closest_to_zero": 0.05, "delta": 0.0}
                                    for m, c in zip(e273.METRICS, triple)}}
    return out


def test_the_four_claims_read_both_faces():
    rows = _rows({"0.25": (0.257, 0.265), "0.50": (0.101, 0.164), "0.75": (-0.063, -0.047), "1.00": (0.131, 0.139)})
    for o in ("0.25", "0.50"):
        for m in e273.METRICS:
            rows[o]["metrics"][m]["ratio"] = 1.16
    for m in e273.METRICS:
        rows["0.75"]["metrics"][m]["ratio"] = 0.97
    j = {r["id"]: r for r in e273.judge(rows)}
    for cid in ("X1", "X2", "X3", "X4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a step that rises is X1's falsifier
    bad = _rows({"0.25": (0.1, 0.1), "0.50": (0.2, 0.2), "0.75": (0.3, 0.3), "1.00": (0.4, 0.4)})
    j = {r["id"]: r for r in e273.judge(bad)}
    assert j["X1"]["verdict"].startswith("FALSIFIER FIRED"), j["X1"]
    # a ratio that stays above one is X2's
    j = {r["id"]: r for r in e273.judge(_rows({"0.25": (0.3, 0.3), "0.50": (0.2, 0.2), "0.75": (0.1, 0.1),
                                               "1.00": (0.05, 0.05)}))}
    assert j["X2"]["verdict"].startswith("FALSIFIER FIRED"), j["X2"]
    # a fourth point below the third is X3's, and a flipped leave-one-out is X4's
    j = {r["id"]: r for r in e273.judge(_rows({"0.25": (0.3, 0.3), "0.50": (0.2, 0.2), "0.75": (0.1, 0.1),
                                               "1.00": (0.05, 0.05)}))}
    assert j["X3"]["verdict"].startswith("FALSIFIER FIRED"), j["X3"]
    rows = _rows({"0.25": (0.3, 0.3), "0.50": (0.2, 0.2), "0.75": (0.1, 0.1), "1.00": (0.4, 0.4)})
    rows["0.75"]["metrics"]["final_accuracy"]["loo_flips"] = True
    j = {r["id"]: r for r in e273.judge(rows)}
    assert j["X4"]["verdict"].startswith("FALSIFIER FIRED"), j["X4"]
    assert e273.judge({"0.25": rows["0.25"]})[0]["verdict"].startswith("REFUSED")


def test_the_live_axis_falls_with_the_overlap_and_its_endpoint_is_fragile():
    """The finding's numbers on the artifact: +0.257, +0.101, -0.063 over the controlled points, the ratio crossing
    below one there, the fourth point above the third -- and X4's falsifier firing on a +0.004 leave-one-out."""
    p = Path("runs/e273_the_pairing_falls_with_the_overlap.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    runs = d["runs"]
    assert sorted(runs) == ["0.25", "0.50", "0.75", "1.00"], sorted(runs)
    acc = [runs[o]["metrics"]["final_accuracy"]["corr"] for o in ("0.25", "0.50", "0.75")]
    assert acc[0] > acc[1] > acc[2] and abs(acc[0] - 0.257) < 1e-3 and abs(acc[2] + 0.063) < 1e-3, acc
    ratios = [runs[o]["metrics"]["final_accuracy"]["ratio"] for o in ("0.25", "0.50", "0.75")]
    assert ratios[0] > ratios[1] > ratios[2] and ratios[2] < 1.0, ratios
    assert runs["1.00"]["metrics"]["final_accuracy"]["corr"] > runs["0.75"]["metrics"]["final_accuracy"]["corr"]
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("X1", "X2", "X3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert claims["X4"]["verdict"].startswith("FALSIFIER FIRED"), claims["X4"]
    assert "+0.004" in claims["X4"]["measured"], claims["X4"]
