"""`e327` turns the feedback knob, so the tests pin the two diffs that have to ignore the manipulation, the
ordering statistic with its tolerance, the end-to-end drop, the zero dose's bit-identity, and both faces of the
four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e327_the_feedback_is_a_dose as e327


def test_the_two_diffs_ignore_the_strength_and_nothing_else():
    a = {"config": {"circuit_size": 300, "json_out": "runs/a.json", "loop_scale": 0.0},
         "env_draw": {"scale": 0.0, "n_cue": 12, "cue_sha1": "x"}}
    b = {"config": {"circuit_size": 300, "json_out": "runs/b.json", "loop_scale": 1.0},
         "env_draw": {"scale": 1.0, "n_cue": 12, "cue_sha1": "x"}}
    assert e327.config_diff(a, b) == {}, e327.config_diff(a, b)
    assert e327.env_diff(a, b) == {}, e327.env_diff(a, b)
    # but a different cue draw or a different circuit is a different configuration
    b["env_draw"]["cue_sha1"] = "y"
    b["config"]["circuit_size"] = 800
    assert e327.env_diff(a, b) == {"cue_sha1": ["x", "y"]}, e327.env_diff(a, b)
    assert e327.config_diff(a, b) == {"circuit_size": [300, 800]}, e327.config_diff(a, b)


def _reading(forgetting=(0.044, 0.030, 0.015, 0.000), accuracy=(0.97, 0.98, 0.99, 1.00),
             config_diff=None, env_diff=None, same_circuit=True, same_counts=True, unwired=None,
             scales=(0.0, 0.25, 0.5, 1.0)):
    tags = [t for t, _ in e327.LEVELS]
    per = {tag: [{"final_accuracy": a, "mean_forgetting": f} for _ in range(5)]
           for tag, a, f in zip(tags, accuracy, forgetting)}
    return {"runs": len(tags), "missing": [], "levels": tags, "scales": list(scales),
            "circuits": ["MB"] * len(tags) if same_circuit else ["MB"] * (len(tags) - 1) + ["MB2"],
            "readout": ["abc"] * len(tags),
            "task_names": [["loop_a", "loop_b", "loop_c"]] * len(tags),
            "n_replicates": [5] * len(tags) if same_counts else [5] * (len(tags) - 1) + [4],
            "config_diff": [config_diff or {}] * (len(tags) - 1),
            "env_diff": [env_diff or {}] * (len(tags) - 1),
            "accuracy": list(accuracy), "forgetting": list(forgetting),
            "per_replicate": per,
            "unwired": unwired if unwired is not None else [
                {"final_accuracy": accuracy[0], "mean_forgetting": forgetting[0]} for _ in range(5)]}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e327.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a differing circuit, count, or an unexpected config or environment field
    assert e327.judge(_reading(same_circuit=False))[0]["verdict"].startswith("FALSIFIER")
    assert e327.judge(_reading(same_counts=False))[0]["verdict"].startswith("FALSIFIER")
    assert e327.judge(_reading(config_diff={"loop_gain": [1.0, 2.0]}))[0]["verdict"].startswith("FALSIFIER")
    assert e327.judge(_reading(env_diff={"cue_sha1": ["x", "y"]}))[0]["verdict"].startswith("FALSIFIER")

    # T2: a rise anywhere along the sweep is the falsifier, and one under the tolerance is not
    assert e327.judge(_reading(forgetting=(0.044, 0.060, 0.015, 0.000)))[1]["verdict"].startswith("FALSIFIER")
    assert e327.judge(_reading(forgetting=(0.044, 0.046, 0.045, 0.000)))[1]["verdict"].startswith("MET")
    # T3: a flat sweep is the falsifier and a partial one is the null
    assert e327.judge(_reading(forgetting=(0.044, 0.044, 0.043, 0.042)))[2]["verdict"].startswith("FALSIFIER")
    assert e327.judge(_reading(forgetting=(0.044, 0.040, 0.035, 0.031)))[2]["verdict"].startswith("NULL")
    # T4: the zero dose has to reproduce the unwired run replicate for replicate
    wrong = [{"final_accuracy": 0.97, "mean_forgetting": 0.05} for _ in range(5)]
    assert e327.judge(_reading(unwired=wrong))[3]["verdict"].startswith("FALSIFIER")
    assert e327.judge(_reading(unwired=None))[3]["verdict"].startswith("MET")     # fixture default matches
    short = [{"final_accuracy": 0.97, "mean_forgetting": 0.044}]
    assert e327.judge(_reading(unwired=short))[3]["verdict"].startswith("FALSIFIER")

    # and too few doses refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e327.judge({"runs": 0, "missing": ["runs/x.json"]}))


def test_the_reader_refuses_when_too_few_doses_are_on_disk(tmp_path):
    paths = {tag: tmp_path / f"{tag}.json" for tag, _ in e327.LEVELS}
    paths["0p00"].write_text(json.dumps({"methods": {"naive": {"replicates": []}}}), encoding="utf-8")
    r = e327.reading(paths, unwired=tmp_path / "absent.json")
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e327.judge(r))


def test_the_live_sweep_is_one_configuration_in_four_doses():
    r = e327.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["runs"] == len(e327.LEVELS), r["missing"]
    assert len(set(r["circuits"])) == 1 and len(set(r["readout"])) == 1, (r["circuits"], r["readout"])
    assert len({tuple(n) for n in r["task_names"]}) == 1, r["task_names"]
    assert len(set(r["n_replicates"])) == 1, r["n_replicates"]
    assert not [d for d in r["config_diff"] if d], r["config_diff"]
    assert not [d for d in r["env_diff"] if d], r["env_diff"]
    assert r["scales"] == [0.0, 0.25, 0.5, 1.0], r["scales"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e327_the_feedback_is_a_dose.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e327.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["scales"] == [0.0, 0.25, 0.5, 1.0], d["scales"]
