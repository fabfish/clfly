"""`e503` adds the card's `payout` clause -- the earned-vs-meter ablation at two and three trials and the payout read
on the action -- and writes the card's twentieth revision, so the tests pin both faces of the three claims: the clause
the card gains, its numbers being the three units' artifacts and readings, and the revision-19 fields surviving. One
test drives the module on synthetic card data so every falsifier can be shown to fire; one reads the live artifact.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from experiments import e503_the_game_card_revision_twenty as e503

ARMS = e503.ARMS
#: a revision-19 `label_first` clause, a subset of the fields this revision must carry unchanged
CLAUSE19 = {"placement": "the label at the episode's first trial", "window": {"label_last": 5, "label_first": 11},
            "shares": {"last": 0.0386, "first": 1.0551}, "arms": list(ARMS), "replicates": [20], "chance": 0.25,
            "bar": 0.10, "three_trials": {"trials": 3, "two_trials": 2}}
CARD19_OTHER = {"name": "the closed-loop earned-label game", "substrate": {"circuit_size": 300}}
#: the episode length each synthetic unit is read at, and the widths the action's currency turns on
EPISODE = {"two_trials": 2, "three_trials": 3, "action": 2}


def _unit(name, episode, reward_gain=None, accuracy_change=None, map_mean=None):
    """One synthetic unit reading with the fields the clause's builder reads."""
    gain = dict(reward_gain or {a: 1.5 + 0.1 * i for i, a in enumerate(ARMS)})
    acc = dict(accuracy_change or {a: (0.001 * i, 0.5 * i) for i, a in enumerate(ARMS)})
    mv = dict(map_mean or {a: (5.0 + i, 4.0 + i) for i, a in enumerate(ARMS)})
    diag_rw = {"earned": {a: -4.0 - i for i, a in enumerate(ARMS)},
               "meter": {a: -6.0 - i for i, a in enumerate(ARMS)}}
    if name == "action":
        diag_rw["carried"] = {a: -5.0 - i for i, a in enumerate(ARMS)}
    return {
        "spans": {"episode": episode, "replicates": [20],
                  "reward_diagonal": diag_rw,
                  "accuracy_diagonal": {"earned": {a: 0.83 + 0.001 * i for i, a in enumerate(ARMS)},
                                        "meter": {a: 0.82 + 0.001 * i for i, a in enumerate(ARMS)}},
                  "map_move": {"earned": {a: {"mean": mv[a][0], "smallest": mv[a][1]} for a in ARMS}}},
        "reward": {a: {"mean": gain[a], "sigma": 20.0 + i} for i, a in enumerate(ARMS)},
        "accuracy": {a: {"mean": acc[a][0], "sigma": acc[a][1]} for i, a in enumerate(ARMS)},
        "runs": {"earned": {"env_draw": {"n_action": 8, "world_dims": 8}}},
    }


def _doc(revision=20, carry=True, absent=None, card_extra=None, ok=True, reason="an artifact the clause is read "
         "from is absent", clause_mutate=None, stored_mutate=None):
    names = {n: Path(e503.ARTIFACTS[n]).name for n in e503.UNIT_ORDER}
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "card19": {}, "clause19": {}, "absent19": [],
                "payout": {}, "rolls": {}, "artifacts": {}}
    fresh = {n: _unit(n, EPISODE[n]) for n in e503.UNIT_ORDER}
    stored = copy.deepcopy(fresh)
    if stored_mutate:
        stored_mutate(stored)
    clause = e503.build_clause(fresh, names) if carry else {}
    if clause_mutate:
        clause_mutate(clause)
    card = {k: copy.deepcopy(v) for k, v in CARD19_OTHER.items()}
    card["revision"] = revision
    card["absent"] = list(absent if absent is not None else [])
    card["label_first"] = copy.deepcopy(CLAUSE19)
    if carry:
        card[e503.CLAUSE] = clause
    if card_extra:
        card.update(card_extra)
    return {"ok": True, "reason": None, "card": card,
            "card19": {k: copy.deepcopy(v) for k, v in CARD19_OTHER.items()},
            "clause19": copy.deepcopy(CLAUSE19), "absent19": [], "payout": clause,
            "rolls": fresh, "artifacts": stored}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e503.judge(_doc(**kw))}


