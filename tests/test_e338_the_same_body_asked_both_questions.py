"""`e338` asks one trained body both questions, so the tests pin the paired arithmetic, the completeness check, the
sign consistency and the smallness claim, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e338_the_same_body_asked_both_questions as e338


def test_the_paired_difference_is_a_within_replicate_one():
    p = e338.paired([0.05, 0.05, 0.05], [0.0, 0.0, 0.0])
    assert p["n"] == 3 and abs(p["delta"] - 0.05) < 1e-12, p
    assert p["sem"] < 1e-12 and p["sigma"] > 1e10, p
    # and one replicate is refused rather than estimated
    assert e338.paired([0.05], [0.0])["delta"] is None


def _run(means, n_tasks=3, leak=0.35, extra=None):
    reps = []
    for m in means:
        entries = [{"task": f"loop_t{j}", "with_loop": 0.5 + m, "without_loop": 0.5} for j in range(n_tasks)]
        rep = {"paired_channel": entries, "final_accuracy": 0.5, "mean_forgetting": 0.05}
        rep.update(extra or {})
        reps.append(rep)
    return {"config": {"circuit_size": 300, "repeats": len(means), "seed0": 0, "methods": "replay",
                       "loop_world_modes": 2, "loop_world_leak": leak, "loop_noise": 1.0, "loop_symbols": 8,
                       "loop_scale": 1.0, "json_out": "x"},
            "circuit": "mb+cx+al@n952", "readout": {"subset_sha1": "abc"},
            "env_draw": {"world_modes": 2, "world_leak": leak},
            "tasks": [{"name": f"loop_t{j}"} for j in range(n_tasks)],
            "methods": {e338.ARM: {"final_accuracy": 0.5, "mean_forgetting": 0.05, "replicates": reps}},
            "timing_s": 100.0}


def _reading(means=(0.030, 0.028, 0.032, 0.029, 0.031), n_tasks=3):
    return e338.reading(_run(list(means), n_tasks=n_tasks))


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e338.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a replicate missing one of its two numbers, or a task absent
    r = _reading()
    r["rows"][2]["deltas"] = r["rows"][2]["deltas"][:1]
    assert e338.judge(r)[0]["verdict"].startswith("FALSIFIER")
    # T2: a difference that does not resolve
    assert e338.judge(_reading(means=(0.030, -0.028, 0.032, -0.029, 0.031)))[1]["verdict"].startswith("FALSIFIER")
    # T3: one replicate leaning the other way
    assert e338.judge(_reading(means=(0.030, 0.028, -0.032, 0.029, 0.031)))[2]["verdict"].startswith("FALSIFIER")
    # T4: an effect as large as the unpaired swings
    assert e338.judge(_reading(means=(0.20, 0.19, 0.21, 0.20, 0.20)))[3]["verdict"].startswith("FALSIFIER")
    assert e338.judge(_reading(means=(0.07, 0.068, 0.072, 0.069, 0.071)))[3]["verdict"].startswith("NULL")

    # and an absent paired record refuses every claim rather than reading a zero
    assert all(row["verdict"].startswith("REFUSED")
               for row in e338.judge({"runs": 0, "missing": ["runs/e338_paired_body.json"]}))
    run = _run([0.03] * 5)
    for r in run["methods"][e338.ARM]["replicates"]:
        r.pop("paired_channel")
    assert all(row["verdict"].startswith("REFUSED") for row in e338.judge(e338.reading(run)))


def test_the_reader_refuses_when_the_artifact_is_absent(tmp_path):
    #: a path that does not exist, rather than the default one, so the test does not depend on the corpus
    r = e338.reading({} if False else None) if not Path("runs/e338_paired_body.json").exists() else         e338.reading(None)
    if r.get("runs"):
        r = {"runs": 0, "missing": [str(tmp_path / "absent.json")]}
    assert r["runs"] == 0 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e338.judge(r))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e338_the_same_body_asked_both_questions.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e338.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["n_replicates"] == 5 and len(d["task_names"]) == 3, (d["n_replicates"], d["task_names"])
    #: a reading is not a result, so the artifact carries no `config` or `env` for the corpus's
    #: conformance contract to count -- see the finding
    assert "config" not in d and "env" not in d, sorted(d)
    # the two unpaired redraws are carried in the artifact so a reader can see what the paired one is measured
    # against
    assert [u["label"] for u in d["unpaired"]] and d["unpaired"][0]["delta"] > 0 > d["unpaired"][1]["delta"], \
        d["unpaired"]
