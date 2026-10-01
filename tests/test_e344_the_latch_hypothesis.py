"""`e344` asks whether the channel helps because the task needs holding, so the tests pin the paired reading in
both conditions, the one-field difference between them, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e344_the_latch_hypothesis as e344


def _run(delta, cue_at=0, n=5, seed=0, readout="r1", leak=0.35, with_step=0.001, without_step=0.0, base=0.5):
    reps = []
    for i in range(n):
        #: the two sides carry **different** alternating spreads, so a paired difference scatters around zero
        #: rather than forming a ramp, and its standard error is finite
        wobble = (i % 3) - 1
        entries = [{"task": f"loop_t{j}", "with_loop": base + delta + with_step * wobble,
                    "without_loop": base + without_step * wobble} for j in range(3)]
        reps.append({"paired_channel": entries, "final_accuracy": base, "mean_forgetting": 0.05})
    return {"config": {"circuit_size": 300, "repeats": n, "train": 96, "test": 48, "readout_size": 32,
                       "seed0": seed, "readout_seed": seed, "loop_seed": seed, "loop_scale": 1.0,
                       "loop_noise": 1.0, "loop_symbols": 2, "loop_world_modes": 2},
            "circuit": "mb+cx+al@n952", "readout": {"subset_sha1": readout},
            "env_draw": {"world_leak": leak, "world_modes": 2, "cue_at": cue_at, "cue_sha1": "c",
                         "action_sha1": "a", "feedback_sha1": "f"},
            "tasks": [{"name": f"loop_t{j}", "n_classes": 2} for j in range(3)],
            "methods": {e344.ARM: {"final_accuracy": base, "mean_forgetting": 0.05, "replicates": reps}},
            "timing_s": 1.0}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _paths(memory=0.08, none=0.0, near=0.0, **kw):
    return {"memory": _write(_run(memory, cue_at=0, **kw)),
            "none": _write(_run(none, cue_at=11, **kw)),
            "near": _write(_run(near, cue_at=10, **kw))}


def test_the_five_claims_read_both_faces():
    j = {row["id"]: row for row in e344.judge(e344.reading(_paths(base=0.9)))}
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: the runs differing in something other than `cue_at` -- here the read-out draw
    moved = e344.reading({"memory": _write(_run(0.08, cue_at=0, base=0.9)),
                          "none": _write(_run(0.0, cue_at=11, base=0.9)),
                          "near": _write(_run(0.0, cue_at=10, base=0.9, readout="r2"))})
    assert e344.judge(moved)[0]["verdict"].startswith("FALSIFIER")
    # T1: and two conditions sharing a `cue_at`, which is no contrast at all
    same = e344.reading({"memory": _write(_run(0.08, cue_at=0, base=0.9)),
                         "none": _write(_run(0.0, cue_at=0, base=0.9)),
                         "near": _write(_run(0.0, cue_at=10, base=0.9))})
    assert e344.judge(same)[0]["verdict"].startswith("FALSIFIER")
    # T2: no help where the cue must be held
    assert e344.judge(e344.reading(_paths(base=0.9, memory=0.0)))[1]["verdict"].startswith("FALSIFIER")
    # T2: help in the wrong direction is not help
    assert e344.judge(e344.reading(_paths(base=0.9, memory=-0.08)))[1]["verdict"].startswith("FALSIFIER")
    # T2: a positive effect smaller than two sigma is unresolved
    assert e344.judge(e344.reading(_paths(base=0.9, memory=0.05, with_step=0.1)))[1]["verdict"].startswith("FALSIFIER")
    # T3: the channel moving the answer with nothing to hold, its falsifier, and the null between
    assert e344.judge(e344.reading(_paths(base=0.9, none=0.10)))[2]["verdict"].startswith("FALSIFIER")
    assert e344.judge(e344.reading(_paths(base=0.9, none=0.035)))[2]["verdict"].startswith("NULL")
    # T4: no difference, the latch's death; and a difference too small to call
    dead = e344.judge(e344.reading(_paths(base=0.9, memory=0.0, none=0.0)))
    assert dead[3]["verdict"].startswith("FALSIFIER"), dead[3]
    assert e344.judge(e344.reading(_paths(base=0.9, memory=0.02, none=0.0)))[3]["verdict"].startswith("NULL")
    # T5: a corrected control that is at chance cannot carry the claim -- this is the `cue_at = 11` failure again
    assert e344.judge(e344.reading(_paths(base=0.5, near=0.0)))[4]["verdict"].startswith("REFUSED")
    # T5: and where it is learnable, a channel that helps is the falsifier and a small one is the null
    assert e344.judge(e344.reading(_paths(base=0.9, near=0.10)))[4]["verdict"].startswith("FALSIFIER")
    assert e344.judge(e344.reading(_paths(base=0.9, near=0.035)))[4]["verdict"].startswith("NULL")

    # a condition missing refuses every claim
    partial = e344.reading({"memory": _write(_run(0.08, cue_at=0, base=0.9))})
    assert all(row["verdict"].startswith("REFUSED") for row in e344.judge(partial)), e344.judge(partial)


def test_the_paired_reading_averages_over_tasks_then_replicates():
    r = e344.condition_reading(_run(0.05, cue_at=0, with_step=0.0, without_step=0.0), "memory")
    assert r["ok"] and r["n"] == 5 and len(r["rows"][0]["deltas"]) == 3, r
    assert abs(r["mean"]["delta"] - 0.05) < 1e-12, r["mean"]
    # the three tasks share a body, so the paired mean's standard error is the across-replicate one
    assert r["mean"]["n"] == 5, r["mean"]
    # and a replicate with no paired record makes the condition unreadable rather than empty
    bad = _run(0.05, cue_at=0)
    bad["methods"][e344.ARM]["replicates"][0].pop("paired_channel")
    assert not e344.condition_reading(bad, "memory")["ok"]
    # one replicate is refused rather than estimated
    assert e344.paired([0.1], [0.0])["delta"] is None


def test_the_reader_refuses_when_a_condition_is_missing():
    r = e344.reading({"memory": _write(_run(0.08, cue_at=0))})
    assert r["missing"] == ["none", "near"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e344.judge(r))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e344_the_latch_hypothesis.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e344.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the contrast is one integer, so the conditions on disk differ in `cue_at` and nothing else
    assert [c["cue_at"] for c in d["conditions"]] == [at for _, at in e344.CONDITIONS], d["conditions"]
    assert d["conditions"][0]["settings"] == d["conditions"][1]["settings"], d["conditions"]
    assert d["conditions"][0]["populations"] == d["conditions"][1]["populations"], d["conditions"]
    #: the late cue measured a floor, which is the reason the corrected control exists at all
    assert min(c["with_loop_mean"] for c in d["conditions"]) < 0.6, d["conditions"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
