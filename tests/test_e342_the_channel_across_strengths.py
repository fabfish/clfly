"""`e342` asks the dissociation across strengths, so the tests pin the paired reading, the four-strength config
comparison, the growth and divergence claims, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e342_the_channel_across_strengths as e342


def _run(scale, delta, n=5, seed=0, readout="r1", leak=0.35, with_step=0.001, without_step=0.0):
    reps = []
    for i in range(n):
        #: the two sides carry **different** alternating spreads, so a paired difference scatters around zero
        #: rather than forming a ramp, and its standard error is finite
        wobble = (i % 3) - 1
        entries = [{"task": f"loop_t{j}", "with_loop": 0.5 + delta + with_step * wobble,
                    "without_loop": 0.5 + without_step * wobble} for j in range(3)]
        reps.append({"paired_channel": entries, "final_accuracy": 0.5, "mean_forgetting": 0.05})
    return {"config": {"circuit_size": 300, "repeats": n, "train": 96, "test": 48, "readout_size": 32,
                       "seed0": seed, "readout_seed": seed, "loop_seed": seed, "loop_scale": scale,
                       "loop_noise": 1.0, "loop_symbols": 8, "loop_world_modes": 2},
            "circuit": "mb+cx+al@n952", "readout": {"subset_sha1": readout},
            "env_draw": {"world_leak": leak, "world_modes": 2, "cue_sha1": "c", "action_sha1": "a",
                         "feedback_sha1": "f"},
            "tasks": [{"name": f"loop_t{j}"} for j in range(3)],
            "methods": {e342.ARM: {"final_accuracy": 0.5, "mean_forgetting": 0.05, "replicates": reps}},
            "timing_s": 1.0}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _paths(deltas=(0.0, 0.0, 0.0, 0.0), **kw):
    return {tag: _write(_run(scale, d, **kw)) for (tag, scale), d in zip(e342.SCALES, deltas)}


_FROZEN = {"circuit": "MB", "size": 300, "readout": 32,
           "scales": {"0.5": {"peak": 1.0, "divergence": 0.19, "divergence_of_peak": 0.19,
                              "readout_divergence_of_peak": 0.045},
                      "4": {"peak": 1.0, "divergence": 0.85, "divergence_of_peak": 0.85,
                            "readout_divergence_of_peak": 0.198}},
           "rise": 0.66, "rise_on_the_readout": 0.153}


def test_the_four_claims_read_both_faces():
    r = e342.reading(_paths(), frozen=False)
    r["frozen"] = dict(_FROZEN)
    j = {row["id"]: row for row in e342.judge(r)}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: two strengths the same, or a setting differing
    same_scale = _paths()
    same_scale["40"] = e342.PATHS["40"]      # absent, but the tag order is what matters
    r2 = e342.reading({**same_scale, "40": _write(_run(2.0, 0.0))}, frozen=False)
    r2["frozen"] = dict(_FROZEN)
    assert e342.judge(r2)[0]["verdict"].startswith("FALSIFIER")
    # T2: one strength resolved away from zero
    grown = e342.reading(_paths(deltas=(0.0, 0.0, 0.0, 0.20)), frozen=False)
    grown["frozen"] = dict(_FROZEN)
    assert e342.judge(grown)[1]["verdict"].startswith("FALSIFIER")
    # T3: the magnitude growing with the strength
    assert e342.judge(grown)[2]["verdict"].startswith("FALSIFIER")
    # T4: a state that barely moves
    flat = e342.reading(_paths(), frozen=False)
    flat["frozen"] = {**_FROZEN, "rise": 0.005}
    assert e342.judge(flat)[3]["verdict"].startswith("FALSIFIER")
    near = e342.reading(_paths(), frozen=False)
    near["frozen"] = {**_FROZEN, "rise": 0.05}
    assert e342.judge(near)[3]["verdict"].startswith("NULL")

    # a strength missing refuses every claim
    partial = e342.reading({tag: _write(_run(s, 0.0)) for tag, s in e342.SCALES[:3]}, frozen=False)
    assert all(row["verdict"].startswith("REFUSED") for row in e342.judge(partial)), e342.judge(partial)


def test_the_paired_reading_averages_over_tasks_then_replicates():
    r = e342.run_reading(_run(1.0, 0.05, with_step=0.0, without_step=0.0), "10")
    assert r["ok"] and r["n"] == 5 and len(r["rows"][0]["deltas"]) == 3, r
    assert abs(r["mean"]["delta"] - 0.05) < 1e-12, r["mean"]
    # the three tasks share a body, so the paired mean's standard error is the across-replicate one
    assert r["mean"]["n"] == 5, r["mean"]
    # and a replicate with no paired record makes the run unreadable rather than empty
    bad = _run(1.0, 0.05)
    bad["methods"][e342.ARM]["replicates"][0].pop("paired_channel")
    assert not e342.run_reading(bad, "10")["ok"]
    # one replicate is refused rather than estimated
    assert e342.paired([0.1], [0.0])["delta"] is None


def test_the_reader_refuses_when_a_strength_is_missing(tmp_path):
    r = e342.reading({"05": _write(_run(0.5, 0.0))}, frozen=False)
    assert r["runs"] == 2 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e342.judge(r))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e342_the_channel_across_strengths.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e342.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert [s["scale"] for s in d["strengths"]] == [s for _, s in e342.SCALES], d["strengths"]
    #: the positive control is part of the artifact: the state's divergence has to grow with the strength
    assert d["frozen"]["rise"] > 0, d["frozen"]
    assert (d["frozen"]["scales"]["4"]["divergence_of_peak"]
            > d["frozen"]["scales"]["0.5"]["divergence_of_peak"]), d["frozen"]
    #: a reading is not a result, so the artifact carries no `config` or `env` for the corpus's contract to count
    assert "config" not in d and "env" not in d, sorted(d)
