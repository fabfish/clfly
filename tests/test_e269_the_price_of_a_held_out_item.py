"""`e269` prices a held-out item, so the tests pin the reading, both faces of the three claims and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e269_the_price_of_a_held_out_item as e269


def _art(n_eval, seconds, *, n_test=48, n_train=96, repeats=1, methods="naive", lam=1.0):
    return {"config": {"repeats": repeats, "methods": methods, "lam": lam, "circuit_size": 300, "readout_size": 32,
                       "basis": "side", "shared_head": True, "fisher_batches": 32},
            "timing_s": seconds, "evaluation_noise": {"n_eval": n_eval},
            "tasks": [{"n_test": n_test, "n_train": n_train} for _ in range(3)]}


def test_the_reading_extracts_the_suite_and_the_clock():
    r = e269.reading(_art(144, 30.0))
    assert r["n_eval"] == 144 and r["seconds"] == 30.0
    assert r["test_per_task"] == [48, 48, 48] and r["train_per_task"] == [96, 96, 96]
    assert r["repeats"] == 1 and r["methods"] == "naive"


def test_the_three_claims_read_both_faces():
    small, large = e269.reading(_art(144, 30.0)), e269.reading(_art(1098, 23.0, n_test=366))
    j = {r["id"]: r for r in e269.judge(small, large)}
    assert j["T1"]["verdict"].startswith("MET") and j["T2"]["verdict"].startswith("MET"), j
    assert j["T3"]["verdict"].startswith("MET"), j["T3"]
    assert "0.0073" in j["T2"]["measured"] or "0.0074" in j["T2"]["measured"], j["T2"]
    # equal suites, or a training set that moved, is T1's falsifier
    j = {r["id"]: r for r in e269.judge(small, e269.reading(_art(144, 20.0)))}
    assert j["T1"]["verdict"].startswith("FALSIFIER FIRED"), j["T1"]
    j = {r["id"]: r for r in e269.judge(small, e269.reading(_art(1098, 20.0, n_test=366, n_train=192)))}
    assert j["T1"]["verdict"].startswith("FALSIFIER FIRED"), j["T1"]
    # a much slower larger run is T2's, and a suite that costs a fifth of a real run is T3's
    j = {r["id"]: r for r in e269.judge(small, e269.reading(_art(1098, 60.0, n_test=366)))}
    assert j["T2"]["verdict"].startswith("FALSIFIER FIRED"), j["T2"]
    j = {r["id"]: r for r in e269.judge(small, e269.reading(_art(4096, 200.0, n_test=1365)))}
    assert j["T3"]["verdict"].startswith("FALSIFIER FIRED"), j["T3"]
    # and nothing on disk refuses
    assert e269.judge(None, large)[0]["verdict"].startswith("REFUSED")
    assert e269.judge(small, None)[0]["verdict"].startswith("REFUSED")


def test_the_live_pair_says_the_suite_is_free():
    """The finding's numbers on the artifact: 144 against 1098 decisions at 30.47 s against 23.38 s, and the suite the
    worst configuration needs at 0.25% of a real run."""
    p = Path("runs/e269_the_price_of_a_held_out_item.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["small"]["n_eval"] == 144 and d["large"]["n_eval"] == 1098, (d["small"], d["large"])
    assert abs(d["small"]["seconds"] - 30.47) < 0.05 and abs(d["large"]["seconds"] - 23.38) < 0.05, d
    assert d["large"]["seconds"] < d["small"]["seconds"], "the larger suite ran faster"
    assert d["small"]["train_per_task"] == d["large"]["train_per_task"], "the training set did not move"
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("T1", "T2", "T3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "0.25%" in claims["T3"]["measured"], claims["T3"]
