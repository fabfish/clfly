"""The matched-random control protocol.

A biological partition is always compared against a **group-size-matched random partition**,
because otherwise it could "win" merely by having larger groups. What that comparison means
depends on a choice nobody usually states: *which* random partition.

There are two different questions and they need two different controls.

**"Is the biological grouping better than a random grouping of this size?"** This is a claim
about the *population* of random partitions, so the control must be averaged over draws, and
the draw-to-draw spread is part of the error bar. ``sd_across_draws`` measures it: on this
substrate it is ~1.1e-3 for coarse partitions (2-10 groups) and ~4e-5 for near-diagonal ones,
against seed sems of ~2e-4 — so for coarse partitions a single-draw sigma understates the
uncertainty several-fold (``docs/findings/2026-09-22-control-drawn-once.md``).

**"Is rung X better than rung Y?"** This is a claim about the *curve*, and it lives or dies on
whether the difference between two deltas exceeds the noise. Because the draw spread is a
*per-observation* standard deviation and not a standard error, it does not shrink with more
seeds: ``draws_needed`` inverts the relation and usually returns a number large enough to show
that the claim is out of reach at any affordable budget. That is a result, not a failure —
it says which questions this substrate can answer.

Keeping the two separate matters. Averaging the control is cheap and worth doing for the
population claim; it is *not* a route to resolving fine structure in a curve, and pretending
otherwise would spend weeks of compute on a question whose answer is already determined by the
draw spread being larger than the effect.
"""

from __future__ import annotations

import numpy as np

from .analytic import analytic_excess
from ..lgcl.bases import random_partition


def averaged_random_control(sequences, labels, rng, draws: int = 1) -> dict:
    """Matched-random control, averaged over ``draws`` independent partitions.

    Returns the same fields :func:`~clfly.bench.analytic.analytic_excess` does, so it can be
    dropped in wherever a single control was used, plus:

    - ``control_draws`` -- how many partitions were averaged;
    - ``control_means`` -- each draw's mean excess, so the spread is visible rather than
      summarised;
    - ``sd_across_draws`` -- the standard deviation of those means, i.e. the draw-to-draw
      component a single-draw sem omits.

    ``excess_per_seed`` is the mean over draws of the per-seed excesses, which keeps the
    downstream paired contrasts working: for seed ``i`` the control value is the average of
    that seed's excess under each draw, and ``paired_delta`` then recovers exactly the right
    sem, ``sqrt(sigma_seed^2/N + sd_across_draws^2/(draws*N))``.

    With ``draws = 1`` the result is identical to the old single-draw behaviour, so this is a
    strict generalisation.
    """
    per_draw = [analytic_excess(sequences, random_partition(labels, rng))
                for _ in range(draws)]
    means = np.array([c["excess_mean"] for c in per_draw])
    stack = np.array([c["excess_per_seed"] for c in per_draw])
    per_seed = stack.mean(axis=0)
    n = per_seed.size
    out = {
        "n": n,
        "excess_mean": float(per_seed.mean()),
        "excess_sd": float(per_seed.std(ddof=1)) if n > 1 else 0.0,
        "excess_sem": float(per_seed.std(ddof=1) / np.sqrt(n)) if n > 1 else 0.0,
        "ewc_mean": float(np.mean([c["ewc_mean"] for c in per_draw])),
        "oracle_mean": float(per_draw[0]["oracle_mean"]),
        "gap_of_means": float(per_seed.mean() / per_draw[0]["oracle_mean"])
        if per_draw[0]["oracle_mean"] else float("nan"),
        "excess_per_seed": [float(x) for x in per_seed],
        "control_draws": draws,
        "control_means": [float(m) for m in means],
        "sd_across_draws": float(means.std(ddof=1)) if draws > 1 else 0.0,
    }
    return out


def delta_sem(sem_seed: float, sd_draw: float, draws: int = 1) -> float:
    """Sem of a delta ``biological - control`` with the draw component included.

    ``sem_seed`` is the seed sem of the difference (paired or not, as the caller computed it)
    and ``sd_draw`` is the draw-to-draw sd of a *single* control's mean. The draw term is a
    per-observation spread, so it is divided by ``sqrt(draws)`` and **not** by ``sqrt(n_seeds)``
    -- more seeds do not make a single control draw less arbitrary.
    """
    return float(np.hypot(sem_seed, sd_draw / np.sqrt(draws)))


def draws_needed(delta: float, sem_seed: float, sd_draw: float,
                 target_sigma: float = 3.0, contrast: bool = True) -> float:
    """How many control draws a claim needs, or ``inf`` if no number of draws suffices.

    ``contrast=True`` treats the claim as the difference between *two* rungs' deltas (each with
    its own control draw, so the draw variance counts twice); ``contrast=False`` treats it as a
    single rung's delta against zero.

    Returns ``inf`` when even averaging the draw noise to nothing leaves the seed sem above the
    target -- in that case the binding constraint is the seed budget, and the caller should be
    told so rather than given a large finite number.
    """
    target = abs(delta) / target_sigma
    want = target ** 2
    factor = 2.0 if contrast else 1.0
    floor = factor * sem_seed ** 2
    if want <= floor:
        return float("inf")
    return float(factor * sd_draw ** 2 / (want - floor))


def concentration(labels) -> float:
    """``sum_g s_g^2 / d^2`` for a partition — how much of the covariance it constrains.

    This is the quantity that predicts a matched-random control's **draw-to-draw** sd, better
    than the group count does. Measured on this substrate (`docs/findings/2026-09-22-draw-sd-
    mechanism.md`):

    | ``sum s^2/d^2`` | 0.006 | 0.020 | 0.325 | 0.498 | 0.678 | 0.754 |
    |---|---|---|---|---|---|---|
    | draw sd | 9e-5 | 4e-5 | 9.3e-4 | *predicted ~1.0e-3* | 1.06e-3 | 1.08e-3 |

    The mechanism is that a permutation changes little when the partition is made of singletons
    (most of ``sum s^2`` is then in pairs that are identical under any permutation) and a great
    deal when one group holds most of the neurons, because then the reshuffle decides *which*
    neurons share that group. It is the concentration, not the number of groups, that sets the
    scale — which is why `side`, a **balanced** 4-group partition at 0.498, belongs with the
    coarse partitions rather than with the fine ones.

    Exact and cheap: no filter is run.
    """
    labels = np.asarray(labels)
    if labels.size == 0:
        return 0.0
    sizes = np.bincount(labels).astype(np.float64)
    return float((sizes ** 2).sum() / labels.size ** 2)
