"""`e258` gives the floor a task-draw band, so the tests pin the draw filter, the span, each verdict of W1 (the 1.05x
bar), W2 (the rise against the span) and W3 (the quoted draw's rank), and the live artifact.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e258_floor_task_draw_band as e258


def art(name: str, size: int, support: int, excess: float, rho: float | None = 0.9, topo: str = "real",
        seeds: int = 3, seed0: int = 0) -> tuple[str, dict]:
    cfg = {"circuit_size": size, "support": support, "seeds": seeds, "seed0": seed0, "q": 0.02}
    if rho is not None:
        cfg["rho"] = rho
    payload = {"config": cfg, "topologies": {topo: {"diagonal(EWC)": {"analytic": {"excess_mean": excess}}}}}
    return name, payload


def write(tmp_path: Path, files: list) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for name, payload in files:
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_the_draw_filter_takes_the_reference_rho_only_and_the_two_cells(tmp_path):
    root = write(tmp_path, [
        art("a.json", 300, 30, 0.029),
        art("b.json", 300, 30, 0.027, rho=0.5),          # a different task geometry, not another draw
        art("c.json", 300, 30, 0.026, rho=None),         # the reference by default
        art("d.json", 300, 40, 0.028),                   # a different cell
        art("e.json", 300, 30, 0.025, topo="alloy1"),    # not the floor
        art("f.json", 800, 80, 0.018),
    ])
    d = e258.draws(root)
    assert [r["artifact"] for r in d[(300, 30)]] == ["a.json", "c.json"], d[(300, 30)]
    assert [r["artifact"] for r in d[(800, 80)]] == ["f.json"], d[(800, 80)]


def test_the_span_and_the_refusal_below_three_draws():
    assert abs(e258.span([0.02, 0.03]) - 1.5) < 1e-12
    thin = {(800, 80): [{"excess": 0.018}, {"excess": 0.0185}], (300, 30): [{"excess": 0.029}]}
    rows = {r["id"]: r for r in e258.judge(thin)}
    for cid in ("W1", "W2", "W3"):
        assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    assert "fewer than three" in rows["W1"]["verdict"]


def base(lo=(0.02516, 0.02645, 0.02978), hi=(0.01739, 0.01830, 0.01902)) -> dict:
    lows = [{"artifact": f"l{i}.json", "seeds": 3, "seed0": 0, "excess": v} for i, v in enumerate(lo)]
    lows[-1]["artifact"] = e258.QUOTED_ARTIFACT          # the quoted draw, and in this fixture also the largest
    return {(800, 80): [{"artifact": f"h{i}.json", "seeds": 3, "seed0": 0, "excess": v} for i, v in enumerate(hi)],
            (300, 30): lows}


def test_W1_is_MET_when_both_floors_are_draws_and_fires_when_one_is_stable():
    rows = {r["id"]: r for r in e258.judge(base())}
    assert rows["W1"]["verdict"].startswith("MET"), rows["W1"]
    flat = base(hi=(0.0180, 0.0180, 0.0181))
    rows = {r["id"]: r for r in e258.judge(flat)}
    assert rows["W1"]["verdict"].startswith("FALSIFIER FIRED"), rows["W1"]


def test_W2_is_MET_when_the_rise_beats_the_span_and_fires_when_it_does_not():
    rows = {r["id"]: r for r in e258.judge(base())}
    assert rows["W2"]["verdict"].startswith("MET"), rows["W2"]
    assert "1.323x to 1.71" in rows["W2"]["measured"], rows["W2"]
    small = base(lo=(0.0185, 0.0190, 0.0195), hi=(0.01739, 0.01830, 0.01902))
    rows = {r["id"]: r for r in e258.judge(small)}
    assert rows["W2"]["verdict"].startswith("FALSIFIER FIRED"), rows["W2"]


def test_W3_reads_the_quoted_draw_s_rank_in_its_own_cell():
    rows = {r["id"]: r for r in e258.judge(base())}
    assert rows["W3"]["verdict"].startswith("MET"), rows["W3"]
    assert "rank 3 of 3" in rows["W3"]["measured"], rows["W3"]
    # the quoted draw is named, so a cell where it is NOT the largest has to fire
    lower = {(800, 80): base()[(800, 80)],
             (300, 30): [{"artifact": e258.QUOTED_ARTIFACT, "seeds": 3, "seed0": 0, "excess": 0.025},
                         {"artifact": "b", "seeds": 3, "seed0": 0, "excess": 0.027},
                         {"artifact": "c", "seeds": 3, "seed0": 0, "excess": 0.029},
                         {"artifact": "d", "seeds": 3, "seed0": 0, "excess": 0.031}]}
    rows = {r["id"]: r for r in e258.judge(lower)}
    assert rows["W3"]["verdict"].startswith("FALSIFIER FIRED"), rows["W3"]
    absent = {(800, 80): base()[(800, 80)], (300, 30): [{"artifact": f"x{i}", "seeds": 3, "seed0": 0,
                                                         "excess": 0.02 + 0.001 * i} for i in range(3)]}
    assert {r["id"]: r for r in e258.judge(absent)}["W3"]["verdict"].startswith("REFUSED")


def test_the_live_band_and_the_quoted_pair():
    """The finding's numbers on the artifact: 8 and 6 draws, a 1.323x to 1.713x band, and e217's draw at rank 6."""
    p = Path("runs/e258_floor_task_draw_band.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["reference_rho"] == 0.9
    assert len(d["draws"]["800/80"]) == 8 and len(d["draws"]["300/30"]) == 6, {k: len(v) for k, v in d["draws"].items()}
    rows = {r["id"]: r for r in d["claims"]}
    for cid in ("W1", "W2", "W3"):
        assert rows[cid]["verdict"].startswith("MET"), rows[cid]
    assert "1.323x to 1.71" in rows["W2"]["measured"], rows["W2"]
    assert "rank 6 of 6" in rows["W3"]["measured"], rows["W3"]
    assert "e217_ladder_cs300.json" in rows["W3"]["measured"], rows["W3"]
