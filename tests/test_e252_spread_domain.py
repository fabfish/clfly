"""`e252` declares a domain and re-reads every pooled claim inside it, so the tests pin the rule's arithmetic, the
threshold grid's stability, the restoration of the three demoted verdicts, the cost of the exclusion, and the blind
claim that no fourth verdict moves.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e252_spread_domain as e252


def fam_of(spec: dict) -> dict:
    """{cell: {family: scatter}} -> a `per_cell`-shaped structure whose excesses realise those scatters."""
    out: dict = {}
    for cell, fams in spec.items():
        for f, spread in fams.items():
            out.setdefault(f, {})[cell] = {"excess": [1.0, spread], "rank": [1.0, 1.1], "keys": [0, 1]}
    return out


def test_a_cell_is_in_the_domain_when_every_family_scatters_within_the_bar():
    fam = fam_of({(300, 30, 0.9): {"alloy1": 2.0, "swap2": 1.5},
                  (300, 30, 0.99): {"alloy1": 32.0, "signshuffle": 4.5}})
    cells = e252.cell_scatters(fam)
    inside, outside = e252.domain(cells, 4.0)
    assert inside == {(300, 30, 0.9)} and outside == {(300, 30, 0.99)}, (inside, outside)
    assert e252.domain(cells, 32.0)[1] == set(), "at the excluded cell's own maximum nothing is excluded"
    assert e252.domain(cells, 1.4)[1] == {(300, 30, 0.9), (300, 30, 0.99)}, "a low bar excludes both"


def test_the_bar_is_read_from_the_rule_s_own_quantity_and_not_from_a_family():
    """The cell's MAXIMUM decides, so a family just above the bar excludes its cell even when the cell's other families
    are far below -- which is the defect the registration's [3.34, 4.15] interval had at its upper end."""
    fam = fam_of({(800, 80, 0.9): {"alloy0.9": 3.3444, "alloy1": 3.3433, "erdos_renyi": 1.06}})
    cells = e252.cell_scatters(fam)
    assert e252.domain(cells, 3.34)[1] == {(800, 80, 0.9)}, "3.34 is below the true maximum"
    assert e252.domain(cells, 3.3445)[1] == set(), "and 3.3445 is above it"
    assert abs(max(cells[(800, 80, 0.9)].values()) - 3.3444) < 1e-9


def test_single_drawing_families_contribute_no_scatter():
    fam = fam_of({(300, 30, 0.9): {"alloy1": 2.0}})
    fam["alloy1"][(300, 30, 0.95)] = {"excess": [1.0], "rank": [1.0], "keys": [0]}
    cells = e252.cell_scatters(fam)
    assert (300, 30, 0.95) not in cells, "one drawing is not a scatter"
    assert e252.domain(cells, 4.0)[0] == {(300, 30, 0.9)}
    assert e252.filtered_fam(fam, {(300, 30, 0.9)})["alloy1"] == {(300, 30, 0.9): fam["alloy1"][(300, 30, 0.9)]}


def test_verdicts_are_read_from_the_three_readers_on_the_filtered_corpus():
    """The module must not re-implement the readers: on the live corpus its verdicts equal theirs."""
    import json as _json
    from experiments import e244_drawing_spread_by_kind as e244
    p = Path("runs/e244_drawing_spread_by_kind.json")
    if not p.exists():
        return
    live = {r["id"]: r["verdict"] for r in _json.loads(p.read_text(encoding="utf-8"))["claims"]}
    gs, _ = e244.groups()
    fam = e252.e247.per_cell(Path("runs"))
    got = e252.verdicts(set(e252.cell_scatters(fam)), gs, fam)
    for cid in ("K1", "K2", "K3"):
        assert got[cid] == live[cid], (cid, got[cid], live[cid])


def test_the_threshold_grid_leaves_the_domain_alone_between_the_two_edges():
    fam = fam_of({(300, 30, 0.9): {"alloy1": 3.0}, (300, 30, 0.99): {"alloy1": 32.0}})
    cells = e252.cell_scatters(fam)
    outs = {t: frozenset(e252.domain(cells, t)[1]) for t in (2.0, 2.5, 3.0, 3.3445, 4.0, 10.0, 31.999, 32.0)}
    assert outs[3.3445] == outs[10.0] == outs[31.999] == frozenset({(300, 30, 0.99)}), outs
    assert outs[32.0] == frozenset(), "at the excluded cell's own maximum the rule includes it: the bar must sit below"
    assert outs[2.0] == frozenset({(300, 30, 0.9), (300, 30, 0.99)}), outs


def test_the_live_artifact_restores_exactly_the_three_demoted_verdicts():
    """The finding's numbers on the artifact: six cells in and one out, K1/R1/R2 restored, 6 of 38 groups removed, and
    the blind claim holding -- the other eight claims read the same inside the domain."""
    p = Path("runs/e252_spread_domain.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert len(d["in_domain"]) == 6 and len(d["out_of_domain"]) == 1, (d["in_domain"], d["out_of_domain"])
    assert d["out_of_domain"] == ["(300, 30, 0.99)"], d["out_of_domain"]
    before, after = d["verdicts_all"], d["verdicts_domain"]
    moved = sorted(cid for cid in before if before[cid] != after.get(cid))
    assert moved == ["K1", "R1", "R2"], moved
    for cid in ("K1", "R1", "R2"):
        assert after[cid].startswith("MET"), (cid, after[cid])
    rows = {r["id"]: r for r in d["claims"]}
    for cid in ("D2", "D3", "D4"):
        assert rows[cid]["verdict"].startswith("MET"), rows[cid]
    assert rows["D1"]["verdict"].startswith("FALSIFIER FIRED"), rows["D1"]
    assert "3.3444" in rows["D1"]["measured"], rows["D1"]
