"""`e339` measures what `--seed0` moves besides the seeds, so the tests pin the per-pair comparison, the two
fingerprint claims, the settings check, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e339_is_the_ordering_immune_to_the_redraw as e339


def _run(seed0, readout, cue, methods=("replay",), scale=0.5, n=5):
    return {"config": {"circuit_size": 300, "repeats": n, "seed0": seed0, "methods": ",".join(methods),
                       "train": 96, "test": 48, "readout_size": 32, "classes": 4, "loop_scale": scale,
                       "loop_noise": 1.0, "loop_symbols": 8, "loop_world_modes": 2, "loop_world_leak": 1.0,
                       "json_out": "x"},
            "circuit": "mb+cx+al@n952", "readout": {"subset_sha1": readout},
            "env_draw": {"cue_sha1": cue, "action_sha1": "a", "feedback_sha1": "f", "tau": 12, "n_symbols": 24},
            "tasks": [{"name": "loop_t"}],
            "methods": {m: {"final_accuracy": 0.6, "mean_forgetting": 0.1,
                            "replicates": [{"final_accuracy": 0.6, "mean_forgetting": 0.1} for _ in range(n)]}
                        for m in methods},
            "timing_s": 1.0}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _pairs(first=None, second=None):
    a = _write(first if first is not None else _run(0, "r1", "c1"))
    b = _write(second if second is not None else _run(4, "r2", "c2"))
    return (("two worlds", a, b),)


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e339.judge(e339.reading(_pairs()))}
    # the default fixture is a pair whose draws moved and whose settings did not, so T1 fires on the read-out while
    # T2, T3 and T4 hold
    assert j["T1"]["verdict"].startswith("FALSIFIER"), j["T1"]
    for cid in ("T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T2's falsifier: the same read-out draw on both sides
    assert e339.judge(e339.reading(_pairs(second=_run(4, "r1", "c2"))))[1]["verdict"].startswith("FALSIFIER")
    # T3's falsifier: the same populations
    assert e339.judge(e339.reading(_pairs(second=_run(4, "r2", "c1"))))[2]["verdict"].startswith("FALSIFIER")
    # T4's falsifier: a non-seed setting differing
    assert e339.judge(e339.reading(_pairs(second=_run(4, "r2", "c2", methods=("naive", "replay")))))[3][
        "verdict"].startswith("FALSIFIER")
    # and a pair whose seeds agree is not a seed-stream pair at all
    assert e339.judge(e339.reading(_pairs(second=_run(0, "r2", "c2"))))[0]["verdict"].startswith("FALSIFIER")

    # no pair at all refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e339.judge({"pairs": []}))


def test_the_reader_refuses_when_a_pair_is_incomplete(tmp_path):
    r = e339.reading((("two worlds", _write(_run(0, "r1", "c1")), tmp_path / "absent.json"),))
    assert r["runs"] == 0 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e339.judge(r))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e339_is_the_ordering_immune_to_the_redraw.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e339.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("FALSIFIER"), d["claims"][0]
    assert d["claims"][1]["verdict"].startswith("MET"), d["claims"][1]
    assert d["claims"][2]["verdict"].startswith("MET"), d["claims"][2]
    assert len(d["pairs"]) == 2, d["pairs"]
    #: a reading is not a result, so the artifact carries no `config` or `env` for the corpus's contract to count
    assert "config" not in d and "env" not in d, sorted(d)
