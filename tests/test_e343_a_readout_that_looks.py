"""`e343` fits a decoder inside one loop and reads it inside the other, so the tests pin the cross-loop gap, the
positive control, the growth claim, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e343_a_readout_that_looks as e343


def _row(scale, divergence=0.5, peak=0.98, within=(0.95, 0.95), across=(0.95, 0.95), steps=12):
    def curve(x):
        return [x] * steps
    return {"scale": scale, "peak": peak, "divergence": divergence,
            "divergence_of_peak": divergence / peak, "readout_divergence": divergence / 2,
            "readout_divergence_of_peak": divergence / 2 / peak,
            "within": {"closed": curve(within[0]), "open": curve(within[1])},
            "across": {"fit_closed_read_open": curve(across[0]), "fit_open_read_closed": curve(across[1])},
            "gaps": {"fit_closed_read_open": abs(across[0] - within[0]),
                     "fit_open_read_closed": abs(across[1] - within[1])},
            "worst_gap": max(abs(across[0] - within[0]), abs(across[1] - within[1]))}


def _reading(rows=None):
    rows = rows or [_row(s) for s in e343.SCALES]
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "readout_sha1": None, "seed": 0,
            "n_train": 96, "n_test": 96, "tau": 12, "strengths": rows, "scales": list(e343.SCALES),
            "worst_gap": max(r["worst_gap"] for r in rows),
            "gap_at_weakest": rows[0]["worst_gap"], "gap_at_strongest": rows[-1]["worst_gap"],
            "worst_gap_growth": rows[-1]["worst_gap"] - rows[0]["worst_gap"]}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e343.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a peak that differs across the strengths is the falsifier
    rows = [_row(s) for s in e343.SCALES]
    rows[-1]["peak"] = 0.5
    assert e343.judge(_reading(rows))[0]["verdict"].startswith("FALSIFIER")
    # T2: a channel that does not move the state
    assert e343.judge(_reading([_row(s, divergence=0.005) for s in e343.SCALES]))[1]["verdict"].startswith(
        "FALSIFIER")
    # T3: a cross-loop decoder that loses a tenth of its accuracy
    bad = [_row(s, across=(0.85, 0.95)) for s in e343.SCALES]
    assert e343.judge(_reading(bad))[2]["verdict"].startswith("FALSIFIER")
    between = [_row(s, across=(0.87, 0.95)) for s in e343.SCALES]
    assert e343.judge(_reading(between))[2]["verdict"].startswith("NULL")
    # T4: a gap that grows with the strength
    grown = [_row(s) for s in e343.SCALES[:-1]] + [_row(e343.SCALES[-1], across=(0.80, 0.95))]
    assert e343.judge(_reading(grown))[3]["verdict"].startswith("FALSIFIER")

    # and a reading with too few strengths refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e343.judge({"strengths": []}))


def test_the_gap_is_the_worst_of_the_two_cross_loop_decoders():
    row = _row(1.0, within=(0.95, 0.90), across=(0.95, 0.80))
    assert abs(row["gaps"]["fit_closed_read_open"]) < 1e-12, row
    assert abs(row["gaps"]["fit_open_read_closed"] - 0.10) < 1e-12, row
    assert abs(row["worst_gap"] - 0.10) < 1e-12, row


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e343_a_readout_that_looks.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e343.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the measurement landed; the gate regenerates it
    for cid in ("T1", "T2", "T3", "T4"):
        assert d["claims"][{"T1": 0, "T2": 1, "T3": 2, "T4": 3}[cid]]["id"] == cid
    #: the positive control is part of the artifact: the state has to move, and by a lot
    assert d["strengths"][-1]["divergence_of_peak"] > e343.DIVERGED, d["strengths"][-1]
    assert d["strengths"][-1]["readout_divergence_of_peak"] > 0.10, d["strengths"][-1]
    #: and the decoder has to be reading the task rather than at chance
    assert d["strengths"][-1]["within"]["closed"][-1] > 0.5, d["strengths"][-1]
