"""`e329` gives the environment a noisy cue and eight symbols, so the tests pin the noise's default-off
reproducibility, the paired contrasts, the config comparison, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from clfly.network import env as fly_env
from experiments import e329_the_environment_gets_a_noisy_cue as e329


class _Circ:
    n_neurons = 40


def _env(noise=0.0, n_symbols=8, tau=6):
    return fly_env.build(_Circ(), n_symbols=n_symbols, tau=tau, n_cue=6, n_action=4, n_feedback=6,
                         seed=0, noise=noise)


def test_a_noiseless_cue_is_still_bit_identical():
    """The field's default has to leave every earlier artifact's path untouched."""
    e = _env(noise=0.0)
    a = e.cue_input(np.array([0, 3, 7]))
    b = e.cue_input(np.array([0, 3, 7]), np.random.default_rng(99))
    assert np.array_equal(a, b), "with no noise the rng is never consulted"
    assert np.any(a[:, 0, e.cue_neurons]), a[:, 0]
    assert np.all(a[:, 1:] == 0.0), "and the cue is still a single-step pulse"
    assert e.summary()["noise"] == 0.0


def test_a_noisy_cue_moves_with_its_rng_and_only_at_step_zero():
    e = _env(noise=1.0)
    y = np.array([0, 3, 7])
    a = e.cue_input(y, np.random.default_rng(1))
    b = e.cue_input(y, np.random.default_rng(2))
    c = e.cue_input(y, np.random.default_rng(1))
    assert np.array_equal(a, c), "the same rng gives the same cue"
    assert not np.allclose(a, b), "a different rng gives a different one"
    assert np.all(a[:, 1:] == 0.0), "and noise is drawn at step 0 only"
    # the two splits of one task are drawn from the same stream, so they are not the same examples
    rng = np.random.default_rng(5)
    first, second = e.cue_input(y, rng), e.cue_input(y, rng)
    assert not np.allclose(first[:, 0], second[:, 0]), "consecutive draws differ"
    assert e.summary()["noise"] == 1.0


def test_the_task_carries_the_noise_into_both_splits():
    e = _env(noise=1.0)
    task = fly_env.make_env_task(e, "loop_x", symbols=range(4), n_train=8, n_test=8,
                                 readout_neurons=np.arange(4), seed=0)
    assert task.u_train.shape == (8, 6, 40) and task.u_test.shape == (8, 6, 40), task.u_train.shape
    assert not np.array_equal(task.u_train[:, 0], task.u_test[:, 0]), "the splits are independent draws"
    assert np.all(task.u_train[:, 1:] == 0.0)
    # and a noiseless environment gives the noise-free task
    quiet = fly_env.make_env_task(_env(noise=0.0), "loop_x", symbols=range(4), n_train=8, n_test=8,
                                  readout_neurons=np.arange(4), seed=0)
    assert np.all(quiet.u_train[:, 1:] == 0.0)


def _run(acc, forget, n=5, scale=0.0):
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_scale": scale, "loop_noise": 1.0,
                       "loop_symbols": 8},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"scale": scale, "noise": 1.0, "n_symbols": 24, "n_cue": 12},
            "tasks": [{"name": n_} for n_ in ("loop_a", "loop_b", "loop_c")],
            "methods": {arm: {"final_accuracy": acc, "mean_forgetting": forget,
                              "replicates": [{"final_accuracy": acc, "mean_forgetting": forget}
                                             for _ in range(n)]} for arm in e329.ARMS}}


def _reading(open_acc=0.80, mid_acc=0.70, open_forget=0.10, mid_forget=0.20,
             config_diff=None, env_diff=None, same_tasks=True, counts=True):
    return {"runs": 2, "levels": ["0p00", "0p50"], "scales": [0.0, 0.5],
            "circuits": ["MB", "MB"] if same_tasks else ["MB", "MB2"],
            "readout": ["abc", "abc"],
            "task_names": [["loop_a"] if same_tasks else ["loop_z"], ["loop_a"]],
            "config_diff": config_diff or {}, "env_diff": env_diff or {},
            "env": {"noise": 1.0, "n_symbols": 24},
            "n_replicates": {arm: [5, 5 if counts else 4] for arm in e329.ARMS},
            "accuracy": {arm: {"n": 5, "delta": mid_acc - open_acc, "sem": 0.02, "sigma": 3.0}
                         for arm in e329.ARMS},
            "forgetting": {arm: {"n": 5, "delta": mid_forget - open_forget, "sem": 0.02, "sigma": 3.0}
                           for arm in e329.ARMS},
            "open": {arm: {"final_accuracy": open_acc, "mean_forgetting": open_forget} for arm in e329.ARMS},
            "mid": {arm: {"final_accuracy": mid_acc, "mean_forgetting": mid_forget} for arm in e329.ARMS},
            "timing_s": [1.0, 1.0]}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e329.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a differing circuit, task name, replicate count, config or environment field
    assert e329.judge(_reading(same_tasks=False))[0]["verdict"].startswith("FALSIFIER")
    assert e329.judge(_reading(counts=False))[0]["verdict"].startswith("FALSIFIER")
    assert e329.judge(_reading(config_diff={"loop_noise": [1.0, 0.0]}))[0]["verdict"].startswith("FALSIFIER")
    assert e329.judge(_reading(env_diff={"noise": [1.0, 0.0]}))[0]["verdict"].startswith("FALSIFIER")
    # T2: still at the ceiling is the falsifier and a near-ceiling reading is the null
    assert e329.judge(_reading(open_acc=0.995))[1]["verdict"].startswith("FALSIFIER")
    assert e329.judge(_reading(open_acc=0.97))[1]["verdict"].startswith("NULL")
    # T3: a rounding artefact is the falsifier and a small loss is the null
    assert e329.judge(_reading(mid_forget=0.01))[2]["verdict"].startswith("FALSIFIER")
    assert e329.judge(_reading(mid_forget=0.05))[2]["verdict"].startswith("NULL")
    # T4: reading higher at the middling setting is the falsifier and a small move is the null
    assert e329.judge(_reading(mid_acc=0.90))[3]["verdict"].startswith("FALSIFIER")
    assert e329.judge(_reading(mid_acc=0.78))[3]["verdict"].startswith("NULL")

    # and one run alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e329.judge({"runs": 1, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_when_one_run_is_missing(tmp_path):
    a = tmp_path / "a.json"
    a.write_text(json.dumps(_run(0.8, 0.1)), encoding="utf-8")
    r = e329.reading({"0p00": a, "0p50": tmp_path / "absent.json"})
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e329.judge(r))


def test_the_live_pair_is_one_configuration_at_two_strengths():
    r = e329.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"][0] == r["task_names"][1], r["task_names"]
    assert not r["config_diff"] and not r["env_diff"], (r["config_diff"], r["env_diff"])
    assert r["scales"] == [0.0, 0.5], r["scales"]
    # the environment is the one this unit is about: eight symbols a task, and a noisy cue
    assert r["env"]["noise"] == 1.0 and r["env"]["n_symbols"] == 24, r["env"]
    assert all(v == [5, 5] for v in r["n_replicates"].values()), r["n_replicates"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e329_the_environment_gets_a_noisy_cue.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e329.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["env"]["noise"] == 1.0, d["env"]
