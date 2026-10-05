"""`e416` reads every penalty cell the corpus holds, so the tests pin both faces of the five claims, the null when no
cell is dominated, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e416_the_penalty_ledger as e416


def _cell(artifact, penalty, reps, acc, mf):
    return {"artifact": artifact, "penalty": penalty, "replicates": reps,
            "accuracy": {"naive": 0.5, "replay": 0.5 + acc, "penalty": 0.5},
            "forgetting": {"naive": 0.4, "replay": 0.4 + mf, "penalty": 0.4},
            "replay_minus_penalty": {"accuracy": acc, "forgetting": mf},
            "lam": 1.0, "circuit_size": 800}


def _ledger(win=52, floor=11, dominated=6, floor_loss=0, floor_dominated=0, dominated_penalty="ewc-block",
            dominated_reps=5, dominated_margin=-0.01, thin=None):
    cells = []
    for i in range(win):
        cells.append(_cell(f"census_{i}.json", "ewc" if i % 2 else "ewc-block", 5, +0.05, -0.05))
    for i in range(floor):
        cells.append(_cell(f"powered_{i}.json", "ewc-block" if i % 2 else "ewc", 20, +0.05, -0.05))
    for i in range(dominated):
        cells.append(_cell(f"dominated_{i}.json", dominated_penalty, dominated_reps, dominated_margin,
                           -dominated_margin))
    for i in range(thin or 0):
        cells.append(_cell(f"thin_{i}.json", "ewc", 2, +0.05, -0.05))
    for i in range(floor_loss):
        cells[i] = _cell(cells[i]["artifact"], "ewc", 20, -0.02, -0.05)
    for i in range(floor_dominated):
        cells[win + i] = _cell(f"powered_{i}.json", "ewc", 20, -0.02, +0.02)
    return cells


def _doc(cells=None, collapsed=24, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "artifacts": [], "collapsed": 0, "floor": 20, "small": 3}
    cells = _ledger() if cells is None else cells
    return {"ok": True, "reason": None, "cells": cells, "artifacts": sorted({c["artifact"] for c in cells}),
            "collapsed": collapsed, "floor": e416.FLOOR, "small": e416.SMALL}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e416.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the ledger carried, most cells won, every powered cell won, and six small dominances
    j = _judge()
    for cid in ("AL1", "AL2", "AL3", "AL4", "AL5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AL1: too few cells, too few artifacts, and a cell under the replicate bound
    assert _judge(cells=_ledger(win=30, floor=8, dominated=6))["AL1"].startswith("FALSIFIER")
    assert _judge(cells=_ledger(win=30, floor=8, dominated=2, thin=1))["AL1"].startswith("FALSIFIER")

    # AL2: a ledger the buffer loses, and one it wins between the bars
    assert _judge(cells=_ledger(win=5, floor=4, dominated=20))["AL2"].startswith("FALSIFIER")
    assert _judge(cells=_ledger(win=10, floor=11, dominated=6))["AL2"].startswith("NULL")

    # AL3: a cell at the floor the buffer loses, and too few cells at the floor
    assert _judge(cells=_ledger(floor_loss=1))["AL3"].startswith("FALSIFIER")
    assert _judge(cells=_ledger(floor=4))["AL3"].startswith("FALSIFIER")

    # AL4: a cell at the floor where the penalty is both more accurate and less forgetful
    assert _judge(cells=_ledger(floor_dominated=1))["AL4"].startswith("FALSIFIER")

    # AL5: no dominance at all, one carrying the diagonal penalty, and one whose margin is wide
    assert _judge(cells=_ledger(dominated=0))["AL5"].startswith("NULL")
    assert _judge(cells=_ledger(dominated=6, dominated_penalty="ewc"))["AL5"].startswith("FALSIFIER")
    assert _judge(cells=_ledger(dominated=6, dominated_margin=-0.20))["AL5"].startswith("FALSIFIER")

    #: the corpus not reading refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e416.judge(_doc(ok=False)))


def test_the_ledger_and_the_thresholds_are_registered():
    #: the glob's root, the two penalties a cell is pooled over, and the two arms it must carry
    assert e416.ROOT == Path("runs")
    assert e416.PENALTIES == ("ewc", "ewc-block") and e416.REQUIRED == ("naive", "replay")
    assert (e416.FLOOR, e416.SMALL) == (20, 3)
    assert (e416.MIN_CELLS, e416.MIN_ARTIFACTS) == (50, 20)
    assert (e416.WIN, e416.WIN_FIRES) == (0.80, 0.60)
    assert e416.FLOOR_CELLS == 8
    assert (e416.MARGIN, e416.MARGIN_FIRES, e416.SMALL_REPS) == (0.05, 0.10, 5)


def test_the_live_ledger_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e416_the_penalty_ledger.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e416.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e416.judge(d)}
    #: the ledger being carried and the powered cells being won are structural facts
    assert verdicts["AL1"].startswith("MET") and verdicts["AL3"].startswith("MET"), verdicts
    assert len(d["cells"]) >= e416.MIN_CELLS and len(d["artifacts"]) >= e416.MIN_ARTIFACTS, (len(d["cells"]),
                                                                                            len(d["artifacts"]))
    assert all(c["replicates"] >= e416.SMALL for c in d["cells"]), min(c["replicates"] for c in d["cells"])
    assert all(c["penalty"] in e416.PENALTIES for c in d["cells"])
    #: the contrast each cell carries is the artifact's own two means, and the floor's cells are a subset
    for c in d["cells"]:
        assert abs(c["replay_minus_penalty"]["accuracy"]
                   - (c["accuracy"]["replay"] - c["accuracy"]["penalty"])) < 1e-12, c["artifact"]
    assert sum(1 for c in d["cells"] if c["replicates"] >= e416.FLOOR) >= e416.FLOOR_CELLS
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
