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


#: the four strengths the screen runs, and their five realizations
STRENGTHS = {"swap8": 0.04, "swap16": 0.05, "swap32": 0.06, "swap64": 0.07}


def full_screen(tmp_path, cells: dict | None = None, extra_artifact: str | None = None,
                extra_cells: dict | None = None, timing_s: float = 500.0) -> None:
    """The registered screen: four strengths x five realizations, at 500 s per run (12.5 min per cell at four cells)."""
    base = dict(cells or STRENGTHS)
    for rs in range(5):
        screen(tmp_path / f"e209_screen_rs{rs}.json", base, timing_s=timing_s)
    if extra_artifact:
        screen(tmp_path / extra_artifact, {**(extra_cells or base)}, timing_s=timing_s)


def judged(rows: list[dict], budget_s: float | None = None) -> dict:
    return {r["id"]: r for r in e210.judge(rows, budget_s)}


def test_the_reader_refuses_every_claim_when_no_screen_artifact_exists():
    """An absent artifact is a refusal and not a fired falsifier -- the rule the whole reader exists to keep."""
    assert e210.screen_cells(Path("runs/definitely-not-here")) == []
    assert all("REFUSED" in r["verdict"] for r in e210.judge([]))


def test_a_partial_screen_is_refused_rather_than_judged(tmp_path):
    """The claims are stated over the WHOLE screen, four strengths x five realizations. Reading eight cells as if
    they were twenty is the neighbouring-subject defect one level over: every number would be right and the verdict
    would still be about a design the registration does not name."""
    for rs in range(2):
        screen(tmp_path / f"e209_screen_rs{rs}.json", STRENGTHS)
    rows = e210.screen_cells(tmp_path)
    assert len(rows) == 8
    assert all("REFUSED" in r["verdict"] and "partial design" in r["verdict"] for r in e210.judge(rows))
    full_screen(tmp_path)
    assert len(e210.screen_cells(tmp_path)) == e210.EXPECTED_CELLS
    assert judged(e210.screen_cells(tmp_path))["S1"]["verdict"] == "MET"


def test_s1_fires_on_either_failure_it_names_a_cell_with_an_arm_or_an_overrun(tmp_path):
    """S1 has two failure modes and both must fire: a cell carrying an arm is a stage-2 measurement sitting in a
    screen, and the total cost is a budget the registration named."""
    full_screen(tmp_path)
    assert judged(e210.screen_cells(tmp_path))["S1"]["verdict"] == "MET"
    full_screen(tmp_path, extra_artifact="e209_screen_rs9.json", extra_cells={"swap8": 0.04}, timing_s=500.0)
    (tmp_path / "e209_screen_rs9.json").write_text(
        json.dumps({"config": {"circuit_size": 800}, "timing_s": 1.0,
                    "topologies": {"swap8": {"geometry": {"all_pairs_alignment": 0.04, "chance_alignment": 0.05},
                                             "diagonal(EWC)": {"analytic": {"excess_mean": 0.02}}}}}),
        encoding="utf-8")
    assert "FALSIFIER FIRED" in judged(e210.screen_cells(tmp_path))["S1"]["verdict"]
    (tmp_path / "e209_screen_rs9.json").unlink()
    full_screen(tmp_path, timing_s=99_999.0)
    assert "FALSIFIER FIRED" in judged(e210.screen_cells(tmp_path), 45 * 60)["S1"]["verdict"]


def test_s2_reads_the_band_by_its_edges_and_s3_needs_four_strengths_with_realizations(tmp_path):
    """The band is the measured pair 0.09101-0.27135 and not a round figure; S3 is stated over four strengths, so a
    screen with fewer is refused rather than judged on the strengths it happens to have."""
    full_screen(tmp_path)
    assert judged(e210.screen_cells(tmp_path))["S2"]["verdict"] == "FALSIFIER FIRED"
    assert judged(e210.screen_cells(tmp_path))["S3"]["verdict"] == "FALSIFIER FIRED"   # no strength spreads
    full_screen(tmp_path, cells={**STRENGTHS, "swap32": 0.12})
    assert judged(e210.screen_cells(tmp_path))["S2"]["verdict"] == "MET"               # one cell inside the band
    # S3 is about the spread WITHIN a strength, so the realizations must differ: two strengths with a ratio >= 1.5
    for rs in range(5):
        cells = {**STRENGTHS, "swap8": 0.02 if rs == 0 else 0.06,      # 3.0x
                 "swap16": 0.03 if rs < 2 else 0.048}                  # 1.6x
        screen(tmp_path / f"e209_screen_rs{rs}.json", cells, timing_s=500.0)
    assert judged(e210.screen_cells(tmp_path))["S3"]["verdict"] == "MET"
    # and one spreading strength is not enough
    for rs in range(5):
        cells = {**STRENGTHS, "swap8": 0.02 if rs == 0 else 0.06}
        screen(tmp_path / f"e209_screen_rs{rs}.json", cells, timing_s=500.0)
    assert judged(e210.screen_cells(tmp_path))["S3"]["verdict"] == "FALSIFIER FIRED"
    # and the band's edges are inclusive: the hole's own floor counts as inside
    full_screen(tmp_path, cells={**STRENGTHS, "swap64": e210.BAND[0]})
    assert judged(e210.screen_cells(tmp_path))["S2"]["verdict"] == "MET"
    full_screen(tmp_path, cells={**STRENGTHS, "swap64": e210.BAND[0] - 1e-6})
    assert judged(e210.screen_cells(tmp_path))["S2"]["verdict"] == "FALSIFIER FIRED"
