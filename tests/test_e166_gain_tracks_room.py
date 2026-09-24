"""`e166`'s design is a pairing rule plus two signs, and both are easy to get wrong in the same direction.

The pairing rule is the whole design: a pair must differ in **exactly one** `config` field, must share an arm and
a replicate count (so replicate *i* is seed *i* on both sides), and must not differ in `seed0` -- a pair that
differs in the seeds is not a pair. The signs are `gain = naive - arm` (so positive means the penalty *wins*) and
the room account's prediction that the level step and the gain step share a sign. And the negative control is the
unit's own falsifier: `fisher_batches` cannot move `naive` (`e160` derives it as unread), so if its pairs moved
the level the join would be broken rather than informative.
"""

from __future__ import annotations

import numpy as np
import pytest

from experiments import e166_gain_tracks_room as e166


def artifact(name, config, arms, replicates):
    """A payload shaped like a run's, in `load_artifacts`' envelope, one `mean_forgetting` per replicate."""
    return {"name": name, "config": config,
            "payload": {"methods": {m: {"replicates": [{"mean_forgetting": v} for v in values]}
                                    for m, values in replicates.items()}}}


def cand(*args, **kwargs):
    """`candidates()` over one hand-built artifact -- the real path, not a hand-built candidate record."""
    return e166.candidates([artifact(*args, **kwargs)])[0]


def test_normalise_treats_an_unset_field_as_absent_and_drops_the_output_path():
    a = e166.normalise({"lam": 0.003, "anchor_bias": None, "json_out": "runs/x.json"})
    b = e166.normalise({"lam": 0.003, "json_out": "runs/y.json"})
    assert a == b == {"lam": 0.003}


def test_a_pair_differing_in_the_seeds_is_not_a_pair_and_neither_is_one_differing_in_two_fields():
    one = cand("a", {"seed0": 0, "lam": 1.0}, ["naive", "ewc"], {"naive": [0.1], "ewc": [0.05]})
    seeds = cand("b", {"seed0": 7, "lam": 1.0}, ["naive", "ewc"], {"naive": [0.1], "ewc": [0.05]})
    two = cand("c", {"seed0": 0, "lam": 2.0, "iters": 9}, ["naive", "ewc"],
               {"naive": [0.1], "ewc": [0.05]})
    half = cand("d", {"seed0": 0, "lam": 1.0}, ["naive", "ewc"], {"naive": [0.1, 0.2], "ewc": [0.05, 0.1]})
    assert e166.pairs([one, seeds]) == []
    assert e166.pairs([one, two]) == []
    assert e166.pairs([one, half]) == []          # different replicate counts cannot be paired
    lam = cand("e", {"seed0": 0, "lam": 2.0}, ["naive", "ewc"], {"naive": [0.1], "ewc": [0.05]})
    got = e166.pairs([one, lam])
    assert len(got) == 1 and got[0]["field"] == "lam" and got[0]["from"] == 1.0 and got[0]["to"] == 2.0


def test_the_two_steps_are_paired_differences_and_the_gain_is_naive_minus_arm():
    a = cand("a", {"lam": 1.0}, ["naive", "ewc"], {"naive": [0.10, 0.20, 0.30], "ewc": [0.06, 0.18, 0.24]})
    b = cand("b", {"lam": 2.0}, ["naive", "ewc"], {"naive": [0.14, 0.24, 0.34], "ewc": [0.04, 0.16, 0.22]})
    row = e166.rows_for(e166.pairs([a, b])[0])[0]
    assert row["level"]["change"] == pytest.approx(0.04)          # the level rose
    assert row["gain_a"] == pytest.approx(0.04) and row["gain_b"] == pytest.approx(0.10)
    assert row["gain"]["change"] == pytest.approx(0.06)           # ... and so did the penalty's advantage
    assert row["same_sign"] is True and row["gain"]["n"] == 3


def test_the_rank_statistic_reports_its_leave_one_out_range_and_survives_a_tiny_input():
    xs, ys = [1, 2, 3, 4, 5], [2, 4, 6, 8, 10]
    r = e166.rank(xs, ys)
    assert r["rho"] == pytest.approx(1.0) and r["loo_min"] == pytest.approx(1.0)
    assert e166.rank([1, 2], [1, 2])["rho"] != e166.rank([1, 2], [1, 2])["rho"]   # nan, not a number


# --- the corpus's own claims, on the artifacts the unit was written for -------------------------------------


def test_the_negative_control_cannot_move_the_level_and_moves_the_gain_anyway():
    from experiments.e103_reproducibility_audit import load_artifacts
    rows = [r for p in e166.pairs(e166.candidates(load_artifacts())) for r in e166.rows_for(p)]
    control = [r for r in rows if r["field"] == e166.CONTROL_FIELD]
    assert len(control) >= 70
    assert not [r for r in control if r["level_resolved"]], "a field `naive` cannot read must not move the level"
    # the only pairs that move it are the two artifacts whose environment was never recorded (e163)
    broken = [r for r in control if not r["naive_bit_identical"]]
    assert broken and all("_omp" in r["a"] + r["b"] for r in broken)
    assert max(abs(r["gain"]["change"]) for r in control) > 0.04, "the control must move the gain for the point"


def test_the_level_moving_manipulations_lean_the_room_accounts_way_and_none_resolve_against_it():
    from experiments.e103_reproducibility_audit import load_artifacts
    rows = [r for p in e166.pairs(e166.candidates(load_artifacts())) for r in e166.rows_for(p)]
    moving = [r for r in rows if r["level_resolved"]]
    # 13 rows over three fields when this unit was written; `e167`'s pair added `noise` as a fourth, which is the
    # field this census said the corpus had never varied and which the unit then went out and varied.
    assert len(moving) >= 13
    assert {"classes", "frozen_bias", "readout_size"} <= {r["field"] for r in moving}
    agree = [r for r in moving if r["same_sign"] and r["gain_resolved"]]
    against = [r for r in moving if not r["same_sign"] and r["gain_resolved"]]
    assert len(agree) >= 5 and not against
    # the largest level move is the classes pair, and every one of its four arms gains
    classes = [r for r in moving if r["field"] == "classes"]
    assert len(classes) == 4 and all(r["gain"]["change"] > 0 for r in classes)
    assert max(r["level"]["sigma"] for r in classes) > 8.0
    # and the near-misses against the account exist, which is why they are printed rather than dropped
    near = [r for r in moving if not r["same_sign"] and not r["gain_resolved"]]
    assert near and max(r["gain"]["sigma"] for r in near) > 1.5


def test_the_rank_statistic_is_uninterpretable_here_which_is_why_rule_43_is_printed_with_it():
    """20 of 102 cells at n >= 5 resolve on either axis, so rho is a statistic over mostly-unresolved inputs."""
    from experiments.e103_reproducibility_audit import load_artifacts
    rows = [r for p in e166.pairs(e166.candidates(load_artifacts())) for r in e166.rows_for(p)]
    # the counts grow with the corpus (127 rows, 13 level-resolved, 8 gain-resolved, 5 both when written), so
    # what is pinned is the shape: the level is the scarce axis and almost nothing resolves on both
    assert len(rows) >= 127
    level = sum(1 for r in rows if r["level_resolved"])
    gain = sum(1 for r in rows if r["gain_resolved"])
    both = len([r for r in rows if r["level_resolved"] and r["gain_resolved"]])
    assert level >= 13 and gain >= 8 and both >= 5
    assert level < len(rows) / 4 and both <= gain
    assert np.isnan(e166.rank([1.0], [1.0])["rho"])
