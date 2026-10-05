"""`e431` reads every paired cell's bias ratio, so the tests pin both faces of the five claims, the null the matched
control lands in, the refusal when the corpus does not read, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e431_the_bias_ledger as e431

#: the corpus's shape: per arm, the cells, the directions and the mean ratio
BY_ARM = {
    "replay": {"cells": 131, "below": 103, "above": 28, "equal": 0, "mean_ratio": 0.946, "artifacts": 131,
               "replicates": [5, 10, 20, 40]},
    "ewc-block-rand": {"cells": 19, "below": 1, "above": 18, "equal": 0, "mean_ratio": 1.456, "artifacts": 19,
                       "replicates": [1, 5, 16, 40, 144]},
    "ewc-block": {"cells": 24, "below": 0, "above": 24, "equal": 0, "mean_ratio": 1.473, "artifacts": 24,
                  "replicates": [1, 5, 16, 20, 40, 144]},
    "ewc": {"cells": 33, "below": 0, "above": 31, "equal": 2, "mean_ratio": 1.508, "artifacts": 33,
            "replicates": [5, 10, 16, 40]},
}


def _arm(spec):
    out = dict(spec)
    out["at_or_above"] = out["above"] + out["equal"]
    out["at_or_above_share"] = out["at_or_above"] / out["cells"] if out["cells"] else 0.0
    out["below_share"] = out["below"] / out["cells"] if out["cells"] else 0.0
    return out


def _doc(by=None, cells=None, artifacts=None, frozen=16, collapsed=24, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "by_arm": {}, "frozen_cells": 0, "collapsed": 0,
                "spans": {}}
    by = {a: _arm(v) for a, v in (BY_ARM if by is None else by).items()}
    total = cells if cells is not None else sum(v["cells"] for v in by.values())
    return {"ok": True, "reason": None, "cells": [], "by_arm": by, "frozen_cells": frozen, "collapsed": collapsed,
            "spans": {"cells": total, "artifacts": artifacts if artifacts is not None else 159,
                      "arms": sorted(by), "frozen_cells": frozen, "buffer_cells": by.get("replay", {}).get("cells", 0)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e431.judge(_doc(**kw))}


def _with(arm, **kw):
    out = {k: dict(v) for k, v in BY_ARM.items()}
    out[arm].update(kw)
    return out


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the buffer below the baseline in most cells, the penalties above it in nearly all
    j = _judge()
    assert j["BG1"].startswith("MET") and j["BG3"].startswith("MET"), j
    assert j["BG4"].startswith("MET") and j["BG5"].startswith("MET"), j
    #: and the second claim's own outcome is a null, the matched control landing just under its bar
    assert j["BG2"].startswith("NULL"), j["BG2"]

    # BG1: too few cells, artifacts, arms and buffer cells
    assert _judge(cells=150)["BG1"].startswith("FALSIFIER")
    assert _judge(artifacts=10)["BG1"].startswith("FALSIFIER")
    assert _judge(by={"replay": BY_ARM["replay"], "ewc": BY_ARM["ewc"]})["BG1"].startswith("FALSIFIER")
    assert _judge(by={**{k: v for k, v in BY_ARM.items() if k != "replay"}, "replay": {**BY_ARM["replay"],
                                                                                     "cells": 50}})["BG1"].startswith("FALSIFIER")

    # BG2: a penalty arm under the falsifier bar, and one between the bars
    assert _judge(by=_with("ewc-block", cells=20, above=15, below=5))["BG2"].startswith("FALSIFIER")
    assert _judge(by=_with("ewc-block", cells=20, above=17, below=3))["BG2"].startswith("NULL")

    # BG3: a penalty arm whose mean ratio is under the bars
    assert _judge(by=_with("ewc", mean_ratio=1.1))["BG3"].startswith("FALSIFIER")
    assert _judge(by=_with("ewc", mean_ratio=1.3))["BG3"].startswith("NULL")

    # BG4: a buffer below the baseline in too few cells
    assert _judge(by=_with("replay", cells=100, below=40, above=60))["BG4"].startswith("FALSIFIER")
    assert _judge(by=_with("replay", cells=100, below=60, above=40))["BG4"].startswith("NULL")

    # BG5: a buffer whose mean ratio is not below one
    assert _judge(by=_with("replay", mean_ratio=1.20))["BG5"].startswith("FALSIFIER")
    assert _judge(by=_with("replay", mean_ratio=1.01))["BG5"].startswith("NULL")

    #: the corpus not reading refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e431.judge(_doc(ok=False)))


def test_the_root_and_the_thresholds_are_registered():
    #: the glob's root, the baseline, and the four arms the ledger pools
    assert e431.ROOT == Path("runs")
    assert e431.BASELINE == "naive" and e431.BUFFER == "replay"
    assert e431.PENALTIES == ("ewc", "ewc-block", "ewc-block-rand")
    assert e431.FIELD == "bias_from_zero" and e431.MIN_REPS == 1
    assert (e431.MIN_CELLS, e431.MIN_ARTIFACTS, e431.MIN_ARMS, e431.MIN_BUFFER) == (200, 20, 4, 100)
    assert (e431.PENALTY_SHARE, e431.PENALTY_FIRES) == (0.95, 0.85)
    assert (e431.RATIO, e431.RATIO_FIRES) == (1.4, 1.2)
    assert (e431.BUFFER_SHARE, e431.BUFFER_FIRES) == (0.70, 0.50)
    assert (e431.BUFFER_RATIO, e431.BUFFER_RATIO_FIRES) == (1.0, 1.05)


def test_the_live_ledger_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e431_the_bias_ledger.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e431.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e431.judge(d)}
    #: the ledger being carried and the buffer's mean ratio being below one are structural facts
    assert verdicts["BG1"].startswith("MET") and verdicts["BG5"].startswith("MET"), verdicts
    assert len(d["by_arm"]) >= 4, sorted(d["by_arm"])
    assert d["spans"]["buffer_cells"] == d["by_arm"]["replay"]["cells"], d["spans"]
    for arm, got in d["by_arm"].items():
        #: each arm's derived shares are its own counts
        assert got["at_or_above"] == got["above"] + got["equal"], arm
        assert abs(got["at_or_above_share"] - got["at_or_above"] / got["cells"]) < 1e-9, arm
        assert abs(got["below_share"] - got["below"] / got["cells"]) < 1e-9, arm
    assert d["by_arm"]["replay"]["mean_ratio"] < 1.0, d["by_arm"]["replay"]
    assert all(got["mean_ratio"] > 1.0 for arm, got in d["by_arm"].items() if arm != "replay"), d["by_arm"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
