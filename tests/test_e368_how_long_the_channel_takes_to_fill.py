"""`e368` measures the fill curve and the invariance `e367` could only report, so the tests pin both faces of the
four claims, the refusal when the frozen grid is absent, and the scale at which a body with a bias stops being
exactly at rest.
"""

from __future__ import annotations

import json
from pathlib import Path

from experiments import e368_how_long_the_channel_takes_to_fill as e368


def _cells(action_clears=8, cue_clears=10, action_first=0.6602, late_sd=0.0):
    cells = {}
    for step in e368.STEPS:
        cells[f"cue@{step}"] = {"accuracy": 0.80 if step <= cue_clears else 0.2578, "world_sd": 0.12,
                                "trial_range": 0.9}
        clears = step <= action_clears
        cells[f"action@{step}"] = {"accuracy": (action_first if step == 0 else 0.70) if clears else 0.2578,
                                   "world_sd": 0.15 if clears else late_sd, "trial_range": 0.9 if clears else 0.0}
    return cells


def _bodies(moves=False, spread=True, untrained_sd=0.0):
    bodies = {e368.UNTRAINED: {}}
    for step in e368.LATE:
        bodies[e368.UNTRAINED][f"action@{step}"] = {"world_sd": untrained_sd, "trial_range": 0.0,
                                                    "accuracy": 0.2578}
    for name in e368.BODIES[1:]:
        bodies[name] = {f"action@{step}": {"world_sd": 0.12 if spread else 0.0,
                                           "trial_range": 1e-8 if moves else 0.0, "accuracy": 0.2578}
                        for step in e368.LATE}
    return bodies


def _doc(cells=None, bodies=None, reference=None, last=None):
    cells = _cells() if cells is None else cells
    doc = {"cells": cells, "bodies": _bodies() if bodies is None else bodies, "late": list(e368.LATE),
           "reference": ({} if reference is None else reference), "chance": 0.25, "steps": list(e368.STEPS),
           "body_names": list(e368.BODIES)}
    doc["reference"] = {"action@11": {"world_sd": 0.0}, "action@10": {"world_sd": 0.0}} if reference is None \
        else reference
    doc["last_clearing"] = {s: e368.last_clearing(doc, s) for s in e368.SOURCES} if last is None else last
    return doc


def _judge(**kw):
    return {row["id"]: row for row in e368.judge(_doc(**kw))}


def test_the_four_claims_read_both_faces():
    j = _judge()
    for cid in ("W1", "W2", "W3", "W4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # W1: a body that is not at rest, and a corpus record that is not zero
    assert _judge(bodies=_bodies(untrained_sd=0.01))["W1"]["verdict"].startswith("FALSIFIER")
    assert _judge(reference={"action@11": {"world_sd": 0.0}, "action@10": {"world_sd": 0.05}})[
        "W1"]["verdict"].startswith("FALSIFIER")
    #: and the grid absent refuses rather than passing
    assert _judge(reference={})["W1"]["verdict"].startswith("REFUSED")

    # W2: a body whose world moves with the trial, in the unit's own real numbers, and the vacuous case
    assert _judge(bodies=_bodies(moves=True))["W2"]["verdict"].startswith("FALSIFIER")
    assert "moves with the trial" in _judge(bodies=_bodies(moves=True))["W2"]["verdict"]
    assert "vacuous" in _judge(bodies=_bodies(spread=False))["W2"]["verdict"]

    # W3: a channel that never filled
    assert _judge(cells=_cells(action_first=0.28))["W3"]["verdict"].startswith("FALSIFIER")

    # W4: a source that clears at the same step, and one that clears at no step
    assert _judge(last={"cue": 10, "action": 10})["W4"]["verdict"].startswith("FALSIFIER")
    assert _judge(last={"cue": 10, "action": 11})["W4"]["verdict"].startswith("FALSIFIER")
    assert _judge(last={"cue": 10, "action": None})["W4"]["verdict"].startswith("REFUSED")

    #: the curve absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e368.judge({"cells": {}}))


def test_last_clearing_reads_the_largest_step_that_clears():
    doc = _doc()
    assert e368.last_clearing(doc, "action") == 8, doc["cells"]["action@8"]
    assert e368.last_clearing(doc, "cue") == 10
    #: a source that clears nowhere is None rather than zero, so a comparison against it refuses
    flat = _doc(cells={f"{s}@{t}": {"accuracy": 0.2578, "world_sd": 0.0, "trial_range": 0.0}
                       for s in e368.SOURCES for t in e368.STEPS})
    assert e368.last_clearing(flat, "cue") is None and e368.last_clearing(flat, "action") is None
    #: and the bar is chance plus `CLEARS`, so a step just under it does not clear
    near = _doc(cells={**{f"cue@{t}": {"accuracy": 0.2578, "world_sd": 0.3, "trial_range": 0.0}
                         for t in e368.STEPS},
                       **{f"action@{t}": {"accuracy": 0.294, "world_sd": 0.3, "trial_range": 0.0}
                          for t in e368.STEPS}})
    assert e368.last_clearing(near, "cue") is None


def test_the_live_reading_is_at_rest_for_the_untrained_body_and_only_rounds_off_for_the_others():
    p = Path("runs/e368_how_long_the_channel_takes_to_fill.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e368.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the corpus landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    #: the untrained body has a zero bias, so its state is exactly zero and its world is exactly at rest
    for step in e368.LATE:
        cell = d["bodies"][e368.UNTRAINED][f"action@{step}"]
        assert cell["world_sd"] == 0.0 and cell["trial_range"] == 0.0, cell
    #: and a body with a bias is not at rest -- it has spread -- while what it does with the trial stays at the
    #: arithmetic's round-off: the claim's own bar was 1e-12, which a float32 pass cannot meet, and that is the
    #: finding rather than a defect to hide
    ranges = [per[f"action@{s}"]["trial_range"] for n, per in d["bodies"].items() if n != e368.UNTRAINED
              for s in e368.LATE]
    spreads = [per[f"action@{s}"]["world_sd"] for n, per in d["bodies"].items() if n != e368.UNTRAINED
               for s in e368.LATE]
    assert ranges and max(ranges) <= 1e-6, max(ranges)
    assert max(spreads) > 0.01, max(spreads)
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
