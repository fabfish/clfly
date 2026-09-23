"""The two forgetting definitions in `e123` must be the same formula, with loss and accuracy swapped.

`e123` claims the loss-valued retention matrix is a better *estimator* than the accuracy-valued one, and the
whole claim rests on the two quantities measuring the same thing. So the test is that it is the same
expression — `retention_loss` gives `L[T-1][j] - min_k L[k][j]`, the accuracy matrix gives
`max_k R[k][j] - R[T-1][j]` — evaluated on hand-built matrices where the answer is arithmetic, not training.

The case that matters is the **non-monotone column**: if loss fell below its just-fitted value at some later
checkpoint, the `min` must find it, or the loss form would not mirror the accuracy form (whose `max` searches
every checkpoint for the same reason).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from experiments.e123_loss_metric import (accuracy_forgetting, loss_forgetting,
                                          loss_forgetting_log_ratio)

NAN = float("nan")


def test_nothing_retained_gives_exactly_zero():
    """If every checkpoint's loss on task j is the just-fitted one, the forgetting is 0 and not a small number."""
    L = [[0.0018, NAN, NAN],
         [0.0018, 0.0015, NAN],
         [0.0018, 0.0015, 0.0012]]
    assert loss_forgetting(L) == 0.0
    assert loss_forgetting_log_ratio(L) == 0.0


def test_the_loss_form_is_the_accuracy_form_with_the_directions_swapped():
    L = [[0.0018, NAN, NAN],
         [0.05, 0.0015, NAN],
         [0.097, 0.029, 0.0012]]
    R = [[0.95, NAN, NAN],
         [0.80, 0.92, NAN],
         [0.70, 0.88, 0.60]]
    # both are the mean over the T-1 forgettable tasks of (final - best) in the metric's own direction
    assert loss_forgetting(L) == pytest.approx(np.mean([0.097 - 0.0018, 0.029 - 0.0015]))
    assert accuracy_forgetting({"retention": R}) == pytest.approx(np.mean([0.95 - 0.70, 0.92 - 0.88]))


def test_the_min_searches_every_checkpoint_not_only_the_diagonal():
    """A column whose loss dips below its just-fitted value: the `min` must find it, as the accuracy `max` does.

    Without this the loss form would silently differ from the accuracy form in exactly the case the accuracy
    form was written to handle.
    """
    L = [[0.0018, NAN, NAN],
         [0.05, 0.0015, NAN],
         [0.097, 0.0009, 0.0012]]          # task 1 ends BETTER than it was after its own task
    assert loss_forgetting(L) == pytest.approx(np.mean([0.097 - 0.0018, 0.0009 - 0.0009]))
    # and the log-ratio companion reports the same dip as a ratio rather than a difference
    assert loss_forgetting_log_ratio(L) == pytest.approx(
        np.mean([math.log(0.097 / 0.0018), math.log(0.0009 / 0.0009)]))


def test_both_forms_are_non_negative_by_construction():
    """`min` includes the final checkpoint and `max` includes it too, so neither can go negative."""
    rng = np.random.default_rng(0)
    for _ in range(20):
        T = 3
        L = np.full((T, T), NAN)
        R = np.full((T, T), NAN)
        for k in range(T):
            for j in range(k + 1):
                L[k, j] = float(np.exp(rng.normal()))       # spans orders of magnitude, as the real loss does
                R[k, j] = float(rng.random())
        assert loss_forgetting(L.tolist()) >= 0.0
        assert accuracy_forgetting({"retention": R.tolist()}) >= 0.0


def test_a_single_task_suite_has_no_forgetting_to_measure():
    """T = 1 means no task has been superseded, and the metric is defined as 0 rather than as nan."""
    assert loss_forgetting([[0.0018]]) == 0.0
    assert accuracy_forgetting({"retention": [[0.95]]}) == 0.0
