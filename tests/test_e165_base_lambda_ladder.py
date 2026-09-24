"""`e165`'s claims are sign claims on two axes, and every one of them is easy to get backwards.

The ladder's top is a **stationary** region, and the way to misread it is as "λ = 1.0 shows the penalty does not
matter" when the measured statement is that *nothing moves between 3e-2 and 1.0* while the level is already the
wrong way. The bottom is the mirror: λ = 3e-4 is where the penalty **wins**, at 4.27σ, which is the falsifier's
shape and the reason a matched λ was needed rather than a level. And the matched-λ interaction's sign says the
wiring family *gains* where the base family *loses* — a sign flip in a cell whose whole content is a sign.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from experiments import e165_base_lambda_ladder as e165
from experiments.e151_pertask_contrast_audit import load_arm, paired


def test_the_registered_verdict_separates_p1s_sign_from_its_resolution():
    # the 1.0 rung as measured: the wrong way, unresolved, with a large cost
    v = e165.registered_verdict(change=0.0091, sigma=0.91, cost=-0.0719)
    assert v["p1_holds"] and not v["falsifier_fires"] and not v["gain_resolved"]
    # the 3e-4 rung: the falsifier's shape, and the reason P1's form is not a verdict on every rung
    v = e165.registered_verdict(change=-0.0354, sigma=4.27, cost=-0.0297)
    assert not v["p1_holds"] and v["falsifier_fires"] and v["gain_resolved"]
    # a cost below the registered threshold fails P1 even with the right sign
    assert not e165.registered_verdict(change=0.0091, sigma=0.91, cost=-0.0313)["p1_holds"]


def test_the_control_is_bit_identical_on_the_headline_arms_across_two_schema_epochs():
    """`e133` and `e140`'s plastic arm differ in one config key and are identical to the last digit."""
    a = load_arm(Path(e165.NAIVE_HOME), "naive")
    b = load_arm(Path(e165.CONTROL_TWIN), "naive")
    c = load_arm(Path(e165.CONTROL_TWIN), "ewc")
    assert np.array_equal(a["forgetting"], b["forgetting"])
    assert np.array_equal(a["newest"], b["newest"])
    assert a["n"] == 40
    # and the 3e-3 rung of the ladder is the same arm in both artifacts
    assert np.array_equal(load_arm(Path("runs/e133_r32_naive_ewc_40reps.json"), "ewc")["forgetting"],
                          c["forgetting"])


def test_the_ladder_turns_over_between_3e_3_and_3e_2_and_the_top_is_stationary():
    naive = load_arm(Path(e165.NAIVE_HOME), "naive")
    gains = {}
    for label, _, path in e165.LADDER:
        arm = load_arm(Path(path), "ewc")
        gains[label] = paired(arm["forgetting"], naive["forgetting"])
    # the wrong-sign, unresolved top: three rungs, all under 1 sigma
    for label in ("3e-2", "3e-1", "1.0"):
        assert gains[label]["change"] > 0 and abs(gains[label]["sigma"]) < 1.0
    # the winning bottom rung
    assert gains["3e-4"]["change"] < 0 and gains["3e-4"]["sigma"] > 4.0


def test_the_two_upper_steps_move_by_nothing_while_the_bottom_step_moves_on_both_axes():
    arm = {label: load_arm(Path(path), "ewc") for label, _, path in e165.LADDER}
    top = paired(arm["1.0"]["forgetting"], arm["3e-2"]["forgetting"])
    top_newest = paired(arm["1.0"]["newest"], arm["3e-2"]["newest"])
    assert abs(top["sigma"]) < 1.0 and abs(top_newest["sigma"]) < 1.0
    bottom = paired(arm["3e-3"]["forgetting"], arm["3e-4"]["forgetting"])
    bottom_newest = paired(arm["3e-3"]["newest"], arm["3e-4"]["newest"])
    assert bottom["sigma"] > 2.5 and bottom_newest["sigma"] > 2.5


def test_the_matched_lambda_interaction_has_the_wiring_family_gaining_and_the_base_family_losing():
    wn, we = load_arm(Path(e165.WIRING), "naive"), load_arm(Path(e165.WIRING), "ewc")
    naive = load_arm(Path(e165.NAIVE_HOME), "naive")
    base = load_arm(Path("runs/e161_r32_base_ewc_lam1.json"), "ewc")
    assert wn["forgetting"].mean() - we["forgetting"].mean() > 0        # the wiring family gains
    assert naive["forgetting"].mean() - base["forgetting"].mean() < 0   # the base family loses
    gain = paired(wn["forgetting"] - we["forgetting"], naive["forgetting"] - base["forgetting"])
    cost = paired(we["newest"] - wn["newest"], base["newest"] - naive["newest"])
    assert gain["change"] > 0 and gain["sigma"] > 3.0
    assert cost["change"] > 0 and cost["sigma"] > 4.0
