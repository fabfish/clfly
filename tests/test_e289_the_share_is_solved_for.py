"""`e289` reproduces the paper's own one-parameter decomposition of the sample swaps and reads where it breaks, so the
tests pin the arithmetic (including the algebraic identity that makes the capture redundant), both faces of the three
claims, and the live numbers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e289_the_share_is_solved_for as e289


def test_the_decomposition_and_its_two_identities():
    # a pair that fell exactly as a pure binomial component would: everything removable, share one
    k = 10.0
    pure = e289.decomposition(1.0, 1 / math.sqrt(k), k)
    assert abs(pure["share_solved"] - 1.0) < 1e-9, pure
    assert pure["ceiling"] is None, pure          # a share of one has no ceiling
    # a pair that did not move at all: nothing removable, share zero
    flat = e289.decomposition(1.0, 1.0, k)
    assert abs(flat["share_solved"]) < 1e-12 and abs(flat["ceiling"] - 1.0) < 1e-12, flat
    # a pair that moved FURTHER than a pure binomial component: the share leaves its range
    over = e289.decomposition(1.0, 0.30, k)
    assert over["share_solved"] > 1 and over["ceiling"] is None, over
    # and the boundary is the pure-binomial ratio itself
    assert e289.decomposition(1.0, 1 / math.sqrt(k), k)["share_solved"] <= 1.0
    # the capture is not a measurement: it is a function of the solved share and the ratio alone
    for q in (0.1, 0.4, 0.8):
        ratio = math.sqrt(1 - (1 - 1 / k) * q)
        d = e289.decomposition(1.0, ratio, k)
        assert abs(d["captured"] - math.sqrt(1 - q) / math.sqrt(1 - (1 - 1 / k) * q)) < 1e-9, (q, d)


def test_the_reading_covers_the_corpus_swaps():
    rows = e289.comparisons()
    assert len(rows) == 14, len(rows)
    assert {r["config"] for r in rows} == {"read-out 128", "read-out 300", "read-out 32"}, {r["config"] for r in rows}
    assert sum(1 for r in rows if r["quoted"]) == 2, [r["config"] for r in rows if r["quoted"]]
    for r in rows:
        assert r["n_old"] == 144 and r["n_new"] > r["n_old"] and r["replicates"] == 40, r
        assert r["sd_ratio"] < 1, r


def _reading(shares=(0.5, 0.8), nominal=(0.6, 1.2), quoted=None, fall=1.47, ceiling=1.57, captured=0.94):
    rows = []
    for i, (q, f) in enumerate(zip(shares, nominal)):
        rows.append({"config": "read-out 128" if i == 0 else "read-out 32", "arm": "naive", "metric": "mean_forgetting",
                     "k": 10.0, "n_old": 144, "n_new": 1440, "sd_old": 0.02, "sd_new": 0.02 * (1 - q) ** 0.5,
                     "replicates": 40, "share_solved": q, "share_nominal": f,
                     "sd_ratio": (1 - q) ** 0.5, "fall": 1 / (1 - q) ** 0.5,
                     "ceiling": 1 / (1 - q) ** 0.5 if q < 1 else None, "captured": 0.9,
                     "quoted": i == 0 and quoted is not None})
    if quoted is not None:
        rows[0]["fall"], rows[0]["ceiling"], rows[0]["captured"] = quoted
    return {"comparisons": rows}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e289.judge(_reading(quoted=(1.47, 1.57, 0.94)))}
    assert j["Z1"]["verdict"].startswith("MET"), j["Z1"]
    assert j["Z3"]["verdict"].startswith("MET"), j["Z3"]      # one of two nominal shares is above one
    # a quoted pair outside the tolerance is Z1's falsifier
    j = {r["id"]: r for r in e289.judge(_reading(quoted=(1.60, 1.57, 0.94)))}
    assert j["Z1"]["verdict"].startswith("FALSIFIER FIRED"), j["Z1"]
    # every share inside the model's range is Z2's
    j = {r["id"]: r for r in e289.judge(_reading(shares=(0.5, 0.9)))}
    assert j["Z2"]["verdict"].startswith("FALSIFIER FIRED"), j["Z2"]
    j = {r["id"]: r for r in e289.judge(_reading(shares=(0.5, 1.05)))}
    assert j["Z2"]["verdict"].startswith("MET"), j["Z2"]
    # a minority of nominal shares above one is Z3's
    j = {r["id"]: r for r in e289.judge(_reading(nominal=(0.6, 0.9)))}
    assert j["Z3"]["verdict"].startswith("FALSIFIER FIRED"), j["Z3"]
    assert e289.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e289.judge({"comparisons": []})[0]["verdict"].startswith("REFUSED")


def test_the_live_numbers_are_what_the_finding_says():
    rows = e289.comparisons()
    quoted = {r["config"]: r for r in rows if r["quoted"]}
    for config, (fall, ceiling, captured) in e289.QUOTED.items():
        r = quoted[config]
        assert abs(r["fall"] - fall) <= 0.01, (config, r["fall"], fall)
        assert abs(r["ceiling"] - ceiling) <= 0.01, (config, r["ceiling"], ceiling)
        assert abs(r["captured"] - captured) <= 0.01, (config, r["captured"], captured)
    above = [r for r in rows if r["share_solved"] > 1]
    assert len(above) == 2, [(r["config"], r["arm"], r["metric"], round(r["share_solved"], 3)) for r in rows]
    assert {(r["arm"], r["metric"]) for r in above} == {("replay", "final_accuracy"),
                                                        ("ewc-block-rand", "mean_forgetting")}, above
    assert all(r["config"] == "read-out 32" for r in above), above
    nominal = [r for r in rows if r["share_nominal"] > 1]
    assert len(nominal) == 8, len(nominal)


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e289_the_share_is_solved_for.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["comparisons"]) == 14, len(d["comparisons"])
    claims = {x["id"]: x for x in d["claims"]}
    for cid in ("Z1", "Z2", "Z3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
    assert "worst difference" in claims["Z1"]["measured"], claims["Z1"]
    assert "above one in 2" in claims["Z2"]["measured"], claims["Z2"]
    assert "8 of 14" in claims["Z3"]["measured"], claims["Z3"]
