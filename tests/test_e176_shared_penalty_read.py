"""`e176` is a rule over a *share* of a known effect, which is why its four outputs are pinned separately.

The falsifier is not a threshold on a σ: it is "the step collapsed toward zero", because the question with the
penalty held fixed is whether the earlier effect **survives** rather than whether it resolves. A test that let a
collapsed step count as "survives", or a surviving but unresolved one count as a falsification, would destroy the
distinction `e175` was registered to make.
"""

from __future__ import annotations

import pytest

from experiments import e176_shared_penalty_read as e176


def test_a_step_of_the_same_size_survives_and_a_collapsed_one_fires_the_falsifier():
    own = e176.OWN_FISHER_GAIN_STEP                     # -0.0370
    full = e176.verdict(own, gain_sigma=3.6)
    assert full["survives"] and not full["collapsed"]
    assert full["share_of_own_fisher_step"] == pytest.approx(1.0)
    # most of the effect still there, resolved: survives
    most = e176.verdict(own * 0.8, gain_sigma=2.5)
    assert most["survives"] and not most["collapsed"]
    # collapsed toward zero AND resolved: the falsifier
    gone = e176.verdict(own * 0.2, gain_sigma=3.0)
    assert gone["collapsed"] and not gone["survives"]


def test_a_collapsed_step_that_does_not_resolve_is_neither():
    """Two runs that differ by nothing measurable say nothing, which is not the same as the falsifier."""
    v = e176.verdict(e176.OWN_FISHER_GAIN_STEP * 0.1, gain_sigma=0.6)
    assert not v["survives"] and not v["collapsed"]


def test_the_read_is_mechanical_with_the_artifacts_absent():
    """The reference and the shared run are both missing, so no verdict may be printed -- and the exit is clean."""
    assert e176.main([]) == 0


def test_the_twins_the_controls_rest_on_exist_and_are_the_ones_the_registration_names():
    from pathlib import Path
    from experiments.e151_pertask_contrast_audit import load_arm

    for path, arm in ((e176.TWIN_EWC, "ewc"), (e176.TWIN_NAIVE, "naive"), (e176.LOW_NOISE_NAIVE, "naive")):
        assert Path(path).is_file(), path
        assert load_arm(Path(path), arm)["n"] == 40


def test_the_verdict_is_robust_to_the_threshold_below_the_measured_share():
    """`COLLAPSE_SHARE` is a choice, so the reading it produces has to be checked against other choices.

    The competing predictions are "the effect survives at the same size" (a share of 1) and "it collapses toward
    zero" (a share of 0), so the registered 0.5 sits between them — and what makes the verdict a *measurement*
    rather than a threshold artefact is that every threshold below the measured share gives the same answer.
    """
    import json
    from pathlib import Path

    artifact = Path("runs/e176_shared_penalty_read.json")
    if not artifact.is_file():
        pytest.skip("runs/e176_shared_penalty_read.json not present (runs/ is gitignored)")

    d = json.loads(artifact.read_text(encoding="utf-8"))
    step, own = d["p2"]["gain_step"]["change"], d["p2"]["own_fisher_gain_step"]
    share = step / own
    registered = e176.COLLAPSE_SHARE
    try:
        for threshold in (0.0, 0.2, 0.4, 0.5, 0.6, 0.7):
            e176.COLLAPSE_SHARE = max(threshold, 1e-9)
            v = e176.verdict(step, d["p2"]["gain_step"]["sigma"], own=own)
            assert v["survives"] and not v["collapsed"], threshold
        for threshold in (0.72, 0.75, 0.8, 1.0):
            e176.COLLAPSE_SHARE = threshold
            v = e176.verdict(step, d["p2"]["gain_step"]["sigma"], own=own)
            assert v["collapsed"], threshold
    finally:
        e176.COLLAPSE_SHARE = registered
    # and the statement that makes it a measurement: the only flip point is the measured share itself
    assert 0.70 < share < 0.73
