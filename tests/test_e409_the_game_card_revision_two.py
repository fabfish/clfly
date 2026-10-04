"""`e409` writes the game card's second revision from five artifact readers, so the tests pin both faces of the five
claims, the refusal when a reader is absent, and the live card the unit publishes.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from experiments import e409_the_game_card_revision_two as e409

CARD1 = {"name": "the closed-loop earned-label game", "revision": 1, "read": "2026-10-04",
         "substrate": {"circuit": "mb+cx+al@n952", "circuit_size": 300}, "loop": {"cue_at": 0, "world_dims": 8},
         "protocol": {"tasks": ["loop_odour_identity"], "train": 96, "test": 48}, "arms": ["naive", "replay"],
         "metrics": ["accuracy"], "absent": ["a reward", "a policy"]}


#: the six clauses the reader compares, which is what `reading` passes on from the revision-1 artifact
def _revision1():
    return {k: copy.deepcopy(CARD1[k]) for k in ("substrate", "loop", "protocol", "arms", "metrics", "absent")}


def _doc(card=None, revision1=None, world=None, stream=None, recovery=None, invariance=None, ok=True, reason="absent"):
    if not ok:
        #: `reading` refuses the whole unit when a reader it needs is absent
        return {"ok": False, "card": None, "revision1": {}, "world": {}, "stream": {}, "recovery": {},
                "invariance": {}, "reason": reason}
    card = card if card is not None else copy.deepcopy(CARD1)
    card["revision"] = e409.REVISION
    card["world"] = dict(e409.WORLD_CLAUSE)
    card["stream"] = dict(e409.STREAM_CLAUSE)
    card["recovery"] = dict(e409.RECOVERY_CLAUSE)
    card["invariance"] = dict(e409.INVARIANCE)
    return {"ok": True, "card": card,
            "revision1": revision1 if revision1 is not None else _revision1(),
            "world": world if world is not None else {"artifact": "e407.json", "span_at_20": 0.0750,
                                                      "span_at_500": 0.3104, "worlds": ["card", "cue1", "cue14", "cue3",
                                                                                        "cue6", "cue9"]},
            "stream": stream if stream is not None else {"artifact": "e403.json", "span_at_500": 0.0323,
                                                         "against_the_worlds": 0.3344,
                                                         "streams": ["1", "2", "card"]},
            "recovery": recovery if recovery is not None else {"artifact": "e396.json",
                                                               "worlds": ["card", "1", "2", "3", "4"],
                                                               "recovering": ["card"]},
            "invariance": invariance if invariance is not None else {"artifact": ["e396.json", "e407.json"],
                                                                     "readings": [0.6875] * 35, "spread": 0.0}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e409.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the card as the corpus carries it: revision 1 unchanged, both spans matching, one of five recovering
    j = _judge()
    for cid in ("AM1", "AM2", "AM3", "AM4", "AM5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # AM1: a clause that moved between the revisions
    moved = _revision1()
    moved["loop"] = {"cue_at": 0, "world_dims": 32}
    assert _judge(revision1=moved)["AM1"].startswith("FALSIFIER")

    # AM2: a span beyond the tolerance, and a world count that is not the clause's
    assert _judge(world={"artifact": "e407.json", "span_at_20": 0.0900, "span_at_500": 0.3104,
                         "worlds": ["card"] * 6})["AM2"].startswith("FALSIFIER")
    assert _judge(world={"artifact": "e407.json", "span_at_20": 0.0750, "span_at_500": 0.3104,
                         "worlds": ["card"] * 5})["AM2"].startswith("FALSIFIER")

    # AM3: either span off
    assert _judge(stream={"artifact": "e403.json", "span_at_500": 0.1000, "against_the_worlds": 0.3344,
                          "streams": ["1", "2", "card"]})["AM3"].startswith("FALSIFIER")
    assert _judge(stream={"artifact": "e403.json", "span_at_500": 0.0323, "against_the_worlds": 0.2000,
                          "streams": ["1", "2", "card"]})["AM3"].startswith("FALSIFIER")

    # AM4: none recovering, and two
    assert _judge(recovery={"artifact": "e396.json", "worlds": ["card", "1", "2", "3", "4"],
                            "recovering": []})["AM4"].startswith("FALSIFIER")
    assert _judge(recovery={"artifact": "e396.json", "worlds": ["card", "1", "2", "3", "4"],
                            "recovering": ["card", "1"]})["AM4"].startswith("FALSIFIER")

    # AM5: a reading that differs, and too few readings for the bound
    assert _judge(invariance={"artifact": ["a", "b"], "readings": [0.6875] * 34 + [0.70],
                              "spread": 0.0125})["AM5"].startswith("FALSIFIER")
    assert _judge(invariance={"artifact": ["a", "b"], "readings": [0.6875] * 4, "spread": 0.0})[
        "AM5"].startswith("FALSIFIER")

    #: a reader absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e409.judge(_doc(ok=False)))


def test_the_readers_and_the_clauses_are_registered():
    #: every clause is read from its own artifact, and the clauses' values are the series' own
    assert e409.REVISION == 2
    assert e409.CARD1.name == "e392_the_game_card.json", e409.CARD1.name
    assert e409.SERIES.name == "e407_five_budgets_on_all_six_worlds.json", e409.SERIES.name
    assert e409.STREAMS.name == "e403_the_far_point_on_the_clean_stream.json", e409.STREAMS.name
    assert e409.WORLDS.name == "e396_the_far_point_on_all_five_worlds.json", e409.WORLDS.name
    assert e409.WORLD_CLAUSE == {"span_at_20": 0.0750, "span_at_500": 0.3104, "worlds_measured": 6}
    assert e409.RECOVERY_CLAUSE["recovering"] == 1 and e409.RECOVERY_CLAUSE["bar"] == e409.GAIN
    assert e409.MIN_READINGS == 10 and e409.INVARIANCE["reading"] == 0.6875


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e409_the_game_card_revision_two.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e409.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e409.judge(d)}
    #: the first revision's clauses and the recovery are structural facts
    assert verdicts["AM1"].startswith("MET") and verdicts["AM4"].startswith("MET"), verdicts
    #: the card publishes its revision and the four clauses the series established
    assert d["card"]["revision"] == e409.REVISION, d["card"]["revision"]
    for clause in ("world", "stream", "recovery", "invariance"):
        assert d["card"][clause] == getattr(e409, clause.upper() + "_CLAUSE" if clause != "invariance"
                                            else "INVARIANCE"), clause
    #: and the readers' own readings are in the artifact beside the card
    assert len(d["invariance"]["readings"]) >= e409.MIN_READINGS, len(d["invariance"]["readings"])
    assert len(d["recovery"]["recovering"]) == e409.RECOVERY_CLAUSE["recovering"], d["recovery"]
    #: a card is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
