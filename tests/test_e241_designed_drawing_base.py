"""`e241`'s four new drawings arrive through `e240`'s census — which is the point of that module — so the tests pin
both halves: that the census picks up new `rewire_seed` values automatically, and that a four-drawing cell's pairwise
median is computed over the full cross-product.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median

from experiments import e240_cross_family_drawings as e240


def test_the_census_sees_four_drawings_after_e241_and_the_medians_are_the_findings(tmp_path):
    """A cell with four `rewire_seed` values per family must yield sixteen pairwise ratios, and the support-160 cell's
    median must be the 0.83x the finding quotes -- i.e. the enlarged base, not the two-drawing value."""
    data = {}
    for field, vals in (("alloy1", (28.35, 2.42, 2.23, 2.00)), ("inalloy1", (2.46, 2.67, 8.99, 6.50))):
        for rw, v in enumerate(vals):
            data[(800, 160, 0.9, field, rw)] = {"rank": v, "excess": None, "artifact": f"{field}_{rw}.json"}
    b = e240.blocks(data)[0]
    r = e240.ratios(b["families"], "alloy1", "rank", "inalloy1", "rank")
    assert len(r) == 16
    assert abs(median(r) - 0.83) < 0.02, median(r)


def test_the_live_census_reports_four_drawings_for_the_two_supports():
    """The live artifact's blocks: both e241 supports must show four drawings per family, or the run did not land."""
    p = Path("runs/e240_cross_family_drawings.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    cells = {tuple(b["cell"]): b for b in d["blocks"]}
    for support in (20, 160):
        fams = cells[(800, support, 0.9)]["families"]
        assert len(fams["alloy1"]) == 4 and len(fams["inalloy1"]) == 4, (support, {t: len(f) for t, f in fams.items()})
        r = e240.ratios(fams, "alloy1", "rank", "inalloy1", "rank")
        assert len(r) == 16 and median(r) < 1.0, (support, median(r))
    # and with the enlarged base every cell's rank median is inside the band (e240's C1 turned MET)
    verdicts = {c["id"]: c["verdict"] for c in d["claims"]}
    assert verdicts["C1"].startswith("MET"), verdicts["C1"]


def test_the_two_side_family_is_the_tightest_one_across_four_drawings():
    """`erdos_renyi`'s spread over the four drawings must be far smaller than the one-side families' -- the level
    statement that survives where the contrasts do not."""
    p = Path("runs/e240_cross_family_drawings.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    cells = {tuple(b["cell"]): b for b in d["blocks"]}
    for support in (20, 160):
        fams = cells[(800, support, 0.9)]["families"]
        spreads = {}
        for t in ("alloy1", "inalloy1", "erdos_renyi"):
            v = [x["rank"] for x in fams[t].values() if x.get("rank")]
            spreads[t] = max(v) / min(v)
        assert spreads["erdos_renyi"] < min(spreads["alloy1"], spreads["inalloy1"]), (support, spreads)
        assert spreads["erdos_renyi"] < 1.5, spreads
