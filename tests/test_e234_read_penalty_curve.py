"""`e234` merges two instruments -- the benchmark runner's analytic excess and `e231`'s task-build-only rank -- into
one cell per (size, topology, `rho`), and its whole job is to refuse rather than to bridge a gap.

Three ways the merge could quote something that is not the cell, all of them measured defects elsewhere in this
session and all of them tested here: a second **family** under the same config (`e225` declared the pooling/cell-class
pair as two quantities, and both carry `circuit_size 300, support 30, seeds 3`), a second **drawing** (`e219`/`e232`),
and the **last file winning** by accident. The claims are then judged only on the registered grid (`rho` 0.7 to 0.99,
since the corpus already contains a sign disagreement at 0.5) and only on families that cover it.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e234_read_penalty_curve as e234


def cell_artifact(name: str, size: int, topo: str, rho: float, excess: float, family: str = "cell_class",
                  rewire_seed: int | None = None) -> tuple[str, dict]:
    block = {"diagonal(EWC)": {"analytic": {"excess_mean": excess}}}
    block["bio:cell_class" if family == "cell_class" else "bio:pool1"] = {"analytic": {"excess_mean": 0.0}}
    cfg = {"circuit_size": size, "support": size // 10, "seeds": 3, "seed0": 0, "q": 0.02, "rho": rho}
    if rewire_seed is not None:
        cfg["rewire_seed"] = rewire_seed
    return name, {"config": cfg, "topologies": {topo: block}}


def write(tmp_path: Path, files: list[tuple[str, dict]]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for name, payload in files:
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_one_cell_one_family_one_drawing(tmp_path):
    """The live defect: `e13_control3_d952` (pooling) and `e217_ladder_cs300` (cell-class) are the same config with
    two different `real` cells, and `e219_draws_cs300_rs1` is a second drawing of the same cell."""
    root = write(tmp_path, [cell_artifact("e217_ladder_cs300.json", 300, "alloy1", 0.9, 0.12247),
                            cell_artifact("e13_control3_d952.json", 300, "alloy1", 0.9, 0.09999, family="pooling"),
                            cell_artifact("e219_draws_cs300_rs1.json", 300, "alloy1", 0.9, 0.07777,
                                          rewire_seed=1)])
    merged = e234.curves(root)
    c = merged[(300, "alloy1", 0.9)]
    assert c["excess"] == 0.12247 and c["family"] == "cell_class", c
    assert c["excess_drawings"] == 3, "the other two are counted, not dropped"
    assert c["other_families"] == ["pooling"] and 0.07777 in c["other_drawings"], c


def test_e1_steps_are_restricted_to_the_registered_grid():
    """`steps` first paired the nearest available cells and so judged the claim on a 0.5-to-0.9 step, which the
    registration explicitly excludes -- the corpus contains that sign disagreement already."""
    merged = {}
    for rho, rank, excess in ((0.5, 27.0, 0.001), (0.7, 23.0, 0.08), (0.9, 7.2, 0.12)):
        merged[(300, "alloy1", rho)] = {"size": 300, "topology": "alloy1", "rho": rho, "rank": rank, "excess": excess}
    st = e234.steps(merged, 300, "alloy1")
    assert [(s["from"], s["to"]) for s in st] == [(0.7, 0.9)], st
    assert st[0]["rank_direction"] == -1 and st[0]["excess_direction"] == 1, "the disagreement is what E1 is about"


def test_e1_refuses_until_a_family_covers_the_grid():
    merged = {(300, "alloy1", rho): {"size": 300, "topology": "alloy1", "rho": rho, "rank": 1.0, "excess": 0.1}
              for rho in (0.7, 0.9)}
    v = [c for c in e234.judge(merged) if c["id"] == "E1"][0]
    assert v["verdict"].startswith("REFUSED") and "0.7" not in v["verdict"], v
    assert "alloy1 2/6 points" in v["verdict"], v


def test_e2_refuses_until_its_three_points_exist_and_then_judges():
    partial = {(300, "erdos_renyi", 0.99): {"size": 300, "topology": "erdos_renyi", "rho": 0.99, "excess": 0.0808},
               (300, "alloy1", 0.99): {"size": 300, "topology": "alloy1", "rho": 0.99, "excess": 0.0055}}
    v = [c for c in e234.judge(partial) if c["id"] == "E2"][0]
    assert v["verdict"].startswith("REFUSED") and "0.95" in v["verdict"], v
    full = dict(partial)
    for rho, ratio in ((0.95, 14.8), (0.98, 66.8)):
        full[(300, "erdos_renyi", rho)] = {"size": 300, "topology": "erdos_renyi", "rho": rho, "excess": 0.0808}
        full[(300, "alloy1", rho)] = {"size": 300, "topology": "alloy1", "rho": rho, "excess": 0.0808 / ratio}
    v = [c for c in e234.judge(full) if c["id"] == "E2"][0]
    assert v["verdict"].startswith("MET"), v
    low = dict(full)
    low[(300, "alloy1", 0.95)] = {"size": 300, "topology": "alloy1", "rho": 0.95, "excess": 0.0808}
    v = [c for c in e234.judge(low) if c["id"] == "E2"][0]
    assert v["verdict"].startswith("FALSIFIER"), v


def test_the_live_reader_refuses_what_the_grid_does_not_yet_support():
    """The live state, whatever it is: the excess grid is being filled by `e233` and every claim whose cells are
    missing must be refused rather than judged on the cells that exist."""
    merged = e234.curves()
    verdicts = {c["id"]: c["verdict"] for c in e234.judge(merged)}
    assert set(verdicts) == {"E1", "E2"}
    for size in (300, 800):
        for topo in e234.TOPOLOGIES:
            have = {c["rho"] for c in merged.values()
                    if c["size"] == size and c["topology"] == topo and "rank" in c and "excess" in c
                    and c["rho"] in e234.GRID}
            if len(have) == len(e234.GRID):
                assert not verdicts["E1"].startswith("REFUSED"), (size, topo, have, verdicts)
                return
    assert verdicts["E1"].startswith("REFUSED"), verdicts
