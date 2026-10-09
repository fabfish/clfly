"""E479 -- the methods on the policy's sequence: does a buffer beat a penalty when the subject is the agent?

`e478` put the agent's policy through a task sequence and read its retention matrix in reward, and it closed on the
one thing it could not do: *"no method is compared: this is the `naive` arm of a policy sequence, and whether a buffer
or a penalty helps a **policy** the way it helps a decoder is a different unit."* That is the corpus's flagship
question -- `e276` found a replay buffer beating the penalty by up to **11.84** sigma on the decoder's diagonal, and
`e476` found the ordering travelling to a second substrate and widening there -- and it has never been asked of the
thing that **acts**.

**This unit asks it.** Three tasks in sequence, each with its **own four cue symbols** so the tasks are separable --
which is the benchmark's own structure and not `e478`'s conflicting-objective case -- and three arms:

  * **`naive`** -- the policy trained on each task alone;
  * **`replay`** -- the same plus a buffer of the earlier tasks' `(cue, target)` pairs, interleaved into the step;
  * **`penalty`** -- the same plus a diagonal-Fisher penalty toward the policy as it stood after the previous task,
    at the card's own strength `lam = 1.0` with the Fisher normalised to unit mean, which is `e140`'s convention.

The subject is `e477`'s 64-number linear policy from the action population to the world's drive, initialized at the
**identity** and read in **reward**. Four claims, registered before any policy was trained.

- **TA1 -- and the three arms are one configuration.** The arms share the circuit, the read-out draw, the world, the
  cue set, the targets, the policy's identity initialization, the replicate seeds, the step count and the learning
  rate, differing only in what the arm's training adds. **Falsifier**: any of those differing between the arms.
- **TA2 -- and every arm learns every task.** For each arm and each task, the reward on that task after training it
  exceeds the identity policy's by at least **0.50**, paired over the replicates, at **two** sigma or more.
  **Falsifier**: a gain below **0.20** for any arm on any task, or one that does not resolve. *This is what makes the
  arms comparable: a penalty so strong it stops the policy learning would otherwise win the comparisons below.*
- **TA3 -- and the buffer beats the penalty on the diagonal.** `replay`'s mean diagonal exceeds `penalty`'s by at
  least **0.50**, paired over the replicates, at **two** sigma or more. **Falsifier**: a gap below **0.20**, or one
  that does not resolve. *`e276`'s V1, on a policy instead of a decoder.*
- **TA4 -- and it does not pay for it in retention.** `replay`'s mean **last row** exceeds `penalty`'s by at least
  **0.50**, paired, at **two** sigma or more. **Falsifier**: a gap below **0.20**, or one that does not resolve.
  *The retention half, which `e276`'s V2 read on forgetting.*

**What it can do beyond that.** It is the first measurement in this corpus of the method contrast that carries its
headline -- the buffer against the penalty -- on a subject that is neither the connectome's body nor a decoder, and it
says whether the benchmark's own answer survives being asked of the agent.

**What it cannot do.** *One strength and one penalty*: the penalty is a diagonal Fisher at `lam = 1.0`, the card's
own number, and a ladder over it is not run, so "the buffer wins at this strength" is not "the buffer wins". *And one
buffer setting*: the replay is a batch of earlier tasks' pairs at one size, not a sweep. *And the tasks share a
circuit and a cue population*: they differ in four cue symbols and one target block, so the sequence is easier than the
benchmark's and the forgetting here is a 64-parameter linear map's. *And no body is trained*: the body is frozen, so
nothing here says how a policy and the recurrent weights would share a sequence. *And eight replicates are not the
population*: the sigma is the paired one over the worlds the replicates share.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

#: the card's own substrate and world, with twelve cue symbols so that three tasks of four are separable
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
SYMBOLS_PER_TASK = 4
N_SYMBOLS = 12
N_TRAIN = 512
N_HELD = 256
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_DIMS = 8
TASKS = 3
REPLICATES = (0, 1, 2, 3, 4, 5, 6, 7)
STEPS = 300
LR = 0.05
TARGET_OFFSET = 101
#: the buffer's size and the penalty's strength, which is the card's own `lam = 1.0` and not a swept knob
REPLAY_TASK = 64
REPLAY_BATCH = 64
LAM = 1.0
FISHER_BATCHES = 8
#: the bars: MET at the bar and resolved, the falsifier at the floor or unresolved, and a null between
SIGMA = 2.0
BAR = 0.50
FLOOR = 0.20
ARMS = ("naive", "replay", "penalty")
CLAIMS = (
    ("TA1", "and the three arms are one configuration",
     "The arms share the circuit, the read-out draw, the world, the cue set, the targets, the policy's identity "
     "initialization, the replicate seeds, the step count and the learning rate, differing only in what the arm's "
     "training adds",
     "falsifier: any of those differing between the arms"),
    ("TA2", f"and every arm learns every task, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "For each arm and each task the reward on that task after training it exceeds the identity policy's by at least "
     "0.50, paired over the replicates, at two sigma or more",
     f"falsifier: a gain below {FLOOR:.2f} for any arm on any task, or one that does not resolve"),
    ("TA3", f"and the buffer beats the penalty on the diagonal, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "replay's mean diagonal exceeds penalty's by at least 0.50, paired over the replicates, at two sigma or more",
     f"falsifier: a gap below {FLOOR:.2f}, or one that does not resolve"),
    ("TA4", f"and it does not pay for it in retention, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "replay's mean last row exceeds penalty's by at least 0.50, paired over the replicates, at two sigma or more",
     f"falsifier: a gap below {FLOOR:.2f}, or one that does not resolve"),
)


def _paired(a: list, b: list) -> dict:
    d = [x - y for x, y in zip(a, b)]
    n = len(d)
    mean = statistics.fmean(d) if n else 0.0
    sd = statistics.stdev(d) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n else 0.0
    return {"n": n, "mean": mean, "sd": sd, "se": se, "sigma": (mean / se) if se > 0 else 0.0}


def _fingerprint(mat) -> str:
    return hashlib.sha1(np.asarray(mat, dtype=np.float64).tobytes()).hexdigest()[:12]


def one_arm(circ, net, seed: int, arm: str, lam: float = LAM) -> dict:
    """One arm on one replicate: three separable tasks in sequence, and the retention matrix in reward.

    ``lam`` is the penalty's strength and is ``e479``'s own constant unless a caller moves it, which is what the
    strength ladder beside this unit does; the default is the value every artifact of this arm carries.
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
    #: each task draws from its **own** block of four symbols, which is what makes the three separable
    y_tr = [rng.choice(np.arange(k * SYMBOLS_PER_TASK, (k + 1) * SYMBOLS_PER_TASK), size=N_TRAIN)
            for k in range(TASKS)]
    y_te = [rng.choice(np.arange(k * SYMBOLS_PER_TASK, (k + 1) * SYMBOLS_PER_TASK), size=N_HELD)
            for k in range(TASKS)]
    u_tr = [torch.from_numpy(np.asarray(e.cue_input(y_tr[k], np.random.default_rng(seed + 31 + k)),
                                        dtype=np.float32)) for k in range(TASKS)]
    u_te = [torch.from_numpy(np.asarray(e.cue_input(y_te[k], np.random.default_rng(seed + 61 + k)),
                                        dtype=np.float32)) for k in range(TASKS)]
    targets = torch.as_tensor(np.random.default_rng(seed + TARGET_OFFSET).standard_normal(
        (TASKS, SYMBOLS_PER_TASK, dims)), dtype=torch.float32)
    tgt_tr = [targets[k][torch.as_tensor(y_tr[k] - k * SYMBOLS_PER_TASK)] for k in range(TASKS)]
    tgt_te = [targets[k][torch.as_tensor(y_te[k] - k * SYMBOLS_PER_TASK)] for k in range(TASKS)]
    eye = torch.eye(n_act, dtype=torch.float32)

    #: TA1 -- the identity policy against no policy at all, which every arm starts from
    with torch.no_grad():
        e.policy = None
        fn = e.feedback()
        net(u_te[0], feedback=fn)
        w_none = fn.last_world
        e.policy = eye
        fn = e.feedback()
        net(u_te[0], feedback=fn)
        w_eye = fn.last_world
    identity_bitwise = bool(torch.equal(w_none, w_eye))

    def reward_of(policy, task: int) -> float:
        e.policy = None if policy is None else policy
        with torch.no_grad():
            fn = e.feedback()
            net(u_te[task], feedback=fn)
            w = fn.last_world
        return -float(((w - tgt_te[task]) ** 2).sum(dim=1).mean())

    def negative_reward(policy, task: int, idx=None):
        """The task's loss on a batch (or the whole split), with the graph kept."""
        e.policy = policy
        fn = e.feedback()
        u = u_tr[task] if idx is None else u_tr[task][idx]
        t = tgt_tr[task] if idx is None else tgt_tr[task][idx]
        net(u, feedback=fn)
        w = fn.last_world
        return ((w - t) ** 2).sum(dim=1).mean()

    R = [[None] * TASKS for _ in range(TASKS + 1)]
    R[0] = [reward_of(eye, j) for j in range(TASKS)]

    pol = torch.nn.Parameter(eye.clone())
    anchor = eye.clone()
    fisher = None
    buffer: list = []
    for k in range(TASKS):
        opt = torch.optim.Adam([pol], lr=LR)
        batch_rng = np.random.default_rng(seed + 100 + k)
        for _ in range(STEPS):
            opt.zero_grad()
            idx = batch_rng.integers(0, N_TRAIN, size=min(128, N_TRAIN))
            loss = negative_reward(pol, k, idx)
            if arm == "replay" and buffer:
                n = min(REPLAY_BATCH, len(buffer))
                pick = batch_rng.integers(0, len(buffer), size=n)
                e.policy = pol
                fn = e.feedback()
                ub = torch.stack([buffer[i][0] for i in pick])
                tb = torch.stack([buffer[i][1] for i in pick])
                net(ub, feedback=fn)
                loss = loss + ((fn.last_world - tb) ** 2).sum(dim=1).mean()
            if arm == "penalty" and fisher is not None:
                loss = loss + 0.5 * lam * torch.sum(fisher * (pol - anchor) ** 2)
            loss.backward()
            opt.step()
        #: the penalty's inputs, taken at the policy this task ended on -- `e140`'s convention: a unit-mean
        #: normalised diagonal Fisher and the parameters it was measured at
        if arm == "penalty":
            g = np.random.default_rng(seed + 200 + k)
            acc = torch.zeros_like(pol)
            for _ in range(FISHER_BATCHES):
                fi = g.integers(0, N_TRAIN, size=min(128, N_TRAIN))
                grad, = torch.autograd.grad(negative_reward(pol, k, fi), pol)
                acc = acc + grad.detach() ** 2
            f = acc / FISHER_BATCHES
            fisher = f / f.mean() if float(f.mean()) > 0 else f
            anchor = pol.detach().clone()
        if arm == "replay":
            take = np.random.default_rng(seed + 300 + k).choice(N_TRAIN, size=min(REPLAY_TASK, N_TRAIN),
                                                                replace=False)
            buffer.extend((u_tr[k][i], tgt_tr[k][i]) for i in take)
        for j in range(k + 1):
            R[k + 1][j] = reward_of(pol.detach(), j)

    return {"seed": int(seed), "arm": arm, "n_act": n_act, "identity_bitwise": identity_bitwise,
            "identity_max_abs": float((w_none - w_eye).abs().max()), "R": R,
            "policy_move": float((pol.detach() - eye).norm()),
            "targets_sha1": _fingerprint(np.random.default_rng(seed + TARGET_OFFSET).standard_normal(
                (TASKS, SYMBOLS_PER_TASK, dims)))}


