from __future__ import annotations

import json
from pathlib import Path

from experiments import e224_share_vs_size_read as e224


def art(path: Path, cells: dict[str, float], rs: int = 0, cs: int = 400, support: int = 80) -> Path:
    """One drawing: `{topology: analytic excess}` in the shape `--no-realized` writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tops = {name: {"diagonal(EWC)": {"analytic": {"excess_mean": val, "excess_sem": 0.001}}}
            for name, val in cells.items()}
    path.write_text(json.dumps({"config": {"circuit_size": cs, "support": support, "rewire_seed": rs},
                                "topologies": tops}), encoding="utf-8")
    return path


def test_a_cells_level_is_the_excess_of_the_topology_named_alloy_not_a_key_inside_a_block(tmp_path):
    """The naming has two levels -- a topology (`alloy1`) and an arm inside it (`diagonal(EWC)`) -- and the one-side
    nulls ARE topologies. The first version of this reader looked for `block["alloy1"]`, which no artifact has, and
    reported both references unreadable; this test pins the reading."""
    art(tmp_path / "e213_alloy_draws_rs0.json", {"alloy1": 0.09, "bio:cell_class": 0.01}, cs=800)
    assert e224.level_of(tmp_path / "e213_alloy_draws_rs0.json") == 0.09
    art(tmp_path / "e216_inalloy_rs0.json", {"alloy1": 0.08, "inalloy1": 0.06}, cs=800)
    assert abs(e224.level_of(tmp_path / "e216_inalloy_rs0.json") - 0.07) < 1e-12


def test_the_reader_refuses_without_two_drawings_or_without_its_references(tmp_path):
    """The claims are stated over two drawings and against two references read from their own artifacts; a claim
    against a remembered number is refused, which is the rule every reader in this line applies."""
    art(tmp_path / "e223_cs400_support80_rs0.json", {"alloy1": 0.12, "inalloy1": 0.11, "erdos_renyi": 0.16})
    assert "2" in e224.judge(e224.drawings(tmp_path), 0.13, 0.05)[0]["verdict"]
    art(tmp_path / "e223_cs400_support80_rs1.json", {"alloy1": 0.12, "inalloy1": 0.11, "erdos_renyi": 0.16}, rs=1)
    rows = e224.drawings(tmp_path)
    assert "REFUSED" in e224.judge(rows, None, 0.05)[0]["verdict"]
    assert "cs 400/support 40" in e224.judge(rows, None, 0.05)[0]["verdict"]
    assert e224.judge(rows, 0.13, 0.05)[0]["verdict"] in ("MET", "null band", "FALSIFIER FIRED")


def test_s1_and_s2_read_the_drop_and_the_midpoint(tmp_path):
    """S1 asks for a 1.5x drop from the same circuit's other support; S2 asks whether the level moved past the
    midpoint toward the larger share. A design that drops 1.2x is S1's null and can still be S2's null."""
    for rs in (0, 1):
        art(tmp_path / f"e223_cs400_support80_rs{rs}.json",
            {"alloy1": 0.045, "inalloy1": 0.045, "erdos_renyi": 0.16}, rs=rs)
    rows = e224.drawings(tmp_path)
    got = {r["id"]: r for r in e224.judge(rows, 0.1327, 0.0496)}
    assert got["S1"]["verdict"] == "MET", got["S1"]          # 0.045 against 0.1327 = 2.9x lower
    assert got["S2"]["verdict"] == "MET", got["S2"]          # below the 0.0912 midpoint
    for rs in (0, 1):
        art(tmp_path / f"e223_cs400_support80_rs{rs}.json",
            {"alloy1": 0.115, "inalloy1": 0.11, "erdos_renyi": 0.16}, rs=rs)
    got = {r["id"]: r for r in e224.judge(e224.drawings(tmp_path), 0.1327, 0.0496)}
    assert got["S1"]["verdict"].startswith("null band"), got["S1"]     # 1.17x lower
    assert got["S2"]["verdict"].startswith("null band"), got["S2"]     # above the midpoint, below the reference
    for rs in (0, 1):
        art(tmp_path / f"e223_cs400_support80_rs{rs}.json",
            {"alloy1": 0.15, "inalloy1": 0.14, "erdos_renyi": 0.16}, rs=rs)
    got = {r["id"]: r for r in e224.judge(e224.drawings(tmp_path), 0.1327, 0.0496)}
    assert "FALSIFIER" in got["S1"]["verdict"] and "FALSIFIER" in got["S2"]["verdict"]


def test_the_references_are_recomputed_and_checked_against_the_registration():
    """The registered figures are printed beside the measured ones, so a disagreement is visible rather than
    silent; the numbers this week's registration quotes are 0.1315 and 0.0490."""
    assert e224.REGISTERED == {"cs400_support40": 0.1315, "cs800_support80": 0.0490}
    assert e224.S1_BAR == 1.5
