"""`e281` is the series' own ledger, so the tests pin the six entries, both faces of the three claims and the live
state after the one outstanding correction was applied in the same fire.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e281_the_correction_ledger as e281


def test_the_ledger_reads_every_instrument_of_the_series():
    rows = e281.ledger()
    assert [r["instrument"] for r in rows] == list(e281.INSTRUMENTS), [r["instrument"] for r in rows]
    for r in rows:
        assert r["reads"] > 0, r
        assert isinstance(r["stale"], int) and r["stale"] >= 0, r
        assert isinstance(r["corrected"], bool), r
    assert sum(r["reads"] for r in rows) >= 100, sum(r["reads"] for r in rows)


def _rows(stale=(), corrected=True, reads=1):
    return [{"instrument": i, "reads": reads, "note": "", "stale": 1 if i in stale else 0,
             "corrected": corrected} for i in e281.INSTRUMENTS]


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e281.judge(_rows())}
    for cid in ("C1", "C2", "C3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # one instrument still stale is inside C2's bound, and it is named
    j = {r["id"]: r for r in e281.judge(_rows(stale=("e277",)))}
    assert j["C2"]["verdict"].startswith("MET") and "e277" in j["C2"]["measured"], j["C2"]
    # three is not
    j = {r["id"]: r for r in e281.judge(_rows(stale=("e270", "e277", "e278")))}
    assert j["C2"]["verdict"].startswith("FALSIFIER FIRED"), j["C2"]
    # a clean instrument with no correction means the check weakened rather than the paper being fixed
    j = {r["id"]: r for r in e281.judge(_rows(corrected=False))}
    assert j["C3"]["verdict"].startswith("FALSIFIER FIRED"), j["C3"]
    # and an instrument that read nothing is C1's
    j = {r["id"]: r for r in e281.judge([dict(r, reads=0) for r in _rows()])}
    assert j["C1"]["verdict"].startswith("FALSIFIER FIRED"), j["C1"]
    assert e281.judge([])[0]["verdict"].startswith("REFUSED")


def test_the_live_ledger_is_closed_because_the_one_item_it_named_was_corrected():
    """The finding's numbers on the artifact: six instruments reading 572 statements, no instrument left stale, and
    the correction clauses on the page."""
    p = Path("runs/e281_the_correction_ledger.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["ledger"]
    assert len(rows) == 6 and all(r["reads"] > 0 for r in rows), rows
    assert sum(r["reads"] for r in rows) >= 500, sum(r["reads"] for r in rows)
    assert [r["instrument"] for r in rows if r["stale"]] == [], rows
    for r in rows:
        assert r["corrected"], r
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("C1", "C2", "C3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "0 of 6" in claims["C2"]["measured"], claims["C2"]
