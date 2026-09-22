"""Tests for the `e45` sectioning and per-seed Spearman helpers.

`e45` compares `e5`'s per-seed association across two circuit sizes, and it has two ingest routes:
JSON artifacts (full precision, carries the absolute excess) and a progress log (4-decimal printing,
and **no** absolute excess because `oracle_final` is not printed). A route that silently dropped a
section, or silently substituted the relative gap for the absolute one, would publish a wrong
comparison -- so both are pinned, including the fact that the log route cannot produce the absolute
column.
"""

from __future__ import annotations

import json

import numpy as np

from experiments.e45_e5_seed_pattern_across_circuits import from_jsons, from_log, rho, summarise

#: A log in `e5`'s real output format, two sections, each with two seeds of three kappas.
LOG = """=== real cs=800 ===
  seed 0 kappa=0     flatten=0.7587 effrank=  55.1 offdiag=0.2665 gap_ewc=+0.0621 (126s)
  seed 0 kappa=0.5   flatten=0.5862 effrank=  42.6 offdiag=0.2712 gap_ewc=+0.0772 (353s)
  seed 0 kappa=1     flatten=0.3215 effrank=  23.3 offdiag=0.2744 gap_ewc=+0.1335 (485s)
  seed 1 kappa=0     flatten=0.7579 effrank=  55.0 offdiag=0.2682 gap_ewc=+0.5757 (846s)
  seed 1 kappa=0.5   flatten=0.5911 effrank=  42.9 offdiag=0.2603 gap_ewc=+0.2670 (1056s)
  seed 1 kappa=1     flatten=0.2821 effrank=  20.5 offdiag=0.2570 gap_ewc=+0.1492 (1165s)
=== real cs=300 ===
  seed 0 kappa=0     flatten=0.7254 effrank=  47.9 offdiag=0.2708 gap_ewc=+0.1801 (56s)
  seed 0 kappa=1     flatten=0.3378 effrank=  22.3 offdiag=0.2423 gap_ewc=+0.6036 (219s)
  seed 0 kappa=4     flatten=0.0474 effrank=   3.1 offdiag=0.1835 gap_ewc=+0.1865 (333s)
"""


def test_log_route_sections_on_the_markers(tmp_path):
    p = tmp_path / "e5.log"
    p.write_text(LOG, encoding="utf-8")
    secs = from_log(str(p))
    assert [s["label"] for s in secs] == ["real cs=800", "real cs=300"]
    assert [len(s["rows"]) for s in secs] == [6, 3]
    assert all(r["excess"] != r["excess"] for s in secs for r in s["rows"])  # nan


def test_log_route_cannot_produce_the_absolute_column(tmp_path):
    p = tmp_path / "e5.log"
    p.write_text(LOG, encoding="utf-8")
    # `oracle_final` is not printed, so every section must be flagged as lacking it rather than
    # silently substituting the relative gap for the absolute one
    assert all(not s["has_absolute"] for s in from_log(str(p)))


def test_log_route_parses_the_fields_it_does_carry(tmp_path):
    p = tmp_path / "e5.log"
    p.write_text(LOG, encoding="utf-8")
    row = from_log(str(p))[0]["rows"][0]
    assert row["seed"] == 0 and row["kappa"] == 0.0
    assert abs(row["flatten"] - 0.7587) < 1e-9
    assert abs(row["gap"] - 0.0621) < 1e-9


def test_json_route_reads_the_stored_absolute_excess_when_present(tmp_path):
    entry = {"config": {"circuit_size": 800, "topology": "real"},
             "points": [{"seed": 0, "kappa": 0.0, "flattening": 0.5, "gap_ewc": 0.1,
                         "excess_ewc": 0.0123, "oracle_final": 0.05}]}
    p = tmp_path / "run.json"
    p.write_text(json.dumps(entry), encoding="utf-8")
    secs = from_jsons([str(p)])
    assert len(secs) == 1 and secs[0]["has_absolute"]
    assert abs(secs[0]["rows"][0]["excess"] - 0.0123) < 1e-12


def test_json_route_derives_the_absolute_excess_when_absent(tmp_path):
    # e5_anisotropy.json predates the stored column, so the derivation gap x oracle must still work
    entry = {"config": {"circuit_size": 800},
             "points": [{"seed": 0, "kappa": 0.0, "flattening": 0.5, "gap_ewc": 0.1,
                         "oracle_final": 0.05}]}
    p = tmp_path / "old.json"
    p.write_text(json.dumps(entry), encoding="utf-8")
    secs = from_jsons([str(p)])
    assert secs[0]["has_absolute"]
    assert abs(secs[0]["rows"][0]["excess"] - 0.005) < 1e-12


def test_summarise_reports_per_seed_and_pooled_separately():
    rows = [{"seed": 0, "kappa": k, "flatten": f, "gap": g} for k, f, g in
            [(0.0, 0.9, 0.1), (1.0, 0.6, 0.2), (2.0, 0.3, 0.3)]]
    rows += [{"seed": 1, "kappa": k, "flatten": f, "gap": g} for k, f, g in
             [(0.0, 0.9, 0.3), (1.0, 0.6, 0.2), (2.0, 0.3, 0.1)]]
    s = summarise("t", rows, "gap")
    assert s["metric"] == "gap"
    assert s["per_seed"]["0"]["rho"] == -1.0        # seed 0 is exactly monotone the e5 way
    assert s["per_seed"]["1"]["rho"] == 1.0         # seed 1 is exactly reversed
    assert s["pooled"]["n"] == 6
    assert s["per_seed_verdicts"]["0"] == "SIGNIFICANT"
    assert s["per_seed_verdicts"]["1"] == "SIGNIFICANT"


def test_rho_refuses_degenerate_input():
    # fewer than three points, or a constant axis, must give nan rather than a fabricated 0 or 1
    cases = [
        ([1.0, 2.0], [1.0, 2.0]),                 # too few points
        ([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]),       # flat x
        ([1.0, 2.0, 3.0], [0.5, 0.5, 0.5]),       # flat y
    ]
    for x, y in cases:
        r, p = rho(x, y)
        assert not np.isfinite(r) and not np.isfinite(p)


def test_incomplete_seeds_are_marked_rather_than_dropped():
    rows = [{"seed": 0, "kappa": k, "flatten": f, "gap": g} for k, f, g in
            [(0.0, 0.9, 0.1), (1.0, 0.6, 0.2), (2.0, 0.3, 0.3)]]
    rows += [{"seed": 1, "kappa": 0.0, "flatten": 0.9, "gap": 0.3},
             {"seed": 1, "kappa": 1.0, "flatten": 0.6, "gap": 0.2}]
    s = summarise("t", rows, "gap")
    assert s["per_seed"]["1"]["n"] == 2
    assert s["per_seed_verdicts"]["1"] == "incomplete"
    assert s["pooled"]["n"] == 5  # the partial seed still contributes to the pool
