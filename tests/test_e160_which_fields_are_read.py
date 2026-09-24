"""`e160`'s table is only as good as its restriction to single-field differences, and that restriction is the test.

Two things are pinned here: **only pairs differing in one field may produce a verdict** (a five-field difference
that moves an arm says nothing about which field it read), and **a field with both an identical pair and a moved
pair must come out CONFLICTING rather than whichever pair the loop reached last** -- the first version of the
readership function had exactly that order-dependence, which is the defect class this project keeps finding in its
own readers. The third test is the substantive one: `lam` must be read by the three penalty methods and unread by
`naive` and `replay`, which is the correction that cost three artifacts on 2026-09-24.
"""

from __future__ import annotations

import numpy as np

from experiments import e160_which_fields_are_read as e160


def _artifact(name, config, values, arm="naive"):
    reps = [{"mean_forgetting": float(v), "final_accuracy": 0.9} for v in values]
    return {"name": name, "config": dict(config), "payload": {"methods": {arm: {"replicates": reps}}}}


def test_a_single_field_difference_that_moves_the_arm_is_READ():
    a = _artifact("a", {"lam": 0.003, "batch": 32, "seed0": 0, "repeats": 3}, [0.1, 0.2, 0.3])
    b = _artifact("b", {"lam": 0.003, "batch": 64, "seed0": 0, "repeats": 3}, [0.4, 0.5, 0.6])
    res = e160.readership([a, b], ("naive",))
    assert res["table"]["naive"]["batch"] == e160.READ
    # and a field that is equal in both is not in the table at all
    assert "lam" not in res["table"]["naive"]


def test_a_single_field_difference_that_leaves_the_arm_identical_is_UNREAD():
    vals = [0.1, 0.2, 0.3]
    a = _artifact("a", {"lam": 0.003, "batch": 32, "seed0": 0, "repeats": 3}, vals)
    b = _artifact("b", {"lam": 0.003, "batch": 64, "seed0": 0, "repeats": 3}, vals)
    assert e160.readership([a, b], ("naive",))["table"]["naive"]["batch"] == e160.UNREAD


def test_both_kinds_of_evidence_give_CONFLICTING_and_not_whichever_came_last():
    vals = [0.1, 0.2, 0.3]
    cfg = {"batch": 32, "seed0": 0, "repeats": 3}
    a = _artifact("a", cfg, vals)
    b = _artifact("b", {"batch": 64, "seed0": 0, "repeats": 3}, vals)            # stayed identical
    c = _artifact("c", {"batch": 128, "seed0": 0, "repeats": 3}, [0.9, 0.9, 0.9])  # moved
    for order in ([a, b, c], [c, b, a], [b, a, c]):
        assert e160.readership(order, ("naive",))["table"]["naive"]["batch"] == e160.CONFLICT


def test_a_multi_field_difference_is_not_evidence_about_any_single_field():
    a = _artifact("a", {"batch": 32, "lam": 0.003, "seed0": 0, "repeats": 3}, [0.1, 0.2, 0.3])
    b = _artifact("b", {"batch": 64, "lam": 0.5, "seed0": 0, "repeats": 3}, [0.9, 0.9, 0.9])
    table = e160.readership([a, b], ("naive",))["table"]["naive"]
    assert table["batch"] == e160.MAYBE and table["lam"] == e160.MAYBE


def test_the_live_corpus_gives_lambda_read_by_the_penalty_methods_and_unread_by_the_others():
    from pathlib import Path
    artifacts = e160.load_artifacts(Path("runs"), skip=("e160_field_readership.json",))
    assert len(artifacts) > 100
    arms = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
    table = e160.readership(artifacts, arms)["table"]
    assert table["naive"]["lam"] == e160.UNREAD and table["replay"]["lam"] == e160.UNREAD
    for arm in ("ewc", "ewc-block", "ewc-block-rand"):
        assert table[arm]["lam"] == e160.READ, f"{arm} must read lam"
    # and the replay settings, which `e140`'s controls rest on
    assert table["replay"]["replay_per_task"] == e160.READ
    assert table["naive"]["replay_per_task"] == e160.UNREAD
