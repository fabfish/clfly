"""`e300` reads the abstract's numbered findings for their scope, so the tests pin the section reader, the nested
emphasis in a heading, both faces of the two claims, and the live four.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e300_the_abstracts_findings as e300

SYNTHETIC = """# A paper

## Abstract

Two findings.

1. **The diagonal pays.** Excess error against the Kalman oracle is 33%.

2. **And the tasks separate.** The subspace beats a random one at 7 sigma.

---

## A later section

1. Run it again.
2. Ask the reversed question.
"""


def test_the_reader_stays_inside_the_abstract():
    rows = e300.findings(SYNTHETIC)
    assert [x["n"] for x in rows] == [1, 2], rows
    assert rows[0]["heading"] == "The diagonal pays.", rows
    assert rows[0]["metrics"] == ["excess"] and "oracle" in rows[0]["comparators"], rows[0]
    assert "random" in rows[1]["comparators"] and rows[1]["metrics"] == ["sigma"], rows[1]
    # the later section's numbered list is not a finding, and no section is refused rather than half-read
    assert all(x["heading"] != "Run it again." for x in rows)
    assert e300.findings("no abstract here") == []


def test_a_heading_with_nested_emphasis_is_one_finding():
    text = ("## Abstract\n\n1. **The claim that this does *not* hold does not survive.** Excess against a random one.\n\n"
            "---\n")
    rows = e300.findings(text)
    assert len(rows) == 1, rows
    assert "*not*" in rows[0]["heading"], rows[0]
    assert rows[0]["metrics"] == ["excess"] and rows[0]["comparators"] == ["random"], rows[0]


def _reading(items=None):
    items = items if items is not None else [
        {"n": 1, "heading": "a", "text": "excess against the oracle", "metrics": ["excess"],
         "comparators": ["oracle"]},
        {"n": 2, "heading": "b", "text": "7 sigma against random", "metrics": ["σ"], "comparators": ["random"]}]
    return {"findings": items}


def test_the_two_claims_read_both_faces():
    j = {r["id"]: r for r in e300.judge(_reading())}
    assert j["A1"]["verdict"].startswith("MET"), j["A1"]
    assert j["A2"]["verdict"].startswith("MET"), j["A2"]
    # no list at all is A1's falsifier, and so is a single item
    j = {r["id"]: r for r in e300.judge(_reading([{"n": 1, "heading": "a", "text": "excess against the oracle",
                                                   "metrics": ["excess"], "comparators": ["oracle"]}]))}
    assert j["A1"]["verdict"].startswith("FALSIFIER FIRED"), j["A1"]
    # a finding with no metric, and one with no comparator, are A2's
    for key in ("metrics", "comparators"):
        items = _reading()["findings"]
        items[0][key] = []
        j = {r["id"]: r for r in e300.judge(_reading(items))}
        assert j["A2"]["verdict"].startswith("FALSIFIER FIRED"), (key, j["A2"])
    assert e300.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e300.judge({"findings": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_abstract_is_scoped():
    text = e300.PAPER.read_text(encoding="utf-8")
    rows = e300.findings(text)
    assert len(rows) == 4, [(x["n"], x["heading"][:40]) for x in rows]
    assert [x["n"] for x in rows] == [1, 2, 3, 4], rows
    # every headline names a metric and a comparator -- unlike the recommendations `e298` had to scope
    for x in rows:
        assert x["metrics"] and x["comparators"], x
    # the four headings are the abstract's four findings, not another section's list
    assert all("Run it again" not in x["heading"] for x in rows), rows
    assert sum(1 for x in rows if "diagonal" in x["comparators"]) >= 2, [x["comparators"] for x in rows]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e300_the_abstracts_findings.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["findings"]) == 4, d["findings"]
    claims = {x["id"]: x for x in d["claims"]}
    assert claims["A1"]["verdict"].startswith("MET"), claims["A1"]
    assert claims["A2"]["verdict"].startswith("MET"), claims["A2"]
    assert "4 of 4" in claims["A2"]["measured"], claims["A2"]
