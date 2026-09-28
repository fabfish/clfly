"""`e293` reads the paper's draw-sd table against its own error bars, so the tests pin the interval arithmetic, the
ordering test, the draws a ratio needs, both faces of the three claims, and the live numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e293_how_many_draws_a_draw_sd_needs as e293


def test_the_interval_is_the_chi_square_one():
    lo, hi = e293.interval(1.0, 5)                      # five draws, four degrees of freedom
    assert abs(lo - math.sqrt(4 / 11.1433)) < 1e-3, (lo, hi)
    assert abs(hi - math.sqrt(4 / 0.4844)) < 1e-2, (lo, hi)
    assert lo < 1 < hi
    # one draw is guarded to a single degree of freedom rather than dividing by zero
    lo1, hi1 = e293.interval(1.0, 1)
    assert lo1 < 1 < hi1 and hi1 > hi, (lo1, hi1)
    # more draws narrow it
    lo8, hi8 = e293.interval(1.0, 8)
    assert (hi8 - lo8) < (hi - lo), ((lo, hi), (lo8, hi8))


def test_the_ordering_and_the_draws_a_ratio_needs():
    a = {"lo": 1.0, "hi": 2.0}
    b = {"lo": 10.0, "hi": 20.0}
    assert e293.ordered(b, a) and e293.ordered(a, b), (a, b)
    assert not e293.ordered(a, {"lo": 1.5, "hi": 3.0}), a
    assert e293.draws_for(2.0) == 18, e293.draws_for(2.0)
    assert e293.draws_for(1.5) == 49, e293.draws_for(1.5)
    # a bigger ratio resolves with fewer draws, and a ratio of one never does
    assert e293.draws_for(5.0) < e293.draws_for(2.0)
    assert e293.draws_for(1.0) is None


def _reading(rows=None, pairs=None, pair=None):
    rows = rows or [{"rung": "a", "artifact": "a.json", "draws": 8, "printed": 2.0e-4, "measured": 2.0e-4,
                     "difference": 0.0, "lo": 1.3e-4, "hi": 4.4e-4, "seed_sem": 1e-4, "replicates": 6},
                    {"rung": "b", "artifact": "b.json", "draws": 5, "printed": 4.0e-5, "measured": 4.0e-5,
                     "difference": 0.0, "lo": 2.4e-5, "hi": 1.2e-4, "seed_sem": 1e-4, "replicates": 6}]
    pairs = pairs or [{"a": "a", "b": "b", "ratio": 5.0, "ordered": True},
                      {"a": "a", "b": "c", "ratio": 1.1, "ordered": False},
                      {"a": "b", "b": "c", "ratio": 1.3, "ordered": False}]
    return {"rows": rows, "pairs": pairs, "unresolved": [p for p in pairs if not p["ordered"]],
            "argument_pair": pair or pairs[0], "draws_for_1.5x": 49, "draws_for_2x": 18}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e293.judge(_reading())}
    for cid in ("V1", "V2", "V3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a printed sd the artifact does not give is V1's falsifier
    rows = _reading()["rows"]
    rows[0]["difference"] = 0.05
    j = {r["id"]: r for r in e293.judge(_reading(rows=rows))}
    assert j["V1"]["verdict"].startswith("FALSIFIER FIRED"), j["V1"]
    # a table whose orderings are all resolved is V2's
    pairs = [{"a": "a", "b": f"r{i}", "ratio": 5.0 + i, "ordered": True} for i in range(4)]
    j = {r["id"]: r for r in e293.judge(_reading(pairs=pairs))}
    assert j["V2"]["verdict"].startswith("FALSIFIER FIRED"), j["V2"]
    # an unresolved argument pair is V3's
    pair = {"a": "a", "b": "b", "ratio": 1.1, "ordered": False}
    j = {r["id"]: r for r in e293.judge(_reading(pairs=[pair], pair=pair))}
    assert j["V3"]["verdict"].startswith("FALSIFIER FIRED"), j["V3"]
    assert e293.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e293.judge({"rows": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_table_is_what_the_finding_says():
    r = e293.reading()
    assert len(r["rows"]) == 5, [x["rung"] for x in r["rows"]]
    assert all(abs(x["difference"]) < 0.01 for x in r["rows"]), [x["difference"] for x in r["rows"]]
    assert all(x["draws_recorded"] == x["draws"] for x in r["rows"]), r["rows"]
    assert len(r["pairs"]) == 10 and len(r["unresolved"]) == 6, (len(r["pairs"]), len(r["unresolved"]))
    assert r["argument_pair"]["ordered"] is True, r["argument_pair"]
    assert abs(r["argument_pair"]["ratio"] - 3.17) < 0.01, r["argument_pair"]
    # the middle of the table is what the error bars cannot separate
    assert all(not p["ordered"] for p in r["unresolved"] if p["ratio"] < 3.0), r["unresolved"]
    assert r["draws_for_1.5x"] == 49 and r["draws_for_2x"] == 18, r


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e293_how_many_draws_a_draw_sd_needs.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["rows"]) == 5 and all(abs(x["difference"]) < 0.01 for x in d["rows"]), d["rows"]
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("V1", "V2", "V3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "6 of 10" in claims["V2"]["measured"], claims["V2"]
    assert "49 draws" in claims["V2"]["measured"], claims["V2"]
