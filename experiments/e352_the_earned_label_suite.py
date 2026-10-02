"""E352 -- the earned-label suite: three tasks through the world, and whether replay holds them.

`e349` to `e351` built and paid for a task whose answer exists only in the **environment**: the head reads the world's
own state, the world is driven by the agent's own actions, and unwired it is at rest, so its read-out is a constant
and the accuracy is chance. That is one task. **A benchmark is a sequence of them**, and every unit in this chain
before those three was a *single* task read through the model's state.

**This unit runs the suite.** One world, three tasks, four cue symbols each, an eight-dimensional world state read by
**one small head per task**, and the body trained through them in order -- which is the corpus's task-incremental
protocol with the read-out moved into the environment. After each task every task seen so far is measured, so the
retention matrix comes out the way the corpus's runners produce it and `mean_forgetting` is the same quantity:
`mean_j (R[j, j] - R[T-1, j])` for the tasks before the last.

Two arms, five seeds, the corpus's optimiser and hyperparameters. **`naive`** trains each task in turn and nothing
else. **`replay`** keeps a buffer of sixteen examples per finished task and adds a cross-entropy term on a batch of
eight of them to every step, through those tasks' own heads. Nothing else differs between the arms.

Four claims, registered before any of it was read.

- **T1 -- one configuration, one difference.** Within a seed the two arms share the world, its maps, the circuit,
  the examples, the body initialisation and the batch order, differing only in whether the buffer is kept.
  **Falsifier**: any of those differing.
- **T2 -- and the suite is learned.** The mean of the three diagonal accuracies, in both arms, is at least **0.10**
  above chance. **Falsifier**: within **0.05** of chance, which would say the earned-label task does not survive
  being made sequential. **Null**: between.
- **T3 -- and the earned-label suite forgets.** `naive`'s `mean_forgetting` is at least **0.05**. **Falsifier**:
  below **0.02**, which would say the body holds the world across the sequence by itself and there is nothing for a
  buffer to fix. **Null**: between.
- **T4 -- and the buffer reduces it.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least **0.05**.
  **Falsifier**: `replay` forgets **more** by 0.05 or more. **Null**: between.

**What it cannot do.** *A bespoke loop and two arms*: the optimiser, learning rate, step count, batch size and
buffer size are the corpus's, but the loop is written here rather than taken from the runner, and `ewc`, the block
penalties and the frozen controls are not run -- so this is a benchmark's *shape* on the earned label and not a
method comparison, and none of its numbers is comparable with the corpus's artifacts. *Three tasks and five seeds*:
a retention matrix with three entries is a small object, and a 0.05 forgetting difference at this spread needs more
seeds than five to resolve, which is why T4 has a null branch it can land in. *One world, one leak and one width*:
`leak = 0.35`, eight dimensions and four symbols per task, with `e351`'s finding that the width is most of the
carrier's value and its shape a seventh. *And the head is per task*, so this is task-incremental: which task the
trial belongs to is given to the read-out, and a shared head over one world is a different and harder benchmark.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

#: the corpus's closed-loop settings, one world with twelve symbols in three tasks of four
SIZE = 300
READOUT_SIZE = 32
SEED = 0
TAU = 12
N_TASKS = 3
N_CLASSES = 4
N_SYMBOLS = N_TASKS * N_CLASSES
N_TRAIN = 96
N_TEST = 48
SCALE = 1.0
GAIN = 1.0
NOISE = 1.0
WORLD_LEAK = 0.35
WORLD_DIMS = 8
ITERS = 500
LR = 3e-3
BATCH = 32
REPLAY_PER_TASK = 16
REPLAY_BATCH = 8
SEEDS = (0, 1, 2, 3, 4)
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
LEARNS = 0.10
FLAT = 0.05
FORGETS = 0.05
NOTHING = 0.02
CLAIMS = (
    ("T1", "one configuration, one difference",
     "Within a seed the two arms share the world, its maps, the circuit, the examples, the body initialisation and "
     "the batch order, differing only in whether the buffer is kept",
     "falsifier: any of those differing"),
    ("T2", f"and the suite is learned, by {LEARNS:.2f} over chance",
     "The mean of the three diagonal accuracies, in both arms, is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the earned-label suite forgets, by {FORGETS:.2f}",
     "`naive`'s `mean_forgetting` is at least 0.05",
     f"falsifier: below {NOTHING:.2f}"),
    ("T4", f"and the buffer reduces it, by {FORGETS:.2f}",
     "`replay`'s `mean_forgetting` is lower than `naive`'s by at least 0.05",
     f"falsifier: `replay` forgets more by {FORGETS:.2f} or more"),
)


def one_arm(circ, conn_net, rs, seed: int, arm: str) -> dict:
    """One seed's one arm: three tasks through one world, sequentially, with a retention matrix at the end."""
    import torch
    from clfly.network import env as fly_env

    env = fly_env.build(circ, readout_subset=rs, seed=SEED, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                        noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS)
    #: the corpus's own task builder: every task a cue range of its own, one world for all of them. The
    #: `readout_neurons` it is handed are the corpus's draw and are **unused** here, because this unit reads the
    #: environment and not the state.
    tasks = [fly_env.make_env_task(env, f"t{i}", symbols=range(i * N_CLASSES, (i + 1) * N_CLASSES),
                                   n_train=N_TRAIN, n_test=N_TEST, readout_neurons=rs,
                                   class_offset=i * N_CLASSES, seed=i) for i in range(N_TASKS)]
    fn = env.feedback()
    torch.manual_seed(seed)
    model = conn_net.torch_model()
    heads = [torch.nn.Linear(WORLD_DIMS, N_CLASSES) for _ in range(N_TASKS)]
    params = [model.theta, model.bias] + [p for h in heads for p in h.parameters()]
    opt = torch.optim.Adam(params, lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    U = [torch.from_numpy(t.u_train).float() for t in tasks]
    Y = [torch.from_numpy(t.y_train).long() for t in tasks]
    Ut = [torch.from_numpy(t.u_test).float() for t in tasks]
    Yt = [torch.from_numpy(t.y_test).long() for t in tasks]
    rng = np.random.default_rng(seed + 7)
    buffer: list[tuple] = []
    R = np.full((N_TASKS, N_TASKS), np.nan)

    def world_read(traj):
        #: **the one read-out**: the environment's state, eight numbers, and nothing about the model's own
        return fn.last_world

    def accuracy(k: int) -> float:
        with torch.no_grad():
            logits = heads[k](world_read(model(Ut[k], None, feedback=fn)))
            return float((logits.argmax(1) == Yt[k]).float().mean())

    for k in range(N_TASKS):
        for _ in range(ITERS):
            idx = rng.integers(0, len(Y[k]), size=min(BATCH, len(Y[k])))
            traj = model(U[k][idx], None, feedback=fn)
            loss = lossf(heads[k](world_read(traj)), Y[k][idx])
            if arm == REPLAY and buffer:
                j, buf_u, buf_y = buffer[rng.integers(0, len(buffer))]
                bidx = rng.integers(0, len(buf_y), size=min(REPLAY_BATCH, len(buf_y)))
                traj_r = model(buf_u[bidx], None, feedback=fn)
                loss = loss + lossf(heads[j](world_read(traj_r)), buf_y[bidx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        if arm == REPLAY:
            #: sixteen stored examples of the task just finished, drawn once from its own training split
            keep = rng.choice(len(Y[k]), size=min(REPLAY_PER_TASK, len(Y[k])), replace=False)
            buffer.append((k, U[k][torch.from_numpy(keep)], Y[k][torch.from_numpy(keep)]))
        for j in range(k + 1):
            R[k, j] = accuracy(j)

    diag = [float(R[i, i]) for i in range(N_TASKS)]
    final = [float(x) for x in R[N_TASKS - 1]]
    forgetting = float(np.mean([R[j, j] - R[N_TASKS - 1, j] for j in range(N_TASKS - 1)]))
    s = env.summary()
    return {"seed": seed, "arm": arm, "chance": 1.0 / N_CLASSES,
            "retention": [[None if np.isnan(x) else float(x) for x in row] for row in R],
            "diagonal": diag, "diagonal_mean": float(np.mean(diag)), "final": final,
            "mean_forgetting": forgetting, "n_buffer": len(buffer),
            "world_dims": s["world_dims"], "world_drive_sha1": s["world_drive_sha1"],
            "world_read_sha1": s["world_read_sha1"], "world_leak": s["world_leak"],
            "action_sha1": s["action_sha1"], "feedback_sha1": s["feedback_sha1"], "cue_sha1": s["cue_sha1"]}


def reading(seeds=SEEDS, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    conn_net = build_net(circ, RateConfig(tau=TAU))
    rows = [one_arm(circ, conn_net, rs, int(s), arm) for s in seeds for arm in ARMS]
    out = {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED, "tau": TAU,
           "n_tasks": N_TASKS, "n_classes": N_CLASSES, "n_symbols": N_SYMBOLS, "chance": 1.0 / N_CLASSES,
           "n_train": N_TRAIN, "n_test": N_TEST, "world_dims": WORLD_DIMS, "world_leak": WORLD_LEAK,
           "iters": ITERS, "lr": LR, "batch": BATCH, "replay_per_task": REPLAY_PER_TASK,
           "replay_batch": REPLAY_BATCH, "seeds": [int(s) for s in seeds], "rows": rows}
    for arm in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        for field in ("diagonal_mean", "mean_forgetting"):
            vals = [r[field] for r in sub]
            out[f"{arm}_{field}"] = statistics.fmean(vals)
            out[f"{arm}_{field}_sem"] = (statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else None
    out["replay_minus_naive_forgetting"] = out[f"{REPLAY}_mean_forgetting"] - out[f"{NAIVE}_mean_forgetting"]
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or []
    if len({x["arm"] for x in rows}) < 2 or len(rows) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the arms were not measured"} for c in CLAIMS]

    fields = ("world_dims", "world_drive_sha1", "world_read_sha1", "world_leak", "cue_sha1", "action_sha1",
              "feedback_sha1")
    agree = {f: len({x[f] for x in rows}) for f in fields}
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), {r['n_tasks']} tasks of "
                                  f"{r['n_classes']} classes at a chance of {r['chance']:.2f}, {r['n_train']} train "
                                  f"and {r['n_test']} test examples each, one {r['world_dims']}-dimensional world at "
                                  f"leak {r['world_leak']}, Adam at lr {r['lr']} for {r['iters']} steps at batch "
                                  f"{r['batch']}, {len(r['seeds'])} seeds; the arms' distinct world and population "
                                  f"fingerprints are {agree}",
          "verdict": "MET -- one configuration, one difference" if all(v == 1 for v in agree.values()) else
          f"FALSIFIER FIRED -- the configs are not shared: { {k: v for k, v in agree.items() if v != 1} }"}

    diag = min(r[f"{NAIVE}_diagonal_mean"], r[f"{REPLAY}_diagonal_mean"]) - r["chance"]
    j2 = {"id": "T2", "measured": f"the diagonal means are {r[f'{NAIVE}_diagonal_mean']:.4f} (`{NAIVE}`) and "
                                  f"{r[f'{REPLAY}_diagonal_mean']:.4f} (`{REPLAY}`) against a chance of "
                                  f"{r['chance']:.2f}, so the worse arm is {diag:+.4f} above it",
          "verdict": f"MET -- the suite is learned, {diag:+.4f} above chance" if diag >= LEARNS else
          f"FALSIFIER FIRED -- only {diag:+.4f} above chance" if diag < FLAT else
          f"NULL -- {diag:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    f_naive = r[f"{NAIVE}_mean_forgetting"]
    j3 = {"id": "T3", "measured": f"`{NAIVE}`'s mean forgetting is {f_naive:.4f} on a sem of "
                                  f"{r[f'{NAIVE}_mean_forgetting_sem']:.4f}, over the {N_TASKS - 1} tasks before "
                                  f"the last",
          "verdict": f"MET -- the suite forgets, {f_naive:.4f}" if f_naive >= FORGETS else
          f"FALSIFIER FIRED -- below {NOTHING:.2f}, {f_naive:.4f}" if f_naive < NOTHING else
          f"NULL -- {f_naive:.4f}, between {NOTHING:.2f} and {FORGETS:.2f}"}

    diff = r["replay_minus_naive_forgetting"]
    j4 = {"id": "T4", "measured": f"`{REPLAY}`'s mean forgetting is {r[f'{REPLAY}_mean_forgetting']:.4f} and "
                                  f"`{NAIVE}`'s is {f_naive:.4f}, so the buffer changes it by {diff:+.4f}",
          "verdict": f"MET -- the buffer reduces it by {abs(diff):.4f}" if diff <= -FORGETS else
          f"FALSIFIER FIRED -- the buffer makes it worse by {diff:.4f}" if diff >= FORGETS else
          f"NULL -- {diff:+.4f}, between {FORGETS:.2f} either way"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or []
    if not rows:
        print("== the earned-label suite ==\n   REFUSED -- the arms were not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the earned-label suite ==")
    print(f"   {r['circuit']} ({r['size']} neurons), {r['n_tasks']} tasks of {r['n_classes']} classes at a chance "
          f"of {r['chance']:.2f}, one {r['world_dims']}-dimensional world at leak {r['world_leak']}")
    print(f"\n   {'seed':>5} {'arm':>7} {'diagonal':>9} {'final t0':>9} {'forgetting':>11} {'retention'}")
    for row in rows:
        print(f"   {row['seed']:5d} {row['arm']:>7} {row['diagonal_mean']:9.4f} {row['final'][0]:9.4f} "
              f"{row['mean_forgetting']:11.4f} {[[None if x is None else round(x, 3) for x in rr] for rr in row['retention']]}")
    print(f"   mean `{NAIVE}`: diagonal {r[f'{NAIVE}_diagonal_mean']:.4f}, forgetting "
          f"{r[f'{NAIVE}_mean_forgetting']:.4f} | mean `{REPLAY}`: diagonal {r[f'{REPLAY}_diagonal_mean']:.4f}, "
          f"forgetting {r[f'{REPLAY}_mean_forgetting']:.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e349` to `e351` built one earned-label task with the answer only in the environment; this makes it")
    print("    a sequence and asks the corpus's own question of it -- does the body hold the world across tasks)")
    return sum("REFUSED" in row["verdict"] for row in j)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", default=",".join(str(x) for x in SEEDS), help="seed streams to train")
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    r = reading(seeds=tuple(int(x) for x in args.seeds.split(",")), size=args.size)
    r["claims"] = judge(r)
    if args.json_out:
        write_json(args.json_out, r)
        print(f"wrote {args.json_out}")
    return report(r)


if __name__ == "__main__":
    sys.exit(main())
