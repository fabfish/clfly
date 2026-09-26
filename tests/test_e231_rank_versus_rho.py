"""`e231` measures the task geometry's effective rank on a `rho` grid the corpus does not have, using the corpus's own
quantity.

The premise the tests pin: `effective_rank` is a property of the tasks alone, so rebuilding the circuit, applying the
same null and building the same seeds must reproduce the stored `geometry` blocks **exactly** -- and the live test
below checks one of them. The rest of the module is bookkeeping: a grid parsed from the command line, an
unmeasurable-cell count as the exit code, and a verification table that says which artifact each cell reproduces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e231_rank_versus_rho as e231


def row(size: int, rho: float, ranks: dict, flattening: dict | None = None) -> dict:
    return {"size": size, "support": 30, "rho": rho, "neurons": 952,
            "topologies": {t: {"effective_rank": v, "flattening": (flattening or {}).get(t, 0.5),
                               "mean_rank": 29.6, "top_eig_share": 0.2, "seeds_measured": 3, "error": None}
                           for t, v in ranks.items()}}


def test_the_registered_grid_is_the_nine_points_the_docstring_names():
    assert e231.DEFAULT_GRID == (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.999)
    assert all(a < b for a, b in zip(e231.DEFAULT_GRID, e231.DEFAULT_GRID[1:])), "the grid is a scan, not a set"
    assert e231.SIZES[300] == 30 and e231.SIZES[800] == 80, "the corpus's support convention"


def test_the_report_names_a_rise_as_the_falsifier_it_is(capsys):
    """P1 is a monotonicity claim, so a rising step must be visible in the report rather than smoothed away."""
    rows = [row(300, 0.5, {"alloy1": 26.5}), row(300, 0.9, {"alloy1": 7.2}), row(300, 0.95, {"alloy1": 9.0})]
    assert e231.report(rows) == 0
    out = capsys.readouterr().out
    assert "RISES at" in out and "0.95" in out


def test_an_unmeasurable_cell_is_the_exit_code(tmp_path, capsys):
    """A cell the instrument cannot measure must not be reported as a number -- and it is what the exit code counts."""
    rows = [row(300, 0.5, {"alloy1": 26.5}), row(300, 0.9, {"alloy1": None})]
    assert e231.report(rows) == 1
    assert "UNMEASURABLE" in capsys.readouterr().out


def test_verify_matches_the_corpus_by_value_and_reports_a_miss(tmp_path):
    """The check that makes this instrument the corpus's: a rebuilt cell either reproduces a stored geometry block or
    it does not, and the report says which artifact it matched."""
    stored = e231.stored_geometry()
    assert stored, "the corpus carries geometry blocks"
    key = (300, "real", 0.9)
    assert key in stored, sorted(k for k in stored if k[0] == 300)[:6]
    exact = stored[key][0]["rank"]
    good = e231.verify([row(300, 0.9, {"real": exact})])
    assert [len(c["matches"]) for c in good] == [1], good
    bad = e231.verify([row(300, 0.9, {"real": exact * 1.5})])
    assert bad[0]["matches"] == [] and bad[0]["stored_values"], bad


def test_the_live_instrument_reproduces_a_stored_cell_exactly():
    """One live cell: rebuild cs 300/`real`/`rho` 0.9 with the corpus's seeds and compare with `e217`'s block."""
    measured = e231.measure(300, 30, 0.9, topologies=("real",), seeds=3)
    checks = e231.verify([measured])
    assert len(checks) == 1 and checks[0]["matches"], checks
    assert abs(measured["topologies"]["real"]["effective_rank"]
               - e231.stored_geometry()[(300, "real", 0.9)][0]["rank"]) < 1e-9


def test_a_grid_point_that_is_not_in_the_corpus_is_measured_and_reported_as_the_asymmetry(tmp_path, capsys):
    """The grid's whole purpose: a `rho` the corpus does not have, with the alloy/inalloy ratio printed beside it."""
    rows = [row(300, 0.5, {"alloy1": 26.5, "inalloy1": 25.8}), row(300, 0.95, {"alloy1": 2.4, "inalloy1": 4.3})]
    assert e231.report(rows) == 0
    out = capsys.readouterr().out
    assert "0.95" in out and "ratio" in out and "0.56" in out
