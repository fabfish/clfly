"""`e366` prices `e365`'s gap with three frozen cells, so the tests pin the ladder's arithmetic, the reference
comparison and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e366_what_the_probes_gap_is_made_of as e366


def _reading(big=0.8594, small=0.7917, three=0.8194, per_task=None, recorded=0.8555, trained=0.5337):
    cells = {"one512": {"accuracy": big, "n_train": 256, "n_test": 256, "n_tasks": 1},
             "one96": {"accuracy": small, "n_train": 48, "n_test": 48, "n_tasks": 1},
             "three96": {"accuracy": three, "per_task": per_task or [three] * 3, "n_train": 48, "n_test": 48,
                         "n_tasks": 3}}
    return {"circuit": "mb+cx+al@n952", "size": 952, "readout": 32, "seed": 0, "tau": 12, "n_symbols": 4,
            "chance": 0.25, "cue_at": 10, "drive_from_cue": True, "world_dims": 8, "world_leak": 0.35,
            "cells": cells, "reference": {"artifact": "ref.json", "accuracy": recorded},
            "trained": {"artifact": "trained.json", "diagonal": trained},
            "splits_cost": big - small, "suite_cost": small - three,
            "reference_gap": big - recorded,
            "training_gap": (three - trained) if trained is not None else None}


def _judge(r):
    return {row["id"]: row for row in e366.judge(r)}


def test_the_four_claims_read_both_faces():
    j = _judge(_reading())
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T2: a cell that does not reproduce the recorded one, and one between the bars
    assert _judge(_reading(big=0.60))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(big=0.80))["T2"]["verdict"].startswith("NULL")
    # T2: and the artifact being absent refuses rather than compares
    r = _reading()
    r["reference"] = {"artifact": None, "accuracy": None}
    r["reference_gap"] = None
    assert _judge(r)["T2"]["verdict"].startswith("REFUSED")
    # T3: splits that cost nothing, and one between the bars
    assert _judge(_reading(big=0.7927, small=0.7917))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(big=0.8017, small=0.7917))["T3"]["verdict"].startswith("NULL")
    assert _judge(_reading(big=0.90, small=0.7917))["T3"]["verdict"].startswith("MET")
    # T4: an arrangement that loses the signal, and one between the bars
    assert _judge(_reading(small=0.7917, three=0.60))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(_reading(small=0.7917, three=0.72))["T4"]["verdict"].startswith("NULL")
    # fewer than three cells refuses every claim
    short = _reading()
    short["cells"].pop("three96")
    assert all(row["verdict"].startswith("REFUSED") for row in e366.judge(short))


def test_the_ladder_is_two_prices_and_a_residue():
    #: the two prices are read off the cells themselves, and the third of the gap -- the training -- is computed
    #: and reported, not claimed, so it must be in the record without a verdict attached to it
    r = _reading()
    assert abs(r["splits_cost"] - (0.8594 - 0.7917)) < 1e-12, r["splits_cost"]
    assert abs(r["suite_cost"] - (0.7917 - 0.8194)) < 1e-12, r["suite_cost"]
    assert abs(r["training_gap"] - (0.8194 - 0.5337)) < 1e-12, r["training_gap"]
    assert "training_gap" not in {row["id"] for row in e366.judge(r)}, "the residue is reported, not claimed"


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e366_what_the_probes_gap_is_made_of.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e366.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    assert set(d["cells"]) == {"one512", "one96", "three96"}, sorted(d["cells"])
    #: the three cells are one world with two differences: the example count and the number of tasks
    assert d["cells"]["one512"]["n_tasks"] == 1 and d["cells"]["three96"]["n_tasks"] == 3, d["cells"]
    assert d["cells"]["one512"]["n_train"] > d["cells"]["one96"]["n_train"], d["cells"]
    assert d["cells"]["one96"]["n_train"] == d["cells"]["three96"]["n_train"], d["cells"]
    assert len(d["cells"]["three96"]["per_task"]) == 3, d["cells"]["three96"]
    #: the reference cell is compared with the artifact's own recorded number
    assert d["reference"]["accuracy"] is not None and d["trained"]["diagonal"] is not None, d
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
