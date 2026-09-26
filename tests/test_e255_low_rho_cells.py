"""`e255` closes the census's work list by adding a drawing to the three thin low-rho cells, so the tests pin the rank
factor's arithmetic, the refusal before the drawings land, every verdict of R1 (the 1.5 bar and the 10% stability
edge) and of R2 (the monotone fall), and the census re-run.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e255_low_rho_cells as e255


def fam_of(spec: dict, ref_ranks=(7.2, 11.19, 4.1)) -> dict:
    """{rho: (alloy1 ranks, alloy1 excesses)} -> the three low-rho cells plus the rho-0.9 reference."""
    out: dict = {}
    cells = {rho: (ranks, ex) for rho, (ranks, ex) in spec.items()}
    cells[0.9] = (list(ref_ranks), [0.12247] * len(ref_ranks))
    for rho, (ranks, excesses) in cells.items():
        cell = (300, 30, rho)
        keys = list(range(len(ranks)))
        for f, s in (("alloy1", 1.0), ("inalloy1", 1.05), ("erdos_renyi", 1.1)):
            out.setdefault(f, {})[cell] = {"rank": [r * s for r in ranks], "excess": [e * s for e in excesses],
                                           "keys": keys}
    return out


def low(r1=(26.52, 12.0), r7=(22.96, 21.0), r8=(17.54, 18.0)) -> dict:
    """Ranks only, with an excess list so the spreads are computable."""
    return fam_of({0.5: (list(r1), [0.02940, 0.02500]), 0.7: (list(r7), [0.08417, 0.08000]),
                   0.8: (list(r8), [0.11987, 0.11500])})


def test_the_series_and_the_factor_readers():
    fam = low()
    assert e255.series(fam, (300, 30, 0.5), "alloy1", "rank") == [26.52, 12.0]
    assert e255.series(fam, (300, 30, 0.5), "swap2", "rank") == []
    assert abs(e255.factor(2.0, 4.0) - 2.0) < 1e-12 and abs(e255.factor(4.0, 2.0) - 2.0) < 1e-12
    assert e255.series(fam, (300, 30, 0.9), "alloy1", "rank") == [7.2, 11.19, 4.1]


def test_a_missing_second_drawing_refuses():
    fam = fam_of({0.5: ([26.52], [0.0294]), 0.7: ([22.96, 21.0], [0.084, 0.08]),
                  0.8: ([17.54, 18.0], [0.12, 0.115])})
    rows = {r["id"]: r for r in e255.judge(fam)}
    for cid in ("R1", "R2"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert "no second drawing" in rows["R1"]["verdict"]


def test_R1_is_MET_when_one_cell_moves_by_1_5x():
    rows = {r["id"]: r for r in e255.judge(low(r1=(26.52, 12.0)))}     # a factor of 2.21 at rho 0.5
    assert rows["R1"]["verdict"].startswith("MET"), rows["R1"]
    assert "rho 0.5: 26.52 against 12.00 (a factor of 2.21)" in rows["R1"]["measured"], rows["R1"]


def test_R1_fires_when_all_three_agree_within_ten_percent():
    rows = {r["id"]: r for r in e255.judge(low(r1=(26.52, 25.0), r7=(22.96, 22.0), r8=(17.54, 17.0)))}
    assert rows["R1"]["verdict"].startswith("FALSIFIER FIRED"), rows["R1"]
    assert "stable" in rows["R1"]["verdict"], rows["R1"]


def test_R1_lands_in_its_null_band_between_the_bar_and_the_stability_edge():
    rows = {r["id"]: r for r in e255.judge(low(r1=(26.52, 22.0), r7=(22.96, 21.0), r8=(17.54, 16.0)))}
    assert rows["R1"]["verdict"].startswith("null band"), rows["R1"]


def test_R2_holds_when_the_new_ranks_still_fall_and_fires_on_a_reversal():
    keep = {r["id"]: r for r in e255.judge(low(r1=(26.52, 20.0), r7=(22.96, 21.0), r8=(17.54, 18.0)))}
    assert keep["R2"]["verdict"].startswith("MET"), keep["R2"]
    flip = {r["id"]: r for r in e255.judge(low(r1=(26.52, 10.0), r7=(22.96, 21.0), r8=(17.54, 20.0)))}
    assert flip["R2"]["verdict"].startswith("FALSIFIER FIRED"), flip["R2"]
    assert "reverse" in flip["R2"]["verdict"], flip["R2"]


def test_the_live_artifact_closes_or_keeps_the_census_s_work_list():
    """The finding's numbers on the artifact: both drawings at the three cells, the factors, and the census re-run."""
    p = Path("runs/e255_low_rho_cells.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert [c[2] for c in d["cells"]] == [0.5, 0.7, 0.8], d["cells"]
    for rho in ("0.5", "0.7", "0.8"):
        ranks = d["series"][f"{rho}/alloy1/rank"]
        assert len(ranks) >= 2, (rho, ranks)
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["R1"]["verdict"].startswith(("MET", "FALSIFIER", "null")), rows["R1"]
    assert rows["R2"]["verdict"].startswith(("MET", "FALSIFIER")), rows["R2"]
    after = {r["name"]: r["verdict"] for r in d["census_after"]}
    assert all(v in ("SAFE", "DECOMPOSED", "STILL EXPOSED", "REFUSED") or v.startswith("REFUSED")
               for v in after.values()), after
