"""`e490` writes the game card's seventeenth revision, so the tests pin both faces of the four claims, the absent list
emptying, the clause's numbers against the runs and the measurement, and the refusal when an artifact the clause is
read from is absent.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from experiments import e490_the_game_card_revision_seventeen as e490

ARMS = e490.ARMS
#: the runs' numbers: the boundary and the plain diagonals inside the band of chance, the contrasts unresolved
DIAG = {"naive": (0.2476, 0.2476), "ewc-block": (0.2497, 0.2451), "replay": (0.2524, 0.2413)}
CONTRAST = {"naive": (-0.0000, -0.00), "ewc-block": (+0.0045, +0.61), "replay": (+0.0111, +1.02)}
LAST = {"naive": (0.2365, 0.2420), "ewc-block": (0.2455, 0.2559), "replay": (0.2441, 0.2441)}
#: the measurement: the episode carried and the boundary's marks
MARKS = [1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0]
CARRY = {"difference": 0.7601, "sigma": 12.62, "episodes": 64, "scale": 0.7727, "at_one_trial": 0.0}
BOUNDARY = {"neurons": 8, "gain": 1.0, "marks": list(MARKS), "disjoint": True, "in_input": True,
            "at_the_endpoint": False}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(revision=17, absent=(), card_extra=None, carry=None, boundary=None, contrast=None, diag=None,
         replicates=(20,), marks=None, measure_marks=None, ok=True,
         reason="an artifact the clause is read from is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision16": {}, "absent16": [], "episode": {},
                "rolls": {}, "reading": {}, "measure": {}}
    diag = dict(diag or DIAG)
    contrast = dict(contrast or CONTRAST)
    clause = {
        "artifact": [e490.READING.name, e490.PLAIN.name, e490.BOUND.name, e490.CARD.name],
        "flag": "--loop-episode", "trials": e490.e489.EPISODE,
        "steps_per_trial": e490.e489.TAU // e490.e489.EPISODE,
        "state": "the episode's", "carry": dict(carry or CARRY),
        "boundary_flag": "--loop-boundary", "boundary": dict(boundary or {**BOUNDARY, "marks": marks or MARKS}),
        "arms": list(ARMS), "replicates": list(replicates), "chance": e490.e489.CHANCE,
        "accuracy": {a: {"boundary": diag[a][0], "plain": diag[a][1], "contrast": contrast[a][0],
                         "sigma": contrast[a][1], "last_boundary": LAST[a][0], "last_plain": LAST[a][1]}
                     for a in ARMS},
        "read_step": "the pass's last",
    }
    rev16 = {"name": "the closed-loop earned-label game", "substrate": {"circuit_size": 300}}
    card = {**rev16, "revision": revision,
            "absent": list(absent if absent is not None else []), "episode": clause}
    if card_extra:
        card.update(card_extra)
    arms = {a: {"replicates": 20, "accuracy_diagonal": [diag[a][0]] * 20, "accuracy_last": [LAST[a][0]] * 20}
            for a in ARMS}
    plain_arms = {a: {"replicates": 20, "accuracy_diagonal": [diag[a][1]] * 20, "accuracy_last": [LAST[a][1]] * 20}
                  for a in ARMS}
    measured = {"endpoint": {"fields": 22, "added": [], "missing": [], "identical": True},
                "carry": {"episode": {"pairing": _paired(CARRY["difference"], CARRY["sigma"], n=CARRY["episodes"]),
                                      "largest": 1.7013, "smallest": 0.003, "state_scale": CARRY["scale"]},
                          "single": {"pairing": _paired(0.0, 0.0, n=64), "largest": CARRY["at_one_trial"],
                                     "smallest": 0.0, "state_scale": 0.7856}},
                "boundary": {"gain": BOUNDARY["gain"], "n_boundary": BOUNDARY["neurons"],
                             "marks": list(measure_marks or MARKS), "wanted": list(MARKS), "steps_agree": True,
                             "overlap": 0, "in_input": True, "off_has_channel": False, "off_input_gap": 8}}
    return {
        "ok": True, "reason": None, "card": card, "revision16": rev16, "absent16": ["an episode boundary"],
        "episode": clause, "measure": measured,
        "rolls": {"runs": {"bound": {"arms": arms}, "plain": {"arms": plain_arms}},
                  "accuracy": {a: _paired(contrast[a][0], contrast[a][1]) for a in ARMS}},
        "reading": {"accuracy": {a: _paired(contrast[a][0], contrast[a][1]) for a in ARMS},
                    "runs": {"bound": {"arms": arms}, "plain": {"arms": plain_arms}},
                    "carry": measured["carry"], "boundary": measured["boundary"],
                    "spans": {"replicates": [20]}},
    }


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e490.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: revision 16 carried, the absent list emptied, the clause's numbers out of the runs and the
    #: measurement, the episode carried and its opening marked, and the cost carried too
    j = _judge()
    for cid in ("UA1", "UA2", "UA3", "UA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # UA1: another field differing, a revision that is not 17, and an absent list that keeps the entry or gains one
    assert _judge(card_extra={"name": "something else"})["UA1"].startswith("FALSIFIER")
    assert _judge(revision=16)["UA1"].startswith("FALSIFIER")
    assert _judge(absent=["an episode boundary"])["UA1"].startswith("FALSIFIER")
    assert _judge(absent=["an episode boundary", "a goal"])["UA1"].startswith("FALSIFIER")

    # UA2: a number in the clause that is not the runs' or the measurement's, and a replicate count that is not
    assert _judge(carry={**CARRY, "difference": 0.5000})["UA2"].startswith("FALSIFIER")
    assert _judge(boundary={**BOUNDARY, "neurons": 12})["UA2"].startswith("FALSIFIER")
    assert _judge(replicates=(10,))["UA2"].startswith("FALSIFIER")
    doc = _doc()
    doc["episode"]["accuracy"]["replay"]["sigma"] = 0.5
    assert e490.judge(doc)[1]["verdict"].startswith("FALSIFIER")

    # UA3: a carry at zero, one that does not resolve, a single-trial value that is not zero, marks that are not the
    # declaration, and marks the measurement did not make
    assert _judge(carry={**CARRY, "difference": 0.0})["UA3"].startswith("FALSIFIER")
    assert _judge(carry={**CARRY, "sigma": 0.90})["UA3"].startswith("FALSIFIER")
    assert _judge(carry={**CARRY, "at_one_trial": 0.31})["UA3"].startswith("FALSIFIER")
    assert _judge(marks=[0.0] * 12)["UA3"].startswith("FALSIFIER")
    assert _judge(measure_marks=[1.0] * 12)["UA3"].startswith("FALSIFIER")
    assert _judge(boundary={**BOUNDARY, "disjoint": False})["UA3"].startswith("FALSIFIER")
    assert _judge(boundary={**BOUNDARY, "in_input": False})["UA3"].startswith("FALSIFIER")

    # UA4: an arm past the band, and a boundaried contrast that resolves
    assert _judge(diag={**DIAG, "naive": (0.4000, 0.2476)})["UA4"].startswith("FALSIFIER")
    doc2 = _doc()
    doc2["episode"]["accuracy"]["replay"]["sigma"] = 2.50
    assert e490.judge(doc2)[3]["verdict"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e490.judge(_doc(ok=False)))


def test_the_card_the_clause_and_the_bars_are_registered():
    assert e490.CARD16.name == "e486_the_game_card_revision_sixteen.json"
    assert e490.READING.name == "e489_the_benchmark_has_an_episode.json"
    assert e490.PLAIN.name == "e489_earned_label_episode3_20reps.json"
    assert e490.BOUND.name == "e489_earned_label_episode3_boundary_20reps.json"
    assert e490.CARD.name == "e438_earned_label_three_arms_20reps.json"
    assert e490.REVISION == 17 and e490.HELD == "an episode boundary"
    assert set(e490.NEW) == {"revision", "episode", "absent"}, e490.NEW
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e490.TOL, e490.SIGMA, e490.BAND) == (0.002, 2.0, 0.05)


def test_the_live_revision_and_the_artifact_carries_the_new_card():
    p = Path("runs/e490_the_game_card_revision_seventeen.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e490.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    card = d["card"]
    assert card["revision"] == 17, card["revision"]
    #: the absent list is revision 16's minus exactly the episode boundary, and it is now empty
    assert card["absent"] == [], card["absent"]
    assert d["absent16"] == ["an episode boundary"], d["absent16"]
    assert "episode" in card and "episode" not in d["revision16"], sorted(card)
    clause = card["episode"]
    assert sorted(clause["accuracy"]) == sorted(ARMS), sorted(clause["accuracy"])
    assert clause["arms"] == list(ARMS) and clause["replicates"] == [20], clause
    assert clause["trials"] * clause["steps_per_trial"] == e490.e489.TAU, clause
    assert len(clause["boundary"]["marks"]) == e490.e489.TAU, clause["boundary"]["marks"]
    assert clause["boundary"]["marks"].count(-clause["boundary"]["gain"]) == clause["trials"] - 1, clause["boundary"]
    #: the numbers are the runs' and the measurement's, and the cost is carried beside the capability
    for a in ARMS:
        assert abs(clause["accuracy"][a]["boundary"] - clause["chance"]) <= e490.BAND, (a, clause["accuracy"][a])
        assert abs(clause["accuracy"][a]["plain"] - clause["chance"]) <= e490.BAND, (a, clause["accuracy"][a])
        assert abs(clause["accuracy"][a]["sigma"]) < e490.SIGMA, (a, clause["accuracy"][a])
    assert d["measure"]["carry"]["episode"]["pairing"]["mean"] > 0.0, d["measure"]["carry"]
    assert d["measure"]["carry"]["single"]["largest"] == 0.0, d["measure"]["carry"]
    #: a revision is a reading, so the artifact carries no top-level `config`, `env` or `tasks`
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
