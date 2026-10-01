"""`e333` gives the world a transition rule, so the tests pin the rule's endpoint, the trial's reset, the exact
ledger comparison the endpoint claim needs, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from clfly.network import env as fly_env
from experiments import e333_the_world_gets_a_rule as e333


class _Circ:
    n_neurons = 40


def _env(leak=1.0, modes=2):
    return fly_env.build(_Circ(), n_symbols=4, tau=8, n_cue=6, n_action=4, n_feedback=6,
                         seed=0, scale=1.0, world_modes=modes, world_leak=leak)


def _drive(e, fn, level=5.0, steps=6, batch=1):
    """Feed a constant action for ``steps`` steps and read the channel's magnitude at each."""
    out = []
    for t in range(steps):
        x = torch.zeros(batch, 40)
        if t > 0:
            x[:, e.action_neurons] = level
        out.append(float(torch.max(torch.abs(fn(x, t)))))
    return out


def test_the_rule_is_the_identity_at_leak_one():
    """`leak = 1` has to be `e332`'s instantaneous world and not merely close to it."""
    instant = _drive(_env(1.0), _env(1.0).feedback())
    assert instant[0] == 0.0, instant
    assert len(set(round(v, 6) for v in instant[1:])) == 1, instant
    # and below one the same drive accumulates towards the same limit
    carried = _drive(_env(0.35), _env(0.35).feedback())
    assert carried[0] == 0.0, carried
    assert all(carried[i] < carried[i + 1] for i in range(1, len(carried) - 1)), carried
    assert carried[-1] < instant[-1], (carried, instant)


def test_the_world_resets_with_the_trial():
    """A state carried across trials would be a different world, and it also breaks the backward pass."""
    e = _env(0.35)
    fn = e.feedback()
    first = _drive(e, fn)
    second = _drive(e, fn)
    assert first == second, (first, second)
    # a trial that opens on a nonzero state still shows nothing at step zero and starts from there
    e2 = _env(0.35)
    fn2 = e2.feedback()
    x = torch.zeros(1, 40)
    x[:, e2.action_neurons] = 5.0
    assert float(torch.max(torch.abs(fn2(x, 0)))) == 0.0
    after = float(torch.max(torch.abs(fn2(x, 1))))
    assert 0.0 < after < float(torch.max(torch.abs(fn2(x, 2)))), after


def test_the_leak_one_channel_is_the_blend_the_rule_defines():
    e = _env(1.0)
    fn = e.feedback()
    x = torch.zeros(1, 40)
    x[:, e.action_neurons] = 5.0
    fn(x, 0)                                   # the trial's first step resets the world
    shown = fn(x, 1).numpy()[0, e.feedback_neurons]
    action = float(np.tanh(e.gain * float(x[0, e.action_neurons].mean())))
    tpl = np.asarray(e.world_templates)
    half = (tpl[1] - tpl[0]) / 2.0
    expected = (((1 + action) / 2 - 0.5) * (tpl[1] - tpl[0]))
    #: the two sides are the same formula, differing only in the precision `self.action` evaluates it at
    assert np.allclose(shown, expected, atol=1e-3), (shown, expected)
    assert np.allclose(shown, half, atol=1e-3) or np.allclose(shown, -half, atol=1e-3), shown
    # and the draw records the leak
    assert e.summary()["world_leak"] == 1.0 and _env(0.35).summary()["world_leak"] == 0.35


def _run(acc, forget, n=5, leak=1.0):
    return {"config": {"circuit_size": 300, "json_out": "x", "loop_world_leak": leak, "loop_world_modes": 2},
            "circuit": "MB", "readout": {"subset_sha1": "abc"},
            "env_draw": {"world_leak": leak, "world_modes": 2, "noise": 1.0, "n_symbols": 24},
            "tasks": [{"name": n_} for n_ in ("loop_a", "loop_b", "loop_c")],
            "methods": {arm: {"final_accuracy": acc[arm], "mean_forgetting": forget[arm],
                              "replicates": [{"final_accuracy": acc[arm] + 0.001 * i,
                                              "mean_forgetting": forget[arm] + 0.001 * i}
                                             for i in range(n)]} for arm in e333.ARMS}}


