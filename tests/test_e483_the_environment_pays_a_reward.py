"""`e483` gives the environment a reward, so the tests pin both faces of the four claims, the draw fields the flag
leaves alone, and the refusal when the replicates were not rolled.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e483_the_environment_pays_a_reward as e483

FIELDS = e483.DRAW_FIELDS
REPS = (0, 1, 2, 3)


def _cell(seed=0, across=1.67, within=0.90, identity=-3.0, trained=-0.80, target_spread=0.50, late_max=0.0,
          reward_sha1="abc", draw=None):
    return {"seed": seed, "draw_agrees": dict(draw if draw is not None else {k: True for k in FIELDS}),
            "reward_sha1": reward_sha1, "per_symbol": [0.0] * 4, "within": within, "across": across,
            "target_spread": target_spread, "late_target_max": late_max, "late_reward": -3.0,
            "identity": identity, "with_none": identity, "trained": trained, "move": 5.0}


def _doc(cells=None, ok=True, reason="the replicates were not rolled"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "spreads": {}, "payout": {}, "spans": {}, "worlds": {}}
    cells = cells if cells is not None else [_cell(seed=s, across=1.60 + 0.05 * s, within=0.90 + 0.02 * s,
                                                   identity=-3.0 - 0.05 * s, trained=-0.80 - 0.03 * s,
                                                   target_spread=0.50 + 0.01 * s) for s in REPS]
    return {"ok": True, "reason": None, "cells": cells, "worlds": {"chance": 0.25},
            "spreads": e483._paired([c["across"] for c in cells], [c["within"] for c in cells]),
            "payout": e483._paired([c["trained"] for c in cells], [c["identity"] for c in cells]),
            "spans": {"replicates": len(cells), "fields": len(FIELDS),
                      "draw_agrees": {k: all(c["draw_agrees"][k] for c in cells) for k in FIELDS},
                      "draw_differ": sorted(k for k in FIELDS if not all(c["draw_agrees"][k] for c in cells)),
                      "reward_sha1": [c["reward_sha1"] for c in cells],
                      "across": [round(c["across"], 4) for c in cells],
                      "within": [round(c["within"], 4) for c in cells],
                      "target_spread_min": min(c["target_spread"] for c in cells),
                      "late_target_max": max(c["late_target_max"] for c in cells),
                      "late_reward": [c["late_reward"] for c in cells],
                      "identity": [c["identity"] for c in cells],
                      "with_none": [c["with_none"] for c in cells],
                      "moves": [c["move"] for c in cells]}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e483.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: the flag draws only the payout, the cue separates the payout, a policy earns more, and the goal is
    #: the cue's read one step after it arrives
    j = _judge()
    for cid in ("RA1", "RA2", "RA3", "RA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # RA1: a draw field the flag moved, and a payout whose map was not recorded
    assert _judge(cells=[_cell(seed=s, draw={**{k: True for k in FIELDS}, "world_sha1": False})
                         for s in REPS])["RA1"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, reward_sha1=None) for s in REPS])["RA1"].startswith("FALSIFIER")

    # RA2: a replicate whose across-symbol spread does not exceed the within-symbol one
    assert _judge(cells=[_cell(seed=s, across=0.5 if s == 2 else 1.60 + 0.05 * s) for s in REPS])["RA2"].startswith(
        "FALSIFIER")

    # RA3: a payout that is not earned, and one between the floor and the bar
    assert _judge(cells=[_cell(seed=s, trained=-2.7 - 0.05 * s) for s in REPS])["RA3"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, trained=-2.4 + 0.12 * s, identity=-3.0) for s in REPS])["RA3"].startswith("NULL")
    assert _judge(cells=[_cell(seed=s, trained=-0.4 - 0.05 * s, identity=-3.0) for s in REPS])["RA3"].startswith("MET")

    # RA4: a target that is not at rest at the read step, and one with no cue spread at the first step
    assert _judge(cells=[_cell(seed=s, late_max=1e-09) for s in REPS])["RA4"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, target_spread=0.0) for s in REPS])["RA4"].startswith("FALSIFIER")

    #: replicates that were not rolled refuse every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e483.judge(_doc(ok=False)))


def test_the_substrate_the_bars_and_the_flag_are_registered():
    assert (e483.SIZE, e483.READOUT_SIZE, e483.SEED) == (300, 32, 0)
    assert (e483.TAU, e483.N_SYMBOLS, e483.N_TRAIN, e483.N_HELD) == (12, 4, 512, 512)
    assert (e483.WORLD_DIMS, e483.WORLD_LEAK) == (8, 0.35)
    assert (e483.STEPS, e483.LR) == (300, 0.05)
    assert (e483.SIGMA, e483.GAIN_BAR, e483.GAIN_FLOOR) == (2.0, 2.00, 0.50)
    assert e483.REPLICATES == (0, 1, 2, 3, 4, 5, 6, 7), e483.REPLICATES
    assert "world_coupling_sha1" in FIELDS and "cue_sha1" in FIELDS, FIELDS
    #: the environment carries the field the flag draws, and it is off by default
    import dataclasses
    from clfly.network.env import CueActionEnv
    fields = {f.name for f in dataclasses.fields(CueActionEnv)}
    assert "reward_map" in fields, sorted(fields)
    #: and the closure exposes the payout and the target it was scored against
    import inspect
    src = inspect.getsource(CueActionEnv.feedback)
    assert "fn.last_reward" in src and "fn.last_target" in src, "the closure does not expose the payout"


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e483_the_environment_pays_a_reward.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e483.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the replicate count is structural; the counts that grow with the corpus are read as floors
    assert d["spans"]["replicates"] == len(e483.REPLICATES), d["spans"]["replicates"]
    assert len(d["cells"]) == len(e483.REPLICATES), len(d["cells"])
    assert not d["spans"]["draw_differ"], d["spans"]["draw_differ"]
    assert all(d["spans"]["reward_sha1"]), d["spans"]["reward_sha1"]
    assert d["spreads"]["n"] == d["payout"]["n"] == len(e483.REPLICATES), (d["spreads"]["n"], d["payout"]["n"])
    for c in d["cells"]:
        #: whether the cue's share beats the payout's own noise is the claim's business and the artifact's verdict is
        #: the one the judge re-derives, so what is asserted here is the shape and not the outcome
        assert c["across"] > 0.0 and c["within"] > 0.0, c
        assert c["with_none"] == c["identity"], c
        assert c["late_target_max"] == 0.0, c
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
