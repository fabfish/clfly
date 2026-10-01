"""`e326` trains an arm whose gradient crosses its own output, so the tests pin the wrapper that wires the loop in
without editing any call site, the paired reading, the config comparison, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import scipy.sparse as sp

from clfly.network.env import ClosedLoop
from clfly.network.model import _make_module
from experiments import e326_training_through_the_loop as e326


def _tiny():
    import torch
    mask = sp.random(6, 6, density=0.4, random_state=0, format="csr")
    mask = (mask != 0).astype(float).tocsr()
    gen = np.random.default_rng(0)
    model = _make_module()(mask, gen.standard_normal(mask.nnz), 0.3, 5)
    u = torch.from_numpy(gen.standard_normal((3, 5, 6)).astype(np.float32))
    return model, u


def test_the_wrapper_passes_everything_but_the_call_through():
    import torch
    model, u = _tiny()
    fn = lambda x, t: 0.25 * x                                       # noqa: E731
    wrapped = ClosedLoop(model, fn)
    # the same forward call the runner makes at every site, with the loop closed behind it
    assert torch.allclose(wrapped(u, None), model(u, None, feedback=fn))
    assert not torch.allclose(wrapped(u, None), model(u, None)), "the loop has to change the trajectory"
    # the parameters and the training hooks are the module's own objects, not copies
    assert wrapped.theta is model.theta and wrapped.bias is model.bias, "an optimiser over these must see them"
    assert wrapped.recurrent() is not None
    wrapped.zero_grad()
    assert model.theta.grad is None
    # anything else falls through, and a missing attribute is still an AttributeError
    assert wrapped.mask_shape is model.mask_shape
    try:
        wrapped.no_such_attribute
        raise AssertionError("a missing attribute must raise rather than return something")
    except AttributeError:
        pass


def test_paired_is_a_replicate_wise_difference():
    p = e326.paired([0.8, 0.7, 0.9], [0.7, 0.6, 0.8])
    assert p["n"] == 3 and abs(p["delta"] - 0.1) < 1e-12, p
    assert e326.paired([0.8], [0.7])["delta"] is None, e326.paired([0.8], [0.7])


def test_the_config_diff_ignores_the_switch_and_the_output_path():
    a = {"config": {"circuit_size": 300, "json_out": "runs/a.json", "no_feedback": False, "seed0": 0}}
    b = {"config": {"circuit_size": 300, "json_out": "runs/b.json", "no_feedback": True, "seed0": 0}}
    assert e326.config_diff(a, b) == {}, e326.config_diff(a, b)
    b["config"]["loop_scale"] = 2.0
    assert set(e326.config_diff(a, b)) == {"loop_scale"}, e326.config_diff(a, b)


def _run(acc, forget, n=5, seed_off=0.0, name_prefix="loop_"):
    methods = {arm: {"final_accuracy": acc, "mean_forgetting": forget,
                     "replicates": [{"final_accuracy": acc + seed_off * i, "mean_forgetting": forget + 0.001 * i}
                                    for i in range(n)]}
               for arm in e326.ARMS}
    return {"config": {"circuit_size": 300}, "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"cue_sha1": "x", "scale": 1.0},
            "tasks": [{"name": name_prefix + s} for s in ("a", "b", "c")], "methods": methods}


def _reading(closed_acc=0.80, open_acc=0.90, closed_forget=0.10, open_forget=0.07,
             config_diff=None, same_readout=True, counts=True, same_tasks=True, same_env=True):
    return {"runs": 2, "circuits": ["MB", "MB"], "readout": ["abc", "abc" if same_readout else "zzz"],
            "n_replicates": {arm: [5, 5 if counts else 4] for arm in e326.ARMS},
            "config_diff": config_diff if config_diff is not None else {},
            "env_draw": [{"cue_sha1": "x", "scale": 1.0}] * 2 if same_env else
                        [{"cue_sha1": "x", "scale": 1.0}, {"cue_sha1": "y", "scale": 1.0}],
            "task_names": {"closed": ["loop_a", "loop_b", "loop_c"] if same_tasks
                           else ["loop_a", "loop_b", "loop_d"], "open": ["loop_a", "loop_b", "loop_c"]},
            "accuracy": {arm: {"n": 5, "delta": closed_acc - open_acc, "sem": 0.01, "sigma": 3.0}
                         for arm in e326.ARMS},
            "forgetting": {arm: {"n": 5, "delta": closed_forget - open_forget, "sem": 0.01, "sigma": 3.0}
                           for arm in e326.ARMS},
            "closed": {arm: {"final_accuracy": closed_acc, "mean_forgetting": closed_forget}
                       for arm in e326.ARMS},
            "open": {arm: {"final_accuracy": open_acc, "mean_forgetting": open_forget} for arm in e326.ARMS},
            "timing_s": [1.0, 1.0]}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e326.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: a differing config field, read-out draw, replicate count, task name or environment draw
    assert e326.judge(_reading(config_diff={"loop_scale": [1.0, 2.0]}))[0]["verdict"].startswith("FALSIFIER")
    assert e326.judge(_reading(same_readout=False))[0]["verdict"].startswith("FALSIFIER")
    assert e326.judge(_reading(counts=False))[0]["verdict"].startswith("FALSIFIER")
    assert e326.judge(_reading(same_tasks=False))[0]["verdict"].startswith("FALSIFIER")
    assert e326.judge(_reading(same_env=False))[0]["verdict"].startswith("FALSIFIER")

    # T2: a loop that does not train, and one that is merely weak
    assert e326.judge(_reading(closed_acc=0.52))[1]["verdict"].startswith("FALSIFIER")
    assert e326.judge(_reading(closed_acc=0.58))[1]["verdict"].startswith("NULL")
    # T3: the loop reading higher is the falsifier and within the band is the null
    assert e326.judge(_reading(closed_acc=0.96, open_acc=0.90))[2]["verdict"].startswith("FALSIFIER")
    assert e326.judge(_reading(closed_acc=0.88, open_acc=0.90))[2]["verdict"].startswith("NULL")
    # T4: forgetting less is the falsifier and within the band is the null
    assert e326.judge(_reading(closed_forget=0.04, open_forget=0.07))[3]["verdict"].startswith("FALSIFIER")
    assert e326.judge(_reading(closed_forget=0.075, open_forget=0.07))[3]["verdict"].startswith("NULL")

    # and a missing run refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e326.judge({"runs": 0, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_rather_than_reading_one_run(tmp_path):
    a = tmp_path / "a.json"
    a.write_text(json.dumps(_run(0.8, 0.1)), encoding="utf-8")
    r = e326.reading(a, tmp_path / "absent.json")
    assert r["runs"] == 0 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e326.judge(r))


def test_the_live_reading_is_one_configuration_in_two_loops():
    r = e326.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"]["closed"] == r["task_names"]["open"], r["task_names"]
    assert r["env_draw"][0] == r["env_draw"][1], r["env_draw"]
    assert not r["config_diff"], r["config_diff"]
    assert all(v[0] == v[1] == 5 for v in r["n_replicates"].values()), r["n_replicates"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e326_training_through_the_loop.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e326.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert not d["config_diff"], d["config_diff"]
