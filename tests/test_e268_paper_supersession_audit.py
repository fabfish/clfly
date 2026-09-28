"""`e268` checks a hand-made registry of supersessions against the paper, so the tests pin the window rule, the
registry's four questions per entry, both faces of the three claims, and the live state after the paper was corrected.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e268_paper_supersession_audit as e268


def test_the_window_is_bounded_and_empty_for_an_absent_phrase():
    text = "a" * 500 + "PHRASE" + "b" * 500
    w = e268.window(text, "PHRASE", span=50)
    assert "PHRASE" in w and len(w) == len("PHRASE") + 100, len(w)
    assert e268.window(text, "nowhere") == ""


def test_check_reads_the_paper_the_finding_and_the_note(tmp_path):
    finding = tmp_path / "superseding.md"
    finding.write_text("the replacement is 1.64x here", encoding="utf-8")
    paper = tmp_path / "paper.md"
    pad = "filler " * 200  # wider than a window, so the two phrases cannot share one
    paper.write_text("a number (3.34x at cs 800) with nothing beside it " + pad
                     + " and 2.0x **[CORRECTED: it is 1.9x]** more text", encoding="utf-8")
    entries = (
        {"phrase": "3.34x at cs 800", "superseded_by": str(finding), "replacement": "1.64", "why": ""},
        {"phrase": "2.0x", "superseded_by": str(finding), "replacement": "1.64", "why": ""},
        {"phrase": "not in the paper", "superseded_by": str(finding), "replacement": "1.64", "why": ""},
        {"phrase": "3.34x at cs 800", "superseded_by": str(tmp_path / "absent.md"), "replacement": "1.64", "why": ""},
    )
    rows = e268.check(entries, paper=paper)
    assert rows[0]["in_paper"] and not rows[0]["carries_a_note"], rows[0]
    assert rows[1]["in_paper"] and rows[1]["carries_a_note"], rows[1]
    assert not rows[2]["in_paper"], rows[2]
    assert not rows[3]["finding_on_disk"] and not rows[3]["replacement_in_finding"], rows[3]
    assert rows[0]["finding_on_disk"] and rows[0]["replacement_in_finding"], rows[0]


def _row(in_paper=True, note=False, on_disk=True, replacement=True, phrase="p", repl="1"):
    return {"phrase": phrase, "in_paper": in_paper, "carries_a_note": note, "finding_on_disk": on_disk,
            "replacement_in_finding": replacement, "replacement": repl, "superseded_by": "x.md", "why": ""}


def test_the_three_claims_read_both_faces():
    stale = [_row(phrase="a"), _row(phrase="b")]
    j = {r["id"]: r for r in e268.judge(stale)}
    assert j["Q1"]["verdict"].startswith("MET") and "2 stale of 2" in j["Q1"]["measured"], j["Q1"]
    assert j["Q2"]["verdict"].startswith("MET") and j["Q3"]["verdict"].startswith("MET"), j
    # one stale phrase is under the bar, and a phrase outside the paper is not counted at all
    j = {r["id"]: r for r in e268.judge([_row(phrase="a"), _row(phrase="b", in_paper=False)])}
    assert j["Q1"]["verdict"].startswith("FALSIFIER FIRED"), j["Q1"]
    # a phrase its own citation does not support is what a provenance audit would see
    j = {r["id"]: r for r in e268.judge([_row(on_disk=False), _row(phrase="b")])}
    assert j["Q2"]["verdict"].startswith("FALSIFIER FIRED"), j["Q2"]
    # a replacement absent from its finding cannot be substituted
    j = {r["id"]: r for r in e268.judge([_row(replacement=False), _row(phrase="b")])}
    assert j["Q3"]["verdict"].startswith("FALSIFIER FIRED"), j["Q3"]


def test_the_live_registry_is_now_corrected_in_the_paper():
    """The finding's numbers on the artifact: three numbers the audits superseded, each carrying the replacement
    beside it, and Q1's own falsifier as the signature of the correction."""
    p = Path("runs/e268_paper_supersession_audit.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["registry"]
    assert len(rows) == 3, rows
    for r in rows:
        assert r["in_paper"] and r["carries_a_note"], r
        assert r["finding_on_disk"] and r["replacement_in_finding"], r
    assert {r["replacement"] for r in rows} == {"1.64", "2.91", "1.24"}, rows
    claims = {r["id"]: r for r in d["claims"]}
    assert claims["Q1"]["verdict"].startswith("FALSIFIER FIRED"), "the paper was corrected in the same fire"
    assert "0 stale of 3" in claims["Q1"]["measured"], claims["Q1"]
    assert claims["Q2"]["verdict"].startswith("MET") and claims["Q3"]["verdict"].startswith("MET"), claims
    paper = Path("docs/paper/clfly-v1.md").read_text(encoding="utf-8")
    assert paper.count("CORRECTED 2026-09-28") >= 3, "later units add their own corrections"
