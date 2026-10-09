"""`e482` writes the game card's fifteenth revision, so the tests pin both faces of the four claims, the absent list's
one-entry loss, and the refusal when an artifact the clause is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e482_the_game_card_revision_fifteen as e482

ARMS = e482.ARMS
#: the contrasts the runs carry: the diagonal and the last row per arm, and only the penalty's diagonal resolving
DIAG = {"naive": (0.0146, 0.63), "ewc-block": (0.0708, 2.40), "replay": (-0.0125, -0.80)}
LAST = {"naive": (-0.0146, -0.86), "ewc-block": (0.0451, 1.71), "replay": (-0.0177, -1.26)}
RESOLVED = ["ewc-block/diagonal"]


def _tbl(mean, sigma, policy=0.80, card=0.79):
    return {"policy": [policy] * 20, "card": [card] * 20,
            "contrast": {"n": 20, "mean": mean, "sigma": sigma}}


def _readings(sigma_diag=None, moves=None):
    got = [m for m in (moves or [7.0 + 0.05 * i for i in range(60)]) if m is not None]
    diag = {a: _tbl(*((DIAG[a][0], sigma_diag) if (a == "ewc-block" and sigma_diag is not None) else DIAG[a]))
            for a in ARMS}
    last = {a: _tbl(*LAST[a]) for a in ARMS}
    spans = {"replicates": {"policy": [20], "card": [20]}, "moves_recorded": len(got),
             "moves_total": len(moves or [0] * 60), "move_min": min(got) if got else None,
             "move_mean": (sum(got) / len(got)) if got else None}
    return diag, last, spans


def _doc(card_extra=None, revision=15, absent=None, moves=None, clause_sigma_off=0.0, resolved=None,
         learn=0.5687, ok=True, reason="an artifact the clause is read from is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision14": {}, "absent14": [], "policy": {},
                "rolls": {}, "reading": {}}
    moves = list(moves if moves is not None else [7.0 + 0.05 * i for i in range(60)])
    diag, last, spans = _readings(None, moves)
    #: the learn knob is `e482`'s chance plus the margin, which is what VA3 reads off the naive arm's diagonal
    diag["naive"]["policy"] = [e482.CHANCE + learn] * 20
    resolved = list(resolved if resolved is not None else RESOLVED)
    clause = {"artifact": [e482.READING.name, e482.NEW_RUN.name, e482.BASE_RUN.name], "flag": "--loop-policy",
              "arms": list(ARMS), "replicates": [20], "moves": {"recorded": spans["moves_recorded"],
                                                                "total": spans["moves_total"],
                                                                "min": spans["move_min"], "mean": spans["move_mean"]},
              "diagonal": {a: {"policy": diag[a]["policy"][0], "against": diag[a]["card"][0],
                               "contrast": diag[a]["contrast"]["mean"],
                               "sigma": diag[a]["contrast"]["sigma"] + (clause_sigma_off if a == "ewc-block" else 0.0)}
                           for a in ARMS},
              "last_row": {a: {"policy": last[a]["policy"][0], "against": last[a]["card"][0],
                               "contrast": last[a]["contrast"]["mean"],
                               "sigma": last[a]["contrast"]["sigma"]} for a in ARMS},
              "resolved": resolved}
    rev14 = {"name": "the closed-loop earned-label game", "substrate": {"circuit_size": 300}}
    card = {**rev14, "revision": revision,
            "absent": list(absent if absent is not None else ["a reward", "an episode boundary"]),
            "policy": clause}
    if card_extra:
        card.update(card_extra)
    return {"ok": True, "reason": None, "card": card, "revision14": rev14,
            "absent14": ["a reward", "a policy", "an episode boundary"], "policy": clause,
            "rolls": {"moves": {a: moves for a in ARMS}, "diagonal": diag, "last_row": last, "spans": spans},
            "reading": {"spans": {"replicates": {"card": [20]}, "moves_recorded": spans["moves_recorded"],
                                  "moves_total": spans["moves_total"]},
                        "diagonal": {a: {"contrast": dict(diag[a]["contrast"])} for a in ARMS},
                        "last_row": {a: {"contrast": dict(last[a]["contrast"])} for a in ARMS}}}


def _reading_with_sigma(doc, sigma):
    """The reading on disk with the penalty's diagonal sigma moved, so a clause and a reading can disagree."""
    doc["reading"]["diagonal"]["ewc-block"]["contrast"]["sigma"] = sigma
    return doc


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e482.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: revision 14 carried, the absent list losing one entry, the clause's numbers out of the runs, the
    #: freedom used and the game learned, and the firing carried
    j = _judge()
    for cid in ("VA1", "VA2", "VA3", "VA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # VA1: another field differing, a revision that is not 15, and an absent list losing the wrong thing
    assert _judge(card_extra={"name": "something else"})["VA1"].startswith("FALSIFIER")
    assert _judge(revision=14)["VA1"].startswith("FALSIFIER")
    assert _judge(absent=["a reward", "an episode boundary", "a policy"])["VA1"].startswith("FALSIFIER")
    assert _judge(absent=["an episode boundary"])["VA1"].startswith("FALSIFIER")

    # VA2: a clause whose sigma is not the runs'
    assert _judge(clause_sigma_off=0.70)["VA2"].startswith("FALSIFIER")

    # VA3: a replicate whose movement is zero, one that is not recorded, and a game that is not learned
    assert _judge(moves=[7.0, 0.0] + [7.0] * 58)["VA3"].startswith("FALSIFIER")
    assert _judge(moves=[7.0, None] + [7.0] * 58)["VA3"].startswith("FALSIFIER")
    assert _judge(learn=0.03)["VA3"].startswith("FALSIFIER")
    assert _judge(learn=0.08)["VA3"].startswith("NULL")
    assert _judge(learn=0.20)["VA3"].startswith("MET")

    # VA4: a clause that does not carry what the reading reports as resolving, and one that carries nothing
    assert _judge()["VA4"].startswith("MET")
    assert e482.judge(_reading_with_sigma(_doc(), 0.5))[3]["verdict"].startswith("FALSIFIER")
    assert _judge(resolved=[])["VA4"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e482.judge(_doc(ok=False)))


def test_the_card_the_clause_and_the_tolerance_are_registered():
    assert e482.CARD14.name == "e470_the_game_card_revision_fourteen.json"
    assert e482.READING.name == "e481_the_benchmark_carries_a_policy.json"
    assert e482.NEW_RUN.name == "e481_earned_label_policy_20reps.json"
    assert e482.BASE_RUN.name == "e438_earned_label_three_arms_20reps.json"
    assert e482.REVISION == 15 and e482.HELD == "a policy"
    assert set(e482.NEW) == {"revision", "policy", "absent"}, e482.NEW
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e482.TOL, e482.SIGMA, e482.CHANCE, e482.LEARNS, e482.FLAT) == (0.002, 2.0, 0.25, 0.10, 0.05)


def test_the_live_reframing_and_the_artifact_carries_the_new_card():
    p = Path("runs/e482_the_game_card_revision_fifteen.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e482.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    card = d["card"]
    assert card["revision"] == 15, card["revision"]
    #: the absent list is revision 14's minus exactly the policy, and the clause is the new field
    assert card["absent"] == ["a reward", "an episode boundary"], card["absent"]
    assert d["absent14"] == ["a reward", "a policy", "an episode boundary"], d["absent14"]
    assert "policy" in card and "policy" not in d["revision14"], sorted(card)
    clause = card["policy"]
    assert sorted(clause["diagonal"]) == sorted(ARMS), sorted(clause["diagonal"])
    assert sorted(clause["last_row"]) == sorted(ARMS), sorted(clause["last_row"])
    assert clause["replicates"] == [20], clause["replicates"]
    assert clause["moves"]["recorded"] == clause["moves"]["total"] == 60, clause["moves"]
    assert clause["moves"]["min"] > 0.0, clause["moves"]
    assert clause["resolved"] == ["ewc-block/diagonal"], clause["resolved"]
    #: a revision is a reading, so the artifact carries no top-level `config`, `env` or `tasks`
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
