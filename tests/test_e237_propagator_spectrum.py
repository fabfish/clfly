"""`e237` measures the whole propagator `G = (I - W)^-1` with no support in it, which is what makes the rank collapse
support-free: the tests pin the two ends of that — a hand-built rank-one operator must read `pr_G = 1` with a leading
share of 1, and one live cell must reproduce the artifact's value while reporting an assembly share strictly inside
the unit interval (the quantity the slice-escape mechanism turns on).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e237_propagator_spectrum as e237


def test_a_rank_one_operator_reads_a_participation_ratio_of_one():
    """The reading's own endpoint: `G = u v^T` is the near-critical limit, and it must come out as exactly one
    effective dimension with the whole share on its single direction."""
    rng = np.random.default_rng(0)
    u, v = rng.standard_normal(50), rng.standard_normal(50)
    sv = np.linalg.svd(np.outer(u, v), compute_uv=False)
    energy = sv ** 2
    assert abs(e237.participation_ratio(energy) - 1.0) < 1e-9
    assert abs(energy[0] / energy.sum() - 1.0) < 1e-12
    # and a flat spectrum of n directions reads n
    assert abs(e237.participation_ratio(np.ones(64)) - 64.0) < 1e-9


def test_the_live_cell_reproduces_the_artifact_and_reports_a_share_inside_the_unit_interval():
    """cs 300/`real`/`rho` 0.9: the propagator does not depend on the seeds, so this is one number, and the
    assemblies' share of its leading direction must be a fraction -- if it were 1 the slice could not escape."""
    row = e237.measure(300, 30, 0.9, topologies=("real",), seeds=1)
    c = row["topologies"]["real"]
    assert abs(c["pr_G"] - 12.63) < 0.01, c["pr_G"]
    assert 0.0 < c["support_share_of_leading_direction"] < 1.0, c
    assert c["condition_number"] > 1.0 and c["top_share"] < 1.0
    assert len(c["sv_head"]) == 5 and c["sv_head"][0] == 1.0


def test_the_report_says_an_unmeasurable_cell_is_unmeasurable(capsys):
    row = {"size": 300, "support": 30, "rho": 0.99, "neurons": 952,
           "topologies": {t: {"error": "RuntimeError: singular"} for t in e237.TOPOLOGIES}}
    assert e237.report([row]) == len(e237.TOPOLOGIES)
    out = capsys.readouterr().out
    assert "UNMEASURABLE" in out and "unmeasurable cells: 4" in out


def test_the_live_artifact_carries_the_collapse_the_finding_quotes():
    """If the artifact is on disk, its whole-G rank must fall over rho for `real` and must be far above one at the
    lowest rho -- the two ends the finding rests on."""
    p = Path("runs/e237_propagator_spectrum.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    cells = {r["rho"]: r["topologies"] for r in d["rows"] if r["size"] == 300}
    grid = sorted(cells)
    ranks = [cells[rho]["real"]["pr_G"] for rho in grid]
    assert ranks[0] > 100 and ranks[-1] < 1.5, ranks
    assert all(b <= a + 1e-9 for a, b in zip(ranks, ranks[1:])), ranks
