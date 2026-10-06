"""`e445` writes the card's eighth revision, so the tests pin both faces of the five claims and the refusal when an
artifact it is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e445_the_game_card_revision_eight as e445

#: the four rolls of the card's own world: fixed true values, so a mutation under test moves one of them
ROLLS = {
    "as_built": {"artifact": "a.json", "buffer_mean": 0.1594, "buffer_sigma": 11.97, "margin": 0.3500,
                 "anchor_mean": -0.0302, "anchor_sigma": -1.77, "anchor_last": -0.1177, "anchor_last_sigma": -3.71},
    "rotated": {"artifact": "b.json", "buffer_mean": 0.2080, "buffer_sigma": 13.51, "margin": 0.4240,
                "anchor_mean": 0.0229, "anchor_sigma": 1.21, "anchor_last": -0.0906, "anchor_last_sigma": -3.56},
    "env_redrawn": {"artifact": "c.json", "buffer_mean": 0.1757, "buffer_sigma": 11.66, "margin": 0.3677,
                    "anchor_mean": 0.0198, "anchor_sigma": 1.30, "anchor_last": -0.0552, "anchor_last_sigma": -2.57},
    "decoder_redrawn": {"artifact": "d.json", "buffer_mean": 0.1503, "buffer_sigma": 7.66, "margin": 0.3281,
                        "anchor_mean": -0.0111, "anchor_sigma": -0.59, "anchor_last": -0.0615,
                        "anchor_last_sigma": -2.62},
}
#: the fields the revision-7 card carries, which this unit may not rewrite
OLD = {"name": "the closed-loop earned-label game", "world": {"worlds_measured": 6},
       "parameters": {"cells": 219}, "order": {"rolls": 16}}


def _ledger_from(rolls: dict) -> dict:
    vs = list(rolls.values())
    margins = {l: v["margin"] for l, v in rolls.items()}
    lasts = {l: v["anchor_last"] for l, v in rolls.items()}
    return {"artifact": [v["artifact"] for v in vs], "rolls": len(rolls), "buffer": e445.BUFFER,
            "anchor": e445.ANCHOR,
            "buffer_mean": {"min": min(v["buffer_mean"] for v in vs), "max": max(v["buffer_mean"] for v in vs)},
            "buffer_least_sigma": min(abs(v["buffer_sigma"]) for v in vs),
            "buffer_margin": margins, "buffer_margin_min": min(margins.values()),
            "buffer_margin_max": max(margins.values()),
            "anchor_mean": {"min": min(v["anchor_mean"] for v in vs), "max": max(v["anchor_mean"] for v in vs)},
            "anchor_greatest_sigma": max(abs(v["anchor_sigma"]) for v in vs),
            "anchor_last": lasts, "anchor_last_min": min(lasts.values()), "anchor_last_max": max(lasts.values()),
            "anchor_last_least_sigma": min(abs(v["anchor_last_sigma"]) for v in vs)}


def _doc(rolls=None, ledger=None, same_differ=None, revision=e445.REVISION, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": {}, "revision7": {}, "ledger": {}, "rolls": {}}
    R = {k: dict(v) for k, v in (ROLLS if rolls is None else rolls).items()}
    led = _ledger_from(R) if ledger is None else ledger
    card = {k: (dict(v) if isinstance(v, dict) else v) for k, v in OLD.items()}
    card["revision"] = revision
    card["ledger"] = led
    if same_differ:
        card[same_differ] = "rewritten"
    return {"ok": True, "reason": None, "card": card, "revision7": dict(OLD), "ledger": led, "rolls": R}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e445.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the seventh revision carried and the ledger clause reading as the four rolls do
    j = _judge()
    for cid in ("BW1", "BW2", "BW3", "BW4", "BW5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BW1: a field rewritten and a revision that did not move
    assert _judge(same_differ="world")["BW1"].startswith("FALSIFIER")
    assert _judge(revision=7)["BW1"].startswith("FALSIFIER")

    # BW2: a buffer number the clause gets wrong, and a margin it gets wrong
    led = _ledger_from(ROLLS)
    led["buffer_least_sigma"] = 9.99
    assert _judge(ledger=led)["BW2"].startswith("FALSIFIER")
    led = _ledger_from(ROLLS)
    led["buffer_margin"]["rotated"] = 0.5000
    assert _judge(ledger=led)["BW2"].startswith("FALSIFIER")

    # BW3: an anchor number the clause gets wrong
    led = _ledger_from(ROLLS)
    led["anchor_greatest_sigma"] = 4.44
    assert _judge(ledger=led)["BW3"].startswith("FALSIFIER")
    led = _ledger_from(ROLLS)
    led["anchor_last"]["as_built"] = -0.2000
    assert _judge(ledger=led)["BW3"].startswith("FALSIFIER")

    # BW4: a roll where the anchor's standing resolves, one where its price does not, and a buffer that does not
    odd = {k: dict(v) for k, v in ROLLS.items()}
    odd["rotated"]["anchor_sigma"] = 3.00
    assert _judge(rolls=odd)["BW4"].startswith("FALSIFIER")
    odd = {k: dict(v) for k, v in ROLLS.items()}
    odd["as_built"]["anchor_last"] = 0.0200
    assert _judge(rolls=odd)["BW4"].startswith("FALSIFIER")
    odd = {k: dict(v) for k, v in ROLLS.items()}
    odd["decoder_redrawn"]["buffer_sigma"] = 1.50
    assert _judge(rolls=odd)["BW4"].startswith("FALSIFIER")

    # BW5: another arm named, another count, a missing artifact and a range that is not the rolls' own
    led = _ledger_from(ROLLS)
    led["buffer"] = "ewc-block"
    assert _judge(ledger=led)["BW5"].startswith("FALSIFIER")
    led = _ledger_from(ROLLS)
    led["rolls"] = 3
    assert _judge(ledger=led)["BW5"].startswith("FALSIFIER")
    led = _ledger_from(ROLLS)
    led["artifact"] = led["artifact"][:3]
    assert _judge(ledger=led)["BW5"].startswith("FALSIFIER")
    led = _ledger_from(ROLLS)
    led["buffer_margin_max"] = 0.9000
    assert _judge(ledger=led)["BW5"].startswith("FALSIFIER")

    #: an artifact the revision is read from absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e445.judge(_doc(ok=False)))


def test_the_card_and_the_rolls_are_registered():
    #: the revision-7 card is what is added to, and the four rolls are the card's own world's
    assert e445.CARD7.name == "e434_the_game_card_revision_seven.json"
    assert {k: v.name for k, v in e445.ROLLS.items()} == {
        "as_built": "e438_earned_label_three_arms_20reps.json",
        "rotated": "e441_earned_label_anchor_order102_20reps.json",
        "env_redrawn": "e443_earned_label_worldseed1_20reps.json",
        "decoder_redrawn": "e444_earned_label_readoutseed1_20reps.json"}
    assert e445.REVISION == 8 and e445.NEW == ("revision", "ledger")
    assert (e445.BASELINE, e445.BUFFER, e445.ANCHOR) == ("naive", "replay", "ewc-block")
    assert e445.MIN_REPS == 20 and e445.N_TASKS == 3 and e445.SIGMA == 2.0
    assert e445.TOL == 0.002


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e445_the_game_card_revision_eight.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e445.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the card at revision 8, its seventh revision carried, and four rolls under the clause
    assert d["card"]["revision"] == e445.REVISION, d["card"]["revision"]
    assert len(d["revision7"]) >= 20, len(d["revision7"])
    assert sorted(d["rolls"]) == sorted(e445.ROLLS), sorted(d["rolls"])
    assert len(d["ledger"]["artifact"]) == len(d["rolls"]), d["ledger"]["artifact"]
    for label, got in d["rolls"].items():
        assert got["replicates"] >= e445.MIN_REPS, label
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
