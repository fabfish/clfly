"""`e496` writes the game card's eighteenth revision, so the tests pin both faces of the four claims, the clause the
revision adds, the absent list it leaves alone, and the refusal when an artifact the clause is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e496_the_game_card_revision_eighteen as e496

ARMS = e496.ARMS
#: the reading's shape: the two placements' diagonals, the shares that order them and the windows
DIAG = {"first": {"naive": 0.8299, "ewc-block": 0.8139, "replay": 0.8267},
        "last": {"naive": 0.3104, "ewc-block": 0.2944, "replay": 0.3031}}
CONTRAST = {"naive": (+0.5194, +62.79), "ewc-block": (+0.5194, +40.52), "replay": (+0.5236, +48.18)}
SHARES = {"last": 0.0386, "first": 1.0551}
WINDOWS = {"label_last": 5, "label_first": 11}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(revision=18, card_extra=None, absent=None, diag=None, contrast=None, shares=None, windows=None,
         replicates=(20,), ok=True, reason="an artifact the clause is read from is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision17": {}, "absent17": [], "label_first": {},
                "rolls": {}, "reading": {}, "windows": {}}
    diag = {k: dict(v) for k, v in (diag or DIAG).items()}
    contrast = dict(contrast or CONTRAST)
    shares = dict(shares or SHARES)
    clause = {
        "artifact": [e496.READING.name, e496.FIRST.name, e496.LAST.name], "flag": "--loop-label-first",
        "placement": "the label at the first trial", "window": dict(windows or WINDOWS),
        "shares": dict(shares), "arms": list(ARMS), "replicates": list(replicates), "chance": e496.CHANCE,
        "accuracy": {a: {"first": diag["first"][a], "last": diag["last"][a], "contrast": contrast[a][0],
                         "sigma": contrast[a][1]} for a in ARMS},
        "bar": e496.BAR, "explains": "the episode clause's reading is this clause's starting point",
    }
    rev17 = {"name": "the closed-loop earned-label game", "substrate": {"circuit_size": 300},
             "revision": 17, "absent": []}
    card = {k: v for k, v in rev17.items() if k not in ("revision",)}
    card["revision"] = revision
    card["absent"] = list(absent if absent is not None else [])
    card["label_first"] = clause
    if card_extra:
        card.update(card_extra)
    spans = {"accuracy_diagonal": {k: dict(diag[k]) for k in diag}, "replicates": list(replicates)}
    return {
        "ok": True, "reason": None, "card": card, "revision17": {k: v for k, v in rev17.items() if k != "revision"},
        "absent17": [], "label_first": clause, "windows": dict(WINDOWS),
        "rolls": {"spans": spans, "share": {k: {"share": shares[k]} for k in shares},
                  "recovery": {a: _paired(contrast[a][0], contrast[a][1]) for a in ARMS}},
        "reading": {"spans": spans, "share": {k: {"share": shares[k]} for k in shares},
                    "recovery": {a: _paired(contrast[a][0], contrast[a][1]) for a in ARMS}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e496.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: revision 17 carried, the clause's numbers out of the runs, the placement's bearing and the cost
    j = _judge()
    for cid in ("NA1", "NA2", "NA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # NA1: another field differing, a revision that is not 18, and an absent list that is no longer empty
    assert _judge(card_extra={"name": "something else"})["NA1"].startswith("FALSIFIER")
    assert _judge(revision=17)["NA1"].startswith("FALSIFIER")
    assert _judge(absent=["an episode boundary"])["NA1"].startswith("FALSIFIER")

    # NA2: a number in the clause that is not the runs' or the reading's, a window differing, and a thin run
    doc = _doc()
    doc["label_first"]["shares"]["first"] = 0.5000
    assert e496.judge(doc)[1]["verdict"].startswith("FALSIFIER")
    assert _judge(windows={"label_last": 4, "label_first": 11})["NA2"].startswith("FALSIFIER")
    doc = _doc()
    doc["label_first"]["replicates"] = [10]
    assert e496.judge(doc)[1]["verdict"].startswith("FALSIFIER")
    doc = _doc()
    doc["label_first"]["accuracy"]["replay"]["sigma"] = 1.0
    assert e496.judge(doc)[1]["verdict"].startswith("FALSIFIER")

    # NA3: an arm whose label-first diagonal is under the bar, and one whose contrast does not resolve
    assert _judge(diag={"first": {"naive": 0.8299, "ewc-block": 0.3000, "replay": 0.8267},
                        "last": DIAG["last"]})["NA3"].startswith("FALSIFIER")
    assert _judge(contrast={"naive": (+0.5194, +0.90), "ewc-block": (+0.5194, +40.52),
                            "replay": (+0.5236, +48.18)})["NA3"].startswith("FALSIFIER")

    # NA4: a label-last arm outside the band, and two shares that do not order the placements
    assert _judge(diag={"first": DIAG["first"], "last": {"naive": 0.9000, "ewc-block": 0.2944, "replay": 0.3031}}
                  )["NA4"].startswith("FALSIFIER")
    assert _judge(shares={"last": 0.0386, "first": 0.0200})["NA4"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e496.judge(_doc(ok=False)))


def test_the_card_the_clause_and_the_tolerance_are_registered():
    assert e496.CARD17.name == "e490_the_game_card_revision_seventeen.json"
    assert e496.READING.name == "e495_the_label_first.json"
    assert e496.FIRST.name == "e495_earned_label_episode2_labelfirst_20reps.json"
    assert e496.LAST.name == "e493_earned_label_episode2_modelread_20reps.json"
    assert e496.REVISION == 18
    assert set(e496.NEW) == {"revision", "label_first"}, e496.NEW
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e496.TOL, e496.SIGMA, e496.BAR, e496.CHANCE) == (0.002, 2.0, 0.10, 0.25)


def test_the_live_revision_and_the_artifact_carries_the_new_card():
    p = Path("runs/e496_the_game_card_revision_eighteen.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e496.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    card = d["card"]
    assert card["revision"] == 18, card["revision"]
    #: nothing is removed and the absent list is carried as it was
    assert card["absent"] == [] and d["absent17"] == [], (card["absent"], d["absent17"])
    assert "label_first" in card and "label_first" not in d["revision17"], sorted(card)
    clause = card["label_first"]
    assert sorted(clause["accuracy"]) == sorted(ARMS), sorted(clause["accuracy"])
    assert clause["arms"] == list(ARMS) and clause["replicates"] == [20], clause
    #: the clause's shape: two windows, two shares that order the placements, and the bar it is read against
    assert clause["window"]["label_first"] > clause["window"]["label_last"], clause["window"]
    assert clause["shares"]["first"] > clause["shares"]["last"], clause["shares"]
    assert clause["bar"] == e496.BAR and clause["chance"] == e496.CHANCE, clause
    for a in ARMS:
        assert clause["accuracy"][a]["last"] < clause["chance"] + clause["bar"], (a, clause["accuracy"][a])
        assert clause["accuracy"][a]["sigma"] > 0.0, (a, clause["accuracy"][a])
    #: a revision is a reading, so the artifact carries no top-level `config`, `env` or `tasks`
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
