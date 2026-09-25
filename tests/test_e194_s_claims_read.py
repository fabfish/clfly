from __future__ import annotations

import json

from pathlib import Path

import numpy as np
import pytest

from experiments import e194_s_claims_read as e194


def test_the_verdict_is_the_registrations_own_ordering_of_bar_falsifier_and_null():
    """Each claim names a bar and a falsifier, and a measurement that clears neither is reported as between them
    rather than forced into one. S1 also names a null."""
    s1 = dict(near=10.0, far=55.0, far_minus_near=45.0)
    assert e194.judge(s1, "far_minus_near", ">=", 40.0, "<", 15.0, (("near", "far"), 30.0, 60.0)) == "MET"
    assert e194.judge(dict(s1, far_minus_near=10.0), "far_minus_near", ">=", 40.0, "<", 15.0,
                      (("near", "far"), 30.0, 60.0)) == "FALSIFIER FIRED"
    assert e194.judge(dict(s1, far_minus_near=25.0), "far_minus_near", ">=", 40.0, "<", 15.0,
                      (("near", "far"), 30.0, 60.0)) == "between the bar and the falsifier"
    # the null is a statement about EACH TERM, not about their difference: 35 points of separation with one term
    # outside the band is not the registered null, and the first version applied the band to the difference
    inside = dict(near=40.0, far=55.0, far_minus_near=15.0)
    assert e194.judge(inside, "far_minus_near", ">=", 41.0, "<", 15.0,
                      (("near", "far"), 30.0, 60.0)) == "the registered null"
    straddling = dict(near=10.0, far=45.0, far_minus_near=35.0)
    assert e194.judge(straddling, "far_minus_near", ">=", 40.0, "<", 15.0,
                      (("near", "far"), 30.0, 60.0)) == "between the bar and the falsifier", \
        "the difference is in the band but one term is not, and the registration names the terms"
    # a claim with no null falls through to the middle class
    assert e194.judge(dict(near=49.0), "near", "<", 50.0, ">=", 50.0, None) == "MET"
    assert e194.judge(dict(near=60.0), "near", "<", 50.0, ">=", 50.0, None) == "FALSIFIER FIRED"


def test_a_claim_whose_level_has_not_landed_is_refused_and_counted():
    """The reader exists before the artifact, so the failure mode that matters is a refusal with a reason rather
    than a number computed from levels that do not exist."""
    assert e194.report({}) == len(e194.CLAIMS), "every claim is refused when nothing is measured"
    # a level present but carrying only some of the quantities refuses exactly the claims that need the missing
    # ones -- computed from the table rather than hardcoded, which broke twice as claims were added to it
    partial = {0.6000: {"near": 20.0, "far": 82.0, "far_minus_near": 62.0}}
    expect = sum(1 for c in e194.CLAIMS if c[2] not in partial[0.6000])
    assert expect > 0
    assert e194.report(partial) == expect


def test_the_claims_name_quantities_the_measure_function_actually_produces():
    """A key spelled wrongly in the table would make every verdict a refusal, and a refusal is a plausible-looking
    output. The midpoint is measured, so the keys can be checked against it."""
    levels = [Path("runs/e193_r32_overlap050_methods_40reps.json")]
    if not levels[0].is_file():
        pytest.skip("the midpoint artifact is not in this checkout")
    values = e194.measure(levels)
    assert values, values
    vals = values[0.3333]
    for cid, ach, key, *_ in e194.CLAIMS:
        assert key in vals, f"{cid} names {key}, which measure() did not produce: {sorted(vals)}"
    # and the four claims are stated at the LAST intermediate level, not at the midpoint the P1/P2 pair names
    assert {c[1] for c in e194.CLAIMS} == {0.6000}
    # the midpoint's own values, which the registrations quote
    assert vals["far"] == pytest.approx(82.1, abs=0.1)
    assert vals["near"] == pytest.approx(20.0, abs=0.1)
    assert vals["far_minus_analytic"] == pytest.approx(65.6, abs=0.1)


