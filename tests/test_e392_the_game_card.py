"""`e392` writes the closed-loop benchmark down as a card and checks each clause against the corpus, so the tests pin
both faces of the five claims, the refusal when the corpus is unreadable, and the live card's own clauses.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from experiments import e392_the_game_card as e392


def _cell_row(artifact="e371_earned_label_cue0_actionsource_20reps.json", tasks=None, n_classes=None, train=96,
              test=48, arms=None, matrices=None):
    return {"artifact": artifact, "iters": 20, "repeats": 20, "lr": 0.003,
            "task_names": tasks if tasks is not None else list(e392.CARD["protocol"]["tasks"]),
            "n_classes": n_classes if n_classes is not None else [e392.CARD["substrate"]["classes_per_task"]],
            "train": train, "test": test, "arms": arms if arms is not None else list(e392.CARD["arms"]),
            "matrix_arms": matrices if matrices is not None else list(e392.CARD["arms"]),
            "world_drive_sha1": "d", "world_read_sha1": "r", "world_coupling_sha1": "c"}


def _invariants(agrees=True):
    sub = e392.CARD["substrate"]
    out = {}
    for field, want in (("circuit", sub["circuit"]), ("readout_subset", sub["readout_subset"]),
                        ("basis", sub["basis"]), ("circuit_size", sub["circuit_size"]), ("seed0", sub["seed0"])):
        out[field] = {"values": [json.dumps(want)], "card": want, "agrees": agrees}
    out["n_classes"] = {"values": [json.dumps([sub["classes_per_task"]])],
                        "card": sub["classes_per_task"], "agrees": agrees}
    return out


def _doc(n_window=40, cell=None, invariants=None, draws=None, scan=None, ok=True, reason="unreadable"):
    if not ok:
        #: `reading` refuses the whole unit when the corpus cannot be read
        return {"ok": False, "reason": reason}
    cell = cell if cell is not None else [_cell_row(f"e37{i}_x.json") for i in range(36)]
    draws = draws if draws is not None else {f: ['"one"'] for f in e392.WORLD_FIELDS}
    scan = scan if scan is not None else {"files": 768, "config_keys": ["a"] * 86, "n_config_keys": 86,
                                          "absent_hits": {}}
    return {"ok": True, "reason": None, "card": copy.deepcopy(e392.CARD), "n_window": n_window,
            "invariants": invariants if invariants is not None else _invariants(), "cell": cell,
            "n_cell": len(cell), "draws": draws, "scan": scan}


def _judge(**kw):
    return {row["id"]: row for row in e392.judge(_doc(**kw))}


def test_the_five_claims_read_both_faces():
    #: the corpus as it stands: one setting, a thirty-six artifact cell, one world and no reward key
    j = _judge()
    for cid in ("M1", "M2", "M3", "M4", "M5"):
        assert j[cid]["verdict"].startswith("MET"), (cid, j[cid])

    # M1: a field differing between two artifacts, one disagreeing with the card, and a window under the bound
    broken = _invariants()
    broken["basis"] = {"values": ['"cell_class"', '"side"'], "card": "cell_class", "agrees": False}
    assert _judge(invariants=broken)["M1"]["verdict"].startswith("FALSIFIER")
    disagreeing = _invariants()
    disagreeing["circuit_size"] = {"values": ["300"], "card": 300, "agrees": False}
    assert _judge(invariants=disagreeing)["M1"]["verdict"].startswith("FALSIFIER")
    assert _judge(n_window=e392.MIN_WINDOW - 1)["M1"]["verdict"].startswith("FALSIFIER")

    # M2: a cell under the bound
    assert _judge(cell=[_cell_row(f"e{i}.json") for i in range(e392.MIN_CELL - 1)])["M2"][
        "verdict"].startswith("FALSIFIER")

    # M3: an ordering, a split and a class count that differ from the card
    assert _judge(cell=[_cell_row(tasks=["loop_heading", "loop_odour_identity", "loop_odour_input"])])["M3"][
        "verdict"].startswith("FALSIFIER")
    assert _judge(cell=[_cell_row(train=48, test=96)])["M3"]["verdict"].startswith("FALSIFIER")
    assert _judge(cell=[_cell_row(n_classes=[2])])["M3"]["verdict"].startswith("FALSIFIER")

    # M4: an arm missing, and a matrix missing for an arm that ran
    assert _judge(cell=[_cell_row(arms=["naive"])])["M4"]["verdict"].startswith("FALSIFIER")
    assert _judge(cell=[_cell_row(arms=["naive", "replay"], matrices=["naive"])])["M4"][
        "verdict"].startswith("FALSIFIER")

    # M5: a second world draw, a reward-shaped key, and a scan under the bound
    two = {f: ['"one"'] for f in e392.WORLD_FIELDS}
    two["world_read_sha1"] = ['"one"', '"two"']
    assert _judge(draws=two)["M5"]["verdict"].startswith("FALSIFIER")
    assert _judge(scan={"files": 768, "config_keys": ["a"], "n_config_keys": 1,
                        "absent_hits": {"loop_reward": 3}})["M5"]["verdict"].startswith("FALSIFIER")
    assert _judge(scan={"files": e392.MIN_SCAN - 1, "config_keys": ["a"], "n_config_keys": 1,
                        "absent_hits": {}})["M5"]["verdict"].startswith("FALSIFIER")

    #: an unreadable corpus refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e392.judge(_doc(ok=False)))


def test_the_absent_pattern_names_what_the_card_says_is_absent():
    #: the pattern is the card's absent list made checkable, so each of its names must match and a loop knob must not
    for name in ("reward", "policy", "episode", "return", "goal"):
        assert e392.ABSENT_PATTERN.search(f"loop_{name}"), name
    for name in ("loop_cue_at", "loop_world_dims", "loop_drive_from_cue", "readout_from_world", "iters"):
        assert not e392.ABSENT_PATTERN.search(name), name


def test_the_live_card_is_checked_and_carries_no_counted_keys():
    p = Path("runs/e392_the_game_card.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e392.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    verdicts = {row["id"]: row["verdict"] for row in e392.judge(d)}
    #: the substrate clause and the absence scan are structural facts about the corpus
    assert verdicts["M1"].startswith("MET") and verdicts["M5"].startswith("MET"), verdicts
    #: the card's own clauses are the module's, so the artifact cannot drift from the definition it publishes
    assert d["card"]["substrate"] == e392.CARD["substrate"], d["card"]["substrate"]
    assert d["card"]["loop"] == e392.CARD["loop"], d["card"]["loop"]
    assert d["card"]["absent"] == e392.CARD["absent"], d["card"]["absent"]
    #: the cell is a subset of the window, and the window a subset of the scan
    assert 0 < d["n_cell"] <= d["n_window"] <= d["scan"]["files"], (d["n_cell"], d["n_window"], d["scan"]["files"])
    #: a card is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
