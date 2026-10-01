"""`e325` closes the loop, so the tests pin the environment's contract, the forward-pass hook's guarantee that
`feedback=None` changes nothing, and both faces of the four claims.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from clfly.network import env as fly_env
from clfly.network.model import _make_module
from experiments import e325_the_loop_closes as e325


class _Circ:
    n_neurons = 40


def _env(seed=0, n_symbols=2, tau=6):
    return fly_env.build(_Circ(), n_symbols=n_symbols, tau=tau, n_cue=5, n_action=4, n_feedback=5, seed=seed)


def test_the_environment_is_disjoint_and_shows_the_cue_only_once():
    e = _env()
    sets = [set(e.cue_neurons.tolist()), set(e.action_neurons.tolist()), set(e.feedback_neurons.tolist())]
    assert not (sets[0] & sets[1]) and not (sets[0] & sets[2]) and not (sets[1] & sets[2]), sets
    u = e.cue_input(np.array([0, 1, 0]))
    assert u.shape == (3, 6, 40), u.shape
    # the cue is at step 0 and **nothing** after it -- the zeros are what make the loop load-bearing
    assert np.any(u[:, 0, e.cue_neurons]), u[:, 0]
    assert np.all(u[:, 1:] == 0.0), np.max(np.abs(u[:, 1:]))
    assert np.any(u[0, 0, e.cue_neurons] != u[1, 0, e.cue_neurons]), "the two symbols differ"


def test_the_feedback_is_zero_at_step_zero_and_moves_with_the_state():
    import torch
    e = _env()
    fn = e.feedback()
    x0 = torch.zeros(3, 40)
    assert float(torch.max(torch.abs(fn(x0, 0)))) == 0.0, "the cue's step stands alone"
    assert float(torch.max(torch.abs(fn(x0, 1)))) == 0.0, "and a zero state has no action"
    x = torch.zeros(3, 40)
    x[:, e.action_neurons] = 2.0
    out = fn(x, 1)
    assert float(torch.max(torch.abs(out))) > 0, out
    # the action lands on the feedback neurons and on nothing else
    touched = set(np.flatnonzero(out.numpy()[0] != 0).tolist())
    assert touched and touched <= set(e.feedback_neurons.tolist()), touched
    # and it is bounded by the scale, since the action is a tanh
    assert float(torch.max(torch.abs(out))) <= e.scale + 1e-6, float(torch.max(torch.abs(out)))


def test_the_hook_leaves_the_open_loop_unchanged():
    """`feedback=None` has to be bit-identical: every artifact in this repository was written through that path."""
    import torch
    import scipy.sparse as sp
    mask = sp.random(6, 6, density=0.4, random_state=0, format="csr")
    mask = (mask != 0).astype(float).tocsr()
    gen = np.random.default_rng(0)
    model = _make_module()(mask, gen.standard_normal(mask.nnz), 0.3, 5)
    u = torch.from_numpy(gen.standard_normal((4, 5, 6)).astype(np.float32))
    a = model(u)
    b = model(u, feedback=None)
    assert torch.equal(a, b), (float(torch.max(torch.abs(a - b))))
    # and a feedback that is identically zero is the same computation too
    c = model(u, feedback=lambda x, t: torch.zeros_like(x))
    assert torch.allclose(a, c, atol=0.0), float(torch.max(torch.abs(a - c)))
    # while a real one is not
    d = model(u, feedback=lambda x, t: 0.5 * x)
    assert not torch.allclose(a, d), "a non-zero feedback must move the trajectory"


def _config(size, fb=0.5, div=0.5, closed=1.0, open_=1.0, readout_div=0.1, peak=1.0):
    return {"circuit": "MB", "size": size, "peak_state": peak, "feedback_max": fb,
            "divergence": div, "divergence_of_peak": div / peak,
            "readout_divergence": readout_div, "readout_divergence_of_peak": readout_div / peak,
            "cue_probe_open": [0.5] * 11 + [open_], "cue_probe_closed": [0.5] * 11 + [closed],
            "env": {"n_cue": 1, "n_action": 1, "n_feedback": 1, "scale": 1.0, "gain": 1.0}}


def _reading(**kw):
    return {"configs": [_config(300, **kw), _config(800, **kw)]}


def test_the_four_claims_read_both_faces():
    j = {row["id"]: row for row in e325.judge(_reading())}
    for cid in ("T1", "T2", "T3", "T4"):
        assert j[cid]["verdict"].startswith("MET"), j[cid]

    # T1's falsifier is a feedback term that is exactly zero everywhere
    assert e325.judge(_reading(fb=0.0))[0]["verdict"].startswith("FALSIFIER FIRED")
    # T2: below the falsifier is decorative, and between the two is the registered null
    assert e325.judge(_reading(div=1e-5))[1]["verdict"].startswith("FALSIFIER FIRED")
    assert e325.judge(_reading(div=0.005))[1]["verdict"].startswith("NULL")
    # T3: a cue that reads at chance under the loop, and one that is merely weak
    assert e325.judge(_reading(closed=0.52))[2]["verdict"].startswith("FALSIFIER FIRED")
    assert e325.judge(_reading(closed=0.58))[2]["verdict"].startswith("NULL")
    # T4 is a share of the peak, so its two bars are on the same axis as T2's
    assert e325.judge(_reading(readout_div=1e-5))[3]["verdict"].startswith("FALSIFIER FIRED")
    assert e325.judge(_reading(readout_div=0.005))[3]["verdict"].startswith("NULL")

    # and nothing measured refuses every claim
    assert all(row["verdict"].startswith("REFUSED") for row in e325.judge({"configs": []}))
    # a run without a read-out subset refuses T4 alone rather than inventing a share
    r = _reading()
    for c in r["configs"]:
        c.pop("readout_divergence_of_peak")
    assert e325.judge(r)[3]["verdict"].startswith("REFUSED"), e325.judge(r)[3]
    assert e325.judge(r)[0]["verdict"].startswith("MET")


def test_the_live_artifact_carries_the_same_reading():
    p = Path("runs/e325_the_loop_closes.json")
    if not p.exists():
        return                      # the artifact is written by the run this unit reads
    d = json.loads(p.read_text(encoding="utf-8"))
    assert {r["id"]: r["verdict"] for r in e325.judge(d)} == {r["id"]: r["verdict"] for r in d["claims"]}
    for row in d["claims"]:
        assert row["verdict"].startswith("MET"), row
    # the cue is read at its ceiling in both loops, which is why T4 is a divergence and not an accuracy margin
    for v in d["configs"]:
        assert v["cue_probe_open"][-1] == 1.0 and v["cue_probe_closed"][-1] == 1.0, v["cue_probe_closed"][-1]
        # and the loop's share of the read-out is smaller than its share of the whole state
        assert 0 < v["readout_divergence_of_peak"] < v["divergence_of_peak"], v
