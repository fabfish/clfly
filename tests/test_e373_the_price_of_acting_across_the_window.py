"""`e373` prices acting at every step of `e363`'s grid by reading six trained runs, so the tests pin both faces of
the four claims, the refusal when a pair is incomplete, and the live table's own shape.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e373_the_price_of_acting_across_the_window as e373

STEPS = (0, 10, 11)


def _run(source, step, diag=0.80, reps=20, coupling=None, basis="cell_class", tasks=3, channel=0.30, forget=0.35):
    drive_from_cue = source == "cue"
    coupling = (e373.CUE_COUPLING if drive_from_cue else e373.ACTION_COUPLING) if coupling is None else coupling
    payload = {
        "config": {"loop_cue_at": step, "loop_drive_from_cue": drive_from_cue, "loop_world_leak": 0.35,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": 8,
                   "loop_world_modes": 0, "loop_world_nonlinear": False, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": 0, "iters": 500},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "cw" if drive_from_cue else "aw",
                     "world_read_sha1": "cr" if drive_from_cue else "r", "world_leak": 0.35, "world_coupled": True,
                     "world_coupling_sha1": coupling, "world_nonlinear": False, "drive_from_cue": drive_from_cue,
                     "cue_at": step, "cue_sha1": "c", "action_sha1": "c" if drive_from_cue else "a",
                     "feedback_sha1": "f", "n_cue": 12, "n_action": 12 if drive_from_cue else 8},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {arm: {"final_accuracy": diag, "mean_forgetting": forget, "learned": [diag] * tasks,
                          "replicates": [{"final_accuracy": diag, "mean_forgetting": forget,
                                          "learned": [diag] * tasks,
                                          "retention": [[diag if i == j else None for j in range(tasks)]
                                                        for i in range(tasks)],
                                          "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel,
                                                              "without_loop": 0.5} for j in range(tasks)]}
                                         for _ in range(reps)]}
                    for arm in ("naive", "replay")},
    }
    return payload


def _frozen(cue=(0.7891, 0.8555, 0.2578), action=(0.6602, 0.2578, 0.2578)):
    sd = {"cue": (0.2156, 0.0719, 0.0), "action": (0.2029, 0.0, 0.0)}
    cells = []
    for i, step in enumerate(STEPS):
        for source, accs in (("cue", cue), ("action", action)):
            cells.append({"source": source, "cue_at": step, "accuracy": accs[i], "chance": 0.25,
                          "world_sd": sd[source][i]})
    return {"cells": cells}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _doc(runs=None, frozen=None):
    """A reading built the way the unit builds one, from payloads written to temp files.

    A payload of ``None`` means the run is absent, which is pointed at a path that holds nothing rather than left
    at the corpus's own artifact.
    """
    import experiments.e373_the_price_of_acting_across_the_window as mod
    runs = runs or {}
    saved = dict(mod.RUNS)
    try:
        for key, payload in runs.items():
            mod.RUNS[key] = _write(payload) if payload is not None else Path("runs/absent_for_this_test.json")
        doc = mod.reading(frozen_path=_write(frozen if frozen is not None else _frozen()))
    finally:
        mod.RUNS.clear()
        mod.RUNS.update(saved)
    return doc


def _judge(**kw):
    return {row["id"]: row for row in e373.judge(_doc(**kw))}


def _default_runs():
    return {("cue", 0): _run("cue", 0, diag=0.8399), ("action", 0): _run("action", 0, diag=0.7691),
            ("cue", 10): _run("cue", 10, diag=0.5337), ("action", 10): _run("action", 10, diag=0.2361),
            ("cue", 11): _run("cue", 11, diag=0.2326), ("action", 11): _run("action", 11, diag=0.2361)}


def test_the_four_claims_read_both_faces():
    j = _judge(runs=_default_runs())
    for cid in ("S1", "S2", "S3", "S4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # S1: a shared field moved within a pair, and a coupling that is not the source's own
    bad = _default_runs()
    bad[("action", 0)] = _run("action", 0, diag=0.7691, basis="neuron")
    assert _judge(runs=bad)["S1"]["verdict"].startswith("FALSIFIER")
    worse = _default_runs()
    worse[("action", 10)] = _run("action", 10, diag=0.2361, coupling=e373.CUE_COUPLING)
    assert _judge(runs=worse)["S1"]["verdict"].startswith("FALSIFIER")

    # S2: a price that does not move with the margin, and one that moves too little to call
    flat = _default_runs()
    flat[("action", 10)] = _run("action", 10, diag=0.5337)
    assert _judge(runs=flat)["S2"]["verdict"].startswith("FALSIFIER")
    small = _default_runs()
    small[("action", 10)] = _run("action", 10, diag=0.4300)
    assert _judge(runs=small)["S2"]["verdict"].startswith("NULL")

    # S3: a source that clears chance at zero margin, which is the claim e364's finding forbids
    cleared = _default_runs()
    cleared[("action", 11)] = _run("action", 11, diag=0.40)
    assert _judge(runs=cleared)["S3"]["verdict"].startswith("FALSIFIER")

    # S4: a trained cost that reaches the frozen price, which at the wide step means the action source at 0.70
    reached = _default_runs()
    reached[("action", 0)] = _run("action", 0, diag=0.7000)
    assert _judge(runs=reached)["S4"]["verdict"].startswith("FALSIFIER")

    #: a step with one run of its pair missing refuses the claims that need it
    partial = _default_runs()
    partial[("action", 10)] = None
    doc = _doc(runs=partial)
    verdicts = {row["id"]: row["verdict"] for row in e373.judge(doc)}
    assert verdicts["S2"].startswith("REFUSED"), verdicts["S2"]
    assert verdicts["S1"].startswith("MET"), verdicts["S1"]

    #: nothing on disk refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e373.judge({"cost": {}, "facts": {}}))


def test_the_frozen_prices_are_read_off_their_own_cells():
    doc = e373.frozen_cells(_write(_frozen()))
    assert abs(doc[("cue", 0)]["accuracy"] - 0.7891) < 1e-12
    assert abs(doc[("action", 10)]["world_sd"]) < 1e-12
    #: a source and a step that the grid does not hold is absent rather than zero
    assert ("cue", 5) not in doc
    assert e373.frozen_cells(Path("runs/does_not_exist.json")) == {}


def test_the_live_reading_has_the_shape_the_line_measured():
    p = Path("runs/e373_the_price_of_acting_across_the_window.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e373.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    assert all(next(row for row in d["claims"] if row["id"] == cid)["verdict"].startswith("MET")
               for cid in ("S1", "S2", "S3", "S4")), d["claims"]
    #: the wide step is where both channels are live, and it is the smallest price in the table
    cost = {int(k): v for k, v in d["cost"].items()}
    assert cost[0]["delta"] < cost[10]["delta"], cost
    #: the middle step's action-source world is at rest in the frozen grid, which is why its price is not a cost
    assert d["frozen"]["action@10"]["world_sd"] == 0.0, d["frozen"]["action@10"]
    assert d["frozen"]["cue@10"]["world_sd"] > 0.0, d["frozen"]["cue@10"]
    #: and the read step's price is inside the resolution rather than merely small
    assert abs(cost[11]["delta"]) < e373.FLAT, cost[11]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
