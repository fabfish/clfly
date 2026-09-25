from __future__ import annotations

from pathlib import Path

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
    # a level present but with only some of the quantities refuses only the claims that need the missing ones
    partial = {0.6000: {"near": 20.0, "far": 82.0, "far_minus_near": 62.0}}
    assert e194.report(partial) == 2, "S3 needs the analytic far and S4 needs the accuracy account"


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
