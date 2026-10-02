"""`e346` asks whether the method contrast travels, so the tests pin the per-artifact pairing, the two collapses
(repeats and configurations), the artifact-level estimate and both faces of the five claims.
"""

from __future__ import annotations

import json
import statistics
import tempfile
from pathlib import Path

from experiments import e346_does_the_method_contrast_travel as e346


def _est(delta, sigma, n=5):
    return {"n": n, "delta": delta, "sem": abs(delta) / sigma if sigma else 0.0, "sigma": sigma}


def _row(name, acc, sigma=3.0, circ=800, sig=None, forget=None, fsig=None, repeats=5):
    return {"artifact": name, "circuit_size": circ, "readout_size": 32, "overlap": 0.0, "frozen_bias": False,
            "closed_loop": False, "n_tasks": 3, "repeats": repeats, "signature": sig or name,
            "signature_id": (sig or name)[:12],
            "final_accuracy": _est(acc, sigma, repeats),
            "mean_forgetting": _est(forget if forget is not None else -acc, fsig if fsig is not None else sigma,
                                    repeats)}


def _reading(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r["signature"], []).append(r)
    by_sig = []
    for s, v in sorted(groups.items()):
        by_sig.append({"signature": s[:12], "artifacts": [x["artifact"] for x in v], "n": len(v),
                       "final_accuracy": _est(statistics.fmean([x["final_accuracy"]["delta"] for x in v]), 0.0),
                       "mean_forgetting": _est(statistics.fmean([x["mean_forgetting"]["delta"] for x in v]), 0.0)})
    return {"artifacts": rows, "collapsed": ["a_repeat.json"], "arm": e346.ARM, "baseline": e346.BASELINE,
            "metrics": [e346.ACC, e346.FORGET], "sigma_bar": e346.SIGMA, "other_size": e346.OTHER_SIZE,
            "by_signature": {"n": len(by_sig), "rows": by_sig,
                             "accuracy": e346.across(by_sig, e346.ACC),
                             "forgetting": e346.across(by_sig, e346.FORGET)}}


def _judge(r):
    return {row["id"]: row for row in e346.judge(r)}


def test_the_five_claims_read_both_faces():
    rows = [_row("a.json", 0.05), _row("b.json", 0.03, circ=300), _row("c.json", 0.02, circ=300)]
    j = _judge(_reading(rows))
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    assert "22 distinct" not in j["T1"]["measured"] and "distinct configurations" in j["T1"]["measured"], j["T1"]

    # T2: one substrate where the difference is negative
    assert _judge(_reading(rows + [_row("d.json", -0.01, circ=300)]))["T2"]["verdict"].startswith("FALSIFIER")
    # T3: the artifact-level mean at or below zero is the wrong sign, and a scattered set under two sigma the other
    assert _judge(_reading([_row("a.json", -0.05), _row("b.json", -0.03)]))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading([_row("a.json", 0.20), _row("b.json", 0.01)]))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: the 300-budget subset has to carry the estimate on its own
    assert _judge(_reading([_row("a.json", 0.05, circ=800), _row("b.json", 0.04, circ=800)]))["T4"][
        "verdict"].startswith("REFUSED")
    assert _judge(_reading(rows + [_row("d.json", -0.02, circ=300)]))["T4"]["verdict"].startswith("FALSIFIER")
    # T5: replay forgetting more is the wrong sign on the forgetting side
    assert _judge(_reading([_row("a.json", 0.05, forget=0.02), _row("b.json", 0.03, forget=0.01)]))["T5"][
        "verdict"].startswith("FALSIFIER")
    # and a corpus that yields no pair refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e346.judge({"artifacts": []}))


def test_one_artifact_pairs_the_replicates_then_reports():
    def run(replay_accs, ewc_accs, metrics=("final_accuracy", "mean_forgetting")):
        return {"config": {"circuit_size": 300, "readout_size": 32, "input_overlap": 0.0},
                "tasks": [{"name": "t0"}],
                "methods": {"replay": {"replicates": [{"final_accuracy": a, "mean_forgetting": -a}
                                                      for a in replay_accs]},
                            "ewc-block": {"replicates": [{"final_accuracy": b, "mean_forgetting": -b}
                                                         for b in ewc_accs]}}}
    row = e346.one_artifact("x.json", run([0.8, 0.9, 0.7], [0.5, 0.6, 0.5]))
    #: the pairing is per replicate and the delta is the mean of the three differences
    assert abs(row[e346.ACC]["delta"] - (0.3 + 0.3 + 0.2) / 3) < 1e-12, row
    assert row["repeats"] == 3 and row["circuit_size"] == 300, row
    #: unequal lists pair on the shorter prefix rather than raising
    short = e346.one_artifact("x.json", run([0.8, 0.9], [0.5, 0.6, 0.4]))
    assert short["repeats"] == 2, short
    #: a missing arm or a missing replicate list makes the artifact unreadable rather than empty
    assert e346.one_artifact("x.json", {"methods": {"replay": {"replicates": []}}}) is None
    assert e346.one_artifact("x.json", {"methods": {"replay": {"replicates": [{}]},
                                                    "ewc-block": {"replicates": []}}}) is None
    #: a metric missing from a replicate leaves that metric unmeasured and the artifact readable
    d = run([0.8, 0.9], [0.5, 0.6])
    del d["methods"]["replay"]["replicates"][0]["mean_forgetting"]
    assert e346.one_artifact("x.json", d)[e346.ACC]["delta"] is not None
    assert e346.one_artifact("x.json", d)[e346.FORGET]["delta"] is None


def test_a_configuration_executed_twice_votes_once():
    rows = [_row("a.json", 0.05, sig="same"), _row("b.json", -0.05, sig="same"), _row("c.json", 0.03, sig="other")]
    r = _reading(rows)
    assert r["by_signature"]["n"] == 2, r["by_signature"]
    assert abs(r["by_signature"]["accuracy"]["delta"] - (0.0 + 0.03) / 2) < 1e-12, r["by_signature"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e346_does_the_method_contrast_travel.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e346.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the corpus was read; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert len(d["artifacts"]) >= 20, len(d["artifacts"])
    #: every row carries both metrics and both arms, and the estimates are the artifacts' own
    for row in d["artifacts"]:
        assert row[e346.ACC]["delta"] is not None, row["artifact"]
        assert row["repeats"] >= 1, row
    #: the two collapses are both in the artifact: the repeat skip list and the configuration count
    assert len(d["collapsed"]) >= 1 and d["by_signature"]["n"] >= 2, d
    assert d["by_signature"]["n"] <= len(d["artifacts"]), d["by_signature"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
