"""`e190` is a reader written before its artifact, so what it can be tested against is the registration's own
arithmetic and the four outcomes it names.

The test that matters most is the last one: against `runs/e10_rung_side.json` -- the only one of the two artifacts
that exists -- the reader must reproduce the registration's numbers exactly (mean −0.0116, sd 0.0462, 0.43σ from
zero at three replicates). A reader that quietly used a different quantity, or paired the replicates wrongly, would
print a plausible number and never be caught by the synthetic cases.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments import e190_side_rung_read as e190


def artifact(path: Path, gaps: list[float], quantity="accuracy", config=None) -> Path:
    """A payload whose two arms differ by `gaps` per replicate, in the shape the runner writes."""
    key = "final_accuracy" if quantity == "accuracy" else "mean_forgetting"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "config": config or {"circuit_size": 300, "basis": "side", "repeats": len(gaps), "readout_size": 32,
                             "input_overlap": None},
        "timing_s": 1234.0,
        "methods": {e190.PAIR[0]: {"replicates": [{key: 0.80} for _ in gaps]},
                    e190.PAIR[1]: {"replicates": [{key: 0.80 - g} for g in gaps]}},
    }), encoding="utf-8")
    return path


def test_the_paired_gap_is_arm_one_minus_arm_two_with_the_registration_s_statistics(tmp_path):
    a = artifact(tmp_path / "x.json", [-0.02, -0.02, -0.02, -0.02])
    g = e190.paired_gap(a)
    assert g["n"] == 4 and abs(g["mean"] + 0.02) < 1e-12
    assert g["n_negative"] == 4 and g["n_positive"] == 0
    assert g["sd"] == pytest.approx(0.0, abs=1e-12) and g["sigma"] is None      # no scatter: no sigma to claim
    assert g["circuit_size"] == 300 and g["basis"] == "side" and g["timing_s"] == 1234.0


def test_a_missing_artifact_prints_the_registration_and_claims_nothing(tmp_path, capsys):
    assert e190.paired_gap(tmp_path / "nope.json") is None
    assert e190.report(None, None, {"outcome": "not yet written"}) == 0
    out = capsys.readouterr().out
    assert "not written yet" in out and "P1" in out and "falsifier" not in out.split("== the registered")[-1]


def test_the_four_registered_outcomes_are_decided_by_the_numbers(tmp_path):
    neg = e190.paired_gap(artifact(tmp_path / "neg.json", [-0.03, -0.02, -0.04, -0.03, -0.02, -0.03]))
    assert neg["mean"] < 0 and neg["sigma"] > 2
    assert e190.verdict(neg, None)["outcome"] == "P1 HOLDS"
    pos = e190.paired_gap(artifact(tmp_path / "pos.json", [0.03, 0.02, 0.04, 0.03, 0.02, 0.03]))
    assert e190.verdict(pos, None)["outcome"] == "THE FALSIFIER FIRES"
    null = e190.paired_gap(artifact(tmp_path / "null.json", [-0.01, 0.01, -0.005, 0.005]))
    assert "UNRESOLVED" in e190.verdict(null, None)["outcome"]


def test_p2_compares_the_gap_against_the_other_circuit():
    small = {"mean": -0.02, "sigma": 3.0, "n": 144}
    big = {"mean": -0.012, "sigma": 1.0, "n": 3}
    assert "agrees" in e190.verdict(small, big)["P2"]
    assert "does NOT agree" in e190.verdict({"mean": -0.005, "sigma": 3.0, "n": 144}, big)["P2"]
    assert e190.verdict(small, {"mean": -0.02})["P2"] == "tied"


def test_the_reader_reproduces_the_registration_s_arithmetic_on_the_artifact_that_exists():
    """The live tie to the registration: `e10_rung_side.json`'s three replicates are `+0.0278 -0.0625 -0.0000` on
    accuracy, mean −0.0116 with sd 0.0462 and 0.43σ from zero. If this drifts, the registration's arithmetic and
    this reader are no longer about the same quantity."""
    g = e190.paired_gap(Path("runs/e10_rung_side.json"), "accuracy")
    assert g is not None and g["n"] == 3
    assert g["mean"] == pytest.approx(-0.011574, abs=5e-4)
    assert g["sd"] == pytest.approx(0.0462, abs=5e-4)
    assert g["sigma"] == pytest.approx(0.43, abs=0.02)
    assert g["n_negative"] == 2 and g["n_positive"] == 1
    assert e190.verdict(g, None)["outcome"].startswith("UNRESOLVED")
    # and the same three replicates on the other quantity, which the registration is NOT about
    f = e190.paired_gap(Path("runs/e10_rung_side.json"), "forgetting")
    assert f["mean"] == pytest.approx(0.0035, abs=5e-4), f
    assert (f["mean"] > 0) != (g["mean"] > 0), "the two quantities disagree in sign on these three replicates"


# --- the artifact, when it exists -------------------------------------------------------------------------------

ARTIFACT = Path("runs/e178_rung_side_cs300_144reps.json")


@pytest.mark.skipif(not ARTIFACT.is_file(), reason="e178's artifact has not been written yet")
def test_the_registered_read_runs_on_the_real_artifact_when_it_lands():
    """The guard that makes the landing self-detecting: from the moment the JSON exists, every run of this suite
    exercises the read on real data, so a malformed or half-written artifact fails here rather than at the moment
    someone remembers to look.

    It asserts the reader's mechanics and NOT the verdict: P1 may hold, the falsifier may fire, or the result may be
    unresolved, and all three are outcomes the registration names. What must hold is that the artifact carries both
    arms at the registered replicate count, that the paired gap is computable, and that the verdict is one of the
    four registered outcomes.
    """
    g = e190.paired_gap(ARTIFACT, "accuracy")
    assert g is not None, "the artifact exists and the registered quantity must be readable from it"
    assert g["n"] == 144, f"the registration is 144 replicates, the artifact has {g['n']}"
    assert g["basis"] == "side" and g["circuit_size"] == 300
    assert g["sd"] > 0, "a zero sd over 144 replicates would mean the arms are not independent"
    v = e190.verdict(g, e190.paired_gap(Path("runs/e10_rung_side.json"), "accuracy"))
    assert v["outcome"].startswith(("P1 HOLDS", "THE FALSIFIER FIRES", "UNRESOLVED")), v
    assert v["P1"] in ("holds", "does not hold") and v["falsifier"] in ("fires", "does not fire")
    assert g["timing_s"], "rule 49: the artifact carries its own cost and it is the figure to quote"
