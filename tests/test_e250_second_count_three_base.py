"""`e250` compares two bases that are on the same footing, so the tests pin the margin's arithmetic on each, every
verdict of U1 (MET, falsifier, null band) and of U2, the refusal when either base is short, and the level report.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e250_second_count_three_base as e250


def fam_of(spec: dict) -> dict:
    """{cell: (kind-0 spread, kind-1 spread)} -> both bases at three drawings each, in `per_cell`'s structure."""
    out: dict = {}
    for cell, (s0, s1) in spec.items():
        for f in e250.KIND0:
            out.setdefault(f, {})[cell] = {"excess": [1.0, 1.0, s0], "rank": [1.0, 1.0, 1.1], "keys": [0, 1, 2]}
        for f in e250.KIND1:
            out.setdefault(f, {})[cell] = {"excess": [1.0, 1.0, s1], "rank": [1.0, 1.0, 1.2], "keys": [0, 1, 2]}
        out.setdefault("erdos_renyi", {})[cell] = {"excess": [1.0, 1.0, 1.02], "rank": [1.0, 1.0, 1.01],
                                                   "keys": [0, 1, 2]}
    return out


def two_bases(new_s0: float, new_s1: float) -> dict:
    """The reference cell at the live value (1.008) plus the new cell."""
    return fam_of({e250.REF: (1.0, 1.008), e250.CELL: (new_s0, new_s1)})


def test_the_margins_are_medians_over_medians_and_either_base_being_short_refuses():
    fam = two_bases(2.0, 1.0)
    assert abs(e250.margin(e250.base(fam, e250.REF, 3)) - 1.008) < 1e-9
    assert abs(e250.margin(e250.base(fam, e250.CELL, 3)) - 0.5) < 1e-9
    short = fam_of({e250.CELL: (2.0, 1.0)})
    rows = {r["id"]: r for r in e250.judge(short)}
    for cid in ("U1", "U2"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert "reference" in rows["U1"]["verdict"], rows["U1"]


def test_U1_is_MET_when_the_flatter_geometry_gives_the_smaller_margin():
    fam = two_bases(2.0, 1.05)                      # margin 0.525, below 1.008 and below 1
    rows = {r["id"]: r for r in e250.judge(fam)}
    assert rows["U1"]["verdict"].startswith("MET"), rows["U1"]
    assert "margin 0.525 against the reference's 1.008" in rows["U1"]["measured"], rows["U1"]
    assert rows["U2"]["verdict"].startswith("MET"), rows["U2"]


def test_U1_lands_in_its_null_band_between_the_reference_and_the_falsifier():
    rows = {r["id"]: r for r in e250.judge(two_bases(1.0, 1.05))}
    assert rows["U1"]["verdict"].startswith("null band"), rows["U1"]


def test_U1_fires_when_the_flattest_geometry_reverses_the_pair():
    rows = {r["id"]: r for r in e250.judge(two_bases(1.0, 1.20))}
    assert rows["U1"]["verdict"].startswith("FALSIFIER FIRED"), rows["U1"]
    assert "flattest geometry reverses" in rows["U1"]["verdict"], rows["U1"]


def test_U2_fires_when_a_one_side_family_is_as_tight_as_the_two_side_one():
    fam = two_bases(2.0, 1.05)
    fam["inalloy1"][e250.CELL]["excess"] = [1.0, 1.0, 1.0]
    rows = {r["id"]: r for r in e250.judge(fam)}
    assert rows["U2"]["verdict"].startswith("FALSIFIER FIRED"), rows["U2"]


def test_the_levels_are_means_over_the_three_drawings_of_each_family():
    fam = two_bases(2.0, 1.05)
    lv = e250.levels(fam, e250.CELL)
    assert abs(lv["swap0.5"] - (1.0 + 1.0 + 2.0) / 3) < 1e-12, lv
    assert abs(lv["alloy1"] - (1.0 + 1.0 + 1.05) / 3) < 1e-12, lv
    assert set(lv) == set(e250.FAMILIES), sorted(lv)


def test_the_live_artifact_reads_the_second_count_three_base():
    """The finding's numbers on the artifact: six families at three drawings at both cells, the runs' own seeds 3, 4
    and 5 for kind 0, and the two margins."""
    p = Path("runs/e250_second_count_three_base.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["cell"] == [400, 40, 0.9] and d["reference"] == [300, 30, 0.9] and d["count"] == 3
    assert len(d["families"]) == 6, sorted(d["families"])
    for f in e250.KIND0:
        assert d["families"][f]["keys"] == [3, 4, 5], (f, d["families"][f]["keys"])
    for f in e250.KIND1:
        assert d["families"][f]["keys"] == [0, 1, 2], (f, d["families"][f]["keys"])
    assert abs(d["reference_margin"] - 1.008) < 0.01, d["reference_margin"]
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["U2"]["verdict"].startswith("MET"), rows["U2"]
    assert len(d["leave_one_out"]) == 3
    assert set(d["levels"]) == set(e250.FAMILIES), sorted(d["levels"])
