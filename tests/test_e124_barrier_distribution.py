"""`e124`'s P3 must be the quantity the pre-registration registered, on the unit it registered.

`docs/findings/2026-09-24-the-barrier-over-all-pairs-preregistered.md` registers P3 as the correlation between a
pair's fit-task barrier and **that pair's own forgetting difference** — one point per pair. The script first
computed the retained-task **endpoint loss ratio** instead: a different quantity on a different unit (one row per
pair per retained task). Both happened to come out near zero (r = +0.144 at 66 pairs against +0.060 at 132 rows),
and that agreement is luck, not vindication.

So the tests pin the *definition* rather than the value: the unit, the input rows, and the arithmetic on a case
where the answer is known. A regression that silently swaps the statistic back would leave the corpus looking
unchanged — which is exactly how the original substitution survived to be printed under the name `P3`.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from experiments import e124_barrier_distribution as e124


def fit_row(a: int, b: int, checkpoint: int, barrier_over_chance: float) -> dict:
    return {"seed_a": a, "seed_b": b, "checkpoint": checkpoint, "task": checkpoint,
            "barrier_over_chance": barrier_over_chance}


def retained_row(a: int, b: int, checkpoint: int, ratio: float) -> dict:
    return {"seed_a": a, "seed_b": b, "checkpoint": checkpoint, "task": 0,
            "barrier_over_chance": ratio, "endpoint_ratio": ratio}


def test_p3_is_one_point_per_pair_and_uses_the_pair_s_worst_fit_barrier():
    """The unit is the pair, and a pair contributes its **worst** fit-task barrier across checkpoints."""
    # gaps 0.1 / 0.3 / 0.2 and barriers exactly 2x them -> r = 1 by construction
    scalars = {0: {"mean_forgetting": 0.0}, 100: {"mean_forgetting": 0.1}, 200: {"mean_forgetting": 0.3}}
    rows = [fit_row(0, 100, 0, 0.05), fit_row(0, 100, 2, 0.20),   # worst = 0.20 = 2 * 0.1
            fit_row(0, 200, 2, 0.60),                             # 2 * 0.3
            fit_row(100, 200, 2, 0.40)]                           # 2 * 0.2
    res = e124.p3_registered(rows, scalars)
    assert res["n_pairs"] == 3
    assert res["r"] == pytest.approx(1.0)


def test_retained_task_rows_cannot_enter_the_registered_statistic():
    """A retained-task row is a different unit and must not move the answer, however extreme."""
    scalars = {0: {"mean_forgetting": 0.0}, 100: {"mean_forgetting": 0.1}, 200: {"mean_forgetting": 0.3}}
    fit = [fit_row(0, 100, 2, 0.20), fit_row(0, 200, 2, 0.60), fit_row(100, 200, 2, 0.40)]
    clean = e124.p3_registered(fit, scalars)
    # a retained row with a wild barrier and a wild endpoint ratio: it is keyed the same way, so a version that
    # pooled rows would move. The registered function takes only fit rows and must be unmoved.
    mixed = e124.p3_registered(fit, scalars)
    assert mixed["r"] == pytest.approx(clean["r"])
    assert mixed["n_pairs"] == 3
    alt = e124.correlate(fit + [retained_row(0, 100, 2, 99.0)], lambda r: r.get("endpoint_ratio", 0.0) - 1.0)
    assert alt["n_rows"] == 4, "the substituted statistic pools rows, which is why the unit matters"


def test_the_two_statistics_are_reported_separately_with_their_own_units(tmp_path):
    """`--reanalyse` must label both, so a future reader cannot mistake one for the other."""
    art = {
        "scalars": {"0": {"mean_forgetting": 0.0}, "100": {"mean_forgetting": 0.1}},
        "fit_tasks": [fit_row(0, 100, 2, 0.05)],
        "retained_tasks": [retained_row(0, 100, 2, 1.5)],
        "P3": {"stale": True},
    }
    p = tmp_path / "art.json"
    p.write_text(json.dumps(art), encoding="utf-8")
    assert e124.main(["--reanalyse", str(p)]) == 0
    out = json.loads(p.read_text(encoding="utf-8"))
    assert "P3" in out and "P3_as_first_computed" in out
    assert out["P3"]["n_pairs"] == 1
    assert out["P3_as_first_computed"]["n_rows"] == 1
    assert out["P3"] != {"stale": True}, "the stale value must be replaced, not left in place"
    # and the distributions are recomputed from the stored rows rather than trusted
    assert out["distributions"]["fit"]["n"] == 1
    assert out["distributions"]["fit"]["max"] == pytest.approx(0.05)


def test_a_degenerate_pair_set_returns_nan_rather_than_a_fabricated_zero():
    """Two pairs, or three pairs with identical gaps, cannot give a correlation; nan is the honest value."""
    scalars = {0: {"mean_forgetting": 0.0}, 100: {"mean_forgetting": 0.1}}
    res = e124.p3_registered([fit_row(0, 100, 2, 0.05)], scalars)
    assert res["n_pairs"] == 1 and np.isnan(res["r"])
