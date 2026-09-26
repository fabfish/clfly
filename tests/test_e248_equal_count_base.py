"""`e248` reads a base that was designed to have equal counts, so the tests pin the three claims' two faces, the
refusal that fires when the base is not equal-count, and the leave-one-out stability that S3 asserts.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e248_equal_count_base as e248


def b_of(spec: dict) -> dict:
    """{family: [values]} -> the base structure `judge` reads."""
    return {f: {"excess": list(v), "rank": [1.0] * len(v), "keys": list(range(len(v)))} for f, v in spec.items()}


def wide_kind0() -> dict:
    return b_of({"swap0.5": [1.0, 1.1, 1.5], "swap2": [1.0, 1.05, 1.2], "signshuffle": [1.0, 1.1, 1.3],
                 "alloy1": [1.0, 1.2, 2.0], "inalloy1": [1.0, 1.1, 1.8], "erdos_renyi": [1.0, 1.02, 1.03]})


def test_the_base_is_refused_when_a_family_is_short_or_absent():
    """The whole point of the cell is that every count is three, so a base that is not equal-count is a refusal."""
    rows = {r["id"]: r for r in e248.judge(b_of({"swap0.5": [1.0, 1.1], "alloy1": [1.0, 1.2, 2.0]}))}
    for cid in ("S1", "S2", "S3"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert "not equal-count" in rows["S1"]["verdict"]
    assert e248.spread([1.0]) is None and e248.spread([2.0, 1.0]) == 2.0


def test_S1_S2_and_S3_are_MET_when_the_pooled_ordering_holds_at_equal_count():
    rows = {r["id"]: r for r in e248.judge(wide_kind0())}
    assert rows["S1"]["verdict"].startswith("MET"), rows["S1"]
    assert "kind 0 1.300x against kind 1 1.900x" in rows["S1"]["measured"], rows["S1"]
    assert rows["S2"]["verdict"].startswith("MET"), rows["S2"]
    assert rows["S3"]["verdict"].startswith("MET"), rows["S3"]
    assert "+46.2%" in rows["S1"]["measured"], rows["S1"]


def test_S1_fires_its_falsifier_when_kind_0_is_the_looser_at_equal_count():
    spec = b_of({"swap0.5": [1.0, 1.5, 3.0], "swap2": [1.0, 1.4, 2.5], "signshuffle": [1.0, 1.3, 2.0],
                 "alloy1": [1.0, 1.1, 1.2], "inalloy1": [1.0, 1.05, 1.1], "erdos_renyi": [1.0, 1.02, 1.03]})
    rows = {r["id"]: r for r in e248.judge(spec)}
    assert rows["S1"]["verdict"].startswith("FALSIFIER FIRED"), rows["S1"]
    assert rows["S2"]["verdict"].startswith("MET"), rows["S2"]


def test_S1_lands_in_its_null_band_when_the_two_kinds_are_within_ten_percent():
    spec = b_of({"swap0.5": [1.0, 1.1, 1.5], "swap2": [1.0, 1.05, 1.5], "signshuffle": [1.0, 1.1, 1.55],
                 "alloy1": [1.0, 1.2, 1.6], "inalloy1": [1.0, 1.15, 1.58], "erdos_renyi": [1.0, 1.02, 1.03]})
    rows = {r["id"]: r for r in e248.judge(spec)}
    assert rows["S1"]["verdict"].startswith("null band"), rows["S1"]


def test_S3_fires_when_one_drawing_is_what_makes_the_two_side_family_wide():
    """Drop the drawing that widens erdos_renyi and a one-side family is tighter, so 'the tightest family' would be
    one drawing's property rather than the family's."""
    spec = b_of({"swap0.5": [1.0, 1.1, 1.5], "swap2": [1.0, 1.05, 1.1], "signshuffle": [1.0, 1.1, 1.3],
                 "alloy1": [1.0, 1.2, 2.0], "inalloy1": [1.0, 1.1, 1.8], "erdos_renyi": [1.0, 1.5, 1.6]})
    rows = {r["id"]: r for r in e248.judge(spec)}
    assert rows["S3"]["verdict"].startswith("FALSIFIER FIRED"), rows["S3"]
    assert "drop" in rows["S3"]["measured"], rows["S3"]


def test_leave_one_out_gives_one_column_per_dropped_drawing():
    cols = e248.leave_one_out(wide_kind0())
    assert len(cols) == e248.COUNT == 3
    assert abs(cols[0]["alloy1"] - 2.0 / 1.2) < 1e-12, cols[0]["alloy1"]      # drops 1.0
    assert abs(cols[1]["alloy1"] - 2.0) < 1e-12, cols[1]["alloy1"]            # drops 1.2
    assert abs(cols[2]["alloy1"] - 1.2) < 1e-12, cols[2]["alloy1"]            # drops 2.0


def test_the_live_artifact_reads_the_equal_count_base():
    """The finding's numbers on the artifact: six families at three drawings, the kind medians, and the claim
    verdicts, with the run's own third drawing (key 5) in each kind-0 family."""
    p = Path("runs/e248_equal_count_base.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["count"] == 3 and len(d["families"]) == 6, (d["count"], sorted(d["families"]))
    for f, fam in d["families"].items():
        assert len(fam["excess"]) == 3 and len(fam["rank"]) == 3, (f, fam)
    for f in ("swap0.5", "swap2", "signshuffle"):
        assert 5 in d["families"][f]["keys"], (f, d["families"][f]["keys"])
    for f in ("alloy1", "inalloy1", "erdos_renyi"):
        assert 5 not in d["families"][f]["keys"], (f, d["families"][f]["keys"])
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["S2"]["verdict"].startswith("MET"), rows["S2"]
    assert len(d["leave_one_out"]) == 3
