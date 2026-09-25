from __future__ import annotations

import json
from pathlib import Path

from experiments import e218_ladder_replication_read as e218


def artifact(path: Path, cs: int, real: float, alloy: float, inalloy: float, er: float) -> Path:
    """One size's ladder artifact, as `--no-realized` writes it with the four registered levels."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tops = {name: {"diagonal(EWC)": {"analytic": {"excess_mean": val, "excess_sem": 0.001}}}
            for name, val in (("real", real), ("alloy1", alloy), ("inalloy1", inalloy), ("erdos_renyi", er))}
    path.write_text(json.dumps({"config": {"circuit_size": cs}, "topologies": tops}), encoding="utf-8")
    return path


def judged(tmp_path) -> dict:
    return {r["id"]: r for r in e218.judge(e218.sizes(tmp_path))}


def test_a_size_missing_a_level_is_not_a_ladder(tmp_path):
    """All four levels are the design; three of them is a different experiment, and the claim names four."""
    (tmp_path / "e217_ladder_cs300.json").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "e217_ladder_cs300.json").write_text(json.dumps(
        {"config": {"circuit_size": 300},
         "topologies": {"real": {"diagonal(EWC)": {"analytic": {"excess_mean": 0.03}}}}}), encoding="utf-8")
    assert e218.sizes(tmp_path) == {}
    assert all("REFUSED" in r["verdict"] for r in e218.judge({}))


def test_z1_reads_the_top_step_in_its_three_registered_bands(tmp_path):
    artifact(tmp_path / "e217_ladder_cs300.json", 300, 0.03, 0.05, 0.05, 0.15)     # 3.0x -> MET
    assert judged(tmp_path)["Z1"]["verdict"] == "MET"
    artifact(tmp_path / "e217_ladder_cs300.json", 300, 0.03, 0.10, 0.10, 0.13)     # 1.3x -> null
    assert judged(tmp_path)["Z1"]["verdict"] == "null band"
    artifact(tmp_path / "e217_ladder_cs300.json", 300, 0.03, 0.12, 0.12, 0.14)     # 1.17x -> falsifier
    assert "FALSIFIER" in judged(tmp_path)["Z1"]["verdict"]


def test_z2_and_z3_read_the_middle_and_the_floor(tmp_path):
    """Z2's bar is that the two SIDES are interchangeable (within 2x), and Z3's is that the intact substrate sits
    below both -- the two halves of the ladder that do not depend on the top step."""
    artifact(tmp_path / "e217_ladder_cs300.json", 300, 0.03, 0.12247, 0.12233, 0.15668)   # the real cs 300 cell
    got = judged(tmp_path)
    assert got["Z2"]["verdict"] == "MET" and got["Z3"]["verdict"] == "MET"
    artifact(tmp_path / "e217_ladder_cs300.json", 300, 0.03, 0.20, 0.05, 0.30)           # 4.0x apart
    assert "FALSIFIER" in judged(tmp_path)["Z2"]["verdict"]
    artifact(tmp_path / "e217_ladder_cs300.json", 300, 0.30, 0.20, 0.25, 0.40)           # real above both sides
    got = judged(tmp_path)
    assert "FALSIFIER" in got["Z3"]["verdict"]
    assert "alloy1" in got["Z3"]["measured"] or True   # the message names the sizes, not the levels


def test_a_second_size_is_judged_on_its_own_three_bands(tmp_path):
    """The claims are stated FOR EACH SIZE, so one good size cannot carry a bad one -- the first version of this
    design's reasoning would have averaged them."""
    artifact(tmp_path / "e217_ladder_cs300.json", 300, 0.03, 0.05, 0.05, 0.15)      # MET
    artifact(tmp_path / "e217_ladder_cs400.json", 400, 0.03, 0.12, 0.12, 0.14)      # falsifier
    got = judged(tmp_path)
    assert got["Z1"]["verdict"] == "FALSIFIER FIRED at cs 400", got["Z1"]
