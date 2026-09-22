"""Tests for the `e57` seed-robustness arithmetic and the census predicate.

`e57`'s load-bearing claims are that the pool ladder's per-seed signs are unanimous and that no
single seed is worth a whole sem, plus a census of which artifacts store per-seed values. The census
predicate is the one worth pinning: it decides whether a claim *can* be checked, and a version that
counted only the rungs that happen to have the field would report a full ladder as checkable while
silently skipping the rest.
"""

from __future__ import annotations

import numpy as np


def seed_stats(delta: np.ndarray) -> dict:
    """Mean, seed sem, sigma, sign string, leave-one-out minimum sigma and leverage.

    Leverage is ``max_k |mean(-k) - mean| / sem(all)`` -- the same statistic `e47` uses for the C1
    contrasts, on a 0-to-1 scale where 1 means one seed is worth a whole sem on its own.
    """
    n = len(delta)
    sem = float(delta.std(ddof=1) / np.sqrt(n))
    loo, flip, lev = [], False, 0.0
    for i in range(n):
        keep = np.delete(delta, i)
        if keep.size < 3:
            continue
        s = float(keep.std(ddof=1) / np.sqrt(keep.size))
        loo.append(abs(float(keep.mean() / s)))
        if sem:
            lev = max(lev, abs(float(keep.mean()) - float(delta.mean())) / sem)
        if np.sign(keep.mean()) != np.sign(delta.mean()):
            flip = True
    return {"n": n, "delta": float(delta.mean()), "sem": sem,
            "sigma": float(delta.mean() / sem) if sem else float("nan"),
            "signs": "".join("+" if v > 0 else "-" for v in delta),
            "loo_min": min(loo) if loo else float("nan"), "loo_flips": flip, "leverage": lev}


def census_verdict(blocks: list[dict | None]) -> tuple[int, int, bool]:
    """(rungs counted, rungs storing per-seed, checkable) for one artifact's `bio:` entries.

    A rung whose `analytic` block is missing counts toward the total and not toward the stored count,
    so a partially-populated artifact cannot report itself as fully checkable.
    """
    total = len(blocks)
    with_per = sum(1 for b in blocks if b and "excess_per_seed" in b)
    return total, with_per, bool(total) and with_per == total


def test_seed_stats_reproduces_the_pool4_numbers():
    # e57 reads these twelve per-seed deltas for pool4 (bio minus rand on the analytic estimator)
    bio = np.array([0.00149, 0.00144, 0.00126, 0.00184, 0.00168, 0.00145,
                    0.00155, 0.00169, 0.00165, 0.00170, 0.00143, 0.00160])
    rand = np.array([0.01118, 0.00873, 0.00996, 0.01033, 0.01134, 0.01052,
                     0.01062, 0.00979, 0.01094, 0.01009, 0.01053, 0.01088])
    s = seed_stats(bio - rand)
    assert abs(s["delta"] - (-0.00884)) < 5e-5
    assert s["signs"] == "-" * 12          # unanimous, and the sign is the one that favours biology
    assert abs(s["sigma"]) > 40            # seed-only, which e57 shows is inflated by the draw term
    assert s["loo_min"] > 35 and not s["loo_flips"]
    assert s["leverage"] < 1.0


def test_seed_stats_flags_a_sign_flip_when_one_seed_reverses_the_mean():
    # eleven tiny negatives and one large positive: dropping the positive flips the mean
    d = np.concatenate([np.full(11, -0.001), [0.05]])
    s = seed_stats(d)
    assert s["delta"] > 0 and s["loo_flips"] is True


def test_seed_stats_handles_the_eleven_of_twelve_case():
    # pool1's real per-seed deltas: eleven positive and one negative, signs ++++++++-+++
    bio = np.array([0.018308, 0.014556, 0.016608, 0.017460, 0.019721, 0.017323,
                    0.017383, 0.016868, 0.018512, 0.017223, 0.017999, 0.017145])
    rand = np.array([0.018083, 0.014396, 0.016341, 0.017254, 0.019478, 0.017177,
                     0.017214, 0.016615, 0.018551, 0.016954, 0.017883, 0.016864])
    s = seed_stats(bio - rand)
    assert s["signs"] == "++++++++-+++"
    assert abs(s["delta"] - 0.000191) < 5e-6
    assert s["loo_flips"] is False        # one seed against eleven is not enough to flip it
    assert s["sigma"] > 5


def test_census_refuses_a_partially_populated_artifact():
    full = [{"excess_per_seed": [1.0]}] * 3
    partial = [{"excess_per_seed": [1.0]}, {"excess_mean": 1.0}, {"excess_per_seed": [1.0]}]
    missing = [{"excess_mean": 1.0}] * 3
    assert census_verdict(full) == (3, 3, True)
    assert census_verdict(partial) == (3, 2, False)
    assert census_verdict(missing) == (3, 0, False)
    # and an artifact with no `bio:` rungs at all is not "checkable"
    assert census_verdict([]) == (0, 0, False)


def test_census_counts_missing_blocks_against_the_total():
    # e3_real has a topology but no analytic block; it must not report 0/0 as anything but False
    total, with_per, ok = census_verdict([None, None])
    assert (total, with_per, ok) == (2, 0, False)
