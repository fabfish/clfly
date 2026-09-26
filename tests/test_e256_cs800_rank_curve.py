"""`e256` tests the profile of the drawing noise in `rho` at the other size, so the tests pin the rank factor, the
refusal before the six second drawings land, every verdict of F1 (the 20% stability bar and the 1.5x edge), of F2 (the
same 1.5x bar and the 10% "stays put" edge) and of F3 (the fall), and the census re-run.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e256_cs800_rank_curve as e256

CORPUS = {0.5: 63.14, 0.7: 45.83, 0.8: 32.78, 0.95: 22.09, 0.98: 21.24, 0.99: 21.01}


def fam_of(new: dict, corpus: dict | None = None) -> dict:
    """{rho: new alloy1 rank} -> six cells at cs 800/support 80 with the corpus's own rank beside it."""
    corpus = corpus or CORPUS
    out: dict = {}
    for rho in e256.LOW + e256.HIGH:
        cell = (800, 80, rho)
        keys = [0, 1]
        for f, scale in (("alloy1", 1.0), ("inalloy1", 1.03), ("erdos_renyi", 1.06)):
            out.setdefault(f, {})[cell] = {"rank": [corpus[rho] * scale, new[rho] * scale],
                                           "excess": [0.05 * scale, 0.051 * scale], "keys": keys}
    return out


def steady(factor: float) -> dict:
    """Every cell's new drawing at the same factor from the corpus's own."""
    return {rho: CORPUS[rho] * factor for rho in CORPUS}


def test_the_series_and_the_factor_readers():
    fam = fam_of(steady(1.0))
    assert e256.series(fam, (800, 80, 0.5), "alloy1", "rank") == [CORPUS[0.5], CORPUS[0.5]]
    assert e256.series(fam, (800, 80, 0.5), "swap2", "rank") == []
    assert abs(e256.factor(2.0, 4.0) - 2.0) < 1e-12 and abs(e256.factor(4.0, 2.0) - 2.0) < 1e-12


def test_a_missing_second_drawing_refuses():
    fam = fam_of(steady(1.0))
    del fam["alloy1"][(800, 80, 0.99)]
    rows = {r["id"]: r for r in e256.judge(fam)}
    for cid in ("F1", "F2", "F3"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert "no second drawing" in rows["F1"]["verdict"]


def test_F1_is_MET_when_the_low_rho_end_stays_within_twenty_percent():
    rows = {r["id"]: r for r in e256.judge(fam_of(steady(1.10)))}
    assert rows["F1"]["verdict"].startswith("MET"), rows["F1"]
    assert "rho 0.5: 63.14 against 69.45 (1.10)" in rows["F1"]["measured"], rows["F1"]


def test_F1_fires_when_a_low_rho_cell_moves_by_1_5x():
    new = steady(1.05)
    new[0.7] = CORPUS[0.7] * 1.6
    rows = {r["id"]: r for r in e256.judge(fam_of(new))}
    assert rows["F1"]["verdict"].startswith("FALSIFIER FIRED"), rows["F1"]
    assert "cs 300's" in rows["F1"]["verdict"], rows["F1"]


def test_F1_lands_in_its_null_band_between_the_bar_and_the_edge():
    new = steady(1.05)
    new[0.8] = CORPUS[0.8] * 1.3
    rows = {r["id"]: r for r in e256.judge(fam_of(new))}
    assert rows["F1"]["verdict"].startswith("null band"), rows["F1"]


def test_F2_fires_when_the_high_rho_rank_stays_put_and_holds_when_it_moves():
    put = {r["id"]: r for r in e256.judge(fam_of(steady(1.03)))}
    assert put["F2"]["verdict"].startswith("FALSIFIER FIRED"), put["F2"]
    assert "excess side's alone" in put["F2"]["verdict"], put["F2"]
    new = steady(1.03)
    new[0.98] = CORPUS[0.98] * 2.0
    moves = {r["id"]: r for r in e256.judge(fam_of(new))}
    assert moves["F2"]["verdict"].startswith("MET"), moves["F2"]


def test_F3_fires_on_a_reversal():
    keep = {r["id"]: r for r in e256.judge(fam_of(steady(1.05)))}
    assert keep["F3"]["verdict"].startswith("MET"), keep["F3"]
    new = steady(1.05)
    new[0.8] = CORPUS[0.5] * 2.0
    flip = {r["id"]: r for r in e256.judge(fam_of(new))}
    assert flip["F3"]["verdict"].startswith("FALSIFIER FIRED"), flip["F3"]


def test_the_live_artifact_reads_the_cs_800_second_drawing():
    """The finding's numbers on the artifact: both drawings at all six cells, the factors, and the census re-run."""
    p = Path("runs/e256_cs800_rank_curve.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert [c[2] for c in d["cells"]] == [0.5, 0.7, 0.8, 0.95, 0.98, 0.99], d["cells"]
    for rho in ("0.5", "0.7", "0.8", "0.95", "0.98", "0.99"):
        assert len(d["series"][f"{rho}/alloy1/rank"]) >= 2, (rho, d["series"][f"{rho}/alloy1/rank"])
    rows = {r["id"]: r for r in d["claims"]}
    for cid in ("F1", "F2", "F3"):
        assert rows[cid]["verdict"].startswith(("MET", "FALSIFIER", "null")), rows[cid]
    after = {r["name"]: r["verdict"] for r in d["census_after"]}
    assert all(v in ("SAFE", "DECOMPOSED", "STILL EXPOSED") or v.startswith("REFUSED") for v in after.values()), after
