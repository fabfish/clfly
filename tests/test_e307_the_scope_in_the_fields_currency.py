"""`e307` reads the front page's scope clause for the currency it is written in, so the tests pin the clause
extraction, the three cues, both faces of the three claims, and the live invariant.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e307_the_scope_in_the_fields_currency as e307


def _readme(clause_body, before="One brain, no catastrophic forgetting.\n"):
    return before + "\n" + clause_body + "\n\nThis repository asks a narrow question.\n"


def test_the_clause_is_the_blockquote_and_not_the_readme(tmp_path):
    text = _readme("> **Scoped 2026-09-29.** The corpus measures it in `mean_forgetting`.\n"
                   "> A second line of the same clause.\n"
                   "\n"
                   "A paragraph outside the clause that mentions the shortfall and e304.\n")
    p = tmp_path / "README.md"
    p.write_text(text, encoding="utf-8")
    c = e307.clause(text)
    assert c.startswith("> **Scoped") and "second line" in c, c
    # the paragraph outside the blockquote is not part of the clause, so its cues do not count
    assert "outside the clause" not in c, c
    r = e307.reading(p)
    assert r["mark"] is True and r["field"] is True, r
    assert r["decomposition"] == [] and r["units"] == [], r
    assert r["absences"] >= 1, r


def test_a_readme_with_no_clause_is_refused(tmp_path):
    p = tmp_path / "README.md"
    p.write_text("One brain, no catastrophic forgetting.\n", encoding="utf-8")
    r = e307.reading(p)
    assert r["mark"] is False and e307.judge(r)[0]["verdict"].startswith("REFUSED"), r


def _reading(field=True, cues=(), units=(), mark=True, chars=800, absences=2):
    return {"mark": mark, "chars": chars, "field": field, "decomposition": list(cues),
            "units": list(units), "absences": absences}


def test_the_three_claims_read_both_faces():
    full = _reading(cues=("the shortfall",), units=("e304",))
    j = {r["id"]: r for r in e307.judge(full)}
    for cid in ("N1", "N2", "N3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # the as-found reading of this unit: the field is named and the currency is not
    as_found = _reading(cues=(), units=())
    j = {r["id"]: r for r in e307.judge(as_found)}
    assert j["N1"]["verdict"].startswith("MET"), j["N1"]
    assert j["N2"]["verdict"].startswith("FALSIFIER FIRED"), j["N2"]
    assert j["N3"]["verdict"].startswith("FALSIFIER FIRED"), j["N3"]
    # and each of the three is falsified on its own
    assert e307.judge(_reading(field=False, cues=("the shortfall",), units=("e304",)))[0]["verdict"] \
        .startswith("FALSIFIER FIRED")
    assert e307.judge(_reading(cues=(), units=("e304",)))[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e307.judge(_reading(cues=("the shortfall",), units=()))[2]["verdict"].startswith("FALSIFIER FIRED")


def test_the_live_clause_satisfies_the_invariant():
    r = e307.reading()
    assert r["mark"] is True, r
    assert r["field"] is True, r
    assert r["decomposition"], r
    assert r["units"], r
    # the scope is still `e299`'s: the front page still states its two absences and still carries its marker
    assert r["absences"] == 2, r["absences"]
    assert "Scoped 2026-09-29" in e307.README.read_text(encoding="utf-8")
    claims = {x["id"]: x["verdict"] for x in e307.judge(r)}
    for cid in ("N1", "N2", "N3"):
        assert claims[cid].startswith("MET"), claims[cid]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e307_the_scope_in_the_fields_currency.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["field"] is True and d["decomposition"] and d["units"], d
    assert d["absences"] == 2, d["absences"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("N1", "N2", "N3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
