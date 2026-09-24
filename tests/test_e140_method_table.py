"""`e140`'s analysis has to read both arms, check per-replicate identities, and print no verdict it cannot support.

The failure modes worth a test are bookkeeping ones, and each has cost this project a fire already:

  * a **missing artifact must read as missing** -- the two runs take hours and the natural way to write this
    script is to average whatever is at the path, which reports an unfinished arm as a zero;
  * the **controls are identities**, so an arm that differs in the last digit must not be reported as matching;
  * and the **difference of differences is paired**, so a test has to be able to see P2 computed on two arms
    whose replay margins move in opposite directions.
"""

from __future__ import annotations

import json

import numpy as np

from experiments import e140_method_table as e140

NAMES = ("naive", "ewc", "ewc-block", "ewc-block-rand", "replay")


def _fake(path, forgetting, accuracy=0.9):
    """A one-method artifact: `forgetting` maps a method name to its forty per-replicate values."""
    methods = {}
    for name, values in forgetting.items():
        reps = [{"mean_forgetting": v, "final_accuracy": accuracy, "forgetting_per_task": [v / 2, v / 2, 0.0]}
                for v in values]
        methods[name] = {"replicates": reps, "forgetting_sem": 0.01 * (len(values) ** -0.5),
                         "final_accuracy": accuracy}
    path.write_text(json.dumps({"methods": methods}), encoding="utf-8")
    return path


def _arm(values):
    v = np.array(values, dtype=float)
    return {"forgetting": v, "accuracy": np.full(len(v), 0.9), "per_task": np.zeros((len(v), 2)),
            "sem": 0.01, "final_accuracy": 0.9, "n": len(v)}


def test_a_missing_arm_reads_as_missing_and_no_verdict_is_printed(tmp_path):
    absent = tmp_path / "not_run_yet.json"
    assert e140.load_arm(absent, "naive") is None
    out = e140.verdicts({"plastic": None, "frozen": None})
    assert "verdict" in out and "P1_holds" not in out

    # one arm alone is also not enough, and the message says which is present
    out = e140.verdicts({"plastic": {"naive": _arm([0.07] * 3)}, "frozen": None})
    assert "both arms are needed" in out["verdict"] and "plastic" in out["verdict"]


def test_the_identity_control_catches_a_difference_in_the_last_digit():
    have = {"forgetting": np.array([0.0417, 0.0521])}
    want = {"forgetting": np.array([0.0417, 0.0521])}
    assert e140.identity(have, want, "forgetting", 2)["identical"]
    want["forgetting"] = np.array([0.0417, 0.0522])
    got = e140.identity(have, want, "forgetting", 2)
    assert not got["identical"]
    assert abs(got["worst_abs_difference"] - 1e-4) < 1e-9


def test_p1_is_the_frozen_arm_s_ewc_contrast_and_needs_both_arms():
    plastic = {"naive": _arm([0.075] * 4), "ewc": _arm([0.0654] * 4)}
    frozen = {"naive": _arm([0.025] * 4), "ewc": _arm([-0.0104] * 4)}
    # zero within-arm variance makes every sem zero, so use a spread the way a real artifact has one
    plastic["ewc"] = _arm([0.0654, 0.0754, 0.0554, 0.0654])
    frozen["ewc"] = _arm([-0.0104, 0.0000, -0.0208, -0.0104])
    out = e140.verdicts({"plastic": plastic, "frozen": frozen})
    assert out["P1_ewc_frozen"]["change"] < 0
    assert out["P1_ewc_frozen"]["sigma"] > 1.0
    assert set(out["P3_ordering"]) == {"plastic", "frozen"}


def test_the_difference_of_differences_is_paired_and_reads_the_cut():
    plastic = {"naive": _arm([0.0729, 0.0729, 0.0729, 0.0729]),
               "replay": _arm([-0.0125, -0.0125, -0.0125, -0.0125])}
    frozen = {"naive": _arm([0.0250, 0.0250, 0.0250, 0.0250]),
              "replay": _arm([-0.0042, -0.0042, -0.0042, -0.0042])}
    out = e140.verdicts({"plastic": plastic, "frozen": frozen})
    m = out["P2_replay_margin"]
    assert abs(m["plastic"] - (-0.0854)) < 1e-9 and abs(m["frozen"] - (-0.0292)) < 1e-9
    assert abs(m["cut"] - 0.658) < 0.01                  # the 66% of `e135`'s five-replicate table


def test_p3_compares_the_two_orderings_rather_than_a_contrast():
    plastic = {"naive": _arm([0.0729]), "ewc": _arm([0.0208])}
    frozen = {"naive": _arm([0.0250]), "ewc": _arm([-0.0104])}
    assert e140.verdicts({"plastic": plastic, "frozen": frozen})["P3_holds"]
    flipped = {"naive": _arm([0.0250]), "ewc": _arm([0.0300])}
    assert not e140.verdicts({"plastic": plastic, "frozen": flipped})["P3_holds"]


def test_a_table_whose_artifact_exists_is_read_through_load_arm(tmp_path):
    path = _fake(tmp_path / "arm.json", {"naive": [0.05, 0.07, 0.09]})
    got = e140.load_arm(path, "naive")
    assert got is not None and got["n"] == 3 and abs(got["forgetting"].mean() - 0.07) < 1e-12
    assert e140.load_arm(path, "replay") is None          # a method the arm does not carry
