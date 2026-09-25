"""`e168`'s verdict is an *identification*, and the tests have to pin both the exposure and the recovery.

The exposure is a count (31 of 38 artifacts cannot say which control sample they used) and the recovery is a
reconstruction that **reproduces all three recorded fingerprints** — without that second half the unit would be a
caution rather than a measurement, and a test that only checked the first half would pass on a corpus where the
draw was unrecoverable. The reconstruction needs the connectome, so it skips cleanly without `data/`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from experiments import e168_draw_fingerprint_census as e168
from experiments.e151_pertask_contrast_audit import load_arm, paired

from clfly.connectome import graph

DATA = Path(graph.DEFAULT_DATA_DIR)
HAS_DATA = (DATA / graph.CONNECTIVITY_FILE).exists() and (DATA / graph.ANNOTATION_FILE).exists()
needs_data = pytest.mark.skipif(not HAS_DATA, reason="connectome data not downloaded")


def payload(methods, draw=None):
    p = {"methods": {m: {"replicates": []} for m in methods}}
    if draw is not None:
        p["partition_draw"] = {"fingerprint_sha1": draw, "matched_random_draw_seed": 1}
    return p


def test_a_fingerprint_is_read_only_from_a_draw_that_was_actually_recorded():
    assert e168.fingerprint(payload(["ewc-block-rand"], "abc123")) == "abc123"
    assert e168.fingerprint(payload(["ewc-block-rand"])) is None
    assert e168.fingerprint({"partition_draw": "not a dict"}) is None
    assert e168.fingerprint({}) is None


def test_only_a_rand_arm_needs_a_draw():
    assert e168.rand_arms(payload(["naive", "ewc", "ewc-block-rand"])) == ["ewc-block-rand"]
    assert e168.rand_arms(payload(["naive", "ewc", "replay"])) == []
    assert e168.rand_arms({}) == []


def test_a_pair_with_the_draw_on_one_side_is_classified_as_one_side_only():
    a = {"name": "a", "payload": payload(["ewc-block-rand"], "fp1")}
    b = {"name": "b", "payload": payload(["ewc-block-rand"])}
    c = {"name": "c", "payload": payload(["ewc-block-rand"], "fp1")}
    assert e168.exposure([a, b])["pairs"]["one_side_only"] == 1
    assert e168.exposure([a, c])["pairs"]["both_same"] == 1
    assert e168.exposure([b, {"name": "d", "payload": payload(["ewc-block-rand"])}])["pairs"]["neither"] == 1
    assert e168.exposure([a, {"name": "e", "payload": payload(["naive"])}])["artifacts_with_a_rand_arm"] == 1


def test_the_corpus_records_the_draw_in_a_fifth_of_the_artifacts_that_need_it():
    from experiments.e103_reproducibility_audit import load_artifacts

    exp = e168.exposure(load_artifacts())
    # The counts grow with the corpus -- 38 rand-arm artifacts, 7 recording the draw and 31 not when this unit
    # was written, and every run the project makes from here adds to all three. What is pinned is the claim and
    # the census's own arithmetic, so that a growing corpus cannot quietly falsify the ratio or double-count.
    assert exp["artifacts_with_a_rand_arm"] >= 38
    assert exp["recording_the_draw"] >= 7
    assert exp["unidentifiable"] == exp["artifacts_with_a_rand_arm"] - exp["recording_the_draw"]
    # The claim is "MOST users of the control cannot say which draw they used", and it is a statement about a
    # ratio that moves as runs start recording their draws -- which is the point of `e168`'s work and the
    # reason `e178`, landing on 2026-09-25, moved 31/11 to 31/11-with-11-recording. The multiplier started at
    # 3x when the census was written; pinning it makes the test fail as the project succeeds.
    assert exp["unidentifiable"] > exp["recording_the_draw"], "most users of the control cannot say which"
    # the cell_class@800 triple is present, and the *list* is not pinned: the corpus gains fingerprints as new
    # bases and circuits are run with a recorded draw, and the meaningful check is per artifact -- that each
    # artifact's reconstruction reproduces its own recorded value, which `identified_draws` verifies.
    assert {"000b42be6ba2", "3058aa874ae6", "f6a658eabf9c"} <= set(exp["fingerprints"])
    assert exp["pairs"]["one_side_only"] > 200 and exp["pairs"]["both_different"] > 0


def test_two_samples_of_the_control_differ_by_a_measurable_amount_on_both_axes():
    size = e168.draw_size()
    base, wiring = size["base (input_overlap 0.0)"], size["wiring (input_overlap 1.0)"]
    assert base["n"] == wiring["n"] == 40
    assert base["forgetting"]["change"] == pytest.approx(0.0055, abs=5e-4)
    assert wiring["forgetting"]["change"] == pytest.approx(-0.0138, abs=5e-4)
    # neither draw pair resolves on either axis at 40 seeds: the sample is *small*, and that is the point
    for d in (base, wiring):
        assert abs(d["forgetting"]["sigma"]) < 2 and abs(d["newest"]["sigma"]) < 2


def test_the_lambda_step_was_under_the_draw_on_one_axis_which_is_why_the_recovery_matters():
    """The bound the identification rules out: had the draws differed, one column would have been lost."""
    pa, pb = e168.LAMBDA_PAIR
    ea, eb = load_arm(Path(pa), "ewc-block-rand"), load_arm(Path(pb), "ewc-block-rand")
    step_f = paired(eb["forgetting"], ea["forgetting"])
    step_n = paired(eb["newest"], ea["newest"])
    size = max(abs(d["forgetting"]["change"]) for d in e168.draw_size().values())
    size_n = max(abs(d["newest"]["change"]) for d in e168.draw_size().values())
    assert abs(step_f["change"]) < size, "the forgetting step is under the draw, so it needed the recovery"
    assert abs(step_n["change"]) > 3 * size_n, "the newest-task step is several times the draw and did not"


def test_the_pair_the_lambda_step_uses_has_the_draw_on_one_side_only():
    from experiments.e103_reproducibility_audit import load_artifacts

    arts = {a["name"]: a["payload"] for a in load_artifacts()}
    fp = {Path(p).name: e168.fingerprint(arts[Path(p).name]) for p in e168.LAMBDA_PAIR}
    assert fp["e144_r32_overlap1_methods_40reps.json"] is None
    assert fp["e153_r32_overlap1_methods_40reps.json"] == "000b42be6ba2"
    # the flag was added after e144's process began, which is why an artifact newer than the commit lacks it
    cfg = {a["name"]: a["config"] for a in load_artifacts()}
    assert "partition_seed" not in cfg["e144_r32_overlap1_methods_40reps.json"]
    assert cfg["e153_r32_overlap1_methods_40reps.json"].get("partition_seed", "absent") in (None, "absent", 0)


@needs_data
def test_the_reconstruction_reproduces_every_recorded_fingerprint():
    """The recovery, which is what makes this an identification rather than a caution."""
    from experiments.e103_reproducibility_audit import load_artifacts

    recorded = set(e168.exposure(load_artifacts())["fingerprints"])
    # the default basis's three seeds reproduce three of them, and the rest are reproduced *per artifact* by
    # `identified_draws`, which reconstructs each artifact's own inputs rather than the default ones
    rebuilt = {seed: e168.reconstruct_fingerprint(seed=seed) for seed in (0, 1, 2)}
    assert set(rebuilt.values()) <= recorded
    assert rebuilt[0] == "000b42be6ba2", "seed 0 is the default draw e144 used and e153 recorded"
    ids = e168.identified_draws(load_artifacts())
    assert not ids["mismatched"] and set(ids["recorded"].values()) == recorded


@needs_data
def test_every_rand_artifact_is_identified_and_the_recorded_ones_verify_the_reconstruction():
    """The extension: 9 recorded + 31 reconstructed, no disagreements, and the pairs fully classified.

    This is the test the *guard* is in: it reconstructs the artifacts that record a fingerprint as well, and a
    reconstruction that disagreed with them would be wrong rather than merely uncheckable. The first version of
    `draw_inputs` was, and it was this check that caught it -- the runner seeds the draw with `partition_seed`
    when the flag is set, so an artifact that set it draws from *that* seed, and four of the nine record one.
    """
    from experiments.e103_reproducibility_audit import load_artifacts

    ids = e168.identified_draws(load_artifacts())
    assert not ids["mismatched"], f"a recorded fingerprint contradicts its reconstruction: {ids['mismatched']}"
    assert len(ids["reconstructed"]) >= 40 and len(ids["recorded"]) >= 9
    assert len(set(ids["inputs"].values())) <= 8, "the partitions are cached by their determining tuple"
    # and the pairs are classified rather than mostly unidentifiable
    vals = sorted(ids["reconstructed"].values())
    same = sum(1 for i in range(len(vals)) for j in range(i + 1, len(vals)) if vals[i] == vals[j])
    assert same >= 440
