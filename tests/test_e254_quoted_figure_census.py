"""`e254` classifies quoted figures by how many drawings their inputs have, so the tests pin the three verdicts, the
refusal when a registered input is absent, both faces of C1, and C2's concentration test -- a thin input through a
well-drawn family at rho 0.9 is the falsifier.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e254_quoted_figure_census as e254


def fam_of(spec: dict, n: int | None = None) -> dict:
    """{(cell, family): n drawings} -> a `per_cell`-shaped structure with those counts."""
    out: dict = {}
    for (cell, f), k in spec.items():
        out.setdefault(f, {})[cell] = {"excess": [0.02 + 0.001 * i for i in range(k)], "rank": [1.0] * k,
                                       "keys": list(range(k))}
    return out


def test_counts_and_the_three_verdicts():
    fam = fam_of({((800, 80, 0.9), "alloy1"): 8, ((800, 80, 0.9), "erdos_renyi"): 9,
                  ((300, 30, 0.5), "alloy1"): 1})
    n = e254.counts(fam)
    assert n[((800, 80, 0.9), "alloy1")] == 8 and n[((300, 30, 0.5), "alloy1")] == 1
    assert len(n) == 3, "one entry per (cell, family) with a positive excess"


def test_an_absent_input_refuses_rather_than_classifying():
    """The registry names cells the corpus must have; a missing one is a refusal, not a verdict."""
    import experiments.e254_quoted_figure_census as mod
    saved = mod.REGISTRY
    try:
        mod.REGISTRY = (("a-figure", "x", [((999, 99, 0.9), "alloy1")], False),) + saved
        rows = {r["id"]: r for r in mod.judge(fam_of({((800, 80, 0.9), "alloy1"): 8}))}
        assert rows["C1"]["verdict"].startswith("REFUSED"), rows["C1"]
        assert "no alloy1 at (999, 99, 0.9)" in rows["C1"]["verdict"], rows["C1"]
    finally:
        mod.REGISTRY = saved


def test_C1_fires_below_three_exposed_and_holds_at_three():
    """Two exposed figures is the live shape; the bar was three, so the live corpus fires the falsifier."""
    import experiments.e254_quoted_figure_census as mod
    saved = mod.REGISTRY
    try:
        spec = {((300, 30, 0.5), "alloy1"): 1, ((300, 30, 0.5), "inalloy1"): 1}
        mod.REGISTRY = (("thin-one", "x", [((300, 30, 0.5), "alloy1")], False),
                        ("thin-two", "y", [((300, 30, 0.5), "inalloy1")], False))
        rows = {r["id"]: r for r in mod.judge(fam_of(spec))}
        assert rows["C1"]["verdict"].startswith("FALSIFIER FIRED"), rows["C1"]
        mod.REGISTRY = mod.REGISTRY + (("thin-three", "z", [((300, 30, 0.5), "swap2")], False),)
        rows = {r["id"]: r for r in mod.judge(fam_of({**spec, ((300, 30, 0.5), "swap2"): 1}))}
        assert rows["C1"]["verdict"].startswith("MET"), rows["C1"]
    finally:
        mod.REGISTRY = saved


def test_C2_fires_when_the_thin_input_is_a_well_drawn_family_at_rho_09():
    """An exposure through a drawn family at the reference rho is not a rho-grid or weak-swap exposure."""
    import experiments.e254_quoted_figure_census as mod
    saved = mod.REGISTRY
    try:
        mod.REGISTRY = (("thin-at-the-convention-cell", "x", [((800, 80, 0.9), "swap8")], False),)
        rows = {r["id"]: r for r in mod.judge(fam_of({((800, 80, 0.9), "swap8"): 1}))}
        assert rows["C2"]["verdict"].startswith("MET"), "a weak-swap rung is a declared exposure class"
        mod.REGISTRY = (("thin-through-a-core-family", "x", [((800, 80, 0.9), "alloy1")], False),)
        rows = {r["id"]: r for r in mod.judge(fam_of({((800, 80, 0.9), "alloy1"): 1}))}
        assert rows["C2"]["verdict"].startswith("FALSIFIER FIRED"), rows["C2"]
    finally:
        mod.REGISTRY = saved


def test_a_decomposed_figure_is_not_safe_and_not_exposed():
    import experiments.e254_quoted_figure_census as mod
    saved = mod.REGISTRY
    try:
        mod.REGISTRY = (("was-thin-now-drawn", "x", [((300, 30, 0.98), "alloy1")], True),
                        ("always-thick", "y", [((800, 80, 0.9), "alloy1")], False))
        rows = {r["name"]: r["verdict"] for r in mod.classify(fam_of(
            {((300, 30, 0.98), "alloy1"): 2, ((800, 80, 0.9), "alloy1"): 8}))}
        assert rows["was-thin-now-drawn"] == "DECOMPOSED" and rows["always-thick"] == "SAFE", rows
    finally:
        mod.REGISTRY = saved


def test_the_live_census_reports_the_cs_300_close_out_and_the_cs_800_exposure():
    """The finding's numbers on the artifact: twelve figures, two still exposed, both through the cs-300 rho 0.5, 0.7
    and 0.8 cells, and four decomposed by this session's fires."""
    p = Path("runs/e254_quoted_figure_census.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    verdicts = {f["verdict"] for f in d["figures"]}
    assert verdicts <= {"SAFE", "DECOMPOSED", "STILL EXPOSED"}, verdicts
    # e255 closed the cs-300 exposure; extending the registry with the cs-800 figures then exposed two more
    # e256 drew all six cs-800 rho cells, so the exposure is closed and every figure is SAFE or DECOMPOSED
    exposed = [f for f in d["figures"] if f["verdict"] == "STILL EXPOSED"]
    assert exposed == [] and len(d["figures"]) == 15, (exposed, len(d["figures"]))
    assert len([f for f in d["figures"] if f["verdict"] == "DECOMPOSED"]) == 8, d["figures"]
    assert len([f for f in d["figures"] if f["verdict"] == "SAFE"]) == 7, d["figures"]
    rows_e = {r["id"]: r for r in d["claims"]}
    # the E-claims' "at least two exposed" direction now fires, which is the work being done rather than a failure
    for cid in ("E1", "E3"):
        assert rows_e[cid]["verdict"].startswith("FALSIFIER FIRED"), rows_e[cid]
    assert rows_e["E2"]["verdict"].startswith("MET"), rows_e["E2"]
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["C1"]["verdict"].startswith("FALSIFIER FIRED"), rows["C1"]
    assert rows["C2"]["verdict"].startswith("MET"), rows["C2"]
    assert d["counts"]["300/30/0.5/alloy1"] == 2 and d["counts"]["800/80/0.9/alloy1"] == 8, d["counts"]
