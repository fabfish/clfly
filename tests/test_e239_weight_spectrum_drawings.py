"""`e239` audits `e238`'s two claims across three drawings of the null, and the tests pin the audit's two halves: the
internal control that makes its movements interpretable (`real` is not rewired, so its whole-`G` rank must be
identical across drawings) and the claim thresholds it registers before looking.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e239_weight_spectrum_drawings as e239


def row(size: int, drawing: int, lam2: dict, ranks: dict) -> dict:
    return {"size": size, "drawing": drawing, "neurons": 1307 if size == 800 else 952,
            "lambda2": lam2, "rhos": {0.99: ranks, 0.95: ranks, 0.9: ranks}}


def test_w1_fires_when_a_drawing_brings_the_ratio_below_the_bar():
    """The registered bars: 4x for the rank ratio, 0.01 for the eigenvalue gap."""
    assert e239.W1_RATIO_BAR == 4.0 and e239.W2_GAP_TOLERANCE == 0.01
    rows = [row(800, 0, {"alloy1": 1.0, "inalloy1": 1.0}, {"alloy1": 29.94, "inalloy1": 1.26}),
            row(800, 1, {"alloy1": 0.7766, "inalloy1": 0.9503}, {"alloy1": 1.01, "inalloy1": 1.01})]
    v = {c["id"]: c["verdict"] for c in e239.judge(rows)}
    assert v["W1"].startswith("FALSIFIER"), v["W1"]
    assert v["W2"].startswith("FALSIFIER"), v["W2"]


def test_a_consistent_drawing_set_would_pass_both():
    rows = [row(800, d, {"alloy1": 1.0, "inalloy1": 1.0}, {"alloy1": 20.0, "inalloy1": 1.0}) for d in (0, 1, 2)]
    v = {c["id"]: c["verdict"] for c in e239.judge(rows)}
    assert v["W1"].startswith("MET") and v["W2"].startswith("MET"), v


def test_a_partial_rho_grid_is_refused_rather_than_judged():
    r = {"size": 800, "drawing": 0, "neurons": 1307, "lambda2": {"alloy1": 1.0, "inalloy1": 1.0},
         "rhos": {0.99: {"alloy1": 20.0, "inalloy1": 1.0}}}
    v = {c["id"]: c["verdict"] for c in e239.judge([r])}
    assert v["W1"].startswith("REFUSED"), v


def test_real_is_identical_across_drawings_on_the_live_substrate():
    """The audit's internal control: `real` is not rewired, so its whole-`G` rank cannot depend on the drawing. If
    this ever fails, the movement in the other families is the instrument's rather than the null's."""
    from experiments import e237_propagator_spectrum as e237

    vals = [e237.measure(300, 30, 0.99, topologies=("real",), seed0=s)["topologies"]["real"]["pr_G"]
            for s in (0, 2)]
    assert vals[0] == vals[1], vals
    p = Path("runs/e239_weight_spectrum_drawings.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    for size in (300, 800):
        seen = {r["rhos"]["0.99"]["real"] for r in d["rows"] if r["size"] == size}
        assert len(seen) == 1, (size, seen)
