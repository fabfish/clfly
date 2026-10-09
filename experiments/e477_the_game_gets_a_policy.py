"""E477 -- the game gets a policy: a trainable map from the agent's action population to the world's drive.

`e325` built the closed loop, measured its gradient path and closed on the sentence every later unit of that line
has repeated: *"What is missing is the thing that makes it a game rather than a loop: **a reward and a policy**.
Nothing here trains on the loop, so all four claims are the frozen substrate's behaviour."* `e361` said the same from
the world's side -- *"nothing here trains a policy -- the task is still hold the cue and not act on the world"* -- and
the card still carries **a reward** and **a policy** in its `absent` list.

**The environment now carries a policy.** A new field on `CueActionEnv`, `policy`, replaces the world's drive
`tanh(gain * x[:, action_neurons])` with `tanh(gain * (x[:, action_neurons] @ policy))` when it is set, and `None` is
every artifact this repository holds -- so **`policy = I` is the corpus's own rule exactly**, which is where this unit
initializes. This unit gives the loop a **reward** (the world's final state is driven to a **cue-dependent target**),
initializes the policy at the identity and trains it by gradient ascent **through the loop**. Four claims, registered
before any policy was trained.

- **QA1 -- and the policy's identity is the environment's own rule, bit for bit.** On every replicate the world's
  final state computed with `policy = I` is **bit-identical** to the one the environment computes with no policy at
  all, so the trained game starts from the loop the corpus already runs and not from a second rule. **Falsifier**: any
  replicate whose two worlds differ.
- **QA2 -- and the reward's gradient is the loop's.** Over the replicates and every one of the policy's `64`
  coordinates, the gradient of the reward with respect to the policy, taken by backprop, agrees with a **central
  finite difference** at `eps = 1e-3` to within **5e-3** absolute, and the gradient at the identity policy is not the
  zero vector. **Falsifier**: any coordinate disagreeing by more than the tolerance, or a gradient whose norm is zero.
- **QA3 -- and the game can be played.** Over the replicates, the trained policy's mean reward on cues it was not
  trained on exceeds the initial policy's by at least **0.50**, paired, at **two** sigma or more. **Falsifier**: a
  gain below **0.20**, or one that does not resolve. **Null**: between.
- **QA4 -- and acting pays the read-out.** The cue is decodable from the world's final state under the trained policy
  at least **0.05** above the same decoder under the initial policy. **Falsifier**: the trained policy **0.02 or more
  below** the initial one, which would say the game's own objective costs the benchmark's. **Null**: between.

**What it can do beyond that.** It is the first unit in this corpus in which an agent is optimized toward something,
and it is the policy half of the sentence `e325` and `e361` both closed on: the reward is the target the world is
driven to, the policy is what drives it, and the thing that carries the gradient is the environment's own loop.

**What it cannot do.** *One target rule*: the reward is a squared distance to a cue-dependent point drawn from a
fixed seed, and a different reward -- sparse, saturating, or on the action rather than the state -- is not in it.
*And the policy is linear over one population*: `64` numbers from the action population to the world's drive, with the
body frozen, so nothing here trains the recurrent weights or a nonlinear policy. *And the policy is not the
benchmark's*: the runner does not carry one, so the card's `absent` list still names **a policy** and this unit does
not revise it. *And eight replicates are not the population*: the sigma is the paired one over the seeds the two
policies share. *And a reward is not a task*: reaching a drawn point is not the olfaction, heading and antennal-lobe
tasks the card's sequence is built from.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from experiments.e322_the_benchmark_has_no_time_in_it import probe

#: the card's own substrate and world: circuit 300 from the mushroom body, central complex and antennal lobe, a
#: 32-neuron read-out draw, four symbols at twelve steps, and the environment's eight-dimensional coupled world
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_SYMBOLS = 4
N_TRAIN = 512
N_HELD = 256
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_DIMS = 8
#: the policy is trained on one split and its reward read on another, so the gain is not the fitting
REPLICATES = (0, 1, 2, 3, 4, 5, 6, 7)
STEPS = 300
LR = 0.05
#: the reward's targets, drawn once per replicate from the environment's seed with this offset
TARGET_OFFSET = 101
#: the finite-difference step, the agreement the gradient must hold to, and the two bars
EPS = 1e-3
FTOL = 5e-3
SIGMA = 2.0
GAIN_BAR = 0.50
GAIN_FLOOR = 0.20
READ_BAR = 0.05
READ_FLOOR = -0.02
CLAIMS = (
    ("QA1", "and the policy's identity is the environment's own rule, bit for bit",
     "On every replicate the world's final state computed with policy = I is bit-identical to the one the "
     "environment computes with no policy at all",
     "falsifier: any replicate whose two worlds differ"),
    ("QA2", f"and the reward's gradient is the loop's, to {FTOL:g}",
     "Over the replicates and every one of the policy's 64 coordinates, the reward's backprop gradient agrees with a "
     "central finite difference at eps = 1e-3 to within 5e-3 absolute, and the gradient at the identity policy is not "
     "the zero vector",
     "falsifier: any coordinate disagreeing by more than the tolerance, or a gradient whose norm is zero"),
    ("QA3", f"and the game can be played, by {GAIN_BAR:.2f} at {SIGMA:.0f} sigma",
     "Over the replicates the trained policy's mean reward on cues it was not trained on exceeds the initial policy's "
     "by at least 0.50, paired, at two sigma or more",
     f"falsifier: a gain below {GAIN_FLOOR:.2f}, or one that does not resolve"),
    ("QA4", f"and acting pays the read-out, by {READ_BAR:.2f}",
     "The cue is decodable from the world's final state under the trained policy at least 0.05 above the same decoder "
     "under the initial policy",
     f"falsifier: the trained policy {abs(READ_FLOOR):.2f} or more below the initial one"),
)


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def one_replicate(circ, net, seed: int) -> dict:
    """One replicate: the world at this seed, the identity policy against a trained one, and the gradient's check.

    The body and the circuit are held across the replicates; the **world** is the replicate, so each one has its own
    cue populations, its own drive and read maps and its own coupling, and its own pair of targets.
    """
    import torch
    from clfly.network import env as fly_env

    dims = WORLD_DIMS
    e = fly_env.build(circ, readout_subset=np.sort(np.random.default_rng(SEED).choice(
        circ.n_neurons, size=READOUT_SIZE, replace=False)), seed=seed, n_symbols=N_SYMBOLS, tau=TAU,
        scale=SCALE, gain=GAIN, noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=dims,
        world_coupled=True, cue_at=0)
    n_act = len(e.action_neurons)
    rng = np.random.default_rng(seed + 7)
    y_all = rng.integers(0, N_SYMBOLS, size=N_TRAIN + N_HELD)
    y_tr, y_te = y_all[:N_TRAIN], y_all[N_TRAIN:]
    u_tr = e.cue_input(y_tr, np.random.default_rng(seed + 31))
    u_te = e.cue_input(y_te, np.random.default_rng(seed + 61))
    targets = torch.as_tensor(np.random.default_rng(seed + TARGET_OFFSET).standard_normal((N_SYMBOLS, dims)),
                              dtype=torch.float32)
    tr_tr = torch.from_numpy(np.asarray(u_tr, dtype=np.float32))
    tr_te = torch.from_numpy(np.asarray(u_te, dtype=np.float32))
    tgt_tr, tgt_te = targets[torch.as_tensor(y_tr)], targets[torch.as_tensor(y_te)]

    def world_of(policy, u_batch, grad: bool = False):
        e.policy = None if policy is None else policy
        fn = e.feedback()
        if grad:
            net(u_batch, feedback=fn)
        else:
            #: every pass that is not the gradient or the training step runs without a graph, so the finite
            #: differences and the readings cost memory and time and not autograd
            with torch.no_grad():
                net(u_batch, feedback=fn)
        return fn.last_world

    def reward_of(policy, u_batch, tgt, grad: bool = False):
        w = world_of(policy, u_batch, grad)
        return -((w - tgt) ** 2).sum(dim=1).mean(), w

    #: QA1 -- the identity policy against no policy at all, on the same cues
    eye = torch.eye(n_act, dtype=torch.float32)
    w_none = world_of(None, tr_te)
    w_eye = world_of(eye, tr_te)
    identity_bitwise = bool(torch.equal(w_none, w_eye))

    #: QA2 -- the reward's gradient at the identity, against a central finite difference on every coordinate
    eye_p = torch.nn.Parameter(eye.clone())
    reward_eye, _ = reward_of(eye_p, tr_tr, tgt_tr, grad=True)
    grad, = torch.autograd.grad(reward_eye, eye_p)
    worst, worst_at = 0.0, None
    for i in range(n_act):
        for j in range(n_act):
            up = eye_p.detach().clone(); up[i, j] += EPS
            dn = eye_p.detach().clone(); dn[i, j] -= EPS
            fd = (float(reward_of(up, tr_tr, tgt_tr)[0].detach()) - float(reward_of(dn, tr_tr, tgt_tr)[0].detach())) \
                / (2 * EPS)
            gap = abs(float(grad[i, j]) - fd)
            if gap > worst:
                worst, worst_at = gap, [i, j]

    init_reward, _ = reward_of(eye, tr_te, tgt_te)
    init_world = world_of(eye, tr_te)

    #: the policy is trained on the training cues and read on the held-out ones
    pol = torch.nn.Parameter(eye.clone())
    opt = torch.optim.Adam([pol], lr=LR)
    for _ in range(STEPS):
        opt.zero_grad()
        r, _ = reward_of(pol, tr_tr, tgt_tr, grad=True)
        (-r).backward()
        opt.step()
    trained_reward, trained_world = reward_of(pol.detach(), tr_te, tgt_te)
    #: the decoder is fitted on one half of the held-out cues and read on the other, and both policies get the
    #: same split, so the two readings differ in the policy and in nothing else
    half = N_HELD // 2
    trained_read = probe(trained_world[:, None, :].detach().numpy()[:half], y_te[:half],
                         trained_world[:, None, :].detach().numpy()[half:], y_te[half:], list(range(dims)))[-1]
    init_read = probe(init_world[:, None, :].detach().numpy()[:half], y_te[:half],
                      init_world[:, None, :].detach().numpy()[half:], y_te[half:], list(range(dims)))[-1]

    move = pol.detach() - eye
    return {"seed": int(seed), "n_act": n_act,
            "identity_bitwise": identity_bitwise,
            "identity_max_abs": float((w_none - w_eye).abs().max()),
            "grad_norm": float(grad.norm()), "fd_worst_abs": worst, "fd_worst_at": worst_at,
            "init_reward": float(init_reward.detach()), "trained_reward": float(trained_reward.detach()),
            "init_read": float(init_read), "trained_read": float(trained_read),
            "policy_move": float(move.norm()),
            "world_sd_init": float(init_world.std()), "world_sd_trained": float(trained_world.std()),
            "target_sha1": _fingerprint(np.random.default_rng(seed + TARGET_OFFSET).standard_normal((N_SYMBOLS, dims)))}


def _fingerprint(mat) -> str:
    import hashlib
    return hashlib.sha1(np.asarray(mat, dtype=np.float64).tobytes()).hexdigest()[:12]


def reading(replicates=REPLICATES, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    cells = [one_replicate(circ, net, int(r)) for r in replicates]
    out = {"ok": True, "reason": None, "cells": cells, "spans": {}, "gains": {}, "reads": {},
           "worlds": {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED,
                      "tau": TAU, "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS, "n_train": N_TRAIN,
                      "n_held": N_HELD, "dims": WORLD_DIMS, "leak": WORLD_LEAK, "scale": SCALE, "gain": GAIN,
                      "noise": NOISE, "replicates": list(map(int, replicates)), "steps": STEPS, "lr": LR,
                      "eps": EPS, "ftol": FTOL}}
    gains = [c["trained_reward"] - c["init_reward"] for c in cells]
    out["gains"] = _paired([c["trained_reward"] for c in cells], [c["init_reward"] for c in cells])
    out["gains"]["values"] = gains
    out["reads"] = _paired([c["trained_read"] for c in cells], [c["init_read"] for c in cells])
    out["reads"]["values"] = [c["trained_read"] - c["init_read"] for c in cells]
    out["spans"] = {
        "replicates": len(cells), "n_act": cells[0]["n_act"], "coords": cells[0]["n_act"] ** 2,
        "identity_all": all(c["identity_bitwise"] for c in cells),
        "identity_worst": max(c["identity_max_abs"] for c in cells),
        "grad_norm_min": min(c["grad_norm"] for c in cells),
        "fd_worst": max(c["fd_worst_abs"] for c in cells),
        "fd_worst_at": max(cells, key=lambda c: c["fd_worst_abs"])["fd_worst_at"],
        "moves": [round(c["policy_move"], 4) for c in cells],
        "targets": [c["target_sha1"] for c in cells],
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the replicates were not rolled"} for c in CLAIMS]
    s, g, rd = r["spans"], r["gains"], r["reads"]
    j1 = {"id": "QA1",
          "measured": f"over {s['replicates']} replicates the identity policy's world is bit-identical to the "
                      f"environment's own rule on **{s['replicates']} of {s['replicates']}**, the worst absolute "
                      f"difference being **{s['identity_worst']:.1e}**",
          "verdict": "MET -- policy = I is the corpus's own rule, exactly" if (s["identity_all"] and
                                                                               s["identity_worst"] == 0.0) else
                     f"FALSIFIER FIRED -- the identity policy is not the environment's own rule: {s['identity_worst']}"}
    j2 = {"id": "QA2",
          "measured": f"the reward's backprop gradient against a central finite difference over **{s['coords']}** "
                      f"coordinates in each of {s['replicates']} replicates: the gradient's smallest norm is "
                      f"**{s['grad_norm_min']:.4f}** and the worst disagreement is **{s['fd_worst']:.2e}** at "
                      f"{s['fd_worst_at']}",
          "verdict": f"MET -- the loop carries the reward's gradient to all {s['coords']} coordinates" if
                     (s["grad_norm_min"] > 0.0 and s["fd_worst"] <= FTOL) else
                     f"FALSIFIER FIRED -- a gradient of norm {s['grad_norm_min']:.4f} or a disagreement of "
                     f"{s['fd_worst']:.2e}"}
    j3 = {"id": "QA3",
          "measured": f"the held-out reward runs "
                      f"{[round(c['init_reward'], 4) for c in r['cells']]} at the identity and "
                      f"{[round(c['trained_reward'], 4) for c in r['cells']]} trained, a paired gain of "
                      f"**{g['mean']:+.4f}** at **{g['sigma']:+.2f}** sigma over {g['n']} replicates",
          "verdict": f"MET -- the game can be played: the trained policy is worth {g['mean']:+.4f} on cues it was "
                     f"not trained on, at {g['sigma']:+.2f} sigma" if (g["mean"] >= GAIN_BAR and g["sigma"] >= SIGMA)
                     else f"FALSIFIER FIRED -- a gain of {g['mean']:+.4f} at {g['sigma']:+.2f} sigma, against a bar "
                          f"of {GAIN_BAR:.2f}" if (g["mean"] < GAIN_FLOOR or g["sigma"] < SIGMA) else
                     f"NULL -- a gain of {g['mean']:+.4f} between the floor {GAIN_FLOOR:.2f} and the bar "
                     f"{GAIN_BAR:.2f}"}
    j4 = {"id": "QA4",
          "measured": f"the decoder on the world's final state runs "
                      f"{[round(c['init_read'], 4) for c in r['cells']]} at the identity and "
                      f"{[round(c['trained_read'], 4) for c in r['cells']]} trained (a chance of "
                      f"{r['worlds']['chance']:.2f}), a paired difference of **{rd['mean']:+.4f}** at "
                      f"**{rd['sigma']:+.2f}** sigma",
          "verdict": f"MET -- acting to the reward raises the cue's decodability by {rd['mean']:+.4f}" if
                     rd["mean"] >= READ_BAR else
                     f"FALSIFIER FIRED -- acting costs the read-out: {rd['mean']:+.4f}" if rd["mean"] <= READ_FLOOR else
                     f"NULL -- {rd['mean']:+.4f} between {READ_FLOOR:.2f} and {READ_BAR:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the game gets a policy ==")
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        print(f"   REFUSED -- the replicates were not rolled")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    w = r["worlds"]
    print(f"   circuit {w['circuit']} ({w['size']} neurons), read-out draw {w['readout']}, {w['n_symbols']} symbols "
          f"at a chance of {w['chance']:.2f}")
    print(f"   the environment's own {w['dims']}-dimensional coupled world at leak {w['leak']}, {w['steps']} policy "
          f"steps at lr {w['lr']}, {len(w['replicates'])} replicates")
    print(f"\n   {'rep':>4} {'init reward':>12} {'trained':>9} {'gain':>8} {'init read':>10} {'trained':>8} "
          f"{'|move|':>8} {'grad norm':>10} {'fd worst':>10}")
    for c in r["cells"]:
        print(f"   {c['seed']:>4} {c['init_reward']:>12.4f} {c['trained_reward']:>9.4f} "
              f"{c['trained_reward'] - c['init_reward']:>+8.4f} {c['init_read']:>10.4f} {c['trained_read']:>8.4f} "
              f"{c['policy_move']:>8.3f} {c['grad_norm']:>10.4f} {c['fd_worst_abs']:>10.2e}")
    print(f"\n   the identity policy is the environment's own rule bit for bit: {r['spans']['identity_all']} "
          f"(worst {r['spans']['identity_worst']:.1e})")
    print("\n== the registered claims, QA1-QA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e325` closed on *a reward and a policy*; this unit gives the loop both and trains the second)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading()
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
