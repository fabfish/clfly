"""`e332` gives the world a state the agent's action selects, so the tests pin the two response kinds in the
environment itself, the paired reading, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from clfly.network import env as fly_env
from experiments import e332_the_world_answers_with_a_state as e332


class _Circ:
    n_neurons = 40


def _env(world_modes=0, scale=1.0, gain=1.0):
    return fly_env.build(_Circ(), n_symbols=4, tau=6, n_cue=6, n_action=4, n_feedback=6,
                         seed=0, scale=scale, gain=gain, world_modes=world_modes)


def test_the_report_channel_is_unchanged_and_recorded_as_zero_states():
    e = _env(world_modes=0)
    fn = e.feedback()
    x = torch.zeros(2, 40)
    x[:, e.action_neurons] = 3.0
    out = fn(x, 1)
    touched = set(np.flatnonzero(out.numpy()[0] != 0).tolist())
    assert touched and touched <= set(e.feedback_neurons.tolist()), touched
    # a scalar report: every feedback neuron carries the same number
    values = out.numpy()[0, e.feedback_neurons]
    assert np.allclose(values, values[0]), values
    assert e.summary()["world_modes"] == 0 and e.summary()["world_sha1"] is None


def test_the_state_channel_carries_a_pattern_the_action_selects():
    e = _env(world_modes=2)
    fn = e.feedback()
    x = torch.zeros(2, 40)
    x[0, e.action_neurons] = 30.0          # a saturated action picks one state
    x[1, e.action_neurons] = -30.0         # and the other picks the other
    out = fn(x, 1).numpy()
    a = out[0, e.feedback_neurons]
    b = out[1, e.feedback_neurons]
    assert not np.allclose(a, b), "the two states have to differ"
    assert not np.allclose(a, a[0]), "and a state is a pattern, not a scalar"
    # at saturation each is the difference between the two states, halved about their midpoint, so the two
    # saturated actions give exact negatives and a neutral one gives nothing
    tpl = np.asarray(e.world_templates)
    half = (tpl[1] - tpl[0]) / 2.0
    assert np.allclose(a, half, atol=1e-4) or np.allclose(a, -half, atol=1e-4), a
    assert np.allclose(b, -a, atol=1e-4), (a, b)
    # and the draw records the patterns and the count
    s = e.summary()
    assert s["world_modes"] == 2 and s["world_sha1"], s


def test_the_state_channel_is_still_zero_at_step_zero_and_off_a_zero_state():
    e = _env(world_modes=2)
    fn = e.feedback()
    x = torch.zeros(1, 40)
    assert float(torch.max(torch.abs(fn(x, 0)))) == 0.0, "the cue's step stands alone"
    assert float(torch.max(torch.abs(fn(x, 1)))) == 0.0, "and a zero state has no action"


def _run(acc, forget, n=5, modes=0):
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_world_modes": modes, "loop_noise": 1.0},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"world_modes": modes, "world_sha1": ("w" if modes else None), "noise": 1.0,
                         "n_symbols": 24},
            "tasks": [{"name": n_} for n_ in ("loop_a", "loop_b", "loop_c")],
            "methods": {arm: {"final_accuracy": acc[arm], "mean_forgetting": forget[arm],
                              "replicates": [{"final_accuracy": acc[arm] + 0.001 * i,
                                              "mean_forgetting": forget[arm] + 0.001 * i}
                                             for i in range(n)]} for arm in e332.ARMS}}


def _reading(state_acc=None, report_acc=None, state_forget=None, report_forget=None,
             config_diff=None, env_diff=None, counts=True, modes=(0, 2)):
    ra = {"naive": 0.51, "replay": 0.64} if report_acc is None else report_acc
    sa = {"naive": 0.55, "replay": 0.65} if state_acc is None else state_acc
    rf = {"naive": 0.22, "replay": 0.04} if report_forget is None else report_forget
    sf = {"naive": 0.25, "replay": 0.05} if state_forget is None else state_forget
    a, b = _run(ra, rf, modes=modes[0]), _run(sa, sf, n=5 if counts else 4, modes=modes[1])
    return e332.reading({"report": _write(a), "state": _write(b)})


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def test_the_four_claims_read_both_faces(tmp_path):
    j = {row["id"]: row for row in e332.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: the world has to be zero states on one side and more than one on the other
    assert e332.judge(_reading(modes=(2, 2)))[0]["verdict"].startswith("FALSIFIER")
    assert e332.judge(_reading(modes=(0, 0)))[0]["verdict"].startswith("FALSIFIER")
    assert e332.judge(_reading(counts=False))[0]["verdict"].startswith("FALSIFIER")
    r = _reading()
    r["circuits"] = ["MB", "MB2"]
    assert e332.judge(r)[0]["verdict"].startswith("FALSIFIER")
    # T2 and T3: a move under the STILL bar fires, one between is the null, and a large one is the MET
    assert e332.judge(_reading(state_acc={"naive": 0.515, "replay": 0.64}))[1]["verdict"].startswith("FALSIFIER")
    assert e332.judge(_reading(state_acc={"naive": 0.53, "replay": 0.64}))[1]["verdict"].startswith("NULL")
    assert e332.judge(_reading(state_forget={"naive": 0.225, "replay": 0.04}))[2]["verdict"].startswith("FALSIFIER")
    assert e332.judge(_reading(state_forget={"naive": 0.24, "replay": 0.04}))[2]["verdict"].startswith("NULL")
    # T4: a gap below the falsifier, between, and above the bar
    assert e332.judge(_reading(state_forget={"naive": 0.07, "replay": 0.04}))[3]["verdict"].startswith("FALSIFIER")
    assert e332.judge(_reading(state_forget={"naive": 0.12, "replay": 0.04}))[3]["verdict"].startswith("NULL")
    assert e332.judge(_reading(state_forget={"naive": 0.25, "replay": 0.04}))[3]["verdict"].startswith("MET")

    # and one run alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e332.judge({"runs": 1, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_when_one_run_is_missing(tmp_path):
    a = _write(_run({"naive": 0.51, "replay": 0.64}, {"naive": 0.22, "replay": 0.04}))
    r = e332.reading({"report": a, "state": tmp_path / "absent.json"})
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e332.judge(r))


def test_the_live_pair_is_one_configuration_in_two_worlds():
    r = e332.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"][0] == r["task_names"][1], r["task_names"]
    assert not r["config_diff"] and not r["env_diff"], (r["config_diff"], r["env_diff"])
    assert r["world_modes"] == [0, 2], r["world_modes"]
    assert all(v == [5, 5] for v in r["n_replicates"].values()), r["n_replicates"]
    assert r["env"]["noise"] == 1.0 and r["env"]["n_symbols"] == 24, r["env"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e332_the_world_answers_with_a_state.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e332.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["world_modes"] == [0, 2], d["world_modes"]
