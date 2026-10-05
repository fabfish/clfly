"""`e418` writes the card's fourth revision and reads every changed clause from the artifact that closed the gap, so
the tests pin both faces of the five claims, the refusal when one of those artifacts is absent, and the live
re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e418_the_game_card_revision_four as e418

#: the card's third revision, as `e414` wrote it: the draw's clauses, the buffer's, and `e392`'s absence list
REV3 = {
    "name": "the closed-loop earned-label game",
    "substrate": {"circuit": "mb+cx+al@n952", "circuit_size": 300, "readout_subset": "59926518137c", "support": 80},
    "loop": {"cue_at": 0, "drive": "action", "world_dims": 8, "coupled": True, "leak": 0.35},
    "protocol": {"tasks": ["loop_odour_identity", "loop_heading", "loop_odour_input"], "train": 96, "test": 48},
    "metrics": ["accuracy", "the retention matrix's diagonal"],
    "world": {"span_at_20": 0.075, "span_at_500": 0.3104, "worlds_measured": 6},
    "stream": {"span_at_500": 0.0323, "against_the_worlds": 0.3344, "streams_measured": 3},
    "recovery": {"worlds_at_the_far_point": 5, "recovering": 1, "bar": 0.05},
    "invariance": {"reading": 0.6875, "spread": 0.0, "over_at_least": 10},
    "arm": {"budgets": [1, 20, 500], "worlds_measured": 6, "small_band": [-0.0174, 0.0365]},
    "draw_terms": {"draw_span_at_500": 0.0309, "least_gain_at_500": 0.1330, "gain_over_draw_span": 4.30},
    "absent": ["a reward", "a policy", "an episode boundary", "a held-out task", "a second world", "a second draw"],
}
PEN = {"accuracy_gain": 0.1764, "accuracy_sigma": 11.50, "forgetting_cut": 0.2521, "forgetting_sigma": -11.65,
       "over_naive": {"accuracy": -0.0274, "sigma": -1.95}}
RULE = "the uncoupled world rule that predates e359"


def _doc(absent=None, over=None, revision=4, third="ewc-block", arms=None, replicates=20, closed=None,
         penalty=None, rule=None, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision3": {}, "closed": {}, "arms": {},
                "penalty": {}, "rule": {}, "old_absent": [], "struck": []}
    old = list(REV3["absent"])
    absent = [a for a in old if a not in e418.STRIKE] if absent is None else absent
    card = {k: json.loads(json.dumps(v)) for k, v in REV3.items()}
    card.pop("absent", None)
    card["revision"] = revision
    card["arms"] = list(arms) if arms is not None else ["naive", "replay", third]
    card["absent"] = list(absent)
    card["penalty"] = {"arm": third, "lam": 1.0, "replicates": replicates, **PEN, "measured_on": RULE}
    card.update(over or {})
    closed = {"artifact": "e409_the_game_card_revision_two.json", "object": REV3["world"], "stream": REV3["stream"],
              "covers": {k: REV3[e418.COVERED_BY[k]] for k in e418.STRIKE}} if closed is None else closed
    return {"ok": True, "reason": None, "card": card,
            "revision3": {k: json.loads(json.dumps(v)) for k, v in REV3.items() if k != "absent"},
            "old_absent": old, "struck": [a for a in old if a in e418.STRIKE],
            "closed": closed,
            "arms": {"artifact": "e415_the_penalty_on_the_cards_world.json",
                     "arms": sorted(["naive", "replay", third]), "third": third, "replicates": replicates},
            "penalty": {"artifact": "e415_the_penalty_on_the_cards_world.json", **(penalty or PEN)},
            "rule": {"artifact": "e415_the_penalty_on_the_cards_world.json",
                     "reference": "e380_earned_label_cue0_actionsource_20reps.json",
                     "coupling_recorded_in_reference": True, "coupling_in_measured_cell": False,
                     "stated": RULE} if rule is None else rule}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e418.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the revision-3 shape: the unchanged clauses carried, the two covered absences struck, the penalty added
    j = _judge()
    for cid in ("AP1", "AP2", "AP3", "AP4", "AP5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AP1: a clause changed that this revision does not rewrite, and a revision number that is not four
    assert _judge(over={"loop": {"cue_at": 11}})["AP1"].startswith("FALSIFIER")
    assert _judge(revision=3)["AP1"].startswith("FALSIFIER")

    # AP2: an absence kept that a clause covers, one struck that none covers, and a cover missing
    assert _judge(absent=[a for a in REV3["absent"] if a != "a reward"])["AP2"].startswith("FALSIFIER")
    drop = {"artifact": "e409.json", "object": REV3["world"], "stream": REV3["stream"], "covers": {}}
    assert _judge(closed=drop)["AP2"].startswith("FALSIFIER")

    # AP3: a third arm the artifact does not carry, a card short of it, and too few replicates
    assert _judge(arms=["naive", "replay"])["AP3"].startswith("FALSIFIER")
    assert _judge(replicates=5)["AP3"].startswith("FALSIFIER")

    # AP4: a clause whose numbers are not the artifact's
    drifted = {**PEN, "accuracy_gain": 0.20}
    assert _judge(penalty=drifted)["AP4"].startswith("FALSIFIER")

    # AP5: the coupling recorded in the measured cell, and a caveat that does not state the rule
    assert _judge(rule={"artifact": "e415.json", "reference": "e380.json", "coupling_recorded_in_reference": True,
                        "coupling_in_measured_cell": True, "stated": RULE})["AP5"].startswith("FALSIFIER")
    assert _judge(rule={"artifact": "e415.json", "reference": "e380.json", "coupling_recorded_in_reference": True,
                        "coupling_in_measured_cell": False, "stated": "measured on the card's world"})[
        "AP5"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e418.judge(_doc(ok=False)))


def test_the_artifacts_and_the_clauses_are_registered():
    #: the revision-3 card, the penalty cell, and the revision-2 card the struck items are covered from
    assert e418.CARD3.name == "e414_the_game_card_revision_three.json"
    assert e418.PENALTY.name == "e415_the_penalty_on_the_cards_world.json"
    assert e418.DRAWS.name == "e409_the_game_card_revision_two.json"
    assert e418.REVISION == 4 and e418.THIRD_ARM == "ewc-block"
    assert e418.STRIKE == ("a second world", "a second draw")
    assert e418.COVERED_BY == {"a second world": "world", "a second draw": "stream"}
    assert e418.REWRITTEN == ("revision", "arms", "absent", "penalty")
    assert e418.PENALTY_CLAUSE["accuracy_gain"] == 0.1764 and e418.PENALTY_CLAUSE["accuracy_sigma"] == 11.50
    assert e418.PENALTY_CLAUSE["forgetting_cut"] == 0.2521 and e418.PENALTY_CLAUSE["forgetting_sigma"] == -11.65
    assert e418.PENALTY_CLAUSE["over_naive"] == {"accuracy": -0.0274, "sigma": -1.95}
    assert (e418.TOL, e418.SIGMA_TOL) == (0.005, 0.05)


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e418_the_game_card_revision_four.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e418.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e418.judge(d)}
    #: the third revision being carried and the two covered absences being struck are structural facts
    assert verdicts["AP1"].startswith("MET") and verdicts["AP2"].startswith("MET"), verdicts
    card = d["card"]
    assert card["revision"] == e418.REVISION, card["revision"]
    assert card["arms"] == ["naive", "replay", e418.THIRD_ARM], card["arms"]
    assert sorted(set(d["old_absent"]) - set(card["absent"])) == sorted(e418.STRIKE), card["absent"]
    #: the penalty clause is the artifact's own numbers, and the rule it was measured on is stated
    got = d["penalty"]
    assert abs(card["penalty"]["accuracy_gain"] - got["accuracy_gain"]) < e418.TOL, card["penalty"]
    assert abs(card["penalty"]["forgetting_cut"] - got["forgetting_cut"]) < e418.TOL, card["penalty"]
    assert "uncoupled" in card["penalty"]["measured_on"], card["penalty"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
