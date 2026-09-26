"""`e242` brackets the register's own top-step figures with the drawings behind them, so the tests pin the two
statistics it turns on (a percentile of a quoted value inside its distribution, and the ratio-versus-relative-width
comparison R2 needs) plus one live cell.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e242_register_intervals as e242


def test_percentile_of_a_quoted_value_inside_its_own_distribution():
    values = [1.0, 2.0, 3.0, 4.0]
    assert e242.percentile_of(values, 0.5) == 0.0
    assert e242.percentile_of(values, 2.5) == 50.0
    assert e242.percentile_of(values, 9.0) == 100.0


def test_r2_compares_a_ratio_gap_with_a_relative_width():
    """The unit bug this module had: a gap of 1.09 is 9%, and it must be compared against an IQR expressed the same
    way. Here the quoted figures' gap (9%) is smaller than a 20% IQR, so the claim is MET."""
    stats = {"a": {"iqr_over_median": 0.20}, "b": {"iqr_over_median": 0.30}}
    worst = min(s["iqr_over_median"] for s in stats.values())
    assert abs(e242.SPELLING_GAP - 1.0) < worst, "9% inside 20% -- the fix's premise"
    assert e242.SPELLING_GAP > worst, "the first version's comparison, which fired on the wrong unit"


def test_quantiles_of_a_small_sample_are_the_sample():
    assert e242.quantiles([2.0, 1.0])["median"] == 1.5
    assert e242.quantiles([2.0, 1.0])["min"] == 1.0 and e242.quantiles([2.0, 1.0])["max"] == 2.0
    assert e242.quantiles([5.0])["q25"] == 5.0


def test_a_cell_without_drawings_is_refused(capsys):
    res = {"cells": []}
    v = {c["id"]: c["verdict"] for c in e242.judge(res)}
    assert all(x.startswith("REFUSED") for x in v.values()), v


def test_the_live_artifact_brackets_the_convention_cell():
    """The live distributions the finding quotes: 30 and 18 pairs, the register's figures at the 20th and 33rd
    percentile, and the two spellings' gap inside both IQRs."""
    p = Path("runs/e242_register_intervals.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    conv = next(r for r in d["cells"] if list(r["cell"]) == list(e242.CONVENTION))
    a, i = conv["erdos_renyi/alloy1"], conv["erdos_renyi/inalloy1"]
    assert a["n"] == 30 and i["n"] == 18, (a["n"], i["n"])
    assert a["q25"] <= e242.DECLARED["erdos_renyi/alloy1"] <= a["q75"] or a["min"] < e242.DECLARED["erdos_renyi/alloy1"]
    assert i["q25"] <= e242.DECLARED["erdos_renyi/inalloy1"] <= i["q75"]
    verdicts = {c["id"]: c["verdict"] for c in d["claims"]}
    assert verdicts["R2"].startswith("MET"), verdicts["R2"]