def test_the_cost_decomposition_closes_and_s5_fires_where_the_cost_came_from():
    """The accuracy cost IS a learning term plus a retention term. The runner records `learned[j]` -- task j's
    accuracy right after learning it -- and `final_per_task[j]`, with `mean_forgetting` the mean drop over the first
    T-1 tasks, so `mean(final_per_task[:-1]) == mean(learned[:-1]) - mean_forgetting` **exactly**. A reader whose two
    components do not add up to the measured cost is reading different tasks on each side, and the identity is
    checked per replicate rather than on the means."""
    levels = [Path(f"runs/e193_r32_overlap{n:03d}_methods_40reps.json") for n in (25, 50)]
    if not all(p.is_file() for p in levels):
        pytest.skip("the interior level artifacts are not in this checkout")
    for path in levels + [e194.DECOMPOSITION_BASELINE]:
        for r in e194.load(path)["methods"]["naive"]["replicates"]:
            assert np.mean(r["final_per_task"][:-1]) == pytest.approx(
                np.mean(r["learned"][:-1]) - r["mean_forgetting"], abs=1e-12), path
    values = e194.measure(levels)
    mid = values[0.3333]
    assert mid["learned_older"] == pytest.approx(-0.03255, abs=1e-4)
    assert mid["learned_older_sigma"] == pytest.approx(8.10, abs=0.05)
    assert mid["forgetting_cost"] == pytest.approx(0.00833, abs=1e-4)
    assert mid["forgetting_cost_sigma"] == pytest.approx(0.79, abs=0.05)
    # the earlier level is the other way round: learning BETTER, forgetting unresolved
    early = values[0.1429]
    assert early["learned_older"] == pytest.approx(0.00651, abs=1e-4)
    assert early["learned_older_sigma"] == pytest.approx(2.03, abs=0.05)
    # S5's own verdicts, on the two values that exist
    s5 = next(c for c in e194.CLAIMS if c[0] == "S5")
    assert e194.judge(mid, s5[2], s5[3], s5[4], s5[5], s5[6], s5[7]) == "FALSIFIER FIRED"
    assert e194.judge(early, s5[2], s5[3], s5[4], s5[5], s5[6], s5[7]) == "MET"
    assert e194.judge(dict(mid, learned_older=-0.015), s5[2], s5[3], s5[4], s5[5], s5[6], s5[7]) == \
        "between the bar and the falsifier"


def test_the_fitting_deficit_is_arm_independent_including_the_matched_random_control():
    """The 0.3333 excursion is the same size in all three arms -- `naive` -0.03255 (8.10σ), the connectome-masked
    penalty arm -0.04010 (9.92σ), and the SIZE-MATCHED RANDOM CONTROL -0.03516 (7.55σ). So it is a property of the
    task set at that achieved overlap and not of the method, and not of WHICH neurons the tasks share either, since
    the control draws its sharing at random. The per-arm baselines come from the same inert-fields admission the dose
    reads use, and the keys are dotted for the arms S5 does not read."""
    levels = [Path(f"runs/e193_r32_overlap{n:03d}_methods_40reps.json") for n in (25, 50)]
    if not all(p.is_file() for p in levels):
        pytest.skip("the interior level artifacts are not in this checkout")
    values = e194.measure(levels)
    mid, early = values[0.3333], values[0.1429]
    for arm, sigma in (("ewc-block", 9.92), ("ewc-block-rand", 7.55)):
        assert mid[f"{arm}.learned_older"] < -0.030, (arm, mid[f"{arm}.learned_older"])
        assert mid[f"{arm}.learned_older_sigma"] == pytest.approx(sigma, abs=0.1)
        # and at the earlier level the same arms show NO fitting deficit
        assert abs(early[f"{arm}.learned_older"]) < 0.006, (arm, early[f"{arm}.learned_older"])
    # the penalty arm's cost at the earlier level is forgetting instead -- the split the finding is about
    assert early["ewc-block.forgetting_cost_sigma"] == pytest.approx(4.10, abs=0.1)
    assert mid["ewc-block.forgetting_cost_sigma"] == pytest.approx(1.60, abs=0.1)
    # S6 reads the control's dip, and it is MET where S5 fires
    s6 = next(c for c in e194.CLAIMS if c[0] == "S6")
    assert s6[2] == "ewc-block-rand.learned_older"
    assert e194.judge(mid, s6[2], s6[3], s6[4], s6[5], s6[6], s6[7]) == "MET"


