"""`e420` reads the per-task gains of the twelve earned-label far-point cells, so the tests pin both faces of the five
claims, the refusal when a cell is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e420_the_trade_is_a_constant as e420

#: the corpus's shape: per cell, the kind of redraw it moves and its three per-task gains
GAINS = {
    "card": ("card", (0.2896, 0.2490, -0.0604)),
    "world1": ("world", (0.3198, 0.2552, -0.0479)),
    "world2": ("world", (0.2615, 0.1479, -0.0563)),
    "world3": ("world", (0.3021, 0.2385, -0.0115)),
    "world4": ("world", (0.2615, 0.2604, -0.0656)),
    "stream1": ("stream", (0.3219, 0.2323, -0.0927)),
    "stream2": ("stream", (0.2333, 0.2240, -0.0802)),
    "cue1": ("cue", (0.2635, 0.2000, -0.0646)),
    "cue3": ("cue", (0.3021, 0.2188, -0.0740)),
    "cue6": ("cue", (0.3156, 0.2500, -0.1031)),
    "cue9": ("cue", (0.3042, 0.2458, -0.0781)),
    "cue14": ("cue", (0.2813, 0.2219, -0.0427)),
}
SE = 0.02


def _cell(name, kind, gains, reps=20, se=SE):
    gains = list(gains)
    older = gains[e420.OLDEST] + gains[e420.MIDDLE]
    loss = -gains[e420.NEWEST]
    return {"artifact": f"{name}.json", "kind": kind, "name": name, "replicates": reps,
            "naive_final": [0.3, 0.4, 0.8], "replay_final": [0.3 + gains[0], 0.4 + gains[1], 0.8 + gains[2]],
            "gain": gains, "se": [se] * e420.N_TASKS, "sigma": [g / se for g in gains],
            "newest_loss": loss, "coverage": older / loss if loss > 0 else float("inf"),
            "share": loss / gains[e420.OLDEST] if gains[e420.OLDEST] > 0 else float("inf")}


def _doc(spec=None, reps=20, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": {}, "kinds": {}, "spans": {}}
    spec = GAINS if spec is None else spec
    cells, kinds = {}, {}
    for name, (kind, gains) in spec.items():
        cells[name] = _cell(name, kind, gains, reps=reps)
        kinds.setdefault(kind, []).append(name)
    return {"ok": True, "reason": None, "cells": cells, "kinds": kinds,
            "spans": {"cells": len(cells), "kinds": sorted(kinds),
                      "replicates": sorted({c["replicates"] for c in cells.values()}),
                      "least_oldest": min(c["gain"][e420.OLDEST] for c in cells.values()),
                      "worst_newest": max(c["gain"][e420.NEWEST] for c in cells.values()),
                      "largest_loss": max(c["newest_loss"] for c in cells.values()),
                      "least_coverage": min(c["coverage"] for c in cells.values()),
                      "largest_share": max(c["share"] for c in cells.values()),
                      "weakest_sigma": min(c["sigma"][e420.OLDEST] for c in cells.values())}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e420.judge(_doc(**kw))}


def _with(name, gains):
    out = {k: (kind, tuple(g)) for k, (kind, g) in GAINS.items()}
    out[name] = (out[name][0], tuple(gains))
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: twelve cells over four kinds, every newest task cost, coverage above five
    j = _judge()
    for cid in ("AU1", "AU2", "AU3", "AU4", "AU5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AU1: too few replicates, too few kinds, and too few cells
    assert _judge(reps=19)["AU1"].startswith("FALSIFIER")
    two_kinds = {k: v for k, v in GAINS.items() if v[0] in ("card", "cue")}
    assert _judge(spec=two_kinds)["AU1"].startswith("FALSIFIER")
    assert _judge(spec={k: v for k, v in list(GAINS.items())[:8]})["AU1"].startswith("FALSIFIER")

    # AU2: a cell whose newest task is not cost
    assert _judge(spec=_with("card", (0.2896, 0.2490, +0.01)))["AU2"].startswith("FALSIFIER")

    # AU3: a cell under the recovery bar, one between the bars, and one unresolved
    assert _judge(spec=_with("card", (0.05, 0.2490, -0.0604)))["AU3"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", (0.15, 0.2490, -0.0604)))["AU3"].startswith("NULL")
    weak = _with("card", (0.2896, 0.2490, -0.0604))
    doc = _doc(spec=weak)
    doc["cells"]["card"]["sigma"][e420.OLDEST] = 3.0
    assert {row["id"]: row["verdict"] for row in e420.judge(doc)}["AU3"].startswith("NULL")

    # AU4: a coverage under the falsifier bar, and one between the bars
    assert _judge(spec=_with("card", (0.05, 0.05, -0.0604)))["AU4"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", (0.20, 0.20, -0.1031)))["AU4"].startswith("NULL")

    # AU5: a loss over the falsifier bar, and one between the bars
    assert _judge(spec=_with("card", (0.10, 0.2490, -0.1031)))["AU5"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", (0.18, 0.2490, -0.1031)))["AU5"].startswith("NULL")

    #: a cell's run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e420.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the twelve far-point cells, four of them world redraws and two clean streams beside the card and five cues
    assert len(e420.RUNS) == 12 and sorted(e420.RUNS) == sorted(GAINS), sorted(e420.RUNS)
    for n, p in e420.RUNS.items():
        assert "iters500" in p.name or "e380" in p.name, n
        assert e420.KIND[n] in ("card", "world", "stream", "cue"), n
    assert sorted(set(e420.KIND.values())) == ["card", "cue", "stream", "world"]
    assert e420.ARMS == ("naive", "replay") and e420.N_TASKS == 3
    assert (e420.OLDEST, e420.MIDDLE, e420.NEWEST) == (0, 1, 2)
    assert (e420.MIN_CELLS, e420.MIN_KINDS, e420.MIN_REPS) == (10, 3, 20)
    assert (e420.RECOVERY, e420.RECOVERY_FIRES, e420.RECOVERY_SIGMA) == (0.20, 0.10, 5.0)
    assert (e420.RATIO, e420.RATIO_FIRES) == (4.0, 2.0)
    assert (e420.SHARE, e420.SHARE_FIRES) == (0.5, 0.75)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e420_the_trade_is_a_constant.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e420.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e420.judge(d)}
    #: the cells being carried and the newest task being cost everywhere are structural facts
    assert verdicts["AU1"].startswith("MET") and verdicts["AU2"].startswith("MET"), verdicts
    assert len(d["cells"]) >= e420.MIN_CELLS and len(d["kinds"]) >= e420.MIN_KINDS, (len(d["cells"]), len(d["kinds"]))
    for n, c in d["cells"].items():
        assert c["replicates"] >= e420.MIN_REPS, n
        assert len(c["gain"]) == len(c["se"]) == len(c["sigma"]) == e420.N_TASKS, n
        assert c["gain"][e420.NEWEST] < 0.0, n
        #: the derived readings are the gains' own
        older = c["gain"][e420.OLDEST] + c["gain"][e420.MIDDLE]
        assert abs(c["coverage"] - older / c["newest_loss"]) < 1e-9, n
        assert abs(c["share"] - c["newest_loss"] / c["gain"][e420.OLDEST]) < 1e-9, n
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
