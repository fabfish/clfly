"""`domain_rule` is where the declared domain lives now, so the tests pin the rule's arithmetic, the two filters the
readers apply, the two-column statement -- including a claim that leaves the table and a domain that leaves a reader
nothing -- and the live corpus's membership.
"""

from __future__ import annotations

from pathlib import Path

from experiments import domain_rule as rule
from experiments.e247_count_matched_spread import per_cell


def fam_of(spec: dict) -> dict:
    """{cell: {family: scatter}} -> a `per_cell`-shaped structure whose excesses realise those scatters."""
    out: dict = {}
    for cell, fams in spec.items():
        for f, spread in fams.items():
            out.setdefault(f, {})[cell] = {"excess": [1.0, spread], "rank": [1.0, 1.1], "keys": [0, 1]}
    return out


def test_a_cell_is_in_the_domain_when_every_family_measured_there_scatters_within_the_bar():
    cells = rule.cell_scatters(fam_of({(300, 30, 0.9): {"alloy1": 2.0, "swap2": 1.5},
                                       (300, 30, 0.99): {"alloy1": 32.0, "signshuffle": 4.5}}))
    inside, outside = rule.domain(cells, 4.0)
    assert inside == {(300, 30, 0.9)} and outside == {(300, 30, 0.99)}, (inside, outside)
    assert rule.domain(cells, 32.0)[1] == set(), "at the excluded cell's own maximum nothing is excluded"
    assert rule.domain(cells, 1.4)[1] == {(300, 30, 0.9), (300, 30, 0.99)}, "a low bar excludes both"


def test_the_bar_is_read_from_the_cell_s_maximum_and_a_family_can_exclude_it_alone():
    cells = rule.cell_scatters(fam_of({(800, 80, 0.9): {"alloy0.9": 3.3444, "alloy1": 3.3433,
                                                       "erdos_renyi": 1.06}}))
    assert rule.domain(cells, 3.34)[1] == {(800, 80, 0.9)}, "3.34 is below the true maximum"
    assert rule.domain(cells, 3.3445)[1] == set(), "and 3.3445 is above it"


def test_a_single_drawing_contributes_no_scatter_and_cannot_carry_a_cell_into_the_domain():
    """A cell whose families each have one drawing has no scatter at all, so it is neither in nor out -- it is absent,
    which is why the rule is applied to the cells a reader actually measured."""
    fam = fam_of({(300, 30, 0.9): {"alloy1": 2.0}})
    fam["alloy1"][(300, 30, 0.95)] = {"excess": [1.0], "rank": [1.0], "keys": [0]}
    cells = rule.cell_scatters(fam)
    assert set(cells) == {(300, 30, 0.9)}, cells
    assert rule.domain(cells, 4.0)[0] == {(300, 30, 0.9)}
    assert rule.domain(cells, 1.9)[0] == set(), "and a bar under the one scatter excludes it"


def test_the_two_filters_keep_the_groups_and_the_family_rows_of_the_in_domain_cells():
    gs = [{"cell": (300, 30, 0.9), "family": "alloy1"}, {"cell": (300, 30, 0.99), "family": "alloy1"}]
    assert rule.filter_gs(gs, {(300, 30, 0.9)}) == [gs[0]]
    assert rule.filter_gs(gs, set()) == []
    fam = fam_of({(300, 30, 0.9): {"alloy1": 2.0}, (300, 30, 0.99): {"alloy1": 32.0}})
    kept = rule.filter_fam(fam, {(300, 30, 0.9)})
    assert kept["alloy1"] == {(300, 30, 0.9): fam["alloy1"][(300, 30, 0.9)]}
    assert rule.filter_fam(fam, set())["alloy1"] == {}, "the family keeps its name and loses its cells"


def _rows(*pairs: tuple[str, str]) -> list[dict]:
    return [{"id": cid, "verdict": v} for cid, v in pairs]


def test_the_statement_names_the_claim_the_domain_moves_and_counts_it():
    all_ = _rows(("K1", "null band -- ordered but overlapping"), ("K2", "MET -- the orderings agree"))
    dom = _rows(("K1", "MET -- the orderings agree"), ("K2", "MET -- the orderings agree"))
    text = rule.statement(all_, dom)
    assert "K1 MET" in text and "K1 null band" in text
    assert "the domain changes 1 of 2: K1" in text, text


def test_the_statement_says_so_when_the_domain_moves_nothing():
    rows = _rows(("N1", "MET -- the family moves"), ("N2", "MET -- the same ordering"))
    assert "the domain changes none of the 2 claims" in rule.statement(rows, rows)


def test_the_statement_reports_a_claim_that_leaves_the_table_as_moved_and_an_empty_domain_as_empty():
    """The hole the fold closes: a claim can go missing rather than change its words, and a reader whose corpus the
    domain empties has no reading at all -- both must be visible in the sentence rather than absent from it."""
    all_ = _rows(("R1", "MET -- the spans are ordered"))
    text = rule.statement(all_, [])
    assert "0 of 1 claims read here" in text and "none of them" in text, text
    assert "the domain changes 1 of 1: R1" in text, text


def test_the_live_corpus_puts_the_near_critical_cells_outside_and_the_convention_cell_inside():
    if not Path("runs").exists():
        return
    inside, outside = rule.corpus(Path("runs"))
    assert inside and outside, (inside, outside)
    assert not inside & outside, "the two sets partition the cells"
    for cell in ((300, 30, 0.98), (300, 30, 0.99)):
        assert cell in outside, cell
    for cell in ((800, 80, 0.9), (300, 30, 0.9)):
        assert cell in inside, cell
    assert rule.inside_cells(Path("runs")) == inside, "the one-cell reading and the pair agree"
    scatters = rule.cell_scatters(per_cell(Path("runs")))
    assert min(max(v.values()) for c, v in scatters.items() if c in outside) > rule.T > \
        max(max(v.values()) for c, v in scatters.items() if c in inside), "the bar sits between the two sides"
    assert rule.inside_cells(Path("runs"), 1e9) == set(inside) | set(outside), "above every scatter nothing is out"
