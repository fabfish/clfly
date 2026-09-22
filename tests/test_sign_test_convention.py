"""Tests for the `e56` sign test, whose convention bug this file exists to prevent.

The bug: `e42` has twelve per-seed correlations, one of which is **exactly zero**. The first version
of the analysis computed `binomtest(2, 12)` -- treating the tie as a positive and asking about the two
negatives -- and reported p = 0.039. Counting the tie *against* the positives gives 0.146. The
standard treatment drops it: `binomtest(9, 11)` = 0.065. A 1.7x error in a headline p-value, from an
implicit convention.

So the helper takes the three counts apart and applies the convention in one place. These tests pin
the three conventions' values so the choice is visible in the code rather than in a reader's head.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import binomtest

from experiments.e56_metric_pathology_both_ways import excess_of, sign_test


def test_the_three_conventions_disagree_by_a_factor_of_1_7_on_the_real_data():
    # e42's twelve per-seed rho on the prescribed metric
    per = np.array([-0.929, 0.214, 0.071, -0.500, 0.643, 0.643,
                    0.929, 0.321, 0.429, 0.750, 0.607, 0.000])
    pos, neg, tied, p = sign_test(per)
    assert (pos, neg, tied) == (9, 2, 1)
    # the convention this module uses: ties dropped
    assert abs(p - binomtest(9, 11).pvalue) < 1e-12
    assert abs(p - 0.0654) < 5e-4
    # the two wrong ones, for the record
    assert abs(binomtest(2, 12).pvalue - 0.0386) < 5e-4   # tie counted AS positive
    assert abs(binomtest(3, 12).pvalue - 0.1460) < 5e-4   # tie counted AGAINST
    assert binomtest(2, 12).pvalue < p < binomtest(3, 12).pvalue


def test_ties_are_counted_not_silently_dropped():
    per = np.array([1.0, 1.0, 0.0, 0.0, -1.0])
    pos, neg, tied, p = sign_test(per)
    assert (pos, neg, tied) == (2, 1, 2)
    assert abs(p - binomtest(2, 3).pvalue) < 1e-12


def test_all_ties_gives_nan_rather_than_a_fabricated_p():
    _, _, tied, p = sign_test(np.zeros(5))
    assert tied == 5 and not np.isfinite(p)


def test_an_exactly_null_split_gives_p_one():
    # e52 on the prescribed metric is 6 positive / 4 negative / 2 tied
    per = np.array([0.143, 0.214, 0.357, 0.429, 0.821, 0.0,
                    -0.286, 0.393, -0.643, -0.750, -0.786, 0.0])
    pos, neg, tied, p = sign_test(per)
    assert (pos, neg, tied) == (6, 4, 2)
    assert abs(p - binomtest(6, 10).pvalue) < 1e-12
    assert p > 0.7  # a null, and it must not read as anything else


def test_excess_of_handles_both_artifact_generations():
    # e42 and later store the field; e5_anisotropy predates it
    assert abs(excess_of({"excess_ewc": 0.01, "gap_ewc": 1.0, "oracle_final": 0.05}) - 0.01) < 1e-12
    assert abs(excess_of({"gap_ewc": 0.4, "oracle_final": 0.05}) - 0.02) < 1e-12
