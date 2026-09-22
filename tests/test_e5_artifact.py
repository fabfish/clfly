"""Regression guard for the `e41` claim about `e5`'s artifact.

Two numbers from `2026-09-22-e5-does-not-reproduce-its-own-artifact.md` are load-bearing enough to
pin: that the published Spearman of -0.75 is reproduced *exactly* by changing one cell of the stored
seed-0 row, and that the stored row itself gives -0.9643.  If either changes, the finding's central
argument -- that the headline number and the U-shape both come from that single cell -- no longer
holds and must be rechecked.

`runs/` is gitignored, so the test skips cleanly when the artifact is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scipy.stats import spearmanr

ARTIFACT = Path("runs/e5_anisotropy.json")
PUBLISHED_RHO = -0.75

pytestmark = pytest.mark.skipif(
    not ARTIFACT.exists(), reason="runs/e5_anisotropy.json not present (runs/ is gitignored)")


def _seed0_row():
    with open(ARTIFACT, encoding="utf-8") as fh:
        d = json.load(fh)
    pts = sorted((p for p in d["points"] if p["seed"] == 0), key=lambda p: p["kappa"])
    return ([p["flattening"] for p in pts],
            [p["gap_ewc"] for p in pts],
            [p["kappa"] for p in pts])


def test_the_artifact_is_the_three_seed_rerun_not_the_quoted_one_seed():
    with open(ARTIFACT, encoding="utf-8") as fh:
        d = json.load(fh)
    assert d["config"]["seeds"] == 3
    assert len({p["seed"] for p in d["points"]}) == 3


def test_stored_seed0_rho_is_minus_0_964_not_the_published_minus_0_75():
    flat, gap, _ = _seed0_row()
    assert abs(float(spearmanr(flat, gap)[0]) - (-0.9643)) < 5e-4


def test_one_substituted_cell_reproduces_the_published_spearman_exactly():
    flat, gap, kappas = _seed0_row()
    assert kappas[0] == 0.0
    sub = list(gap)
    sub[0] = 0.139  # the gap:EWC published for kappa = 0
    assert abs(float(spearmanr(flat, sub)[0]) - PUBLISHED_RHO) < 1e-9


def test_that_same_cell_is_what_moves_the_u_shape_minimum():
    _, gap, kappas = _seed0_row()
    sub = list(gap)
    sub[0] = 0.139
    assert kappas[gap.index(min(gap))] == 0.0       # stored: minimum at kappa = 0
    assert kappas[sub.index(min(sub))] == 0.5       # published: minimum at kappa = 0.5


def test_the_association_is_not_significant_when_pooled_or_averaged():
    with open(ARTIFACT, encoding="utf-8") as fh:
        d = json.load(fh)
    pts = d["points"]
    flat = [p["flattening"] for p in pts]
    gap = [p["gap_ewc"] for p in pts]
    absx = [p["gap_ewc"] * p["oracle_final"] for p in pts]
    assert spearmanr(flat, gap)[1] > 0.2            # pooled relative: p = 0.216
    assert spearmanr(flat, absx)[1] > 0.5           # pooled absolute: p = 0.862


def test_only_one_of_the_three_seeds_shows_the_association():
    with open(ARTIFACT, encoding="utf-8") as fh:
        d = json.load(fh)
    rhos = []
    for s in (0, 1, 2):
        m = [p for p in d["points"] if p["seed"] == s]
        rhos.append(round(float(spearmanr([p["flattening"] for p in m],
                                         [p["gap_ewc"] for p in m])[0]), 3))
    assert rhos == [-0.964, -0.321, 0.107]
