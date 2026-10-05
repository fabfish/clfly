"""`e421` reads the per-task gains of the same twelve cells at twenty updates and at five hundred, so the tests pin
both faces of the five claims, the refusal when a cell is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e421_the_trade_turns_on as e421

#: the corpus's shape: per cell, its kind and the three per-task gains at twenty updates and at five hundred
GAINS = {
    "card": ("card", (0.0198, -0.0073, -0.0260), (0.2896, 0.2490, -0.0604)),
    "cue1": ("cue", (0.0115, 0.0104, -0.0156), (0.2635, 0.2000, -0.0646)),
    "cue3": ("cue", (0.0604, 0.0354, +0.0083), (0.3021, 0.2188, -0.0740)),
    "cue6": ("cue", (0.0354, 0.0406, +0.0333), (0.3156, 0.2500, -0.1031)),
    "cue9": ("cue", (0.0354, 0.0469, +0.0042), (0.3042, 0.2458, -0.0781)),
    "cue14": ("cue", (0.0354, 0.0125, -0.0427), (0.2813, 0.2219, -0.0427)),
    "world1": ("world", (0.0552, 0.0354, -0.0302), (0.3198, 0.2552, -0.0479)),
    "world2": ("world", (0.0250, 0.0135, -0.0115), (0.2615, 0.1479, -0.0563)),
    "world3": ("world", (0.0125, 0.0667, -0.0010), (0.3021, 0.2385, -0.0115)),
    "world4": ("world", (0.0750, 0.0021, +0.0250), (0.2615, 0.2604, -0.0656)),
    "stream1": ("stream", (0.0229, 0.0135, -0.0260), (0.3219, 0.2323, -0.0927)),
    "stream2": ("stream", (0.0219, 0.0271, -0.0052), (0.2333, 0.2240, -0.0802)),
}
UNPAIRED = (0.0708, -0.0208, 0.0396)


def _end(gains, reps=20):
    gains = list(gains)
    older = gains[e421.OLDEST] + gains[e421.MIDDLE]
    loss = -gains[e421.NEWEST]
    return {"artifact": "x.json", "replicates": reps, "naive_final": [0.3, 0.4, 0.5],
            "replay_final": [0.3 + gains[k] for k in range(e421.N_TASKS)], "gain": gains, "newest_loss": loss,
            "coverage": (older / loss) if loss > 0 else None}


def _doc(spec=None, reps=20, unpaired=UNPAIRED, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": {}, "kinds": {}, "unpaired": None, "spans": {}}
    spec = GAINS if spec is None else spec
    cells, kinds = {}, {}
    for name, (kind, near, far) in spec.items():
        cells[name] = {"kind": kind, e421.NEAR: _end(near, reps), e421.FAR: _end(far, reps)}
        kinds.setdefault(kind, []).append(name)
    near = [c[e421.NEAR]["gain"][e421.NEWEST] for c in cells.values()]
    far = [c[e421.FAR]["gain"][e421.NEWEST] for c in cells.values()]
    return {"ok": True, "reason": None, "cells": cells, "kinds": kinds,
            "unpaired": ({"artifact": "stream3.json", "gain": list(unpaired), "coverage": None}
                         if unpaired else None),
            "spans": {"cells": len(cells), "kinds": sorted(kinds),
                      "near_negative": sum(1 for x in near if x < 0), "near_positive": sum(1 for x in near if x > 0),
                      "far_negative": sum(1 for x in far if x < 0),
                      "near_oldest_max": max(c[e421.NEAR]["gain"][e421.OLDEST] for c in cells.values()),
                      "far_oldest_min": min(c[e421.FAR]["gain"][e421.OLDEST] for c in cells.values()),
                      "near_coverage_min": min([c[e421.NEAR]["coverage"] for c in cells.values()
                                                 if c[e421.NEAR]["coverage"] is not None] or [None]),
                      "near_without_loss": sum(1 for c in cells.values() if c[e421.NEAR]["coverage"] is None),
                      "far_coverage_min": min([c[e421.FAR]["coverage"] for c in cells.values()
                                                if c[e421.FAR]["coverage"] is not None] or [None]),
                      "replicates": sorted({c[e]["replicates"] for c in cells.values()
                                            for e in (e421.NEAR, e421.FAR)})}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e421.judge(_doc(**kw))}


def _with(name, near=None, far=None):
    out = {k: (kind, tuple(n), tuple(f)) for k, (kind, n, f) in GAINS.items()}
    kind = out[name][0]
    out[name] = (kind, tuple(near) if near is not None else out[name][1],
                 tuple(far) if far is not None else out[name][2])
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: twelve paired cells, the newest task mixed at twenty and cost at five hundred
    j = _judge()
    for cid in ("AV1", "AV2", "AV3", "AV4", "AV5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AV1: too few replicates, too few kinds, and too few cells
    assert _judge(reps=19)["AV1"].startswith("FALSIFIER")
    two_kinds = {k: v for k, v in GAINS.items() if v[0] in ("card", "cue")}
    assert _judge(spec=two_kinds)["AV1"].startswith("FALSIFIER")
    assert _judge(spec={k: v for k, v in list(GAINS.items())[:8]})["AV1"].startswith("FALSIFIER")

    # AV2: a near band whose newest task is cost everywhere
    all_cost = {k: (kind, (n[0], n[1], -abs(n[2]) if n[2] else -0.001), f) for k, (kind, n, f) in GAINS.items()}
    assert _judge(spec=all_cost)["AV2"].startswith("FALSIFIER")

    # AV3: a cell whose newest task is not cost at five hundred
    assert _judge(spec=_with("card", far=(0.2896, 0.2490, +0.01)))["AV3"].startswith("FALSIFIER")

    # AV4: a near recovery over its limit, a far recovery under its bar, and one between the bars
    assert _judge(spec=_with("card", near=(0.25, -0.0073, -0.0260)))["AV4"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", far=(0.05, 0.2490, -0.0604)))["AV4"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", near=(0.15, -0.0073, -0.0260)))["AV4"].startswith("NULL")

    # AV5: a near band whose least coverage is over the bar, and one between the bars
    flat = {k: (kind, (0.10, 0.10, -0.02), f) for k, (kind, n, f) in GAINS.items()}
    assert _judge(spec=flat)["AV5"].startswith("FALSIFIER")
    assert _judge(spec=_with("card", near=(0.03, 0.01, -0.0260)))["AV5"].startswith("NULL")
    #: a cell's run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e421.judge(_doc(ok=False)))


def test_the_runs_and_the_thresholds_are_registered():
    #: the twelve cells, each with a twenty-update run and its five-hundred-update partner
    assert len(e421.RUNS) == 12 and sorted(e421.RUNS) == sorted(GAINS), sorted(e421.RUNS)
    for n, (near, far) in e421.RUNS.items():
        assert "iters20" in near.name, n
        assert "iters500" in far.name or "e380" in far.name, n
        assert e421.KIND[n] in ("card", "world", "stream", "cue"), n
    assert "stream3" in e421.UNPAIRED.name
    assert e421.ARMS == ("naive", "replay") and e421.N_TASKS == 3
    assert (e421.OLDEST, e421.MIDDLE, e421.NEWEST) == (0, 1, 2)
    assert (e421.MIN_CELLS, e421.MIN_KINDS, e421.MIN_REPS) == (10, 3, 20)
    assert (e421.NEAR_BAR, e421.NEAR_LIMIT, e421.FAR_BAR, e421.FAR_FIRES) == (0.10, 0.20, 0.20, 0.10)
    assert (e421.COVERAGE_NEAR, e421.COVERAGE_FAR, e421.COVERAGE_FIRES) == (1.0, 5.0, 2.0)


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e421_the_trade_turns_on.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e421.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e421.judge(d)}
    #: the pairing being carried and the far end being cost everywhere are structural facts
    assert verdicts["AV1"].startswith("MET") and verdicts["AV3"].startswith("MET"), verdicts
    assert len(d["cells"]) >= e421.MIN_CELLS and len(d["kinds"]) >= e421.MIN_KINDS, (len(d["cells"]), len(d["kinds"]))
    for n, c in d["cells"].items():
        for e in (e421.NEAR, e421.FAR):
            assert c[e]["replicates"] >= e421.MIN_REPS, (n, e)
            assert len(c[e]["gain"]) == e421.N_TASKS, (n, e)
        assert c[e421.FAR]["gain"][e421.NEWEST] < 0.0, n
        #: the coverage is the two older gains over the newest loss, and absent where there is no loss
        for e in (e421.NEAR, e421.FAR):
            older = c[e]["gain"][e421.OLDEST] + c[e]["gain"][e421.MIDDLE]
            if c[e]["newest_loss"] > 0:
                assert abs(c[e]["coverage"] - older / c[e]["newest_loss"]) < 1e-9, (n, e)
            else:
                assert c[e]["coverage"] is None, (n, e)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
