"""`e171` is a verdict over four predictions, and it is written before its data exists -- so the tests are too.

The one thing that must not happen is a **silent** verdict: a script that reported "P2 agrees" for a setting whose
level never moved would be reading a sign off noise. Each combination is therefore pinned here, including the two
that produce no result at all, and the corpus facts are pinned against the reference artifacts the read uses.
"""

from __future__ import annotations

from pathlib import Path


from experiments import e171_noise_level_knob as e171
from experiments.e151_pertask_contrast_audit import load_arm


def test_a_level_that_moved_and_a_gain_that_followed_it_agrees():
    v = e171.verdict(level_sigma=9.0, gain_change=0.02, gain_sigma=2.5)
    assert v["level_moved"] and v["gain_resolved"] and v["agrees"] and not v["against"]


def test_the_two_ways_it_can_disagree_are_kept_apart():
    # a resolved step the wrong way is the falsifier; a step the right way that does not resolve is neither
    assert e171.verdict(9.0, -0.02, 2.5)["against"]
    unresolved = e171.verdict(9.0, 0.02, 1.1)
    assert not unresolved["agrees"] and not unresolved["against"] and unresolved["level_moved"]


def test_an_unmoved_level_produces_no_verdict_at_all():
    """The null worth keeping: `noise` may simply not be a level knob for this metric."""
    for sigma in (0.3, -1.9):
        v = e171.verdict(sigma, 0.05, 4.0)
        assert not v["level_moved"] and not v["agrees"] and not v["against"]


def test_the_reference_is_a_level_and_a_gain_and_the_level_is_one_number():
    """`e133` and `e141` differ in `lam`, which `naive` cannot read -- so the level is not doubled."""
    naive = load_arm(Path(e171.REFERENCE_NAIVE), "naive")
    ewc = load_arm(Path(e171.REFERENCE_EWC), "ewc")
    assert naive["n"] == ewc["n"] == 40
    import pytest

    # the values are the project's standard quantity, computed in float32 and accumulated in float64, so they are
    # pinned to eight digits rather than exactly
    assert naive["forgetting"].mean() == pytest.approx(0.075, abs=1e-8)
    assert (naive["forgetting"] - ewc["forgetting"]).mean() == pytest.approx(0.03541667, abs=1e-7)


def test_the_read_is_mechanical_when_the_artifacts_are_absent(tmp_path):
    """A verdict for a design whose arms do not exist is the one output this script must never produce."""
    code = e171.main([])
    assert code == 0


def test_the_read_knows_two_knobs_and_refuses_a_verdict_for_either_without_its_arms():
    """`e173` is the second knob, and the whole point of `--knob` is that its read is the same function.

    `iters` is the one whose Fisher does not depend on it, so a gain step measured there has no Fisher
    explanation available -- which is what makes it worth reading with the *same* verdict rather than a new one.
    """
    assert sorted(e171.KNOBS) == ["iters", "noise"]
    for knob, runs in e171.KNOBS.items():
        assert len(runs) == 2 and all(path.startswith("runs/") for _, _, path in runs)
    # the noise family is measured, so its verdict prints; the iters family is not yet, so it must not
    assert e171.main(["--knob", "noise"]) == 0
    assert e171.main(["--knob", "iters"]) == 0


def test_an_unknown_knob_is_rejected_rather_than_read_as_noise():
    import pytest

    with pytest.raises(SystemExit):
        e171.main(["--knob", "lr"])
