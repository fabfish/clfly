from __future__ import annotations

import json
from pathlib import Path

from experiments import e201_single_draw_family_census as e201


def art(path: Path, **config) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"config": config, "circuit": "mb+cx+al@n1307"}), encoding="utf-8")
    return path


def test_a_family_that_varies_a_manipulation_at_one_draw_is_single_draw(tmp_path):
    """The defect `e200` cannot see. `input_overlap` must NOT be part of the family's identity -- it is the
    manipulation -- and a first version that inferred the family from a design key put it there and then reported that
    no family varied anything."""
    d = tmp_path / "runs"
    art(d / "e900_a.json", circuit_size=800, support=80, input_overlap=0.0, seed0=0, methods="naive")
    art(d / "e900_b.json", circuit_size=800, support=80, input_overlap=0.5, seed0=0, methods="naive")
    rows = {r["family"]: r for r in e201.census(d)["families"]}
    assert rows["e900"]["varies"] == ["input_overlap"], rows["e900"]
    assert rows["e900"]["verdict"] == "SINGLE-DRAW", rows["e900"]


def test_the_same_family_across_two_support_draws_is_replicated(tmp_path):
    d = tmp_path / "runs"
    art(d / "e901_a.json", circuit_size=800, support=80, input_overlap=0.0, seed0=0, methods="naive")
    art(d / "e901_b.json", circuit_size=800, support=80, input_overlap=0.0, seed0=0, support_seed=1, methods="naive")
    rows = {r["family"]: r for r in e201.census(d)["families"]}
    # varying ONLY the draw is a DRAW ONLY family -- the design that measures a draw's own effect -- and calling it
    # "replicates" would hide the one family type that answers the question this census is about
    assert rows["e901"]["verdict"] == "DRAW ONLY", rows["e901"]
    art(d / "e901_c.json", circuit_size=800, support=80, input_overlap=0.5, seed0=0, support_seed=1, methods="naive")
    rows = {r["family"]: r for r in e201.census(d)["families"]}
    assert rows["e901"]["verdict"] == "REPLICATED ACROSS DRAWS", rows["e901"]


def test_a_rerun_under_a_different_filename_is_not_a_manipulation_family(tmp_path):
    """`json_out` is bookkeeping: a set of reruns is not a family that varies a manipulation, and counting the output
    path as one inflated the single-draw count on the census's first run."""
    d = tmp_path / "runs"
    art(d / "e902_a.json", circuit_size=800, support=80, input_overlap=0.0, seed0=0, methods="naive",
        json_out="runs/e902_a.json")
    art(d / "e902_b.json", circuit_size=800, support=80, input_overlap=0.0, seed0=0, methods="naive",
        json_out="runs/e902_b.json")
    rows = {r["family"]: r for r in e201.census(d)["families"]}
    assert rows["e902"]["varies"] == [], rows["e902"]
    assert rows["e902"]["verdict"] == "replicates", rows["e902"]


def test_the_live_census_finds_e113_varying_the_read_out_draw():
    """The census's own first catch: `e199`'s registration claimed no artifact in the record had ever been run at a
    second read-out draw, and `e113` had -- four artifacts at size 300 with `readout_seed` 1, 2 and 3. A census that
    cannot see a variation the corpus contains is not a census."""
    res = e201.census(Path("runs"))
    if not res["families"]:
        return
    fams = {r["family"]: r for r in res["families"]}
    assert "e113" in fams, sorted(fams)[:20]
    assert fams["e113"]["verdict"] == "REPLICATED ACROSS DRAWS", fams["e113"]
    assert "readout_seed" in fams["e113"]["varies"], fams["e113"]
    # and the corpus's headline exposure is reported rather than left implicit
    singles = [r for r in res["families"] if r["verdict"] == "SINGLE-DRAW"]
    assert len(singles) > 0 and sum(r["n_artifacts"] for r in singles) > 0