def _write(payload):
    import tempfile
    fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, fh)
    fh.close()
    return Path(fh.name)


def _reading(carry_acc=None, carry_forget=None, leaks=(1.0, 0.35), counts=True, endpoint=None):
    acc = {"naive": 0.51, "replay": 0.62}
    ca = {"naive": 0.55, "replay": 0.63} if carry_acc is None else carry_acc
    cf = {"naive": 0.28, "replay": 0.05} if carry_forget is None else carry_forget
    forget = {"naive": 0.22, "replay": 0.05}
    a = _run(acc, forget, leak=leaks[0])
    b = _run(ca, cf, n=5 if counts else 4, leak=leaks[1])
    return e333.reading({"instant": _write(a), "carry": _write(b)}, endpoint=_write(endpoint or a))


def test_the_four_claims_read_both_faces(tmp_path):
    j = {row["id"]: row for row in e333.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1: the leaks have to be one and less than one, the counts equal, and nothing else may differ
    assert e333.judge(_reading(leaks=(0.5, 0.35)))[0]["verdict"].startswith("FALSIFIER")
    assert e333.judge(_reading(leaks=(1.0, 1.0)))[0]["verdict"].startswith("FALSIFIER")
    assert e333.judge(_reading(counts=False))[0]["verdict"].startswith("FALSIFIER")
    # T2 and T3: under the STILL bar fires, between is the null, and a large move is the MET
    assert e333.judge(_reading(carry_acc={"naive": 0.515, "replay": 0.62}))[1]["verdict"].startswith("FALSIFIER")
    assert e333.judge(_reading(carry_acc={"naive": 0.53, "replay": 0.62}))[1]["verdict"].startswith("NULL")
    assert e333.judge(_reading(carry_forget={"naive": 0.225, "replay": 0.05}))[2]["verdict"].startswith("FALSIFIER")
    assert e333.judge(_reading(carry_forget={"naive": 0.24, "replay": 0.05}))[2]["verdict"].startswith("NULL")
    # T4: the endpoint has to be that world's own numbers
    moved = _reading()
    moved["endpoint"] = {"naive": {"identical": False, "n_instant": 5, "n_endpoint": 5}}
    assert e333.judge(moved)[3]["verdict"].startswith("FALSIFIER")
    assert e333.judge(_reading())[3]["verdict"].startswith("MET")
    # and no endpoint at all refuses the claim rather than passing it
    r = _reading()
    r["endpoint"] = None
    assert e333.judge(r)[3]["verdict"].startswith("REFUSED")

    # one run alone refuses every claim
    assert all(row["verdict"].startswith("REFUSED")
               for row in e333.judge({"runs": 1, "missing": ["runs/b.json"]}))


def test_the_reader_refuses_when_one_run_is_missing(tmp_path):
    a = _write(_run({"naive": 0.51, "replay": 0.62}, {"naive": 0.22, "replay": 0.05}))
    r = e333.reading({"instant": a, "carry": tmp_path / "absent.json"}, endpoint=a)
    assert r["runs"] == 1 and r["missing"], r
    assert all(row["verdict"].startswith("REFUSED") for row in e333.judge(r))


def test_the_live_pair_is_one_configuration_at_two_leaks():
    r = e333.reading()
    if not r.get("runs"):
        return                      # the artifacts are written by the runs this unit reads
    assert r["circuits"][0] == r["circuits"][1], r["circuits"]
    assert r["readout"][0] == r["readout"][1], r["readout"]
    assert r["task_names"][0] == r["task_names"][1], r["task_names"]
    assert not r["config_diff"] and not r["env_diff"], (r["config_diff"], r["env_diff"])
    assert r["leaks"] == [1.0, 0.35], r["leaks"]
    assert all(v == [5, 5] for v in r["n_replicates"].values()), r["n_replicates"]


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e333_the_world_gets_a_rule.json")
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e333.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    if d["claims"][0]["verdict"].startswith("REFUSED"):
        return                      # written before the two runs landed; the gate regenerates it
    assert d["claims"][0]["verdict"].startswith("MET"), d["claims"][0]
    assert d["leaks"] == [1.0, 0.35], d["leaks"]
