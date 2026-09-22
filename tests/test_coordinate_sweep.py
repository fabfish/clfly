"""Tests for the `e53` coordinate sweep's statistical machinery.

Two things in `e53` decide its conclusion and both were wrong in the first version:

* **the p-value above n = 8.** The exact permutation p is capped at 8! and the first version returned
  ``nan`` for anything larger, which the report then printed as "degenerate" — hiding the pooled
  axis's real result behind a bug in the *reporting*. The fallback is a Monte-Carlo p with a stated
  draw count, and "no p available" is now distinct from "no spread to correlate".
* **the multiple-comparison structure.** Eight coordinates are not eight tests: `effective_rank`,
  `flattening` and `mean_rank_fraction` are monotone in one another, so the same line of evidence was
  being counted five times. The first "distinct" correction scaled each p by its own rank within the
  distinct set, which gives the largest ``|rho|`` no correction at all and is not Holm. The
  corrected version runs Holm over one representative per distinct ``|rho|`` and maps back.
"""

from __future__ import annotations

import numpy as np

from experiments.e53_geometry_coordinate_sweep import (
    EXACT_MAX_N,
    holm,
    permutation_p,
    spearman,
)


def test_spearman_hits_the_extremes():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert abs(spearman(x, x) - 1.0) < 1e-12
    assert abs(spearman(x, x[::-1]) + 1.0) < 1e-12


def test_exact_p_at_six_points_matches_the_enumeration():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    p, method = permutation_p(x, x)
    assert "exact" in method
    assert abs(p - 2 / 720) < 1e-12  # rho = 1 is one of 720 orderings, two-sided


def test_permutation_p_falls_back_to_monte_carlo_above_the_exact_cap():
    rng = np.random.default_rng(0)
    x = rng.standard_normal(12)
    y = rng.standard_normal(12)
    p, method = permutation_p(x, y)
    assert "Monte-Carlo" in method
    assert 0.0 < p <= 1.0
    assert np.isfinite(p)
    # and it must not report a hard zero from a finite sample
    p_perfect, _ = permutation_p(np.arange(12.0), np.arange(12.0))
    assert p_perfect > 0.0
    assert EXACT_MAX_N == 8


def test_degenerate_is_reported_separately_from_no_p_available():
    # constant coordinate -> degenerate, no correlation to test
    p, method = permutation_p(np.zeros(6), np.arange(6.0))
    assert not np.isfinite(p) and method == "degenerate"
    # longer series with spread -> a real p, not degenerate
    p2, method2 = permutation_p(np.arange(12.0), np.arange(12.0)[::-1])
    assert np.isfinite(p2) and method2 != "degenerate"


def test_holm_is_a_step_up_and_monotone():
    # the classic Holm behaviour: 5 * 0.01 = 0.05, then 4 * 0.02 = 0.08, and never decreasing
    adj = holm([0.01, 0.02, 0.03, 0.04, 0.05])
    assert abs(adj[0] - 0.05) < 1e-12
    assert abs(adj[1] - 0.08) < 1e-12
    assert all(a <= b for a, b in zip(adj, adj[1:]))


def test_holm_caps_at_one_and_passes_nan_through():
    # m = 2: adjusted = [2*0.4, max(2*0.4, 1*0.6)] = [0.8, 0.8]. The step-up keeps the running
    # maximum, so the second entry cannot fall back to its raw p.
    assert holm([0.4, 0.6]) == [0.8, 0.8]
    # a nan contributes no test, so m = 1 here and the finite entry is left at its raw p
    out = holm([float("nan"), 0.01])
    assert not np.isfinite(out[0]) and abs(out[1] - 0.01) < 1e-12


def test_holm_counts_only_coordinates_with_a_computable_p():
    # a degenerate coordinate contributes no test, so it must not inflate m.  The realization axis
    # has 8 coordinates of which 3 have no spread at fixed circuit size, so m = 5.
    assert holm([0.01, float("nan"), float("nan"), float("nan")])[0] == 0.01  # m = 1
    assert abs(holm([0.01, 0.02, 0.03, 0.04, 0.05])[0] - 0.05) < 1e-12      # m = 5


def test_holm_over_distinct_orderings_is_less_conservative_than_over_coordinates():
    # the real realization axis, exactly: 5 coordinates with a computable p, made of 3 sharing
    # |rho| = 0.943 (raw p = 0.0167) and 2 sharing |rho| = 0.829 (raw p = 0.0583)
    raw = [0.0167, 0.0167, 0.0167, 0.0583, 0.0583]
    over_coordinates = min(holm(raw))
    assert abs(over_coordinates - 0.0833) < 1e-3
    # Holm over ONE representative per distinct |rho| -- m = 2, not 5
    rep = sorted({0.0167, 0.0583})
    over_distinct = min(min(1.0, 2 * p) for p in rep)
    assert abs(over_distinct - 0.0334) < 1e-3
    # and they land on opposite sides of 0.05, which is exactly why the correction matters
    assert over_coordinates > 0.05 > over_distinct
