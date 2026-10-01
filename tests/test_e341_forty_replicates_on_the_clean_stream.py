"""`e341` resolves the effect on the clean stream, so the tests pin the paired statistic with its per-replicate
spread, the resolution and size claims, the five-replicate check, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e341_forty_replicates_on_the_clean_stream as e341


def test_the_paired_statistic_carries_its_own_spread():
    p = e341.paired([0.05, 0.06, 0.04], [0.0, 0.0, 0.0])
    assert p["n"] == 3 and abs(p["delta"] - 0.05) < 1e-12, p
    assert p["sem"] > 0, p
    assert e341.paired([0.05], [0.0])["delta"] is None


def _world(forget, leak, n, seed=4, spread=0.01):
    return {"config": {"circuit_size": 300, "repeats": n, "train": 96, "test": 48, "readout_size": 32,
                       "readout_seed": 0, "loop_seed": 0, "seed0": seed, "loop_scale": 1.0, "loop_noise": 1.0,
                       "loop_symbols": 8, "loop_world_modes": 2},
            "circuit": "mb+cx+al@n952", "readout": {"subset_sha1": "r1"},
            "env_draw": {"world_leak": leak, "cue_sha1": "c1", "action_sha1": "a", "feedback_sha1": "f",
                         "tau": 12, "n_symbols": 24},
            "tasks": [{"name": "loop_t"}],
            "methods": {e341.ARM: {"final_accuracy": 0.6, "mean_forgetting": forget,
                                   "replicates": [{"final_accuracy": 0.6,
                                                   "mean_forgetting": forget + spread * (i % 3 - 1)}
                                                  for i in range(n)]}},
            "timing_s": 1.0}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _reading(instant=0.0500, carry=0.0670, short_instant=0.0500, short_carry=0.0667, n=40, seed=4,
             carry_leak=0.35, spread=(0.01, 0.02)):
    """The two worlds carry **different** replicate spreads, so a paired difference has a finite standard error."""
    return e341.reading(_write(_world(instant, 1.0, n, seed=seed, spread=spread[0])),
                        _write(_world(carry, carry_leak, n, seed=seed, spread=spread[1])),
                        (_write(_world(short_instant, 1.0, 5, seed=seed)),
                         _write(_world(short_carry, 0.35, 5, seed=seed))))


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e341.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: two worlds that do not differ in the leak
    assert e341.judge(_reading(carry_leak=1.0))[0]["verdict"].startswith("FALSIFIER")
    # T2: a negative difference, and an unresolved one
    assert e341.judge(_reading(carry=0.0400))[1]["verdict"].startswith("FALSIFIER")
    assert e341.judge(_reading(carry=0.0504))[1]["verdict"].startswith("FALSIFIER")
    # T3: a magnitude under the trivial floor
    assert e341.judge(_reading(carry=0.0502, short_carry=0.0502))[2]["verdict"].startswith("FALSIFIER")
    assert e341.judge(_reading(carry=0.0560, short_carry=0.0560))[2]["verdict"].startswith("NULL")
    # T4: five replicates that were far off
    assert e341.judge(_reading(short_carry=0.1000))[3]["verdict"].startswith("FALSIFIER")

    # a missing long pair refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e341.judge({"long": {"ok": False, "missing": ["runs/x.json"]}}))


def test_the_reader_refuses_when_the_long_pair_is_incomplete(tmp_path):
    r = e341.reading(tmp_path / "absent.json", tmp_path / "absent2.json",
                     (_write(_world(0.05, 1.0, 5)), _write(_world(0.067, 0.35, 5))))
    assert not r["long"].get("ok") and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e341.judge(r))


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e341_forty_replicates_on_the_clean_stream.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e341.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["long"]["n"] == [40, 40], d["long"]["n"]
    #: the point of the unit: forty replicates on the clean stream, whose draws match `e340`'s five-replicate pair
    assert d["long"]["readout"][0] == d["short"]["readout"][0], (d["long"]["readout"], d["short"]["readout"])
    assert (d["long"]["populations"]["cue_sha1"][0] == d["short"]["populations"]["cue_sha1"][0]), d["short"]
    #: a reading is not a result, so the artifact carries no `config` or `env` for the corpus's contract to count
    assert "config" not in d and "env" not in d, sorted(d)
