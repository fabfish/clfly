"""E478 -- the agent's policy in a sequence: a continual-learning benchmark whose subject is the policy.

`e477` gave the environment a **policy** and trained one on a reward. Its own finding names what that leaves: *"the
policy is not the benchmark's ... the runner does not carry one"* -- and every one of the corpus's retention
instruments is built for a **decoder over a task sequence**, not for the thing that acts. **This unit asks the
benchmark's own question of the policy**: three tasks in sequence, the policy trained on each in turn, and the
retention matrix read in **reward** rather than in accuracy.

The game is `e477`'s: the card's substrate and the environment's eight-dimensional coupled world, a reward that is
the squared distance from the world's final state to a **task-specific target**, and a 64-number linear policy from
the action population to the world's drive, initialized at the **identity** -- which is the environment's own rule,
bit for bit. The three tasks share one cue set and differ in the target, which is the conflicting-objective case. Four
claims, registered before any policy was trained.

- **SA1 -- and every replicate starts from the environment's own rule.** On every replicate the policy's first step
  is the corpus's own action rule **bit for bit**, and the replicate differs from its neighbours only in the
  environment's seed. **Falsifier**: any replicate whose identity world differs from the one the environment
  computes with no policy at all.
- **SA2 -- and every task in the sequence is learned.** For each task `k`, the reward on that task after training it
  exceeds the identity policy's reward on it by at least **0.50**, paired over the replicates, at **two** sigma or
  more. **Falsifier**: a gain below **0.20** on any task, or one that does not resolve.
- **SA3 -- and the policy forgets the first task.** The first task's reward after the whole sequence is below its
  value right after the first task, by at least **0.50**, paired, at **two** sigma or more. **Falsifier**: a drop
  below **0.20**, or one that does not resolve.
- **SA4 -- and the retention matrix says what the benchmark's does.** The mean of the policy's **diagonal** exceeds
  the mean of its **last row** by at least **0.50**, paired over the replicates, at **two** sigma or more.
  **Falsifier**: a gap below **0.20**, or one that does not resolve.

**What it can do beyond that.** It is the first unit in this corpus whose continual-learning subject is the **agent**
rather than a decoder: the same three-task sequence, the same diagonal-and-last-row instrument, and the two numbers
the benchmark's own retention statement is made of -- on a policy that decides what the agent does.

**What it cannot do.** *Three tasks and one target rule*: the reward is a squared distance to a drawn point, so a
sparse, saturating or action-side reward is not in it, and the sequence is three targets rather than the odour,
heading and antennal-lobe tasks. *And the tasks share one cue set*: they differ in the target and not in what the
agent is shown, which is the conflicting-objective case and not the benchmark's disjoint cue sets. *And the policy is
linear over one population with the body frozen*: 64 numbers, so the repertoire is small and the forgetting measured
here is a linear map's. *And no method is compared*: this is the `naive` arm of a policy sequence, and whether a
buffer or a penalty helps a **policy** the way it helps a decoder is a different unit. *And eight replicates are not
the population*: the sigma is the paired one over the worlds the replicates share.
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

#: the card's own substrate and world, as `e477` runs them
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
#: three tasks in sequence, one target each, and one policy trained on them in turn
TASKS = 3
REPLICATES = (0, 1, 2, 3, 4, 5, 6, 7)
STEPS = 300
LR = 0.05
TARGET_OFFSET = 101
#: the bars: a gain or a drop is MET at the bar and resolved, and its falsifier fires at the floor or unresolved
SIGMA = 2.0
BAR = 0.50
FLOOR = 0.20
CLAIMS = (
    ("SA1", "and every replicate starts from the environment's own rule, bit for bit",
     "On every replicate the policy's first step is the corpus's own action rule bit for bit, so the sequence starts "
     "from the loop every other unit of this line runs",
     "falsifier: any replicate whose identity world differs from the one the environment computes with no policy at "
     "all"),
    ("SA2", f"and every task in the sequence is learned, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "For each task the reward on that task after training it exceeds the identity policy's by at least 0.50, paired "
     "over the replicates, at two sigma or more",
     f"falsifier: a gain below {FLOOR:.2f} on any task, or one that does not resolve"),
    ("SA3", f"and the policy forgets the first task, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "The first task's reward after the whole sequence is below its value right after the first task by at least 0.50, "
     "paired, at two sigma or more",
     f"falsifier: a drop below {FLOOR:.2f}, or one that does not resolve"),
    ("SA4", f"and the retention matrix says what the benchmark's does, by {BAR:.2f} at {SIGMA:.0f} sigma",
     "The mean of the policy's diagonal exceeds the mean of its last row by at least 0.50, paired over the replicates, "
     "at two sigma or more",
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


def one_replicate(circ, net, seed: int) -> dict:
    """One replicate: three targets in sequence, the policy trained on each, and the retention matrix in reward.

    Row ``0`` is the identity policy on every task; row ``k + 1`` is the policy after task ``k``, read on tasks
    ``0`` through ``k``. The body, the circuit and the cue set are held; the **world** and its three targets are the
    replicate.
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
    tr_tr = torch.from_numpy(np.asarray(e.cue_input(y_tr, np.random.default_rng(seed + 31)), dtype=np.float32))
    tr_te = torch.from_numpy(np.asarray(e.cue_input(y_te, np.random.default_rng(seed + 61)), dtype=np.float32))
    #: one target per task and per symbol, drawn from the environment's seed
    targets = torch.as_tensor(np.random.default_rng(seed + TARGET_OFFSET).standard_normal((TASKS, N_SYMBOLS, dims)),
                              dtype=torch.float32)

    def reward_of(policy, task: int) -> float:
        e.policy = None if policy is None else policy
        with torch.no_grad():
            fn = e.feedback()
            net(tr_te, feedback=fn)
            w = fn.last_world
        tgt = targets[task][torch.as_tensor(y_te)]
        return -float(((w - tgt) ** 2).sum(dim=1).mean())

    eye = torch.eye(n_act, dtype=torch.float32)

    #: SA1 -- the identity policy against no policy at all, on the same cues
    e.policy = None
    with torch.no_grad():
        fn = e.feedback()
        net(tr_te, feedback=fn)
        w_none = fn.last_world
    e.policy = eye
    with torch.no_grad():
        fn = e.feedback()
        net(tr_te, feedback=fn)
        w_eye = fn.last_world
    identity_bitwise = bool(torch.equal(w_none, w_eye))

    R = [[None] * TASKS for _ in range(TASKS + 1)]
    R[0] = [reward_of(eye, j) for j in range(TASKS)]

    pol = torch.nn.Parameter(eye.clone())
    tgt_tr = [targets[k][torch.as_tensor(y_tr)] for k in range(TASKS)]
    for k in range(TASKS):
        #: a fresh optimizer per task, exactly as the runner builds one per task: the sequence's policy is trained
        #: the way the benchmark's decoder is -- inherited parameters, reset moments
        opt = torch.optim.Adam([pol], lr=LR)
        for _ in range(STEPS):
            opt.zero_grad()
            e.policy = pol
            fn = e.feedback()
            net(tr_tr, feedback=fn)
            w = fn.last_world
            task_reward = -((w - tgt_tr[k]) ** 2).sum(dim=1).mean()
            (-task_reward).backward()
            opt.step()
        for j in range(k + 1):
            R[k + 1][j] = reward_of(pol.detach(), j)

    return {"seed": int(seed), "n_act": n_act, "identity_bitwise": identity_bitwise,
            "identity_max_abs": float((w_none - w_eye).abs().max()),
            "identity_reward": list(R[0]),
            "R": R,
            "policy_move": float((pol.detach() - eye).norm()),
            "targets_sha1": _fingerprint(np.random.default_rng(seed + TARGET_OFFSET).standard_normal(
                (TASKS, N_SYMBOLS, dims)))}


