"""`e424` writes the card's fifth revision and reads every new clause from the artifact that measured it, so the tests
pin both faces of the five claims, the refusal when one of those artifacts is absent, and the live re-framing the unit
produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e424_the_game_card_revision_five as e424

#: the card's fourth revision, as `e418` wrote it: the draw's clauses, the buffer's, the penalty clause and the arms
REV4 = {
    "name": "the closed-loop earned-label game",
    "substrate": {"circuit": "mb+cx+al@n952", "circuit_size": 300, "support": 80},
    "loop": {"cue_at": 0, "drive": "action", "world_dims": 8, "coupled": True},
    "protocol": {"tasks": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "train": 96, "test": 48},
    "metrics": ["accuracy", "the retention matrix's diagonal", "its last row", "their difference"],
    "absent": ["a reward", "a policy", "an episode boundary", "a held-out task"],
    "arms": ["naive", "replay", "ewc-block"],
    "world": {"span_at_20": 0.075, "span_at_500": 0.3104, "worlds_measured": 6},
    "stream": {"span_at_500": 0.0323, "against_the_worlds": 0.3344, "streams_measured": 3},
    "recovery": {"worlds_at_the_far_point": 5, "recovering": 1, "bar": 0.05},
    "invariance": {"reading": 0.6875, "spread": 0.0, "over_at_least": 10},
    "arm": {"budgets": [1, 20, 500], "worlds_measured": 6, "small_band": [-0.0174, 0.0365]},
    "draw_terms": {"draw_span_at_500": 0.0309, "least_gain_at_500": 0.1330, "gain_over_draw_span": 4.30},
    "penalty": {"arm": "ewc-block", "lam": 1.0, "replicates": 20, "accuracy_gain": 0.1764},
}
TRADE = {"artifact": ["e420_the_trade_is_a_constant.json", "e421_the_trade_turns_on.json"],
         "far_cells": 12, "far_newest_cost": 12, "far_oldest_min": 0.23333333432674408,
         "far_coverage_min": 5.484848470398875, "far_oldest_max": 0.3218750059604645,
         "far_loss_min": 0.011458337306976318, "far_loss_max": 0.103125,
         "near_cells": 13, "near_newest_cost": 8, "near_oldest_max": 0.0749999977648258}
TERMS = {"artifact": "e422_the_buffer_buys_retention.json", "cells": 12, "oldest_learning": 0.0,
         "newest_retention": 0.0, "oldest_retention_min": 0.23333333432674414,
         "newest_learning_worst": -0.011458337306976318, "middle_ratio_min": 3.9861111938953417}
ARM = {"artifact": "e423_the_penalty_buys_a_tenth.json", "retention_ratio_min": 7.128205670877801,
       "retention_ratio_max": 9.749998192702375, "price_gap_max": 0.03436}


def _doc(trade=None, terms=None, arm=None, revision=None, mutate=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision4": {}, "trade": {}, "terms": {},
                "arm_terms": {}}
    card = {k: json.loads(json.dumps(v)) for k, v in REV4.items()}
    card["revision"] = e424.REVISION if revision is None else revision
    card["trade"] = dict(TRADE if trade is None else trade)
    card["terms"] = dict(TERMS if terms is None else terms)
    card["arm_terms"] = dict(ARM if arm is None else arm)
    if mutate:
        card[mutate] = {"changed": True}
    return {"ok": True, "reason": None, "card": card,
            "revision4": {k: json.loads(json.dumps(v)) for k, v in REV4.items()},
            "trade": dict(TRADE if trade is None else trade), "terms": dict(TERMS if terms is None else terms),
            "arm_terms": dict(ARM if arm is None else arm)}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e424.judge(_doc(**kw))}


def _with(base, **kw):
    out = dict(base)
    out.update(kw)
    return out


def test_the_five_claims_read_both_faces():
    #: the revision-4 shape: the clauses carried, the trade's two ends, the terms and the arm terms read off the runs
    j = _judge()
    for cid in ("AZ1", "AZ2", "AZ3", "AZ4", "AZ5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AZ1: a clause changed that this revision does not rewrite, and a revision number that is not five
    assert _judge(mutate="loop")["AZ1"].startswith("FALSIFIER")
    assert _judge(revision=4)["AZ1"].startswith("FALSIFIER")

    # AZ2: a cell count, a cost count, a shallow recovery and a thin coverage, each off the artifact's own
    assert _judge(trade=_with(TRADE, far_cells=11))["AZ2"].startswith("FALSIFIER")
    assert _judge(trade=_with(TRADE, far_newest_cost=11))["AZ2"].startswith("FALSIFIER")
    assert _judge(trade=_with(TRADE, far_oldest_min=0.20))["AZ2"].startswith("FALSIFIER")
    assert _judge(trade=_with(TRADE, far_coverage_min=4.0))["AZ2"].startswith("FALSIFIER")

    # AZ3: the near point's counts and its recovery
    assert _judge(trade=_with(TRADE, near_cells=12))["AZ3"].startswith("FALSIFIER")
    assert _judge(trade=_with(TRADE, near_newest_cost=7))["AZ3"].startswith("FALSIFIER")
    assert _judge(trade=_with(TRADE, near_oldest_max=0.10))["AZ3"].startswith("FALSIFIER")

    # AZ4: a non-zero structural term, and a middle ratio under the artifact's
    assert _judge(terms=_with(TERMS, oldest_learning=0.01))["AZ4"].startswith("FALSIFIER")
    assert _judge(terms=_with(TERMS, newest_retention=0.01))["AZ4"].startswith("FALSIFIER")
    assert _judge(terms=_with(TERMS, middle_ratio_min=3.0))["AZ4"].startswith("FALSIFIER")

    # AZ5: a ratio under the artifact's, and a price gap over it
    assert _judge(arm=_with(ARM, retention_ratio_min=5.0))["AZ5"].startswith("FALSIFIER")
    assert _judge(arm=_with(ARM, price_gap_max=0.08))["AZ5"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e424.judge(_doc(ok=False)))


def test_the_artifacts_and_the_clauses_are_registered():
    #: the revision-4 card and the four artifacts the new clauses are read from
    assert e424.CARD4.name == "e418_the_game_card_revision_four.json"
    assert e424.TRADE_FAR.name == "e420_the_trade_is_a_constant.json"
    assert e424.TRADE_NEAR.name == "e421_the_trade_turns_on.json"
    assert e424.TERMS.name == "e422_the_buffer_buys_retention.json"
    assert e424.ARM_TERMS.name == "e423_the_penalty_buys_a_tenth.json"
    assert e424.REVISION == 5 and e424.NEW == ("revision", "trade", "terms", "arm_terms")
    assert e424.TOL == 0.002 and e424.RATIO_TOL == 0.01
    assert e424.EXPECTED["far_cells"] == 12 and e424.EXPECTED["far_newest_cost"] == 12
    assert e424.EXPECTED["near_cells"] == 13 and e424.EXPECTED["near_newest_cost"] == 8
    assert e424.EXPECTED["oldest_learning"] == 0.0 and e424.EXPECTED["newest_retention"] == 0.0
    assert e424.EXPECTED["retention_ratio_min"] == 7.13 and e424.EXPECTED["price_gap_max"] == 0.0344


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e424_the_game_card_revision_five.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e424.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e424.judge(d)}
    #: the fourth revision being carried and the trade clause being the artifacts' own are structural facts
    assert verdicts["AZ1"].startswith("MET") and verdicts["AZ2"].startswith("MET"), verdicts
    card = d["card"]
    assert card["revision"] == e424.REVISION, card["revision"]
    for k in ("world", "stream", "recovery", "invariance", "arm", "draw_terms", "penalty", "trade", "terms",
              "arm_terms"):
        assert k in card, k
    #: the clauses' numbers are read, not stated: the trade's two ends point at the two artifacts
    assert card["trade"]["artifact"] == [e424.TRADE_FAR.name, e424.TRADE_NEAR.name]
    assert card["terms"]["artifact"] == e424.TERMS.name and card["arm_terms"]["artifact"] == e424.ARM_TERMS.name
    assert card["trade"]["far_cells"] == e424.EXPECTED["far_cells"]
    assert abs(card["terms"]["middle_ratio_min"] - e424.EXPECTED["middle_ratio_min"]) < e424.RATIO_TOL
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
