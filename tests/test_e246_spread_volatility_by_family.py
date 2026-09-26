"""`e246` decomposes one number (the pooled level-against-spread correlation) into two, so the tests pin the pieces:
the span per family, the Spearman helper with its ties, and both faces of N3 -- the claim it makes and the falsifier
it fires when the between-family ordering is weak.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e246_spread_volatility_by_family as e246


def row(family: str, kind: int, cell: tuple, level: float, spread: float, rank: float = 2.0) -> dict:
    return {"family": family, "kind": kind, "cell": cell, "excess_mean": level, "excess_spread": spread,
            "rank_spread": rank, "drawings": 2}


def test_a_family_s_span_is_over_the_cells_it_was_measured_in_and_none_for_one_cell():
    gs = [row("alloy1", 1, (300, 30, 0.9), 0.10, 1.0), row("alloy1", 1, (800, 80, 0.9), 0.05, 3.0),
          row("swap0.5", 0, (800, 80, 0.9), 0.02, 1.4)]
    fam = e246.by_family(gs)
    assert sorted(fam) == ["alloy1", "swap0.5"]
    assert fam["alloy1"][0]["cell"] == (300, 30, 0.9), "rows are sorted by cell, not by insertion"
    assert e246.span(fam["alloy1"], "excess_spread") == 3.0
    assert e246.span(fam["swap0.5"], "excess_spread") is None, "one cell is not a range"
    assert e246.span(fam["alloy1"], "excess_spread") and e246.by_family(gs)["alloy1"][0]["family"] == "alloy1"


def test_spearman_is_the_rank_correlation_and_ties_share_a_rank():
    assert abs(e246.spearman([1.0, 2.0, 3.0], [3.0, 2.0, 1.0]) + 1.0) < 1e-12
    assert abs(e246.spearman([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) - 1.0) < 1e-12
    assert e246.spearman([1.0, 2.0, 3.0], [5.0, 5.0, 5.0]) is None, "a constant column has no rank variance"
    assert e246.spearman([1.0, 2.0], [1.0, 2.0]) is None, "fewer than three points is not a correlation"
    # a tie in the middle of one column still orders the others
    assert e246.spearman([1.0, 2.0, 2.0, 4.0], [1.0, 2.0, 3.0, 4.0]) > 0.9


def _ordered_corpus() -> list[dict]:
    """The shape N3 claims: a low-level kind-0 family that moves, and two higher-level families that do not."""
    gs = [row("swap2", 0, (300 + i, 30, 0.9), 0.010 + 0.001 * i, spread) for i, spread in
          enumerate((2.0, 1.5, 2.0, 1.5, 2.0))]
    gs += [row("alloy1", 1, (c, 40, 0.9), lv, sp, rank=8.0) for c, lv, sp in ((300, 0.05, 1.0), (800, 0.06, 2.0))]
    gs += [row("erdos_renyi", 2, (c, 80, 0.9), lv, 1.0, rank=1.1) for c, lv in ((300, 0.15), (800, 0.16))]
    return gs


def test_N1_and_N3_are_MET_when_the_one_side_family_moves_and_the_level_orders_between_families():
    gs = _ordered_corpus()
    rows = {r["id"]: r for r in e246.judge(gs)}
    assert rows["N1"]["verdict"].startswith("MET"), rows["N1"]
    assert rows["N3"]["verdict"].startswith("MET"), rows["N3"]
    assert "50%" in rows["N3"]["measured"], rows["N3"]
    assert e246.between(e246.by_family(gs))[1] < -0.9, "the fixture is built to order"


def test_N3_fires_its_falsifier_when_the_between_family_ordering_is_weak():
    """The live shape: the family that moves most sits at a MIDDLE level, so ordering the family means does not
    reproduce the ordering the pooled groups suggest. The spreads here are set to rank 3, 1, 4, 2 in level order,
    which is a rank correlation of 0.0."""
    gs = [row("swap2", 0, cell, 0.012 + 0.001 * i, sp) for i, (cell, sp) in enumerate(
        (((300, 30, 0.9), 1.8), ((400, 40, 0.9), 2.4), ((400, 80, 0.9), 1.9), ((800, 20, 0.9), 1.9)))]
    gs += [row("alloy0.9", 1, (c, 30, 0.9), lv, 1.0, rank=6.0) for c, lv in ((300, 0.037), (800, 0.038))]
    gs += [row("alloy1", 1, (c, 40, 0.9), 0.05 + 0.01 * i, 2.0 + i, rank=8.0)
           for i, c in enumerate((300, 400, 800))]
    gs += [row("erdos_renyi", 2, (c, 80, 0.9), lv, 1.5, rank=1.1) for c, lv in ((300, 0.15), (800, 0.16))]
    rows = {r["id"]: r for r in e246.judge(gs)}
    assert rows["N3"]["verdict"].startswith("FALSIFIER FIRED"), rows["N3"]
    assert "between-family Spearman" in rows["N3"]["measured"], rows["N3"]
    assert abs(e246.between(e246.by_family(gs))[1]) < e246.BETWEEN_FLOOR, "the fixture is built to have no ordering"


def test_N1_fires_when_a_no_destruction_family_moves_as_much_as_a_one_side_one():
    gs = [row("swap2", 0, (300, 30, 0.9), 0.01, 1.0), row("swap2", 0, (800, 80, 0.9), 0.02, 4.0)]
    gs += [row("alloy1", 1, (300, 30, 0.9), 0.05, 1.0), row("alloy1", 1, (800, 80, 0.9), 0.06, 1.5, rank=8.0)]
    gs += [row("erdos_renyi", 2, (300, 30, 0.9), 0.15, 1.0, rank=1.1), row("erdos_renyi", 2, (800, 80, 0.9), 0.16, 1.1)]
    rows = {r["id"]: r for r in e246.judge(gs)}
    assert rows["N1"]["verdict"].startswith("FALSIFIER FIRED"), rows["N1"]
    assert "1.10x-4.00x" in rows["N1"]["measured"], rows["N1"]
    assert "MET" in rows["N2"]["verdict"] or "FALSIFIER" in rows["N2"]["verdict"], rows["N2"]


def test_the_live_corpus_puts_the_volatility_in_the_one_side_families():
    """The finding's numbers on the artifact: kind 1's spans 8.56x and 29.17x once `e251`'s near-critical cell is in the census, against 1.40x to 6.11x elsewhere
    `e248`'s third kind-0 drawing is in the census, the rank observable wider still (7.34x, 9.27x), and N3's falsifier
    fired on a between-family Spearman of -0.200, with six families now at four or more cells and 30 adjacent pairs."""
    p = Path("runs/e246_spread_volatility_by_family.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["N1"]["verdict"].startswith("MET"), rows["N1"]
    assert rows["N2"]["verdict"].startswith("MET"), rows["N2"]
    assert "8.56" in rows["N1"]["measured"] and "29.17" in rows["N1"]["measured"], rows["N1"]
    assert "1.40" in rows["N1"]["measured"] and "6.11" in rows["N1"]["measured"], rows["N1"]
    assert rows["N3"]["verdict"].startswith("FALSIFIER FIRED"), rows["N3"]
    assert "-0.200" in rows["N3"]["measured"] and "58%" in rows["N3"]["measured"], rows["N3"]
    between = {b[0]: b for b in d["between"]}
    assert abs(between["erdos_renyi"][1] - 0.13338) < 1e-4, between["erdos_renyi"]
    assert len(between["erdos_renyi"]) == 4 and between["erdos_renyi"][3] == 9, between["erdos_renyi"]
    within = {w[0]: w for w in d["within"]}
    assert set(within) == {"alloy1", "inalloy1", "erdos_renyi", "swap0.5", "swap2", "signshuffle"}, set(within)
    assert within["alloy1"][1] == 9 and within["alloy1"][2] == 6, within["alloy1"]
