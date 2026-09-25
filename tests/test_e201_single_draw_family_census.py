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


def test_the_linear_lines_draws_are_seed0_seeds_and_control_draws(tmp_path):
    """The correction this census needed. The LINEAR line has none of the network line's draw flags: `e3` builds its
    tasks with `build_tasks(..., seed=seed)` for `seed in range(seed0, seed0 + seeds)` -- verified on the real line by
    three distinct `Sigma` matrices at seeds 0, 1 and 2 -- and draws its controls from `default_rng(seed0)` averaging
    `control_draws` of them. Reading only `readout_seed`/`support_seed`/`partition_seed` called a 12-seed ladder
    "single-draw"."""
    d = tmp_path / "runs"
    # a linear family varying the TASK DRAW (seeds) is a draw-replicated family
    art(d / "e903_a.json", circuit_size=1500, support=150, q=0.02, seed0=0, seeds=3, k=13, shape="flat", draws=5)
    art(d / "e903_b.json", circuit_size=1500, support=150, q=0.02, seed0=0, seeds=12, k=13, shape="flat", draws=5)
    rows = {r["family"]: r for r in e201.census(d)["families"]}
    assert rows["e903"]["verdict"] == "REPLICATED ACROSS DRAWS", rows["e903"]
    # and a linear family holding the task draw fixed but AVERAGING five of them reports the averaging
    d2 = tmp_path / "runs2"
    art(d2 / "e904_a.json", circuit_size=1500, support=150, q=0.02, seed0=0, seeds=3, k=13, shape="flat", draws=5)
    art(d2 / "e904_b.json", circuit_size=1500, support=150, q=0.02, seed0=0, seeds=3, k=8, shape="flat", draws=5)
    rows2 = {r["family"]: r for r in e201.census(d2)["families"]}
    assert rows2["e904"]["verdict"] == "SINGLE-DRAW", rows2["e904"]
    assert rows2["e904"]["averaging"] == ["seeds=3, draws=5"], rows2["e904"]["averaging"]
    # `--repeats` is NOT a draw average: the network line runs its replicas at ONE draw
    d3 = tmp_path / "runs3"
    art(d3 / "e905_a.json", circuit_size=800, readout_size=32, seed0=0, repeats=5, methods="naive")
    art(d3 / "e905_b.json", circuit_size=800, readout_size=32, seed0=0, repeats=40, methods="naive")
    rows3 = {r["family"]: r for r in e201.census(d3)["families"]}
    assert rows3["e905"]["averaging"] == [], rows3["e905"]["averaging"]


def test_the_null_model_rewiring_is_a_draw_and_not_a_manipulation(tmp_path):
    """`rewire_seed` chooses the rewiring a topology control is built from, so a family that varies it is measuring a
    DRAW -- and the corpus carries it in 26 artifacts (`e32`/`e33`/`e65`). A handwritten field list omitted it, which
    made those families look like "replicates" and hid the one family type that answers this census's question; and
    the fix has to reach `draw_keys` too, since a field in the list but not in the tuple leaves len(draws) == 1."""
    d = tmp_path / "runs"
    art(d / "e906_a.json", circuit_size=800, support=80, rewire_seed=0, topology="shuffled")
    art(d / "e906_b.json", circuit_size=800, support=80, rewire_seed=1, topology="shuffled")
    rows = {r["family"]: r for r in e201.census(d)["families"]}
    assert rows["e906"]["verdict"] == "DRAW ONLY", rows["e906"]
    assert "rewire_seed" in rows["e906"]["varies"], rows["e906"]
    assert set(e201.draw_keys(json.loads((d / "e906_a.json").read_text(encoding="utf-8")))) != \
        set(e201.draw_keys(json.loads((d / "e906_b.json").read_text(encoding="utf-8")))), \
        "the rewire component must reach draw_keys, not only the field list"


def test_a_key_holding_a_path_string_is_not_a_draw(tmp_path):
    """The rule over the corpus's vocabulary has to exclude `matching_seeds`, which is a path and not a seed."""
    d = tmp_path / "runs"
    art(d / "e907_a.json", circuit_size=800, matching_seeds="runs/e116_a.json")
    art(d / "e907_b.json", circuit_size=800, matching_seeds="runs/e116_b.json")
    res = e201.census(d)
    rows = {r["family"]: r for r in res["families"]}
    # it IS a difference between the two artifacts, and it counts as a DESIGN input rather than a draw
    assert "matching_seeds" in rows["e907"]["manipulations"], rows["e907"]
    assert "matching_seeds" not in res["draw_fields"], res["draw_fields"]
    assert res["draw_fields"] == [], "the only seed-like key here holds a path, so this corpus has no draw field"


def test_the_live_census_names_the_families_that_deliberately_measure_a_draw():
    """The four DRAW ONLY families are the corpus's own draw measurements -- the rewiring's (`e32`/`e33`/`e65`) and the
    read-out's (`e117`) -- and a reader asking "has this draw ever been varied?" can now read the answer off the
    census instead of believing a claim like the one `e199`'s registration got wrong."""
    res = e201.census(Path("runs"))
    if not res["families"]:
        return
    only = {r["family"] for r in res["families"] if r["verdict"] == "DRAW ONLY"}
    assert {"e32", "e33", "e65", "e117"} <= only, (only, "e32/e33/e65 vary rewire_seed and e117 varies readout_seed")
    singles = [r for r in res["families"] if r["verdict"] == "SINGLE-DRAW"]
    assert sum(r["n_artifacts"] for r in singles) == 187, sum(r["n_artifacts"] for r in singles)
    # the rule is derived from the corpus's own vocabulary, and on the real corpus it names exactly six keys --
    # including the two a handwritten list was missing
    assert set(res["draw_fields"]) == {"readout_seed", "support_seed", "partition_seed", "rewire_seed",
                                       "seed_b", "seed_step"}, res["draw_fields"]
