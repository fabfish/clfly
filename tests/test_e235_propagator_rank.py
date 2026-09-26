"""`e235` measures the propagator's own rank beside the task geometry's, on the same circuits and the same `rho`.

The premise the tests pin: the TASK side is the corpus's own statistic, rebuilt through the same calls
(`stable_weights` -> `propagator_solver` -> `assembly_support` in the builder's order -> `task_covariance` ->
`task_geometry`), so it reproduces `e231`'s stored numbers -- checked live below. The propagator side solves
`G x = e_i` over the assemblies' union support and reads the participation ratio of the propagated matrix's squared
singular values, which is the same kind of reading one level down.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e235_propagator_rank as e235


def test_the_participation_ratio_is_the_task_geometry_s_own_reading():
    """A flat spectrum of n equal weights gives n; a one-mode spectrum gives 1; and it is scale free."""
    assert abs(e235.participation_ratio(np.ones(10)) - 10.0) < 1e-9
    assert abs(e235.participation_ratio(np.array([1.0, 0.0, 0.0])) - 1.0) < 1e-9
    assert abs(e235.participation_ratio(np.array([3.0, 3.0, 3.0, 3.0])) - 4.0) < 1e-9
    assert np.isnan(e235.participation_ratio(np.zeros(3))), "an empty spectrum is not a rank of 0"


def test_the_propagator_rank_reads_the_action_of_a_known_operator():
    """Two operators solvable by hand: one direction dominating to 0.1% gives a participation ratio of 1.001, and a
    (1, 1, 1, 0.5) diagonal gives 49/19 because its squared singular values are (1, 1, 1, 4)."""
    class Dominant:
        diag = np.array([1.0, 0.5, 0.01])

        def solve(self, e):
            return e / self.diag

    r = e235.propagator_rank(Dominant(), np.array([0, 1, 2]), 3)
    s2 = (1.0 / Dominant.diag) ** 2
    assert abs(r["propagator_effective_rank"] - e235.participation_ratio(s2)) < 1e-12
    assert 1.0 < r["propagator_effective_rank"] < 1.01, r
    assert r["support_size"] == 3

    class Balanced:
        diag = np.array([1.0, 1.0, 1.0, 0.5])

        def solve(self, e):
            return e / self.diag

    r2 = e235.propagator_rank(Balanced(), np.array([0, 1, 2, 3]), 4)
    assert abs(r2["propagator_effective_rank"] - 49.0 / 19.0) < 1e-9, r2
    assert abs(r2["propagator_top_share"] - 4.0 / 7.0) < 1e-9, r2


def test_the_task_side_reproduces_the_corpus_s_own_numbers():
    """One live cell at cs 300/`rho` 0.9: the four topologies must equal `e231`'s stored values, or this instrument
    is measuring something else."""
    row = e235.measure(300, 30, 0.9, seeds=3)
    stored = e235.stored_ranks()
    matched = 0
    for topo in e235.TOPOLOGIES:
        got = row["topologies"][topo].get("effective_rank")
        vals = stored.get((300, topo, 0.9), [])
        assert vals, (topo, sorted(k for k in stored if k[0] == 300)[:4])
        assert any(abs(v - got) <= 1e-6 * max(abs(v), 1e-12) for v in vals), (topo, got, vals)
        assert row["topologies"][topo]["propagator_effective_rank"] > 0
        matched += 1
    assert matched == 4


def test_the_report_names_an_unmeasurable_cell_rather_than_printing_a_number(capsys):
    row = {"size": 300, "support": 30, "rho": 0.99, "neurons": 952,
           "topologies": {t: {"error": "RuntimeError: singular"} for t in e235.TOPOLOGIES}}
    assert e235.report([row]) == len(e235.TOPOLOGIES)
    out = capsys.readouterr().out
    assert "UNMEASURABLE" in out and "unmeasurable cells: 4" in out