def reading(replicates=REPLICATES, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    net = build_net(circ, RateConfig(tau=TAU)).torch_model()
    cells = [one_replicate(circ, net, int(r)) for r in replicates]
    out = {"ok": True, "reason": None, "cells": cells, "mean_R": [],
           "learned": {}, "forgot": {}, "retention": {}, "spans": {},
           "worlds": {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED,
                      "tau": TAU, "n_symbols": N_SYMBOLS, "chance": 1.0 / N_SYMBOLS, "n_train": N_TRAIN,
                      "n_held": N_HELD, "dims": WORLD_DIMS, "leak": WORLD_LEAK, "tasks": TASKS,
                      "replicates": list(map(int, replicates)), "steps": STEPS, "lr": LR}}
    #: the mean retention matrix over the replicates, so a reader sees the shape below the claims. The matrix is
    #: lower-triangular, so a cell no replicate read is `None` rather than a mean over nothing
    mean_R = []
    for k in range(TASKS + 1):
        row = []
        for j in range(TASKS):
            vals = [c["R"][k][j] for c in cells if c["R"][k][j] is not None]
            row.append(statistics.fmean(vals) if vals else None)
        mean_R.append(row)
    out["mean_R"] = mean_R
    #: SA2 -- each task's own gain over the identity policy, paired over the replicates
    out["learned"] = {f"task{k}": _paired([c["R"][k + 1][k] for c in cells],
                                          [c["R"][0][k] for c in cells]) for k in range(TASKS)}
    #: SA3 -- the first task's reward after the whole sequence against right after the first task
    out["forgot"] = _paired([c["R"][1][0] for c in cells], [c["R"][TASKS][0] for c in cells])
    #: SA4 -- the diagonal against the last row
    out["retention"] = _paired([statistics.fmean([c["R"][k + 1][k] for k in range(TASKS)]) for c in cells],
                               [statistics.fmean([c["R"][TASKS][j] for j in range(TASKS)]) for c in cells])
    out["spans"] = {
        "replicates": len(cells), "tasks": TASKS, "n_act": cells[0]["n_act"],
        "identity_all": all(c["identity_bitwise"] for c in cells),
        "identity_worst": max(c["identity_max_abs"] for c in cells),
        "moves": [round(c["policy_move"], 4) for c in cells],
        "targets": [c["targets_sha1"] for c in cells],
        "rows": TASKS + 1,
    }
    return out


def judge(r: dict) -> list[dict]:
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the replicates were not rolled"} for c in CLAIMS]
    s = r["spans"]
    j1 = {"id": "SA1",
          "measured": f"over {s['replicates']} replicates the identity policy's world is bit-identical to the "
                      f"environment's own rule on **{s['replicates']} of {s['replicates']}**, the worst absolute "
                      f"difference being **{s['identity_worst']:.1e}**",
          "verdict": "MET -- every replicate starts from the corpus's own rule, exactly" if
                     (s["identity_all"] and s["identity_worst"] == 0.0) else
                     f"FALSIFIER FIRED -- the first step is not the environment's own rule: {s['identity_worst']}"}
    gains = r["learned"]
    weakest = min(v["mean"] for v in gains.values())
    weak_sigma = min(v["sigma"] for v in gains.values())
    learned_met = all(v["mean"] >= BAR and v["sigma"] >= SIGMA for v in gains.values())
    learned_fired = any(v["mean"] < FLOOR or v["sigma"] < SIGMA for v in gains.values())
    j2 = {"id": "SA2",
          "measured": f"each task's reward after training it against the identity policy's, paired: "
                      f"{ {k: round(v['mean'], 4) for k, v in gains.items()} } at "
                      f"{ {k: round(v['sigma'], 2) for k, v in gains.items()} } sigma",
          "verdict": f"MET -- all {s['tasks']} tasks are learned, the weakest gain {weakest:+.4f} at "
                     f"{weak_sigma:+.2f} sigma" if learned_met else
                     f"FALSIFIER FIRED -- the weakest gain is {weakest:+.4f} at {weak_sigma:+.2f} sigma, against a "
                     f"bar of {BAR:.2f}" if learned_fired else
                     f"NULL -- the weakest gain {weakest:+.4f} sits between the floor {FLOOR:.2f} and the bar "
                     f"{BAR:.2f}"}
    f = r["forgot"]
    j3 = {"id": "SA3",
          "measured": f"the first task's reward right after it runs "
                      f"{[round(c['R'][1][0], 4) for c in r['cells']]} and after the whole sequence "
                      f"{[round(c['R'][s['tasks']][0], 4) for c in r['cells']]}, a paired drop of "
                      f"**{f['mean']:+.4f}** at **{f['sigma']:+.2f}** sigma",
          "verdict": f"MET -- the policy forgets the first task by {f['mean']:+.4f} at {f['sigma']:+.2f} sigma" if
                     (f["mean"] >= BAR and f["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- a drop of {f['mean']:+.4f} at {f['sigma']:+.2f} sigma, against a bar of "
                     f"{BAR:.2f}" if (f["mean"] < FLOOR or f["sigma"] < SIGMA) else
                     f"NULL -- a drop of {f['mean']:+.4f} between the floor {FLOOR:.2f} and the bar {BAR:.2f}"}
    rt = r["retention"]
    j4 = {"id": "SA4",
          "measured": f"the policy's mean diagonal against its mean last row, paired: "
                      f"**{rt['mean']:+.4f}** at **{rt['sigma']:+.2f}** sigma, with the mean matrix "
                      f"{[[round(x, 3) if x is not None else None for x in row] for row in r['mean_R']]}",
          "verdict": f"MET -- the diagonal exceeds the last row by {rt['mean']:+.4f} at {rt['sigma']:+.2f} sigma" if
                     (rt["mean"] >= BAR and rt["sigma"] >= SIGMA) else
                     f"FALSIFIER FIRED -- a gap of {rt['mean']:+.4f} at {rt['sigma']:+.2f} sigma, against a bar of "
                     f"{BAR:.2f}" if (rt["mean"] < FLOOR or rt["sigma"] < SIGMA) else
                     f"NULL -- a gap of {rt['mean']:+.4f} between the floor {FLOOR:.2f} and the bar {BAR:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    print("== the agent's policy in a sequence ==")
    if not r.get("ok") or len(r.get("cells") or []) < 2:
        print("   REFUSED -- the replicates were not rolled")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)
    w = r["worlds"]
    print(f"   circuit {w['circuit']} ({w['size']} neurons), {w['tasks']} tasks in sequence, {w['replicates']} "
          f"replicates, {w['steps']} policy steps at lr {w['lr']}")
    print("\n   the retention matrix in reward, averaged over the replicates "
          "(row 0 is the identity policy):")
    for k, row in enumerate(r["mean_R"]):
        print(f"      row {k}: " + "  ".join(f"{x:>9.4f}" if x is not None else f"{'-':>9}" for x in row))
    print("\n== the registered claims, SA1-SA4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e477` gave the loop a policy; this unit asks the benchmark's own retention question of it)")
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
