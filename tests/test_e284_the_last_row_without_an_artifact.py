"""`e284` reads the paper's reproducibility table for three mechanical properties: its artifact cells, its commands,
and why a row leaves no artifact. One of the three registered claims fired, and the tests pin which.

The three cells the reading belongs to are the last three rows of the paper's table, and the two that matter are the
`e12_control_spread` pair.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e284_the_last_row_without_an_artifact as e284

ROW_WITH = "| a claim | `python -m experiments.e284_x --seed0 0 --json-out runs/whatever.json` | `runs/whatever.json` |"
ROW_NONE = "| a claim | `python -m experiments.e284_x --seed0 0` | *(none)* |"
ROW_TEXT = """some prose
| claim | command | artifact |
|---|---|---|
| one | `python -m experiments.e284_x --json-out runs/a.json` | `runs/a.json` |
| two | `python -m experiments.e284_x --seed0 0` | *(none)* |
| three | `python -m experiments.e284_x --json-out …` | `runs/e86_drawsd_*` |
"""


def test_the_table_is_read_as_rows_and_cells():
    rows = e284.table_rows(ROW_TEXT)
    # the prose line, and the header's rule line, are not rows
    assert len(rows) == 4, rows
    assert all(len(e284.cells(r)) == 3 for r in rows), [e284.cells(r) for r in rows]
    assert e284.cells(ROW_WITH)[2] == "`runs/whatever.json`"


def test_the_flag_is_read_from_the_command_span_and_not_from_the_prose():
    # a module that has the flag, and one that does not
    assert e284.has_flag("experiments.e12_control_spread") is True
    assert e284.has_flag("clfly.lgcl.repro") is False
    assert e284.has_flag("experiments.no_such_module_at_all") is False
    assert e284.module_path("clfly.lgcl.repro").name == "repro.py", e284.module_path("clfly.lgcl.repro")


def _reading(rows=None, missing=(), commands=("experiments.e284_x",), unimportable=(), n_without=1, n_flagged=1,
             artifacts=("runs/a.json",), why=None, row_command=None):
    return {"rows": 4, "cells": 12, "artifact_mentions": len(artifacts), "artifacts": list(artifacts),
            "missing": list(missing), "commands": list(commands), "unimportable": list(unimportable),
            "reproducibility_rows": 2, "rows_with_an_artifact": 1, "rows_without_an_artifact": [ROW_NONE],
            "why": why or [], "artifact_free_rows_whose_runner_has_the_flag": {}, "n_without": n_without,
            "n_without_and_flagged": n_flagged, "row_command": row_command}


def _rep(draw_sd=4.69e-5, delta=0.000215, draws=5, seeds=2):
    return {"path": "runs/e12_control_spread.json", "delta": delta, "draw_sd": draw_sd, "seed_sem": 0.00266,
            "sigma_single_draw": 0.081, "sigma_with_draw_noise": 0.115, "draws": draws, "seeds": seeds,
            "circuit_size": 800, "column": "cell_type", "min_size": 1, "timing_s": 222.5}


def test_the_three_claims_read_both_faces():
    j = {r["id"]: r for r in e284.judge(_reading())}
    for cid in ("V1", "V2", "V3"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]
    j = {r["id"]: r for r in e284.judge(_reading(missing=("runs/gone.json",)))}
    assert j["V1"]["verdict"].startswith("FALSIFIER FIRED"), j["V1"]
    j = {r["id"]: r for r in e284.judge(_reading(unimportable=("experiments.nope",)))}
    assert j["V2"]["verdict"].startswith("FALSIFIER FIRED"), j["V2"]
    # one artifact-free row whose runner has no flag is V3's falsifier
    j = {r["id"]: r for r in e284.judge(_reading(n_without=2, n_flagged=1))}
    assert j["V3"]["verdict"].startswith("FALSIFIER FIRED"), j["V3"]
    assert e284.judge(None)[0]["verdict"].startswith("REFUSED")
    assert e284.judge({"artifacts": []})[0]["verdict"].startswith("REFUSED")
    # V4 is refused without the artifact, met inside the band, and fired outside it
    assert e284.judge(_reading())[3]["verdict"].startswith("REFUSED")
    j = {r["id"]: r for r in e284.judge(_reading(row_command=_rep()))}
    assert j["V4"]["verdict"].startswith("MET"), j["V4"]
    for sd in (2e-5, 1.2e-4, 1.1e-3, 5e-3):
        j = {r["id"]: r for r in e284.judge(_reading(row_command=_rep(draw_sd=sd)))}
        assert j["V4"]["verdict"].startswith("FALSIFIER FIRED"), (sd, j["V4"])


def test_the_live_paper_is_read_as_the_finding_states_it():
    """The artifact cells are backed and the commands resolve; the artifact-free rows are three kinds, and the one
    V3's falsifier fires on is the test-suite row, where an empty cell is the right answer."""
    if not e284.PAPER.exists():
        return
    r = e284.reading(e284.PAPER.read_text(encoding="utf-8"))
    assert not r["missing"], r["missing"]
    assert not r["unimportable"], r["unimportable"]
    assert len(r["artifacts"]) >= 30 and not set(r["artifacts"]) & set(r["missing"]), r["artifacts"][:5]
    assert len(r["commands"]) >= 10, r["commands"]
    # the artifact-free rows: at least one names a family as a glob, and the test-suite row's runner has no flag
    kinds = {(w["command_declares_the_flag"], w["cell_holds_a_glob"], bool(w["runners_with_the_flag"]))
             for w in r["why"]}
    assert (False, False, False) in kinds, kinds
    assert any(w["cell_holds_a_glob"] for w in r["why"]), r["why"]
    j = {x["id"]: x for x in e284.judge(r)}
    assert j["V1"]["verdict"].startswith("MET"), j["V1"]
    assert j["V2"]["verdict"].startswith("MET"), j["V2"]
    assert j["V3"]["verdict"].startswith("FALSIFIER FIRED"), j["V3"]
    rep = e284.reproduction()
    assert rep is not None, "the row's artifact is on disk"
    assert rep["draws"] >= 5 and rep["seeds"] >= 2 and rep["circuit_size"] == 800, rep
    assert 4e-5 <= rep["draw_sd"] <= 9e-5 < 1.1e-3, rep["draw_sd"]
    r["row_command"] = rep
    j = {x["id"]: x for x in e284.judge(r)}
    assert j["V4"]["verdict"].startswith("MET"), j["V4"]


