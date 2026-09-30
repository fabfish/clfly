"""`e291` asks what the larger suite did to the configuration's own contrasts, so the tests pin the paired
arithmetic, the consecutive pairing, both faces of the three claims, and the live reading including the one sign the
sample did not keep.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e291_what_the_suite_bought as e291


def _art(path: Path, arms, rows=6, scale=1.0):
    payload = {"evaluation_noise": {"n_eval": 144}, "methods": {a: {"replicates": []} for a in arms}}
    for i in range(rows):
        for j, a in enumerate(arms):
            payload["methods"][a]["replicates"].append(
                {"final_accuracy": 0.5 + 0.01 * j + 0.02 * i * scale,
                 "mean_forgetting": 0.10 - 0.01 * j + 0.005 * i * scale})
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_paired_contrast_is_by_position_over_shared_replicates(tmp_path):
    a = _art(tmp_path / "a.json", ("naive", "ewc"))
    c = e291.contrast(a, "ewc", "naive", "final_accuracy")
    # arm ewc is +0.01 above naive in every replicate, so the difference has no spread and no sem
    assert abs(c["delta"] - 0.01) < 1e-12 and c["sd"] < 1e-12 and c["negative"] == 0, c
    assert c["sigma"] == float("inf"), c
    # a contrast against an arm with fewer replicates pairs only the shared prefix
    b = _art(tmp_path / "b.json", ("naive", "ewc"), rows=3)
    c = e291.contrast(b, "ewc", "naive", "final_accuracy")
    assert c["n"] == 3, c
    # one replicate is not a contrast
    assert e291.contrast({"methods": {"x": {"replicates": [{"final_accuracy": 0.5}]}}},
                         "x", "x", "final_accuracy") is None


def test_the_pairing_is_over_consecutive_suites(tmp_path):
    one = _art(tmp_path / "one.json", ("naive", "ewc"))
    two = _art(tmp_path / "two.json", ("naive", "ewc"), scale=0.4)
    three = _art(tmp_path / "three.json", ("naive", "ewc"), scale=0.2)
    runs = [("144", one), ("600", two), ("1440", three)]
    rows = e291.contrasts(runs)
    assert len(rows) == 6, rows          # two arm pairs, two metrics, three suites
    paired = e291.pair_up(rows, ["144", "600", "1440"])
    assert len(paired) == 4, paired      # two arm pairs, two metrics, two consecutive steps
    assert {x["first"] for x in paired} == {"144", "600"}, paired
    assert {x["second"] for x in paired} == {"600", "1440"}, paired


def _reading(ratios=(2.0, 1.5), flips=(), weak_first=()):
    """A stand-in reading whose resolutions follow from its own sigmas, so the faces cannot be set inconsistently."""
    rows = []
    for i, ratio in enumerate(ratios):
        sf = 1.0 if i in weak_first else 3.0
        ss = sf * ratio
        rows.append({"a": f"arm{i}", "b": "naive", "metric": "final_accuracy", "first": "144", "second": "600",
                     "delta_first": -0.01 if i in flips else 0.01, "delta_second": 0.01,
                     "sigma_first": sf, "sigma_second": ss, "sd_first": 0.02, "sd_second": 0.01,
                     "resolved_first": sf >= 2.0, "resolved_second": ss >= 2.0,
                     "sign_kept": i not in flips, "sigma_ratio": ratio})
    return {"paired": rows, "resolved_by_suite": {"144": sum(1 for r in rows if r["resolved_first"]),
                                                  "600": sum(1 for r in rows if r["resolved_second"])},
            "resolved_first": sum(1 for r in rows if r["resolved_first"]),
            "resolved_second": sum(1 for r in rows if r["resolved_second"])}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e291.judge(_reading())}
    assert j["R1"]["verdict"].startswith("MET"), j["R1"]
    assert j["R2"]["verdict"].startswith("MET"), j["R2"]
    assert j["R3"]["verdict"].startswith("MET"), j["R3"]
    # sigmas that mostly fall are R1's falsifier
    j = {r["id"]: r for r in e291.judge(_reading(ratios=(0.5, 0.4)))}
    assert j["R1"]["verdict"].startswith("FALSIFIER FIRED"), j["R1"]
    # a resolved contrast that lost its resolution is R2's, and its sign did not change
    j = {r["id"]: r for r in e291.judge(_reading(ratios=(0.4, 1.5)))}
    assert j["R2"]["verdict"].startswith("FALSIFIER FIRED"), j["R2"]
    assert j["R3"]["verdict"].startswith("MET"), j["R3"]
    # a resolved contrast whose sign flipped is R2's too
    j = {r["id"]: r for r in e291.judge(_reading(flips=(0,)))}
    assert j["R2"]["verdict"].startswith("FALSIFIER FIRED"), j["R2"]
    assert j["R3"]["verdict"].startswith("FALSIFIER FIRED"), j["R3"]
    # an UNRESOLVED contrast that flips is R3's alone, which is the live case
    j = {r["id"]: r for r in e291.judge(_reading(ratios=(2.0, 0.4), flips=(1,), weak_first=(1,)))}
    assert j["R2"]["verdict"].startswith("MET"), j["R2"]
    assert j["R3"]["verdict"].startswith("FALSIFIER FIRED"), j["R3"]
    assert e291.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e291.judge({"paired": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_reading_is_what_the_finding_says():
    runs = [(label, d) for label, path in e291.SUITES if (d := e291.load(path)) is not None]
    assert len(runs) == 3, [label for label, _ in runs]
    rows = e291.contrasts(runs)
    assert len(rows) == 60, len(rows)                     # ten arm pairs, two metrics, three suites
    assert all(x["suite"] in {"144", "600", "1440"} for x in rows), {x["suite"] for x in rows}
    paired = e291.pair_up(rows, [label for label, _ in runs])
    assert len(paired) == 40, len(paired)                 # ten arm pairs, two metrics, two consecutive steps
    assert {x["first"] for x in paired} == {"144", "600"} and {x["second"] for x in paired} == {"600", "1440"}
    assert sum(1 for x in paired if x["sigma_ratio"] > 1) == 38, [round(x["sigma_ratio"], 2) for x in paired]
    by_suite = {label: sum(1 for x in rows if x["suite"] == label and x["sigma"] >= 2) for label, _ in runs}
    assert by_suite == {"144": 14, "600": 18, "1440": 19}, by_suite
    flips = [x for x in paired if not x["sign_kept"]]
    assert len(flips) == 2 and {(x["a"], x["b"], x["metric"]) for x in flips} == {
        ("ewc", "replay", "mean_forgetting")}, flips
    assert all(x["sigma_first"] < 2 and x["sigma_second"] < 2 for x in flips), flips
    assert {(x["first"], x["second"]) for x in flips} == {("144", "600"), ("600", "1440")}, flips
    # and the resolved ones are the ones that kept their sign
    assert all(x["sign_kept"] for x in paired if x["resolved_first"])


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e291_what_the_suite_bought.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["n_suites"] == 3 and len(d["paired"]) == 40, (d["n_suites"], len(d["paired"]))
    assert d["resolved_by_suite"] == {"144": 14, "600": 18, "1440": 19}, d["resolved_by_suite"]
    claims = {x["id"]: x for x in d["claims"]}
    assert claims["R1"]["verdict"].startswith("MET"), claims["R1"]
    assert claims["R2"]["verdict"].startswith("MET"), claims["R2"]
    assert claims["R3"]["verdict"].startswith("FALSIFIER FIRED"), claims["R3"]
    assert "ewc - replay on mean_forgetting" in claims["R3"]["measured"], claims["R3"]
