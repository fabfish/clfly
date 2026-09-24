"""`e156`'s ordering statistic has to be checkable, because it is a rank correlation over ten non-independent cells.

Two failure modes worth pinning: a **rho computed over the wrong cells** (a cell missing one method must shrink
both sides of the comparison), and a **pairwise count that disagrees with the ranking without saying so** -- the
two are quoted together precisely because a near-tie can move one and not the other, so the test drives a case
where the count must move by exactly the number of reversed pairs.
"""

from __future__ import annotations

import numpy as np

from experiments import e156_channel_resolved_ordering as e156

REPS = 4


def _series(mean: float) -> np.ndarray:
    """``REPS`` values with this mean and a small deterministic wobble, so the cell mean is the control."""
    return mean + np.linspace(-0.001, 0.001, REPS)


def _cell(fg: float, wb: float) -> dict:
    return {"forgetting": _series(fg), "whole_body": _series(wb), "theta_only": _series(wb * 0.5),
            "bias_only": _series(wb * 0.5), "whole_body_task0": _series(wb), "whole_body_task1": _series(wb),
            "n": REPS}


def _spec(rows: dict[tuple[str, str], tuple[float, float]]) -> dict[str, dict[str, dict]]:
    out: dict[str, dict[str, dict]] = {}
    for (arm, method), (fg, wb) in rows.items():
        out.setdefault(arm, {})[method] = _cell(fg, wb)
    return out


#: six cells whose whole-body term is strictly ordered the same way as their forgetting
ORDERED = {
    ("plastic", "replay"): (0.00, 0.10), ("frozen", "replay"): (0.01, 0.15),
    ("frozen", "ewc"): (0.04, 0.20), ("plastic", "ewc"): (0.05, 0.30),
    ("frozen", "naive"): (0.09, 0.40), ("plastic", "naive"): (0.10, 0.50),
}


def test_a_perfectly_ordered_set_gives_rho_one_and_every_pair_agreeing():
    r = e156.ordering(_spec(ORDERED), "whole_body")
    assert len(r["cells"]) == 6
    assert r["pairs_total"] == 15 and r["pairs_agreeing"] == 15
    assert abs(r["rho"] - 1.0) < 1e-9


def test_one_reversal_moves_both_statistics_and_the_count_by_the_reversed_pair_count():
    # `frozen/replay` gets the WORST forgetting while keeping the second-smallest form: it reverses against the
    # four cells whose forgetting it now exceeds (ewc x2, naive x2) and against none of the others.
    perturbed = dict(ORDERED)
    perturbed[("frozen", "replay")] = (0.11, 0.15)
    r = e156.ordering(_spec(perturbed), "whole_body")
    assert r["pairs_agreeing"] == 15 - 4
    assert r["rho"] < 1.0


def test_a_missing_method_shrinks_BOTH_sides_of_the_comparison():
    cells = _spec(ORDERED)
    del cells["frozen"]["replay"]
    r = e156.ordering(cells, "whole_body")
    assert len(r["cells"]) == 5
    assert r["pairs_total"] == 10          # C(5,2), not C(6,2)
    assert "frozen/replay" not in r["cells"]


def test_the_real_registries_resolve_and_the_ten_cells_are_all_there():
    from pathlib import Path
    assert all(Path(p).is_file() for p in e156.ARMS.values()), "a registry artifact is not on disk"
    loaded = e156.load_cells()
    assert len(loaded) == 2 and all(len(v) == 5 for v in loaded.values())
    for arm in e156.ARMS:
        for method in e156.METHODS:
            assert loaded[arm][method]["n"] == 40
    # the frozen arm's bias component is structurally zero, which `e149` verified per replicate
    assert all(float(loaded["frozen"][m]["bias_only"].mean()) == 0.0 for m in e156.METHODS)