def _levels_artifact_like_the_launch(path, near, far, forgetting, accuracy, arms=("naive", "ewc-block-rand")):
    """A synthetic level at target `--input_overlap 0.75`, with its config DERIVED from `e116`'s rather than written
    from scratch: the admission rule compares every key, so a minimal config would be refused for differing in
    `circuit_size`, `iters` and the rest, and the pre-flight would then be testing the refusal instead of the read."""
    path.parent.mkdir(parents=True, exist_ok=True)
    base = json.loads(Path("runs/e116_r32_40reps.json").read_text(encoding="utf-8"))
    config = dict(base["config"], input_overlap=0.75, methods=",".join(arms))
    config.pop("json_out", None)
    methods = {}
    for arm in arms:
        reps = []
        for _ in range(40):   # the readers pair by replicate index, so the count has to match the baselines'
            def row(j, vals):
                return {"task": j, "per_task": [{"first_order": v} for v in vals]}
            reps.append({
                "mean_forgetting": forgetting,
                "forgetting_per_task": [forgetting, forgetting, forgetting],
                "final_accuracy": accuracy,
                "learned": [accuracy + forgetting] * 3,
                "final_per_task": [accuracy] * 3,
                "interference": [row(0, [0.0, near, far]), row(1, [0.0, 0.0, near])],
            })
        methods[arm] = {"replicates": reps}
    path.write_text(json.dumps({"config": config, "methods": methods}), encoding="utf-8")
    return path


def test_a_level_at_the_pending_achieved_overlap_produces_verdicts_not_refusals(tmp_path, capsys):
    """Pre-flight for the artifact that has not landed. A reader that REFUSES when the artifact finally appears wastes
    the run that waited for it, and a refusal cannot be told from a level that is not there -- which is the defect the
    reader's own `levels found` line was added for. So the pending achieved overlap is exercised on a synthetic level
    first, with all six claims required to return a verdict."""
    lvl = _levels_artifact_like_the_launch(tmp_path / "runs" / "synth075.json",
                                          near=0.05, far=0.03, forgetting=0.08, accuracy=0.90)
    values = e194.measure([lvl])
    vals = values.get(0.6)
    assert vals, f"the synthetic 0.75 level produced no values: {values}"
    for cid, ach, key, *_ in e194.CLAIMS:
        assert ach == 0.6000, cid
        assert key in vals, f"{cid} names {key}, absent at achieved 0.6 -- that claim would be REFUSED"
    e194.report(values)
    out = capsys.readouterr().out
    assert "REFUSED" not in out, out
    assert "levels found: achieved 0.6" in out, out


def test_a_replicate_count_that_does_not_match_the_baseline_is_refused_not_crashed(tmp_path, capsys):
    """The pre-flight found this. `e191` guarded its ANCHOR pairing against a count mismatch and not its BASELINE
    pairing, so a level with four replicates against the live forty raised a broadcast error inside `paired` and took
    the whole read with it -- including the levels that were fine. A crash is worse than a refusal. `e188`'s mirror
    defect was the other way round: it `continue`d silently, so an arm with the wrong count vanished with no trace.
    Both now refuse with the counts named, and both reports print the refusal instead of a bare level heading."""
    lvl = _levels_artifact_like_the_launch(tmp_path / "runs" / "short.json",
                                          near=0.05, far=0.03, forgetting=0.08, accuracy=0.90)
    d = json.loads(lvl.read_text(encoding="utf-8"))
    for arm in d["methods"].values():
        arm["replicates"] = arm["replicates"][:4]
    lvl.write_text(json.dumps(d), encoding="utf-8")
    values = e194.measure([lvl])
    assert not values, f"a four-replicate level produced values against forty-replicate baselines: {values}"
    e194.report(values)
    out = capsys.readouterr().out
    assert "levels found: NONE" in out, out


