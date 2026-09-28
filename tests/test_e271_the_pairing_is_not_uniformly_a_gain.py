"""`e271` censuses the corpus's own paired correlations, so the tests pin the scan, the configuration grouping, both
faces of the three claims and the live numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e271_the_pairing_is_not_uniformly_a_gain as e271


def _art(path: Path, corr, n=40, unpaired=0.02, paired=0.017, lam=0.003, metric="final_accuracy"):
    payload = {"config": {"lam": lam, "json_out": path.name},
               "methods": {"ewc-block": {"replicates": [{"final_accuracy": 0.5}] * n}},
               "matched_pair": {metric: {"n": n, "corr": corr, "sem_unpaired": unpaired, "sem_paired": paired}}}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_the_census_reads_only_artifacts_that_carry_the_block(tmp_path):
    _art(tmp_path / "a.json", 0.4)
    _art(tmp_path / "neg.json", -0.3, n=5)
    (tmp_path / "no_block.json").write_text(json.dumps({"config": {}, "methods": {}}), encoding="utf-8")
    (tmp_path / "broken.json").write_text("{oops", encoding="utf-8")
    rows = e271.census(tmp_path)
    assert sorted(r["artifact"] for r in rows) == ["a.json", "neg.json"], rows
    a = next(r for r in rows if r["artifact"] == "a.json")
    assert abs(a["ratio"] - 0.02 / 0.017) < 1e-9, a
    assert a["corr"] == 0.4 and a["n"] == 40


def test_the_configuration_grouping_collapses_a_configuration_written_twice(tmp_path):
    _art(tmp_path / "one.json", -0.2, n=5)
    _art(tmp_path / "two.json", -0.2, n=5)          # same config, a second file
    _art(tmp_path / "other.json", -0.3, n=5, lam=1.0)
    rows = e271.census(tmp_path)
    groups = e271.configurations(rows)
    assert len(groups) == 2, groups
    assert sorted(len(v) for v in groups.values()) == [1, 2], groups


def _rows(corrs, n=40, ratios=None):
    out = []
    for i, c in enumerate(corrs):
        r = ratios[i] if ratios else 1.18
        out.append({"artifact": f"a{i}.json", "metric": "final_accuracy", "n": n, "corr": c,
                    "sem_unpaired": r, "sem_paired": 1.0, "ratio": r, "key": (("lam", str(i)),)})
    return out


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e271.judge(_rows([0.4, -0.1, -0.2, -0.3, -0.15, -0.05]))}
    assert j["W1"]["verdict"].startswith("MET"), j["W1"]
    assert "5 rows negative" in j["W1"]["measured"] or "5 rows negative" in j["W1"]["measured"], j["W1"]
    assert j["W2"]["verdict"].startswith("MET") and j["W3"]["verdict"].startswith("FALSIFIER FIRED"), j
    # fewer than five negatives is W1's falsifier
    j = {r["id"]: r for r in e271.judge(_rows([0.4, -0.1, -0.2, 0.3, 0.15, 0.2]))}
    assert j["W1"]["verdict"].startswith("FALSIFIER FIRED"), j["W1"]
    # a median outside the band is W2's, and a powered ratio below 1 is W3's
    j = {r["id"]: r for r in e271.judge(_rows([0.4] * 6, ratios=[1.0] * 6))}
    assert j["W2"]["verdict"].startswith("FALSIFIER FIRED"), j["W2"]
    j = {r["id"]: r for r in e271.judge(_rows([0.4] * 6, ratios=[1.2, 1.2, 0.97, 1.2, 1.2, 1.2]))}
    assert j["W3"]["verdict"].startswith("MET") and "0.970" in j["W3"]["measured"], j["W3"]
    # at no powered budget at all, W2 and W3 have nothing to read
    j = {r["id"]: r for r in e271.judge(_rows([0.4] * 6, n=5))}
    assert j["W2"]["verdict"].startswith("REFUSED") and j["W3"]["verdict"].startswith("REFUSED"), j
    assert e271.judge([])[0]["verdict"].startswith("REFUSED")


def test_the_live_census_bounds_the_pairing_s_gain_and_finds_it_negative_sometimes():
    """The finding's numbers on the artifact: 64 rows over 32 artifacts, a median correlation near +0.30, nine
    negative rows over six configurations, and a powered median gain of 1.18x with two rows below 1."""
    p = Path("runs/e271_the_pairing_is_not_uniformly_a_gain.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = d["rows"]
    assert len(rows) >= 64 and len({r["artifact"] for r in rows}) >= 32, len(rows)
    corrs = sorted(r["corr"] for r in rows)
    assert 0.2 <= corrs[len(corrs) // 2] <= 0.4, corrs[len(corrs) // 2]
    neg = [r for r in rows if r["corr"] <= 0]
    assert len(neg) >= 9 and len(e271.configurations(neg)) <= len(neg), (len(neg), len(e271.configurations(neg)))
    powered = sorted(r["ratio"] for r in rows if r["n"] and r["n"] >= e271.POWERED and r["ratio"])
    assert len(powered) >= 24 and 1.1 <= powered[len(powered) // 2] <= 1.3, powered[len(powered) // 2]
    assert powered[0] < 1.0, "at least one powered row is below 1"
    claims = {r["id"]: r for r in d["claims"]}
    for cid in ("W1", "W2", "W3"):
        assert claims[cid]["verdict"].startswith("MET"), claims[cid]
