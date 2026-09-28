"""`e299` reads the front page's absence claim against the corpus's arms, so the tests pin the absence reader, the
distance-from-zero census, both faces of the three claims, and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e299_the_front_page_claim as e299


def test_the_absence_reader_and_its_cue_list():
    text = ("One brain, many behaviours, no catastrophic forgetting.\n\n"
            "Models are never used for forgetting curves.\n\n"
            "We recommend running more seeds.")
    rows = e299.absence_claims(text)
    # the first sentence is an absence claim; the second uses `never` in another sense and is not in the list
    assert len(rows) == 1, rows
    assert rows[0]["subjects"] == ["forgetting"], rows
    assert "never" not in e299.ABSENCE, e299.ABSENCE
    # a subject with no cue, and a cue with no subject
    assert e299.absence_claims("The memories are held in the mushroom body.") == []
    assert e299.absence_claims("We run without a GPU.") == []
    # the scope marker is read as a description
    assert e299.absence_claims("No catastrophic forgetting.\n\n> Scoped 2026-09-29: see below.")[0]["scoped"] is False
    assert e299.absence_claims("No catastrophic forgetting, scoped 2026-09-29.")[0]["scoped"] is True


def _art(path: Path, arms, rows=6, means=None):
    """A stand-in artifact. An arm whose mean is zero is built by *straddling* zero -- a ramp's distance from zero is
    scale-invariant, so a ramp can never be indistinguishable from zero however small it is."""
    payload = {"methods": {}}
    for i, a in enumerate(arms):
        mean = (means or {}).get(a, 0.05 * (i + 1))
        if mean == 0.0:
            vals = [0.02 * (-1) ** r for r in range(rows)]
        else:
            vals = [mean + 0.001 * r for r in range(rows)]
        payload["methods"][a] = {"replicates": [{"mean_forgetting": v} for v in vals]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload


def test_the_distance_from_zero_census(tmp_path):
    _art(tmp_path / "a.json", ("zero", "away"), means={"zero": 0.0, "away": 0.5})
    _art(tmp_path / "b.json", ("thin",), rows=2)          # below the replicate floor
    (tmp_path / "c.json").write_text("not json", encoding="utf-8")
    rows = e299.zeros(tmp_path)
    assert len(rows) == 2, rows
    at_zero = [x for x in rows if x["at_zero"]]
    assert [x["arm"] for x in at_zero] == ["zero"], rows
    # the smallest mean has the smallest distance from zero
    assert sorted(rows, key=lambda x: x["sigma"])[0]["arm"] == "zero", rows


def _reading(claims=None, arms=None):
    claims = claims if claims is not None else [{"sentence": 0, "cues": ["no catastrophic"], "subjects": ["forgetting"],
                                                 "text": "no catastrophic forgetting", "scoped": False}]
    arms = arms if arms is not None else [
        {"artifact": "a.json", "arm": "replay", "n": 40, "mean": 0.002, "sem": 0.003, "sigma": 0.6, "at_zero": True},
        {"artifact": "a.json", "arm": "naive", "n": 40, "mean": 0.09, "sem": 0.01, "sigma": 9.0, "at_zero": False},
        {"artifact": "b.json", "arm": "ewc", "n": 5, "mean": 0.04, "sem": 0.01, "sigma": 4.0, "at_zero": False}]
    return {"absence_claims": claims, "arms": arms}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e299.judge(_reading())}
    for cid in ("F1", "F2", "F3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a front page with no absence claim is F1's falsifier
    j = {r["id"]: r for r in e299.judge(_reading(claims=[]))}
    assert j["F1"]["verdict"].startswith("FALSIFIER FIRED"), j["F1"]
    # no arm at forty replicates inside two sigma is F2's
    arms = _reading()["arms"]
    arms[0]["n"] = 5
    j = {r["id"]: r for r in e299.judge(_reading(arms=arms))}
    assert j["F2"]["verdict"].startswith("FALSIFIER FIRED"), j["F2"]
    # most arms indistinguishable from zero is F3's
    arms = _reading()["arms"]
    for x in arms:
        x["at_zero"] = True
    j = {r["id"]: r for r in e299.judge(_reading(arms=arms))}
    assert j["F3"]["verdict"].startswith("FALSIFIER FIRED"), j["F3"]
    assert e299.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e299.judge({"arms": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_front_page_and_corpus():
    r = {"absence_claims": e299.absence_claims(e299.README.read_text(encoding="utf-8")),
         "arms": e299.zeros()}
    assert len(r["absence_claims"]) == 2, r["absence_claims"]
    at_zero = [x for x in r["arms"] if x["at_zero"]]
    assert len(r["arms"]) >= 280, len(r["arms"])
    assert len(at_zero) >= 50, len(at_zero)
    assert sum(1 for x in at_zero if x["n"] >= 40) >= 5, at_zero
    # the tightest bound on zero is a few thousandths against a baseline whose median is far larger
    tightest = min((x for x in at_zero if x["n"] >= 40), key=lambda x: x["sem"])
    baseline = [x["mean"] for x in r["arms"] if x["arm"] == "naive"]
    assert tightest["sem"] < 0.005, tightest
    import statistics
    assert statistics.median(baseline) > 0.05, statistics.median(baseline)
    # and most arms resolve away from zero, the largest far above it
    assert sum(1 for x in r["arms"] if not x["at_zero"]) > 2 * len(at_zero), len(r["arms"])
    assert max(x["sigma"] for x in r["arms"]) > 20, max(x["sigma"] for x in r["arms"])
    # the correction is in the README, as a description and not a claim
    assert "Scoped 2026-09-29" in e299.README.read_text(encoding="utf-8"), "the scope clause is missing"


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e299_the_front_page_claim.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["absence_claims"]) == 2, d["absence_claims"]
    assert d["scoped_marker_in_the_readme"] is True, d
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("F1", "F2", "F3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "64 of 294" in claims["F2"]["measured"], claims["F2"]
    assert "230 of 294" in claims["F3"]["measured"], claims["F3"]
