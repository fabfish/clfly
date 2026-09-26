"""`e259` turns `e76`'s floors into the statement a null needs, so the tests pin the arithmetic (the sigma a published
effect would have had, the replicates it would need), each verdict of P1 (the 2.5-sigma bar), P2 (the 20x spread) and
P3 (the pattern of implied sigmas), and the live artifact.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from experiments import e259_c2b_null_power as e259


def rows_of(side: float, cell_class: float, cross: float) -> list[dict]:
    """A table with the three figures' sems set, the published effects taken from e76's own constants."""
    sems = {"side": side, "cell_class": cell_class, "side - cell_class": cross}
    out = []
    for name, (effect, published) in e259.PUBLISHED_3REP.items():
        s16 = sems[name]
        out.append({"figure": name, "published_effect": effect, "published_sigma": published, "sem_16": s16,
                    "implied_sigma_at_16": abs(effect) / s16,
                    "replicates_needed_2sigma": 64 * s16 ** 2 / effect ** 2, "floor_at_16": 2 * s16,
                    "floors": {n: 2 * s16 * math.sqrt(16 / n) for n in e259.NS}})
    return out


def test_the_arithmetic_of_the_sigma_and_the_replicates_needed():
    r = {x["figure"]: x for x in rows_of(0.01278, 0.01615, 0.02161)}
    assert abs(r["side - cell_class"]["implied_sigma_at_16"] - 0.0718 / 0.02161) < 1e-9
    assert abs(r["side - cell_class"]["replicates_needed_2sigma"] - 64 * 0.02161 ** 2 / 0.0718 ** 2) < 1e-9
    # a bigger sem needs more replicates for the same effect, and the floor shrinks as 1/sqrt(n)
    assert r["side"]["floors"][3] > r["side"]["floors"][16] > r["side"]["floors"][40]
    assert abs(r["side"]["floors"][16] - 2 * 0.01278) < 1e-12


def test_P1_is_MET_when_the_published_effect_would_have_shown_and_fires_when_it_would_not():
    met = {r["id"]: r for r in e259.judge(rows_of(0.01278, 0.01615, 0.02161))}
    assert met["P1"]["verdict"].startswith("MET"), met["P1"]
    assert "3.32 sigma" in met["P1"]["measured"], met["P1"]
    fired = {r["id"]: r for r in e259.judge(rows_of(0.01278, 0.01615, 0.05))}
    assert fired["P1"]["verdict"].startswith("FALSIFIER FIRED"), fired["P1"]
    band = {r["id"]: r for r in e259.judge(rows_of(0.01278, 0.01615, 0.033))}
    assert band["P1"]["verdict"].startswith("null band"), band["P1"]


def test_P2_reads_the_spread_of_the_replicates_the_three_claims_would_need():
    rows = {r["id"]: r for r in e259.judge(rows_of(0.01278, 0.01615, 0.02161))}
    assert rows["P2"]["verdict"].startswith("MET"), rows["P2"]
    assert "a 55x spread" in rows["P2"]["measured"], rows["P2"]
    # three claims of the SAME detectability need the falsifier: equal replicates means sem proportional to effect
    even = {r["id"]: r for r in e259.judge(rows_of(0.0069, 0.0648, 0.0718))}
    assert even["P2"]["verdict"].startswith("FALSIFIER FIRED"), even["P2"]
    assert "a 1x spread" in even["P2"]["measured"], even["P2"]


def test_P3_needs_one_claim_never_detectable_and_two_excluded_at_three_sigma():
    rows = {r["id"]: r for r in e259.judge(rows_of(0.01278, 0.01615, 0.02161))}
    assert rows["P3"]["verdict"].startswith("MET"), rows["P3"]
    assert "side 0.54" in rows["P3"]["measured"] and "4.01" in rows["P3"]["measured"], rows["P3"]
    # a side sem small enough to make its claim detectable at 16 flips the pattern
    flipped = {r["id"]: r for r in e259.judge(rows_of(0.004, 0.01615, 0.02161))}
    assert flipped["P3"]["verdict"].startswith("FALSIFIER FIRED"), flipped["P3"]


def test_a_missing_artifact_refuses():
    import experiments.e259_c2b_null_power as mod
    saved = mod.ARTIFACT
    try:
        mod.ARTIFACT = Path("runs/does-not-exist-e259.json")
        assert mod.table() == []
        rows = {r["id"]: r for r in mod.judge([])}
        for cid in ("P1", "P2", "P3"):
            assert rows[cid]["verdict"].startswith("REFUSED"), rows[cid]
    finally:
        mod.ARTIFACT = saved


def test_the_live_artifact_states_what_the_null_rules_out():
    """The finding's numbers on the artifact: the three figures' implied sigmas, the 219.5 / 4.0 / 5.8 replicates, and
    the 55x spread."""
    p = Path("runs/e259_c2b_null_power.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    by = {r["figure"]: r for r in d["figures"]}
    assert set(by) == {"side", "cell_class", "side - cell_class"}, sorted(by)
    assert abs(by["side"]["replicates_needed_2sigma"] - 219.5) < 0.5, by["side"]
    assert abs(by["cell_class"]["replicates_needed_2sigma"] - 4.0) < 0.1, by["cell_class"]
    assert abs(by["side - cell_class"]["implied_sigma_at_16"] - 3.32) < 0.01, by["side - cell_class"]
    assert abs(by["side"]["implied_sigma_at_16"] - 0.54) < 0.01, by["side"]
    rows = {r["id"]: r for r in d["claims"]}
    for cid in ("P1", "P2", "P3"):
        assert rows[cid]["verdict"].startswith("MET"), rows[cid]
    assert "55x" in rows["P2"]["measured"], rows["P2"]
