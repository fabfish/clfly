"""E354 -- both protocols in one module: what the shared head costs, paired.

`e352` made the earned label sequential with a head per task and `e353` ran the same suite with one shared head over
every class, and it closed on the gap its own comparison left: *"the protocol comparison is against one number on
disk, `e352`'s 0.3333 over five seeds, so T3 is a difference of two estimates with their own spreads and not a
paired contrast; the paired version would need both protocols in one module."*

**This is that module.** One process, one seed at a time, **four arms per seed**: the task-incremental and
class-incremental protocols crossed with `naive` and `replay`. Everything the two protocols share is built the same
way from the same seed -- the world, its maps, the circuit, the populations, the three tasks and the examples -- and
the body's initialisation is the same because the torch seed is reset before each arm. So the protocol cost is a
difference of two arms of the **same seed and the same world**, and its sigma is the across-seed spread of that
difference instead of the distance between two unpaired means.

Four claims, registered before any of it was read.

- **T1 -- one world, four arms.** Every arm's world fingerprints agree, and within a protocol the arms differ only
  in the buffer while across protocols they differ only in the head. **Falsifier**: a world fingerprint differing,
  or a within-protocol difference other than the buffer.
- **T2 -- and the shared head costs something.** The paired cost -- `naive`'s forgetting in the class-incremental
  protocol minus its forgetting in the task-incremental one, per seed -- is **positive at 2 sigma**. **Falsifier**:
  at or below zero at 2 sigma, i.e. the shared head resolving as free, which would say the task's identity is worth
  nothing to this read-out. **Null**: unresolved.
- **T3 -- and it is small.** The paired cost is at most **0.05**. **Falsifier**: **0.10** or more, which would say
  the identity is worth as much as a tenth of the benchmark. **Null**: between. `e353`'s unpaired reading put it at
  +0.0208; this asks the same question with the seed's own world held fixed.
- **T4 -- and the buffer is worth the same in both protocols.** The buffer's reduction of forgetting differs between
  the protocols by at most **0.05**. **Falsifier**: **0.10** or more apart, which would say the value of a replay
  buffer is a property of the protocol and not of the buffer. **Null**: between.

**What it cannot do.** *Two arms and two protocols, three tasks and five seeds*: the paired cost has four degrees of
freedom, so T2 resolves a cost of about 0.03 and not less. *A bespoke loop*, with `ewc`, the block penalties and the
frozen controls unrun, so this is a benchmark's shape and not a method comparison, and none of its numbers is
comparable with the corpus's artifacts. *One world, one leak and one width*: `leak = 0.35`, eight dimensions and
four symbols per task, with `e351`'s finding that the width is 88% of the carrier's value and its channel's shape a
seventh. *And the two protocols differ only in the head*, which is what makes the cost attributable: a shared head
over a wider or non-linear read-out is `e350`'s axis and not this unit's.
"""

from __future__ import annotations

import argparse
import math
import statistics
import sys
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json

#: `e352`'s suite, unchanged, and the two protocols crossed with the same two arms
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
PROTOCOLS = ("task", "class")
TASK, CLASS = PROTOCOLS
ARMS = ("naive", "replay")
NAIVE, REPLAY = ARMS
COSTS = 0.05
COSTS_FIRES = 0.10
SAME = 0.05
SAME_FIRES = 0.10
SIGMA = 2.0
CLAIMS = (
    ("T1", "one world, four arms",
     "Every arm's world fingerprints agree, and within a protocol the arms differ only in the buffer while across "
     "protocols they differ only in the head",
     "falsifier: a world fingerprint differing, or a within-protocol difference other than the buffer"),
    ("T2", f"and the shared head costs something, at {SIGMA:.0f} sigma",
     "The paired cost is positive at 2 sigma",
     "falsifier: at or below zero at 2 sigma; null: unresolved"),
    ("T3", f"and it is small, at most {COSTS:.2f}",
     "The paired cost is at most 0.05",
     f"falsifier: {COSTS_FIRES:.2f} or more"),
    ("T4", f"and the buffer is worth the same in both protocols, within {SAME:.2f}",
     "The buffer's reduction of forgetting differs between the protocols by at most 0.05",
     f"falsifier: {SAME_FIRES:.2f} or more apart"),
)


