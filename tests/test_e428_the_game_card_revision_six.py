"""`e428` writes the card's sixth revision and reads each new clause from the artifacts that measured it, so the tests
pin both faces of the five claims, the refusal when one of those artifacts is absent, and the live re-framing the unit
produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e428_the_game_card_revision_six as e428

#: the card's fifth revision, as `e424` wrote it: the draw's clauses, the buffer's, the penalty's and the trade's
REV5 = {
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
}
ORDER = {
    "artifact": ["e425_the_trade_follows_the_position.json", "e426_the_damage_lands_by_arm.json"],
    "configs": 3, "rolls": 16, "position_contrast_min": 0.05833, "reversal_costs": [-0.0694, -0.0618, -0.0028],
    "first_ahead": 16, "first_positive": 15, "buffer_positive_means": 6, "buffer_rolls": 6,
    "penalty_negative_means": 10, "penalty_rolls": 10, "buffer_worst_last": 6, "penalty_worst_middle": 9,
}
CONTROLS = {
    "artifact": ["e417_the_aid_needs_a_plastic_body.json", "e427_most_of_the_aid_needs_a_plastic_bias.json"],
    "frozen_body_cells": 3, "frozen_body_worst_gain": 0.001736, "frozen_body_worst_cut": 0.0,
    "frozen_bias_gain_ratio": 0.268817, "frozen_bias_cut_ratio": 0.265781,
    "frozen_bias_naive_forgetting_drop": 0.052344,
}


def _doc(order=None, controls=None, revision=None, mutate=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision5": {}, "order": {}, "controls": {}}
    card = {k: json.loads(json.dumps(v)) for k, v in REV5.items()}
    card["revision"] = e428.REVISION if revision is None else revision
    card["order"] = dict(ORDER if order is None else order)
    card["controls"] = dict(CONTROLS if controls is None else controls)
    if mutate:
        card[mutate] = {"changed": True}
    return {"ok": True, "reason": None, "card": card,
            "revision5": {k: json.loads(json.dumps(v)) for k, v in REV5.items()},
            "order": dict(ORDER if order is None else order),
            "controls": dict(CONTROLS if controls is None else controls)}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e428.judge(_doc(**kw))}


def _with(base, **kw):
    out = dict(base)
    out.update(kw)
    return out


def test_the_five_claims_read_both_faces():
    #: the revision-5 shape: the clauses carried, the order clause and the two controls read off the runs
    j = _judge()
    for cid in ("BD1", "BD2", "BD3", "BD4", "BD5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BD1: a clause changed that this revision does not rewrite, and a revision number that is not six
    assert _judge(mutate="loop")["BD1"].startswith("FALSIFIER")
    assert _judge(revision=5)["BD1"].startswith("FALSIFIER")

    # BD2: a configuration count, a roll count, a weak contrast, an arm-roll not ahead, the buffer's mean, and the
    # reversal's costs, each off the artifacts' own
    assert _judge(order=_with(ORDER, configs=2))["BD2"].startswith("FALSIFIER")
    assert _judge(order=_with(ORDER, rolls=15))["BD2"].startswith("FALSIFIER")
    assert _judge(order=_with(ORDER, position_contrast_min=0.03))["BD2"].startswith("FALSIFIER")
    assert _judge(order=_with(ORDER, first_ahead=15))["BD2"].startswith("FALSIFIER")
    assert _judge(order=_with(ORDER, buffer_positive_means=5))["BD2"].startswith("FALSIFIER")
    assert _judge(order=_with(ORDER, reversal_costs=[-0.0694, -0.0618, -0.05]))["BD2"].startswith("FALSIFIER")

    # BD3: where each arm's damage falls, off the artifact's own counts
    assert _judge(order=_with(ORDER, buffer_worst_last=5))["BD3"].startswith("FALSIFIER")
    assert _judge(order=_with(ORDER, penalty_worst_middle=7))["BD3"].startswith("FALSIFIER")

    # BD4: the frozen-body half
    assert _judge(controls=_with(CONTROLS, frozen_body_cells=2))["BD4"].startswith("FALSIFIER")
    assert _judge(controls=_with(CONTROLS, frozen_body_worst_gain=0.02))["BD4"].startswith("FALSIFIER")
    assert _judge(controls=_with(CONTROLS, frozen_body_worst_cut=0.01))["BD4"].startswith("FALSIFIER")

    # BD5: the frozen-bias half
    assert _judge(controls=_with(CONTROLS, frozen_bias_gain_ratio=0.5))["BD5"].startswith("FALSIFIER")
    assert _judge(controls=_with(CONTROLS, frozen_bias_naive_forgetting_drop=0.02))["BD5"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e428.judge(_doc(ok=False)))


def test_the_artifacts_and_the_clauses_are_registered():
    #: the revision-5 card and the four artifacts the new clauses are read from
    assert e428.CARD5.name == "e424_the_game_card_revision_five.json"
    assert e428.POSITION.name == "e425_the_trade_follows_the_position.json"
    assert e428.ARMS.name == "e426_the_damage_lands_by_arm.json"
    assert e428.BODY.name == "e417_the_aid_needs_a_plastic_body.json"
    assert e428.BIAS.name == "e427_most_of_the_aid_needs_a_plastic_bias.json"
    assert e428.REVISION == 6 and e428.NEW == ("revision", "order", "controls")
    assert (e428.TOL, e428.RATIO_TOL) == (0.002, 0.01)
    assert e428.EXPECTED["rolls"] == 16 and e428.EXPECTED["configs"] == 3
    assert e428.EXPECTED["frozen_cells"] == 3 and e428.EXPECTED["gain_ratio"] == 0.27
    assert e428.EXPECTED["penalty_worst_middle"] == 9 and e428.EXPECTED["buffer_worst_last"] == 6


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e428_the_game_card_revision_six.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e428.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e428.judge(d)}
    #: the fifth revision being carried and the order clause being the artifacts' own are structural facts
    assert verdicts["BD1"].startswith("MET") and verdicts["BD2"].startswith("MET"), verdicts
    card = d["card"]
    assert card["revision"] == e428.REVISION, card["revision"]
    for k in ("world", "stream", "recovery", "invariance", "arm", "draw_terms", "penalty", "trade", "terms",
              "arm_terms", "order", "controls"):
        assert k in card, k
    #: the clauses' numbers are read, not stated: each points at the artifacts that measured them
    assert card["order"]["artifact"] == [e428.POSITION.name, e428.ARMS.name]
    assert card["controls"]["artifact"] == [e428.BODY.name, e428.BIAS.name]
    assert card["order"]["rolls"] == e428.EXPECTED["rolls"]
    assert abs(card["controls"]["frozen_bias_gain_ratio"] - e428.EXPECTED["gain_ratio"]) < e428.RATIO_TOL
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
