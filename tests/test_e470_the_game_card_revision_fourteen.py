"""`e470` writes the game card's fourteenth revision, so the tests pin both faces of the four claims, the absent list
that loses exactly one entry, and the refusal when an artifact the clause is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e470_the_game_card_revision_fourteen as e470

ABSENT13 = ["a reward", "a policy", "an episode boundary", "a held-out task"]
ANCHOR_OF = e470.ANCHOR_OF
ROLLS = ("bio", "rand")
BEFORE = 0.6875
AFTER = {e470.BASELINE: 0.7719, "ewc-block": 0.7625, "ewc-block-rand": 0.7667, e470.BUFFER: 0.7677}


def _mean(values):
    return sum(values) / len(values)


def _doc(fields_differ=None, revision=e470.REVISION, absent=None, change_sigma=10.0, versus_sigma=-0.86,
         counts=(96, 48), off=False, ok=True, reason="an artifact is absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": None, "revision13": {}, "holdout": {}, "rolls": {},
                "reading": {}, "absent13": ABSENT13}
    rolls = {label: {"anchor": ANCHOR_OF[label], "arms": {}} for label in ROLLS}
    holdout = {"task": ["loop_holdout"], "in_sequence": False,
               "probe": {"kind": "ridge", "ridge": [1e-2], "n_train": [counts[0]], "n_eval": [counts[1]]},
               "initial": {}, "trained": {}, "change": {}, "change_sigma": {},
               "against_baseline": {}, "against_baseline_sigma": {}}
    for label in ROLLS:
        anchor = ANCHOR_OF[label]
        base = AFTER[e470.BASELINE]
        holdout["initial"][label] = {}
        holdout["trained"][label] = {}
        holdout["change"][label] = {}
        holdout["change_sigma"][label] = {}
        holdout["against_baseline"][label] = {}
        holdout["against_baseline_sigma"][label] = {}
        for arm in (e470.BASELINE, anchor, e470.BUFFER):
            after = AFTER[anchor if arm == anchor else arm]
            rolls[label]["arms"][arm] = {"replicates": 20, "before": [BEFORE] * 20, "after": [after] * 20,
                                         "task": ["loop_holdout"], "n_train": [96], "n_eval": [48], "ridge": [1e-2]}
            holdout["initial"][label][arm] = BEFORE
            holdout["trained"][label][arm] = after
            holdout["change"][label][arm] = after - BEFORE + (0.01 if off and arm == e470.BASELINE else 0.0)
            holdout["change_sigma"][label][arm] = change_sigma
            if arm != e470.BASELINE:
                holdout["against_baseline"][label][arm] = after - base
                holdout["against_baseline_sigma"][label][arm] = versus_sigma
    base_fields = {k: f"v-{k}" for k in ("name", "read", "substrate", "loop", "arms", "metrics", "world")}
    fields = dict(base_fields)
    if fields_differ:
        fields[fields_differ] = "changed"
    return {"ok": True, "reason": None,
            "revision13": fields,
            "absent13": list(ABSENT13),
            "card": {**base_fields, "revision": revision,
                     "absent": list(absent if absent is not None else ABSENT13[:3]), "holdout": {}},
            "holdout": holdout, "rolls": rolls,
            "reading": {"spans": {"n_train": [96], "n_eval": [48]}}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e470.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    #: the shape: revision 13 carried, the absent list losing exactly the held-out task, the clause's numbers and nulls
    j = _judge()
    for cid in ("WA1", "WA2", "WA3", "WA4"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # WA1: another field differing, a revision that is not 14, an absent list that loses the wrong entry or gains one
    assert _judge(fields_differ="loop")["WA1"].startswith("FALSIFIER")
    assert _judge(revision=13)["WA1"].startswith("FALSIFIER")
    assert _judge(absent=["a reward", "a policy"])["WA1"].startswith("FALSIFIER")
    assert _judge(absent=ABSENT13[:3] + ["a second world"])["WA1"].startswith("FALSIFIER")

    # WA2: a clause whose baseline change is not the rolls', and counts that disagree with the reading
    assert _judge(off=True)["WA2"].startswith("FALSIFIER")
    assert _judge(counts=(96, 24))["WA2"].startswith("FALSIFIER")

    # WA3: a change that does not resolve
    assert _judge(change_sigma=1.20)["WA3"].startswith("FALSIFIER")
    assert _judge(change_sigma=-10.0)["WA3"].startswith("FALSIFIER")

    # WA4: an anchor whose contrast against the baseline resolves, in either direction
    assert _judge(versus_sigma=-2.40)["WA4"].startswith("FALSIFIER")
    assert _judge(versus_sigma=2.40)["WA4"].startswith("FALSIFIER")
    assert _judge(versus_sigma=-1.90)["WA4"].startswith("MET")

    #: the card and the reading are both required, so an absent artifact refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e470.judge(_doc(ok=False)))


def test_the_card_the_clause_and_the_bounds_are_registered():
    assert e470.CARD13.name == "e461_the_game_card_revision_thirteen.json"
    assert e470.E469.name == "e469_the_held_out_cue_set.json"
    assert e470.ROLLS["bio"].name == "e469_earned_label_neurons_holdout_20reps.json"
    assert e470.ROLLS["rand"].name == "e469_earned_label_rand_neurons_holdout_20reps.json"
    assert e470.REVISION == 14 and e470.HELD == "a held-out task"
    assert set(e470.NEW) == {"revision", "holdout", "absent"}, e470.NEW
    assert (e470.BASELINE, e470.BUFFER, e470.SIGMA) == ("naive", "replay", 2.0)
    assert e470.ANCHOR_OF == {"bio": "ewc-block", "rand": "ewc-block-rand"}, e470.ANCHOR_OF
    #: the revision before this one carried exactly these four absent entries, which is what WA1 is read against
    assert ABSENT13 == e470.load(e470.CARD13)["card"]["absent"], e470.load(e470.CARD13)["card"]["absent"]


def test_the_live_reframing_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e470_the_game_card_revision_fourteen.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e470.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the revision and the absent list are structural; the clause's counts are the reading's, read as equalities
    assert d["card"]["revision"] == e470.REVISION, d["card"].get("revision")
    assert e470.HELD not in d["card"]["absent"], d["card"]["absent"]
    assert d["holdout"]["in_sequence"] is False, d["holdout"]
    assert len(d["holdout"]["initial"]) == len(e470.ROLLS), d["holdout"]["initial"]
    for label, arms in d["holdout"]["initial"].items():
        assert arms, label
        assert set(arms) == set(d["holdout"]["trained"][label]) == set(d["holdout"]["change"][label]), label
        for arm in arms:
            assert 0.0 <= arms[arm] <= 1.0 and 0.0 <= d["holdout"]["trained"][label][arm] <= 1.0, (label, arm)
    assert d["holdout"]["probe"]["n_train"] == [96] and d["holdout"]["probe"]["n_eval"] == [48], d["holdout"]["probe"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
