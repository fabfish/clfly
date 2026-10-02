"""E353 -- the class-incremental earned-label suite: one head, twelve classes, and the harder protocol.

`e352` made the earned label sequential -- three tasks of four cue symbols each through one world, the head reading
the environment's own state -- and it named the boundary of what it had built in its own "what it cannot do": *"the
head is per task, so this is task-incremental: which task the trial belongs to is given to the read-out, and a shared
head over one world is a different and harder benchmark."*

**This runs the harder one.** The suite is `e352`'s exactly -- the same world, the same circuits and populations,
the same three cue ranges, the same examples by construction -- and the only change is the read-out: **one shared
head over twelve classes**, each task's four occupying a slice of its own, with the loss taken over the current
task's slice so a learner is never shown a future task's classes. That is the corpus's class-incremental protocol,
moved onto a task whose answer exists only in the environment. Two arms again: **`naive`** and **`replay`** with
sixteen stored examples per finished task.

Four claims, registered before any of it was read.

- **T1 -- the same suite in another protocol.** The world, the circuit and the populations are `e352`'s to the
  fingerprint, and the arms share them within a seed, differing only in the buffer. **Falsifier**: a fingerprint
  differing from `e352`'s artifact, or a shared field differing between the arms.
- **T2 -- and the class-incremental suite is learned.** The mean of the three diagonal accuracies, in both arms, is
  at least **0.10** above chance. **Falsifier**: within **0.05** of chance, which would say the harder protocol
  leaves nothing to forget. **Null**: between.
- **T3 -- and the protocol is what costs.** `naive`'s `mean_forgetting` exceeds the **0.3333** `e352` measured in the
  task-incremental suite by at least **0.05**. **Falsifier**: within **0.02** of it, which would say giving the
  read-out the task's identity costs nothing. **Null**: between. **REFUSED** when `e352`'s artifact is absent, since
  the number it is compared against would then not be on disk.
- **T4 -- and the buffer still helps.** `replay`'s `mean_forgetting` is lower than `naive`'s by at least **0.05**.
  **Falsifier**: `replay` forgets **more** by 0.05 or more. **Null**: between. This is `e352`'s T4 asked in the
  harder protocol, and either answer is a result: a buffer that stops working when the head is shared would be a
  property of the benchmark and not of the buffer.

**What it cannot do.** *The comparison is against one number on disk*, `e352`'s `naive` forgetting of 0.3333 over
five seeds, so T3 is a difference between two estimates with their own spreads and not a paired contrast; the paired
version would need both protocols run in one module. *A bespoke loop and two arms*, with `ewc`, the block penalties
and the frozen controls unrun, so this is a benchmark's shape and not a method comparison. *Three tasks and five
seeds*, with a six-entry lower-left block. *One world, one leak and one width*: `leak = 0.35`, eight dimensions and
four symbols per task. *And the shared head is linear over one world*, so a wider or non-linear read-out of the same
world is `e350`'s and `e345`'s axis and not this unit's.
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

#: `e352`'s suite, unchanged: one world with twelve symbols in three tasks of four, the same seeds and sizes
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
#: the task-incremental number this protocol is compared against, from `e352`
TASK_INCREMENTAL = Path("runs/e352_the_earned_label_suite.json")
LEARNS = 0.10
FLAT = 0.05
COSTS = 0.05
NOTHING = 0.02
CLAIMS = (
    ("T1", "the same suite in another protocol",
     f"The world, circuit and populations are `{TASK_INCREMENTAL.name}`'s to the fingerprint, and the arms share "
     f"them within a seed, differing only in the buffer",
     "falsifier: a fingerprint differing from that artifact, or a shared field differing between the arms"),
    ("T2", f"and the class-incremental suite is learned, by {LEARNS:.2f} over chance",
     "The mean of the three diagonal accuracies, in both arms, is at least 0.10 above chance",
     f"falsifier: within {FLAT:.2f} of chance"),
    ("T3", f"and the protocol is what costs, by {COSTS:.2f}",
     "`naive`'s `mean_forgetting` exceeds the task-incremental one `e352` measured by at least 0.05",
     f"falsifier: within {NOTHING:.2f} of it; refused when that artifact is absent"),
    ("T4", f"and the buffer still helps, by {COSTS:.2f}",
     "`replay`'s `mean_forgetting` is lower than `naive`'s by at least 0.05",
     f"falsifier: `replay` forgets more by {COSTS:.2f} or more"),
)


def load(path) -> dict | None:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def one_arm(circ, conn_net, rs, seed: int, arm: str) -> dict:
    """One seed's one arm: three tasks through one world and **one shared head over all twelve classes**."""
    import torch
    from clfly.network import env as fly_env

    env = fly_env.build(circ, readout_subset=rs, seed=SEED, n_symbols=N_SYMBOLS, tau=TAU, scale=SCALE, gain=GAIN,
                        noise=NOISE, world_modes=0, world_leak=WORLD_LEAK, world_dims=WORLD_DIMS)
    tasks = [fly_env.make_env_task(env, f"t{i}", symbols=range(i * N_CLASSES, (i + 1) * N_CLASSES),
                                   n_train=N_TRAIN, n_test=N_TEST, readout_neurons=rs,
                                   class_offset=i * N_CLASSES, seed=i) for i in range(N_TASKS)]
    fn = env.feedback()
    torch.manual_seed(seed)
    model = conn_net.torch_model()
    #: **the one change from `e352`**: a single head over every class, each task confined to its own slice
    head = torch.nn.Linear(WORLD_DIMS, N_SYMBOLS)
    opt = torch.optim.Adam([model.theta, model.bias] + list(head.parameters()), lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    U = [torch.from_numpy(t.u_train).float() for t in tasks]
    Y = [torch.from_numpy(t.y_train).long() for t in tasks]
    Ut = [torch.from_numpy(t.u_test).float() for t in tasks]
    Yt = [torch.from_numpy(t.y_test).long() for t in tasks]
    rng = np.random.default_rng(seed + 7)
    buffer: list[tuple] = []
    R = np.full((N_TASKS, N_TASKS), np.nan)

    def world_read(traj):
        return fn.last_world

    def slice_logits(traj, k: int):
        """The shared head's logits over task ``k``'s own classes, which is the class-incremental protocol."""
        return head(world_read(traj))[:, k * N_CLASSES:(k + 1) * N_CLASSES]

    def accuracy(k: int) -> float:
        with torch.no_grad():
            logits = slice_logits(model(Ut[k], None, feedback=fn), k)
            return float((logits.argmax(1) == Yt[k]).float().mean())

    for k in range(N_TASKS):
        for _ in range(ITERS):
            idx = rng.integers(0, len(Y[k]), size=min(BATCH, len(Y[k])))
            loss = lossf(slice_logits(model(U[k][idx], None, feedback=fn), k), Y[k][idx])
            if arm == REPLAY and buffer:
                j, buf_u, buf_y = buffer[rng.integers(0, len(buffer))]
                bidx = rng.integers(0, len(buf_y), size=min(REPLAY_BATCH, len(buf_y)))
                loss = loss + lossf(slice_logits(model(buf_u[bidx], None, feedback=fn), j), buf_y[bidx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        if arm == REPLAY:
            keep = rng.choice(len(Y[k]), size=min(REPLAY_PER_TASK, len(Y[k])), replace=False)
            buffer.append((k, U[k][torch.from_numpy(keep)], Y[k][torch.from_numpy(keep)]))
        for j in range(k + 1):
            R[k, j] = accuracy(j)

    diag = [float(R[i, i]) for i in range(N_TASKS)]
    s = env.summary()
    return {"seed": seed, "arm": arm, "chance": 1.0 / N_CLASSES,
            "retention": [[None if np.isnan(x) else float(x) for x in row] for row in R],
            "diagonal": diag, "diagonal_mean": float(np.mean(diag)),
            "final": [float(x) for x in R[N_TASKS - 1]],
            "mean_forgetting": float(np.mean([R[j, j] - R[N_TASKS - 1, j] for j in range(N_TASKS - 1)])),
            "n_buffer": len(buffer), "shared_head": True,
            "world_dims": s["world_dims"], "world_drive_sha1": s["world_drive_sha1"],
            "world_read_sha1": s["world_read_sha1"], "world_leak": s["world_leak"],
            "cue_sha1": s["cue_sha1"], "action_sha1": s["action_sha1"], "feedback_sha1": s["feedback_sha1"]}


def reading(seeds=SEEDS, size: int = SIZE, readout_size: int = READOUT_SIZE,
            task_path: Path = TASK_INCREMENTAL) -> dict:
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
           "replay_batch": REPLAY_BATCH, "protocol": "class-incremental", "seeds": [int(s) for s in seeds],
           "rows": rows}
    for arm in ARMS:
        sub = [r for r in rows if r["arm"] == arm]
        for field in ("diagonal_mean", "mean_forgetting"):
            vals = [r[field] for r in sub]
            out[f"{arm}_{field}"] = statistics.fmean(vals)
            out[f"{arm}_{field}_sem"] = (statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else None
    out["replay_minus_naive_forgetting"] = out[f"{REPLAY}_mean_forgetting"] - out[f"{NAIVE}_mean_forgetting"]
    #: the task-incremental suite this one is the harder protocol of, and the world it should share with it
    other = load(task_path)
    out["task_incremental_source"] = Path(task_path).name if other else None
    out["task_incremental_naive_forgetting"] = (other.get(f"{NAIVE}_mean_forgetting") if other else None)
    out["task_incremental_world_sha1"] = (
        sorted({r["world_read_sha1"] for r in other["rows"]}) if other else None)
    out["this_world_sha1"] = sorted({r["world_read_sha1"] for r in rows})
    out["same_world_as_task_incremental"] = (
        out["task_incremental_world_sha1"] == out["this_world_sha1"] if other else None)
    out["protocol_cost"] = (out[f"{NAIVE}_mean_forgetting"] - out["task_incremental_naive_forgetting"]
                            if other else None)
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or []
    if len({x["arm"] for x in rows}) < 2 or len(rows) < 2:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the arms were not measured"} for c in CLAIMS]

    fields = ("world_dims", "world_drive_sha1", "world_read_sha1", "world_leak", "cue_sha1", "action_sha1",
              "feedback_sha1")
    agree = {f: len({x[f] for x in rows}) for f in fields}
    same = r.get("same_world_as_task_incremental")
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), {r['n_tasks']} tasks of "
                                  f"{r['n_classes']} classes at a chance of {r['chance']:.2f}, one shared head over "
                                  f"{r['n_symbols']} classes, one {r['world_dims']}-dimensional world at leak "
                                  f"{r['world_leak']}, {len(r['seeds'])} seeds; the arms' distinct fingerprints "
                                  f"are {agree}, and this run's world fingerprints are "
                                  f"{r['this_world_sha1']} against the task-incremental artifact's "
                                  f"{r['task_incremental_world_sha1']}",
          "verdict": "MET -- the same suite in another protocol" if all(v == 1 for v in agree.values())
          and same is not False else
          f"FALSIFIER FIRED -- the arms are not shared {agree}, or the world is not the same {same}"}

    diag = min(r[f"{NAIVE}_diagonal_mean"], r[f"{REPLAY}_diagonal_mean"]) - r["chance"]
    j2 = {"id": "T2", "measured": f"the diagonal means are {r[f'{NAIVE}_diagonal_mean']:.4f} (`{NAIVE}`) and "
                                  f"{r[f'{REPLAY}_diagonal_mean']:.4f} (`{REPLAY}`) against a chance of "
                                  f"{r['chance']:.2f}, so the worse arm is {diag:+.4f} above it",
          "verdict": f"MET -- the class-incremental suite is learned, {diag:+.4f} above chance" if diag >= LEARNS
          else f"FALSIFIER FIRED -- only {diag:+.4f} above chance" if diag < FLAT else
          f"NULL -- {diag:+.4f} above chance, between {FLAT:.2f} and {LEARNS:.2f}"}

    cost = r.get("protocol_cost")
    if cost is None:
        j3 = {"id": "T3", "measured": "the task-incremental artifact is not on disk",
              "verdict": "REFUSED -- the number this protocol is compared against is absent"}
    else:
        j3 = {"id": "T3", "measured": f"`{NAIVE}` forgets {r[f'{NAIVE}_mean_forgetting']:.4f} here against "
                                      f"{r['task_incremental_naive_forgetting']:.4f} in the task-incremental suite, "
                                      f"a cost of {cost:+.4f}",
              "verdict": f"MET -- the protocol costs {cost:+.4f}" if cost >= COSTS else
              f"FALSIFIER FIRED -- within {NOTHING:.2f} of it, {cost:+.4f}" if cost < NOTHING else
              f"NULL -- {cost:+.4f}, between {NOTHING:.2f} and {COSTS:.2f}"}

    diff = r["replay_minus_naive_forgetting"]
    j4 = {"id": "T4", "measured": f"`{REPLAY}`'s mean forgetting is {r[f'{REPLAY}_mean_forgetting']:.4f} and "
                                  f"`{NAIVE}`'s is {r[f'{NAIVE}_mean_forgetting']:.4f}, so the buffer changes it "
                                  f"by {diff:+.4f}",
          "verdict": f"MET -- the buffer still helps, by {abs(diff):.4f}" if diff <= -COSTS else
          f"FALSIFIER FIRED -- it makes forgetting worse by {diff:.4f}" if diff >= COSTS else
          f"NULL -- {diff:+.4f}, between {COSTS:.2f} either way"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or []
    if not rows:
        print("== the class-incremental earned-label suite ==\n   REFUSED -- the arms were not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== the class-incremental earned-label suite ==")
    print(f"   {r['circuit']} ({r['size']} neurons), {r['n_tasks']} tasks of {r['n_classes']} classes at a chance "
          f"of {r['chance']:.2f}, one shared head over {r['n_symbols']} classes, world width {r['world_dims']}")
    print(f"\n   {'seed':>5} {'arm':>7} {'diagonal':>9} {'forgetting':>11} {'retention'}")
    for row in rows:
        print(f"   {row['seed']:5d} {row['arm']:>7} {row['diagonal_mean']:9.4f} {row['mean_forgetting']:11.4f} "
              f"{[[None if x is None else round(x, 3) for x in rr] for rr in row['retention']]}")
    print(f"   mean `{NAIVE}`: diagonal {r[f'{NAIVE}_diagonal_mean']:.4f}, forgetting "
          f"{r[f'{NAIVE}_mean_forgetting']:.4f} | mean `{REPLAY}`: diagonal {r[f'{REPLAY}_diagonal_mean']:.4f}, "
          f"forgetting {r[f'{REPLAY}_mean_forgetting']:.4f}")
    if r.get("task_incremental_naive_forgetting") is not None:
        print(f"   the task-incremental suite forgets {r['task_incremental_naive_forgetting']:.4f} under "
              f"`{NAIVE}`, so this protocol costs {r['protocol_cost']:+.4f}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e352` made the earned label sequential with a head per task; this asks the same suite with the")
    print("    task's identity taken away from the read-out, which is the corpus's own class-incremental protocol)")
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