def one_arm(circ, conn_net, rs, seed: int, protocol: str, arm: str) -> dict:
    """One seed's one (protocol, arm): the same world and the same body initialisation in all four."""
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
    #: **the one difference between the protocols**: a head per task, or one head over every class
    shared = protocol == CLASS
    heads = [torch.nn.Linear(WORLD_DIMS, N_SYMBOLS if shared else N_CLASSES) for _ in range(N_TASKS)]
    if shared:
        heads = [heads[0]] * N_TASKS
    opt = torch.optim.Adam([model.theta, model.bias] + [p for h in {id(h): h for h in heads}.values()
                                                        for p in h.parameters()], lr=LR)
    lossf = torch.nn.CrossEntropyLoss()
    U = [torch.from_numpy(t.u_train).float() for t in tasks]
    Y = [torch.from_numpy(t.y_train).long() for t in tasks]
    Ut = [torch.from_numpy(t.u_test).float() for t in tasks]
    Yt = [torch.from_numpy(t.y_test).long() for t in tasks]
    rng = np.random.default_rng(seed + 7)
    buffer: list[tuple] = []
    R = np.full((N_TASKS, N_TASKS), np.nan)

    def logits(traj, k: int):
        """Task ``k``'s logits: its own head, or the shared head's slice, which is the class-incremental rule."""
        out = heads[k](fn.last_world)
        return out[:, k * N_CLASSES:(k + 1) * N_CLASSES] if shared else out

    def accuracy(k: int) -> float:
        with torch.no_grad():
            return float((logits(model(Ut[k], None, feedback=fn), k).argmax(1) == Yt[k]).float().mean())

    for k in range(N_TASKS):
        for _ in range(ITERS):
            idx = rng.integers(0, len(Y[k]), size=min(BATCH, len(Y[k])))
            loss = lossf(logits(model(U[k][idx], None, feedback=fn), k), Y[k][idx])
            if arm == REPLAY and buffer:
                j, buf_u, buf_y = buffer[rng.integers(0, len(buffer))]
                bidx = rng.integers(0, len(buf_y), size=min(REPLAY_BATCH, len(buf_y)))
                loss = loss + lossf(logits(model(buf_u[bidx], None, feedback=fn), j), buf_y[bidx])
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
    return {"seed": seed, "protocol": protocol, "arm": arm, "chance": 1.0 / N_CLASSES, "shared_head": shared,
            "retention": [[None if np.isnan(x) else float(x) for x in row] for row in R],
            "diagonal": diag, "diagonal_mean": float(np.mean(diag)),
            "final": [float(x) for x in R[N_TASKS - 1]],
            "mean_forgetting": float(np.mean([R[j, j] - R[N_TASKS - 1, j] for j in range(N_TASKS - 1)])),
            "n_buffer": len(buffer), "world_dims": s["world_dims"], "world_drive_sha1": s["world_drive_sha1"],
            "world_read_sha1": s["world_read_sha1"], "world_leak": s["world_leak"], "cue_sha1": s["cue_sha1"],
            "action_sha1": s["action_sha1"], "feedback_sha1": s["feedback_sha1"]}


