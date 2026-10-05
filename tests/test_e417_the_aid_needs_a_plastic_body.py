"""`e417` reads the corpus's own frozen-body cells beside its plastic ones, so the tests pin both faces of the five
claims, the refusal when the frozen pair is absent, and the live re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e417_the_aid_needs_a_plastic_body as e417


def _cell(artifact, naive, gain, cut, reps, frozen):
    return {"artifact": artifact, "replicates": reps, "naive_accuracy": naive, "gain": gain, "cut": cut,
            "frozen_body": frozen, "lr": 0.003, "circuit_size": 300}


def _ledger(n_plastic=152, n_aided=4, n_frozen=3, frozen_reps=20, frozen_gain=0.0007, frozen_cut=0.0,
            aided_gain=0.15, aided_level=0.52):
    plastic = []
    for i in range(n_plastic):
        if i < n_aided:
            plastic.append(_cell(f"plastic_{i}.json", aided_level, +aided_gain, +0.20, 20, False))
        else:
            plastic.append(_cell(f"plastic_{i}.json", 0.70, +0.02, +0.03, 5, False))
    frozen = [_cell(f"frozen_{i}.json", 0.61 + 0.01 * i, frozen_gain, frozen_cut, frozen_reps, True)
              for i in range(n_frozen)]
    return plastic, frozen


def _pair(a_acc=0.4490, b_acc=0.6455, a_gain=-0.0017, b_gain=0.0007, differing=("lr",), same=True, absent=False):
    if absent:
        return {"artifacts": ["e375.json", "e376.json"], "absent": True}
    return {"artifacts": ["e375_earned_label_frozenbody_cue8_actionsource_20reps.json",
                          "e376_earned_label_frozenbody_lr03_cue8_actionsource_20reps.json"],
            "absent": False, "differing_config": list(differing), "same_draws": same,
            "a": {"naive_accuracy": a_acc, "gain": a_gain, "cut": 0.0, "replicates": 20, "frozen_body": True},
            "b": {"naive_accuracy": b_acc, "gain": b_gain, "cut": 0.0, "replicates": 20, "frozen_body": True}}


def _doc(plastic=None, frozen=None, pair=None, collapsed=24, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "cells": [], "frozen": [], "plastic": [], "pair": None,
                "collapsed": 0}
    base_plastic, base_frozen = _ledger()
    plastic = base_plastic if plastic is None else plastic
    frozen = base_frozen if frozen is None else frozen
    pair = _pair() if pair is None else pair
    return {"ok": True, "reason": None, "cells": list(plastic) + list(frozen), "frozen": list(frozen),
            "plastic": list(plastic), "pair": pair, "collapsed": collapsed}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e417.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus's shape: the ledger carried, the frozen bodies worth nothing, the plastic ones worth a tenth
    j = _judge()
    for cid in ("AN1", "AN2", "AN3", "AN4", "AN5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AN1: too few cells, too few frozen bodies, and a frozen cell under the replicate bound
    small, frozen = _ledger(n_plastic=100)
    assert _judge(plastic=small, frozen=frozen)["AN1"].startswith("FALSIFIER")
    assert _judge(frozen=frozen[:2])["AN1"].startswith("FALSIFIER")
    thin = [_cell("thin.json", 0.61, 0.0, 0.0, 5, True)]
    assert _judge(frozen=thin)["AN1"].startswith("FALSIFIER")

    # AN2: a frozen body the buffer moves, and one between the bars
    assert _judge(frozen=[_cell("f.json", 0.61, 0.03, 0.0, 20, True)])["AN2"].startswith("NULL")
    assert _judge(frozen=[_cell("f.json", 0.61, 0.08, 0.0, 20, True)])["AN2"].startswith("FALSIFIER")

    # AN3: a frozen body whose forgetting the buffer moves
    assert _judge(frozen=[_cell("f.json", 0.61, 0.0, 0.02, 20, True)])["AN3"].startswith("FALSIFIER")

    # AN4: no plastic cell below the level worth a tenth
    quiet, frozen = _ledger(n_aided=0)
    assert _judge(plastic=quiet, frozen=frozen)["AN4"].startswith("FALSIFIER")
    # ... and one below the level whose gain is under the bar
    weak, frozen = _ledger(n_aided=4, aided_gain=0.05)
    assert _judge(plastic=weak, frozen=frozen)["AN4"].startswith("FALSIFIER")

    # AN5: the pair absent, its gains apart, its levels together, and a differing field that is not the step size
    assert _judge(pair=_pair(absent=True))["AN5"].startswith("REFUSED")
    assert _judge(pair=_pair(b_gain=0.05))["AN5"].startswith("FALSIFIER")
    assert _judge(pair=_pair(b_acc=0.46))["AN5"].startswith("FALSIFIER")
    assert _judge(pair=_pair(differing=("lr", "batch")))["AN5"].startswith("FALSIFIER")

    #: the corpus not reading refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e417.judge(_doc(ok=False)))


def test_the_ledger_and_the_thresholds_are_registered():
    #: the glob's root, the two arms a cell must carry, and the frozen-body pair the fifth claim is about
    assert e417.ROOT == Path("runs")
    assert e417.REQUIRED == ("naive", "replay")
    assert len(e417.FROZEN_PAIR) == 2 and all("frozenbody" in p.name for p in e417.FROZEN_PAIR)
    assert e417.RUN_FIELDS == ("json_out", "save_theta")
    assert (e417.MIN_REPS, e417.FROZEN_REPS) == (5, 20)
    assert (e417.MIN_CELLS, e417.MIN_FROZEN) == (150, 3)
    assert (e417.ZERO, e417.ZERO_FIRES, e417.CUT_ZERO) == (0.01, 0.05, 0.005)
    assert (e417.PLASTIC, e417.LEVEL) == (0.10, 0.58)
    assert (e417.LEVEL_SPLIT, e417.LEVEL_GAIN_DIFF) == (0.05, 0.02)


def test_the_live_ledger_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e417_the_aid_needs_a_plastic_body.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e417.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e417.judge(d)}
    #: the ledger being carried and the frozen bodies being worth nothing are structural facts
    assert verdicts["AN1"].startswith("MET") and verdicts["AN2"].startswith("MET"), verdicts
    assert len(d["cells"]) >= e417.MIN_CELLS and len(d["frozen"]) >= e417.MIN_FROZEN, (len(d["cells"]),
                                                                                      len(d["frozen"]))
    assert all(c["frozen_body"] for c in d["frozen"]) and not any(c["frozen_body"] for c in d["plastic"])
    assert all(c["replicates"] >= e417.MIN_REPS for c in d["cells"])
    #: the frozen pair's two artifacts are on disk and differ in the step size alone
    assert d["pair"]["differing_config"] == ["lr"] and d["pair"]["same_draws"], d["pair"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
