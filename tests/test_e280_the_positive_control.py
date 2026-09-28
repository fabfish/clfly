"""`e280` is the audit series' positive control, so the tests pin the reading, both faces of the three claims and the
live confirmation to the last quoted digit.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e280_the_positive_control as e280


def _art(rows=132, pairs=66, checkpoints=(0, 2), lo=0.0108, hi=0.1252, mid=None, break_summary=False):
    # the live distribution is left-skewed, so the fixture ramps through its median rather than linearly
    mid = 0.0361 if mid is None else mid
    half = rows // 2
    vals = ([lo + (mid - lo) * i / (half - 1) for i in range(half)]
            + [mid + (hi - mid) * i / (rows - half - 1) for i in range(rows - half)])
    fit_tasks = []
    for i, v in enumerate(vals):
        fit_tasks.append({"seed_a": i % pairs, "seed_b": 100 + i % pairs, "checkpoint": checkpoints[i % len(checkpoints)],
                          "task": i % 3, "barrier": v, "barrier_over_chance": v})
    summary = {"n": rows, "min": min(vals), "median": statistics.median(vals), "max": max(vals)}
    if break_summary:
        summary["median"] = summary["median"] + 0.01
    return {"fit_tasks": fit_tasks, "distributions": {"fit": summary}}


def test_the_reading_recomputes_the_three_numbers_from_the_rows():
    r = e280.reading(_art())
    assert r["n"] == 132 and r["pairs"] == 66 and r["checkpoints"] == [0, 2], r
    assert abs(r["min"] - 0.0108) < 1e-9 and abs(r["max"] - 0.1252) < 1e-9, r
    assert r["n_below_bar"] == 132, r["n_below_bar"]
    assert r["summary"]["n"] == 132


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e280.judge(e280.reading(_art()))}
    for cid in ("C1", "C2", "C3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    # a population of the wrong shape is C1's falsifier
    j = {r["id"]: r for r in e280.judge(e280.reading(_art(rows=120, pairs=66)))}
    assert j["C1"]["verdict"].startswith("FALSIFIER FIRED"), j["C1"]
    # numbers that are not the sentence's are C2's
    d = _art(lo=0.05, hi=0.9, mid=0.5)
    j = {r["id"]: r for r in e280.judge(e280.reading(d))}
    assert j["C2"]["verdict"].startswith("FALSIFIER FIRED"), j["C2"]
    # a row above the bar, or a summary that disagrees with its rows, is C3's
    j = {r["id"]: r for r in e280.judge(e280.reading(_art(lo=0.0108, hi=0.30)))}
    assert j["C3"]["verdict"].startswith("FALSIFIER FIRED"), j["C3"]
    j = {r["id"]: r for r in e280.judge(e280.reading(_art(break_summary=True)))}
    assert j["C3"]["verdict"].startswith("FALSIFIER FIRED"), j["C3"]
    assert e280.judge(None)[0]["verdict"].startswith("REFUSED")


def test_the_live_claim_is_confirmed_to_the_last_quoted_digit():
    """The finding's numbers on the artifact: 132 rows over 66 pairs and two checkpoints, the three quoted numbers
    recomputed, and every row below the bar with the artifact agreeing with itself."""
    p = Path("runs/e280_the_positive_control.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    r = d["reading"]
    assert r["n"] == 132 and r["pairs"] == 66 and r["checkpoints"] == [0, 2], r
    for k, v in d["quoted"].items():
        assert abs(round(r[k], 4) - v) <= 5e-5, (k, r[k], v)
    assert r["n_below_bar"] == r["n"], r
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("C1", "C2", "C3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
