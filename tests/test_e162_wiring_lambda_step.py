"""`e162`'s two claims are arithmetic on two artifacts, and both have a sign that is easy to get backwards.

The **control** is the first thing pinned: `naive` cannot read `lam`, so its step between the two λ must be exactly
zero -- if it is not, the pair is not a λ difference and nothing else in the script means anything. The second is
the **direction** of the block arms' newest-task step: it is a *cost appearing* (−0.0266, i.e. the accuracy falls
at the larger λ), which the first version of the script's prose called an improvement. A sign error in a reader
whose whole content is a sign is the defect the test exists for.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from experiments import e162_wiring_lambda_step as e162


def test_the_control_arm_is_untouched_because_it_cannot_read_lam():
    from experiments.e151_pertask_contrast_audit import load_arm, paired
    n3 = load_arm(Path(e162.AT_3E3), "naive")
    n1 = load_arm(Path(e162.AT_1_0), "naive")
    step = paired(n1["forgetting"], n3["forgetting"])
    assert step["change"] == 0.0 and step["sem"] == 0.0
    assert np.array_equal(n1["forgetting"], n3["forgetting"])


def test_the_diagonal_is_flat_while_the_block_arms_move_and_the_sign_is_a_cost():
    from experiments.e151_pertask_contrast_audit import load_arm, paired
    out = {}
    for arm in ("ewc", "ewc-block", "ewc-block-rand"):
        a = load_arm(Path(e162.AT_3E3), arm)
        b = load_arm(Path(e162.AT_1_0), arm)
        out[arm] = (paired(b["forgetting"], a["forgetting"]), paired(b["newest"], a["newest"]))
    # the diagonal: neither axis resolves
    assert out["ewc"][0]["sigma"] < 2 and out["ewc"][1]["sigma"] < 2
    # the block arms: the newest-task step is NEGATIVE (a cost acquired) and resolved
    for arm in ("ewc-block", "ewc-block-rand"):
        step_newest = out[arm][1]
        assert step_newest["change"] < 0 and step_newest["sigma"] > 4
        assert out[arm][1]["change"] < -0.02


def test_the_family_contrast_this_is_about_is_the_base_familys_opposite():
    """The base family's one-step λ increase worsens both axes, with both resolved -- the claim e162 contrasts."""
    from experiments.e151_pertask_contrast_audit import load_arm, paired
    l4 = load_arm(Path("runs/e141_r32_ewc_lam3e-4.json"), "ewc")
    l3 = load_arm(Path("runs/e133_r32_naive_ewc_40reps.json"), "ewc")
    fg = paired(l3["forgetting"], l4["forgetting"])
    nw = paired(l3["newest"], l4["newest"])
    assert fg["change"] > 0 and fg["sigma"] > 2      # forgetting worse
    assert nw["change"] < 0 and nw["sigma"] > 2      # newest accuracy worse
