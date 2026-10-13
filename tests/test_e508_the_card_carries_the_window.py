"""`e508` adds the card's `windows` field -- the label's window in drive steps and the eight placements the corpus
holds, with the two comparisons that decide the variable -- and writes the card's twenty-first revision, so the tests
pin both faces of the four claims: the window structure the clause gains and its numbers being the four units'
artifacts and readings, the revision-20 fields surviving, and the comparisons saying which variable orders the pass.
One test drives the module on synthetic card data so every falsifier can be shown to fire; one reads the live
artifact.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from experiments import e508_the_card_carries_the_window as e508

ARMS = e508.ARMS
#: a revision-20 `label_first` clause, a subset of the fields this revision must carry unchanged
CLAUSE20 = {"placement": "the cue the task's label names at the episode's first trial",
            "flag": "--loop-label-first",
            "window": {"label_last": 5, "label_first": 11},
            "shares": {"last": 0.0386, "first": 1.0551},
            "arms": list(ARMS), "replicates": [20], "chance": 0.25, "bar": 0.10,
            "accuracy": {a: {"first": 0.83, "last": 0.31, "contrast": 0.52, "sigma": 60.0} for a in ARMS},
            "three_trials": {"trials": 3, "two_trials": 2}}
CARD20_OTHER = {"name": "the closed-loop earned-label game", "substrate": {"circuit_size": 300}}
#: one synthetic accuracy and share per placement: window 11's family spread is 0.02, window 5's 0.01, and the
#: same-position pair rises 0.08, so the same-window families read alike inside the bound and the position does not
CANON = {
    "two_at0": {"accuracy": {"naive": 0.83, "ewc-block": 0.82, "replay": 0.81}, "share": 1.05},
    "two_at1": {"accuracy": {"naive": 0.31, "ewc-block": 0.29, "replay": 0.30}, "share": 0.04},
    "three_at0": {"accuracy": {"naive": 0.85, "ewc-block": 0.84, "replay": 0.83}, "share": 1.06},
    "three_at1": {"accuracy": {"naive": 0.32, "ewc-block": 0.30, "replay": 0.31}, "share": 0.05},
    "three_at2": {"accuracy": {"naive": 0.26, "ewc-block": 0.26, "replay": 0.25}, "share": 0.03},
    "four_at0": {"accuracy": {"naive": 0.84, "ewc-block": 0.83, "replay": 0.82}, "share": 1.02},
    "four_at1": {"accuracy": {"naive": 0.40, "ewc-block": 0.38, "replay": 0.39}, "share": 0.09},
    "four_at2": {"accuracy": {"naive": 0.30, "ewc-block": 0.28, "replay": 0.29}, "share": 0.04},
}
#: where each unit's reading keeps its rolls: e506's key is `placements`, the other three's is `runs`
ROLLS = {"e495": "runs", "e497": "runs", "e505": "runs", "e506": "placements"}
#: the label each unit names a placement by, per placement key
WHERE = {"e495": {"two_at0": "first", "two_at1": "last"},
         "e497": {"two_at0": "two", "three_at0": "three"},
         "e505": {"three_at0": "at0", "three_at1": "at1", "three_at2": "at2"},
         "e506": {key: key for key in CANON}}


def _roll(key):
    return {"arms": {a: {"replicates": 20, "accuracy_diagonal": [CANON[key]["accuracy"][a]] * 20}
                     for a in ARMS}}


def _unit(name):
    """One synthetic unit reading, shaped like the real artifact's own rolls and shares."""
    rolls = {where: _roll(key) for key, where in WHERE[name].items()}
    share = {where: {"share": CANON[key]["share"]} for key, where in WHERE[name].items()}
    return {ROLLS[name]: rolls, "share": share, "spans": {"replicates": [20]}}