def test_the_readers_take_explicit_endpoints_which_is_what_a_second_draw_needs():
    """A family on a different support draw cannot be admitted against this draw's baselines: `support_seed` is not an
    inert field and should not be, since a different draw is a different realization of the x-axis. So `measure`
    threads `baseline`, `candidates` and `overlap1`, and this pins that the threading reaches the readers: with `e153`
    (overlap 1.0) as the baseline the progress fractions are REFUSED -- the denominator is not a 0 -> 1 change -- while
    the cost decomposition still resolves, which is what separates a threaded read from a refused one."""
    levels = [Path("runs/e193_r32_overlap050_methods_40reps.json")]
    e153 = Path("runs/e153_r32_overlap1_methods_40reps.json")
    if not levels[0].is_file() or not e153.is_file():
        pytest.skip("the midpoint artifact or e153 is not in this checkout")
    default = e194.measure(levels)[0.3333]
    threaded = e194.measure(levels, baseline=e153, candidates=[e153], overlap1=e153)[0.3333]
    assert "near" in default and "learned_older" in default
    assert "near" not in threaded, threaded
    assert "learned_older" in threaded, threaded
    assert abs(threaded["learned_older"] - default["learned_older"]) > 1e-6, "the threading did not reach the readers"


def test_the_cli_takes_the_endpoints_and_echoes_which_draw_they_belong_to(capsys):
    """A replicated family's read has to be a COMMAND rather than a snippet, and it has to say whose endpoints it
    used: `--baseline`, `--candidate` and `--overlap1` reach `measure`, and the echo is what makes a reader notice
    that a draw-1 family was read against draw-1 baselines rather than silently refused against draw 0's."""
    rc = e194.main(["--dose", "runs/e193_r32_overlap050_methods_40reps.json",
                    "--baseline", "runs/e153_r32_overlap1_methods_40reps.json",
                    "--candidate", "runs/e153_r32_overlap1_methods_40reps.json",
                    "--overlap1", "runs/e153_r32_overlap1_methods_40reps.json"])
    out = capsys.readouterr().out
    assert "endpoints given: baseline runs/e153" in out, out
    # the six claims are all stated at achieved 0.6 and this dose carries 0.3333, so the read refuses them -- the
    # point of the test is that it refused for THAT reason and echoed the endpoints while doing it
    assert rc >= 1, out


def test_the_replication_table_calibrates_on_draw_zero_before_it_is_applied_to_draw_one(capsys):
    """The four second-draw claims are decidable BEFORE draw 1 exists, because draw 0 satisfies them: R1 needs
    `learned (older)` at or below -0.0200 (draw 0: -0.0326), R2 a gap of at least 40 points (draw 0: 62.1), R3a
    forgetting at or above +0.0200 (draw 0: +0.0318) and R3b an absolute `learned (older)` at or below 0.0100 (draw
    0: 0.0010). A replication table whose own claims the family being replicated FAILS would fire its falsifiers for
    the wrong reason, so the calibration is asserted rather than assumed."""
    lv = [Path(f"runs/e193_r32_overlap{n:03d}_methods_40reps.json") for n in (25, 50)]
    e116 = Path("runs/e116_r32_40reps.json")
    e144 = Path("runs/e144_r32_overlap1_methods_40reps.json")
    if not all(p.is_file() for p in lv + [e116, e144]):
        pytest.skip("the draw-0 family is not in this checkout")
    values = e194.measure(lv + [e144], baseline=e116, candidates=[e116], overlap1=e144)
    for cid, ach, key, op, bar, fals_op, fals, null_spec, _ in e194.CLAIMS_REPLICATION:
        assert ach in values and key in values[ach], (cid, sorted(values))
        assert e194.judge(values[ach], key, op, bar, fals_op, fals, null_spec) == "MET", (cid, values[ach][key])
    # and the table is selectable from the command line, with the endpoints that a second draw needs
    rc = e194.main(["--claims", "replication", "--dose", str(lv[1]), "--dose", str(e144),
                    "--baseline", str(e116), "--candidate", str(e116), "--overlap1", str(e144)])
    out = capsys.readouterr().out
    assert "== the R claims" in out and "R1:" in out and "R3b:" in out, out
    assert rc == 0, "draw 0 satisfies all four claims, so nothing should be refused"
