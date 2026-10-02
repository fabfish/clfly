"""`e370` lets the distance fall where it falls over sixteen draws, so the tests pin both faces of the four claims,
the unreachable case, and the live reading's own distribution.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e370_the_distance_moves_the_cliff as e370


def _src(distance, clears=None, direct=0):
    return {"distance": distance, "predicted_last": e370.predicted_last(distance), "accuracy": {},
            "last_clearing": e370.predicted_last(distance) if clears is None else clears,
            "direct_edges": direct}


def _row(circuit="c@n952", size=952, draw=0, action=None, cue=None):
    return {"circuit": circuit, "size": size, "draw_seed": draw,
            "sources": {"cue": _src(0) if cue is None else cue, "action": _src(1, direct=1) if action is None else action}}


def _doc(rows=None):
    rows = {"300:0": _row(action=_src(1, direct=1)), "300:1": _row(action=_src(1, direct=2)),
            "600:0": _row("c@n1149", 1149, action=_src(2, direct=0))} if rows is None else rows
    return {"rows": rows, "sizes": [300, 600], "tau": e370.TAU, "chance": 0.25}


def _judge(**kw):
    return {row["id"]: row for row in e370.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    j = _judge()
    for cid in ("Q1", "Q2", "Q3", "Q4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # Q1: one distance everywhere, which is the case this unit exists to avoid
    flat = _judge(rows={"a": _row(action=_src(2, direct=0)), "b": _row(action=_src(2, direct=0))})
    assert flat["Q1"]["verdict"].startswith("FALSIFIER"), flat["Q1"]

    # Q2: a cliff that is not its own draw's distance, and the unreachable case where both sides are None
    bad = _judge(rows={"a": _row(action=_src(1, clears=8)), "b": _row(action=_src(2, direct=0))})
    assert bad["Q2"]["verdict"].startswith("FALSIFIER"), bad["Q2"]
    gone = _judge(rows={"a": _row(action=_src(None)), "b": _row(action=_src(2, direct=0))})
    assert gone["Q2"]["verdict"].startswith("MET"), gone["Q2"]
    #: and an unreachable population that clears somewhere is a fired claim, not a refusal
    assert _judge(rows={"a": _row(action=_src(None, clears=9))})["Q2"]["verdict"].startswith("FALSIFIER")

    # Q3: two distances sharing a step, an order reversed, and one distance alone
    share = _judge(rows={"a": _row(action=_src(1, clears=9)), "b": _row(action=_src(2, clears=9))})
    assert share["Q3"]["verdict"].startswith("FALSIFIER"), share["Q3"]
    rev = _judge(rows={"a": _row(action=_src(1, clears=8)), "b": _row(action=_src(2, clears=9))})
    assert rev["Q3"]["verdict"].startswith("FALSIFIER"), rev["Q3"]
    one = _judge(rows={"a": _row(action=_src(1)), "b": _row(action=_src(1))})
    assert one["Q3"]["verdict"].startswith("FALSIFIER"), one["Q3"]

    # Q4: a control that moves
    assert _judge(rows={"a": _row(cue=_src(0, clears=9)), "b": _row(action=_src(2, direct=0))})[
        "Q4"]["verdict"].startswith("FALSIFIER")

    #: no configuration drawn refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e370.judge({"rows": {}}))


def test_the_bar_is_chance_plus_clears():
    assert e370.last_clearing({t: 0.2578 for t in e370.STEPS}) is None
    assert e370.last_clearing({t: 0.294 for t in e370.STEPS}) is None
    assert e370.last_clearing({t: (0.30 if t <= 8 else 0.20) for t in e370.STEPS}) == 8
    assert e370.last_clearing({0: 0.9}) == 0


def test_the_live_reading_has_both_distances_and_a_still_control():
    p = Path("runs/e370_the_distance_moves_the_cliff.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e370.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    for cid in ("Q1", "Q2", "Q3", "Q4"):
        claim = next(row for row in d["claims"] if row["id"] == cid)
        assert claim["verdict"].startswith("MET"), claim
    #: the direct-edge count is what the distance is one when it is zero and two when it is not
    for entry in d["rows"].values():
        action = entry["sources"]["action"]
        assert action["distance"] == (1 if action["direct_edges"] else 2), action
        assert action["last_clearing"] == action["predicted_last"], action
        #: the cue source's drive population is the cue population itself, so its walk is zero by construction
        assert entry["sources"]["cue"]["distance"] == 0, entry["sources"]["cue"]
    #: the sweep has to have produced more than one distance for its own claim to mean anything
    assert len({entry["sources"]["action"]["distance"] for entry in d["rows"].values()}) >= 2, d["rows"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
