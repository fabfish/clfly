"""`e454` writes the card's tenth revision, so the tests pin both faces of the five claims and the refusal when an
artifact it is read from is absent.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e454_the_game_card_revision_ten as e454

#: the ten rolls of the card's own world: fixed true values, so a mutation under test moves one of them
CELLS = {
    "biological/as_built": ("ewc-block", 0.1896, 10.89, -0.2370),
    "biological/rotated": ("ewc-block", 0.1851, 10.03, -0.2271),
    "biological/env_redrawn": ("ewc-block", 0.1559, 8.40, -0.2344),
    "biological/decoder_redrawn": ("ewc-block", 0.1615, 8.27, -0.2245),
    "biological/reversed": ("ewc-block", 0.1753, 8.38, -0.2240),
    "biological/wide_16": ("ewc-block", 0.1250, 8.38, -0.2115),
    "biological/narrow_4": ("ewc-block", 0.1483, 10.12, -0.2057),
    "matched_random/as_built": ("ewc-block-rand", 0.1958, 15.33, -0.2615),
    "matched_random/reversed": ("ewc-block-rand", 0.1861, 12.90, -0.2448),
    "matched_random/narrow_4": ("ewc-block-rand", 0.1382, 9.70, -0.1776),
}
#: the fields the revision-9 card carries, which this unit may not rewrite
OLD = {"name": "the closed-loop earned-label game", "width": {"card_width": 8}, "ledger": {"rolls": 4}}


def _rolls(cells=None) -> dict:
    spec = CELLS if cells is None else cells
    out = {}
    for label, (anchor, acc, sig, frg) in spec.items():
        out[label] = {"artifact": label.replace("/", "_") + ".json", "anchor": anchor, "replicates": 20,
                      "accuracy": {"n": 20, "mean": acc, "sd": 0.05, "se": 0.01, "sigma": sig},
                      "forgetting": {"n": 20, "mean": frg, "sd": 0.05, "se": 0.01, "sigma": -14.0}}
    return out


def _clause(rolls: dict) -> dict:
    acc = {l: v["accuracy"]["mean"] for l, v in rolls.items()}
    sig = {l: v["accuracy"]["sigma"] for l, v in rolls.items()}
    families = {}
    for label in rolls:
        families[label.split("/")[0]] = families.get(label.split("/")[0], 0) + 1
    return {"artifact": [v["artifact"] for v in rolls.values()], "rolls": len(rolls), "families": families,
            "buffer": e454.BUFFER, "anchors": dict(e454.FAMILIES),
            "accuracy": acc, "accuracy_sigma": sig,
            "accuracy_min": min(acc.values()), "accuracy_max": max(acc.values()),
            "span": max(acc.values()) - min(acc.values()),
            "least_sigma": min(abs(s) for s in sig.values()),
            "greatest_sigma": max(abs(s) for s in sig.values()),
            "forgetting": {l: v["forgetting"]["mean"] for l, v in rolls.items()}}


def _doc(cells=None, method=None, rolls=None, same_differ=None, revision=e454.REVISION, ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "card": {}, "revision9": {}, "method": {}, "rolls": {}}
    rr = _rolls(cells) if rolls is None else rolls
    m = _clause(rr) if method is None else method
    card = {k: (dict(v) if isinstance(v, dict) else v) for k, v in OLD.items()}
    card["revision"] = revision
    card["method"] = m
    if same_differ:
        card[same_differ] = "rewritten"
    return {"ok": True, "reason": None, "card": card, "revision9": dict(OLD), "method": m, "rolls": rr}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e454.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the shape: the ninth revision carried and the method clause reading as the ten rolls do
    j = _judge()
    for cid in ("DA1", "DA2", "DA3", "DA4", "DA5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # DA1: a field rewritten and a revision that did not move
    assert _judge(same_differ="ledger")["DA1"].startswith("FALSIFIER")
    assert _judge(revision=9)["DA1"].startswith("FALSIFIER")

    # DA2: a contrast the clause gets wrong, a derived number it gets wrong, and a forgetting it gets wrong
    rr = _rolls()
    m = _clause(rr)
    m["accuracy"] = dict(m["accuracy"])
    m["accuracy"]["biological/as_built"] = 0.4000
    assert _judge(rolls=rr, method=m)["DA2"].startswith("FALSIFIER")
    m = _clause(rr)
    m["least_sigma"] = 2.00
    assert _judge(rolls=rr, method=m)["DA2"].startswith("FALSIFIER")
    m = _clause(rr)
    m["forgetting"] = dict(m["forgetting"])
    m["forgetting"]["biological/wide_16"] = -0.9000
    assert _judge(rolls=rr, method=m)["DA2"].startswith("FALSIFIER")

    # DA3: a roll where the buffer is not ahead at two sigma
    odd = dict(CELLS)
    odd["biological/as_built"] = ("ewc-block", -0.0200, -1.10, -0.2370)
    assert _judge(cells=odd)["DA3"].startswith("FALSIFIER")

    # DA4: a weakest instance under the floor, one between the bars, and a span past the falsifier
    odd = dict(CELLS)
    odd["biological/wide_16"] = ("ewc-block", 0.1250, 1.50, -0.2115)
    assert _judge(cells=odd)["DA4"].startswith("FALSIFIER")
    odd = dict(CELLS)
    odd["biological/wide_16"] = ("ewc-block", 0.1250, 3.00, -0.2115)
    assert _judge(cells=odd)["DA4"].startswith("NULL")
    odd = dict(CELLS)
    odd["biological/as_built"] = ("ewc-block", 0.4000, 10.89, -0.2370)
    assert _judge(cells=odd)["DA4"].startswith("FALSIFIER")

    # DA5: another buffer, another count, a missing artifact and the wrong families
    rr = _rolls()
    m = _clause(rr)
    m["buffer"] = "ewc-block"
    assert _judge(rolls=rr, method=m)["DA5"].startswith("FALSIFIER")
    m = _clause(rr)
    m["rolls"] = 9
    assert _judge(rolls=rr, method=m)["DA5"].startswith("FALSIFIER")
    m = _clause(rr)
    m["artifact"] = m["artifact"][:9]
    assert _judge(rolls=rr, method=m)["DA5"].startswith("FALSIFIER")
    m = _clause(rr)
    m["families"] = {"biological": 8, "matched_random": 2}
    assert _judge(rolls=rr, method=m)["DA5"].startswith("FALSIFIER")

    #: an artifact the revision is read from absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e454.judge(_doc(ok=False)))


def test_the_card_and_the_rolls_are_registered():
    #: the revision-9 card is what is added to, and the ten rolls are the card's own world's
    assert e454.CARD9.name == "e450_the_game_card_revision_nine.json"
    assert e454.FAMILIES == {"biological": "ewc-block", "matched_random": "ewc-block-rand"}
    assert (e454.BASELINE, e454.BUFFER) == ("naive", "replay")
    assert len(e454.ROLLS) == 10, sorted(e454.ROLLS)
    assert sum(1 for k in e454.ROLLS if k.startswith("biological/")) == 7
    assert sum(1 for k in e454.ROLLS if k.startswith("matched_random/")) == 3
    assert e454.ROLLS["biological/wide_16"].name == "e448_earned_label_worlddims16_20reps.json"
    assert e454.ROLLS["biological/narrow_4"].name == "e449_earned_label_worlddims4_20reps.json"
    assert e454.ROLLS["matched_random/narrow_4"].name == "e451_earned_label_rand_worlddims4_20reps.json"
    assert e454.REVISION == 10 and e454.NEW == ("revision", "method")
    assert e454.N_TASKS == 3 and e454.MIN_REPS == 20 and e454.SIGMA == 2.0 and e454.TOL == 0.002
    assert (e454.LEAST_SIGMA, e454.LEAST_FLOOR) == (5.0, 2.0)
    assert (e454.SPAN, e454.SPAN_FIRES) == (0.10, 0.20)


def test_the_live_card_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e454_the_game_card_revision_ten.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e454.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    #: the card at revision 10, its ninth revision carried, ten rolls under the clause
    assert d["card"]["revision"] == e454.REVISION, d["card"]["revision"]
    assert len(d["revision9"]) >= 20, len(d["revision9"])
    assert sorted(d["rolls"]) == sorted(e454.ROLLS), sorted(d["rolls"])
    assert len(d["method"]["artifact"]) == len(d["rolls"]), d["method"]["artifact"]
    assert d["method"]["families"] == {"biological": 7, "matched_random": 3}, d["method"]["families"]
    for label, got in d["rolls"].items():
        assert got["replicates"] >= e454.MIN_REPS, label
        assert got["anchor"] == e454.FAMILIES[label.split("/")[0]], label
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
