"""`e367` trains the closed loop whose world listens to the agent's own action, so the tests pin the three-run
configuration check, the frozen floor, the comparison with the hard-wired channel and both faces of the five claims.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from experiments import e367_the_world_the_agent_drives as e367

ACTION_COUPLING = e367.COUPLING_SHA1
CUE_COUPLING = "1b7d09f2b469"


def _run(cue_step=10, diag=0.90, reps=20, tasks=3, drive_from_cue=False, coupling=ACTION_COUPLING,
         drive_sha="aw", basis="cell_class", iters=500, channel=0.30, forget=0.35, replay_forget=0.09,
         world_dims=8, leak=0.35, modes=0, nonlinear=False):
    #: the source moves the action population and the three world draws that follow it in the environment's own
    #: draw, which is what `FOLLOWS_FROM_THE_SOURCE` registers -- a fixture that held them fixed would test a
    #: configuration the corpus cannot produce
    payload = {
        "config": {"loop_cue_at": cue_step, "loop_drive_from_cue": drive_from_cue, "loop_world_leak": leak,
                   "loop_world_coupled": True, "readout_from_world": True, "loop_world_dims": world_dims,
                   "loop_world_modes": modes, "loop_world_nonlinear": nonlinear, "closed_loop": True,
                   "repeats": reps, "circuit_size": 300, "readout_size": 32, "basis": basis, "seed0": 0,
                   "iters": iters},
        "env_draw": {"world_dims": world_dims, "world_drive_sha1": "cw" if drive_from_cue else drive_sha,
                     "world_read_sha1": "cr" if drive_from_cue else "r",
                     "world_leak": leak, "world_coupled": True, "world_coupling_sha1": coupling,
                     "world_nonlinear": nonlinear, "drive_from_cue": drive_from_cue, "cue_at": cue_step,
                     "cue_sha1": "c", "action_sha1": "c" if drive_from_cue else "a", "feedback_sha1": "f",
                     "n_cue": 12, "n_action": 12 if drive_from_cue else 8},
        "tasks": [{"name": f"loop_t{i}", "n_classes": 4, "n_readout": 8} for i in range(tasks)],
        "methods": {},
    }
    for arm in e367.ARMS:
        forget_arm = forget if arm == e367.NAIVE else replay_forget
        reps_list = []
        for r in range(reps):
            reps_list.append({
                "final_accuracy": diag, "mean_forgetting": forget_arm,
                "learned": [diag] * tasks, "forgetting_per_task": [forget_arm] * (tasks - 1),
                "final_per_task": [diag] * tasks,
                "retention": [[diag if i == j else None for j in range(tasks)] for i in range(tasks)],
                "paired_channel": [{"task": f"loop_t{j}", "with_loop": 0.5 + channel,
                                    "without_loop": 0.5} for j in range(tasks)]})
        payload["methods"][arm] = {"final_accuracy": diag, "final_sem": 0.01, "mean_forgetting": forget_arm,
                                   "forgetting_sem": 0.01, "learned": [diag] * tasks, "replicates": reps_list}
    return payload


def _frozen(accuracy=0.2578, source=e367.FROZEN_SOURCE, step=e367.FROZEN_STEP):
    return {"cells": [{"source": source, "cue_at": step, "accuracy": accuracy, "chance": 0.25},
                      {"source": source, "cue_at": e367.FROZEN_SAME_STEP, "accuracy": 0.6602, "chance": 0.25},
                      {"source": "cue", "cue_at": 10, "accuracy": 0.8555, "chance": 0.25}]}


def _write(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


#: `None` means "this artefact is absent" and the sentinel means "use the standard fixture"
_ABSENT = object()


def _judge(closed=_ABSENT, cue=_ABSENT, late=_ABSENT, frozen=_ABSENT):
    default_cue = _run(cue_step=10, diag=0.5337, drive_from_cue=True, coupling=CUE_COUPLING, drive_sha="cw")
    chosen = {"closed": _run(diag=0.40) if closed is _ABSENT else closed,
              "cue": default_cue if cue is _ABSENT else cue,
              "late": _run(cue_step=11, diag=0.2361) if late is _ABSENT else late,
              "frozen": _frozen(0.2578) if frozen is _ABSENT else frozen}
    paths = {k: _write(v) if v is not None else Path(f"runs/absent_{k}.json") for k, v in chosen.items()}
    return {row["id"]: row
            for row in e367.judge(e367.reading(closed_path=paths["closed"], cue_path=paths["cue"],
                                               late_path=paths["late"], frozen_path=paths["frozen"]))}


def test_the_five_claims_read_both_faces():
    j = _judge()
    for cid in ("T1", "T2", "T3", "T4", "T5"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: the cue's step not moved, a shared field moved, the action pair's coupling moved, the drive's draws
    # not following the source, and fewer replicates
    assert _judge(late=_run(cue_step=10, diag=0.2361))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(closed=_run(diag=0.80, basis="neuron"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(late=_run(cue_step=11, diag=0.2361, coupling=CUE_COUPLING))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(cue=_run(cue_step=10, diag=0.5337, drive_from_cue=True, coupling=ACTION_COUPLING,
                           drive_sha="aw"))["T1"]["verdict"].startswith("FALSIFIER")
    assert _judge(closed=_run(diag=0.80, reps=5))["T1"]["verdict"].startswith("FALSIFIER")
    #: and a comparison run that is absent refuses the check rather than passing it
    assert _judge(cue=None)["T1"]["verdict"].startswith("REFUSED")
    # T2: a cell the frozen probe could already read, and one whose floor is between the two bars
    assert _judge(frozen=_frozen(0.40))["T2"]["verdict"].startswith("FALSIFIER")
    assert _judge(frozen=_frozen(0.32))["T2"]["verdict"].startswith("NULL")
    # T3: a body that cannot build the channel, and one that builds it too weakly to call
    assert _judge(closed=_run(diag=0.26))["T3"]["verdict"].startswith("FALSIFIER")
    assert _judge(closed=_run(diag=0.33))["T3"]["verdict"].startswith("NULL")
    # T4: a closed loop that matches the hard-wired channel, and one whose cost is too small to call
    assert _judge(closed=_run(diag=0.53))["T4"]["verdict"].startswith("FALSIFIER")
    assert _judge(closed=_run(diag=0.50))["T4"]["verdict"].startswith("NULL")
    # T5: an arm whose answer is not earned
    assert _judge(closed=_run(diag=0.80, channel=0.01))["T5"]["verdict"].startswith("FALSIFIER")
    # the closed-loop run absent refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e367.judge(e367.reading(closed_path=Path("runs/does_not_exist.json"),
                                                  cue_path=_write(_run(drive_from_cue=True)),
                                                  late_path=_write(_run(cue_step=11)),
                                                  frozen_path=_write(_frozen()))))


def test_the_frozen_floor_is_read_off_the_right_cell():
    cell = e367.frozen_cell(_write(_frozen(0.2578, source="action", step=10)))
    assert cell and abs(cell["accuracy"] - 0.2578) < 1e-12, cell
    #: the same source at the first step is the eleven-step reference and not this cell, and the cue source there
    #: is a different configuration
    assert e367.frozen_cell(_write(_frozen(0.66, source="action", step=0))) is None
    assert e367.frozen_cell(_write(_frozen(0.8555, source="cue", step=10))) is None
    assert e367.frozen_cell(Path("runs/does_not_exist.json")) is None
    wider = e367.frozen_cell(_write(_frozen()), source="action", step=0)
    assert wider and abs(wider["accuracy"] - 0.6602) < 1e-12, wider


def test_the_live_reader_carries_the_same_reading():
    p = Path("runs/e367_the_world_the_agent_drives.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {row["id"]: row["verdict"] for row in e367.judge(d)} == {row["id"]: row["verdict"] for row in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the run landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["facts"]["closed"]["loop_cue_at"] == e367.CUE_STEP, d["facts"]
    assert d["facts"]["late"]["loop_cue_at"] == e367.LATE_STEP, d["facts"]
    assert d["facts"]["cue"]["loop_cue_at"] == e367.CUE_STEP, d["facts"]
    #: the closed loop and the read-step run share the action-source draw; the cue-source run is a different one
    assert d["facts"]["closed"]["world_coupling_sha1"] == ACTION_COUPLING, d["facts"]["closed"]
    assert d["facts"]["late"]["world_coupling_sha1"] == ACTION_COUPLING, d["facts"]["late"]
    assert d["facts"]["cue"]["world_coupling_sha1"] == CUE_COUPLING, d["facts"]["cue"]
    for key in (f"closed_{e367.NAIVE}", f"closed_{e367.REPLAY}"):
        assert d["rows"][key]["n"] == e367.REPLICATES, d["rows"][key]
    #: a reading is not a result, so the artifact carries no `config`, `env` or `tasks` for the corpus to count
    assert "config" not in d and "env" not in d and "tasks" not in d, sorted(d)