def reading(replicates=REPLICATES, arms=ARMS, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    cells = [one_arm(circ, net, int(r), a) for r in replicates for a in arms]
    out = {"ok": True, "reason": None, "cells": cells, "mean_R": {}, "learned": {}, "diagonal": {},
           "last_row": {}, "ordering": {}, "spans": {},
           "worlds": {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED,
                      "tau": TAU, "n_symbols": N_SYMBOLS, "symbols_per_task": SYMBOLS_PER_TASK, "tasks": TASKS,
                      "chance": 1.0 / SYMBOLS_PER_TASK, "n_train": N_TRAIN, "n_held": N_HELD, "dims": WORLD_DIMS,
                      "leak": WORLD_LEAK, "arms": list(arms), "replicates": list(map(int, replicates)),
                      "steps": STEPS, "lr": LR, "lam": LAM, "replay_task": REPLAY_TASK,
                      "replay_batch": REPLAY_BATCH, "fisher_batches": FISHER_BATCHES}}
    by = {(c["seed"], c["arm"]): c for c in cells}

    def mean_R(arm):
        rows = []
        for k in range(TASKS + 1):
            row = []
            for j in range(TASKS):
                vals = [by[(r, arm)]["R"][k][j] for r in replicates if by[(r, arm)]["R"][k][j] is not None]
                row.append(statistics.fmean(vals) if vals else None)
            rows.append(row)
        return rows

    out["mean_R"] = {a: mean_R(a) for a in arms}
    out["learned"] = {a: {f"task{k}": _paired([by[(r, a)]["R"][k + 1][k] for r in replicates],
                                              [by[(r, a)]["R"][0][k] for r in replicates])
                          for k in range(TASKS)} for a in arms}
    out["diagonal"] = {a: [statistics.fmean([by[(r, a)]["R"][k + 1][k] for k in range(TASKS)])
                           for r in replicates] for a in arms}
    out["last_row"] = {a: [statistics.fmean([by[(r, a)]["R"][TASKS][j] for j in range(TASKS)])
                           for r in replicates] for a in arms}
    out["ordering"] = {
        "diagonal": _paired(out["diagonal"]["replay"], out["diagonal"]["penalty"]),
        "last_row": _paired(out["last_row"]["replay"], out["last_row"]["penalty"]),
        "penalty_over_naive": _paired(out["diagonal"]["penalty"], out["diagonal"]["naive"]),
        "replay_over_naive": _paired(out["diagonal"]["replay"], out["diagonal"]["naive"]),
    }
    out["spans"] = {
        "arms": list(arms), "replicates": len(replicates), "tasks": TASKS, "n_act": cells[0]["n_act"],
        "identity_all": all(c["identity_bitwise"] for c in cells),
        "identity_worst": max(c["identity_max_abs"] for c in cells),
        "targets": sorted({c["targets_sha1"] for c in cells}),
        "seeds": sorted({c["seed"] for c in cells}),
        "moves": {a: [round(by[(r, a)]["policy_move"], 3) for r in replicates] for a in arms},
        "cells": len(cells),
    }
    return out


def _band(mean, sigma, what):
    """MET at the bar and resolved, FALSIFIER at the floor or unresolved, and a null between."""
    if mean >= BAR and sigma >= SIGMA:
        return f"MET -- {what} {mean:+.4f} at {sigma:+.2f} sigma"
    if mean < FLOOR or sigma < SIGMA:
        return f"FALSIFIER FIRED -- {what} {mean:+.4f} at {sigma:+.2f} sigma, against a bar of {BAR:.2f}"
    return f"NULL -- {what} {mean:+.4f} between the floor {FLOOR:.2f} and the bar {BAR:.2f}"


def judge(r: dict) -> list[dict]:
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the arms were not rolled"} for c in CLAIMS]
    s = r["spans"]
    j1 = {"id": "TA1",
          "measured": f"{s['cells']} cells over the arms {s['arms']} and {s['replicates']} replicates, the seeds "
                      f"{s['seeds']}, the target fingerprints {s['targets']}, and the identity policy bit-identical "
                      f"to the environment's own rule on **{s['cells']} of {s['cells']}** cells with a worst absolute "
                      f"difference of **{s['identity_worst']:.1e}**",
          "verdict": "MET -- one configuration, three arms, and every cell starting from the corpus's own rule" if
                     (s["identity_all"] and s["identity_worst"] == 0.0 and len(s["seeds"]) == s["replicates"] and
                      len(s["targets"]) == s["replicates"]) else
                     f"FALSIFIER FIRED -- the cells are not one configuration: identity {s['identity_all']} at "
                     f"{s['identity_worst']}, {len(s['seeds'])} seeds over {s['replicates']} replicates, "
                     f"{len(s['targets'])} target draws"}
    gains = r["learned"]
    weakest = min(v["mean"] for a in gains.values() for v in a.values())
    weak_sigma = min(v["sigma"] for a in gains.values() for v in a.values())
    where = min(((v["mean"], a, k) for a in gains for k, v in gains[a].items()))[1:]
    j2 = {"id": "TA2",
          "measured": f"the gain over the identity policy, by arm and task: "
                      f"{ {a: {k: round(v['mean'], 4) for k, v in gains[a].items()} for a in gains} } at "
                      f"{ {a: {k: round(v['sigma'], 2) for k, v in gains[a].items()} for a in gains} } sigma",
          "verdict": f"MET -- all {len(gains)} arms learn all {s['tasks']} tasks, the weakest gain {weakest:+.4f} at "
                     f"{weak_sigma:+.2f} sigma" if (weakest >= BAR and weak_sigma >= SIGMA) else
                     f"FALSIFIER FIRED -- the weakest gain is {weakest:+.4f} at {weak_sigma:+.2f} sigma ({where}), "
                     f"against a bar of {BAR:.2f}" if (weakest < FLOOR or weak_sigma < SIGMA) else
                     f"NULL -- the weakest gain {weakest:+.4f} ({where}) is between the floor {FLOOR:.2f} and the bar "
                     f"{BAR:.2f}"}
    o = r["ordering"]
    d = o["diagonal"]
    j3 = {"id": "TA3",
          "measured": f"the mean diagonals are "
                      f"{ {a: round(statistics.fmean(r['diagonal'][a]), 4) for a in r['spans']['arms']} }, so the "
                      f"buffer over the penalty is **{d['mean']:+.4f}** at **{d['sigma']:+.2f}** sigma "
                      f"(replay over naive {o['replay_over_naive']['mean']:+.4f} at "
                      f"{o['replay_over_naive']['sigma']:+.2f}, penalty over naive "
                      f"{o['penalty_over_naive']['mean']:+.4f} at {o['penalty_over_naive']['sigma']:+.2f})",
          "verdict": _band(d["mean"], d["sigma"], "the buffer leads the penalty on the diagonal by")}
    lr_ = o["last_row"]
    j4 = {"id": "TA4",
          "measured": f"the mean last rows are "
                      f"{ {a: round(statistics.fmean(r['last_row'][a]), 4) for a in r['spans']['arms']} }, so the "
                      f"buffer over the penalty is **{lr_['mean']:+.4f}** at **{lr_['sigma']:+.2f}** sigma",
          "verdict": _band(lr_["mean"], lr_["sigma"], "the buffer retains more than the penalty by")}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the methods on the policy's sequence ==")
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        print("   REFUSED -- the arms were not rolled")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    w = r["worlds"]
    print(f"   circuit {w['circuit']} ({w['size']} neurons), {w['tasks']} tasks of {w['symbols_per_task']} symbols "
          f"each, {len(w['arms'])} arms, {w['replicates']} replicates")
    print(f"   the penalty at lam {w['lam']} with a unit-mean diagonal Fisher; the buffer at "
          f"{w['replay_task']} pairs per task and {w['replay_batch']} per step")
    for a in w["arms"]:
        print(f"\n   {a}: the mean retention matrix in reward (row 0 is the identity policy)")
        for k, row in enumerate(r["mean_R"][a]):
            print(f"      row {k}: " + "  ".join(f"{x:>9.4f}" if x is not None else f"{'-':>9}" for x in row))
    print("\n== the registered claims, TA1-TA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e276` found the buffer over the penalty on a decoder and `e476` found it travelling;")
    print("    this unit asks the same question of the 64 numbers that decide what the agent does)")
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
