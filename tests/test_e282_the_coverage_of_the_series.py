"""`e282` measures how much of the paper the series can read, and its second claim's falsifier fires. The tests pin the
two definitions, both faces of the three claims, and the live census -- as bounds, since a clause added to the paper
moves the counts and must not move the reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e282_the_coverage_of_the_series as e282


def _census(sentences=10, checkable=10, read=1, unread=(" 9 of 9 artifacts were on disk.", ),
            quantified=0, by_form=None, digit_only=0, with_digit=0, both=0):
    return {"sentences": sentences, "checkable": checkable, "read": read, "unread_checkable": list(unread),
            "quantified_unread": quantified, "by_form": by_form or {k: 1 for k in e282.INSTRUMENTS},
            "read_examples": [], "digit_checkable": checkable - digit_only, "quantifier_only": digit_only,
            "unread_with_digit": with_digit, "read_with_digit": read, "unread_both": both, "quantifier_hist": {}}


def test_the_sentence_split_and_the_two_legs_of_checkable():
    text = ("One claim is stated. And a second is not; Then a third: "
            "EWC is a Kalman filter. Theta is a vector.")
    ss = e282.sentences(text)
    assert len(ss) == 5 and ss[1].startswith("And a second") and ss[-1].startswith("Theta is a vector"), ss
    # a division after a semicolon stays inside the sentence when the next word is lower case, which is the
    # module's stated limit: the split is a lexical rule and not a parser
    assert "not; then a fourth" not in " ".join(ss)
    assert e282.checkable("17 arms were on disk")
    assert e282.checkable("every one of the stored runs used 16")
    assert not e282.checkable("theta is a vector, projected onto a basis")
    # a digit inside a filename is a digit, which is one of the definitions' stated limits
    assert e282.checkable("the run `e140_r32_methods` was re-run")


def test_census_counts_what_the_instruments_read_and_what_they_leave():
    forms = e282.forms()
    phrase = next(f["form"] for f in forms if f["instrument"] == "e268" and f["kind"] == "phrase")
    text = (f"{phrase} :: the sentence an instrument reads. "
            "The 27 arms are not enumerated. "
            "No instrument registered a phrase for it. "
            "The basis is projected onto a subspace.")
    c = e282.census(text)
    # one sentence read, one unread with a digit, one unread quantified, and one that is not checkable at all
    assert c["sentences"] == 4 and c["checkable"] == 3, c
    assert c["read"] == 1 and c["by_form"] == {"e268": 1}, c
    assert len(c["unread_checkable"]) == 2 and c["unread_with_digit"] == 1, c
    assert c["quantified_unread"] == 1 and c["unread_both"] == 0, c
    assert c["quantifier_hist"] == {"no": 1}, c["quantifier_hist"]
    assert c["digit_checkable"] == 2 and c["quantifier_only"] == 1, c
    # every registered instrument is searchable, and the empty text is refused rather than judged
    assert len({f["instrument"] for f in forms}) == len(e282.INSTRUMENTS), forms
    assert e282.census("")["checkable"] == 0


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e282.judge(_census(checkable=100, read=2))}
    assert j["C1"]["verdict"].startswith("MET"), j["C1"]
    j = {r["id"]: r for r in e282.judge(_census(checkable=100, read=50))}
    assert j["C1"]["verdict"].startswith("FALSIFIER FIRED"), j["C1"]

    j = {r["id"]: r for r in e282.judge(_census(unread=("a 7 and b 8 and c 9",) * 3, quantified=0))}
    assert j["C2"]["verdict"].startswith("MET"), j["C2"]
    j = {r["id"]: r for r in e282.judge(_census(unread=("a 7 and b 8 and c 9",) * 3, quantified=1))}
    assert j["C2"]["verdict"].startswith("FALSIFIER FIRED"), j["C2"]

    j = {r["id"]: r for r in e282.judge(_census())}
    assert j["C3"]["verdict"].startswith("MET"), j["C3"]
    silent = {k: 1 for k in e282.INSTRUMENTS if k != "e279"}
    j = {r["id"]: r for r in e282.judge(_census(by_form=silent))}
    assert j["C3"]["verdict"].startswith("FALSIFIER FIRED"), j["C3"]
    assert e282.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e282.judge(_census(checkable=0))[0]["verdict"].startswith("REFUSED")


def test_the_live_paper_is_read_as_the_finding_states_it():
    """The paper is a numbers paper, so nearly every sentence is one an instrument could read; the series reads a
    handful of them; and the residue is not typed -- which is the falsifier the finding reports."""
    if not e282.PAPER.exists():
        return
    c = e282.census(e282.PAPER.read_text(encoding="utf-8"))
    assert c["sentences"] >= 400 and c["checkable"] >= 300, c
    # the digit leg carries the set, and the quantifier leg is a small addition to it
    assert c["digit_checkable"] <= c["checkable"]
    assert c["quantifier_only"] < c["checkable"] / 5, c
    assert 2 <= c["read"] <= 40, c["read"]
    assert c["read"] / c["checkable"] < 0.5, c
    assert set(c["by_form"]) == set(e282.INSTRUMENTS), c["by_form"]
    # C2's falsifier: the unread set is not typed, and both legs overlap heavily inside it
    assert c["quantified_unread"] / len(c["unread_checkable"]) >= 1 / 3, c
    assert c["unread_both"] > c["quantified_unread"] / 2, c
    assert c["unread_both"] <= min(c["quantified_unread"], c["unread_with_digit"]), c
    assert set(c["quantifier_hist"]) <= {q.strip() for q in e282.QUANTIFIERS}, c["quantifier_hist"]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e282_the_coverage_of_the_series.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    counts, claims = d["counts"], {x["id"]: x for x in d["claims"]}
    assert counts["sentences"] >= 400 and counts["checkable"] >= 300, counts
    assert counts["read"] >= 2 and counts["read"] / counts["checkable"] < 0.5, counts
    assert claims["C1"]["verdict"].startswith("MET"), claims["C1"]
    assert claims["C3"]["verdict"].startswith("MET"), claims["C3"]
    assert claims["C2"]["verdict"].startswith("FALSIFIER FIRED"), claims["C2"]
    # the artifact was written from the paper as it stands. A clause added to the paper moves the counts, so the
    # artifact is held to a band rather than to the digit: the reading is what must not move, and the gate re-runs
    # this module before it re-reads the artifact.
    live = e282.census(e282.PAPER.read_text(encoding="utf-8"))
    for k in ("sentences", "checkable", "read", "quantified_unread", "digit_checkable", "unread_both"):
        assert abs(counts[k] - live[k]) <= 0.1 * max(live[k], 1), (k, counts[k], live[k])
    assert set(d["counts"]["by_form"]) == set(e282.INSTRUMENTS), d["counts"]["by_form"]
