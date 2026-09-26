"""`e249` judges a prediction about a cell that did not exist when the prediction was written, so the tests pin the
margin's arithmetic, the refusal when the base is short, each verdict of T1 and of the consistent-footing T1b, and the
three-cell table both claims are read against.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e249_third_cell_margin as e249


def cells(spec: dict) -> dict:
    """{cell: (kind0 spread, kind1 spread)} -> a `per_cell` structure with the six families at two drawings each."""
    out: dict = {}
    for cell, (s0, s1) in spec.items():
        out.setdefault("swap0.5", {})[cell] = {"excess": [1.0, s0], "rank": [1.0, 1.2], "keys": [4, 5]}
        out.setdefault("swap2", {})[cell] = {"excess": [1.0, s0], "rank": [1.0, 1.1], "keys": [4, 5]}
        out.setdefault("signshuffle", {})[cell] = {"excess": [1.0, s0], "rank": [1.0, 1.1], "keys": [4, 5]}
        out.setdefault("alloy1", {})[cell] = {"excess": [1.0, s1], "rank": [1.0, 6.28], "keys": [0, 1]}
        out.setdefault("inalloy1", {})[cell] = {"excess": [1.0, s1], "rank": [1.0, 2.21], "keys": [0, 1]}
        out.setdefault("erdos_renyi", {})[cell] = {"excess": [1.0, 1.02], "rank": [1.0, 1.01], "keys": [0, 1]}
    return out


def three_cells(new_kind0: float, new_kind1: float) -> dict:
    """The two reference cells at their measured equal-count-two margins (0.851 and 1.660) plus a new cell."""
    spec = {(300, 30, 0.9): (1.176, 1.0), (800, 80, 0.9): (1.0, 1.660), (800, 20, 0.9): (new_kind0, new_kind1)}
    out: dict = {}
    for cell, (s0, s1) in spec.items():
        for f in ("swap0.5", "swap2", "signshuffle"):
            out.setdefault(f, {})[cell] = {"excess": [1.0, s0], "rank": [1.0, 1.1], "keys": [4, 5]}
        live = cell == e249.CELL
        out.setdefault("alloy1", {})[cell] = {"excess": [1.0, s1], "rank": [1.0, 6.28 if live else 14.08],
                                              "keys": [0, 1]}
        out.setdefault("inalloy1", {})[cell] = {"excess": [1.0, s1], "rank": [1.0, 2.21 if live else 8.02],
                                                "keys": [0, 1]}
        out.setdefault("erdos_renyi", {})[cell] = {"excess": [1.0, 1.02], "rank": [1.0, 1.01], "keys": [0, 1]}
    return out


def test_the_margin_is_one_median_over_the_other_and_the_base_refuses_when_short():
    b = e249.base(cells({(800, 20, 0.9): (2.0, 1.0)}))
    assert len(b) == 6 and e249.margin(b) == 0.5
    rows = {r["id"]: r for r in e249.judge({"alloy1": {(800, 20, 0.9): {"excess": [1.0], "rank": [], "keys": [0]}}},
                                           {"alloy1": {}})}
    for cid in ("T1", "T1b", "T2"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert e249.spread([1.0]) is None and e249.spread([1.0, 3.0]) == 3.0


def test_T1_and_T1b_are_MET_when_the_margin_interpolates():
    fam = three_cells(1.2, 1.7)          # margin = 1.7 / 1.2 = 1.417
    b = e249.base(fam)
    rows = {r["id"]: r for r in e249.judge(b, fam)}
    assert rows["T1"]["verdict"].startswith("MET"), rows["T1"]
    assert "margin 1.417" in rows["T1"]["measured"], rows["T1"]
    assert rows["T1b"]["verdict"].startswith("MET"), rows["T1b"]
    assert rows["T2"]["verdict"].startswith("MET"), rows["T2"]
    assert "6.28" in rows["T1"]["measured"], rows["T1"]


def test_T1_fires_low_when_the_margin_is_a_tie_and_T1b_fires_when_it_is_outside_the_references():
    fam = three_cells(2.0, 1.5)          # margin = 0.75: a tie, and below the 0.851 reference
    b = e249.base(fam)
    rows = {r["id"]: r for r in e249.judge(b, fam)}
    assert rows["T1"]["verdict"].startswith("FALSIFIER FIRED"), rows["T1"]
    assert "not ordered by the rank contrast" in rows["T1"]["verdict"], rows["T1"]
    assert rows["T1b"]["verdict"].startswith("FALSIFIER FIRED"), rows["T1b"]
    assert "not monotone" in rows["T1b"]["verdict"], rows["T1b"]


def test_T1_fires_high_and_lands_in_its_null_band_at_the_two_bounds():
    hi = e249.base(three_cells(1.0, 3.0))                     # 3.0, above the 2.50 falsifier
    assert e249.judge(hi, three_cells(1.0, 3.0))[0]["verdict"].startswith("FALSIFIER FIRED")
    null = e249.base(three_cells(2.0, 2.25))                  # 1.125, inside the 1.10-2.00 bar -> MET
    assert e249.judge(null, three_cells(2.0, 2.25))[0]["verdict"].startswith("MET")
    band = e249.base(three_cells(2.0, 2.10))                  # 1.05, exactly the low falsifier
    assert e249.judge(band, three_cells(2.0, 2.10))[0]["verdict"].startswith("FALSIFIER FIRED")


def test_T2_fires_when_a_one_side_family_is_as_tight_as_the_two_side_one():
    fam = three_cells(1.2, 1.7)
    fam["alloy1"][(800, 20, 0.9)]["excess"] = [1.0, 1.0]
    rows = {r["id"]: r for r in e249.judge(e249.base(fam), fam)}
    assert rows["T2"]["verdict"].startswith("FALSIFIER FIRED"), rows["T2"]


def test_the_three_cell_table_reads_every_cell_on_the_same_two_drawing_footing():
    fam = three_cells(1.2, 1.7)
    table = e249.matched_two_margins(fam)
    by_cell = {c: m for c, m, _ in table}
    assert [c for c, _, _ in table] == list(e249.CELLS)
    assert abs(by_cell[(300, 30, 0.9)] - 1.0 / 1.176) < 1e-9, by_cell
    assert abs(by_cell[(800, 80, 0.9)] - 1.660) < 1e-9, by_cell
    assert abs(by_cell[(800, 20, 0.9)] - 1.4166666) < 1e-6, by_cell
    assert all(set(r) == set(e249.KIND1) for _, _, r in table)


def test_the_live_artifact_reads_the_third_cell():
    """The finding's numbers on the artifact: the six families at two drawings with the runs' own seeds 4 and 5 for
    kind 0, the margin, and the verdicts of T1/T1b/T2."""
    p = Path("runs/e249_third_cell_margin.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["cell"] == [800, 20, 0.9] and d["count"] == 2, (d["cell"], d["count"])
    assert len(d["families"]) == 6, sorted(d["families"])
    for f in ("swap0.5", "swap2", "signshuffle"):
        assert d["families"][f]["keys"] == [4, 5], (f, d["families"][f]["keys"])
    for f in ("alloy1", "inalloy1", "erdos_renyi"):
        assert d["families"][f]["keys"][:2] == [0, 1], (f, d["families"][f]["keys"])
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["T2"]["verdict"].startswith("MET"), rows["T2"]
    refs = {tuple(c): m for c, m, _ in d["matched_two"]}
    assert abs(refs[(300, 30, 0.9)] - 0.851) < 0.01, refs
    assert abs(refs[(800, 80, 0.9)] - 1.660) < 0.01, refs
