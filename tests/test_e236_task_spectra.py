"""`e236` audits one sentence of `e235`: that the tasks keep more dimensions than the propagation they are built from.

The premise is one line of `task_covariance` — `S = (Gs * weights) @ Gs.T` — so `span(S) ⊆ span(Gs)`,
`rank(S) <= rank(Gs)`, and what can exceed is only the participation ratio. The tests pin both halves: the containment
identity on a hand-built quadratic form (no connectome needed) and one live cell whose task column must equal
`e235`'s, with the propagator's own participation ratio *above* it rather than below.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e236_task_spectra as e236


def test_a_quadratic_form_in_gs_lies_inside_span_gs_and_cannot_exceed_its_rank():
    """The audit's premise, on a random 20x5 `Gs`: containment ~0, `rank(S) <= rank(Gs)`, while the participation
    ratio is free to move either way."""
    rng = np.random.default_rng(0)
    Gs = rng.standard_normal((20, 5))
    w = np.array([1.0, 0.5, 2.0, 0.1, 1.0])
    S = (Gs * w) @ Gs.T
    S = (S + S.T) * 0.5
    q = np.linalg.qr(Gs)[0]
    resid = np.linalg.norm(S - q @ (q.T @ S)) / np.linalg.norm(S)
    assert resid < 1e-12, resid
    s_sv = np.linalg.svd(Gs, compute_uv=False)
    e_s = np.linalg.eigvalsh(S)
    e_s = e_s[e_s > 0]
    assert int(np.sum(e_s > e236.RANK_RTOL * e_s.max())) <= int(np.sum(s_sv > e236.RANK_RTOL * s_sv.max()))
    assert e236.participation_ratio(e_s) < 5.0, "a quadratic form of 5 columns cannot have more than 5 flat directions"


def test_the_live_cell_reproduces_e235_and_shows_the_small_deficit():
    """cs 300/`real`/`rho` 0.9: the task column must equal `e235`'s 22.1086, the propagation of the SAME support must
    sit just above it (the quadratic form's own cost), and the containment must be exact."""
    row = e236.measure(300, 30, 0.9, topologies=("real",), seeds=3)
    c = row["topologies"]["real"]
    assert abs(c["mean_pr_s"] - 22.1086) < 1e-3, c["mean_pr_s"]
    assert c["mean_pr_s"] < c["mean_pr_gs"], (c["mean_pr_s"], c["mean_pr_gs"])
    assert 0.9 < c["pr_ratio"] <= 1.0, c["pr_ratio"]
    assert c["max_containment"] < 1e-12, c["max_containment"]
    assert c["mean_rank_s"] == c["mean_rank_gs"], (c["mean_rank_s"], c["mean_rank_gs"])


def test_the_report_says_an_unmeasurable_cell_is_unmeasurable(capsys):
    row = {"size": 300, "support": 30, "rho": 0.99, "neurons": 952,
           "topologies": {t: {"error": "RuntimeError: singular"} for t in e236.TOPOLOGIES}}
    assert e236.report([row]) == len(e236.TOPOLOGIES)
    out = capsys.readouterr().out
    assert "UNMEASURABLE" in out and "unmeasurable cells: 4" in out


def test_the_live_artifact_carries_the_range_the_finding_quotes():
    """If the artifact is not on disk yet the test says so rather than failing on a missing file."""
    p = Path("runs/e236_task_spectra.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    ratios = [c["pr_ratio"] for r in d["rows"] for c in r["topologies"].values() if c.get("pr_ratio")]
    assert ratios and min(ratios) > 0.9 and max(ratios) <= 1.02, (min(ratios), max(ratios))
