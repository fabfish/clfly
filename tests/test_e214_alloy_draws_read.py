from __future__ import annotations

import json
from pathlib import Path

from experiments import e214_alloy_draws_read as e214


def artifact(path: Path, cells: dict[str, tuple[float, float]], rew: int = 0,
             chance: float = 0.0555, sem: float = 0.0005) -> Path:
    """One drawing: `{topology: (alignment, excess)}` in the shape `--no-realized` writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tops = {}
    for topology, (alignment, excess) in cells.items():
        tops[topology] = {
            "geometry": {"all_pairs_alignment": alignment, "chance_alignment": chance,
                         "top_eig_share": 0.3, "effective_rank": 10.0},
            "diagonal(EWC)": {"analytic": {"excess_mean": excess, "excess_sem": sem,
                                           "excess_per_seed": [excess, excess + 0.001]}},
        }
    path.write_text(json.dumps({"config": {"circuit_size": 800, "rewire_seed": rew}, "topologies": tops}),
                    encoding="utf-8")
    return path


def design(tmp_path, pairs: list[tuple[float, float, float]]) -> None:
    """`pairs` is one `(alloy0.9 excess, alloy1 excess, alloy1 alignment)` per drawing, five of them."""
    for rew, (e09, e1, a1) in enumerate(pairs):
        artifact(tmp_path / f"e213_alloy_draws_rs{rew}.json",
                 {"alloy0.9": (a1 * 0.75, e09), "alloy1": (a1, e1)}, rew=rew)


def judged(tmp_path) -> dict:
    return {r["id"]: r for r in e214.judge(e214.cells(tmp_path))}


def test_the_reader_refuses_while_the_design_is_partial():
    """The claims are stated over ten cells, and reading four as if they were ten is the neighbouring-subject defect
    one level over -- every number right and the verdict about a design the registration does not name."""
    assert "no e213" in e214.judge([])[0]["verdict"]
    assert e214.cells(Path("runs/definitely-not-here")) == []
    # one cell is not ten, and the refusal says which count it was given
    one = [{"alignment": 0.14, "excess": 0.1, "fraction": 1.0, "sem": 0.001}]
    assert "1 are on disk" in e214.judge(one)[0]["verdict"]


def test_w1_counts_the_band_by_its_measured_edges(tmp_path):
    """The band is the measured pair 0.09101-0.27135, so a cell exactly on the floor counts and one just below does
    not; the claim needs three of ten."""
    design(tmp_path, [(0.02, 0.10, 0.15), (0.02, 0.09, 0.13), (0.02, 0.08, 0.12),
                      (0.02, 0.07, 0.06), (0.02, 0.06, 0.05)])
    rows = e214.cells(tmp_path)
    assert len(rows) == 10
    assert judged(tmp_path)["W1"]["verdict"] == "MET"          # three alignments (0.15, 0.13, 0.12) are in the band
    design(tmp_path, [(0.02, 0.10, e214.BAND[0] - 1e-6), (0.02, 0.09, 0.08), (0.02, 0.08, 0.07),
                      (0.02, 0.07, 0.06), (0.02, 0.06, 0.05)])
    assert judged(tmp_path)["W1"]["verdict"] == "FALSIFIER FIRED"


def test_w2_compares_the_fraction_effect_against_the_drawing_spread(tmp_path):
    """The claim is not "the fractions differ" but "they differ by more than the drawings of one fraction do" -- which
    is the question the two-drawing alloy1 disagreement raised."""
    # five alloy1 drawings spread over 0.02 (range), five alloy0.9 drawings tight, means 0.06 apart
    design(tmp_path, [(0.02, 0.05, 0.10), (0.02, 0.06, 0.11), (0.02, 0.07, 0.12), (0.02, 0.05, 0.13), (0.02, 0.06, 0.14)])
    assert judged(tmp_path)["W2"]["verdict"] == "MET"          # means differ by 0.04 against a 0.02 range
    # now the drawings of alloy1 spread MORE than the two means differ
    design(tmp_path, [(0.02, 0.02, 0.10), (0.02, 0.06, 0.11), (0.02, 0.10, 0.12), (0.02, 0.04, 0.13), (0.02, 0.08, 0.14)])
    assert judged(tmp_path)["W2"]["verdict"] == "FALSIFIER FIRED"
    # and a difference between one and one-and-a-half times the range is the registered null
    design(tmp_path, [(0.02, 0.02, 0.10), (0.02, 0.05, 0.11), (0.02, 0.08, 0.12), (0.02, 0.04, 0.13), (0.02, 0.06, 0.14)])
    assert judged(tmp_path)["W2"]["verdict"] in ("null band", "FALSIFIER FIRED")


def test_w3_ranks_alignment_against_penalty_across_drawings(tmp_path):
    """The quantity the whole design exists for: if this is strong while W2 is not, the ALIGNMENT is the variable to
    index by and the fraction is only a means of producing it."""
    design(tmp_path, [(0.02, 0.02, 0.10), (0.03, 0.03, 0.11), (0.04, 0.04, 0.12), (0.05, 0.05, 0.13), (0.06, 0.06, 0.14)])
    assert judged(tmp_path)["W3"]["verdict"] == "MET"          # perfectly ranked
    design(tmp_path, [(0.06, 0.10, 0.10), (0.05, 0.06, 0.11), (0.04, 0.05, 0.12), (0.03, 0.04, 0.13), (0.02, 0.04, 0.14)])
    assert judged(tmp_path)["W3"]["verdict"] == "FALSIFIER FIRED"   # inverted
    # the rank helper must not invent an order among ties
    assert e214.rank([1.0, 1.0, 2.0]) == [1.5, 1.5, 3.0]
    assert round(e214.pearson(e214.rank([1.0, 2.0, 3.0]), e214.rank([3.0, 2.0, 1.0])), 12) == -1.0
