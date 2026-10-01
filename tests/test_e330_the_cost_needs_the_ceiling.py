"""`e330` takes `e329`'s fork at forty replicates, so the tests pin the paired contrasts and their standard errors,
the three-valued claims, the config comparison, and the headroom check.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e330_the_cost_needs_the_ceiling as e330


def test_the_paired_contrast_reports_its_own_standard_error():
    p = e330.paired([0.5, 0.45, 0.55, 0.4], [0.55, 0.5, 0.6, 0.45])
    assert p["n"] == 4 and abs(p["delta"] + 0.05) < 1e-12, p
    assert p["sem"] < 1e-12, p                     # four identical differences have no spread but for rounding
    assert p["sigma"] > 1e10, p
    # one replicate is not enough for a standard error and is refused rather than estimated
    assert e330.paired([0.5], [0.4])["delta"] is None


def _run(acc, forget, n=40, scale=0.0, seed_spread=0.0):
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_scale": scale, "loop_noise": 1.0,
                       "loop_symbols": 8},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"scale": scale, "noise": 1.0, "n_symbols": 24, "n_cue": 12},
            "tasks": [{"name": n_} for n_ in ("loop_a", "loop_b", "loop_c")],
            "methods": {e330.NAIVE: {"final_accuracy": acc, "mean_forgetting": forget,
                                     "replicates": [{"final_accuracy": acc + seed_spread * (i % 3 - 1),
                                                     "mean_forgetting": forget + seed_spread * (i % 3 - 1)}
                                                    for i in range(n)]}}}


def _reading(open_acc=0.5292, mid_acc=0.4931, open_forget=0.2188, mid_forget=0.2354,
             config_diff=None, env_diff=None, same_tasks=True, counts=True, spread=0.01):
    a, b = _run(open_acc, open_forget, scale=0.0, seed_spread=spread), \
        _run(mid_acc, mid_forget, n=40 if counts else 30, scale=0.5, seed_spread=spread)
    return {"runs": 2, "levels": ["0p00", "0p50"], "scales": [0.0, 0.5],
            "circuits": ["MB", "MB"] if same_tasks else ["MB", "MB2"], "readout": ["abc", "abc"],
            "task_names": [["loop_a"] if same_tasks else ["loop_z"], ["loop_a"]],
            "config_diff": config_diff or {}, "env_diff": env_diff or {},
            "env": {"noise": 1.0, "n_symbols": 24},
            "n": [len(a["methods"][e330.NAIVE]["replicates"]), len(b["methods"][e330.NAIVE]["replicates"])],
            "accuracy": e330.paired([r["final_accuracy"] for r in b["methods"][e330.NAIVE]["replicates"]],
                                    [r["final_accuracy"] for r in a["methods"][e330.NAIVE]["replicates"]]),
            "forgetting": e330.paired([r["mean_forgetting"] for r in b["methods"][e330.NAIVE]["replicates"]],
                                      [r["mean_forgetting"] for r in a["methods"][e330.NAIVE]["replicates"]]),
            "open": {"final_accuracy": open_acc, "mean_forgetting": open_forget},
            "mid": {"final_accuracy": mid_acc, "mean_forgetting": mid_forget},
            "open_spread": {"accuracy_sd": spread, "forgetting_sd": spread},
            "timing_s": [1.0, 1.0]}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e330.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a differing circuit or task name, a differing replicate count, or an unexpected config or env field
    assert e330.judge(_reading(same_tasks=False))[0]["verdict"].startswith("FALSIFIER")
    assert e330.judge(_reading(counts=False))[0]["verdict"].startswith("FALSIFIER")
    assert e330.judge(_reading(config_diff={"loop_noise": [1.0, 0.0]}))[0]["verdict"].startswith("FALSIFIER")
    assert e330.judge(_reading(env_diff={"noise": [1.0, 0.0]}))[0]["verdict"].startswith("FALSIFIER")
    # T2: reading higher is the falsifier, and a small move is the null
    assert e330.judge(_reading(mid_acc=0.60))[1]["verdict"].startswith("FALSIFIER")
    assert e330.judge(_reading(mid_acc=0.52))[1]["verdict"].startswith("NULL")
    # T3: a large forgetting shift is the falsifier and a middling one is the null
    assert e330.judge(_reading(mid_forget=0.30))[2]["verdict"].startswith("FALSIFIER")
    assert e330.judge(_reading(mid_forget=0.27))[2]["verdict"].startswith("NULL")
    # T4: a saturated instrument
    assert e330.judge(_reading(open_acc=0.75))[3]["verdict"].startswith("FALSIFIER")
    assert e330.judge(_reading(open_acc=0.65))[3]["verdict"].startswith("NULL")

    # and one run alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e330.judge({"runs": 1, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_when_one_run_is_missing(tmp_path):
    a = tmp_path / "a.json"
    a.write_text(json.dumps(_run(0.53, 0.22)), encoding="utf-8")
    r = e330.reading({"0p00": a, "0p50": tmp_path / "absent.json"})
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e330.judge(r))


def test_the_live_pair_is_one_configuration_at_two_strengths():
    r = e330.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"][0] == r["task_names"][1], r["task_names"]
    assert not r["config_diff"] and not r["env_diff"], (r["config_diff"], r["env_diff"])
    assert r["scales"] == [0.0, 0.5], r["scales"]
    assert r["n"] == [40, 40], r["n"]
    # the environment is the noisy one `e329` built, not the saturated one `e326` to `e328` ran
    assert r["env"]["noise"] == 1.0 and r["env"]["n_symbols"] == 24, r["env"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e330_the_cost_needs_the_ceiling.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e330.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["n"] == [40, 40], d["n"]
