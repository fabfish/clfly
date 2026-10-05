"""`e434` writes the card's seventh revision and reads its new clause from the three artifacts that measured it, so the
tests pin both faces of the five claims, the refusal when one of those artifacts is absent, and the live re-framing the
unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e434_the_game_card_revision_seven as e434

#: the card's sixth revision, as `e428` wrote it: the draw's clauses, the buffer's, the penalty's, the trade's, the
#: order's and the controls'
REV6 = {
    "name": "the closed-loop earned-label game",
    "substrate": {"circuit": "mb+cx+al@n952", "circuit_size": 300, "support": 80},
    "loop": {"cue_at": 0, "drive": "action", "world_dims": 8, "coupled": True},
    "protocol": {"tasks": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "train": 96, "test": 48},
    "metrics": ["accuracy", "the retention matrix's diagonal", "its last row", "their difference"],
    "absent": ["a reward", "a policy", "an episode boundary", "a held-out task"],
    "arms": ["naive", "replay", "ewc-block"],
    "world": {"span_at_20": 0.075, "span_at_500": 0.3104, "worlds_measured": 6},
    "stream": {"span_at_500": 0.0323, "streams_measured": 3},
    "recovery": {"worlds_at_the_far_point": 5, "recovering": 1, "bar": 0.05},
    "invariance": {"reading": 0.6875, "spread": 0.0, "over_at_least": 10},
    "arm": {"budgets": [1, 20, 500], "worlds_measured": 6, "small_band": [-0.0174, 0.0365]},
    "draw_terms": {"draw_span_at_500": 0.0309, "least_gain_at_500": 0.1330, "gain_over_draw_span": 4.30},
    "penalty": {"arm": "ewc-block", "lam": 1.0, "replicates": 20, "accuracy_gain": 0.1764},
    "trade": {"far_cells": 12, "far_newest_cost": 12, "far_oldest_min": 0.2333},
    "terms": {"cells": 12, "oldest_learning": 0.0, "newest_retention": 0.0, "middle_ratio_min": 3.99},
    "arm_terms": {"retention_ratio_min": 7.13, "price_gap_max": 0.0344},
    "order": {"rolls": 16, "first_ahead": 16, "penalty_worst_middle": 9},
    "controls": {"frozen_body_cells": 3, "frozen_body_worst_gain": 0.0017, "frozen_bias_gain_ratio": 0.27},
}
PARAMETERS = {
    "artifact": ["e431_the_bias_ledger.json", "e433_the_penalties_hold_the_weights.json",
                 "e432_the_interference_runs_through_the_bias.json"],
    "cells": 207,
    "bias_ratio": {"replay": 0.9461, "ewc": 1.5076, "ewc-block": 1.4734, "ewc-block-rand": 1.4556},
    "bias_below_share": {"replay": 0.7863, "ewc": 0.0, "ewc-block": 0.0, "ewc-block-rand": 0.0526},
    "drift_ratio": {"replay": 0.9838, "ewc": 0.7184, "ewc-block": 0.7507, "ewc-block-rand": 0.752},
    "joint_share": {"replay": 0.0534, "ewc": 0.9091, "ewc-block": 0.8333, "ewc-block-rand": 0.7895},
    "channel_bias_share": {"cell": {"ewc-block": [0.7554, 0.8995], "naive": [0.3961, 0.4902],
                                    "replay": [0.4287, 0.4097]},
                           "pair/plastic": {"ewc": [0.9839, 0.9195], "ewc-block": [0.6520, 0.6252],
                                            "ewc-block-rand": [0.6106, 0.6792], "naive": [0.4524, 0.4359],
                                            "replay": [0.5863, 0.7395]}},
    "frozen_bias_max": 0.0,
}


def _sources(parameters):
    return {
        "bias": {a: {"mean_ratio": v, "below_share": parameters["bias_below_share"][a]}
                 for a, v in parameters["bias_ratio"].items()},
        "params": {a: {"mean_drift_ratio": parameters["drift_ratio"][a],
                       "both_share": parameters["joint_share"][a]}
                   for a in parameters["drift_ratio"]},
        "channel": {lbl: {a: {"share": list(v)} for a, v in arms.items()}
                    for lbl, arms in parameters["channel_bias_share"].items()}}


def _doc(parameters=None, revision=None, mutate=None, source_shift=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision6": {}, "parameters": {}, "sources": {}}
    parameters = json.loads(json.dumps(PARAMETERS if parameters is None else parameters))
    card = {k: json.loads(json.dumps(v)) for k, v in REV6.items()}
    card["revision"] = e434.REVISION if revision is None else revision
    card["parameters"] = parameters
    if mutate:
        card[mutate] = {"changed": True}
    sources = _sources(PARAMETERS)
    if source_shift:
        for path, value in source_shift.items():
            a, field = path.split("/")
            if a in sources["bias"] and field in sources["bias"][a]:
                sources["bias"][a][field] = value
            elif a in sources["params"]:
                sources["params"][a][field] = value
    return {"ok": True, "reason": None, "card": card,
            "revision6": {k: json.loads(json.dumps(v)) for k, v in REV6.items()},
            "parameters": parameters, "sources": sources}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e434.judge(_doc(**kw))}


def _parameters(**kw):
    out = json.loads(json.dumps(PARAMETERS))
    for k, v in kw.items():
        out[k] = v
    return out


def test_the_five_claims_read_both_faces():
    #: the revision-6 shape: the clauses carried, the parameters clause read off the three ledgers
    j = _judge()
    for cid in ("BJ1", "BJ2", "BJ3", "BJ4", "BJ5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BJ1: a clause changed that this revision does not rewrite, and a revision number that is not seven
    assert _judge(mutate="loop")["BJ1"].startswith("FALSIFIER")
    assert _judge(revision=6)["BJ1"].startswith("FALSIFIER")

    # BJ2: a bias ratio and a below-share that are not the ledger's
    ratios = dict(PARAMETERS["bias_ratio"], replay=0.80)
    assert _judge(parameters=_parameters(bias_ratio=ratios))["BJ2"].startswith("FALSIFIER")
    shares = dict(PARAMETERS["bias_below_share"], replay=0.50)
    assert _judge(parameters=_parameters(bias_below_share=shares))["BJ2"].startswith("FALSIFIER")

    # BJ3: a drift ratio that is not the ledger's
    drift = dict(PARAMETERS["drift_ratio"], ewc=0.50)
    assert _judge(parameters=_parameters(drift_ratio=drift))["BJ3"].startswith("FALSIFIER")

    # BJ4: a joint share that is not the artifact's
    joint = dict(PARAMETERS["joint_share"], replay=0.50)
    assert _judge(parameters=_parameters(joint_share=joint))["BJ4"].startswith("FALSIFIER")

    # BJ5: a channel share and the frozen side's maximum that are not the artifact's
    channel = json.loads(json.dumps(PARAMETERS["channel_bias_share"]))
    channel["pair/plastic"]["ewc"] = [0.50, 0.9195]
    assert _judge(parameters=_parameters(channel_bias_share=channel))["BJ5"].startswith("FALSIFIER")
    assert _judge(parameters=_parameters(frozen_bias_max=0.02))["BJ5"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e434.judge(_doc(ok=False)))


def test_the_artifacts_and_the_clause_are_registered():
    #: the revision-6 card and the three artifacts the new clause is read from
    assert e434.CARD6.name == "e428_the_game_card_revision_six.json"
    assert e434.BIAS.name == "e431_the_bias_ledger.json"
    assert e434.PARAMS.name == "e433_the_penalties_hold_the_weights.json"
    assert e434.CHANNEL.name == "e432_the_interference_runs_through_the_bias.json"
    assert e434.REVISION == 7 and e434.NEW == ("revision", "parameters")
    assert e434.ARMS == ("replay", "ewc", "ewc-block", "ewc-block-rand")
    assert e434.ROLLS == ("cell", "pair/plastic")
    assert (e434.TOL, e434.SHARE_TOL) == (0.002, 0.005)
    assert e434.EXPECTED == {"cells": 207, "frozen_max": 0.0}


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e434_the_game_card_revision_seven.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e434.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e434.judge(d)}
    #: the sixth revision being carried and the clause being the ledgers' own are structural facts
    assert verdicts["BJ1"].startswith("MET") and verdicts["BJ2"].startswith("MET"), verdicts
    card = d["card"]
    assert card["revision"] == e434.REVISION, card["revision"]
    for k in ("world", "stream", "recovery", "invariance", "arm", "draw_terms", "penalty", "trade", "terms",
              "arm_terms", "order", "controls", "parameters"):
        assert k in card, k
    par = card["parameters"]
    #: the clause points at the three artifacts that measured it and its four arms are the corpus's
    assert par["artifact"] == [e434.BIAS.name, e434.PARAMS.name, e434.CHANNEL.name]
    assert sorted(par["bias_ratio"]) == sorted(e434.ARMS), sorted(par["bias_ratio"])
    #: the two ledgers agree cell for cell on the bias ratio, which is why one clause can carry both
    for a in e434.ARMS:
        assert abs(par["bias_ratio"][a] - d["sources"]["bias"][a]["mean_ratio"]) < e434.TOL, a
        assert par["drift_ratio"][a] == d["sources"]["params"][a]["mean_drift_ratio"], a
    assert abs(par["frozen_bias_max"]) < 1e-9, par["frozen_bias_max"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