def reading(seeds=SEEDS, size: int = SIZE, readout_size: int = READOUT_SIZE) -> dict:
    from clfly.connectome import annotate, circuits, graph
    from clfly.network.model import RateConfig, build_net

    conn, ann = graph.build(), annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=size)
    rs = np.sort(np.random.default_rng(SEED).choice(circ.n_neurons, size=readout_size, replace=False))
    conn_net = build_net(circ, RateConfig(tau=TAU))
    rows = [one_arm(circ, conn_net, rs, int(s), p, a) for s in seeds for p in PROTOCOLS for a in ARMS]
    out = {"circuit": circ.name, "size": circ.n_neurons, "readout": int(len(rs)), "seed": SEED, "tau": TAU,
           "n_tasks": N_TASKS, "n_classes": N_CLASSES, "n_symbols": N_SYMBOLS, "chance": 1.0 / N_CLASSES,
           "n_train": N_TRAIN, "n_test": N_TEST, "world_dims": WORLD_DIMS, "world_leak": WORLD_LEAK,
           "iters": ITERS, "lr": LR, "batch": BATCH, "replay_per_task": REPLAY_PER_TASK,
           "replay_batch": REPLAY_BATCH, "protocols": list(PROTOCOLS), "arms": list(ARMS),
           "seeds": [int(s) for s in seeds], "rows": rows}

    def cell(protocol, arm, field=("mean_forgetting",)):
        sub = [r for r in rows if r["protocol"] == protocol and r["arm"] == arm]
        vals = [r[field[0]] for r in sub]
        return {"n": len(vals), "mean": statistics.fmean(vals) if vals else None,
                "sem": (statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else None, "vals": vals}

    for protocol in PROTOCOLS:
        for arm in ARMS:
            out[f"{protocol}_{arm}_forgetting"] = cell(protocol, arm)
            out[f"{protocol}_{arm}_diagonal"] = cell(protocol, arm, ("diagonal_mean",))
    #: **the paired contrast**: both numbers come from the same seed and the same world
    out["cost"] = {}
    for arm in ARMS:
        c = {r["seed"]: r["mean_forgetting"] for r in rows if r["arm"] == arm and r["protocol"] == CLASS}
        t = {r["seed"]: r["mean_forgetting"] for r in rows if r["arm"] == arm and r["protocol"] == TASK}
        vals = [c[s] - t[s] for s in sorted(set(c) & set(t))]
        out["cost"][arm] = {"n": len(vals), "vals": vals, "mean": statistics.fmean(vals) if vals else None,
                            "sem": (statistics.stdev(vals) / math.sqrt(len(vals))) if len(vals) > 1 else None}
    for arm, est in out["cost"].items():
        est["sigma"] = (abs(est["mean"]) / est["sem"]) if est["mean"] is not None and est["sem"] else None
    #: **the buffer's value in each protocol**, and how far apart the two are
    out["buffer_value"] = {}
    for protocol in PROTOCOLS:
        n = out[f"{protocol}_{NAIVE}_forgetting"]["mean"]
        r = out[f"{protocol}_{REPLAY}_forgetting"]["mean"]
        out["buffer_value"][protocol] = (r - n) if (n is not None and r is not None) else None
    vals = [out["buffer_value"][p] for p in PROTOCOLS if out["buffer_value"][p] is not None]
    out["buffer_gap"] = (max(vals) - min(vals)) if len(vals) == 2 else None
    return out


def judge(r: dict) -> list[dict]:
    rows = r.get("rows") or []
    if len(rows) < 2 or len({(x["protocol"], x["arm"]) for x in rows}) < 4:
        return [{"id": c[0], "measured": "", "verdict": "REFUSED -- the four arms were not measured"}
                for c in CLAIMS]

    fields = ("world_dims", "world_drive_sha1", "world_read_sha1", "world_leak", "cue_sha1", "action_sha1",
              "feedback_sha1")
    agree = {f: len({x[f] for x in rows}) for f in fields}
    j1 = {"id": "T1", "measured": f"circuit {r['circuit']} ({r['size']} neurons), {r['n_tasks']} tasks of "
                                  f"{r['n_classes']} classes at a chance of {r['chance']:.2f}, {r['n_train']} train "
                                  f"and {r['n_test']} test examples each, one {r['world_dims']}-dimensional world at "
                                  f"leak {r['world_leak']}, Adam at lr {r['lr']} for {r['iters']} steps at batch "
                                  f"{r['batch']}, {len(r['seeds'])} seeds and {len(rows) // len(r['seeds'])} arms "
                                  f"each; the arms' distinct fingerprints are {agree}",
          "verdict": "MET -- one world, four arms" if all(v == 1 for v in agree.values()) else
          f"FALSIFIER FIRED -- the arms do not share the world: { {k: v for k, v in agree.items() if v != 1} }"}

    cost = r["cost"][NAIVE]
    met = cost["mean"] is not None and cost["mean"] > 0 and (cost["sigma"] or 0) >= SIGMA
    j2 = {"id": "T2", "measured": f"`{NAIVE}`'s paired cost is {cost['mean']:+.4f} on a sem of {cost['sem']:.4f} "
                                  f"({cost['sigma']:.2f} sigma), the per-seed costs being "
                                  f"{[round(x, 4) for x in cost['vals']]}",
          "verdict": f"MET -- the shared head costs {cost['mean']:+.4f} at {cost['sigma']:.2f} sigma" if met else
          f"FALSIFIER FIRED -- it resolves as free or negative, {cost['mean']:+.4f} at {cost['sigma']:.2f} sigma"
          if (cost["mean"] is not None and cost["mean"] <= 0) else
          f"NULL -- {cost['mean']:+.4f} at {(cost['sigma'] or 0):.2f} sigma, unresolved"}

    c = cost["mean"]
    j3 = {"id": "T3", "measured": f"the paired cost is {c:+.4f}, against `e353`'s unpaired +0.0208",
          "verdict": f"MET -- it is small, {c:+.4f}" if c <= COSTS else
          f"FALSIFIER FIRED -- {c:.4f}, as much as a tenth of the benchmark" if c >= COSTS_FIRES else
          f"NULL -- {c:+.4f}, between {COSTS:.2f} and {COSTS_FIRES:.2f}"}

    gap = r.get("buffer_gap")
    if gap is None:
        j4 = {"id": "T4", "measured": "one of the protocols' buffer values was not computable",
              "verdict": "REFUSED -- the buffer's value was not computable"}
    else:
        j4 = {"id": "T4", "measured": f"the buffer is worth {r['buffer_value'][TASK]:+.4f} in the task-incremental "
                                      f"protocol and {r['buffer_value'][CLASS]:+.4f} in the class-incremental one, "
                                      f"{gap:.4f} apart",
              "verdict": f"MET -- the buffer is worth the same in both, {gap:.4f} apart" if gap < SAME else
              f"FALSIFIER FIRED -- {gap:.4f} apart" if gap >= SAME_FIRES else
              f"NULL -- {gap:.4f} apart, between {SAME:.2f} and {SAME_FIRES:.2f}"}
    return [j1, j2, j3, j4]


def report(r: dict) -> int:
    rows = r.get("rows") or []
    if not rows:
        print("== both protocols in one module ==\n   REFUSED -- the four arms were not measured")
        for row in judge(r):
            print(f"      {row['id']}: {row['verdict']}")
        return len(CLAIMS)

    print("== both protocols in one module ==")
    print(f"   {r['circuit']} ({r['size']} neurons), {r['n_tasks']} tasks of {r['n_classes']} classes at a chance "
          f"of {r['chance']:.2f}, one {r['world_dims']}-dimensional world at leak {r['world_leak']}")
    print(f"\n   {'seed':>5} {'protocol':>7} {'arm':>7} {'diagonal':>9} {'forgetting':>11}")
    for row in rows:
        print(f"   {row['seed']:5d} {row['protocol']:>7} {row['arm']:>7} {row['diagonal_mean']:9.4f} "
              f"{row['mean_forgetting']:11.4f}")
    print(f"\n   forgetting by cell: " + ", ".join(
        f"{p}/{a} {r[f'{p}_{a}_forgetting']['mean']:.4f}" for p in PROTOCOLS for a in ARMS))
    for arm in ARMS:
        e = r["cost"][arm]
        print(f"   paired cost, `{arm}`: {e['mean']:+.4f} on a sem of {e['sem']:.4f} "
              f"({e['sigma']:.2f} sigma), per seed {[round(x, 4) for x in e['vals']]}")

    print("\n== the registered claims, T1-T4 ==")
    j = judge(r)
    for cl, row in zip(CLAIMS, j):
        print(f"      {row['id']}: {row['measured']}  -> {row['verdict']}")
        print(f"          the claim was: {cl[2]}")
        print(f"          and its {cl[3]}")
    print("\n   (`e353` compared the protocols across two artifacts and could not pair them; this runs both in one")
    print("    process so the cost is a difference of the same seed's own world)")
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
