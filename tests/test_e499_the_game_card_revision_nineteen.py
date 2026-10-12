"""`e499` folds `e497`'s three-trial rung into the card's `label_first` clause and writes the card's nineteenth
revision, so the tests pin both faces of the three claims -- the rung the clause gains, its numbers being `e497`'s, and
the revision-18 fields surviving -- and the refusal when an artifact the clause is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e499_the_game_card_revision_nineteen as e499

ARMS = e499.ARMS
#: the reading's shape: the three-trial rung beside the two-trial point it is read from
DIAG = {"three": {"naive": 0.8538, "ewc-block": 0.8392, "replay": 0.8580},
        "two": {"naive": 0.8299, "ewc-block": 0.8139, "replay": 0.8267}}
CHANGE = {"naive": (0.0240, 3.78), "ewc-block": (0.0253, 3.38), "replay": (0.0312, 5.93)}
SHARES = {"two": 1.0551, "three": 1.0571, "spreads": {"two": 4.2967, "three": 4.3099}}
#: a revision-18 clause, the fields this revision must carry unchanged
CLAUSE18 = {"placement": "the label at the episode's first trial", "window": {"label_last": 5, "label_first": 11},
            "shares": {"last": 0.0386, "first": 1.0551}, "arms": list(ARMS), "replicates": [20], "chance": 0.25,
            "bar": 0.10}
CARD18_OTHER = {"name": "the closed-loop earned-label game", "substrate": {"circuit_size": 300}}


def _rung(diag=None, change=None, shares=None, replicates=(20,)):
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    change = dict(change or CHANGE)
    shares = dict(shares or SHARES)
    return {"artifact": [e499.READING.name, e499.THREE.name], "flag": "--loop-label-first --loop-episode 3",
            "trials": 3, "two_trials": 2, "replicates": list(replicates), "chance": e499.CHANCE, "bar": e499.BAR,
            "accuracy": {a: {"diagonal": diag["three"][a], "two_trials": diag["two"][a], "change": change[a][0],
                             "sigma": change[a][1]} for a in ARMS},
            "shares": {"two": shares["two"], "three": shares["three"], "spreads": dict(shares["spreads"])},
            "explains": "the two-trial reading is this rung's starting point"}


def _reading(diag=None, change=None, shares=None, replicates=(20,)):
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    change = dict(change or CHANGE)
    shares = dict(shares or SHARES)
    roll = {"spans": {"accuracy_diagonal": {k: dict(diag[k]) for k in diag}, "replicates": list(replicates)},
            "recovery": {a: {"n": 20, "mean": change[a][0], "sigma": change[a][1]} for a in ARMS},
            "share": {name: {"share": shares[name], "across": shares["spreads"][name]} for name in ("two", "three")}}
    return roll


def _doc(revision=19, carry=True, absent=None, card_extra=None, clause_extra=None, ok=True,
         reason="an artifact the clause is read from is absent", rung=None, read=None):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "card18": {}, "clause18": {}, "absent18": [],
                "three_trials": {}, "reading": {}, "rolls": {}}
    rung = _rung(**(rung or {}))
    roll = _reading(**(read or {}))
    clause = dict(CLAUSE18)
    if carry:
        clause[e499.RUNG] = rung
    if clause_extra:
        clause.update(clause_extra)
    card = {k: v for k, v in CARD18_OTHER.items()}
    card["revision"] = revision
    card["absent"] = list(absent if absent is not None else [])
    card["label_first"] = clause
    if card_extra:
        card.update(card_extra)
    return {"ok": True, "reason": None, "card": card, "card18": dict(CARD18_OTHER), "clause18": dict(CLAUSE18),
            "absent18": [], "three_trials": rung, "rolls": roll, "reading": roll}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e499.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    #: the shape: the rung the clause gains, its numbers being e497's, and revision 18 surviving into it
    j = _judge()
    for cid in ("NA1", "NA2", "NA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # NA1: no three-trial field, and a revision that is not 19
    assert _judge(carry=False)["NA1"].startswith("FALSIFIER")
    assert _judge(revision=18)["NA1"].startswith("FALSIFIER")

    # NA2: a diagonal the reading does not carry, a change and a sigma that are not its, a share that is not, and a
    #      replicate count that is not the runs'
    assert _judge(rung={"diag": {"three": {**DIAG["three"], "replay": 0.5000}, "two": DIAG["two"]}}
                  )["NA2"].startswith("FALSIFIER")
    assert _judge(rung={"change": {**CHANGE, "naive": (0.0900, 3.78)}})["NA2"].startswith("FALSIFIER")
    assert _judge(rung={"change": {**CHANGE, "replay": (0.0312, 0.90)}})["NA2"].startswith("FALSIFIER")
    assert _judge(rung={"shares": {"two": 1.0551, "three": 0.5000, "spreads": SHARES["spreads"]}}
                  )["NA2"].startswith("FALSIFIER")
    assert _judge(rung={"replicates": (10,)})["NA2"].startswith("FALSIFIER")

    # NA3: a revision-18 clause field moved, a card field moved, and an absent list that grew
    doc = _doc()
    doc["card"]["label_first"]["placement"] = "the label somewhere else"
    assert e499.judge(doc)[2]["verdict"].startswith("FALSIFIER")
    assert _judge(card_extra={"name": "something else"})["NA3"].startswith("FALSIFIER")
    assert _judge(absent=["an episode boundary"])["NA3"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e499.judge(_doc(ok=False)))


def test_the_card_the_reading_and_the_precision_are_registered():
    assert e499.CARD18.name == "e496_the_game_card_revision_eighteen.json"
    assert e499.READING.name == "e497_the_label_first_at_three_trials.json"
    assert e499.THREE.name == "e497_earned_label_episode3_labelfirst_20reps.json"
    assert e499.TWO.name == "e495_earned_label_episode2_labelfirst_20reps.json"
    assert e499.REVISION == 19
    assert e499.RUNG == "three_trials"
    assert set(e499.NEW) == {"revision", "label_first"}, e499.NEW
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e499.PLACES, e499.SIGMA_PLACES, e499.BAR, e499.CHANCE) == (4, 2, 0.10, 0.25)


def test_the_live_revision_and_the_artifact_carries_the_new_card():
    p = Path("runs/e499_the_game_card_revision_nineteen.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e499.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    card = d["card"]
    assert card["revision"] == 19, card["revision"]
    #: nothing is removed and the absent list is carried as it was
    assert card["absent"] == [] and d["absent18"] == [], (card["absent"], d["absent18"])
    assert "label_first" in card and "label_first" not in d["card18"]
    clause = card["label_first"]
    #: the revision-18 clause survives into revision 19 field for field
    for k, v in d["clause18"].items():
        assert clause[k] == v, (k, clause.get(k), v)
    rung = clause[e499.RUNG]
    assert sorted(rung["accuracy"]) == sorted(ARMS), sorted(rung["accuracy"])
    assert rung["trials"] == 3 and rung["two_trials"] == 2, rung
    assert rung["replicates"] == [20] and rung["chance"] == e499.CHANCE and rung["bar"] == e499.BAR, rung
    for a in ARMS:
        g = rung["accuracy"][a]
        #: the rung's shape: a three-trial diagonal and the two-trial point beside it, with a change and its sigma
        assert 0.0 <= g["diagonal"] <= 1.0 and 0.0 <= g["two_trials"] <= 1.0, (a, g)
        assert isinstance(g["change"], float) and isinstance(g["sigma"], float) and g["sigma"] > 0.0, (a, g)
    assert rung["shares"]["two"] > 0.0 and rung["shares"]["three"] > 0.0, rung["shares"]
    #: a revision is a reading, so the artifact carries no top-level `config`, `env` or `tasks`
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
