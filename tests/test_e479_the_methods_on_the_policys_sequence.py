"""`e479` runs three arms of a task sequence whose subject is the agent's policy, so the tests pin both faces of the
four claims, the ordering between the arms, and the refusal when the arms were not rolled.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from experiments import e479_the_methods_on_the_policys_sequence as e479

ARMS = e479.ARMS
TASKS = e479.TASKS
REPS = (0, 1, 2, 3)
#: the arm bonuses the fake carries: the buffer's diagonal and last row sit above the penalty's on both
DB = {"naive": 0.0, "replay": 0.9, "penalty": 0.1}
LB = {"naive": 0.0, "replay": 0.8, "penalty": 0.1}


def _R(seed, arm, db=None, lb=None, gain=None):
    j = lambda i: 0.1 * ((seed + i) % 4)
    #: the arm's own bonus scaled by the replicate, so a paired contrast between arms has a standard error at all
    scale = 1.0 + 0.05 * seed
    db = (DB[arm] if db is None else db) * scale
    lb = (LB[arm] if lb is None else lb) * scale
    learn = 2.0 if gain is None else gain
    ident = [-9.0, -8.0, -7.0]
    diag = [ident[k] + learn + db + j(k + 1) for k in range(TASKS)]
    R = [list(ident), [None] * TASKS, [None] * TASKS, [None] * TASKS]
    for k in range(TASKS):
        R[k + 1][k] = diag[k]
        for jj in range(k):
            R[k + 1][jj] = diag[jj] - (1.5 - lb) + j(20 + k + jj)
    return R


def _cell(seed, arm, **kw):
    R = _R(seed, arm, **kw)
    return {"seed": seed, "arm": arm, "n_act": 8, "identity_bitwise": True, "identity_max_abs": 0.0,
            "R": R, "policy_move": 12.0, "targets_sha1": f"t{seed}"}


def _doc(cells=None, ok=True, arms=ARMS, reps=REPS, identity_all=True, identity_worst=0.0,
         seeds=None, targets=None, reason="the arms were not rolled"):
    arms = tuple(arms)
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "mean_R": {}, "learned": {}, "diagonal": {},
                "last_row": {}, "ordering": {}, "spans": {}, "worlds": {}}
    cells = cells if cells is not None else [_cell(s, a) for s in reps for a in arms]
    by = {(c["seed"], c["arm"]): c for c in cells}
    T = TASKS

    def mean_R(a):
        rows = []
        for k in range(T + 1):
            row = []
            for j in range(T):
                vals = [by[(s, a)]["R"][k][j] for s in reps if (s, a) in by and by[(s, a)]["R"][k][j] is not None]
                row.append(statistics.fmean(vals) if vals else None)
            rows.append(row)
        return rows

    diagonal = {a: [statistics.fmean([by[(s, a)]["R"][k + 1][k] for k in range(T)]) for s in reps] for a in arms}
    last_row = {a: [statistics.fmean([by[(s, a)]["R"][T][j] for j in range(T)]) for s in reps] for a in arms}
    ordering = {}
    if all(a in arms for a in ("naive", "replay", "penalty")):
        ordering = {"diagonal": e479._paired(diagonal["replay"], diagonal["penalty"]),
                    "last_row": e479._paired(last_row["replay"], last_row["penalty"]),
                    "penalty_over_naive": e479._paired(diagonal["penalty"], diagonal["naive"]),
                    "replay_over_naive": e479._paired(diagonal["replay"], diagonal["naive"])}
    return {"ok": True, "reason": None, "cells": cells, "mean_R": {a: mean_R(a) for a in arms},
            "worlds": {"chance": 0.25, "tasks": T, "arms": list(arms)},
            "learned": {a: {f"task{k}": e479._paired([by[(s, a)]["R"][k + 1][k] for s in reps],
                                                     [by[(s, a)]["R"][0][k] for s in reps])
                            for k in range(T)} for a in arms},
            "diagonal": diagonal, "last_row": last_row, "ordering": ordering,
            "spans": {"arms": list(arms), "replicates": len(reps), "tasks": T, "n_act": cells[0]["n_act"],
                      "identity_all": identity_all, "identity_worst": identity_worst,
                      "targets": list(targets if targets is not None else sorted({f"t{s}" for s in reps})),
                      "seeds": list(seeds if seeds is not None else reps),
                      "moves": {a: [12.0 for _ in reps] for a in arms}, "cells": len(cells)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e479.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: one configuration from the corpus's rule, every arm learning every task, and the buffer ahead of
    #: the penalty on both the diagonal and the retention
    j = _judge()
    for cid in ("TA1", "TA2", "TA3", "TA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # TA1: a first step that is not the corpus's rule, a seed or target draw that does not match, and a reported gap
    assert _judge(identity_all=False)["TA1"].startswith("FALSIFIER")
    assert _judge(identity_worst=1e-09)["TA1"].startswith("FALSIFIER")
    assert _judge(seeds=(0, 1, 2))["TA1"].startswith("FALSIFIER")
    assert _judge(targets=("t0",))["TA1"].startswith("FALSIFIER")

    # TA2: an arm that does not learn its tasks -- below the floor fires it, and between the bands is a null
    slow = [_cell(s, a, gain=-1.0 if a == "penalty" else None) for s in REPS for a in ARMS]
    assert _judge(cells=slow)["TA2"].startswith("FALSIFIER")
    mid = [_cell(s, a, gain=0.25, db=0.0) for s in REPS for a in ARMS]
    assert _judge(cells=mid)["TA2"].startswith("NULL")

    # TA3: a buffer that does not lead the penalty on the diagonal, and one between the bands
    tie = [_cell(s, a, db=0.0) for s in REPS for a in ARMS]
    assert _judge(cells=tie)["TA3"].startswith("FALSIFIER")
    close = [_cell(s, a, db=0.35 if a == "replay" else 0.0) for s in REPS for a in ARMS]
    assert _judge(cells=close)["TA3"].startswith("NULL")

    # TA4: the same on retention
    tie4 = [_cell(s, a, lb=0.0, db=0.0) for s in REPS for a in ARMS]
    assert _judge(cells=tie4)["TA4"].startswith("FALSIFIER")
    close4 = [_cell(s, a, lb=0.35 if a == "replay" else 0.0, db=0.0) for s in REPS for a in ARMS]
    assert _judge(cells=close4)["TA4"].startswith("NULL")

    #: a run with fewer than two cells refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e479.judge(_doc(ok=False)))
    assert all(row["verdict"].startswith("REFUSED")
               for row in e479.judge(_doc(cells=[_cell(0, "naive")], arms=("naive",), reps=(0,))))


def test_the_substrate_the_arms_and_the_bars_are_registered():
    assert (e479.SIZE, e479.READOUT_SIZE, e479.SEED) == (300, 32, 0)
    assert (e479.TAU, e479.SYMBOLS_PER_TASK, e479.N_SYMBOLS) == (12, 4, 12), (e479.TAU, e479.N_SYMBOLS)
    assert (e479.WORLD_DIMS, e479.WORLD_LEAK) == (8, 0.35)
    assert (e479.TASKS, e479.STEPS, e479.LR) == (3, 300, 0.05)
    assert (e479.LAM, e479.REPLAY_TASK, e479.REPLAY_BATCH, e479.FISHER_BATCHES) == (1.0, 64, 64, 8)
    assert (e479.SIGMA, e479.BAR, e479.FLOOR) == (2.0, 0.50, 0.20)
    assert e479.ARMS == ("naive", "replay", "penalty"), e479.ARMS
    assert e479.REPLICATES == (0, 1, 2, 3, 4, 5, 6, 7), e479.REPLICATES
    assert e479.TARGET_OFFSET == 101


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e479_the_methods_on_the_policys_sequence.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e479.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the arms, the tasks and the replicate count are structural; the counts that grow with the corpus are floors
    assert sorted(d["mean_R"]) == sorted(e479.ARMS), sorted(d["mean_R"])
    assert d["spans"]["replicates"] == len(e479.REPLICATES), d["spans"]["replicates"]
    assert d["spans"]["cells"] == len(e479.ARMS) * len(e479.REPLICATES), d["spans"]["cells"]
    assert d["spans"]["identity_all"] is True and d["spans"]["identity_worst"] == 0.0, d["spans"]
    assert len(d["spans"]["seeds"]) == len(e479.REPLICATES), d["spans"]["seeds"]
    for a, rows in d["mean_R"].items():
        assert len(rows) == TASKS + 1, (a, len(rows))
        for k, row in enumerate(rows):
            assert len(row) == TASKS, (a, k, row)
            for j, x in enumerate(row):
                assert (x is not None) == ((k == 0) or (j <= k - 1)), (a, k, j, x)
    assert sorted(d["learned"]) == sorted(e479.ARMS), sorted(d["learned"])
    assert sorted(d["ordering"]) == ["diagonal", "last_row", "penalty_over_naive", "replay_over_naive"], \
        sorted(d["ordering"])
    for a in e479.ARMS:
        assert len(d["diagonal"][a]) == len(e479.REPLICATES), a
        assert len(d["last_row"][a]) == len(e479.REPLICATES), a
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
