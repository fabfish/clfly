"""Tests for the `e43` replication comparison.

`e43` decides whether `runs/e5_anisotropy.json` is the live output of the current code or a stale
file, by comparing it cell for cell against another run of the same configuration. The comparison
itself is the thing worth pinning: a tolerance that is too tight calls a perfect replication a
mismatch on print rounding, and one that is too loose calls a real disagreement a match. Both
directions were hit while writing it -- the log comparison failed at ratio 0.99 on 4-decimal
rounding before the log tolerances were separated from the artifact ones.

The comparison functions are pure, so they are tested on synthetic entries and do not need `runs/`.
"""

from __future__ import annotations

from experiments.e43_e5_replication import LOG_TOL, TOL, by_key, compare


def _entry(points):
    return {"config": {}, "points": points}


def _pt(seed, kappa, flat=0.5, effrank=10.0, gap=0.1, excess=0.01):
    return {"seed": seed, "kappa": kappa, "flattening": flat, "effective_rank": effrank,
            "gap_ewc": gap, "excess_ewc": excess}


def test_by_key_is_keyed_on_seed_and_float_kappa():
    keyed = by_key(_entry([_pt(0, 0.0), _pt(1, 2.5)]))
    assert set(keyed) == {(0, 0.0), (1, 2.5)}
    # kappa arrives from JSON as a float, so an int 0 and a float 0.0 must key the same way
    assert (0, 0.0) in by_key(_entry([_pt(0, 0)]))


def test_identical_entries_agree_on_every_shared_row():
    a = _entry([_pt(0, 0.0), _pt(0, 1.0), _pt(1, 0.0)])
    shared, agreed, bad = compare(a, a, "same")
    assert (shared, agreed, bad) == (3, 3, [])


def test_a_difference_inside_tolerance_is_not_a_mismatch():
    a = _entry([_pt(0, 0.0, flat=0.7587, effrank=55.1, gap=0.0621)])
    b = _entry([_pt(0, 0.0, flat=0.7587 + TOL["flattening"] * 0.9,
                    effrank=55.1 + TOL["effective_rank"] * 0.9,
                    gap=0.0621 + TOL["gap_ewc"] * 0.9)])
    shared, agreed, bad = compare(a, b, "barely-different")
    assert (shared, agreed, bad) == (1, 1, [])


def test_a_difference_beyond_tolerance_is_a_mismatch_and_is_reported():
    a = _entry([_pt(0, 0.0, gap=0.0621)])
    b = _entry([_pt(0, 0.0, gap=0.139)])
    shared, agreed, bad = compare(a, b, "different")
    assert shared == 1 and agreed == 0
    assert len(bad) == 1
    seed, kappa, field, ref, cand, ratio = bad[0]
    assert (seed, kappa, field) == (0, 0.0, "gap_ewc")
    assert ref == 0.0621 and cand == 0.139 and ratio > 100


def test_only_shared_keys_are_compared():
    a = _entry([_pt(0, 0.0), _pt(0, 1.0)])
    b = _entry([_pt(0, 0.0)])
    shared, agreed, bad = compare(a, b, "subset")
    assert (shared, agreed, bad) == (1, 1, [])


def test_the_log_tolerance_is_strictly_looser_than_the_artifact_tolerance():
    # the log prints 4 dp for flatten/gap and 1 dp for the effective rank; if these ever coincide,
    # a perfect replication starts failing on print rounding (it did, at 0.99 of tolerance)
    for field in ("flattening", "effective_rank", "gap_ewc"):
        assert LOG_TOL[field] > TOL[field]
