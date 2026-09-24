"""`e149`'s decomposition has three things that can be wrong silently, and one that is a convention.

The algebra is checkable: build four arms with a *known* interaction and the identity has to return it. The
bookkeeping is the thing this project keeps getting wrong: a missing quarter of the 2x2 must read as missing
rather than as a zero (every run here costs hours), and the pairing check is what licenses calling the four
arms paired at all. The convention is `e56`'s: **ties are dropped and counted**, never folded into a side.

And the verdict has to depend on the **resolution rather than the size** -- a big interaction at 0.5 sigma is a
bound and not a finding, which is the whole content of this reader.
"""

from __future__ import annotations

import json

import numpy as np

from experiments import e149_intervention_interaction as e149

ARM_KEYS = ("naive", "freeze", "pen", "both")


def _arm(values: dict, config: dict | None = None) -> dict:
    n = len(next(iter(values.values())))
    out = {k: np.asarray(v, dtype=float) for k, v in values.items()}
    out["config"] = config or {}
    out["n"] = n
    return out


def _four(interaction: np.ndarray, base: float = 0.08, n: int | None = None) -> dict:
    """Four arms whose interaction is exactly ``interaction``, with a seed-level wobble in every arm."""
    n = len(interaction) if n is None else n
    wobble = np.linspace(-0.01, 0.01, n)
    naive = base + wobble
    freeze = naive - 0.05 + 0.3 * wobble
    pen = naive - 0.03 - 0.4 * wobble
    both = freeze + pen - naive + interaction
    vals = {"naive": naive, "freeze": freeze, "pen": pen, "both": both}
    return {k: _arm({m: v for m, v in [(m, vals[k]) for m in e149.METRICS]}) for k in ARM_KEYS}


def test_the_identity_returns_the_interaction_that_was_built_in():
    rng = np.random.default_rng(0)
    built = rng.normal(0.01, 0.02, size=40)
    arms = _four(built)
    d = e149.decompose(arms)["forgetting"]
    assert abs(d["interaction"]["change"] - built.mean()) < 1e-12
    # the closed form the docstring states, to the last digit
    closed = d["d_both"]["change"] - d["d_freeze"]["change"] - d["d_pen"]["change"]
    assert abs(d["interaction"]["change"] - closed) < 1e-12


def test_the_ceiling_is_the_SMALLER_main_effect_and_the_share_uses_it():
    built = np.full(40, 0.01)
    arms = _four(built)
    d = e149.decompose(arms)["forgetting"]
    assert abs(d["ceiling"] - 0.03) < 1e-12          # |d_pen| = 0.03 < |d_freeze| = 0.05
    assert abs(d["ceiling_share"] - 0.01 / 0.03) < 1e-12


def test_retention_fractions_are_the_interaction_read_from_the_other_end():
    arms = _four(np.full(40, 0.006))
    d = e149.decompose(arms)["forgetting"]
    # pen_given_freeze = d_pen + I, so retention = 1 + I/d_pen and 1 - retention = -I/d_pen
    assert abs(d["pen_given_freeze"]["change"] - (d["d_pen"]["change"] + d["interaction"]["change"])) < 1e-12
    assert abs((1 - d["retention_of_pen"]) + d["interaction"]["change"] / d["d_pen"]["change"]) < 1e-12
    assert abs((1 - d["retention_of_freeze"]) + d["interaction"]["change"] / d["d_freeze"]["change"]) < 1e-12
    # and in magnitudes, which is how the finding quotes them: the lost share is I / |d|
    assert abs((1 - d["retention_of_pen"]) - d["interaction"]["change"] / abs(d["d_pen"]["change"])) < 1e-12


def test_a_share_is_refused_when_a_main_effect_is_itself_unresolved():
    # the penalty's effect is ~0.001 against a seed spread of 0.05: not an effect, so no ceiling to share
    arms = _four(np.full(40, 0.01))
    for k in ARM_KEYS:
        base = arms[k]["forgetting"]
        arms[k]["accuracy"] = base.copy()
    arms["pen"]["accuracy"] = arms["naive"]["accuracy"] + 0.001 + 0.05 * np.linspace(-1, 1, 40)
    d = e149.decompose(arms, ("accuracy",))["accuracy"]
    assert d["main_effects_sigma"]["pen"] < 2
    assert d["ceiling_interpretable"] is False
    quiet = e149.decompose(_four(np.full(40, 0.01)), ("accuracy",))["accuracy"]
    assert quiet["ceiling_interpretable"] is True