def test_the_three_claims_read_both_faces():
    #: the shape the judge has to accept: the clause the card gains, its numbers the units', and revision 19 surviving
    j = _judge()
    for cid in ("NA1", "NA2", "NA3"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # NA1: no payout clause at all, and a revision that is not 20
    assert _judge(carry=False)["NA1"].startswith("FALSIFIER")
    assert _judge(revision=19)["NA1"].startswith("FALSIFIER")

    # NA2: a clause number that is not the artifact's, and a stored artifact that has moved away from the clause
    def bump_reward(clause):
        clause["two_trials"]["reward"]["naive"]["change"] = 9.9999

    def bump_sigma(clause):
        clause["three_trials"]["reward"]["replay"]["sigma"] = 0.01

    def bump_map(clause):
        clause["action"]["map_move"]["ewc-block"]["mean"] = 0.0001

    for mutate in (bump_reward, bump_sigma, bump_map):
        assert _judge(clause_mutate=mutate)["NA2"].startswith("FALSIFIER")

    def move_stored(units):
        units["action"]["reward"]["naive"]["mean"] = 0.0000

    assert _judge(stored_mutate=move_stored)["NA2"].startswith("FALSIFIER")

    # NA3: a revision-19 clause field moved, a card field moved, and an absent list that grew
    doc = _doc()
    doc["card"]["label_first"]["placement"] = "the label somewhere else"
    assert e503.judge(doc)[2]["verdict"].startswith("FALSIFIER")
    doc = _doc()
    doc["card"]["label_first"].pop("shares")
    assert e503.judge(doc)[2]["verdict"].startswith("FALSIFIER")
    assert _judge(card_extra={"name": "something else"})["NA3"].startswith("FALSIFIER")
    assert _judge(absent=["an episode boundary"])["NA3"].startswith("FALSIFIER")

    #: an artifact the clause is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e503.judge(_doc(ok=False)))


def test_the_card_the_units_and_the_precision_are_registered():
    assert e503.CARD19.name == "e499_the_game_card_revision_nineteen.json"
    assert e503.REVISION == 20
    assert e503.CLAUSE == "payout"
    assert set(e503.NEW) == {"revision", "payout"}, e503.NEW
    assert e503.UNIT_ORDER == ("two_trials", "three_trials", "action"), e503.UNIT_ORDER
    assert Path(e503.ARTIFACTS["two_trials"]).name == "e500_the_pass_plays_for_the_payout.json"
    assert Path(e503.ARTIFACTS["three_trials"]).name == "e501_the_pass_plays_at_three_trials.json"
    assert Path(e503.ARTIFACTS["action"]).name == "e502_the_world_pays_the_action.json"
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert set(e503.CURRENCY) == {"carried", "action"}, sorted(e503.CURRENCY)
    assert e503.READER == {"two_trials": "carried", "three_trials": "carried", "action": "action"}, e503.READER
    assert (e503.PLACES, e503.SIGMA_PLACES) == (4, 2)


def test_the_reading_refuses_when_an_input_is_absent():
    #: a card that is not on disk, and an artifact the clause is read from that is not
    assert e503.reading(card19=Path("runs/e503_no_such_card.json"))["ok"] is False
    bogus = {n: Path("runs/e503_no_such_artifact.json") for n in e503.UNIT_ORDER}
    live = e503.reading(card19=e503.CARD19, artifacts=bogus)
    assert live["ok"] is False, live.get("reason")
    assert all(row["verdict"].startswith("REFUSED") for row in e503.judge(live))


def test_the_live_revision_and_the_artifact_carries_the_new_card():
    p = Path("runs/e503_the_game_card_revision_twenty.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e503.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    card = d["card"]
    assert card["revision"] == 20, card["revision"]
    #: nothing is removed and the absent list is carried as it was
    assert card["absent"] == [] and d["absent19"] == [], (card["absent"], d["absent19"])
    assert e503.CLAUSE in card and e503.CLAUSE not in d["card19"]
    #: the revision-19 `label_first` clause survives into revision 20 field for field
    for k, v in d["clause19"].items():
        assert card["label_first"][k] == v, (k, card["label_first"].get(k), v)
    clause = card[e503.CLAUSE]
    #: the clause's shape: both readers, three rungs, each arm's earning and the map's move
    assert sorted(clause["currency"]) == ["action", "carried"], sorted(clause["currency"])
    for name in e503.UNIT_ORDER:
        rung = clause[name]
        assert rung["currency"] == e503.READER[name], (name, rung["currency"])
        assert sorted(rung["reward"]) == sorted(ARMS), sorted(rung["reward"])
        for a in ARMS:
            rw, ac, mm = rung["reward"][a], rung["accuracy"][a], rung["map_move"][a]
            assert isinstance(rw["earned"], float) and isinstance(rw["meter"], float), (name, a, rw)
            assert isinstance(rw["sigma"], float) and rw["sigma"] > 0.0, (name, a, rw)
            assert isinstance(ac["change"], float) and isinstance(ac["sigma"], float), (name, a, ac)
            assert isinstance(mm["mean"], float) and isinstance(mm["smallest"], float), (name, a, mm)
    #: the action's currency is the card's own width coincidence
    widths = clause["action"]["widths"]
    assert widths["n_action"] == widths["world_dims"], widths
    #: counts that grow with the corpus are bounds, not equalities
    assert len(d["card19"]) >= 30, len(d["card19"])
    assert len(d["clause19"]) >= 11, len(d["clause19"])
    assert len(clause) >= 9, len(clause)
    #: a revision is a reading, so the artifact carries no top-level `config`, `env` or `tasks`
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
