"""`e253` decomposes the register's two one-drawing points, so the tests pin the top step's arithmetic, the refusal
before the second drawing lands, every verdict of W1 (the factor of 1.5, both edges) and of W2 (the trend's sign), and
the level report.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e253_two_drawings_at_high_rho as e253


def fam_of(spec: dict) -> dict:
    """{rho: (alloy1 values, erdos_renyi values)} -> six families at both cells, keys 0..n-1."""
    out: dict = {}
    for rho, (al, er) in spec.items():
        cell = (300, 30, rho)
        keys = list(range(len(al)))
        out.setdefault("alloy1", {})[cell] = {"excess": list(al), "rank": [1.0] * len(al), "keys": keys}
        out.setdefault("erdos_renyi", {})[cell] = {"excess": list(er), "rank": [1.0] * len(er), "keys": keys}
        out.setdefault("inalloy1", {})[cell] = {"excess": [x * 1.1 for x in al], "rank": [1.0] * len(al), "keys": keys}
        for f in ("swap0.5", "swap2", "signshuffle"):
            out.setdefault(f, {})[cell] = {"excess": [0.02], "rank": [1.0], "keys": [0]}
    return out


def both(al_95, er_95, al_98, er_98) -> dict:
    return fam_of({0.95: (al_95, er_95), 0.98: (al_98, er_98)})


def test_the_top_step_is_one_drawing_over_another_and_the_share_is_symmetric():
    fam = both([0.07, 0.07], [0.13, 0.2], [0.02, 0.02], [0.11, 0.11])
    assert abs(e253.top_step(fam, (300, 30, 0.98), 0) - 0.11 / 0.02) < 1e-9
    assert abs(e253.top_step(fam, (300, 30, 0.95), 1) - 0.2 / 0.07) < 1e-9
    assert e253.top_step(fam, (300, 30, 0.98), 7) is None, "an absent drawing is not a top step"
    assert abs(e253.share(2.0, 4.0) - 2.0) < 1e-12 and abs(e253.share(4.0, 2.0) - 2.0) < 1e-12
    assert e253.drawing_keys(fam, (300, 30, 0.98)) == [0, 1]


def test_either_cell_missing_its_second_drawing_refuses():
    rows = {r["id"]: r for r in e253.judge(both([0.07], [0.13], [0.02, 0.02], [0.11, 0.11]))}
    for cid in ("W1", "W2"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert "no second drawing" in rows["W1"]["verdict"]


def test_W1_is_MET_when_the_new_drawing_moves_the_quoted_figure_by_1_5x():
    rows = {r["id"]: r for r in e253.judge(both([0.07, 0.07], [0.13, 0.14], [0.02, 0.02], [0.11, 0.20]))}
    assert rows["W1"]["verdict"].startswith("MET"), rows["W1"]
    assert "5.50x against the new drawing 10.00x" in rows["W1"]["measured"], rows["W1"]
    assert "a factor of 1.82" in rows["W1"]["measured"], rows["W1"]


def test_W1_fires_when_the_new_drawing_agrees_within_ten_percent():
    rows = {r["id"]: r for r in e253.judge(both([0.07, 0.07], [0.13, 0.14], [0.02, 0.02], [0.11, 0.112]))}
    assert rows["W1"]["verdict"].startswith("FALSIFIER FIRED"), rows["W1"]
    assert "typical" in rows["W1"]["verdict"], rows["W1"]


def test_W1_lands_in_its_null_band_between_the_two_edges():
    rows = {r["id"]: r for r in e253.judge(both([0.07, 0.07], [0.13, 0.14], [0.02, 0.02], [0.11, 0.132]))}
    assert rows["W1"]["verdict"].startswith("null band"), rows["W1"]


def test_W2_fires_when_the_new_drawings_reverse_the_rho_order():
    keep = {r["id"]: r for r in e253.judge(both([0.07, 0.07], [0.13, 0.14], [0.02, 0.02], [0.11, 0.20]))}
    assert keep["W2"]["verdict"].startswith("MET"), keep["W2"]
    flip = {r["id"]: r for r in e253.judge(both([0.07, 0.02], [0.13, 0.20], [0.02, 0.05], [0.11, 0.11]))}
    assert flip["W2"]["verdict"].startswith("FALSIFIER FIRED"), flip["W2"]
    assert "reverses the order" in flip["W2"]["verdict"], flip["W2"]


def test_the_levels_are_means_over_the_drawings_a_family_has():
    fam = both([0.07, 0.03], [0.13, 0.14], [0.02, 0.02], [0.11, 0.11])
    lv = e253.levels(fam, (300, 30, 0.95))
    assert abs(lv["alloy1"] - 0.05) < 1e-12, lv
    assert abs(lv["erdos_renyi"] - 0.135) < 1e-12, lv
    assert lv["swap0.5"] == 0.02 and set(lv) == set(e253.FAMILIES)


def test_the_live_artifact_decomposes_both_quoted_points():
    """The finding's numbers on the artifact: the corpus's own drawing and the new one at each rho, the two top steps
    and their factors, and the claims."""
    p = Path("runs/e253_two_drawings_at_high_rho.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["cells"] == [[300, 30, 0.95], [300, 30, 0.98]], d["cells"]
    for rho in ("0.95", "0.98"):
        steps = d["top_steps"][rho]
        assert set(steps) == {"0", "1"}, (rho, steps)
        assert abs(steps["0"] - e253.QUOTED[float(rho)]) < 0.02, (rho, steps)
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["W1"]["verdict"].startswith(("MET", "FALSIFIER", "null")), rows["W1"]
    assert rows["W2"]["verdict"].startswith(("MET", "FALSIFIER")), rows["W2"]
