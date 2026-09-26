"""`e262` closes the replicate-order lead against its own null, so the tests pin the three order statistics, the
permutation null and its reproducibility, the rerun check, the seed census, both faces of all five claims, and the
live table's numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from experiments import e262_replicate_order_is_not_a_variable as e262


def test_the_runs_test_counts_runs_and_drops_ties():
    r = e262.runs_test("+-+-+-+-----++--")
    assert r["n"] == 16 and r["runs"] == 10, r
    assert r["expected"] > 0 and math.isfinite(r["p"])
    alternating = e262.runs_test("+-+-+-+-")
    assert alternating["n"] == 8 and alternating["runs"] == 8 and alternating["p"] < 0.05, alternating
    assert math.isnan(e262.runs_test("++++++++")["p"]), "one sign is no sequence"
    tied = e262.runs_test("+-0-+")
    assert tied["n"] == 4 and tied["runs"] == 3, tied


def test_the_half_split_is_in_null_units_and_zero_for_a_flat_half():
    d = [0.0] * 8 + [1.0] * 8
    z = e262.half_split_z(d)
    assert z > 2.5, z
    flat = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0] * 2
    assert abs(e262.half_split_z(flat)) < 1e-9, e262.half_split_z(flat)


def test_the_index_correlation_is_a_rank_correlation_with_ties_averaged():
    assert abs(e262.index_rho(list(range(16))) - 1.0) < 1e-9
    assert abs(e262.index_rho(list(range(16, 0, -1))) + 1.0) < 1e-9
    assert math.isnan(e262.index_rho([1.0] * 16)), "a constant column has no rank variance"
    assert abs(e262.index_rho([1.0, 2.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0])) > 0.9


def _seqs():
    return {"a/acc": [(-1) ** i * (1.0 + 0.1 * i) for i in range(16)],
            "b/acc": [(-1) ** i * (1.0 + 0.2 * i) for i in range(16)]}


def test_the_null_permutes_each_sequence_s_own_signs_and_is_reproducible():
    seqs = _seqs()
    a = e262.best_of_six_null(seqs, draws=40, seed=7)
    b = e262.best_of_six_null(seqs, draws=40, seed=7)
    assert a.shape == (40,) and np.allclose(a, b), "the same seed gives the same null"
    assert np.all((a >= 0) & (a <= 1)), a
    # every sequence here alternates perfectly, so a permuted draw is usually much less ordered
    kept = e262.best_of_six_null({"a/acc": [(-1) ** i for i in range(16)]}, draws=200, seed=3)
    assert float(kept.mean()) > 0.05, "a permutation null must not reproduce the sequence it permutes"


def test_the_seed_census_finds_a_per_replicate_seed_when_there_is_one(tmp_path):
    clean = {"config": {"circuit_size": 300}, "methods": {"m": {"replicates": [{"final_accuracy": 0.5}] * 3}}}
    dirty = {"config": {"circuit_size": 300}, "methods": {"m": {"replicates": [{"final_accuracy": 0.5, "seed": 1},
                                                                            {"final_accuracy": 0.5, "seed": 2}]}}}
    (tmp_path / "clean.json").write_text(json.dumps(clean), encoding="utf-8")
    (tmp_path / "dirty.json").write_text(json.dumps(dirty), encoding="utf-8")
    (tmp_path / "listy.json").write_text(json.dumps({"methods": [1, 2]}), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{oops", encoding="utf-8")
    got = e262.seed_field_census(tmp_path)
    assert got["artifacts"] == 2 and got["records"] == 5, got
    assert got["named"] == ["dirty.json"], got
    assert "seed" in got["keys"] and "final_accuracy" in got["keys"]


def _rows(p_best=0.0187, half_max=1.88, clustered="cc/forget", biggest="cross/forget"):
    rows = {clustered: {"p": p_best, "half_z": -1.35, "runs": 4, "expected": 8.2, "rho": -0.508, "signs": "x"},
            biggest: {"p": 0.782, "half_z": half_max, "runs": 8, "expected": 8.5, "rho": 0.403, "signs": "y"}}
    return rows


#: a stand-in best-of-six null: a 5th percentile of 0.0165 and an 0.05 rate of 0.159
NULL = np.linspace(0.001, 0.310, 1000)


def test_N1_and_N2_fire_when_the_observed_minimum_beats_its_own_null():
    census = {"artifacts": 1, "records": 1, "keys": [], "named": []}
    rerun = {"replicates_identical": True, "matched_pair_identical": True, "seconds": [10.0, 20.0],
             "clock_ratio": 2.0, "config_differs_only_in_json_out": True}
    j = {r["id"]: r for r in e262.judge(_seqs(), _rows(), NULL, census, rerun)}
    assert j["N1"]["verdict"].startswith("MET"), j["N1"]
    assert j["N2"]["verdict"].startswith("MET"), j["N2"]
    j = {r["id"]: r for r in e262.judge(_seqs(), _rows(p_best=0.002), NULL, census, rerun)}
    assert j["N1"]["verdict"].startswith("FALSIFIER FIRED"), j["N1"]
    j = {r["id"]: r for r in e262.judge(_seqs(), _rows(), np.full(1000, 0.5), census, rerun)}
    assert j["N2"]["verdict"].startswith("FALSIFIER FIRED"), j["N2"]


def test_N3_N4_and_N5_read_both_faces():
    census_clean = {"artifacts": 309, "records": 5366, "keys": ["final_accuracy"], "named": []}
    census_dirty = dict(census_clean, named=["x.json"])
    rerun = {"replicates_identical": True, "matched_pair_identical": True, "seconds": [14616.0, 11553.0],
             "clock_ratio": 0.79, "config_differs_only_in_json_out": True}
    j = {r["id"]: r for r in e262.judge(_seqs(), _rows(), NULL, census_clean, rerun)}
    assert j["N3"]["verdict"].startswith("MET") and j["N4"]["verdict"].startswith("MET")
    assert j["N5"]["verdict"].startswith("MET"), j["N5"]
    # a different reading is extremal on both statistics
    same = {"cc/forget": {"p": 0.019, "half_z": 2.4, "runs": 4, "expected": 8.2, "rho": 0.0, "signs": "x"},
            "cross/forget": {"p": 0.782, "half_z": 1.0, "runs": 8, "expected": 8.5, "rho": 0.0, "signs": "y"}}
    j = {r["id"]: r for r in e262.judge(_seqs(), same, NULL, census_clean, rerun)}
    assert j["N3"]["verdict"].startswith("FALSIFIER FIRED"), j["N3"]
    j = {r["id"]: r for r in e262.judge(_seqs(), _rows(), NULL, census_dirty, rerun)}
    assert j["N4"]["verdict"].startswith("FALSIFIER FIRED"), j["N4"]
    for bad in (dict(rerun, replicates_identical=False), dict(rerun, clock_ratio=1.0)):
        j = {r["id"]: r for r in e262.judge(_seqs(), _rows(), NULL, census_clean, bad)}
        assert j["N5"]["verdict"].startswith("FALSIFIER FIRED"), (bad, j["N5"])
    j = {r["id"]: r for r in e262.judge(_seqs(), _rows(), NULL, census_clean, None)}
    assert j["N5"]["verdict"].startswith("REFUSED"), j["N5"]


def test_the_live_table_closes_the_lead_and_finds_no_seed_anywhere():
    """The finding's numbers on the artifact: the best of six at 0.0187 against a null whose 5th percentile is
    0.0103, the nominal scan at 0.225, the disagreeing order statistics, and the bit-identical rerun."""
    p = Path("runs/e262_replicate_order_is_not_a_variable.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert abs(d["best_of_six"] - 0.0187) < 5e-4, d["best_of_six"]
    assert abs(d["null_percentiles"]["5"] - 0.0103) < 5e-3, d["null_percentiles"]
    assert abs(d["p_best_at_or_below_observed"] - 0.127) < 0.02, d["p_best_at_or_below_observed"]
    assert abs(d["p_best_at_or_below_0.05"] - 0.225) < 0.02, d["p_best_at_or_below_0.05"]
    rows = d["readings"]
    assert min(rows, key=lambda n: rows[n]["p"]) == "cell_class/mean_forgetting", rows
    assert max(rows, key=lambda n: abs(rows[n]["half_z"])) == "cross/mean_forgetting", rows
    assert max(abs(r["half_z"]) for r in rows.values()) < 2.0
    assert d["seed_census"]["named"] == [] and d["seed_census"]["records"] == 5366, d["seed_census"]
    assert d["rerun"]["replicates_identical"] is True and d["rerun"]["clock_ratio"] < 0.9, d["rerun"]
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("N1", "N2", "N3", "N4", "N5"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
