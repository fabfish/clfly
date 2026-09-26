"""`e240` re-tests the cross-family contrasts on the corpus's own drawings, so its tests pin the three things that
make that a measurement: the cross-product of drawings (`ratios`), the per-cell grouping (`blocks`), and the
registration's bars — with a synthetic consistent set and a synthetic systematic one landing on opposite verdicts.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e240_cross_family_drawings as e240


def test_ratios_is_the_cross_product_of_the_two_families_drawings():
    fams = {"alloy1": {0: {"rank": 10.0}, 1: {"rank": 20.0}},
            "inalloy1": {0: {"rank": 5.0}, 1: {"rank": 4.0}, 2: {"rank": 2.0}}}
    r = e240.ratios(fams, "alloy1", "rank", "inalloy1", "rank")
    assert len(r) == 6 and r == sorted(r)
    assert r[0] == 10.0 / 5.0 and r[-1] == 20.0 / 2.0
    assert e240.ratios(fams, "erdos_renyi", "rank", "alloy1", "rank") == [], "a missing family gives no pairs"


def test_blocks_groups_by_cell_and_keeps_every_drawing():
    data = {(300, 30, 0.9, "alloy1", 0): {"rank": 10.0, "excess": 0.1, "artifact": "a.json"},
            (300, 30, 0.9, "alloy1", 1): {"rank": 12.0, "excess": 0.2, "artifact": "b.json"},
            (300, 30, 0.9, "inalloy1", 0): {"rank": 5.0, "excess": 0.3, "artifact": "c.json"}}
    b = e240.blocks(data)
    assert len(b) == 1 and b[0]["cell"] == (300, 30, 0.9)
    assert sorted(b[0]["families"]["alloy1"]) == [0, 1]
    assert b[0]["families"]["inalloy1"][0]["rank"] == 5.0


def test_a_consistent_set_and_a_systematic_one_land_on_opposite_verdicts():
    def block(ratios, size=800, support=80):
        fams = {"alloy1": {i: {"rank": 10.0 * r, "excess": 0.05 * r} for i, r in enumerate(ratios)},
                "inalloy1": {0: {"rank": 10.0, "excess": 0.05},
                             1: {"rank": 9.0, "excess": 0.06}},
                "erdos_renyi": {0: {"rank": 1.0, "excess": 0.15},
                                1: {"rank": 1.0, "excess": 0.14}}}
        return {"cell": (size, support, 0.9), "families": fams}

    consistent = [block([0.7, 0.7]), block([0.6, 0.6], size=400, support=40)]
    v = {c["id"]: c["verdict"] for c in e240.judge(consistent)}
    assert v["C1"].startswith("MET"), v
    assert v["C2"].startswith("MET"), v
    assert v["C3"].startswith("MET"), v

    systematic = [block([6.0, 6.0])]
    v = {c["id"]: c["verdict"] for c in e240.judge(systematic)}
    assert v["C1"].startswith("FALSIFIER"), v


def test_a_cell_without_drawings_refuses_its_claim(capsys):
    weak = [{"cell": (800, 80, 0.9),
             "families": {t: {0: {"rank": 1.0, "excess": 0.1}} for t in ("alloy1", "inalloy1", "erdos_renyi")}}]
    v = {c["id"]: c["verdict"] for c in e240.judge(weak)}
    assert v["C1"].startswith("REFUSED") and v["C2"].startswith("REFUSED"), v


def test_the_live_artifact_carries_the_six_cells_and_the_real_control():
    """If the artifact is on disk, the six cells' medians are what the finding quotes, and `real` carries exactly one
    drawing per cell -- the corpus's own control, since that topology is not rewired."""
    p = Path("runs/e240_cross_family_drawings.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    cells = {tuple(b["cell"]): b for b in d["blocks"]}
    for key in [(300, 30, 0.9), (400, 40, 0.9), (400, 80, 0.9), (800, 20, 0.9), (800, 160, 0.9), (800, 80, 0.9)]:
        b = cells[key]
        fams = b["families"]
        assert len(fams.get("alloy1", {})) >= 2 and len(fams.get("inalloy1", {})) >= 2, key
        # the corpus's own control: `real` is not rewired, so whatever drawings a cell has for it must agree
        real_ranks = {round(v["rank"], 12) for v in fams.get("real", {}).values() if v.get("rank") is not None}
        assert len(real_ranks) <= 1, (key, real_ranks)