def test_the_whole_body_loader_takes_ratios_of_means_and_the_frozen_bias_is_exactly_zero(tmp_path):
    def rep(wb0, bias0, wb1):
        return {"interference": [
            {"task": 0, "whole_body": {"cumulative": wb0, "bias_only_cumulative": bias0}},
            {"task": 1, "whole_body": {"cumulative": wb1, "bias_only_cumulative": 0.0}}]}
    payload = {"methods": {"naive": {"replicates": [rep(0.4, 0.2, 0.1), rep(0.6, 0.0, 0.3)]}},
               "config": {}}
    path = tmp_path / "wb.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    arm = e149.load_wb(path, "naive")
    assert np.allclose(arm["whole_body_task0"], [0.4, 0.6])
    assert np.allclose(arm["whole_body_task1"], [0.1, 0.3])
    assert np.allclose(arm["whole_body_mean"], [0.25, 0.45])
    # the share is a ratio of MEANS: 0.1 / 0.5 = 0.2, not the mean of 0.5 and 0.0
    assert abs(float(arm["bias_only_task0"].mean()) / float(arm["whole_body_task0"].mean()) - 0.2) < 1e-12
    assert e149.load_wb(path, "ewc") is None
    assert e149.load_wb(tmp_path / "nope.json", "naive") is None


def test_a_missing_quarter_reads_as_missing_not_as_a_zero(tmp_path):
    payload = {"methods": {"naive": {"replicates": [
        {"mean_forgetting": 0.1, "final_accuracy": 0.9, "theta_drift": [0.01, 0.01, 0.01],
         "retention_loss": [[0.01, None, None], [0.02, 0.01, None], [0.03, 0.02, 0.01]]}]}},
        "config": {}}
    part = tmp_path / "part.json"
    part.write_text(json.dumps(payload), encoding="utf-8")
    assert e149.load_arm(part, "naive") is not None
    assert e149.load_arm(part, "ewc") is None            # method absent
    assert e149.load_arm(tmp_path / "nope.json", "naive") is None
    assert e149.load_arm(part, "ewc") is None
    # an artifact that predates `forgetting_per_task` loads, with the per-task series undefined rather than 0.0
    arm = e149.load_arm(part, "naive")
    assert np.isnan(arm["forgetting_task0"]).all() and np.isnan(arm["forgetting_task1"]).all()


def test_ties_are_dropped_and_counted_rather_than_folded_into_a_side():
    pos, neg, tied, p = e149.sign_test(np.array([1.0, 1.0, 0.0, 0.0, -1.0]))
    assert (pos, neg, tied) == (2, 1, 2)
    assert abs(p - 1.0) < 1e-12                          # binomtest(2, 3) two-sided
    # all ties is not a sign test at all
    assert np.isnan(e149.sign_test(np.zeros(5))[3])


def test_the_pairing_check_separates_the_seed_stream_from_the_knobs():
    same = {"seed0": 0, "repeats": 40, "batch": 32, "frozen_bias": False, "lam": 3e-3}
    arms = _four(np.zeros(40))
    for k in ARM_KEYS:
        arms[k]["config"] = dict(same)
    arms["both"]["config"] = dict(same, frozen_bias=True, lam=3e-4)
    check = e149.pairing_check(arms)
    # the knobs are not seed fields, so they are reported in their own block and NOT as a pairing failure
    assert "batch" in check["fields_agreeing"] and "seed0" in check["fields_agreeing"]
    assert check["fields_differing"] == []
    assert check["knobs"]["both"]["frozen_bias"] is True
    assert check["knobs"]["naive"]["frozen_bias"] is False
    assert check["replicates_agree"] is True
    # a seed field that differs IS a pairing failure, and must not also be listed as agreeing
    arms["pen"]["config"] = dict(same, batch=64)
    check2 = e149.pairing_check(arms)
    assert [f for f, _ in check2["fields_differing"]] == ["batch"]
    assert "batch" not in check2["fields_agreeing"]
    # and a differing replicate count is a pairing failure too
    short = _four(np.zeros(40))
    for k in ARM_KEYS:
        short[k]["config"] = dict(same)
    short["both"] = _arm({m: np.zeros(38) for m in e149.METRICS})
    short["both"]["config"] = dict(same)
    assert e149.pairing_check(short)["replicates_agree"] is False


