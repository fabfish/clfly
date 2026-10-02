"""`e369` measures the cue population's distance to the drive population and the cliff formula it implies, so the
tests pin the walk itself on a hand-built mask, both faces of the four claims, and the live reading's distances.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from experiments import e369_why_the_cliff_is_where_it_is as e369


def _mask():
    """0 -> 1 -> 2 and 0 -> 3, with nothing leaving 2."""
    m = np.zeros((4, 4), dtype=bool)
    m[1, 0] = True
    m[2, 1] = True
    m[3, 0] = True
    return m


def test_the_walk_reads_the_direction_the_model_propagates_in():
    m = _mask()
    assert e369.distance(m, [0], [0]) == 0
    assert e369.distance(m, [0], [1]) == 1
    assert e369.distance(m, [0], [2]) == 2
    assert e369.distance(m, [0], [3]) == 1
    #: the arrows point one way, so a walk against them reaches nothing
    assert e369.distance(m, [2], [0]) is None
    #: and a source that reaches nothing at all is None rather than a large number
    assert e369.distance(m, [2], [3]) is None
    assert e369.distance(m, [0], [2], max_hops=1) is None


def _source(distance=2, predicted=None, clears=None):
    return {"drive_population": 8, "distance": distance,
            "predicted_last": e369.predicted_last(distance) if predicted is None else predicted,
            "accuracy": {t: 0.5 for t in e369.STEPS},
            "last_clearing": e369.predicted_last(distance) if clears is None else clears}


def _entry(circuit="c@n", size=1, edges=3, cue=None, action=None):
    return {"circuit": circuit, "size": size, "n_edges": edges,
            "sources": {"cue": cue or _source(0), "action": action or _source(2)}}


def _doc(rows=None, maps=None, sizes=(300, 600), reference=None):
    #: the default second size's distance **moves**, so the formula is checked against a number it has not seen
    rows = {"300": _entry("mb+cx+al@n952", 952, 20079),
            "600": _entry("mb+cx+al@n1149", 1149, 23551, action=_source(1))} if rows is None else rows
    maps = {"300:cue": {"world_drive_size": 96, "world_drive_nonzero": 96,
                        "world_read_size": 96, "world_read_nonzero": 96}} if maps is None else maps
    return {"rows": rows, "maps": maps, "sizes": list(sizes),
            "reference": {"artifact": "e368.json", "last_clearing": {"cue": 10, "action": 8}} if reference is None
            else reference}


def _judge(**kw):
    return {row["id"]: row for row in e369.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    j = _judge()
    for cid in ("P1", "P2", "P3", "P4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # P1: a direct edge, and a walk three hops long
    assert _judge(rows={"300": _entry(action=_source(1)), "600": _entry("b", 2)})["P1"]["verdict"].startswith("FALSIFIER")
    assert _judge(rows={"300": _entry(action=_source(3)), "600": _entry("b", 2)})["P1"]["verdict"].startswith("FALSIFIER")
    assert _judge(rows={"300": _entry(action=_source(None)), "600": _entry("b", 2)})["P1"]["verdict"].startswith("FALSIFIER")

    # P2: a curve whose cliff is not the distance's own
    assert _judge(rows={"300": _entry(action=_source(2, clears=9)), "600": _entry("b", 2)})[
        "P2"]["verdict"].startswith("FALSIFIER")

    # P3: the null case where the second size predicts the same number twice, and a curve that breaks even when
    # the distance moves
    same = _judge(rows={"300": _entry(), "600": _entry("c@n1149", 1149)})
    assert same["P3"]["verdict"].startswith("NULL"), same["P3"]
    broke = _judge(rows={"300": _entry(), "600": _entry("c@n1149", 1149, action=_source(1, clears=8))})
    assert broke["P3"]["verdict"].startswith("FALSIFIER"), broke["P3"]
    #: and one size is not a check
    assert _judge(rows={"300": _entry()}, sizes=(300,))["P3"]["verdict"].startswith("REFUSED")

    # P4: a world map with a hole in it
    assert _judge(maps={"300:cue": {"world_drive_size": 96, "world_drive_nonzero": 95,
                                    "world_read_size": 96, "world_read_nonzero": 96}})["P4"]["verdict"].startswith(
        "FALSIFIER")

    #: no circuit walked refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e369.judge({"rows": {}}))


def test_the_prediction_is_the_formula():
    assert e369.predicted_last(0) == e369.TAU - 2
    assert e369.predicted_last(2) == e369.TAU - 4
    #: an unreachable population has no last step rather than a step before the trial
    assert e369.predicted_last(None) is None
    assert e369.predicted_last(0, tau=8) == 6


def test_the_live_reading_matches_its_own_claims_and_the_curve():
    p = Path("runs/e369_why_the_cliff_is_where_it_is.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e369.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert len(d["rows"]) >= 2, sorted(d["rows"])
    for entry in d["rows"].values():
        #: the cue population is what the cue is written on, so its distance is zero by construction
        assert entry["sources"]["cue"]["distance"] == 0, entry["sources"]["cue"]
        for source, s in entry["sources"].items():
            assert s["last_clearing"] == s["predicted_last"], (source, s)
            assert s["last_clearing"] <= e369.TAU - 2, (source, s)
    #: the second size is a different draw and not the first circuit relabelled
    names = [entry["circuit"] for entry in d["rows"].values()]
    assert len(set(names)) == len(names), names
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
