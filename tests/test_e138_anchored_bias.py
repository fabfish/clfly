"""`e138`'s analysis script has to read the arms it names and print no verdict it cannot support.

The two failure modes worth a test are not arithmetic but bookkeeping. First, **a missing artifact must read as
missing**: the runs take an hour each and the natural way to write this script is to load whatever is at the path
and average it, which silently reports an unfinished arm as a zero. Second, **monotonicity is the registered
claim and it is asymmetric** -- the prediction is a strict fall in the scale, so an arm that ties must not be
reported as holding. Both are checked here on synthetic arms, with no torch and no run.
"""

from __future__ import annotations

import json

import numpy as np

from experiments import e138_anchored_bias as e138

# task 0's step is 1.0 in every arm -- C0a's control -- while the path lengths differ, which is C0b's claim
STEPS_UNANCHORED = [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]      # path 6.0
STEPS_SCALE1 = [[1.0, 2.0], [1.0, 2.0]]                    # path 3.0
STEPS_SCALE33 = [[1.0, 1.0], [1.0, 1.0]]                   # path 2.0


def _fake_artifact(path, forgetting, bias_steps, accuracy=0.9):
    reps = []
    for f, steps in zip(forgetting, bias_steps):
        reps.append({
            "mean_forgetting": f,
            "forgetting_per_task": [f / 2, f / 2, 0.0],
            "bias_norms": [{"step": s, "from_zero": s} for s in steps],
            "theta_drift": [0.05, 0.06, 0.07],
        })
    path.write_text(json.dumps({"methods": {"ewc": {"replicates": reps, "final_accuracy": accuracy}}}),
                    encoding="utf-8")
    return path


def test_a_missing_artifact_reads_as_missing_and_not_as_zero(tmp_path):
    absent = tmp_path / "not_run_yet.json"
    assert e138.load_arm(absent, "ewc") is None
    v = e138.verdicts({"unanchored": {"bias_step_task0": np.array([1.0])}, "scale_1.0": None})
    assert "verdict" in v and "P1_holds" not in v


def test_task_zero_is_shared_across_arms_and_that_is_what_c0a_asserts(tmp_path):
    a = e138.load_arm(_fake_artifact(tmp_path / "a.json", [0.06, 0.07], STEPS_UNANCHORED), "ewc")
    b = e138.load_arm(_fake_artifact(tmp_path / "b.json", [0.05, 0.06], STEPS_SCALE1), "ewc")
    assert e138.verdicts({"unanchored": a, "scale_1.0": b})["C0a_holds"]

    # and a flag that disturbed task 0 is caught rather than averaged away
    c = e138.load_arm(_fake_artifact(tmp_path / "c.json", [0.05, 0.06], STEPS_SCALE1), "ewc")
    c["bias_step_task0"] = c["bias_step_task0"] + 1e-6
    assert not e138.verdicts({"unanchored": a, "scale_1.0": c})["C0a_holds"]


def test_both_registered_orders_hold_only_when_every_arm_falls(tmp_path):
    arms = {
        "unanchored": e138.load_arm(_fake_artifact(tmp_path / "u.json", [0.0654, 0.0700], STEPS_UNANCHORED), "ewc"),
        "scale_1.0": e138.load_arm(_fake_artifact(tmp_path / "s1.json", [0.0400, 0.0450], STEPS_SCALE1), "ewc"),
        "scale_33.2": e138.load_arm(_fake_artifact(tmp_path / "s33.json", [0.0300, 0.0350], STEPS_SCALE33), "ewc"),
    }
    v = e138.verdicts(arms)
    assert v["C0b_holds"] and v["P1_holds"]
    assert v["C0b_order"] == ["unanchored", "scale_1.0", "scale_33.2"]
    # the strong arm is far enough from unanchored that the falsifier does not fire
    assert not v["falsifier_fired"]

    # a tie is not a fall -- a strict inequality is what was registered
    arms["scale_33.2"]["forgetting"] = np.array([0.0400, 0.0450])
    assert not e138.verdicts(arms)["P1_holds"]

    # and neither is a reversal, which is the arm failing on its own terms
    arms["scale_33.2"]["forgetting"] = np.array([0.0900, 0.0900])
    assert not e138.verdicts(arms)["P1_holds"]


def test_the_falsifier_reads_sigma_and_not_the_mean(tmp_path):
    # a 0.002 mean shift carrying a 0.002 sem is one sigma: inside the registered two
    close = {
        "unanchored": e138.load_arm(_fake_artifact(tmp_path / "u.json", [0.0654, 0.0654],
                                                   STEPS_UNANCHORED), "ewc"),
        "scale_33.2": e138.load_arm(_fake_artifact(tmp_path / "s33.json", [0.0654, 0.0614],
                                                   STEPS_SCALE33), "ewc"),
    }
    v = e138.verdicts(close)
    assert v["P1_scale33_vs_unanchored"]["sigma"] < 2.0
    assert v["falsifier_fired"]

    # the same direction with a real gap is not a falsifier, whatever the sign of the mean
    far = dict(close)
    far["scale_33.2"] = e138.load_arm(_fake_artifact(tmp_path / "f.json", [0.0200, 0.0250],
                                                     STEPS_SCALE33), "ewc")
    assert not e138.verdicts(far)["falsifier_fired"]
