"""`e486` writes the game card's sixteenth revision, so the tests pin both faces of the four claims, the absent list's
one-entry loss, and the refusal when an artifact the clause is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e486_the_game_card_revision_sixteen as e486

ARMS = e486.ARMS
#: the runs' numbers: the reward's diagonal below its last row, the accuracy's above, and the orderings reversed
REWARD = {"naive": (-6.8857, -6.5639, 0.7691), "ewc-block": (-6.8495, -6.4992, 0.7073), "replay": (-6.8743, -6.6866, 0.7389)}
CONTRAST = {"naive": (-0.3218, -4.91), "ewc-block": (-0.3503, -4.98), "replay": (-0.1877, -3.46)}
ACC_LAST = {"naive": 0.5191, "ewc-block": 0.4889, "replay": 0.6785}


def _paired(mean, sigma, n=20):
    return {"n": n, "mean": mean, "sd": 0.05, "se": 0.02, "sigma": sigma}


def _doc(card_extra=None, revision=16, absent=None, contrast=None, acc_last=None, order_agree=False,
         first_identical=True, ok=True, reason="an artifact the clause is read from is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision15": {}, "absent15": [], "reward": {},
                "rolls": {}, "reading": {}, "acc_last": {}}
    contrast = dict(contrast or CONTRAST)
    acc_last = dict(acc_last or ACC_LAST)
    clause = {
        "artifact": [e486.READING.name, e486.NEW_RUN.name, e486.BASE_RUN.name], "flag": "--loop-reward",
        "arms": list(ARMS), "replicates": [20],
        "reward": {a: {"diagonal": REWARD[a][0], "last_row": REWARD[a][1], "contrast": contrast[a][0],
                       "sigma": contrast[a][1]} for a in ARMS},
        "accuracy": {a: {"diagonal": REWARD[a][2], "last_row": acc_last[a]} for a in ARMS},
        "orderings": {"accuracy": sorted(ARMS, key=lambda a: REWARD[a][2], reverse=True),
                      "reward": sorted(ARMS, key=lambda a: REWARD[a][0], reverse=True),
                      "agree": order_agree},
        "first_task_one_training": first_identical,
    }
    rev15 = {"name": "the closed-loop earned-label game", "substrate": {"circuit_size": 300}}
    card = {**rev15, "revision": revision,
            "absent": list(absent if absent is not None else ["an episode boundary"]), "reward": clause}
    if card_extra:
        card.update(card_extra)
    diag = {a: {"reward": _paired(contrast[a][0], contrast[a][1]), "accuracy_diagonal": REWARD[a][2]} for a in ARMS}
    arms = {a: {"replicates": 20, "reward_diagonal": [REWARD[a][0]] * 20, "reward_last": [REWARD[a][1]] * 20,
                "accuracy_diagonal": [REWARD[a][2]] * 20, "reward_rows": [], "first_row": [[1.0, None, None]] * 20}
            for a in ARMS}
    return {"ok": True, "reason": None, "card": card, "revision15": rev15,
            "absent15": ["a reward", "an episode boundary"], "reward": clause,
            "acc_last": acc_last,
            "rolls": {"runs": {"reward": {"arms": arms}}, "diagonal": diag,
                      "order": {"accuracy": clause["orderings"]["accuracy"], "reward": clause["orderings"]["reward"],
                                "agrees": order_agree},
                      "first": {"identical": first_identical}},
            "reading": {"spans": {"replicates": [20]}, "diagonal": diag, "first": {"identical": first_identical}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e486.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: revision 15 carried, the absent list losing one entry, the clause's numbers out of the runs, the two
    #: currencies disagreeing and the reversal carried
    j = _judge()
    for cid in ("TA1", "TA2", "TA3", "TA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # TA1: another field differing, a revision that is not 16, and an absent list losing the wrong thing
    assert _judge(card_extra={"name": "something else"})["TA1"].startswith("FALSIFIER")
    assert _judge(revision=15)["TA1"].startswith("FALSIFIER")
    assert _judge(absent=["a reward", "an episode boundary"])["TA1"].startswith("FALSIFIER")
    assert _judge(absent=[])["TA1"].startswith("FALSIFIER")

    # TA2: a clause whose sigma is not the runs'
    assert _judge(contrast={"naive": (-0.3218, -4.91), "ewc-block": (-0.3503, -4.98),
                            "replay": (-0.1877, -1.00)})["TA2"].startswith("MET")
    doc = _doc()
    doc["reward"]["reward"]["replay"]["diagonal"] = -6.0
    assert e486.judge(doc)[1]["verdict"].startswith("FALSIFIER")

    # TA3: an arm whose reward contrast does not resolve, and an accuracy diagonal that is not above its last row
    assert _judge(contrast={"naive": (-0.3218, -4.91), "ewc-block": (-0.3503, -4.98),
                            "replay": (-0.1877, -1.20)})["TA3"].startswith("FALSIFIER")
    assert _judge(contrast={"naive": (-0.10, -0.50), "ewc-block": (-0.3503, -4.98),
                            "replay": (-0.1877, -3.46)})["TA3"].startswith("FALSIFIER")
    assert _judge(acc_last={"naive": 0.9000, "ewc-block": 0.4889, "replay": 0.6785})["TA3"].startswith("FALSIFIER")

    # TA4: orderings that agree, and one that is not recorded
    assert _judge(order_agree=True)["TA4"].startswith("FALSIFIER")
    doc = _doc()
    doc["reward"]["orderings"]["reward"] = []
    assert e486.judge(doc)[3]["verdict"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e486.judge(_doc(ok=False)))


def test_the_card_the_clause_and_the_tolerance_are_registered():
    assert e486.CARD15.name == "e482_the_game_card_revision_fifteen.json"
    assert e486.READING.name == "e485_the_benchmark_pays_a_reward.json"
    assert e486.NEW_RUN.name == "e485_earned_label_reward_20reps.json"
    assert e486.BASE_RUN.name == "e438_earned_label_three_arms_20reps.json"
    assert e486.REVISION == 16 and e486.HELD == "a reward"
    assert set(e486.NEW) == {"revision", "reward", "absent"}, e486.NEW
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e486.TOL, e486.SIGMA) == (0.002, 2.0)


def test_the_live_reframing_and_the_artifact_carries_the_new_card():
    p = Path("runs/e486_the_game_card_revision_sixteen.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e486.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    card = d["card"]
    assert card["revision"] == 16, card["revision"]
    #: the absent list is revision 15's minus exactly the reward, and the clause is the new field
    assert card["absent"] == ["an episode boundary"], card["absent"]
    assert d["absent15"] == ["a reward", "an episode boundary"], d["absent15"]
    assert "reward" in card and "reward" not in d["revision15"], sorted(card)
    clause = card["reward"]
    assert sorted(clause["reward"]) == sorted(ARMS), sorted(clause["reward"])
    assert sorted(clause["accuracy"]) == sorted(ARMS), sorted(clause["accuracy"])
    assert clause["replicates"] == [20], clause["replicates"]
    assert clause["orderings"]["agree"] is False, clause["orderings"]
    assert clause["first_task_one_training"] is True, clause
    for a in ARMS:
        assert clause["reward"][a]["diagonal"] < clause["reward"][a]["last_row"], (a, clause["reward"][a])
        assert clause["accuracy"][a]["diagonal"] > clause["accuracy"][a]["last_row"], (a, clause["accuracy"][a])
    #: a revision is a reading, so the artifact carries no top-level `config`, `env` or `tasks`
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
