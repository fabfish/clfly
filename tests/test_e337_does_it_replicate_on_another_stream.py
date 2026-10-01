"""`e337` asks the thread's headline effect of a second seed stream, so the tests pin the per-stream checks, the
sign and size comparisons, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e337_does_it_replicate_on_another_stream as e337


def _run(instant_forget, carry_forget, seed0=0, leak=1.0, n=5, arms=(e337.ARM,)):
    #: the two runs of a stream carry **different** replicate spreads, so a paired difference has a finite sem
    #: rather than collapsing to zero and reporting an infinite sigma for any delta at all
    base = carry_forget if leak == 0.35 else instant_forget
    step = 0.003 if leak == 0.35 else 0.001
    reps = [{"mean_forgetting": base + step * i, "final_accuracy": 0.6} for i in range(n)]
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_world_leak": leak, "seed0": seed0},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"world_leak": leak, "world_modes": 2, "noise": 1.0, "n_symbols": 24},
            "tasks": [{"name": "t"}],
            "methods": {a: {"final_accuracy": 0.6, "mean_forgetting": instant_forget, "replicates": reps}
                        for a in arms}}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _reading(first=(0.0479, 0.0854), second=(0.0500, 0.0780), seed0=(0, 4), counts=(5, 5)):
    streams = {}
    for tag, (inst, carry), s0 in zip(e337.ORDER, (first, second), seed0):
        a = _write(_run(inst, carry, seed0=s0, leak=1.0, n=counts[0]))
        b = _write(_run(inst, carry, seed0=s0, leak=0.35, n=counts[1]))
        streams[tag] = (a, b)
    return e337.reading(streams)


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e337.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: streams that share a seed schedule are not two samples
    assert e337.judge(_reading(seed0=(0, 0)))[0]["verdict"].startswith("FALSIFIER")
    # T2: a negative difference on the second stream is the falsifier
    assert e337.judge(_reading(second=(0.0500, 0.0400)))[1]["verdict"].startswith("FALSIFIER")
    # T3: a difference an order of magnitude smaller is the falsifier, a quarter of it is the null
    assert e337.judge(_reading(second=(0.0500, 0.0510)))[2]["verdict"].startswith("FALSIFIER")
    assert e337.judge(_reading(second=(0.0500, 0.0580)))[2]["verdict"].startswith("NULL")
    # T4: a first stream that does not resolve on this reader
    assert e337.judge(_reading(first=(0.0500, 0.0460)))[3]["verdict"].startswith("FALSIFIER")
    # and a missing stream refuses every claim
    r = _reading()
    r["streams"]["seed0=4"] = {"ok": False}
    assert all(row["verdict"].startswith("REFUSED") for row in e337.judge(r)), e337.judge(r)


def test_the_stream_reading_pairs_by_replicate_index():
    a = _write(_run(0.05, 0.06, leak=1.0))
    b = _write(_run(0.05, 0.06, leak=0.35))
    st = e337.stream_reading(json.loads(a.read_text(encoding="utf-8")),
                             json.loads(b.read_text(encoding="utf-8")))
    assert st["counts"] == [5, 5] and st["leaks"] == [1.0, 0.35], st
    # the paired difference is the runs' 0.01 apart plus the spread step, and its sem is the spread's own
    assert abs(st["forgetting"]["delta"] - 0.014) < 1e-12, st["forgetting"]
    assert 0.0 < st["forgetting"]["sem"] < 0.01, st["forgetting"]
    # and one replicate is refused rather than estimated
    assert e337.paired([0.1], [0.05])["delta"] is None


def test_the_reader_refuses_when_a_stream_is_incomplete():
    r = e337.reading({"seed0=0": (Path("runs/e333_world_instant.json"), Path("runs/absent.json"))})
    assert r["runs"] < 4 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e337.judge(r))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e337_does_it_replicate_on_another_stream.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e337.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the second stream landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["streams"]["seed0=0"]["seed0"] == [0, 0], d["streams"]["seed0=0"]["seed0"]
    assert d["streams"]["seed0=4"]["seed0"] == [4, 4], d["streams"]["seed0=4"]["seed0"]
