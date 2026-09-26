"""`e229` decides `e228`'s three registered claims, and its first duty is to say which denominator each figure is.

The top step is (**Erdős–Rényi**) ÷ (**the one-side level** = the mean of the `alloy1` and `inalloy1` excesses);
Erdős–Rényi ÷ `real` is a *different* quantity, and the live cs-300 cell shows why that matters: at `rho` 0.5 it
reads **109×** while the top step reads **1.02×**, because the `real` cell's own excess collapses by 135× when `rho`
falls. The reader also recomputes the `rho = 0.9` references from the artifacts that measured them rather than from
the record's prose, which is how the record's quoted 2.76×/3.02× turn out to be the two **families'** spellings of
one level (alloy1 over seven drawings, inalloy1 over three) rather than one level and something else.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from experiments import e229_read_rho_sweep as e229


def cell_payload(topology_excess: dict, circuit_size: int, rho: float | None = None) -> dict:
    block = {t: {"diagonal(EWC)": {"analytic": {"excess_mean": v}}} for t, v in topology_excess.items()}
    cfg = {"circuit_size": circuit_size, "support": 30 if circuit_size == 300 else 80, "seeds": 3, "seed0": 0,
           "q": 0.02}
    if rho is not None:
        cfg["rho"] = rho
    return {"config": cfg, "topologies": block, "timing_s": 1.0}


def write_runs(tmp_path: Path, files: dict[str, dict]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for name, payload in files.items():
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def full_design(cs300: dict, cs800: dict) -> dict:
    """A complete design: the two new cells per size, plus the `rho = 0.9` references the reader recomputes."""
    files = {}
    for rho, (ones, er) in cs300.items():
        files[f"e228_rho{str(rho).replace('.', '')}_cs300.json"] = cell_payload(
            {"real": 0.02, "alloy1": ones, "inalloy1": ones, "erdos_renyi": er}, 300, rho)
    for rho, (ones, er) in cs800.items():
        files[f"e228_rho{str(rho).replace('.', '')}_cs800.json"] = cell_payload(
            {"real": 0.018, "alloy1": ones, "inalloy1": ones, "erdos_renyi": er}, 800, rho)
    # the references: cs 300 from one artifact, cs 800 from an ER artifact plus each family's own drawings
    files["e217_ladder_cs300.json"] = cell_payload({"real": 0.02978, "alloy1": 0.12247, "inalloy1": 0.12233,
                                                    "erdos_renyi": 0.15668}, 300)
    files["e208_hole_sweep_cs800_3seeds.json"] = cell_payload({"real": 0.01830, "erdos_renyi": 0.14187}, 800)
    files["e212_alloy_analytic_rs0.json"] = cell_payload({"alloy1": 0.10067}, 800)
    files["e213_alloy_draws_rs0.json"] = cell_payload({"alloy1": 0.04130}, 800)
    files["e216_inalloy_rs0.json"] = cell_payload({"inalloy1": 0.04671}, 800)
    return files


def test_an_incomplete_design_is_refused_rather_than_judged(tmp_path):
    """The fire that launched the sweep saw exactly this: one cell of sixteen, and three refusals."""
    root = write_runs(tmp_path, {"e228_rho05_cs300.json": cell_payload(
        {"real": 0.00022, "alloy1": 0.02940, "inalloy1": 0.01876, "erdos_renyi": 0.02452}, 300, 0.5)})
    cells = [e229.cell(root / "e228_rho05_cs300.json")]
    verdicts = e229.judge(cells, e229.references(root))
    assert [v["id"] for v in verdicts] == ["R1", "R2", "R3"]
    assert all("REFUSED" in v["verdict"] for v in verdicts)
    assert e229.main(["--runs", str(root)]) == 3, "the exit code is the refusal count"


def test_the_two_ratios_are_different_quantities_on_the_live_cell(tmp_path):
    """ER ÷ `real` and the top step disagree by two orders of magnitude on the registered sweep's first cell, so the
    reader has to print both and the claims have to name which one they are about."""
    root = write_runs(tmp_path, {"e228_rho05_cs300.json": cell_payload(
        {"real": 0.00022, "alloy1": 0.02940, "inalloy1": 0.01876, "erdos_renyi": 0.02452}, 300, 0.5)})
    c = e229.cell(root / "e228_rho05_cs300.json")
    assert 1.0 < c["top_step"] < 1.05 and c["er_over_real"] > 100
    assert c["top_step_by_family"]["alloy1"] < 1 < c["top_step_by_family"]["inalloy1"]


def test_the_references_are_recomputed_from_the_artifacts_not_from_the_record(tmp_path):
    """cs 800's quoted 3.02x is `inalloy1`'s spelling of the one-side level and the 2.76x is `alloy1`'s, so the
    reader computes both families separately and prints the mean as a third spelling."""
    root = write_runs(tmp_path, full_design({0.5: (0.02, 0.06), 0.99: (0.2, 0.1)},
                                            {0.5: (0.05, 0.045), 0.99: (0.05, 0.55)}))
    refs = e229.references(root)
    assert abs(refs["cs300"]["top_step"] - 1.28) < 0.02
    assert abs(refs["cs800"]["top_step_by_family"]["inalloy1"] - 3.037) < 0.01
    assert abs(refs["cs800"]["family_means"]["alloy1"] - 0.070985) < 1e-6
    assert refs["cs800_drawings"] == {"alloy1": 2, "inalloy1": 1}
    assert abs(refs["cs800"]["top_step"] - 2.411) < 0.02
    assert refs["cs800"]["top_step_by_family"]["alloy1"] < refs["cs800"]["top_step"] \
        < refs["cs800"]["top_step_by_family"]["inalloy1"]


def test_a_complete_design_is_judged_and_a_falling_top_step_meets_r2(tmp_path):
    root = write_runs(tmp_path, full_design({0.5: (0.02, 0.06), 0.99: (0.2, 0.1)},
                                            {0.5: (0.05, 0.045), 0.99: (0.05, 0.55)}))
    cells = [c for c in (e229.cell(p) for p in sorted(root.glob("e228_rho*_cs*.json"))) if c is not None]
    verdicts = {v["id"]: v["verdict"] for v in e229.judge(cells, e229.references(root))}
    assert verdicts["R1"].startswith("MET"), verdicts["R1"]
    assert verdicts["R2"].startswith("MET"), verdicts["R2"]
    assert verdicts["R3"].startswith("MET"), verdicts["R3"]
    assert e229.main(["--runs", str(root)]) == 0


def test_a_rising_top_step_fires_r2_s_falsifier_and_a_flat_one_fires_r1_s(tmp_path):
    rising = write_runs(tmp_path / "rising",
                        full_design({0.5: (0.2, 0.1), 0.99: (0.02, 0.06)},
                                    {0.5: (0.05, 0.045), 0.99: (0.05, 0.55)}))
    cells = [c for c in (e229.cell(p) for p in sorted(rising.glob("e228_rho*_cs*.json"))) if c is not None]
    v = {x["id"]: x["verdict"] for x in e229.judge(cells, e229.references(rising))}
    assert v["R2"].startswith("FALSIFIER")
    # a flat cs-300 range fires R1's falsifier, and cs-800 cells that sit ON the reference fire R3's
    flat = write_runs(tmp_path / "flat",
                      full_design({0.5: (0.02, 0.0242), 0.99: (0.02, 0.0232)},
                                  {0.5: (0.05, 0.12), 0.99: (0.05, 0.13)}))
    cells = [c for c in (e229.cell(p) for p in sorted(flat.glob("e228_rho*_cs*.json"))) if c is not None]
    v = {x["id"]: x["verdict"] for x in e229.judge(cells, e229.references(flat))}
    assert v["R1"].startswith("FALSIFIER"), v["R1"]
    assert v["R3"].startswith("FALSIFIER"), v["R3"]


def test_rho_is_read_from_the_config_and_a_missing_one_is_the_builders_default(tmp_path):
    root = write_runs(tmp_path, {"e228_rho05_cs300.json": cell_payload(
        {"real": 0.02, "alloy1": 0.03, "inalloy1": 0.03, "erdos_renyi": 0.06}, 300, 0.5),
        "e228_rhocs300.json": cell_payload({"real": 0.02, "alloy1": 0.03, "inalloy1": 0.03, "erdos_renyi": 0.06}, 300)})
    assert e229.cell(root / "e228_rho05_cs300.json")["rho"] == 0.5
    assert e229.cell(root / "e228_rhocs300.json")["rho"] == 0.9


def test_each_claim_is_refused_only_while_its_OWN_cells_are_missing(tmp_path):
    """The three claims do not need the same cells: R1 and R2 are cs-300 statements and R3 alone needs cs 800, so a
    half-finished design carries the verdicts the finished half can already support."""
    root = write_runs(tmp_path, full_design({0.5: (0.02, 0.06), 0.99: (0.2, 0.1)}, {}))
    cells = [c for c in (e229.cell(p) for p in sorted(root.glob("e228_rho*_cs*.json"))) if c is not None]
    verdicts = {v["id"]: v["verdict"] for v in e229.judge(cells, e229.references(root))}
    assert verdicts["R1"].startswith("MET") and verdicts["R2"].startswith("MET")
    assert verdicts["R3"].startswith("REFUSED") and "cs 800" in verdicts["R3"], verdicts["R3"]


def test_the_live_reader_refuses_only_the_claims_whose_cells_are_absent():
    """The live state, whatever it is: the refusal count must be the number of claims whose own grid is missing, and
    the reader must never report a verdict it cannot compute."""
    cells = [c for c in (e229.cell(p) for p in sorted(e229.RUNS.glob(e229.TEST_GLOB))) if c is not None]
    sizes = {c["circuit_size"]: {d["rho"] for d in cells if d["circuit_size"] == c["circuit_size"]}
             for c in cells}
    refs = e229.references()
    need300 = not {0.5, 0.99} <= sizes.get(300, set())
    need800 = not {0.5, 0.99} <= sizes.get(800, set())
    expected = (2 if need300 else 0) + (1 if need800 else 0)
    verdicts = e229.judge(cells, refs)
    assert sum("REFUSED" in v["verdict"] for v in verdicts) == expected, (sizes, verdicts)
    assert len(verdicts) == 3


def test_the_mechanism_cross_tab_reads_the_alignment_block_the_runner_writes(tmp_path):
    """The penalty's rho dependence against the ALIGNMENT's: both ratios are computed from the artifacts' own
    `geometry` blocks, so "the top step is the alignment contrast" is a measurement rather than an assumption."""
    payload = cell_payload({"real": 0.02, "alloy1": 0.03, "inalloy1": 0.03, "erdos_renyi": 0.06}, 300, 0.5)
    payload["topologies"]["alloy1"]["geometry"] = {"all_pairs_alignment": 0.6, "chance_alignment": 1.0}
    payload["topologies"]["inalloy1"]["geometry"] = {"all_pairs_alignment": 0.4, "chance_alignment": 1.0}
    payload["topologies"]["erdos_renyi"]["geometry"] = {"all_pairs_alignment": 2.0, "chance_alignment": 1.0}
    root = write_runs(tmp_path, {"e228_rho05_cs300.json": payload})
    rows = e229.mechanism([e229.cell(root / "e228_rho05_cs300.json")], root)
    assert len(rows) == 1
    assert rows[0]["alignment_x_chance"] == {"alloy1": 0.6, "inalloy1": 0.4, "erdos_renyi": 2.0}
    assert abs(rows[0]["one_side_alignment"] - 0.5) < 1e-12
    assert abs(rows[0]["alignment_top_step"] - 4.0) < 1e-12
    assert rows[0]["penalty_top_step"] == pytest.approx(0.06 / 0.03, rel=1e-9)


def test_a_cell_without_a_geometry_block_is_skipped_rather_than_guessed(tmp_path):
    """A cell whose artifact carries no `geometry` block cannot answer the alignment question, and the cross-tab says
    nothing about it instead of assuming a chance level of 1."""
    payload = cell_payload({"real": 0.02, "alloy1": 0.03, "inalloy1": 0.03, "erdos_renyi": 0.06}, 300, 0.5)
    root = write_runs(tmp_path, {"e228_rho05_cs300.json": payload})
    assert e229.mechanism([e229.cell(root / "e228_rho05_cs300.json")], root) == []
