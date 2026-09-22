"""Tests for the `e38` variance-budget helpers.

Three small statistics decide the network line's error bars, and each is easy to get subtly wrong:
the chi-square interval on a sample sd (a wrong quantile direction silently narrows it), the
Fisher-z interval on a correlation (undefined at n <= 3, where the project was quoting point
estimates), and the replicate requirement.  They are pinned here.
"""

from __future__ import annotations

import numpy as np

from experiments.e38_variance_budget import corr_interval, required_repeats, sd_interval


def test_sd_interval_brackets_the_estimate_and_is_wide_at_two_df():
    lo, hi = sd_interval(0.0422, 2)
    assert lo < 0.0422 < hi
    # at 2 df the 95% interval spans a factor of ~12, which is the whole reason the e38 finding
    # exists: a "training remainder" quoted from three replicates is barely bounded
    assert 10 < hi / lo < 14


def test_sd_interval_narrows_as_degrees_of_freedom_grow():
    widths = [hi / lo for lo, hi in (sd_interval(0.04, df) for df in (2, 4, 8, 30))]
    assert all(a > b for a, b in zip(widths, widths[1:]))


def test_sd_interval_is_undefined_for_degenerate_input():
    for args in ((0.0, 2), (0.04, 0), (float("nan"), 2)):
        lo, hi = sd_interval(*args)
        assert np.isnan(lo) and np.isnan(hi)


def test_corr_interval_refuses_the_three_replicate_case():
    # Fisher z has standard error 1/sqrt(n-3), which does not exist at n = 3
    for n in (0, 1, 2, 3):
        lo, hi = corr_interval(0.97, n)
        assert np.isnan(lo) and np.isnan(hi)


def test_corr_interval_contains_the_estimate_and_the_expected_width():
    lo, hi = corr_interval(0.02, 9)
    assert lo < 0.02 < hi
    # 1.96/sqrt(6) = 0.80 in z, i.e. +/-0.66 on the correlation -- which is 2/3 of the range and is
    # why the pairing question is unresolved rather than refuted
    assert -0.75 < lo < -0.5 and 0.5 < hi < 0.75
    assert lo < 0.97 and hi > -0.98  # both n = 3 extremes are inside it


def test_corr_interval_is_degenerate_at_perfect_correlation():
    lo, hi = corr_interval(1.0, 9)
    assert np.isnan(lo) and np.isnan(hi)


def test_required_repeats_scales_as_the_inverse_square_of_the_effect():
    a = required_repeats(0.01, 0.05)
    b = required_repeats(0.02, 0.05)
    assert abs(a / b - 4.0) < 1e-9
    # and with the sd: doubling the spread needs four times the replicates
    assert abs(required_repeats(0.01, 0.10) / a - 4.0) < 1e-9
    assert required_repeats(0.0, 0.05) == float("inf")
