"""`e363` tells the two causes of `e362`'s limit apart in six frozen rolls, so the tests pin the grid, the shared
fields, the drive's fingerprint following the cue's and both faces of the five claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e363_where_the_cue_can_reach_the_world as e363


def _reading(grid=None, chance=0.25, world_reads=("r1", "r2")):
    """The six cells from a 2x3 accuracy grid, with the drive's fingerprints following the cue's where they should."""
    grid = grid if grid is not None else {"action": {0: 0.66, 10: 0.26, 11: 0.26},
                                          "cue": {0: 0.79, 10: 0.86, 11: 0.26}}
    cells = []
    for i, s in enumerate(e363.SOURCES):
        for k in e363.STEPS:
            cells.append({"source": s, "cue_at": k, "accuracy": grid[s][k], "chance": chance,
                          "world_sd": 0.2, "cue_sha1": "c", "action_sha1": "c" if s == "cue" else "a",
                          "feedback_sha1": "f", "drive_from_cue": s == "cue",
                          "world_read_sha1": world_reads[i], "world_dims": 8, "world_leak": 0.35, "cue_at_summary": k})
    by = {(c["source"], c["cue_at"]): c for c in cells}
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "n_symbols": 4, "chance": chance,
            "n_examples": 512, "read_step": 11, "sources": list(e363.SOURCES), "steps": list(e363.STEPS),
            "cells": cells, "world_dims": 8, "world_leak": 0.35,
            "accuracy": {f"{s}@{k}": by[(s, k)]["accuracy"] for s in e363.SOURCES for k in e363.STEPS},
            "gap_at_read_step": {s: by[(s, 0)]["accuracy"] - by[(s, 11)]["accuracy"] for s in e363.SOURCES}}


def _judge(r):
    return {row["id"]: row for row in e363.judge(r)}


def test_the_five_claims_read_both_faces():
    j = _judge(_reading())
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    #: the registered prediction for T5 is that ONE step of margin is enough in both sources, and it is not in the
    #: action source -- that firing is this unit's finding
    assert j["T5"]["verdict"].startswith("FALSIFIER"), j["T5"]

    # T1: a cell whose action fingerprint does not follow its source, and a shared field that differs
    cells = _reading()["cells"]
    cells[0]["action_sha1"] = "c"          # an action-source cell pretending to read the cue
    r = _reading()
    r["cells"][0]["action_sha1"] = "c"
    assert _judge(r)["T1"]["verdict"].startswith("FALSIFIER")
    r2 = _reading()
    r2["cells"][3]["world_leak"] = 0.5
    assert _judge(r2)["T1"]["verdict"].startswith("FALSIFIER")
    # T2: a source that carries the cue at the read step
    assert _judge(_reading({"action": {0: 0.66, 10: 0.26, 11: 0.60},
                            "cue": {0: 0.79, 10: 0.86, 11: 0.26}}))["T2"]["verdict"].startswith("FALSIFIER")
    # T3: a source that cannot carry it even from step 0
    assert _judge(_reading({"action": {0: 0.30, 10: 0.26, 11: 0.26},
                            "cue": {0: 0.79, 10: 0.86, 11: 0.26}}))["T3"]["verdict"].startswith("FALSIFIER")
    # T4: a source that loses nothing from step 0 to the read step
    assert _judge(_reading({"action": {0: 0.31, 10: 0.26, 11: 0.26},
                            "cue": {0: 0.79, 10: 0.86, 11: 0.26}}))["T4"]["verdict"].startswith("FALSIFIER")
    # T5: both sources carrying it with one step of margin is what the claim asked for
    assert _judge(_reading({"action": {0: 0.66, 10: 0.70, 11: 0.26},
                            "cue": {0: 0.79, 10: 0.86, 11: 0.26}}))["T5"]["verdict"].startswith("MET")
    # fewer than six cells refuses every claim
    short = _reading()
    short["cells"] = short["cells"][:4]
    assert all(row["verdict"].startswith("REFUSED") for row in e363.judge(short))


def test_the_drive_map_follows_the_population_and_the_cue_does_not_move():
    #: the cue's fingerprint is the cell-invariant one: the draw is the same three populations in every cell
    cells = _reading()["cells"]
    assert len({c["cue_sha1"] for c in cells}) == 1 and len({c["feedback_sha1"] for c in cells}) == 1, cells
    #: and the action's either is the cue's or is not, per source -- never something in between
    assert all((c["source"] == "cue") == (c["action_sha1"] == c["cue_sha1"]) for c in cells), cells
    #: the grid is two sources by three cue steps
    assert len({(c["source"], c["cue_at"]) for c in cells}) == 6, cells


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e363_where_the_cue_can_reach_the_world.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e363.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the rolls landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert len(d["cells"]) == 6, d["cells"]
    assert {c["source"] for c in d["cells"]} == set(e363.SOURCES), d["cells"]
    #: at the read step both sources are at chance, and with a step of margin they are not equal
    assert all(abs(c["accuracy"] - d["chance"]) < 0.05 for c in d["cells"] if c["cue_at"] == 11), d["cells"]
    assert abs(d["accuracy"]["cue@10"] - d["accuracy"]["action@10"]) > 0.10, d["accuracy"]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