def test_the_verdict_follows_the_resolution_and_not_the_size():
    # a LARGE interaction carried by a spread that swamps it is still a bound
    noisy = e149.decompose(_four(np.full(40, 0.01) + np.tile([0.2, -0.2], 20)))["forgetting"]
    assert e149.verdicts({"forgetting": noisy})["forgetting"].startswith("additive")
    # the same mean with a quiet spread resolves, in the direction the metric's sign says
    quiet = e149.decompose(_four(np.full(40, 0.01)))["forgetting"]
    assert e149.verdicts({"forgetting": quiet})["forgetting"].startswith("sub-additive")


def _cell(step_mean: float, n: int = 40, sd: float = 0.03) -> "np.ndarray":
    """A paired difference with this mean and sd, so a step's sigma is arithmetic."""
    d = np.zeros(n)
    d[0] = 1.0
    d = d - d.mean()
    d = d / d.std(ddof=1)
    return step_mean + sd * d


def _channel_lambda(free_step: float, frozen_step: float, n: int = 40) -> dict:
    base = np.zeros(n)
    return {
        ("free", "3e-4"): {"forgetting": base.copy(), "loss_forgetting": base.copy(),
                           "accuracy": base.copy(), "newest": base.copy(), "config": {}, "n": n},
        ("free", "3e-3"): {"forgetting": base + _cell(free_step, n), "loss_forgetting": base + _cell(free_step, n),
                           "accuracy": base + _cell(free_step, n), "newest": base + _cell(free_step, n),
                           "config": {}, "n": n},
        ("frozen", "3e-4"): {"forgetting": base.copy(), "loss_forgetting": base.copy(),
                             "accuracy": base.copy(), "newest": base.copy(), "config": {}, "n": n},
        ("frozen", "3e-3"): {"forgetting": base + _cell(frozen_step, n),
                             "loss_forgetting": base + _cell(frozen_step, n),
                             "accuracy": base + _cell(frozen_step, n), "newest": base + _cell(frozen_step, n),
                             "config": {}, "n": n},
    }


def test_the_step_interaction_is_the_difference_of_the_two_steps_and_flips_when_they_do():
    arms = _channel_lambda(free_step=+0.025, frozen_step=-0.005)
    st = e149.step_interaction(arms, "forgetting")
    assert abs(st["step_free"]["change"] - 0.025) < 1e-12
    assert abs(st["step_frozen"]["change"] + 0.005) < 1e-12
    assert abs(st["interaction"]["change"] + 0.030) < 1e-12
    # the interaction's sem is its OWN per-seed difference's sem, and the quadrature sum is carried beside it
    # as the bound it would be if the two steps were independent -- which they are not, sharing the seeds.
    per_seed = (arms[("frozen", "3e-3")]["forgetting"] - arms[("frozen", "3e-4")]["forgetting"]) - \
               (arms[("free", "3e-3")]["forgetting"] - arms[("free", "3e-4")]["forgetting"])
    assert abs(st["interaction"]["sem"] - per_seed.std(ddof=1) / np.sqrt(len(per_seed))) < 1e-12
    assert st["interaction"]["sem"] <= st["interaction"]["sem_quadrature"] + 1e-12
    assert st["interaction"]["sigma"] > 2
    # one cell missing is not a zero: the second 2x2 prints nothing rather than a number
    partial = dict(arms)
    del partial[("frozen", "3e-3")]
    assert e149.step_interaction(partial, "forgetting") is None


def test_the_second_2x2_reports_the_same_interaction_for_every_metric_it_is_given():
    arms = _channel_lambda(free_step=+0.02, frozen_step=-0.01)
    for metric in ("forgetting", "loss_forgetting", "accuracy", "newest"):
        st = e149.step_interaction(arms, metric)
        assert abs(st["interaction"]["change"] + 0.030) < 1e-12
