"""Tests for the `e36` analysis helpers.

`e36` is a read-only analysis over `runs/`, so the part worth testing is the statistics: the
exact permutation p-value for Spearman's rho (which is the number the finding quotes, at n = 5)
and the lower-tail p-value used to reject an *overstated* standard deviation.  Both are easy to
get subtly wrong -- an upper-tail p where a lower-tail one belongs turns a rejection into an
endorsement -- so they are pinned here.
"""

from __future__ import annotations

import numpy as np

from experiments.e36_geometry_carrier import (
    exact_spearman_p,
    normal_two_sided_p,
    spearman,
    small_difference_p,
)


def test_spearman_hits_plus_and_minus_one_on_monotone_pairs():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert spearman(x, x) == 1.0
    assert spearman(x, x[::-1]) == -1.0
    # ranks, not values: an arbitrary monotone rescaling must not move it
    assert abs(spearman(x, [v ** 3 + 7 for v in x]) - 1.0) < 1e-12


def test_spearman_is_rank_based_and_survives_outliers():
    x = [1.0, 2.0, 3.0, 4.0]
    y = [1.0, 2.0, 3.0, 1e6]
    assert abs(spearman(x, y) - 1.0) < 1e-12


def test_exact_spearman_p_matches_the_enumeration_for_n5():
    # rho = 1 at n = 5 is attained by exactly one of the 120 orderings
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    one, two = exact_spearman_p(x, x)
    assert abs(one - 1 / 120) < 1e-12
    assert abs(two - 2 / 120) < 1e-12


def test_exact_spearman_p_is_large_for_an_unrelated_ordering():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    one, two = exact_spearman_p(x, [3.0, 1.0, 5.0, 2.0, 4.0])
    assert one > 0.2 and two > 0.4


def test_exact_spearman_p_declines_to_guess_beyond_its_enumeration():
    x = list(range(9))
    one, two = exact_spearman_p(x, x)
    assert np.isnan(one) and np.isnan(two)


def test_small_difference_p_is_the_zero_containing_tail():
    # a difference three attributed sds wide is no evidence at all; one of exactly zero is maximal
    assert small_difference_p(3.0) > 0.99
    assert normal_two_sided_p(3.0) < 0.01
    assert small_difference_p(0.0) == 0.0
    assert abs(normal_two_sided_p(0.0) - 1.0) < 1e-12
    # and the two tails partition
    for z in (0.0, 0.3, 1.0, 2.5):
        assert abs(small_difference_p(z) + normal_two_sided_p(z) - 1.0) < 1e-12


def test_small_difference_p_is_monotone_in_z():
    zs = [0.0, 0.1, 0.5, 1.0, 1.96, 3.0]
    ps = [small_difference_p(z) for z in zs]
    assert all(a < b for a, b in zip(ps, ps[1:]))
