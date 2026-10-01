"""`e345` asks whether a wider read-out sees the channel, so the tests pin the per-width arithmetic (the divergence
on the decoder's own neurons and the four decoders' gap), the nesting T1 rests on, and both faces of the claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e345_a_wider_readout as e345


def _reading(widths=(2, 6), case="nil", n=16, tau=2, N=6):
    """A synthetic roll: neuron 0 carries the label at the last step, and `case` says what the loop does to it."""
    rng = np.random.default_rng(0)
    y = np.arange(n) % 2
    open_ = rng.standard_normal((n, tau, N)) * 0.05
    open_[:, -1, 0] = np.where(y == 1, 1.0, -1.0)
    closed = open_.copy()
    if case == "nil":
        #: the loop rewrites a neuron the label does not use, so the state moves and the decisions do not
        closed[:, -1, 5] += 0.5
    elif case == "sees":
        #: and here it rewrites the label's own neuron, which is what a decoder that can see it would notice
        closed[:, -1, 0] = 0.0
    elif case == "flat":
        closed = open_.copy()               # no divergence at all, which is T2's falsifier
    peak = float(np.max(np.abs(open_))) or 1.0
    rows = [e345.one_width(closed, closed, open_, open_, y, y, np.arange(w), peak) for w in widths]
    return _top(widths, rows, max(r["divergence_of_peak"] for r in rows), max(widths), N, n)


def _from_gaps(widths, gaps, divergence=0.5, N=6, n=16):
    """A reading with the per-width gaps set by hand, so T3's and T4's branches can be read off directly."""
    rows = [{"width": w, "divergence_of_peak": divergence, "mean_divergence_of_peak": 0.0,
             "within": {"closed": [0.8], "open": [0.8]},
             "across": {"fit_closed_read_open": [0.8], "fit_open_read_closed": [0.8]},
             "gaps": {"fit_closed_read_open": g, "fit_open_read_closed": 0.0}, "worst_gap": g}
            for w, g in zip(widths, gaps)]
    return _top(widths, rows, divergence, max(widths), N, n)


def _top(widths, rows, divergence, draw_size, N, n):
    return {"circuit": "test", "size": N, "scale": 1.0, "world_leak": 0.35, "world_modes": 2, "n_symbols": 2,
            "n_train": n, "n_test": n, "widths": list(widths), "draw_size": draw_size,
            "readouts": rows, "concentration": {}, "divergence_of_peak": divergence,
            "worst_gap": max(r["worst_gap"] for r in rows),
            "gap_at_narrowest": rows[0]["worst_gap"], "gap_at_widest": rows[-1]["worst_gap"],
            "worst_gap_growth": rows[-1]["worst_gap"] - rows[0]["worst_gap"]}


def _judge(r):
    return {row["id"]: row for row in e345.judge(r)}


def test_the_positive_control_and_the_nesting():
    #: the loop rewrites a neuron the label does not use: the state moves and no decision moves
    nil = _judge(_reading(case="nil"))
    for cid in ("T1", "T2", "T3", "T4"):
        assert nil[cid]["verdict"].startswith("MET"), nil[cid]
    assert "50.00%" in nil["T2"]["measured"], nil["T2"]

    #: and here it rewrites the label's own neuron, which is what a decoder that can see it would notice
    sees = _judge(_reading(case="sees"))
    assert sees["T3"]["verdict"].startswith("FALSIFIER"), sees["T3"]

    #: a loop that changes nothing is T2's falsifier
    flat = _judge(_reading(case="flat"))
    assert flat["T2"]["verdict"].startswith("FALSIFIER"), flat["T2"]
    assert flat["T3"]["verdict"].startswith("MET"), flat["T3"]

    #: T1: widths that are not increasing are not a nested ladder
    not_nested = _judge(_reading(widths=(6, 2)))
    assert not_nested["T1"]["verdict"].startswith("FALSIFIER"), not_nested["T1"]
    #: and a single width refuses every claim
    one = _reading(widths=(6,))
    assert all(row["verdict"].startswith("REFUSED") for row in e345.judge(one)), e345.judge(one)


def test_the_gap_branches():
    for gaps, t3, t4 in (((0.0, 0.01), "MET", "MET"),
                         ((0.02, 0.03), "MET", "MET"),
                         ((0.0, 0.07), "NULL", "NULL"),
                         ((0.0, 0.20), "FALSIFIER", "FALSIFIER")):
        j = _judge(_from_gaps((8, 512), gaps))
        assert j["T3"]["verdict"].startswith(t3), (gaps, j["T3"])
        assert j["T4"]["verdict"].startswith(t4), (gaps, j["T4"])
    #: T3's window is on the worst width and T4's growth is widest minus narrowest
    j = _judge(_from_gaps((8, 128, 512), (0.0, 0.0, 0.06)))
    assert j["T3"]["verdict"].startswith("NULL"), j["T3"]
    assert j["T4"]["verdict"].startswith("NULL"), j["T4"]


def test_the_width_reads_the_divergence_on_its_own_neurons():
    r = _reading(widths=(1, 6), case="nil")
    narrow, wide = r["readouts"]
    assert narrow["width"] == 1 and wide["width"] == 6, r["readouts"]
    #: the perturbation lives on neuron 5, so the one-neuron decoder sees only the label and no divergence
    assert narrow["divergence_of_peak"] < 0.02, narrow["divergence_of_peak"]
    assert wide["divergence_of_peak"] > 0.4, wide["divergence_of_peak"]
    #: the gap is the distance from a cross-loop decoder to the accuracy it had in its own loop, at the last step
    for row in r["readouts"]:
        assert row["worst_gap"] == max(row["gaps"].values()), row


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e345_a_wider_readout.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e345.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the measurement landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the ladder is nested and the decoder's own inputs move with it
    assert [row["width"] for row in d["readouts"]] == d["widths"], d["readouts"]
    assert d["readouts"][0]["divergence_of_peak"] < d["readouts"][-1]["divergence_of_peak"], d["readouts"]
    assert d["divergence_of_peak"] >= d["readouts"][-1]["divergence_of_peak"], d
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
