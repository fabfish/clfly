"""Tests for the `e55` resolution arithmetic and its two ingest paths.

`e55`'s numbers decide how a plan rule is worded, so the arithmetic is pinned: the
minimum-detectable relation, the variance decomposition that recovers the arm correlation from the
difference's sd, and the fallback that reads `excess_ewc` when present and derives it from
`gap_ewc x oracle_final` when a run predates the field. The last one matters because `e5_anisotropy`
is the artifact the rule was written from and it predates the field.
"""

from __future__ import annotations

import numpy as np

from experiments.e55_seed_resolution_of_excess import excess_of

#: 2.8 x sem is the 80%-power minimum detectable difference at a two-sided 5% test; e55 quotes it
#: throughout and the constant is visible here so a change to it is a change to every number.
Z_80 = 2.8


def min_detectable(sd: float, n: int) -> float:
    return Z_80 * sd / np.sqrt(n)


def test_min_detectable_falls_as_the_root_of_n():
    assert abs(min_detectable(0.02, 12) - 0.016166) < 1e-5
    assert abs(min_detectable(0.02, 3) - 0.032332) < 1e-5
    assert abs(min_detectable(0.02, 48) - 0.008083) < 1e-5
    # quadrupling n halves it
    assert abs(min_detectable(0.02, 12) / min_detectable(0.02, 48) - 2.0) < 1e-9


def test_the_plan_figure_is_conservative_at_every_n_e55_reports():
    # the plan says "below ~0.05 are not resolvable"; e55 measures the median across-seed sd of
    # excess(real) at 0.01971 on e42
    for n in (3, 6, 12):
        assert min_detectable(0.01971, n) < 0.05


def test_arm_correlation_recovered_from_the_difference_sd():
    # var(diff) = var_a + var_b - 2 r sqrt(var_a var_b), which is how e55 reports r = +0.29 for the
    # cs = 800 contrast rather than assuming the arms are independent
    sd_a, sd_b, sd_d = 0.00083, 0.00062, 0.00088
    r = (sd_a ** 2 + sd_b ** 2 - sd_d ** 2) / (2 * sd_a * sd_b)
    assert abs(r - 0.29) < 0.02
    # independent arms would give a larger difference sd than observed
    assert np.hypot(sd_a, sd_b) > sd_d


def test_excess_of_uses_the_stored_field_when_present():
    assert abs(excess_of({"excess_ewc": 0.0123, "gap_ewc": 1.0, "oracle_final": 0.5}) - 0.0123) < 1e-12


def test_excess_of_derives_it_when_the_field_is_absent():
    # e5_anisotropy predates the field, so the rule's own artifact needs the fallback
    got = excess_of({"gap_ewc": 0.4, "oracle_final": 0.05})
    assert abs(got - 0.02) < 1e-12


def test_excess_of_prefers_the_stored_field_over_the_derivation():
    # if the two ever disagree, the stored value is the one the run actually computed
    pt = {"excess_ewc": 0.999, "gap_ewc": 0.4, "oracle_final": 0.05}
    assert excess_of(pt) == 0.999