def test_the_artifact_carries_the_same_reading():
    p = Path("runs/e284_the_last_row_without_an_artifact.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["missing"] == [], d["missing"]
    assert d["unimportable"] == [], d["unimportable"]
    # a band rather than the digit: the paper gains and loses artifact paths as it is edited
    live = e284.reading(e284.PAPER.read_text(encoding="utf-8"))
    assert abs(len(d["artifacts"]) - len(live["artifacts"])) <= 0.2 * len(live["artifacts"]), len(live["artifacts"])
    claims = {x["id"]: x for x in d["claims"]}
    assert claims["V1"]["verdict"].startswith("MET"), claims["V1"]
    assert claims["V2"]["verdict"].startswith("MET"), claims["V2"]
    assert claims["V3"]["verdict"].startswith("FALSIFIER FIRED"), claims["V3"]
    assert claims["V4"]["verdict"].startswith("MET"), claims["V4"]
    assert d["rows_with_an_artifact"] >= 8, d["rows_with_an_artifact"]
    # the correction's own number: 4.69e-5 sits in the band §4.3 states and 23x below the row's 1.1e-3
    rep = d["row_command"]
    assert 4e-5 <= rep["draw_sd"] <= 9e-5, rep
    assert 1.1e-3 / rep["draw_sd"] > 10, rep
    assert d["n_without"] <= 2 and d["n_without_and_flagged"] <= d["n_without"], d["n_without"]
