"""`e244` reads the corpus's accidental drawings, so the tests pin the three things its verdicts turn on: that `real`
is not a kind, that the relative spread is scale-free where the first implementation's was not, and that the
within-cell test (K3) fires on a reversal the pooled test cannot see -- which is the finding's whole point.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median

from experiments import e244_drawing_spread_by_kind as e244


def _artifact(path: Path, *, size: int, support: int, rewire_seed: int, tops: dict) -> None:
    """One stand-in run: only the fields the module reads (`config`, and each topology's excess and rank)."""
    path.write_text(json.dumps({
        "config": {"circuit_size": size, "support": support, "rho": 0.9, "seeds": 3, "rewire_seed": rewire_seed},
        "topologies": {t: {"diagonal(EWC)": {"analytic": {"excess_mean": ex}},
                           "geometry": {"effective_rank": rk}} for t, (ex, rk) in tops.items()}}),
        encoding="utf-8")


def _one(gs, cell, family):
    return {(x["cell"], x["family"]): x for x in gs}[(cell, family)]


def test_real_is_not_a_kind_and_the_swap_strengths_are():
    """`real` is the observed network, never redrawn -- it must fall outside the ladder, and every construction on it."""
    assert e244.kind_of("real") is None
    assert e244.kind_of("swap0.5") == e244.kind_of("swap64") == e244.kind_of("signshuffle") == 0
    assert e244.kind_of("alloy1") == e244.kind_of("alloy0.25") == e244.kind_of("inalloy1") == 1
    assert e244.kind_of("erdos_renyi") == 2
    assert e244.kind_of("degree_sequence") is None


def test_the_relative_range_is_scale_free_while_spread_over_mean_is_not(tmp_path):
    """The same two drawings at ten times the level: the ratio spread and `(max - min)/mean` are unchanged, while the
    first implementation's `spread / mean` moves by the factor of ten. That is why K2 was rewritten before reporting."""
    for name, scale in (("a", 1.0), ("b", 10.0)):
        d = tmp_path / name
        d.mkdir()
        for rw, v in ((0, 0.05), (1, 0.10)):
            _artifact(d / f"r{rw}.json", size=800, support=80, rewire_seed=rw, tops={"alloy1": (v * scale, 30.0)})
    lo, _ = e244.groups(tmp_path / "a")
    hi, _ = e244.groups(tmp_path / "b")
    lo, hi = _one(lo, (800, 80, 0.9), "alloy1"), _one(hi, (800, 80, 0.9), "alloy1")
    assert lo["excess_spread"] == hi["excess_spread"] == 2.0
    assert abs(lo["excess_rel_range"] - hi["excess_rel_range"]) < 1e-12, (lo, hi)
    assert abs((lo["excess_spread"] / lo["excess_mean"]) / (hi["excess_spread"] / hi["excess_mean"]) - 10.0) < 1e-9


def _corpus(root: Path, alloy1_at_convention: tuple[float, float]) -> None:
    """The live shape in miniature: one cell carries all three kinds, four more carry only kinds 1 and 2 -- so the
    kind-0 rung is one cell's number while kind 1's is a five-cell median, which is how a reversal gets diluted."""
    for rw, (a0, a1) in ((0, (0.020, alloy1_at_convention[0])), (1, (0.021, alloy1_at_convention[1]))):
        _artifact(root / f"conv{rw}.json", size=800, support=80, rewire_seed=rw,
                  tops={"swap2": (a0, 5.0), "alloy1": (a1, 30.0), "erdos_renyi": (0.100 + 0.001 * rw, 90.0)})
    for i, (size, support) in enumerate(((400, 40), (400, 80), (300, 30), (800, 20))):
        for rw, a1 in ((0, 0.040), (1, 0.041)):
            _artifact(root / f"c{i}_{rw}.json", size=size, support=support, rewire_seed=rw,
                      tops={"alloy1": (a1, 30.0), "erdos_renyi": (0.100 + 0.001 * rw, 90.0)})


def test_k3_is_MET_when_every_cell_lists_the_kinds_in_order(tmp_path):
    """All kinds ordered inside every cell: the pooled K1 orders and the within-cell K3 confirms it."""
    _corpus(tmp_path, (0.040, 0.041))
    gs, _ = e244.groups(tmp_path)
    rows = {r["id"]: r for r in e244.judge(gs)}
    assert rows["K1"]["verdict"].startswith("MET"), rows["K1"]
    assert rows["K3"]["verdict"].startswith("MET"), rows["K3"]
    assert "6 of 6" in rows["K3"]["measured"], rows["K3"]


def test_k3_fires_on_one_cell_whose_one_side_family_spreads_wider(tmp_path):
    """The same corpus with the one cell that carries all three kinds reversed: the pooled K1 still orders, because the
    kind-0 rung is that single cell while kind 1's median sits on five -- and K3 is the claim that notices."""
    _corpus(tmp_path, (0.010, 0.030))
    gs, _ = e244.groups(tmp_path)
    rows = {r["id"]: r for r in e244.judge(gs)}
    assert rows["K1"]["verdict"].startswith("MET"), rows["K1"]
    assert rows["K3"]["verdict"].startswith("FALSIFIER FIRED"), rows["K3"]
    assert "5 of 6" in rows["K3"]["measured"] and "800/sup 80" in rows["K3"]["measured"], rows["K3"]


def test_the_same_reversal_without_the_four_other_cells_breaks_the_pooled_K1(tmp_path):
    """Drop the four kind-1-and-2-only cells and the reversal is no longer diluted: now K1 and K3 fire together, which
    is what makes K3's role here a check on the pooling rather than a second opinion."""
    for rw, (a0, a1) in ((0, (0.020, 0.010)), (1, (0.021, 0.030))):
        _artifact(tmp_path / f"conv{rw}.json", size=800, support=80, rewire_seed=rw,
                  tops={"swap2": (a0, 5.0), "alloy1": (a1, 30.0), "erdos_renyi": (0.100 + 0.001 * rw, 90.0)})
    gs, _ = e244.groups(tmp_path)
    rows = {r["id"]: r for r in e244.judge(gs)}
    assert rows["K1"]["verdict"].startswith("FALSIFIER FIRED"), rows["K1"]
    assert rows["K3"]["verdict"].startswith("FALSIFIER FIRED"), rows["K3"]


def test_the_live_census_orders_when_pooled_and_reverses_at_every_comparable_cell():
    """The findings' numbers, pinned on the artifact: K1 ordered with disjoint ranges, K3's reversal at both cells that
    carry a no-destruction construction, and the margins -- +2.2% at cs 300/support 30 and +104.4% at cs 800/support
    80 -- which is why kind 0's stability and kind 1's volatility, not kind 0's looseness, is the reading."""
    p = Path("runs/e244_drawing_spread_by_kind.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in d["claims"]}
    assert rows["K1"]["verdict"].startswith("null band"), rows["K1"]  # e255's six stable low-rho groups pulled kind 1 back
    assert rows["K2"]["verdict"].startswith("MET"), rows["K2"]  # the relative form orders again with e255's groups in
    assert rows["K3"]["verdict"].startswith("FALSIFIER FIRED"), rows["K3"]
    assert "18 of 23" in rows["K3"]["measured"], rows["K3"]
    kinds: dict = {}
    for g in d["groups"]:
        if g["excess_spread"] is not None:
            kinds.setdefault(tuple(g["cell"]), {}).setdefault(g["kind"], []).append(g["excess_spread"])
    cell = kinds[(800, 80, 0.9)]
    assert sorted(cell) == [0, 1, 2], sorted(cell)
    assert median(cell[1]) > median(cell[0]), "the reversal: the one-side kind is the looser one inside the cell"
    assert median(cell[2]) < min(median(cell[0]), median(cell[1])), "the two-side kind is tightest there"
    # and the second cell, where the reversal is 47x smaller -- the direction replicates, the magnitude does not
    small = kinds[(300, 30, 0.9)]
    assert sorted(small) == [0, 1, 2], sorted(small)
    assert median(small[1]) > median(small[0]), small
    assert median(small[1]) / median(small[0]) < 1.1, "inside the registered null band, not a second reversal"
    assert median(cell[1]) / median(cell[0]) > 1.5, "and the convention cell's margin is the one that is large"
    # the third cell e249 bought: there the NO-destruction rung is the looser one, the pooled K1 direction
    third = kinds[(800, 20, 0.9)]
    assert sorted(third) == [0, 1, 2], sorted(third)
    assert median(third[0]) > median(third[1]), "cs 800/support 20 gives the pooled direction at matched counts"
    # kind 0 is the stable rung across the cells and kind 1 is the volatile one -- the reading, pinned
    assert abs(median(cell[0]) / median(small[0]) - 1.0) < 0.1, (median(cell[0]), median(small[0]))
    assert {tuple(g["cell"]) for g in d["groups"] if g["kind"] == 0} == {(800, 80, 0.9), (300, 30, 0.9), (300, 30, 0.99), (800, 20, 0.9), (400, 40, 0.9)}
    assert d["control"] and all(c["excess_spread"] == 1.0 for c in d["control"]), d["control"]


def test_the_domain_flag_adds_a_second_reading_and_changes_the_first_in_nothing(tmp_path, capsys):
    """A corpus with nothing to exclude: the flag writes `claims_domain` beside `claims`, the two agree row for row,
    and the statement says so. This is the additive half of the fold, on a corpus the rule cannot fire on."""
    _corpus(tmp_path, (0.040, 0.041))
    out = tmp_path / "e244.json"
    assert e244.main(["--runs", str(tmp_path), "--json-out", str(out), "--domain"]) == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    assert [r["id"] for r in d["claims_domain"]] == [r["id"] for r in d["claims"]]
    assert d["claims_domain"] == d["claims"], "nothing is excluded, so the two readings are the same rows"
    assert d["domain"] and d["out_of_domain"] == [], (d["domain"], d["out_of_domain"])
    text = capsys.readouterr().out
    assert "the same claims, read inside the declared domain" in text and "changes none of the 3 claims" in text, text


def test_a_cell_the_domain_excludes_leaves_the_reader_its_claim_ids_and_not_their_old_words(tmp_path, capsys):
    """One cell, scattered fortyfold past the bar: the domain empties this reader's corpus, and what it reports is
    three REFUSED rows with K1 to K3's ids rather than the excluded cell's verdicts -- the hole the fold closes."""
    for rw, ex in ((0, 0.005), (1, 0.200)):
        _artifact(tmp_path / f"only{rw}.json", size=800, support=80, rewire_seed=rw,
                  tops={"alloy1": (ex, 30.0), "swap2": (0.020, 5.0), "erdos_renyi": (0.100, 90.0)})
    out = tmp_path / "e244.json"
    assert e244.main(["--runs", str(tmp_path), "--json-out", str(out), "--domain"]) == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["domain"] == [] and len(d["out_of_domain"]) == 1, (d["domain"], d["out_of_domain"])
    assert [r["id"] for r in d["claims_domain"]] == [r["id"] for r in d["claims"]]
    assert all(r["verdict"].startswith("REFUSED") for r in d["claims_domain"]), d["claims_domain"]
    text = capsys.readouterr().out
    assert "inside the declared domain (3 of 3 claims read here)" in text and "K1 REFUSED" in text, text
