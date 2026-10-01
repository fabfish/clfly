"""`e340` builds the clean seed-stream pair, so the tests pin the fingerprint comparison, the sign and size
checks, the gap against the confounded pair, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e340_the_clean_seed_stream as e340


def _world(forget, seed0=0, readout="r1", cue="c1", env_seed=None, n=5, settings=None):
    return {"config": dict({"circuit_size": 300, "repeats": n, "train": 96, "test": 48, "readout_size": 32,
                            "seed0": seed0, "readout_seed": 0 if env_seed is not None else None,
                            "loop_seed": env_seed, "loop_scale": 1.0, "loop_noise": 1.0, "loop_symbols": 8,
                            "loop_world_modes": 2, "loop_world_leak": 1.0}, **(settings or {})),
            "circuit": "mb+cx+al@n952", "readout": {"subset_sha1": readout},
            "env_draw": {"cue_sha1": cue, "action_sha1": "a", "feedback_sha1": "f", "tau": 12, "n_symbols": 24},
            "tasks": [{"name": "loop_t"}],
            "methods": {e340.ARM: {"final_accuracy": 0.6, "mean_forgetting": forget,
                                   "replicates": [{"final_accuracy": 0.6,
                                                   "mean_forgetting": forget + 0.002 * i} for i in range(n)]}},
            "timing_s": 1.0}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _reading(clean=(0.0, 0.0375), second=(0.0, 0.0167), confounded=(0.0, -0.0771),
             seed0=4, cue="c1", readout="r1"):
    """Each world is given as (``without the loop``, ``with it``) so the difference is the delta."""
    streams = {
        "clean, seed0=0": (_write(_world(clean[0], seed0=0, readout="r1", cue="c1")),
                           _write(_world(clean[1], seed0=0, readout="r1", cue="c1"))),
        "clean, seed0=4": (_write(_world(second[0], seed0=seed0, readout=readout, cue=cue, env_seed=0)),
                           _write(_world(second[1], seed0=seed0, readout=readout, cue=cue, env_seed=0))),
    }
    conf = {"instant": _write(_world(confounded[0], seed0=4, readout="r9", cue="c9")),
            "carry": _write(_world(confounded[1], seed0=4, readout="r9", cue="c9"))}
    return e340.reading(streams, conf)


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e340.judge(_reading())}
    for cid in ("T1", "T2", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    #: the default fixture is the measured shape: the clean size is **0.45x** stream 0's, which is the registered
    #: null and not a MET -- the band is a factor of two wide and the observed factor is 2.2
    assert j["T3"]["verdict"].startswith("NULL"), j["T3"]

    # T1: a differing cue or read-out, or two streams sharing a seed
    assert e340.judge(_reading(cue="c2"))[0]["verdict"].startswith("FALSIFIER")
    assert e340.judge(_reading(readout="r2"))[0]["verdict"].startswith("FALSIFIER")
    assert e340.judge(_reading(seed0=0))[0]["verdict"].startswith("FALSIFIER")
    # T2: the opposite sign on the clean stream
    assert e340.judge(_reading(second=(0.0, -0.0167)))[1]["verdict"].startswith("FALSIFIER")
    # T3: an order of magnitude smaller
    assert e340.judge(_reading(second=(0.0, 0.0037)))[2]["verdict"].startswith("FALSIFIER")
    assert e340.judge(_reading(second=(0.0, 0.0120)))[2]["verdict"].startswith("NULL")
    # T4: a confounded pair that agrees with the clean one
    assert e340.judge(_reading(confounded=(0.0, 0.0167)))[3]["verdict"].startswith("FALSIFIER")

    # and a missing stream refuses every claim
    r = _reading()
    r["streams"]["clean, seed0=4"] = {"ok": False}
    assert all(row["verdict"].startswith("REFUSED") for row in e340.judge(r)), e340.judge(r)


def test_the_reader_refuses_when_a_stream_is_incomplete(tmp_path):
    r = e340.reading({"clean, seed0=0": (_write(_world(0.0)), tmp_path / "absent.json")}, {})
    assert r["runs"] < 4 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e340.judge(r))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e340_the_clean_seed_stream.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e340.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the point of the unit: the clean stream carries the same two draws as `e333`'s
    assert d["streams"]["clean, seed0=0"]["readout"][0] == d["streams"]["clean, seed0=4"]["readout"][0]
    assert (d["streams"]["clean, seed0=0"]["populations"]["cue_sha1"][0]
            == d["streams"]["clean, seed0=4"]["populations"]["cue_sha1"][0])
    assert d["streams"]["clean, seed0=4"]["seed0"] == [4, 4], d["streams"]["clean, seed0=4"]["seed0"]
    #: a reading is not a result, so the artifact carries no `config` or `env` for the corpus's contract to count
    assert "config" not in d and "env" not in d, sorted(d)
