"""`e422` splits the paired gain into the level a task is taught to and what is lost afterwards, so the tests pin both
faces of the five claims, the refusal when a cell is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e422_the_buffer_buys_retention as e422

#: the corpus's shape: per cell, `(learned term, retention term)` over the three tasks
TERMS = {
    "card": ((0.0000, -0.0302, -0.0604), (0.2896, 0.2792, 0.0000)),
    "world1": ((0.0000, -0.0177, -0.0479), (0.3198, 0.2729, 0.0000)),
    "world2": ((0.0000, -0.0115, -0.0563), (0.2615, 0.1594, 0.0000)),
    "world3": ((0.0000, +0.0208, -0.0115), (0.3021, 0.2177, 0.0000)),
    "world4": ((0.0000, -0.0667, -0.0656), (0.2615, 0.3271, 0.0000)),
    "stream1": ((0.0000, -0.0531, -0.0927), (0.3219, 0.2854, 0.0000)),
    "stream2": ((0.0000, -0.0750, -0.0802), (0.2333, 0.2990, 0.0000)),
    "cue1": ((0.0000, -0.0042, -0.0646), (0.2635, 0.2042, 0.0000)),
    "cue3": ((0.0000, -0.0146, -0.0740), (0.3021, 0.2333, 0.0000)),
    "cue6": ((0.0000, -0.0635, -0.1031), (0.3156, 0.3135, 0.0000)),
    "cue9": ((0.0000, -0.0646, -0.0781), (0.3042, 0.3104, 0.0000)),
    "cue14": ((0.0000, -0.0479, -0.0427), (0.2813, 0.2698, 0.0000)),
}


def _cell(learned, retention, reps=20, break_identity=0.0):
    learned, retention = list(learned), list(retention)
    gain = [learned[k] + retention[k] for k in range(e422.N_TASKS)]
    gain[e422.MIDDLE] += break_identity
    ratio = (abs(retention[e422.MIDDLE]) / abs(learned[e422.MIDDLE])) if learned[e422.MIDDLE] else None
    return {"artifact": "x.json", "replicates": reps,
            "naive": {"learned": [0.5] * e422.N_TASKS, "final": [0.3] * e422.N_TASKS,
                      "forgetting": [0.2] * e422.N_TASKS},
            "replay": {"learned": [0.5 + learned[k] for k in range(e422.N_TASKS)],
                       "final": [0.3 + gain[k] for k in range(e422.N_TASKS)],
                       "forgetting": [0.2 - retention[k] for k in range(e422.N_TASKS)]},
            "learned": learned, "retention": retention, "gain": gain, "middle_ratio": ratio}


def _doc(spec=None, reps=20, break_identity=0.0, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": {}, "spans": {}}
    spec = TERMS if spec is None else spec
    cells = {n: _cell(learned, retention, reps, break_identity) for n, (learned, retention) in spec.items()}
    return {"ok": True, "reason": None, "cells": cells,
            "spans": {"cells": len(cells), "replicates": sorted({c["replicates"] for c in cells.values()}),
                      "oldest_learn_max": max(abs(c["learned"][e422.OLDEST]) for c in cells.values()),
                      "oldest_retain_min": min(c["retention"][e422.OLDEST] for c in cells.values()),
                      "newest_retain_max": max(abs(c["retention"][e422.NEWEST]) for c in cells.values()),
                      "newest_learn_max": max(c["learned"][e422.NEWEST] for c in cells.values()),
                      "middle_retain_min": min(c["retention"][e422.MIDDLE] for c in cells.values()),
                      "middle_learn_worst": min(c["learned"][e422.MIDDLE] for c in cells.values()),
                      "middle_learn_cost": sum(1 for c in cells.values() if c["learned"][e422.MIDDLE] < 0),
                      "middle_ratio_min": min(c["middle_ratio"] for c in cells.values()
                                              if c["middle_ratio"] is not None),
                      "worst_identity": max(abs(c["gain"][k] - c["learned"][k] - c["retention"][k])
                                            for c in cells.values() for k in range(e422.N_TASKS))}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e422.judge(_doc(**kw))}


def _with(name, learned=None, retention=None):
    out = {k: (tuple(l), tuple(r)) for k, (l, r) in TERMS.items()}
    kind_l, kind_r = out[name]
    out[name] = (tuple(learned) if learned is not None else kind_l,
                 tuple(retention) if retention is not None else kind_r)
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the two structural zeros, a large retention, and an identity that holds exactly
    j = _judge()
    for cid in ("AW1", "AW2", "AW3", "AW4", "AW5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AW1: too few replicates, and too few cells
    assert _judge(reps=19)["AW1"].startswith("FALSIFIER")
    assert _judge(spec={k: v for k, v in list(TERMS.items())[:8]})["AW1"].startswith("FALSIFIER")

    # AW2: a cell whose oldest task is learned differently, one whose retention is under the falsifier bar, and one
    # between the bars
    assert _judge(spec=_with("card", learned=(0.02, -0.0302, -0.0604)))["AW2"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", retention=(0.08, 0.2792, 0.0)))["AW2"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", retention=(0.15, 0.2792, 0.0)))["AW2"].startswith("NULL")

    # AW3: a cell whose newest task is forgotten at all, and one whose newest learning term is not a loss
    assert _judge(spec=_with("card", retention=(0.2896, 0.2792, 0.01)))["AW3"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", learned=(0.0, -0.0302, +0.01)))["AW3"].startswith("FALSIFIER")

    # AW4: a shallow middle retention, one under the falsifier bar, and a tight ratio
    assert _judge(spec=_with("card", retention=(0.2896, 0.08, 0.0)))["AW4"].startswith("NULL")
    assert _judge(spec=_with("card", retention=(0.2896, 0.03, 0.0)))["AW4"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", learned=(0.0, -0.20, -0.0604)))["AW4"].startswith("FALSIFIER")

    # AW5: a cell whose gain is not the two terms
    assert _judge(break_identity=0.02)["AW5"].startswith("FALSIFIER")

    #: a cell's run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e422.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the twelve far-point cells `e420` and `e421` read
    assert len(e422.RUNS) == 12 and sorted(e422.RUNS) == sorted(TERMS), sorted(e422.RUNS)
    for n, p in e422.RUNS.items():
        assert "iters500" in p.name or "e380" in p.name, n
    assert e422.ARMS == ("naive", "replay") and e422.N_TASKS == 3
    assert (e422.OLDEST, e422.MIDDLE, e422.NEWEST) == (0, 1, 2)
    assert (e422.MIN_CELLS, e422.MIN_REPS) == (10, 20)
    assert (e422.ZERO, e422.RETENTION, e422.RETENTION_FIRES) == (1e-3, 0.20, 0.10)
    assert (e422.MIDDLE_BAR, e422.MIDDLE_FIRES) == (0.10, 0.05)
    assert (e422.RATIO, e422.RATIO_FIRES) == (3.0, 2.0)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e422_the_buffer_buys_retention.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e422.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e422.judge(d)}
    #: the ledger being carried and the two structural zeros are facts of the recording
    assert verdicts["AW1"].startswith("MET") and verdicts["AW5"].startswith("MET"), verdicts
    assert len(d["cells"]) >= e422.MIN_CELLS, len(d["cells"])
    for n, c in d["cells"].items():
        assert c["replicates"] >= e422.MIN_REPS, n
        assert abs(c["learned"][e422.OLDEST]) <= e422.ZERO, n
        assert abs(c["retention"][e422.NEWEST]) <= e422.ZERO, n
        assert c["learned"][e422.NEWEST] < 0.0, n
        #: the identity holds in the artifact and each arm carries the three per-task readings
        for k in range(e422.N_TASKS):
            assert abs(c["gain"][k] - c["learned"][k] - c["retention"][k]) <= e422.ZERO, (n, k)
        for arm in e422.ARMS:
            assert len(c[arm]["learned"]) == len(c[arm]["final"]) == len(c[arm]["forgetting"]) == e422.N_TASKS, n
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
