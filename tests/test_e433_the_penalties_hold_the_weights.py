"""`e433` reads each arm's weight drift beside its bias distance, so the tests pin both faces of the five claims, the
refusal when the corpus does not read, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e433_the_penalties_hold_the_weights as e433

#: the corpus's shape: per arm, the cells, the two shares and the two mean ratios
BY_ARM = {
    "ewc": {"cells": 33, "artifacts": 33, "held": 30, "pushed": 31, "both": 30,
            "mean_drift_ratio": 0.718, "mean_bias_ratio": 1.508},
    "ewc-block": {"cells": 24, "artifacts": 24, "held": 20, "pushed": 24, "both": 20,
                  "mean_drift_ratio": 0.751, "mean_bias_ratio": 1.473},
    "ewc-block-rand": {"cells": 19, "artifacts": 19, "held": 15, "pushed": 18, "both": 15,
                       "mean_drift_ratio": 0.752, "mean_bias_ratio": 1.456},
    "replay": {"cells": 131, "artifacts": 131, "held": 96, "pushed": 28, "both": 7,
               "mean_drift_ratio": 0.984, "mean_bias_ratio": 0.946},
}


def _arm(spec):
    out = dict(spec)
    out["held_share"] = out["held"] / out["cells"] if out["cells"] else 0.0
    out["both_share"] = out["both"] / out["cells"] if out["cells"] else 0.0
    return out


def _doc(by=None, cells=None, artifacts=None, collapsed=24, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "by_arm": {}, "collapsed": 0, "spans": {}}
    by = {a: _arm(v) for a, v in (BY_ARM if by is None else by).items()}
    total = cells if cells is not None else sum(v["cells"] for v in by.values())
    return {"ok": True, "reason": None, "cells": [], "by_arm": by, "collapsed": collapsed,
            "spans": {"cells": total, "artifacts": artifacts if artifacts is not None else 159,
                      "arms": sorted(by), "buffer_cells": by.get("replay", {}).get("cells", 0)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e433.judge(_doc(**kw))}


def _with(arm, **kw):
    out = {k: dict(v) for k, v in BY_ARM.items()}
    out[arm].update(kw)
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the penalties holding the weights by a fifth and the buffer moving both least
    j = _judge()
    for cid in ("BI1", "BI2", "BI3", "BI4", "BI5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BI1: too few cells, artifacts, arms and buffer cells
    assert _judge(cells=150)["BI1"].startswith("FALSIFIER")
    assert _judge(artifacts=10)["BI1"].startswith("FALSIFIER")
    assert _judge(by={"replay": BY_ARM["replay"], "ewc": BY_ARM["ewc"]})["BI1"].startswith("FALSIFIER")
    short = {"replay": {**BY_ARM["replay"], "cells": 50}, "ewc": BY_ARM["ewc"],
             "ewc-block": BY_ARM["ewc-block"], "ewc-block-rand": BY_ARM["ewc-block-rand"]}
    assert _judge(by=short)["BI1"].startswith("FALSIFIER")

    # BI2: a penalty that holds the weights in too few cells, and one between the bars
    assert _judge(by=_with("ewc", cells=20, held=8))["BI2"].startswith("FALSIFIER")
    assert _judge(by=_with("ewc", cells=20, held=10))["BI2"].startswith("NULL")

    # BI3: a penalty whose mean drift ratio is under the bars
    assert _judge(by=_with("ewc", mean_drift_ratio=0.95))["BI3"].startswith("FALSIFIER")
    assert _judge(by=_with("ewc", mean_drift_ratio=0.85))["BI3"].startswith("NULL")

    # BI4: a penalty whose two parameters do not move opposite ways often enough
    assert _judge(by=_with("ewc", cells=20, both=8))["BI4"].startswith("FALSIFIER")

    # BI5: a buffer whose joint share is between the bars, and one over them
    assert _judge(by=_with("replay", cells=100, both=25))["BI5"].startswith("NULL")
    assert _judge(by=_with("replay", cells=100, both=40))["BI5"].startswith("FALSIFIER")

    #: the corpus not reading refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e433.judge(_doc(ok=False)))


def test_the_root_and_the_thresholds_are_registered():
    #: the glob's root, the two fields, the baseline and the arms the ledger pools
    assert e433.ROOT == Path("runs")
    assert e433.BASELINE == "naive" and e433.BUFFER == "replay"
    assert e433.PENALTIES == ("ewc", "ewc-block", "ewc-block-rand")
    assert (e433.DRIFT, e433.BIAS) == ("theta_drift", "bias_from_zero")
    assert (e433.MIN_CELLS, e433.MIN_ARTIFACTS, e433.MIN_ARMS, e433.MIN_BUFFER) == (200, 20, 4, 100)
    assert (e433.HOLD_SHARE, e433.HOLD_FIRES) == (0.60, 0.45)
    assert (e433.HOLD_RATIO, e433.HOLD_RATIO_FIRES) == (0.8, 0.9)
    assert (e433.JOINT_SHARE, e433.JOINT_FIRES) == (0.60, 0.45)
    assert (e433.BUFFER_JOINT, e433.BUFFER_JOINT_FIRES) == (0.20, 0.35)


def test_the_live_ledger_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e433_the_penalties_hold_the_weights.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e433.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e433.judge(d)}
    #: the ledger being carried and the penalties holding the weights are structural facts
    assert verdicts["BI1"].startswith("MET") and verdicts["BI2"].startswith("MET"), verdicts
    assert len(d["by_arm"]) >= 4, sorted(d["by_arm"])
    for arm, got in d["by_arm"].items():
        #: each arm's shares are its own counts
        assert got["held_share"] == got["held"] / got["cells"], arm
        assert got["both_share"] == got["both"] / got["cells"], arm
        assert got["both"] <= min(got["held"], got["pushed"]), arm
    #: the penalties hold the weights and push the bias, the buffer moves both less than one
    for arm in e433.PENALTIES:
        assert d["by_arm"][arm]["mean_drift_ratio"] < 0.8, arm
        assert d["by_arm"][arm]["mean_bias_ratio"] > 1.0, arm
    assert d["by_arm"]["replay"]["mean_bias_ratio"] < 1.0, d["by_arm"]["replay"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
