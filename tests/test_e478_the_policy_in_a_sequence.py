"""`e478` puts the agent's policy through a task sequence, so the tests pin both faces of the four claims, the
retention matrix's shape, and the refusal when the replicates were not rolled.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e478_the_policy_in_a_sequence as e478

TASKS = e478.TASKS


def _R(seed: int, task2_gain=None, first_drop=None, gap=None):
    """A retention matrix in reward: row 0 is the identity policy, row k+1 is after task k.

    The small seed-dependent jitter is what gives the paired contrasts a standard error, so a fake with a flat
    difference is not a fake this unit's instrument can resolve anything on.
    """
    j = lambda i: 0.1 * ((seed + i) % 4)
    R = [[-9.0, -8.0, -7.0],
         [-7.0 + j(1), None, None],
         [-8.2 + j(2), -6.2 + j(3), None],
         [-8.6 + j(4), -7.4 + j(5), -4.6 + j(6)]]
    if task2_gain is not None:
        R[3][2] = R[0][2] + task2_gain + 0.05 * seed
    if first_drop is not None:
        R[3][0] = R[1][0] - first_drop - 0.05 * seed
    if gap is not None:
        diag = [R[1][0], R[2][1], R[3][2]]
        for i in range(TASKS):
            R[TASKS][i] = diag[i] - gap - 0.05 * seed
    return R


def _cell(seed=0, identity=True, ident_max=0.0, move=12.0, **kw):
    R = _R(seed, **kw)
    return {"seed": seed, "n_act": 8, "identity_bitwise": identity, "identity_max_abs": ident_max,
            "identity_reward": R[0], "R": R, "policy_move": move, "targets_sha1": f"t{seed}"}


def _doc(cells=None, ok=True, reason="the replicates were not rolled"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "mean_R": [], "learned": {}, "forgot": {},
                "retention": {}, "spans": {}, "worlds": {}}
    cells = cells if cells is not None else [_cell(seed=s) for s in range(4)]
    T = TASKS
    mean_R = []
    for k in range(T + 1):
        row = []
        for j in range(T):
            vals = [c["R"][k][j] for c in cells if c["R"][k][j] is not None]
            row.append(statistics.fmean(vals) if vals else None)
        mean_R.append(row)
    return {"ok": True, "reason": None, "cells": cells, "mean_R": mean_R,
            "worlds": {"chance": 0.25, "tasks": T},
            "learned": {f"task{k}": e478._paired([c["R"][k + 1][k] for c in cells],
                                                 [c["R"][0][k] for c in cells]) for k in range(T)},
            "forgot": e478._paired([c["R"][1][0] for c in cells], [c["R"][T][0] for c in cells]),
            "retention": e478._paired([statistics.fmean([c["R"][k + 1][k] for k in range(T)]) for c in cells],
                                      [statistics.fmean([c["R"][T][j] for j in range(T)]) for c in cells]),
            "spans": {"replicates": len(cells), "tasks": T, "n_act": cells[0]["n_act"],
                      "identity_all": all(c["identity_bitwise"] for c in cells),
                      "identity_worst": max(c["identity_max_abs"] for c in cells),
                      "moves": [c["policy_move"] for c in cells],
                      "targets": [c["targets_sha1"] for c in cells], "rows": T + 1}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e478.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: every replicate starts from the corpus's rule, all three tasks are learned, the first is forgotten,
    #: and the diagonal sits above the last row
    j = _judge()
    for cid in ("SA1", "SA2", "SA3", "SA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # SA1: a first step that is not the environment's own rule, with and without a reported difference
    assert _judge(cells=[_cell(seed=s, identity=False) for s in range(4)])["SA1"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, ident_max=1e-09) for s in range(4)])["SA1"].startswith("FALSIFIER")

    # SA2: a task the sequence does not learn -- below the floor fires it, and between the floor and the bar is a null
    assert _judge(cells=[_cell(seed=s, task2_gain=0.05) for s in range(4)])["SA2"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, task2_gain=0.35) for s in range(4)])["SA2"].startswith("NULL")

    # SA3: a first task that is barely dropped is a falsifier, one dropped between the bands is a null
    assert _judge(cells=[_cell(seed=s, first_drop=0.05) for s in range(4)])["SA3"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, first_drop=0.35) for s in range(4)])["SA3"].startswith("NULL")

    # SA4: a last row level with the diagonal fires it, one between the bands is a null
    assert _judge(cells=[_cell(seed=s, gap=0.05) for s in range(4)])["SA4"].startswith("FALSIFIER")
    assert _judge(cells=[_cell(seed=s, gap=0.35) for s in range(4)])["SA4"].startswith("NULL")

    #: replicates that were not rolled refuse every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e478.judge(_doc(ok=False)))
    assert all(row["verdict"].startswith("REFUSED") for row in e478.judge(_doc(cells=[_cell()])))


def test_the_substrate_the_bars_and_the_sequence_are_registered():
    assert (e478.SIZE, e478.READOUT_SIZE, e478.SEED) == (300, 32, 0)
    assert (e478.TAU, e478.N_SYMBOLS, e478.N_TRAIN, e478.N_HELD) == (12, 4, 512, 256)
    assert (e478.WORLD_DIMS, e478.WORLD_LEAK) == (8, 0.35), (e478.WORLD_DIMS, e478.WORLD_LEAK)
    assert (e478.TASKS, e478.STEPS, e478.LR) == (3, 300, 0.05), (e478.TASKS, e478.STEPS, e478.LR)
    assert (e478.SIGMA, e478.BAR, e478.FLOOR) == (2.0, 0.50, 0.20)
    assert e478.REPLICATES == (0, 1, 2, 3, 4, 5, 6, 7), e478.REPLICATES
    assert e478.TARGET_OFFSET == 101


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e478_the_policy_in_a_sequence.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e478.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the sequence and the replicate count are structural; the counts that grow with the corpus are read as floors
    assert d["spans"]["replicates"] == len(e478.REPLICATES), d["spans"]["replicates"]
    assert d["spans"]["tasks"] == TASKS and d["spans"]["rows"] == TASKS + 1, d["spans"]
    assert d["spans"]["identity_all"] is True and d["spans"]["identity_worst"] == 0.0, d["spans"]
    assert len(d["mean_R"]) == TASKS + 1, len(d["mean_R"])
    for k, row in enumerate(d["mean_R"]):
        assert len(row) == TASKS, (k, row)
        for j, x in enumerate(row):
            #: the matrix is lower-triangular: the identity row is full and row k+1 is read on tasks 0 through k
            assert (x is not None) == ((k == 0) or (j <= k - 1)), (k, j, x)
    assert sorted(d["learned"]) == [f"task{k}" for k in range(TASKS)], sorted(d["learned"])
    for v in list(d["learned"].values()) + [d["forgot"], d["retention"]]:
        assert v["n"] == len(e478.REPLICATES), v
    assert len(d["cells"]) == len(e478.REPLICATES), len(d["cells"])
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
