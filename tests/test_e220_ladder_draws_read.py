from __future__ import annotations

import json
from pathlib import Path

from experiments import e220_ladder_draws_read as e220


def drawing(path: Path, cs: int, rs: int, alloy: float, inalloy: float, er: float) -> Path:
    """One drawing's artifact, as `--no-realized` writes it with the three levels the ratios need."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tops = {name: {"diagonal(EWC)": {"analytic": {"excess_mean": val, "excess_sem": 0.001}}}
            for name, val in (("alloy1", alloy), ("inalloy1", inalloy), ("erdos_renyi", er))}
    path.write_text(json.dumps({"config": {"circuit_size": cs, "rewire_seed": rs}, "topologies": tops}),
                    encoding="utf-8")
    return path


def size(tmp_path, cs: int, rows: list[tuple[float, float, float]]) -> None:
    for rs, (a, i, e) in enumerate(rows):
        drawing(tmp_path / f"e219_draws_cs{cs}_rs{rs}.json", cs, rs, a, i, e)


def judged(tmp_path) -> dict:
    return {r["id"]: r for r in e220.judge(e220.drawings(tmp_path))}


def test_a_size_short_of_its_three_drawings_is_refused(tmp_path):
    """Three drawings per size is the design; two is a different experiment, and the claims are stated over three."""
    assert e220.judge({})[0]["verdict"].startswith("REFUSED")
    size(tmp_path, 300, [(0.12, 0.12, 0.16), (0.14, 0.10, 0.16)])
    assert "2" in judged(tmp_path)["R1"]["verdict"]
    size(tmp_path, 300, [(0.12, 0.12, 0.16), (0.14, 0.10, 0.16), (0.13, 0.11, 0.15)])
    assert judged(tmp_path)["R1"]["verdict"] in ("MET", "null band"), judged(tmp_path)["R1"]


def test_r1_reads_the_mean_and_the_worst_drawing(tmp_path):
    """The claim has two halves -- the mean below 1.5x AND no drawing at 2.0x -- and a reader that checked only the
    mean would pass a design whose worst drawing looks like cs 800's. A worst drawing of exactly 1.5x is the
    registered NULL (one drawing between 1.5x and 2.0x) rather than a MET, because the claim's first half is the mean
    and its second is the worst."""
    size(tmp_path, 300, [(0.12, 0.12, 0.17), (0.12, 0.12, 0.17), (0.12, 0.12, 0.16)])   # 1.42/1.42/1.33 -> MET
    assert judged(tmp_path)["R1"]["verdict"].startswith("MET"), judged(tmp_path)["R1"]
    size(tmp_path, 300, [(0.12, 0.12, 0.18), (0.12, 0.12, 0.16), (0.12, 0.12, 0.16)])   # worst 1.5x -> null
    assert judged(tmp_path)["R1"]["verdict"].startswith("null band"), judged(tmp_path)["R1"]
    size(tmp_path, 300, [(0.12, 0.12, 0.26), (0.12, 0.12, 0.16), (0.12, 0.12, 0.16)])   # worst 2.17x -> falsifier
    assert "FALSIFIER" in judged(tmp_path)["R1"]["verdict"]
    size(tmp_path, 300, [(0.12, 0.12, 0.19), (0.12, 0.12, 0.18), (0.12, 0.12, 0.17)])   # mean 1.5x -> falsifier
    assert "FALSIFIER" in judged(tmp_path)["R1"]["verdict"]


def test_r2_needs_every_drawing_within_two_times(tmp_path):
    """The middle level is one level only if the two sides agree in EVERY drawing -- a mean that agrees while one
    drawing is four times apart is the mean artifact the claim's falsifier names."""
    size(tmp_path, 300, [(0.12, 0.12, 0.16), (0.14, 0.10, 0.16), (0.13, 0.11, 0.15)])
    assert judged(tmp_path)["R2"]["verdict"].startswith("MET"), judged(tmp_path)["R2"]
    size(tmp_path, 300, [(0.12, 0.12, 0.16), (0.40, 0.10, 0.16), (0.13, 0.11, 0.15)])
    assert "FALSIFIER" in judged(tmp_path)["R2"]["verdict"]


def test_each_size_is_judged_apart(tmp_path):
    """One good size cannot carry a bad one, which is why both claims are stated per size."""
    size(tmp_path, 300, [(0.12, 0.12, 0.17), (0.12, 0.12, 0.17), (0.12, 0.12, 0.17)])
    size(tmp_path, 400, [(0.12, 0.12, 0.26), (0.12, 0.12, 0.26), (0.12, 0.12, 0.26)])
    got = judged(tmp_path)
    assert got["R1"]["verdict"] == "FALSIFIER FIRED at cs 400", got["R1"]
