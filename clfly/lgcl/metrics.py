"""The decomposed forgetting the benchmark block prescribes and the corpus has never stored.

`clfly.lgcl.model.summarize` computes the conventional forgetting measure and says in its own note why that is not
enough:

    NOTE: this metric rewards shrinkage bias -- an estimator that pulls toward zero can score well on it while being
    wrong (LGCL v8 audit note).  Use :func:`clfly.lgcl.metrics.decompose_forgetting` when that matters.

That note referred to this module, and until now the module did not exist (`e303`). What it can decompose is set by
what the artifacts record, so the definition below is stated in the corpus's own terms rather than in LGCL's.

**What the corpus stores.** Every one of its 334 arm artifacts carries a lower-triangular `retention` matrix
`R[t][j]`: the accuracy on task `j` measured right after the arm finished learning task `t`. Its diagonal is the
level each task reached at the time it was learned and its last row is where each task ended up.

**What this module splits.** For one task, with `a = R[j][j]` the level the task reached, `b = R[T-1][j]` the level
it ended at and `c` the ceiling (1.0 for accuracy):

    c - b  =  (c - a)  +  (a - b)
    shortfall   unlearned   lost

The split is **exact and has no free parameter**, and the two terms are different failures with the same signature
under the conventional measure: `lost` is what the arm took and gave back, which is what `mean_forgetting` computes,
and `unlearned` is what the arm never had, which the conventional measure cannot see at all -- an estimator that
never solved a task has nothing to lose, so it scores as having forgotten nothing.

**What that is not.** LGCL's own decomposition separates an *irreducible* drift term from *estimation* degradation,
and the irreducible part is defined against a reference estimator (the Kalman/RTS line in `clfly/bench/oracle.py`),
which no artifact in this corpus carries for its own arms. **The split above is therefore a different decomposition
of the same shortfall**: it is exact, it is computable for every arm, and it separates the failure the block names
from the one it does not -- it does not claim to be LGCL's, and a caller that wants LGCL's needs a reference line.
"""

from __future__ import annotations

from typing import Sequence


def levels(retention: Sequence[Sequence[float | None]]) -> tuple[list[float], list[float]]:
    """``(reached, ended)`` -- the matrix's diagonal, and its last row.

    The matrix is lower triangular, so the diagonal is the level each task reached when it was learned and the last
    row is where every task finished. A `None` where a number is required is an error rather than a zero: an
    artifact that did not record a cell must not be read as having scored nothing on it.
    """
    if not retention:
        raise ValueError("a retention matrix needs at least one row")
    n = len(retention)
    if any(len(row) != n for row in retention) or any(retention[j][j] is None for j in range(n)):
        raise ValueError("a retention matrix must be square with a diagonal")
    if any(retention[n - 1][j] is None for j in range(n)):
        raise ValueError("a retention matrix's last row must be complete")
    return [float(retention[j][j]) for j in range(n)], [float(retention[n - 1][j]) for j in range(n)]


def decompose_forgetting(retention: Sequence[Sequence[float | None]], ceiling: float = 1.0) -> dict:
    """One arm's retention matrix split into the part lost and the part never learned, task by task.

    Returns the two terms per task, their per-task sum (the shortfall against `ceiling`), and the arm-level totals
    `lost`, `unlearned` and `unlearned_share`. The share is `None` for an arm with no shortfall at all, which is a
    perfect arm rather than a failure, and every total is a mean over tasks so arms of different lengths compare.
    """
    reached, ended = levels(retention)
    n = len(reached)
    lost = [reached[j] - ended[j] for j in range(n)]
    unlearned = [ceiling - reached[j] for j in range(n)]
    shortfall = [ceiling - ended[j] for j in range(n)]
    tot_lost = sum(lost) / n
    tot_unlearned = sum(unlearned) / n
    whole = tot_lost + tot_unlearned
    return {"reached": reached, "ended": ended, "lost": lost, "unlearned": unlearned,
            "shortfall": shortfall, "ceiling": ceiling, "n_tasks": n,
            "lost_mean": tot_lost, "unlearned_mean": tot_unlearned, "shortfall_mean": whole,
            "unlearned_share": tot_unlearned / whole if whole else None}


def residual(reading: dict) -> float:
    """The largest disagreement between the split and the shortfall it splits -- what makes the split *exact*.

    A caller reports this rather than trusting the arithmetic: a decomposition whose two terms do not add to the
    quantity they decompose is a different reading of the matrix, not a decomposition of it.
    """
    return max((abs(reading["lost"][j] + reading["unlearned"][j] - reading["shortfall"][j])
                for j in range(reading["n_tasks"])), default=0.0)
