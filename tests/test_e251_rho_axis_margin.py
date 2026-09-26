"""`e251` reads the (1, 0) margin along the one axis that holds size and support fixed, and on two footings at once --
each family's two FIRST drawings and its two NEWEST. The fixtures therefore give every family four drawings, so the two
footings are different pairs and each claim can fire on its own.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e251_rho_axis_margin as e251

KEYS = [0, 1, 3, 4]


def build(new_first=(1.10, 1.32), new_newest=(1.10, 1.32), new_rank=5.0, ref_rank=2.0) -> dict:
    """Six families, four drawings each, at both cells. The first pair and the newest pair are independent."""
    out: dict = {}
    for cell, (k0f, k1f), (k0n, k1n), rk in ((e251.CELL, new_first, new_newest, new_rank),
                                            (e251.REF, (1.175, 1.0), (1.0, 1.0), ref_rank)):
        for f in e251.KIND0:
            out.setdefault(f, {})[cell] = {"excess": [1.0, k0f, 1.0, k0n], "rank": [1.0, rk, 1.0, 1.0], "keys": KEYS}
        for f in e251.KIND1:
            out.setdefault(f, {})[cell] = {"excess": [1.0, k1f, 1.0, k1n], "rank": [1.0, rk, 1.0, 1.0], "keys": KEYS}
        out.setdefault("erdos_renyi", {})[cell] = {"excess": [1.0, 1.02, 1.0, 1.02], "rank": [1.0, 1.01, 1.0, 1.01],
                                                  "keys": KEYS}
    return out


def test_the_margin_is_one_median_over_the_other_and_a_short_base_refuses():
    fam = build(new_first=(1.10, 1.32))                     # margin 1.20
    assert len(e251.base(fam)) == 6 and abs(e251.margin(e251.base(fam)) - 1.32 / 1.10) < 1e-9
    rows = {r["id"]: r for r in e251.judge({f: {} for f in e251.FAMILIES})}
    for cid in ("V1", "V1b", "V2", "V3"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert "not equal-count" in rows["V1"]["verdict"]


def test_V1_and_V1b_are_MET_when_the_margin_and_the_driver_both_rise():
    fam = build(new_first=(1.10, 1.32), new_newest=(1.10, 1.43))
    rows = {r["id"]: r for r in e251.judge(fam)}
    assert rows["V1"]["verdict"].startswith("MET"), rows["V1"]
    assert "margin 1.200 against rho 0.9's 0.851" in rows["V1"]["measured"], rows["V1"]
    assert rows["V1b"]["verdict"].startswith("MET"), rows["V1b"]
    assert "margin 1.300 over the seeds [3, 4]" in rows["V1b"]["measured"], rows["V1b"]
    assert rows["V2"]["verdict"].startswith("MET"), rows["V2"]
    assert rows["V3"]["verdict"].startswith("MET"), rows["V3"]


def test_V1_fires_when_the_margin_does_not_rise_with_rho():
    rows = {r["id"]: r for r in e251.judge(build(new_first=(1.20, 1.00)))}   # margin 0.833, at/below 0.851
    assert rows["V1"]["verdict"].startswith("FALSIFIER FIRED"), rows["V1"]
    assert "does not rise with rho" in rows["V1"]["verdict"], rows["V1"]


def test_V1_lands_in_its_null_band_for_a_rise_inside_the_noise():
    rows = {r["id"]: r for r in e251.judge(build(new_first=(1.20, 1.03)))}   # margin 0.858, above 0.851, below 0.90
    assert rows["V1"]["verdict"].startswith("null band"), rows["V1"]


def test_V1b_fires_when_only_the_newest_pair_reads_at_or_below_the_reference():
    fam = build(new_first=(1.10, 1.32), new_newest=(2.00, 1.50))            # V1 MET, the newest pair 0.750
    rows = {r["id"]: r for r in e251.judge(fam)}
    assert rows["V1"]["verdict"].startswith("MET"), rows["V1"]
    assert rows["V1b"]["verdict"].startswith("FALSIFIER FIRED"), rows["V1b"]


def test_V2_fires_when_the_driver_falls_while_the_margin_rises():
    rows = {r["id"]: r for r in e251.judge(build(new_rank=1.5, ref_rank=2.0))}
    assert rows["V1"]["verdict"].startswith("MET"), rows["V1"]
    assert rows["V2"]["verdict"].startswith("FALSIFIER FIRED"), rows["V2"]
    assert "against 2.00x" in rows["V2"]["measured"], rows["V2"]


def test_the_newest_base_takes_the_last_drawings_of_every_family():
    fam = build()
    newest = e251.base(fam, newest=True)
    assert all(v["keys"] == [3, 4] for v in newest.values()), newest
    assert all(e251.base(fam)[f]["keys"] == [0, 1] for f in e251.FAMILIES)
    assert abs(e251.margin(e251.base(fam, e251.REF, 2, True)) - 1.0) < 1e-9, "the reference's newest pair is a tie"
    assert abs(e251.margin(e251.base(fam, e251.REF, 2)) - 0.851) < 1e-3, "and its first pair is the live 0.851"


def test_the_live_artifact_reads_the_rho_axis():
    """The finding's numbers on the artifact: six families at two drawings at both rho values, the same two seeds
    everywhere at rho 0.99, the reference margin, and the claims."""
    p = Path("runs/e251_rho_axis_margin.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["cell"] == [300, 30, 0.99] and d["reference"] == [300, 30, 0.9] and d["count"] == 2
    assert len(d["families"]) == 6 and len(d["equally_drawn"]) == 6, (sorted(d["families"]), sorted(d["equally_drawn"]))
    for f, v in d["equally_drawn"].items():
        assert v["keys"] == [3, 4], (f, v["keys"])
    assert abs(d["reference_margin"] - 0.851) < 0.01, d["reference_margin"]
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["V3"]["verdict"].startswith("MET"), rows["V3"]
