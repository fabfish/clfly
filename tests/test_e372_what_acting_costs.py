"""`e372` trains the same game with the channel handed over, so the tests pin the two-run configuration check, the
frozen licence, both faces of the five claims and the live pairing.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e372_what_acting_costs as e372

CUE_COUPLING = e372.CUE_COUPLING
ACTION_COUPLING = e372.ACTION_COUPLING


def _run(drive_from_cue=True, cue_step=0, diag=0.80, reps=20, tasks=3, coupling=None, basis="cell_class", iters=500,
         channel=0.30, forget=0.35, replay_forget=0.09):
    coupling = (CUE_COUPLING if drive_from_cue else ACTION_COUPLING) if coupling is None else coupling
    payload = {
        "config": {"loop_cue_at": cue_step, "loop_drive_from_cue": drive_from_cue, "loop_world_leak": 0.35,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": 8,
                   "loop_world_modes": 0, "loop_world_nonlinear": False, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": 0, "iters": iters},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "cw" if drive_from_cue else "aw",
                     "world_read_sha1": "cr" if drive_from_cue else "r", "world_leak": 0.35, "world_coupled": True,
                     "world_coupling_sha1": coupling, "world_nonlinear": False,
                     "drive_from_cue": drive_from_cue, "cue_at": cue_step, "cue_sha1": "c",
                     "action_sha1": "c" if drive_from_cue else "a", "feedback_sha1": "f",
                     "n_cue": 12, "n_action": 12 if drive_from_cue else 8},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {},
    }
    for arm in e372.ARMS:
        forget_arm = forget if arm == e372.NAIVE else replay_forget
        reps_list = []
        for r in range(reps):
            reps_list.append({
                "final_accuracy": diag, "mean_forgetting": forget_arm, "learned": [diag] * tasks,
                "forgetting_per_task": [forget_arm] * (tasks - 1), "final_per_task": [diag] * tasks,
                "retention": [[diag if i == j else None for j in range(tasks)] for i in range(tasks)],
                "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel, "without_loop": 0.5}
                                   for j in range(tasks)]})
        payload["methods"][arm] = {"final_accuracy": diag, "final_sem": 0.01, "mean_forgetting": forget_arm,
                                   "forgetting_sem": 0.01, "learned": [diag] * tasks, "replicates": reps_list}
    return payload


def _frozen(cue=0.7891, action=0.6602):
    return {"cells": [{"source": "cue", "cue_at": 0, "accuracy": cue, "chance": 0.25, "world_sd": 0.2156},
                      {"source": "action", "cue_at": 0, "accuracy": action, "chance": 0.25, "world_sd": 0.2029},
                      {"source": "action", "cue_at": 10, "accuracy": 0.2578, "chance": 0.25, "world_sd": 0.0}]}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


_ABSENT = object()


def _judge(over=_ABSENT, played=_ABSENT, frozen=_ABSENT):
    chosen = {"over": _run(drive_from_cue=True, diag=0.80) if over is _ABSENT else over,
              "played": _run(drive_from_cue=False, diag=0.7691) if played is _ABSENT else played,
              "frozen": _frozen() if frozen is _ABSENT else frozen}
    paths = {k: _write(v) if v is not None else Path(f"runs/absent_{k}.json") for k, v in chosen.items()}
    return {row["id"]: row
            for row in e372.judge(e372.reading(overhand_path=paths["over"], played_path=paths["played"],
                                               frozen_path=paths["frozen"]))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("R1", "R2", "R3", "R4", "R5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # R1: the same source twice, a shared field moved, the wrong coupling, and the run this unit pairs against
    # absent
    assert _judge(played=_run(drive_from_cue=True, diag=0.7691))["R1"]["verdict"].startswith("FALSIFIER")
    assert _judge(over=_run(drive_from_cue=True, basis="neuron", diag=0.80))["R1"]["verdict"].startswith("FALSIFIER")
    assert _judge(over=_run(drive_from_cue=True, coupling=ACTION_COUPLING, diag=0.80))[
        "R1"]["verdict"].startswith("FALSIFIER")
    assert _judge(played=None)["R1"]["verdict"].startswith("REFUSED")

    # R2: a world at rest for the cue source too, one whose floor is between the bars, and the grid absent
    assert _judge(frozen=_frozen(cue=0.26))["R2"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_frozen(cue=0.32))["R2"]["verdict"].startswith("NULL")
    assert _judge(frozen={})["R2"]["verdict"].startswith("REFUSED")

    # R3: a handed-over game that does not train
    assert _judge(over=_run(drive_from_cue=True, diag=0.26))["R3"]["verdict"].startswith("FALSIFIER")

    # R4: an arm whose answer is not earned
    assert _judge(over=_run(drive_from_cue=True, channel=0.01))["R4"]["verdict"].startswith("FALSIFIER")

    # R5: a channel that is worth something, and one whose difference is too small to call
    assert _judge(over=_run(drive_from_cue=True, diag=0.95))["R5"]["verdict"].startswith("FALSIFIER")
    assert _judge(over=_run(drive_from_cue=True, diag=0.84))["R5"]["verdict"].startswith("NULL")

    #: the cue-source run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e372.judge(e372.reading(overhand_path=Path("runs/does_not_exist.json"),
                                                  played_path=_write(_run(drive_from_cue=False)),
                                                  frozen_path=_write(_frozen()))))


def test_the_two_frozen_cells_are_read_off_their_own_sources():
    doc = _write(_frozen())
    assert abs(e372.frozen_cell(doc, "cue", 0)["accuracy"] - 0.7891) < 1e-12
    assert abs(e372.frozen_cell(doc, "action", 0)["accuracy"] - 0.6602) < 1e-12
    #: the cue source has no late cell here that is the one this unit pairs against
    assert e372.frozen_cell(doc, "cue", 10) is None
    assert e372.frozen_cell(Path("runs/does_not_exist.json"), "cue", 0) is None


def test_the_live_reading_pairs_the_two_sources_at_one_step():
    p = Path("runs/e372_what_acting_costs.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e372.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["facts"]["over"]["loop_cue_at"] == e372.CUE_STEP, d["facts"]["over"]
    assert d["facts"]["played"]["loop_cue_at"] == e372.CUE_STEP, d["facts"]["played"]
    #: the two sources carry the two couplings, which is what the drive's population decides
    assert d["facts"]["over"]["world_coupling_sha1"] == CUE_COUPLING, d["facts"]["over"]
    assert d["facts"]["played"]["world_coupling_sha1"] == ACTION_COUPLING, d["facts"]["played"]
    for key in (f"over_{e372.NAIVE}", f"over_{e372.REPLAY}"):
        assert d["rows"][key]["n"] == e372.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
