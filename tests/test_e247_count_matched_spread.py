"""`e247` removes a sample-size confound from a comparison three earlier modules made, so the tests pin the two
count-matched statistics, the invariant that a bigger sample can only widen a spread, and each claim's two faces.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median

from experiments import e247_count_matched_spread as e247


def fam_of(spec: dict) -> dict:
    """{family: {cell: (excesses, ranks)}} -> the structure `judge` reads."""
    return {f: {cell: {"excess": list(ex), "rank": list(rk), "keys": list(range(len(ex)))}
                for cell, (ex, rk) in cells.items()} for f, cells in spec.items()}


def test_the_two_count_matched_statistics_and_their_edges():
    assert e247.median_pair([1.0, 2.0]) == 2.0
    assert e247.median_pair([1.0, 2.0, 4.0]) == median([2.0, 4.0, 2.0])
    assert e247.median_pair([1.0]) is None and e247.lowest_two([1.0]) is None
    assert e247.lowest_two([3.0, 1.0, 2.0]) == 2.0, "the two SMALLEST values, not the two first"


def test_more_drawings_can_only_widen_the_all_drawings_spread():
    """The confound itself, as an invariant: `all` is a max-over-min over more points, so it dominates the
    count-matched statistics that are computed from a subset of them."""
    spec = {"alloy1": {(300, 30, 0.9): ([1.0, 1.5, 3.0], [1.0, 1.1, 1.2]),
                       (800, 80, 0.9): ([1.0, 2.0], [1.0, 1.4])}}
    table = e247.matched_table(fam_of(spec), "excess")
    for cell, r in table["alloy1"].items():
        assert r["all"] >= r["pair_median"] >= 1.0, (cell, r)
        assert r["all"] >= r["lowest_two"] >= 1.0, (cell, r)
    assert table["alloy1"][(300, 30, 0.9)]["all"] == 3.0
    assert table["alloy1"][(300, 30, 0.9)]["pair_median"] < 3.0, "the big sample is what makes the 3.0"


def test_R1_and_R2_are_MET_when_one_cell_s_big_sample_is_what_made_the_span():
    """Both one-side families move with the cell only because each has one six-drawing cell; at a two-drawing budget
    their spans collapse and the kind-0 family's no longer sits below them."""
    spec = {}
    for one_side in ("alloy1", "inalloy1"):
        spec[one_side] = {(300, 30, 0.9): ([1.0, 1.1, 1.2, 1.3, 1.4, 3.0], [1.0] * 6),
                          (800, 80, 0.9): ([1.0, 1.1, 1.2, 1.3, 1.4, 1.5], [1.0] * 6)}
    spec["swap2"] = {(300, 30, 0.9): ([1.05, 1.06], [1.0, 1.1]), (800, 80, 0.9): ([1.0, 1.02], [1.0, 1.05])}
    spec["erdos_renyi"] = {(300, 30, 0.9): ([1.0, 1.01], [1.0, 1.02]), (800, 80, 0.9): ([1.0, 1.01], [1.0, 1.03])}
    rows = {r["id"]: r for r in e247.judge(fam_of(spec))}
    assert rows["R1"]["verdict"].startswith("MET"), rows["R1"]
    assert "3.04x" not in rows["R1"]["measured"] or rows["R1"]["measured"].count("->") == 2, rows["R1"]
    assert rows["R2"]["verdict"].startswith("MET"), rows["R2"]
    assert rows["R3"]["verdict"].startswith("MET") or rows["R3"]["verdict"].startswith("REFUSED"), rows["R3"]


def test_R4_fires_when_both_cells_take_the_same_direction():
    spec = {"swap0.5": {(300, 30, 0.9): ([1.0, 1.5], [1.0, 1.1]), (800, 80, 0.9): ([1.0, 1.6], [1.0, 1.2])},
            "alloy1": {(300, 30, 0.9): ([1.0, 1.1], [1.0, 1.1]), (800, 80, 0.9): ([1.0, 1.1], [1.0, 1.2])},
            "erdos_renyi": {(300, 30, 0.9): ([1.0, 1.01], [1.0, 1.1]), (800, 80, 0.9): ([1.0, 1.01], [1.0, 1.2])}}
    rows = {r["id"]: r for r in e247.judge(fam_of(spec))}
    assert rows["R4"]["verdict"].startswith("FALSIFIER FIRED"), rows["R4"]
    assert "pooled" in rows["R4"]["measured"], rows["R4"]


def test_R5_fires_when_a_drawing_moves_one_observable_and_not_the_other():
    """The observables anti-ordered: the family whose drawings move its penalty is the one whose drawings leave its
    geometry alone, so the correlation is negative and the shared-noise reading does not hold."""
    spec = {"alloy1": {(300, 30, 0.9): ([1.0, 1.1], [1.0, 4.0]), (800, 80, 0.9): ([1.0, 1.5], [1.0, 1.5])},
            "swap2": {(300, 30, 0.9): ([1.0, 2.0], [1.0, 1.2]), (800, 80, 0.9): ([1.0, 3.0], [1.0, 1.1])}}
    rows = {r["id"]: r for r in e247.judge(fam_of(spec))}
    assert rows["R5"]["verdict"].startswith("null band"), rows["R5"]
    assert "-1.000" in rows["R5"]["measured"], rows["R5"]


def test_per_cell_reads_the_live_artifacts_into_families_by_kind(tmp_path):
    """`per_cell` must key on (family, cell) with the per-drawing values, and must leave `real` out of the kinds."""
    payload = {"config": {"circuit_size": 800, "support": 80, "rho": 0.9, "seeds": 3, "rewire_seed": 0},
               "topologies": {"alloy1": {"diagonal(EWC)": {"analytic": {"excess_mean": 0.05}},
                                         "geometry": {"effective_rank": 9.0}},
                              "real": {"diagonal(EWC)": {"analytic": {"excess_mean": 0.02}},
                                       "geometry": {"effective_rank": 27.0}}}}
    (tmp_path / "a.json").write_text(json.dumps(payload), encoding="utf-8")
    fam = e247.per_cell(tmp_path)
    assert "real" not in fam and "alloy1" in fam
    assert fam["alloy1"][(800, 80, 0.9)]["excess"] == [0.05]


def test_the_live_corpus_halves_the_quoted_spreads_and_shares_the_noise():
    """The finding's numbers on the artifact: alloy1's six-drawing cell at 3.34x is 1.64x at a two-drawing budget,
    the count-matched separation collapses to 1.004x, the cell covariates are flat, and R5's +0.724."""
    p = Path("runs/e247_count_matched_spread.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in d["claims"]}
    for cid in ("R1", "R2", "R3", "R4", "R5"):
        assert rows[cid]["verdict"].startswith("MET"), rows[cid]
    assert "2.36x" in rows["R1"]["measured"] and "1.83x" in rows["R1"]["measured"], rows["R1"]
    assert "1.004x" in rows["R2"]["measured"], rows["R2"]
    assert "overlapping=True" in rows["R2"]["measured"], rows["R2"]
    assert "+0.724" in rows["R5"]["measured"], rows["R5"]
    cell = d["table"]["alloy1"]["(800, 80, 0.9)"]
    assert cell["n"] == 8 and abs(cell["all"] - 3.34) < 0.01 and abs(cell["pair_median"] - 1.64) < 0.01, cell
