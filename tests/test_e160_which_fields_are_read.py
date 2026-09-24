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


STANDARD_ENV = {"omp_num_threads": "unset", "calibration_matmul_s": 0.0003}


def _artifact(name, config, values, arm="naive"):
    """A synthetic one-arm artifact, **carrying an environment**, because a pair that records none is no longer
    evidence about a config field."""
    reps = [{"mean_forgetting": float(v), "final_accuracy": 0.9} for v in values]
    return {"name": name, "config": dict(config),
            "payload": {"environment": dict(STANDARD_ENV), "methods": {arm: {"replicates": reps}}}}


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
    # The replay-settings evidence comes from pairs with a pre-2026-09-23-19:06 artifact in them, so the rule
    # that refuses an unrecorded pair reports "possibly read" for both rather than deciding -- recorded here as
    # a loss rather than quietly asserted as before.
    assert table["replay"]["replay_per_task"] == e160.MAYBE
    assert table["naive"]["replay_per_task"] == e160.MAYBE
    # And the rule earns it back on the cell the corpus has cited most: `fisher_batches` x `naive` was
    # CONFLICTING because of the `_omp1`/`_omp4` thread pairs, and refusing them leaves two 40-replicate
    # recorded-environment pairs that agree -- so it is UNREAD, on better evidence than the conflict had.
    assert table["naive"]["fisher_batches"] == e160.UNREAD
    assert table["naive"].get(e160.ENVIRONMENT_FIELD, e160.UNTESTED) == e160.UNTESTED


# --- the environment as a field, and what an unrecorded one costs ------------------------------------------


def _env_artifact(name, config, values, environment=STANDARD_ENV, arm="naive"):
    """The same, with the environment set explicitly. `environment=None` means the artifact records **none**."""
    a = _artifact(name, config, values, arm=arm)
    if environment is None:
        a["payload"].pop("environment")
    else:
        a["payload"]["environment"] = environment
    return a


def test_a_default_valued_entry_and_an_absent_one_are_the_same_statement():
    """A schema epoch is not an intervention: `e104` predates `frozen_bias`, `e164` records it as False."""
    older = _artifact("a", {"lam": 0.003, "seed0": 0, "repeats": 2}, [0.1, 0.2])
    newer = _artifact("b", {"lam": 0.003, "seed0": 0, "repeats": 2, "frozen_bias": False}, [0.1, 0.2])
    assert e160.effective(older["config"]) == e160.effective(newer["config"])
    # and a real setting of 0 is not dropped along with the False values
    assert e160.effective({"pool_below": 0, "readout_size": 0, "frozen_bias": False}) == {"pool_below": 0,
                                                                                          "readout_size": 0}
    # so the pair is a repeat, not a single-field difference, and no verdict is produced for it
    assert "frozen_bias" not in e160.readership([older, newer], ("naive",))["table"]["naive"]


def test_the_environment_is_a_field_when_both_sides_record_it_and_not_when_one_does_not():
    a = _env_artifact("a", {"lam": 1.0, "seed0": 0, "repeats": 2}, [0.1, 0.2],
                      {"omp_num_threads": "unset", "calibration_matmul_s": 0.0003})
    b = _env_artifact("b", {"lam": 1.0, "seed0": 0, "repeats": 2}, [0.9, 0.8],
                      {"omp_num_threads": "1", "calibration_matmul_s": 0.0003})
    assert e160.readership([a, b], ("naive",))["table"]["naive"][e160.ENVIRONMENT_FIELD] == e160.READ
    # a difference in the machine's *speed* alone is not a difference at all
    c = _env_artifact("c", {"lam": 1.0, "seed0": 0, "repeats": 2}, [0.1, 0.2],
                      {"omp_num_threads": "unset", "calibration_matmul_s": 0.00028})
    d = _env_artifact("d", {"lam": 1.0, "seed0": 0, "repeats": 2}, [0.3, 0.4],
                      {"omp_num_threads": "unset", "calibration_matmul_s": 0.00033})
    assert e160.ENVIRONMENT_FIELD not in e160.readership([c, d], ("naive",))["table"]["naive"]
    # one side unrecorded: the pair is marked with what it cannot resolve, and it cannot be field evidence either
    e = _env_artifact("e", {"lam": 1.0, "seed0": 0, "repeats": 2}, [0.1, 0.2], environment=None)
    res = e160.readership([a, e], ("naive",))["table"]["naive"]
    assert e160.UNIDENTIFIABLE in res


def test_the_corpus_table_has_no_conflict_left_about_a_field():
    """Every remaining conflict is the marker for an unrecorded environment, and the recorded subset has none."""
    from pathlib import Path

    from experiments.e103_reproducibility_audit import load_artifacts

    arms = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")
    arts = load_artifacts(Path("runs"), skip=("e160_field_readership.json",))
    table = e160.readership(arts, arms)["table"]
    fields = sorted({f for v in table.values() for f in v})
    conflicts = [(a, f) for a in arms for f in fields if table[a].get(f) == e160.CONFLICT]
    assert conflicts and {f for _, f in conflicts} == {e160.UNIDENTIFIABLE}
    # the check the table exists for survives everything above
    assert [table[a].get("lam") for a in arms] == [e160.UNREAD, e160.READ, e160.READ, e160.READ, e160.UNREAD]

    recorded = [a for a in arts if isinstance(a["payload"].get("environment"), dict)]
    rtable = e160.readership(recorded, arms)["table"]
    rfields = sorted({f for v in rtable.values() for f in v})
    assert not [f for a in arms for f in rfields if rtable[a].get(f) == e160.CONFLICT]
    # and it costs nothing: on every cell the recorded subset can decide, the full table agrees exactly
    decided = lambda v: v in (e160.READ, e160.UNREAD)          # noqa: E731
    decided_cells = [(a, f) for a in arms for f in rfields if decided(rtable[a].get(f, e160.UNTESTED))]
    assert decided_cells and all(table[a].get(f, e160.UNTESTED) == rtable[a].get(f) for a, f in decided_cells)

    # the two directions, counted: the sharper rule decides 23 more cells (all of them resting on an unrecorded
    # pair), and this rule decides exactly 1 that the sharper one cannot -- the `fisher_batches` upgrade above.
    sharp = e160.readership(arts, arms, environment_field=False)["table"]
    allf = sorted({f for v in table.values() for f in v} | {f for v in sharp.values() for f in v})
    extra = [(a, f) for a in arms for f in allf
             if decided(sharp[a].get(f, e160.UNTESTED)) and not decided(table[a].get(f, e160.UNTESTED))]
    lost = [(a, f) for a in arms for f in allf
            if decided(table[a].get(f, e160.UNTESTED)) and not decided(sharp[a].get(f, e160.UNTESTED))]
    assert len(extra) >= 23 and lost == [("naive", "fisher_batches")], (
        "the sharper rule decides more cells as the corpus grows; the cell it must never decide is the one this "
        "rule upgrades, and that is structural rather than a count")
