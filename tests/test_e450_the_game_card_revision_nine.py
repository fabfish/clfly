"""`e450` writes the card's ninth revision, so the tests pin both faces of the five claims and the refusal when an
artifact it is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e450_the_game_card_revision_nine as e450

#: the three widths of the card's own world: fixed true values, so a mutation under test moves one of them
BASE_DIAGONAL = {"four": 0.4493, "eight": 0.5191, "sixteen": 0.5705}
BUFFER_FIRST = {"four": 0.2115, "eight": 0.2896, "sixteen": 0.2500}
BUFFER_MARGIN = {"four": 0.2865, "eight": 0.3500, "sixteen": 0.3167}
BUFFER_DIAGONAL = {"four": 0.1212, "eight": 0.1594, "sixteen": 0.1323}
ANCHOR_DIAGONAL = {"four": -0.0271, "eight": -0.0302, "sixteen": 0.0073}
ANCHOR_LAST = {"four": -0.0937, "eight": -0.1177, "sixteen": -0.0292}
BUFFER_SIGMA = {"four": 8.60, "eight": 11.97, "sixteen": 9.29}
ANCHOR_DIAG_SIGMA = {"four": 2.29, "eight": 1.77, "sixteen": 0.44}
ANCHOR_LAST_SIGMA = {"four": 2.81, "eight": 3.71, "sixteen": 1.68}
#: the fields the revision-8 card carries, which this unit may not rewrite
OLD = {"name": "the closed-loop earned-label game", "world": {"worlds_measured": 6},
       "ledger": {"rolls": 4}, "parameters": {"cells": 219}}


def _width_clause() -> dict:
    return {"artifact": ["a.json", "b.json", "c.json"], "widths": {k: e450.WIDTHS[k] for k in e450.WIDTHS},
            "card_width": e450.CARD_WIDTH,
            "baseline_diagonal": dict(BASE_DIAGONAL), "buffer_first": dict(BUFFER_FIRST),
            "buffer_margin": dict(BUFFER_MARGIN), "buffer_diagonal": dict(BUFFER_DIAGONAL),
            "buffer_diagonal_sigma": dict(BUFFER_SIGMA),
            "anchor_diagonal": dict(ANCHOR_DIAGONAL), "anchor_diagonal_sigma": dict(ANCHOR_DIAG_SIGMA),
            "anchor_last": dict(ANCHOR_LAST), "anchor_last_sigma": dict(ANCHOR_LAST_SIGMA)}


def _rolls() -> dict:
    return {label: {"artifact": a, "baseline_diagonal": BASE_DIAGONAL[label], "buffer_first": BUFFER_FIRST[label],
                    "buffer_margin": BUFFER_MARGIN[label],
                    "buffer_diagonal": {"mean": BUFFER_DIAGONAL[label], "sigma": BUFFER_SIGMA[label]},
                    "anchor_diagonal": {"mean": ANCHOR_DIAGONAL[label], "sigma": ANCHOR_DIAG_SIGMA[label]},
                    "anchor_last": {"mean": ANCHOR_LAST[label], "sigma": ANCHOR_LAST_SIGMA[label]}}
            for label, a in zip(e450.ROLLS, ("a.json", "b.json", "c.json"))}


def _doc(width=None, rolls=None, same_differ=None, revision=e450.REVISION, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": {}, "revision8": {}, "width": {}, "rolls": {}}
    w = _width_clause() if width is None else width
    rr = _rolls() if rolls is None else rolls
    card = {k: (dict(v) if isinstance(v, dict) else v) for k, v in OLD.items()}
    card["revision"] = revision
    card["width"] = w
    if same_differ:
        card[same_differ] = "rewritten"
    return {"ok": True, "reason": None, "card": card, "revision8": dict(OLD), "width": w, "rolls": rr}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e450.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the eighth revision carried and the width clause reading as the three rolls do
    j = _judge()
    for cid in ("CW1", "CW2", "CW3", "CW4", "CW5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # CW1: a field rewritten and a revision that did not move
    assert _judge(same_differ="world")["CW1"].startswith("FALSIFIER")
    assert _judge(revision=8)["CW1"].startswith("FALSIFIER")

    # CW2: a number the clause gets wrong, in each of the two halves
    w = _width_clause()
    w["buffer_first"] = dict(BUFFER_FIRST)
    w["buffer_first"]["eight"] = 0.4000
    assert _judge(width=w)["CW2"].startswith("FALSIFIER")
    w = _width_clause()
    w["anchor_last"] = dict(ANCHOR_LAST)
    w["anchor_last"]["sixteen"] = -0.2000
    assert _judge(width=w)["CW2"].startswith("FALSIFIER")

    # CW3: a number whose peak is not at the card's own width
    w = _width_clause()
    w["buffer_first"] = dict(BUFFER_FIRST)
    w["buffer_first"]["sixteen"] = 0.4000
    assert _judge(width=w)["CW3"].startswith("FALSIFIER")
    w = _width_clause()
    w["anchor_last_sigma"] = dict(ANCHOR_LAST_SIGMA)
    w["anchor_last_sigma"]["four"] = 5.00
    assert _judge(width=w)["CW3"].startswith("FALSIFIER")

    # CW4: a price that stops resolving at eight, one that resolves at sixteen, and a standing that resolves at eight
    w = _width_clause()
    w["anchor_last_sigma"] = dict(ANCHOR_LAST_SIGMA)
    w["anchor_last_sigma"]["eight"] = 1.50
    assert _judge(width=w)["CW4"].startswith("FALSIFIER")
    w = _width_clause()
    w["anchor_last_sigma"] = dict(ANCHOR_LAST_SIGMA)
    w["anchor_last_sigma"]["sixteen"] = 3.00
    assert _judge(width=w)["CW4"].startswith("FALSIFIER")
    w = _width_clause()
    w["anchor_diagonal_sigma"] = dict(ANCHOR_DIAG_SIGMA)
    w["anchor_diagonal_sigma"]["eight"] = 2.60
    assert _judge(width=w)["CW4"].startswith("FALSIFIER")

    # CW5: another width, another card width, a missing artifact and a baseline that is not the rolls' own
    w = _width_clause()
    w["widths"] = {"four": 4, "eight": 8, "sixteen": 32}
    assert _judge(width=w)["CW5"].startswith("FALSIFIER")
    w = _width_clause()
    w["card_width"] = 16
    assert _judge(width=w)["CW5"].startswith("FALSIFIER")
    w = _width_clause()
    w["artifact"] = w["artifact"][:2]
    assert _judge(width=w)["CW5"].startswith("FALSIFIER")
    w = _width_clause()
    w["baseline_diagonal"] = dict(BASE_DIAGONAL)
    w["baseline_diagonal"]["eight"] = 0.9000
    assert _judge(width=w)["CW5"].startswith("FALSIFIER")

    #: an artifact the revision is read from absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e450.judge(_doc(ok=False)))


def test_the_card_and_the_rolls_are_registered():
    #: the revision-8 card is what is added to, and the three rolls are the card's own world at three widths
    assert e450.CARD8.name == "e445_the_game_card_revision_eight.json"
    assert {k: v.name for k, v in e450.ROLLS.items()} == {
        "four": "e449_earned_label_worlddims4_20reps.json",
        "eight": "e438_earned_label_three_arms_20reps.json",
        "sixteen": "e448_earned_label_worlddims16_20reps.json"}
    assert e450.WIDTHS == {"four": 4, "eight": 8, "sixteen": 16}
    assert e450.CARD_WIDTH == 8
    assert e450.REVISION == 9 and e450.NEW == ("revision", "width")
    assert (e450.BASELINE, e450.BUFFER, e450.ANCHOR) == ("naive", "replay", "ewc-block")
    assert e450.MIN_REPS == 20 and e450.N_TASKS == 3 and e450.SIGMA == 2.0 and e450.TOL == 0.002


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e450_the_game_card_revision_nine.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e450.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the card at revision 9, its eighth revision carried, the three widths under the clause
    assert d["card"]["revision"] == e450.REVISION, d["card"]["revision"]
    assert len(d["revision8"]) >= 20, len(d["revision8"])
    assert sorted(d["rolls"]) == ["eight", "four", "sixteen"], sorted(d["rolls"])
    assert sorted(d["width"]["widths"].values()) == [4, 8, 16], d["width"]["widths"]
    assert len(d["width"]["artifact"]) == len(d["rolls"]), d["width"]["artifact"]
    for label, got in d["rolls"].items():
        assert got["replicates"] >= e450.MIN_REPS, label
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
