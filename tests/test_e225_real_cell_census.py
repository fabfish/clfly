from __future__ import annotations

import json
from pathlib import Path

from experiments import e225_real_cell_census as e225


def art(path: Path, value: float, **config) -> Path:
    """One artifact carrying a `real` cell, with a config that fixes the group."""
    path.parent.mkdir(parents=True, exist_ok=True)
    base = {"circuit_size": 800, "support": 80, "seeds": 3, "seed0": 0, "q": 0.02, "rewire_seed": 0}
    block = {"diagonal(EWC)": {"analytic": {"excess_mean": value}},
             "bio:cell_class": {}, "rand:cell_class": {}}
    path.write_text(json.dumps({"config": {**base, **config}, "topologies": {"real": block}}), encoding="utf-8")
    return path


def grouped(tmp_path) -> dict:
    return {tuple(sorted(g["key"].items())): g for g in e225.census(tmp_path)["groups"]}


def test_the_class_is_read_from_the_values_and_the_family_from_the_base_names(tmp_path):
    """The classification is derived: `bio:cell_class` marks the cell-class implementation and a `bio:pool*` name the
    pooling one, so a group mixing them is reported as two quantities rather than as a reproducibility failure."""
    a = art(tmp_path / "x.json", 0.0183041398)
    b = art(tmp_path / "y.json", 0.0183041398, rewire_seed=1)
    g = grouped(tmp_path)[tuple(sorted(e225.census(tmp_path)["groups"][0]["key"].items()))]
    assert g["class"] == "EXACT" and g["families"] == ["cell_class"], g
    assert b.exists() and a.exists()
    # a pooling block is a different family, and mixing them is MATERIAL-across-families rather than a failure
    p = tmp_path / "z.json"
    p.write_text(json.dumps({"config": {"circuit_size": 800, "support": 80, "seeds": 3, "seed0": 0, "q": 0.02},
                             "topologies": {"real": {"bio:pool4": {}, "diagonal(EWC)":
                                                     {"analytic": {"excess_mean": 0.03}}}}}), encoding="utf-8")
    g = [g for g in e225.census(tmp_path)["groups"] if g["n"] > 1][0]
    assert g["class"] == "MATERIAL" and sorted(g["families"]) == ["cell_class", "pooling"], g
    assert e225.report(e225.census(tmp_path)) == 0, "a mixed-family group is declared, not counted"


def test_a_material_gap_inside_one_family_is_counted(tmp_path):
    """The class that would be a reproducibility failure: two artifacts of the SAME family whose `real` cells differ
    by more than the floating bound."""
    art(tmp_path / "a.json", 0.02)
    art(tmp_path / "b.json", 0.021, rewire_seed=1)
    assert e225.report(e225.census(tmp_path)) == 1


def test_the_two_bounds_and_the_gap_that_makes_them_do_no_work():
    """The corpus's own values leave four orders between its largest within-family difference and its only
    cross-family one, so the boundary classifies identically anywhere in [1e-5, 1e-3] -- the choice is stated rather
    than hidden."""
    assert (e225.EXACT, e225.FLOATING) == (1e-12, 1e-4)
    assert e225.DECLARED_CROSS_FAMILY == "any group mixing families"
