"""`e484` sweeps the cue's noise under the payout's cue-share, so the tests pin both faces of the four claims, the
draw fields the sweep leaves alone, and the refusal when the ladder was not walked.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e484_the_cues_noise_on_the_payouts_share as e484

LEVELS = [e484.key(n) for n in e484.NOISES]
REPS = (0, 1, 2, 3)
#: the quiet level separates the payout and the corpus's own does not, which is the shape the claims read
SPEC = {"0": (2.60, 0.90, -3.0, -1.40), "0.25": (2.20, 1.10, -3.1, -1.70), "0.5": (1.90, 1.30, -3.2, -2.00),
        "1": (1.60, 1.55, -3.3, -2.30), "2": (1.40, 1.80, -3.4, -2.60)}


def _cells(k, across=None, within=None, identity=None, trained=None, draw=None):
    a0, w0, i0, t0 = SPEC[k]
    out = []
    for s in REPS:
        a, w = (a0 if across is None else across) + 0.03 * s, (w0 if within is None else within) + 0.02 * s
        i, t = (i0 if identity is None else identity) - 0.05 * s, (t0 if trained is None else trained) - 0.03 * s
        out.append({"seed": s, "draw_agrees": dict(draw if draw is not None else
                                                   {f: True for f in e484.e483.DRAW_FIELDS}),
                    "reward_sha1": "abc", "per_symbol": [0.0] * 4, "within": w, "across": a,
                    "target_spread": 0.50, "late_target_max": 0.0, "late_reward": 0.0,
                    "identity": i, "with_none": i, "trained": t, "move": 5.0})
    return out


def _doc(cells=None, pair=None, ok=True, reason="the ladder was not walked"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": {}, "margin": {}, "gain": {}, "levels": {}, "spans": {},
                "pair": {}}
    cells = cells if cells is not None else {k: _cells(k) for k in LEVELS}
    fields = e484.e483.DRAW_FIELDS
    within_differ = {k: sorted({f for c in v for f, okk in c["draw_agrees"].items() if not okk})
                     for k, v in cells.items()}
    within_differ = {k: v for k, v in within_differ.items() if v}
    cross = sorted({f for f in fields
                    if len({tuple(c["draw_agrees"][f] for c in cells[k]) for k in LEVELS}) > 1})
    one = all(len({cells[k][i]["reward_sha1"] for k in LEVELS}) == 1 for i in range(len(REPS)))
    margin = {k: e484._paired([c["across"] for c in cells[k]], [c["within"] for c in cells[k]]) for k in LEVELS}
    gain = {k: e484._paired([c["trained"] for c in cells[k]], [c["identity"] for c in cells[k]]) for k in LEVELS}
    pair = pair if pair is not None else e484._paired(
        [c["across"] - c["within"] for c in cells[LEVELS[0]]],
        [c["across"] - c["within"] for c in cells[LEVELS[-2]]])
    return {"ok": True, "reason": None, "cells": cells, "margin": margin, "gain": gain, "pair": pair,
            "worlds": {"noises": LEVELS},
            "levels": {k: {"across": [round(c["across"], 4) for c in cells[k]],
                           "within": [round(c["within"], 4) for c in cells[k]],
                           "identity": [round(c["identity"], 4) for c in cells[k]],
                           "trained": [round(c["trained"], 4) for c in cells[k]],
                           "separating": sum(1 for c in cells[k] if c["across"] > c["within"]),
                           "reward_sha1": [c["reward_sha1"] for c in cells[k]]} for k in LEVELS},
            "spans": {"levels": LEVELS, "replicates": len(REPS), "fields": len(fields),
                      "within_level_differ": within_differ, "across_level_differ": cross,
                      "reward_sha1_one_draw": one, "target_spread": {k: [0.5] for k in LEVELS},
                      "late_target_max": 0.0, "moves": {k: [5.0] for k in LEVELS}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e484.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: the sweep moves only the level, a quiet cue carries more, it separates everywhere, and the payout
    #: is still earned
    j = _judge()
    for cid in ("SA1", "SA2", "SA3", "SA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # SA1: a draw field differing within a level, one differing across levels, and a payout map redrawn
    assert _judge(cells={k: _cells(k, draw={**{f: True for f in e484.e483.DRAW_FIELDS}, "world_sha1": False})
                         for k in LEVELS})["SA1"].startswith("FALSIFIER")
    redrawn = {k: _cells(k) for k in LEVELS}
    for i in range(len(REPS)):
        redrawn[LEVELS[-1]][i]["reward_sha1"] = f"other{i}"
    assert _judge(cells=redrawn)["SA1"].startswith("FALSIFIER")

    # SA2: a quiet cue that carries no more than the corpus's own, and one between the bands
    assert _judge(pair={"n": len(REPS), "mean": 0.20, "sd": 0.05, "se": 0.03, "sigma": 6.0})["SA2"].startswith(
        "FALSIFIER")
    assert _judge(pair={"n": len(REPS), "mean": 0.70, "sd": 0.05, "se": 0.03, "sigma": 6.0})["SA2"].startswith("NULL")
    #: an unresolved gap fires it whatever its size
    assert _judge(pair={"n": len(REPS), "mean": 1.50, "sd": 0.05, "se": 0.03, "sigma": 1.20})["SA2"].startswith(
        "FALSIFIER")

    # SA3: a quiet level with one replicate that does not separate them
    assert _judge(cells={**{k: _cells(k) for k in LEVELS[1:]},
                         LEVELS[0]: [dict(_cells(LEVELS[0])[0], across=0.5, within=2.0)] + _cells(LEVELS[0])[1:]}
                  )["SA3"].startswith("FALSIFIER")

    # SA4: a payout that is not earned at the quiet level, and one between the floor and the bar
    assert _judge(cells={**{k: _cells(k) for k in LEVELS[1:]},
                         LEVELS[0]: _cells(LEVELS[0], identity=-3.0, trained=-2.9)}
                  )["SA4"].startswith("FALSIFIER")
    assert _judge(cells={**{k: _cells(k) for k in LEVELS[1:]},
                         LEVELS[0]: _cells(LEVELS[0], identity=-3.0, trained=-2.4)}
                  )["SA4"].startswith("NULL")
    assert _judge(cells={**{k: _cells(k) for k in LEVELS[1:]},
                         LEVELS[0]: _cells(LEVELS[0], identity=-3.0, trained=-1.4)}
                  )["SA4"].startswith("MET")

    #: a ladder that was not walked refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e484.judge(_doc(ok=False)))


def test_the_ladder_the_bars_and_the_reused_replicate_are_registered():
    assert e484.NOISES == (0.0, 0.25, 0.5, 1.0, 2.0), e484.NOISES
    assert (e484.QUIET, e484.CORPUS) == (0.0, 1.0)
    assert (e484.SIGMA, e484.MARGIN_BAR, e484.MARGIN_FLOOR) == (2.0, 1.00, 0.50)
    assert (e484.GAIN_BAR, e484.GAIN_FLOOR) == (1.00, 0.30)
    assert e484.REPLICATES == (0, 1, 2, 3, 4, 5, 6, 7), e484.REPLICATES
    #: the replicate this ladder drives is e483's own, and the cue's noise is a parameter of it
    import inspect
    from experiments import e483_the_environment_pays_a_reward as e483m
    sig = inspect.signature(e483m.one_replicate)
    assert "noise" in sig.parameters, sorted(sig.parameters)
    assert sig.parameters["noise"].default == e483m.NOISE == 1.0, sig.parameters["noise"]


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e484_the_cues_noise_on_the_payouts_share.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e484.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    keys = [e484.key(n) for n in e484.NOISES]
    assert d["spans"]["levels"] == keys, d["spans"]["levels"]
    assert sorted(d["cells"]) == sorted(keys), sorted(d["cells"])
    assert not d["spans"]["within_level_differ"] and not d["spans"]["across_level_differ"], d["spans"]
    assert d["spans"]["reward_sha1_one_draw"] is True, d["spans"]
    for k in keys:
        assert len(d["cells"][k]) == len(e484.REPLICATES), (k, len(d["cells"][k]))
        assert d["margin"][k]["n"] == d["gain"][k]["n"] == len(e484.REPLICATES), k
        assert 0 <= d["levels"][k]["separating"] <= len(e484.REPLICATES), k
        for c in d["cells"][k]:
            assert c["with_none"] == c["identity"], c
            assert c["late_target_max"] == 0.0, c
    assert d["pair"]["n"] == len(e484.REPLICATES), d["pair"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
