"""`e435` reads the front page's parameters region back against the card and re-runs the first region's own check, so
the tests pin both faces of the five claims, the refusal when the README or the card is absent, and the live
re-framing the unit produces.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e435_the_front_pages_second_region as e435

#: a card shaped like `e434`'s, carrying every field the vocabulary reads
PARAMETERS = {
    "artifact": ["e431_the_bias_ledger.json", "e433_the_penalties_hold_the_weights.json",
                 "e432_the_interference_runs_through_the_bias.json"],
    "cells": 207,
    "bias_ratio": {"replay": 0.9461, "ewc": 1.5076, "ewc-block": 1.4734, "ewc-block-rand": 1.4556},
    "drift_ratio": {"replay": 0.9838, "ewc": 0.7184, "ewc-block": 0.7507, "ewc-block-rand": 0.752},
    "joint_share": {"replay": 0.0534, "ewc": 0.9091, "ewc-block": 0.8333, "ewc-block-rand": 0.7895},
    "channel_bias_share": {"cell": {"naive": [0.3961, 0.4902], "ewc-block": [0.7554, 0.8995]},
                           "pair/plastic": {"naive": [0.4524, 0.4359], "ewc": [0.9839, 0.9195],
                                            "replay": [0.5863, 0.7395]}},
    "frozen_bias_max": 0.0,
}
ROWS = {
    "the cells the parameters are pooled over": "207",
    "the buffer's bias ratio": "0.9461",
    "the diagonal penalty's bias ratio": "1.5076",
    "the buffer's drift ratio": "0.9838",
    "the diagonal penalty's drift ratio": "0.7184",
    "the buffer's cells with the weights held and the bias pushed": "0.0534",
    "the diagonal penalty's cells with the weights held and the bias pushed": "0.9091",
    "the diagonal penalty's bias share of the interference account": "0.9839",
    "the unpenalised arm's bias share of the interference account": "0.4524",
    "the frozen side's bias half": "0.0",
}
FIRST_OK = {"markers": True, "rows": 21,
            "verdicts": {f"BE{i}": f"MET -- claim {i}" for i in range(1, 6)}}


def _doc(rows=None, parameters=None, naming=True, revision=7, first=None, unknown=(), ok=True, reason="absent"):
    if not ok:
        return {"ok": False, "reason": reason, "rows": {}, "unknown": [], "region": False, "artifact_named": False,
                "revision_named": False, "checked": {}, "parameters": {}, "first_region": False, "first": {},
                "spans": {}}
    rows = ROWS if rows is None else rows
    parameters = PARAMETERS if parameters is None else parameters
    checked = {l: e435._agrees(rows[l], e435._value(parameters, p), m)
               for l, (p, m) in e435.VOCABULARY.items() if l in rows}
    first = FIRST_OK if first is None else first
    first_region = bool(first.get("markers")) and len(first.get("verdicts") or {}) == 5 and all(
        v.startswith("MET") for v in (first.get("verdicts") or {}).values())
    return {"ok": True, "reason": None, "rows": dict(rows), "unknown": sorted(unknown),
            "region": True, "artifact_named": naming, "revision_named": revision == 7, "checked": checked,
            "parameters": parameters, "first_region": first_region, "first": first,
            "spans": {"rows": len(rows), "vocabulary": len(e435.VOCABULARY),
                      "first_rows": first.get("rows", 0)}}


def _judge(**kw):
    return {row["id"]: row["verdict"] for row in e435.judge(_doc(**kw))}


def _rows(**kw):
    out = dict(ROWS)
    out.update(kw)
    return out


def test_the_five_claims_read_both_faces():
    #: the front page's shape: both regions carried, every row the card's own, the first region's claims still green
    j = _judge()
    for cid in ("BK1", "BK2", "BK3", "BK4", "BK5"):
        assert j[cid].startswith("MET"), (cid, j[cid])

    # BK1: an unknown label, the artifact's name absent, and the wrong revision
    assert _judge(unknown=["an unknown clause"])["BK1"].startswith("FALSIFIER")
    assert _judge(naming=False)["BK1"].startswith("FALSIFIER")
    assert _judge(revision=6)["BK1"].startswith("FALSIFIER")

    # BK2: a cells row and a bias ratio that are not the card's
    assert _judge(rows=_rows(**{"the cells the parameters are pooled over": "200"}))["BK2"].startswith("FALSIFIER")
    assert _judge(rows=_rows(**{"the buffer's bias ratio": "0.85"}))["BK2"].startswith("FALSIFIER")

    # BK3: a joint row that is not the card's
    assert _judge(rows=_rows(**{"the diagonal penalty's cells with the weights held and the bias pushed": "0.50"}))[
        "BK3"].startswith("FALSIFIER")

    # BK4: a channel row and the frozen side's half, each off the card's
    assert _judge(rows=_rows(**{"the unpenalised arm's bias share of the interference account": "0.90"}))[
        "BK4"].startswith("FALSIFIER")
    assert _judge(rows=_rows(**{"the frozen side's bias half": "0.01"}))["BK4"].startswith("FALSIFIER")

    # BK5: a first region whose markers are gone, and one whose claims have turned red
    assert _judge(first={"markers": False, "rows": 21, "verdicts": FIRST_OK["verdicts"]})["BK5"].startswith("FALSIFIER")
    red = dict(FIRST_OK, verdicts={**FIRST_OK["verdicts"], "BE3": "FALSIFIER FIRED -- a row disagrees"})
    assert _judge(first=red)["BK5"].startswith("FALSIFIER")

    #: the README or the card absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e435.judge(_doc(ok=False)))


def test_the_region_and_the_vocabulary_are_registered():
    #: the front page, the card artifact, the two markers, the vocabulary's size and the tolerances
    assert e435.README.name == "README.md"
    assert e435.CARD.name == "e434_the_game_card_revision_seven.json"
    assert e435.START.startswith("<!-- e435") and e435.END == "<!-- end e435 -->"
    assert len(e435.VOCABULARY) == 10 and len(ROWS) == 10
    assert sorted(e435.GROUPS) == ["BK2", "BK3", "BK4"], sorted(e435.GROUPS)
    assert sum(len(labels) for _, labels in e435.GROUPS.values()) == len(e435.VOCABULARY)
    assert e435.TOL == 1e-3


def test_the_live_region_and_the_artifact_carries_no_counted_keys():
    p = Path("runs/e435_the_front_pages_second_region.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e435.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e435.judge(d)}
    #: the region being carried and the first region still holding are structural facts
    assert verdicts["BK1"].startswith("MET") and verdicts["BK5"].startswith("MET"), verdicts
    assert d["region"] and d["artifact_named"] and d["revision_named"], d["spans"]
    assert len(d["rows"]) == len(e435.VOCABULARY), len(d["rows"])
    assert not d["unknown"], d["unknown"]
    assert all(label in d["checked"] for label in d["rows"]), sorted(set(d["rows"]) - set(d["checked"]))
    assert d["first_region"], d["first"]
    #: the README on disk carries both regions and the front page's own scope blockquote is untouched
    text = Path("README.md").read_text(encoding="utf-8")
    assert e435.START in text and e435.END in text, "the parameters markers are on disk"
    assert "<!-- e429: the closed-loop card's numbers, checked against its own artifact -->" in text
    assert "Scoped 2026-09-29, re-read 2026-10-01" in text, "the front page's scope blockquote is untouched"
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