def _doc(revision=21, carry=True, absent=None, card_extra=None, ok=True,
         reason="an artifact the clause is read from is absent", clause_mutate=None, stored_mutate=None,
         comp_mutate=None):
    names = {u: Path(e508.ARTIFACTS[u]).name for u in e508.UNITS}
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "card20": {}, "clause20": {}, "absent20": [],
                "windows": {}, "rolls": {}, "artifacts": {}}
    fresh = {u: _unit(u) for u in e508.UNITS}
    stored = copy.deepcopy(fresh)
    if stored_mutate:
        stored_mutate(stored)
    windows = e508.build_windows(fresh, names) if carry else {}
    if comp_mutate:
        comp_mutate(windows)
    clause = copy.deepcopy(CLAUSE20)
    if carry:
        clause[e508.FIELD] = windows
    if clause_mutate:
        clause_mutate(clause)
    card20 = {k: copy.deepcopy(v) for k, v in CARD20_OTHER.items()}
    card20["absent"] = []
    card = {k: copy.deepcopy(v) for k, v in card20.items()}
    card["revision"] = revision
    card["absent"] = list(absent if absent is not None else [])
    card["label_first"] = clause
    if card_extra:
        card.update(card_extra)
    return {"ok": True, "reason": None, "card": card, "card20": card20,
            "clause20": copy.deepcopy(CLAUSE20), "absent20": [], "windows": windows,
            "rolls": fresh, "artifacts": stored}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e508.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape the judge has to accept: the window table, its numbers the units', revision 20 surviving, the
    #: comparisons present
    j = _judge()
    for cid in ("NA1", "NA2", "NA3", "NA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # NA1: no window field at all, and a revision that is not 21
    assert _judge(carry=False)["NA1"].startswith("FALSIFIER")
    assert _judge(revision=20)["NA1"].startswith("FALSIFIER")

    # NA2: a table number that is not the artifact's, and a stored artifact that has moved away from the table
    def bump_accuracy(clause):
        clause[e508.FIELD]["placements"]["four_at1"]["accuracy"]["naive"] = 9.9999

    def bump_share(clause):
        clause[e508.FIELD]["placements"]["two_at0"]["share"] = 0.0001

    def bump_window(clause):
        clause[e508.FIELD]["placements"]["three_at1"]["window"] = 99

    for mutate in (bump_accuracy, bump_share, bump_window):
        assert _judge(clause_mutate=mutate)["NA2"].startswith("FALSIFIER")

    def move_stored(units):
        units["e506"]["placements"]["four_at0"]["arms"]["naive"]["accuracy_diagonal"] = [0.0] * 20

    assert _judge(stored_mutate=move_stored)["NA2"].startswith("FALSIFIER")

    #: a placement carried by more than one unit: the recorded source stands and a cross-check moves, which only
    #: the per-source reading catches
    def move_cross_check(units):
        units["e497"]["runs"]["two"]["arms"]["naive"]["accuracy_diagonal"] = [0.0] * 20

    def move_cross_check_share(units):
        units["e506"]["share"]["three_at0"]["share"] = 0.0

    for mutate in (move_cross_check, move_cross_check_share):
        assert _judge(stored_mutate=mutate)["NA2"].startswith("FALSIFIER")

    # NA3: a revision-20 clause field moved, a card field moved, and an absent list that grew
    def move_clause20(clause):
        clause["placement"] = "the label somewhere else"

    def drop_clause20(clause):
        clause.pop("shares")

    assert _judge(clause_mutate=move_clause20)["NA3"].startswith("FALSIFIER")
    assert _judge(clause_mutate=drop_clause20)["NA3"].startswith("FALSIFIER")
    assert _judge(card_extra={"name": "something else"})["NA3"].startswith("FALSIFIER")
    assert _judge(absent=["an episode boundary"])["NA3"].startswith("FALSIFIER")

    # NA4: a comparison dropped, a spread that is not the readings', a difference that is not, and a bound over
    # which the same-position pair would read alike
    def drop_comparison(windows):
        windows["comparisons"].pop("same_position")

    def bump_spread(windows):
        windows["comparisons"]["same_window"]["families"]["5"]["largest"] = 9.9999

    def bump_difference(windows):
        windows["comparisons"]["same_position"]["difference"]["replay"] = 0.0001

    def loosen_bound(windows):
        windows["comparisons"]["same_window"]["bound"] = 9.9999
        windows["comparisons"]["same_window"]["alike"] = True

    for mutate in (drop_comparison, bump_spread, bump_difference, loosen_bound):
        assert _judge(comp_mutate=mutate)["NA4"].startswith("FALSIFIER")

    #: an artifact the table is read from being absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e508.judge(_doc(ok=False)))


def test_the_card_the_units_and_the_windows_are_registered():
    assert e508.CARD20.name == "e503_the_game_card_revision_twenty.json"
    assert e508.REVISION == 21
    assert e508.CLAUSE == "label_first"
    assert e508.FIELD == "windows"
    assert set(e508.NEW) == {"revision", "label_first"}, e508.NEW
    assert e508.UNITS == ("e495", "e497", "e505", "e506"), e508.UNITS
    assert Path(e508.ARTIFACTS["e495"]).name == "e495_the_label_first.json"
    assert Path(e508.ARTIFACTS["e497"]).name == "e497_the_label_first_at_three_trials.json"
    assert Path(e508.ARTIFACTS["e505"]).name == "e505_where_in_the_pass_the_label_sits.json"
    assert Path(e508.ARTIFACTS["e506"]).name == "e506_the_window_or_the_position.json"
    assert ARMS == ("naive", "ewc-block", "replay"), ARMS
    assert (e508.PLACES, e508.SIGMA_PLACES) == (4, 2)
    #: the eight placements the corpus holds, and the window each leaves: 11 - i * 12 / N
    assert len(e508.PLACEMENTS) == 8, e508.PLACEMENTS
    assert e508.WINDOW == {"two_at0": 11, "two_at1": 5, "three_at0": 11, "three_at1": 7, "three_at2": 3,
                           "four_at0": 11, "four_at1": 8, "four_at2": 5}, e508.WINDOW
    assert e508.window(2, 0) == 11 and e508.window(2, 1) == 5
    assert e508.window(4, 0) == 11 and e508.window(4, 1) == 8 and e508.window(4, 2) == 5
    #: the families carried by more than one pass length, and the one pair read at a held position
    assert e508.SHARED == {11: ["two_at0", "three_at0", "four_at0"], 5: ["two_at1", "four_at2"]}, e508.SHARED
    assert e508.BIG_WINDOW == 11
    assert e508.POSITION == ("four_at1", "three_at1"), e508.POSITION


def test_the_reading_refuses_when_an_input_is_absent():
    #: a card that is not on disk, and a unit artifact the table is read from that is not
    assert e508.reading(card20=Path("runs/e508_no_such_card.json"))["ok"] is False
    bogus = {u: Path("runs/e508_no_such_artifact.json") for u in e508.UNITS}
    live = e508.reading(card20=e508.CARD20, artifacts=bogus)
    assert live["ok"] is False, live.get("reason")
    assert all(row["verdict"].startswith("REFUSED") for row in e508.judge(live))


def test_the_live_revision_carries_the_window_table():
    p = Path("runs/e508_the_card_carries_the_window.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e508.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    card = d["card"]
    assert card["revision"] == 21, card["revision"]
    #: nothing is removed and the absent list is carried as it was
    assert card["absent"] == [] and d["absent20"] == [], (card["absent"], d["absent20"])
    assert e508.FIELD in card[e508.CLAUSE] and e508.FIELD not in d["clause20"]
    #: the revision-20 `label_first` clause survives into revision 21 field for field
    for k, v in d["clause20"].items():
        assert card[e508.CLAUSE][k] == v, (k, card[e508.CLAUSE].get(k), v)
    field = card[e508.CLAUSE][e508.FIELD]
    #: the window table's shape: every placement with its pass length, trial, window, accuracy and share
    for key, trials, at, _ in e508.PLACEMENTS:
        row = field["placements"][key]
        assert (row["trials"], row["trial"], row["window"]) == (trials, at, e508.WINDOW[key]), (key, row)
        assert sorted(row["accuracy"]) == sorted(ARMS), (key, row["accuracy"])
        for a in ARMS:
            assert isinstance(row["accuracy"][a], float), (key, a, row["accuracy"][a])
        assert isinstance(row["share"], float) and row["share"] > 0.0, (key, row["share"])
    #: the two comparisons, and the spread and the difference each carries, each consistent with its own numbers
    comp = field["comparisons"]
    sw, sp = comp["same_window"], comp["same_position"]
    assert sw["families"], sw
    assert sw["bound"] == max(f["largest"] for f in sw["families"].values())
    assert sw["alike"] == all(f["largest"] <= sw["bound"] + 1e-9 for f in sw["families"].values())
    assert sp["placements"] == list(e508.POSITION)
    assert sorted(sp["difference"]) == sorted(ARMS), sp["difference"]
    assert sp["alike"] == (sp["smallest"] <= sp["bound"] + 1e-9)
    #: counts that grow with the corpus are bounds, not equalities
    assert len(field["placements"]) >= 8, len(field["placements"])
    assert len(d["clause20"]) >= 11, len(d["clause20"])
    assert len(d["card20"]) >= 30, len(d["card20"])
    #: an artifact carrying a revision is a reading, so it carries no top-level `config`, `env` or `tasks`
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
