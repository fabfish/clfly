"""`e324` asks what training on a trial with a time axis costs, so the tests pin the paired difference, the
config comparison that keeps the two runs one configuration, the cross-arm ordering contrast, and both faces of
the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e324_what_the_time_axis_costs as e324


def test_paired_is_a_replicate_wise_difference():
    p = e324.paired([0.5, 0.6, 0.7], [0.4, 0.5, 0.6])
    assert p["n"] == 3 and abs(p["delta"] - 0.1) < 1e-12, p
    assert p["sigma"] == float("inf"), p          # three identical differences have no spread
    # one replicate is not enough for a standard error and is refused rather than estimated
    assert e324.paired([0.5], [0.4])["delta"] is None, e324.paired([0.5], [0.4])
    # an unpaired reading would lose the seed structure, so the pairing has to be by index
    assert e324.paired([0.5, 0.6], [0.6, 0.5])["delta"] == 0.0


def test_the_config_diff_ignores_the_builder_and_the_output_path():
    a = {"config": {"circuit_size": 300, "json_out": "runs/a.json", "seed0": 0}}
    b = {"config": {"circuit_size": 300, "json_out": "runs/b.json", "seed0": 0, "sequence": True}}
    assert e324.config_diff(a, b) == {}, e324.config_diff(a, b)
    b["config"]["circuit_size"] = 800
    b["config"]["classes"] = 9
    d = e324.config_diff(a, b)
    assert set(d) == {"circuit_size", "classes"}, d
    assert d["circuit_size"] == [300, 800], d


def _run(acc, forget, n=5, replay_gap=0.1, sigma=4.0, seed_off=0.0):
    methods = {}
    for arm in ("naive", "ewc", "ewc-block", "ewc-block-rand", e324.REPLAY):
        bonus = replay_gap if arm == e324.REPLAY else 0.0
        methods[arm] = {
            "final_accuracy": acc + bonus,
            "mean_forgetting": forget + (0.0 if arm == e324.REPLAY else 0.0),
            "replicates": [{"final_accuracy": acc + bonus + seed_off * i,
                            "mean_forgetting": forget + 0.001 * i} for i in range(n)]}
    return {"config": {"circuit_size": 300, "input_overlap": None}, "circuit": "MB",
            "readout": {"subset_sha1": "abc"}, "tasks": [{"name": "t0"}], "methods": methods}


def _reading(naive_delta=-0.08, naive_forget_delta=0.04, seq_delta=0.1, seq_sigma=4.0,
             config_diff=None, same_readout=True, counts=True):
    n = 5
    a, b = _run(0.5, 0.10, n=n), _run(0.5, 0.10, n=n, seed_off=0.0)
    for arm in b["methods"]:
        b["methods"][arm]["replicates"] = [
            {"final_accuracy": v["final_accuracy"] + naive_delta, "mean_forgetting": v["mean_forgetting"]}
            for v in b["methods"][arm]["replicates"]]
    ordering = {arm: {"sustained": {"n": n, "delta": 0.1, "sem": 0.01, "sigma": 5.0},
                      "sequence": {"n": n, "delta": seq_delta, "sem": 0.01, "sigma": seq_sigma}}
                for arm in e324.PENALTIES}
    return {"runs": 2, "circuits": ["MB", "MB"], "readout": ["abc", "abc" if same_readout else "def"],
            "n_replicates": {arm: [n, n if counts else n + 1] for arm in a["methods"]},
            "config_diff": config_diff if config_diff is not None else {},
            "accuracy": {arm: {"n": n, "delta": naive_delta if arm == e324.NAIVE else 0.0, "sem": 0.01,
                               "sigma": 2.0} for arm in a["methods"]},
            "forgetting": {arm: {"n": n, "delta": naive_forget_delta if arm == e324.NAIVE else 0.0,
                                 "sem": 0.01, "sigma": 2.0} for arm in a["methods"]},
            "ordering": ordering,
            "sustained": {arm: {"final_accuracy": 0.5, "mean_forgetting": 0.1} for arm in a["methods"]},
            "sequence": {arm: {"final_accuracy": 0.5, "mean_forgetting": 0.1} for arm in a["methods"]}}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e324.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a differing config field, a differing read-out draw, or a differing replicate count
    assert e324.judge(_reading(config_diff={"circuit_size": [300, 800]}))[0]["verdict"].startswith("FALSIFIER")
    assert e324.judge(_reading(same_readout=False))[0]["verdict"].startswith("FALSIFIER")
    assert e324.judge(_reading(counts=False))[0]["verdict"].startswith("FALSIFIER")

    # T2: higher is the falsifier, and inside the band is the null
    assert e324.judge(_reading(naive_delta=0.08))[1]["verdict"].startswith("FALSIFIER")
    assert e324.judge(_reading(naive_delta=0.01))[1]["verdict"].startswith("NULL")
    # T3: a penalty arm `replay` does not beat fires, and so does one whose contrast is unresolved
    assert e324.judge(_reading(seq_delta=-0.02))[2]["verdict"].startswith("FALSIFIER")
    assert e324.judge(_reading(seq_sigma=1.0))[2]["verdict"].startswith("FALSIFIER")
    # T4: less forgetting is the falsifier and inside the band is the null
    assert e324.judge(_reading(naive_forget_delta=-0.04))[3]["verdict"].startswith("FALSIFIER")
    assert e324.judge(_reading(naive_forget_delta=0.005))[3]["verdict"].startswith("NULL")

    # and a missing run refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e324.judge({"runs": 0, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_rather_than_reading_one_run(tmp_path):
    a = tmp_path / "a.json"
    a.write_text(json.dumps(_run(0.5, 0.10)), encoding="utf-8")
    r = e324.reading(a, tmp_path / "absent.json")
    assert r["runs"] == 0 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e324.judge(r))


def test_the_live_reading_is_one_configuration_in_two_suits():
    r = e324.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["suites"][0] is None and r["suites"][1] is True, r["suites"]
    assert not r["config_diff"], r["config_diff"]
    assert all(v[0] == v[1] == 5 for v in r["n_replicates"].values()), r["n_replicates"]
    # the sequence suite's names are the sequence family and the sustained one's are the assembly family
    assert all(n.startswith("seq_") for n in r["task_names"]["sequence"]), r["task_names"]
    assert not any(n.startswith("seq_") for n in r["task_names"]["sustained"]), r["task_names"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e324_what_the_time_axis_costs.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e324.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert len(d["ordering"]) == len(e324.PENALTIES), d["ordering"]
