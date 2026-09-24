"""`e152`'s two rules have to be checkable, because both are the kind that can be read as a preference.

`dominates` is a **point-estimate** rule over two axes, and `evidence` is what keeps that honest: a frontier that
does not say how resolved each dominance is would be the fourth time this project printed a comparison at a
resolution it did not have. And `ladder_steps` must compute each step as its **own** paired contrast -- a
difference of two arms' sigmas is not the step's resolution, and that is the arithmetic error the first version of
this script made.
"""

from __future__ import annotations

import numpy as np

from experiments import e152_stability_plasticity_trade as e152


def _pts(**kw) -> dict:
    """A plane from `label=(forgetting_change, newest_change)` pairs."""
    return {k: {"forgetting_change": v[0], "newest_change": v[1]} for k, v in kw.items()}


def test_dominance_needs_BOTH_axes_and_is_strict_on_one():
    # newest-change: HIGHER is better, so -0.01 is better than -0.02
    pts = _pts(a=(-0.05, -0.02), b=(-0.04, -0.02), c=(-0.04, -0.01), d=(-0.06, -0.03))
    # b is worse on forgetting and equal on newest -> dominated
    assert e152.dominates(pts["a"], pts["b"]) and not e152.dominates(pts["b"], pts["a"])
    # c is worse on forgetting and BETTER on newest -> a trade, so neither dominates
    assert not e152.dominates(pts["a"], pts["c"]) and not e152.dominates(pts["c"], pts["a"])
    # d is better on forgetting and worse on newest -> also a trade
    assert not e152.dominates(pts["a"], pts["d"]) and not e152.dominates(pts["d"], pts["a"])
    # equality on both axes is not dominance: the rule needs strictness on one
    twin = {"forgetting_change": -0.05, "newest_change": -0.02}
    assert not e152.dominates(pts["a"], twin)


def test_the_frontier_keeps_only_undominated_arms():
    pts = _pts(best=(-0.05, -0.02), mid=(-0.04, -0.02), trade=(-0.04, -0.01), worst=(-0.01, -0.05))
    fr = e152.frontier(pts)
    assert fr["frontier"] == ["best", "trade"]
    assert "best" in fr["arms"]["mid"]["dominated_by"] and "best" in fr["arms"]["worst"]["dominated_by"]
    assert fr["arms"]["trade"]["dominated_by"] == []


def _arm(forgetting, newest, n=40):
    return {"forgetting": np.asarray(forgetting, float), "newest": np.asarray(newest, float), "n": n}


def test_evidence_grades_a_dominance_and_a_trade_still_resolves_on_one_axis():
    n = 40
    step = np.zeros(n)
    step[0] = 1.0
    step = step - step.mean()
    step = step / step.std(ddof=1)
    better = _arm(np.zeros(n), np.zeros(n))
    worse = _arm(0.02 + 0.05 * step, -0.001 + 0.05 * step)   # worse on forgetting, better on newest
    arms = {"better": better, "worse": worse}
    pts = {"better": {"forgetting_change": 0.0, "newest_change": 0.0},
           "worse": {"forgetting_change": 0.02, "newest_change": -0.001}}
    ev = e152.evidence(arms, "better", "worse")
    assert ev["resolved_axes"] == 1 and ev["grade"] == "resolved on one"
    assert ev["forgetting_sigma"] > 2 and ev["newest_sigma"] < 2
    fr = e152.frontier(pts, arms)
    assert fr["arms"]["worse"]["dominated_by"] == ["better"]
    assert "evidence" in fr["arms"]["worse"]


def test_a_step_is_its_own_paired_contrast_and_not_a_difference_of_sigmas():
    """Both arms carry a large per-seed sd; the STEP between them is exact, and that is the point."""
    n = 40
    wobble = np.linspace(-0.05, 0.05, n)
    lo = _arm(0.05 + wobble, 0.95 - wobble)
    hi = _arm(0.07 + wobble, 0.93 - wobble)
    steps = e152.ladder_steps({"lo": lo, "hi": hi}, ladder=("lo", "hi"))
    assert len(steps) == 1
    s = steps[0]
    assert abs(s["forgetting_change"] - 0.02) < 1e-12 and abs(s["newest_change"] + 0.02) < 1e-12
    assert s["both_worse"] is True
    # the two axes are EXACT here, so both resolve -- the sigmas come from the step, not from the arms' spread
    assert s["both_resolved"] is True


def test_the_registry_resolves_and_the_reference_is_on_disk():
    from pathlib import Path
    missing = [c[0] for c in e152.ARMS if not Path(c[1]).is_file()] + \
              [c[0] for c in e152.WIRING_ARMS if not Path(c[1]).is_file()] + \
              [c[0] for c in e152.FROZEN_ARMS if not Path(c[1]).is_file()] + \
              [n for n in (e152.REFERENCE[0], e152.WIRING_REFERENCE[0], e152.FROZEN_REFERENCE[0])
               if not Path({"naive": e152.REFERENCE[1], "naive (wiring)": e152.WIRING_REFERENCE[1],
                            "naive (frozen arm)": e152.FROZEN_REFERENCE[1]}[n]).is_file()]
    assert missing == [], f"the registry names artifacts that are not on disk: {missing}"


def test_the_three_planes_are_separate_registries_against_separate_baselines():
    """Each plane must carry its own reference: contrasting one family's arms against another's baseline is wrong."""
    assert len({e152.REFERENCE[1], e152.WIRING_REFERENCE[1], e152.FROZEN_REFERENCE[1]}) == 3
    labels = [{a[0] for a in reg} for reg in (e152.ARMS, e152.WIRING_ARMS, e152.FROZEN_ARMS)]
    assert labels[0].isdisjoint(labels[1]) and labels[1].isdisjoint(labels[2]) and labels[0].isdisjoint(labels[2])
    assert e152.WIRING_REFERENCE[1] == "runs/e144_r32_overlap1_methods_40reps.json"
    assert e152.FROZEN_REFERENCE[1] == "runs/e140_r32_methods_frozenbias_40reps.json"
