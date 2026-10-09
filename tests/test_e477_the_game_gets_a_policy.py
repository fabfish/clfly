"""`e477` gives the loop a policy and trains it, so the tests pin both faces of the four claims, the library field the
policy lives on, and the refusal when the replicates were not rolled.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from experiments import e477_the_game_gets_a_policy as e477

#: the shape: the identity policy is the environment's own rule, the gradient is the loop's, and the game is playable
GAINS = (2.00, 2.20, 1.90, 2.10)
READS = (0.40, 0.45, 0.35, 0.42)


def _cell(seed=0, gain=2.0, read=0.4, init_reward=-6.9, init_read=0.50, grad_norm=0.82, fd=1.8e-4,
          identity=True, ident_max=0.0, move=12.7):
    return {"seed": seed, "n_act": 8, "identity_bitwise": identity, "identity_max_abs": ident_max,
            "grad_norm": grad_norm, "fd_worst_abs": fd, "fd_worst_at": [3, 5],
            "init_reward": init_reward, "trained_reward": init_reward + gain,
            "init_read": init_read, "trained_read": init_read + read, "policy_move": move,
            "world_sd_init": 0.20, "world_sd_trained": 0.32, "target_sha1": f"t{seed}"}


def _doc(cells=None, ok=True, reason="the replicates were not rolled"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "spans": {}, "gains": {}, "reads": {}, "worlds": {}}
    cells = cells if cells is not None else [_cell(seed=s, gain=GAINS[s % len(GAINS)], read=READS[s % len(READS)])
                                             for s in range(4)]
    gains = e477._paired([c["trained_reward"] for c in cells], [c["init_reward"] for c in cells])
    reads = e477._paired([c["trained_read"] for c in cells], [c["init_read"] for c in cells])
    return {"ok": True, "reason": None, "cells": cells, "worlds": {"chance": 0.25},
            "gains": gains, "reads": reads,
            "spans": {"replicates": len(cells), "n_act": cells[0]["n_act"], "coords": cells[0]["n_act"] ** 2,
                      "identity_all": all(c["identity_bitwise"] for c in cells),
                      "identity_worst": max(c["identity_max_abs"] for c in cells),
                      "grad_norm_min": min(c["grad_norm"] for c in cells),
                      "fd_worst": max(c["fd_worst_abs"] for c in cells),
                      "fd_worst_at": max(cells, key=lambda c: c["fd_worst_abs"])["fd_worst_at"],
                      "moves": [c["policy_move"] for c in cells],
                      "targets": [c["target_sha1"] for c in cells]}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e477.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: the identity policy trick, the loop's gradient, a playable game and a read-out that gains
    j = _judge()
    for cid in ("QA1", "QA2", "QA3", "QA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # QA1: a policy whose identity is not the environment's rule, bit for bit
    assert _judge(cells=[_cell(seed=s, identity=False, ident_max=1e-07) for s in range(4)])["QA1"].startswith(
        "FALSIFIER")
    assert _judge(cells=[_cell(seed=s, ident_max=1e-09) for s in range(4)])["QA1"].startswith("FALSIFIER")

    # QA2: a gradient that disagrees with the finite difference, and one that vanishes
    assert _judge(cells=[_cell(seed=s, fd=1e-02) for s in range(4)])["QA2"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, grad_norm=0.0) for s in range(4)])["QA2"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, fd=4e-03) for s in range(4)])["QA2"].startswith("MET")

    # QA3: a gain below the floor fires it, one between the floor and the bar is a null, and an unresolved gain fires
    assert _judge(cells=[_cell(seed=s, gain=0.10) for s in range(4)])["QA3"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=i, gain=g) for i, g in enumerate((0.30, 0.40, 0.35, 0.38))])["QA3"].startswith(
        "NULL")
    assert _judge(cells=[_cell(seed=i, gain=g) for i, g in enumerate((0.60, 0.70, 0.55, 0.65))])["QA3"].startswith(
        "MET")
    assert _judge(cells=[_cell(seed=0, gain=2.00), _cell(seed=1, gain=-2.00)])["QA3"].startswith("FALSIFIER")

    # QA4: a read-out the trained policy makes worse fires it, and a flat one is a null
    assert _judge(cells=[_cell(seed=s, read=-0.05) for s in range(4)])["QA4"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, read=0.00) for s in range(4)])["QA4"].startswith("NULL")
    assert _judge(cells=[_cell(seed=s, read=0.06) for s in range(4)])["QA4"].startswith("MET")

    #: replicates that were not rolled refuse every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e477.judge(_doc(ok=False)))
    assert all(row["verdict"].startswith("REFUSED") for row in e477.judge(_doc(cells=[_cell()])))


def test_the_substrate_the_bars_and_the_library_field_are_registered():
    assert (e477.SIZE, e477.READOUT_SIZE, e477.SEED) == (300, 32, 0)
    assert (e477.TAU, e477.N_SYMBOLS, e477.N_TRAIN, e477.N_HELD) == (12, 4, 512, 256)
    assert (e477.WORLD_DIMS, e477.WORLD_LEAK, e477.SCALE, e477.GAIN, e477.NOISE) == (8, 0.35, 1.0, 1.0, 1.0)
    assert (e477.STEPS, e477.LR) == (300, 0.05), (e477.STEPS, e477.LR)
    assert (e477.EPS, e477.FTOL) == (1e-3, 5e-3), (e477.EPS, e477.FTOL)
    assert (e477.SIGMA, e477.GAIN_BAR, e477.GAIN_FLOOR) == (2.0, 0.50, 0.20)
    assert (e477.READ_BAR, e477.READ_FLOOR) == (0.05, -0.02)
    assert e477.REPLICATES == (0, 1, 2, 3, 4, 5, 6, 7), e477.REPLICATES
    assert e477.TARGET_OFFSET == 101
    #: the policy is a field of the environment the corpus already builds, off by default
    from clfly.network.env import CueActionEnv
    fields = {f.name: f for f in dataclasses.fields(CueActionEnv)}
    assert "policy" in fields, sorted(fields)
    assert fields["policy"].default is None, fields["policy"].default


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e477_the_game_gets_a_policy.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e477.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the replicate count is structural; the counts that grow with the corpus are read as floors
    assert d["spans"]["replicates"] == len(e477.REPLICATES), d["spans"]["replicates"]
    assert d["spans"]["coords"] == d["spans"]["n_act"] ** 2, d["spans"]
    assert d["spans"]["identity_all"] is True and d["spans"]["identity_worst"] == 0.0, d["spans"]
    assert d["worlds"]["dims"] == e477.WORLD_DIMS and d["worlds"]["n_symbols"] == e477.N_SYMBOLS, d["worlds"]
    assert 0.0 < d["worlds"]["chance"] < 1.0, d["worlds"]["chance"]
    assert len(d["cells"]) == len(e477.REPLICATES), len(d["cells"])
    for c in d["cells"]:
        assert 0.0 <= c["init_read"] <= 1.0 and 0.0 <= c["trained_read"] <= 1.0, c
    assert d["gains"]["n"] == d["reads"]["n"] == len(e477.REPLICATES), (d["gains"]["n"], d["reads"]["n"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
