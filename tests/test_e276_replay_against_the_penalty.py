"""`e276` reads the method contrast the register has not quoted, so the tests pin the paired helper, both faces of the
four claims and the live numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e276_replay_against_the_penalty as e276


def test_the_paired_helper_reads_a_delta_its_sem_and_its_sigma():
    a = [0.50, 0.52, 0.54, 0.56]
    b = [0.40, 0.42, 0.44, 0.46]
    c = e276.paired(a, b)
    assert c["n"] == 4 and abs(c["delta"] - 0.10) < 1e-12, c
    assert abs(c["sem"] - 0.0) < 1e-12, "a constant difference has no sem"
    assert c["sigma"] > 1e9, "a constant difference reads as an unbounded sigma (its residue is rounding)"
    noisy = e276.paired([0.5, 0.6, 0.4, 0.7], [0.4, 0.2, 0.35, 0.6])
    assert 0 < noisy["sigma"] < float("inf") and noisy["delta"] > 0, noisy


def _art(path: Path, n=40, replay_gain=0.04, pen_gain=0.003, arms=("naive", "ewc-block", "ewc-block-rand", "replay")):
    base = [0.9 + 0.001 * i for i in range(n)]
    payload = {"config": {"circuit_size": 800, "readout_size": 32},
               "methods": {a: {"replicates": [{"final_accuracy": v, "mean_forgetting": v} for v in base]}
                           for a in arms}}
    for i, r in enumerate(payload["methods"]["ewc-block"]["replicates"]):
        r["final_accuracy"] += pen_gain
        r["mean_forgetting"] -= pen_gain
    for i, r in enumerate(payload["methods"]["replay"]["replicates"]):
        r["final_accuracy"] += pen_gain + replay_gain
        r["mean_forgetting"] -= pen_gain + replay_gain
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_contrast_reader_is_paired_and_only_over_arms_both_runs_carry(tmp_path):
    p = tmp_path / "a.json"
    d = _art(p)
    c = e276.contrasts(d, "final_accuracy")
    assert set(c) == {"replay-ewc-block", "ewc-block-naive", "replay-naive"}, sorted(c)
    assert abs(c["replay-ewc-block"]["delta"] - 0.04) < 1e-9, c["replay-ewc-block"]
    assert c["replay-ewc-block"]["sigma"] > 1e9, "a constant gain reads as an unbounded sigma"
    assert abs(c["replay-naive"]["delta"] - 0.043) < 1e-9, c["replay-naive"]


def _rows(v1=(3.3, 9.1, 11.8), v2=(-0.004, -0.06, -0.05), v3=(1.7, 0.8, 0.8), sigma2=(1.3, 8.4, 7.1)):
    out = {}
    for i, label in enumerate(("a", "b", "c")):
        out[label] = {"artifact": f"{label}.json", "n": 40, "config": {},
                      "contrasts": {m: {} for m in e276.METRICS}}
        out[label]["contrasts"]["final_accuracy"] = {"replay-ewc-block": {"sigma": v1[i], "delta": 0.01},
                                                     "ewc-block-naive": {"sigma": v3[i], "delta": 0.004}}
        out[label]["contrasts"]["mean_forgetting"] = {"replay-ewc-block": {"sigma": sigma2[i], "delta": v2[i]}}
    return out


def test_the_four_claims_read_both_faces():
    j = {r["id"]: r for r in e276.judge(_rows(), {"same_replicates": True, "configs_differ_in": ["json_out"]})}
    for cid in ("V1", "V2", "V3", "V4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a configuration where replay does not win is V1's
    j = {r["id"]: r for r in e276.judge(_rows(v1=(1.0, 9.1, 11.8)), {"same_replicates": True,
                                                                    "configs_differ_in": []})}
    assert j["V1"]["verdict"].startswith("FALSIFIER FIRED"), j["V1"]
    # replay forgetting more is V2's, and a resolved penalty is V3's
    j = {r["id"]: r for r in e276.judge(_rows(v2=(0.01, -0.06, -0.05)), {"same_replicates": True,
                                                                       "configs_differ_in": []})}
    assert j["V2"]["verdict"].startswith("FALSIFIER FIRED"), j["V2"]
    j = {r["id"]: r for r in e276.judge(_rows(v3=(2.5, 2.5, 0.8)), {"same_replicates": True,
                                                                   "configs_differ_in": []})}
    assert j["V3"]["verdict"].startswith("FALSIFIER FIRED"), j["V3"]
    # and a rerun that differs is V4's
    j = {r["id"]: r for r in e276.judge(_rows(), {"same_replicates": False, "configs_differ_in": ["lam"]})}
    assert j["V4"]["verdict"].startswith("FALSIFIER FIRED"), j["V4"]
    assert e276.judge(_rows(), None)[3]["verdict"].startswith("REFUSED")
    assert e276.judge({}, None)[0]["verdict"].startswith("REFUSED")


def test_the_live_read_quotes_the_strongest_contrast_on_the_line():
    """The finding's numbers on the artifact: replay over the penalty at 3.3, 9.1 and 11.8 sigma on accuracy, the
    penalty's own gain unresolved at 1.7, 0.8 and 0.8, and the rerun bit-identical."""
    p = Path("runs/e276_replay_against_the_penalty.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["readings"]
    assert sorted(rows) == ["frozen bias", "overlap 1.0", "plastic"], sorted(rows)
    sig = {k: round(v["contrasts"]["final_accuracy"]["replay-ewc-block"]["sigma"], 2) for k, v in rows.items()}
    assert sig == {"frozen bias": 3.30, "plastic": 9.09, "overlap 1.0": 11.84}, sig
    pen = {k: round(v["contrasts"]["final_accuracy"]["ewc-block-naive"]["sigma"], 2) for k, v in rows.items()}
    assert all(v < 2.0 for v in pen.values()), pen
    assert d["rerun"]["same_replicates"] is True, d["rerun"]
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("V1", "V2", "V3", "V4"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
