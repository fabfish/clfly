from __future__ import annotations

import json
from pathlib import Path

from experiments import e207_penalty_driver_join as e207


def art(path: Path, topologies: dict, circuit_size: int = 800) -> Path:
    """One artifact as the join reads it: a `topologies` dict carrying a geometry block and the penalty arm."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"config": {"circuit_size": circuit_size}, "topologies": topologies}),
                    encoding="utf-8")
    return path


def cell(alignment: float, penalty: float, chance: float = 0.0555) -> dict:
    return {"geometry": {"all_pairs_alignment": alignment, "chance_alignment": chance},
            "diagonal(EWC)": {"analytic": {"excess_mean": penalty}}}


def test_only_cells_with_both_a_geometry_block_and_a_penalty_are_joined(tmp_path):
    """The join's admission: a topology with geometry and no analytic penalty, or the other way round, is not a cell --
    and `e2_topology.json` in the real corpus is exactly that, its penalty being realized-only."""
    art(tmp_path / "e900.json", {
        "real": cell(0.005, 0.019),
        "swap2": cell(0.06, 0.012),
        "no_penalty": {"geometry": {"all_pairs_alignment": 0.05}},
        "no_geometry": {"diagonal(EWC)": {"analytic": {"excess_mean": 0.02}}},
    })
    rows = e207.cells(tmp_path)
    assert [r["topology"] for r in rows] == ["real", "swap2"], rows


def test_the_rank_association_is_the_one_reported_and_validates_the_real_corpus():
    """The formula, pinned against a case whose answer is known: a monotone rise gives +1, a monotone fall -1, and a
    constant statistic has no association to report rather than an infinite one."""
    assert round(e207.spearman([1.0, 2.0, 3.0], [5.0, 6.0, 7.0]), 12) == 1.0
    assert round(e207.spearman([1.0, 2.0, 3.0], [7.0, 6.0, 5.0]), 12) == -1.0
    import math
    assert math.isnan(e207.pearson([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]))  # a constant side has no association
    # and the ranking must not invent an order among ties, or a tied family would report a spurious sign
    assert e207.rank([1.0, 1.0, 2.0]) == [1.5, 1.5, 3.0]


def test_the_sorted_table_separates_the_two_regimes_the_corpus_actually_has(tmp_path):
    """The finding's shape: 34 cells below alignment 0.12 spanning 0.047 of penalty, 8 cells at or above it spanning
    0.0076, and nothing in between. Built here at both extremes so the regime split is a property the code computes
    rather than a sentence in a finding."""
    tops = {"real": cell(0.005, 0.019), "swap0.5": cell(0.021, 0.023), "swap2": cell(0.061, 0.0125),
            "erdos_renyi": cell(0.290, 0.1419), "er2": cell(0.271, 0.1490)}
    art(tmp_path / "e901.json", tops)
    reg = e207.regime(e207.cells(tmp_path))
    assert reg[0]["topology"] == "real" and reg[-1]["alignment"] == 0.290
    flat = [c for c in reg if c["alignment"] < 0.12]
    high = [c for c in reg if c["alignment"] >= 0.12]
    assert len(flat) == 3 and len(high) == 2
    assert min(c["penalty"] for c in high) - max(c["penalty"] for c in flat) > 0.08
    assert (min(c["alignment"] for c in high) / max(c["alignment"] for c in flat)) > 3.0


def test_the_outlier_is_named_and_its_leverage_is_made_visible(tmp_path):
    """The ER topology carries a Pearson coefficient on its own, which is why the rank correlation decides and the
    Pearson-without-ER is printed beside it. The first version of the module printed only Pearson and reported
    +0.97 for alignment, i.e. a statement about one point of five."""
    tops = {"real": cell(0.005, 0.019), "swap0.5": cell(0.021, 0.023), "swap2": cell(0.061, 0.0125),
            "erdos_renyi": cell(0.290, 0.1419)}
    art(tmp_path / "e902.json", tops, circuit_size=800)
    rows = e207.cells(tmp_path)
    a = e207.associations(rows)["all_pairs_alignment"]
    assert abs(a["r"] - a["rho"]) > 0.4, a          # Pearson is the outlier's line, Spearman is not
    assert a["n"] == 4
    # removing the outlier leaves the in-axis triple, whose association is the opposite sign
    assert a["r_without_outlier"] < 0, a
