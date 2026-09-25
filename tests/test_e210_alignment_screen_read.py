from __future__ import annotations

import json
from pathlib import Path

from experiments import e210_alignment_screen_read as e210


def screen(path: Path, cells: dict, timing_s: float = 400.0, with_arm: bool = False) -> Path:
    """One screen artifact: a `topologies` dict of geometry-only cells, as `--geometry-only` writes them."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tops = {}
    for topology, alignment in cells.items():
        block = {"geometry": {"all_pairs_alignment": alignment, "chance_alignment": 0.0555,
                              "top_eig_share": 0.5, "effective_rank": 10.0}}
        if with_arm:
            block["diagonal(EWC)"] = {"analytic": {"excess_mean": 0.02}}
        tops[topology] = block
    path.write_text(json.dumps({"config": {"circuit_size": 800, "rewire_seed": 0}, "timing_s": timing_s,
                                "topologies": tops}), encoding="utf-8")
    return path


def test_the_reader_refuses_every_claim_when_no_screen_artifact_exists():
    """An absent artifact is a refusal and not a fired falsifier -- the rule the whole reader exists to keep."""
    assert e210.screen_cells(Path("runs/definitely-not-here")) == []
    rows = e210.judge([])
    assert all("REFUSED" in r["verdict"] for r in rows), rows


def test_s1_fires_on_either_failure_it_names_a_cell_with_an_arm_or_an_overrun(tmp_path):
    """S1 has two failure modes and both must fire: a cell carrying an arm is a stage-2 measurement sitting in a
    screen, and the total cost is a budget the registration named."""
    clean = screen(tmp_path / "e209_screen_rs0.json", {"swap8": 0.05, "swap16": 0.06})
    rows = e210.screen_cells(tmp_path)
    assert {r["id"]: r for r in e210.judge(rows)}["S1"]["verdict"] == "MET"
    armed = screen(tmp_path / "e209_screen_rs1.json", {"swap8": 0.05}, with_arm=True)
    rows = e210.screen_cells(tmp_path)
    assert "FALSIFIER FIRED" in {r["id"]: r for r in e210.judge(rows)}["S1"]["verdict"]
    armed.unlink()
    screen(tmp_path / "e209_screen_rs2.json", {"swap8": 0.05}, timing_s=99_999.0)
    rows = e210.screen_cells(tmp_path)
    assert "FALSIFIER FIRED" in {r["id"]: r for r in e210.judge(rows, budget_s=45 * 60)}["S1"]["verdict"]
    assert clean.exists()


def test_s2_reads_the_band_by_its_edges_and_s3_needs_four_strengths_with_realizations(tmp_path):
    """The band is the measured pair 0.09101-0.27135 and not a round figure, and S3 is stated over four strengths --
    so a screen with fewer is refused rather than judged on the strengths it happens to have."""
    low = {"swap8": 0.04, "swap16": 0.05, "swap32": 0.06, "swap64": 0.07}
    screen(tmp_path / "e209_screen_rs0.json", low)
    rows = e210.screen_cells(tmp_path)
    assert {r["id"]: r for r in e210.judge(rows)}["S2"]["verdict"] == "FALSIFIER FIRED"
    assert "REFUSED" in {r["id"]: r for r in e210.judge(rows)}["S3"]["verdict"]
    screen(tmp_path / "e209_screen_rs1.json", {**low, "swap32": 0.12})
    rows = e210.screen_cells(tmp_path)
    judged = {r["id"]: r for r in e210.judge(rows)}
    assert judged["S2"]["verdict"] == "MET", judged["S2"]
    assert judged["S3"]["verdict"] == "FALSIFIER FIRED", judged["S3"]   # only one strength spreads
    screen(tmp_path / "e209_screen_rs2.json", {**low, "swap32": 0.12, "swap8": 0.02})
    rows = e210.screen_cells(tmp_path)
    assert {r["id"]: r for r in e210.judge(rows)}["S3"]["verdict"] == "MET"
