"""`e371` trains the closed loop where the world can see the agent's own action, so the tests pin the two-run
configuration check, the frozen licence, both faces of the five claims and the live artifact's own step.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e371_the_game_the_agent_can_play as e371

ACTION_COUPLING = e371.COUPLING_SHA1


def _run(cue_step=0, diag=0.60, reps=20, tasks=3, coupling=ACTION_COUPLING, basis="cell_class", iters=500,
         channel=0.30, forget=0.35, replay_forget=0.09, drive_from_cue=False):
    payload = {
        "config": {"loop_cue_at": cue_step, "loop_drive_from_cue": drive_from_cue, "loop_world_leak": 0.35,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": 8,
                   "loop_world_modes": 0, "loop_world_nonlinear": False, "closed_loop": True, "repeats": reps,
                   "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": 0, "iters": iters},
        "env_draw": {"world_dims": 8, "world_drive_sha1": "aw", "world_read_sha1": "r", "world_leak": 0.35,
                     "world_coupled": True, "world_coupling_sha1": coupling, "world_nonlinear": False,
                     "drive_from_cue": drive_from_cue, "cue_at": cue_step, "cue_sha1": "c", "action_sha1": "a",
                     "feedback_sha1": "f", "n_cue": 12, "n_action": 8},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {},
    }
    for arm in e371.ARMS:
        forget_arm = forget if arm == e371.NAIVE else replay_forget
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


def _frozen(accuracy=0.6602, source=e371.FROZEN_SOURCE, step=e371.FROZEN_STEP):
    return {"cells": [{"source": source, "cue_at": step, "accuracy": accuracy, "chance": 0.25, "world_sd": 0.2029},
                      {"source": source, "cue_at": 10, "accuracy": 0.2578, "chance": 0.25, "world_sd": 0.0},
                      {"source": "cue", "cue_at": 0, "accuracy": 0.7891, "chance": 0.25, "world_sd": 0.2156}]}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


_ABSENT = object()


def _judge(played=_ABSENT, empty=_ABSENT, frozen=_ABSENT):
    chosen = {"played": _run(diag=0.60) if played is _ABSENT else played,
              "empty": _run(cue_step=10, diag=0.2361) if empty is _ABSENT else empty,
              "frozen": _frozen(0.6602) if frozen is _ABSENT else frozen}
    paths = {k: _write(v) if v is not None else Path(f"runs/absent_{k}.json") for k, v in chosen.items()}
    return {row["id"]: row
            for row in e371.judge(e371.reading(played_path=paths["played"], empty_path=paths["empty"],
                                               frozen_path=paths["frozen"]))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("G1", "G2", "G3", "G4", "G5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # G1: the cue's step not moved, a shared field moved, the wrong coupling, fewer replicates, and the run this
    # unit pairs against absent
    assert _judge(played=_run(cue_step=10, diag=0.60))["G1"]["verdict"].startswith("FALSIFIER")
    assert _judge(played=_run(cue_step=0, basis="neuron", diag=0.60))["G1"]["verdict"].startswith("FALSIFIER")
    assert _judge(played=_run(cue_step=0, coupling="other", diag=0.60))["G1"]["verdict"].startswith("FALSIFIER")
    assert _judge(played=_run(cue_step=0, reps=5, diag=0.60))["G1"]["verdict"].startswith("FALSIFIER")
    assert _judge(empty=None)["G1"]["verdict"].startswith("REFUSED")

    # G2: a world at rest at the first step, and one whose floor is between the two bars
    assert _judge(frozen=_frozen(0.26))["G2"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_frozen(0.32))["G2"]["verdict"].startswith("NULL")
    assert _judge(frozen=None)["G2"]["verdict"].startswith("REFUSED")

    # G3: a game the body cannot learn, and one it learns too weakly to call
    assert _judge(played=_run(diag=0.26))["G3"]["verdict"].startswith("FALSIFIER")
    assert _judge(played=_run(diag=0.33))["G3"]["verdict"].startswith("NULL")

    # G4: an arm whose answer is not earned
    assert _judge(played=_run(channel=0.01))["G4"]["verdict"].startswith("FALSIFIER")
    assert _judge(played=_run(channel=0.30, replay_forget=0.09))["G4"]["verdict"].startswith("MET")

    # G5: a buffer that makes the game worse, and one whose effect is too small to call
    assert _judge(played=_run(replay_forget=0.60))["G5"]["verdict"].startswith("FALSIFIER")
    assert _judge(played=_run(replay_forget=0.36))["G5"]["verdict"].startswith("NULL")

    #: the first-step run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e371.judge(e371.reading(played_path=Path("runs/does_not_exist.json"),
                                                  empty_path=_write(_run(cue_step=10)),
                                                  frozen_path=_write(_frozen()))))


def test_the_frozen_cell_is_read_off_the_right_configuration():
    cell = e371.frozen_cell(_write(_frozen(0.6602, source="action", step=0)))
    assert cell and abs(cell["accuracy"] - 0.6602) < 1e-12 and abs(cell["world_sd"] - 0.2029) < 1e-12, cell
    #: the late step of the same source is the empty cell and not the licence, and the cue source is another source
    assert e371.frozen_cell(_write(_frozen(0.2578, source="action", step=10))) is None
    assert e371.frozen_cell(_write(_frozen(0.7891, source="cue", step=0))) is None
    assert e371.frozen_cell(Path("runs/does_not_exist.json")) is None


def test_the_live_reading_pairs_the_first_step_with_the_read_step():
    p = Path("runs/e371_the_game_the_agent_can_play.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e371.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["facts"]["played"]["loop_cue_at"] == e371.CUE_STEP, d["facts"]["played"]
    assert d["facts"]["empty"]["loop_cue_at"] == e371.EMPTY_STEP, d["facts"]["empty"]
    #: both runs are action-source, so the drive maps have the same width and the couplings agree
    assert d["facts"]["played"]["world_coupling_sha1"] == ACTION_COUPLING, d["facts"]["played"]
    assert d["facts"]["empty"]["world_coupling_sha1"] == ACTION_COUPLING, d["facts"]["empty"]
    for key in (f"played_{e371.NAIVE}", f"played_{e371.REPLAY}"):
        assert d["rows"][key]["n"] == e371.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
