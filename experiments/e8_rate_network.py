"""E8 — the rate-network substrate: does sequential training on real wiring forget?

Everything measured so far sits on the linear-Gaussian reduction, where the connectome
sets the problem geometry exactly but the dynamics are a linearisation.  That bought
an exact oracle, which is why it was worth doing first — but a benchmark has to
eventually run on a network that has to be *trained*, and this is the first
end-to-end run of that.

The model is a connectome-constrained rate network (see
:mod:`clfly.network.model`): the wiring's sign pattern is a fixed mask, its ``log1p``
synapse strengths are the initialisation, and the masked weights, the bias and a
linear decoder are trained by backprop-through-time.  Three behavioural tasks on
distinct circuits are learned **in sequence** and the per-task accuracy is measured
after *every* task, so the full retention matrix is available rather than just the
endpoint.

The question this fire answers is deliberately the minimal one: **does it work at
all, and does it forget?**  A benchmark whose naive baseline does not forget has no
problem for continual learning to solve; a benchmark whose tasks are not learnable has
no signal.  Both have to be checked before any method comparison means anything.

    python -m experiments.e8_rate_network --circuit-size 800 --iters 400
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from clfly.connectome import annotate, circuits, graph
from clfly.network import tasks as rate_tasks
from clfly.network.model import RateConfig, build_net

REPO_ROOT = Path(__file__).resolve().parents[1]


def train_task(model, heads, suite, k: int, iters: int, lr: float, batch: int,
               seed: int, ewc=None, replay: list | None = None,
               replay_batch: int = 16):
    """Train on task ``k``; optionally with an EWC penalty or a replay buffer.

    ``heads`` is the list of per-task decoders — one per task, since the read-out
    populations differ in size and a shared head would have to be resized per task.
    Only the current task's head and the shared recurrent body are trained.

    ``ewc`` is ``(fisher, anchor, lam)`` with a per-parameter diagonal Fisher over the
    masked recurrent weights, and ``replay`` a list of ``(u, y, task_index)`` from
    earlier tasks.  Both live here rather than in separate scripts so the *training
    procedure* is identical across methods and a difference cannot come from the loop.
    """
    import torch

    task = suite[k]
    readout = heads[k]
    rng = np.random.default_rng(seed)
    params = [model.theta, model.bias] + list(readout.parameters())
    opt = torch.optim.Adam(params, lr=lr)
    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    lossf = torch.nn.CrossEntropyLoss()

    for step in range(iters):
        idx = rng.integers(0, len(Y), size=min(batch, len(Y)))
        traj = model(U[idx], None)
        x = traj[:, -1, :][:, task.readout_neurons]
        loss = lossf(readout(x), Y[idx])

        if ewc is not None:
            fisher, anchor, lam = ewc
            loss = loss + 0.5 * lam * torch.sum(
                torch.from_numpy(fisher).float() * (model.theta - anchor) ** 2)
        if replay:
            n = min(replay_batch, len(replay))
            pick = rng.integers(0, len(replay), size=n)
            ru = torch.from_numpy(np.stack([replay[i][0] for i in pick])).float()
            ry = torch.from_numpy(np.array([replay[i][1] for i in pick])).long()
            rtask = [replay[i][2] for i in pick]
            rtraj = model(ru, None)
            rloss = 0.0
            # Each replayed sample is scored through *its own* task head, because the
            # heads are task-specific: using the current head would be asking it to
            # classify an old task's labels.
            for t_idx in set(rtask):
                sel = torch.tensor([i for i, t in enumerate(rtask) if t == t_idx])
                heads[t_idx](rtraj[sel, -1, :][:, suite[t_idx].readout_neurons])
                rloss = rloss + lossf(
                    heads[t_idx](rtraj[sel, -1, :][:, suite[t_idx].readout_neurons]),
                    ry[sel])
            loss = loss + rloss / max(1, len(set(rtask)))

        opt.zero_grad()
        loss.backward()
        opt.step()
    return float(loss.item())


def evaluate(model, readout, task) -> float:
    """Held-out accuracy at the final timestep."""
    import torch

    with torch.no_grad():
        U = torch.from_numpy(task.u_test).float()
        Y = torch.from_numpy(task.y_test).long()
        traj = model(U, None)
        logits = readout(traj[:, -1, :][:, task.readout_neurons])
        return float((logits.argmax(dim=1) == Y).float().mean())


def diagonal_fisher(model, readout, task, n_batches: int = 8, seed: int = 0) -> np.ndarray:
    """Diagonal Fisher over the masked recurrent weights.

    Accumulated over the task's own training data after training on it, which is the
    EWC construction.  Only ``theta`` is differentiated: the decoder is task-specific
    and the bias is shared, and letting either into the Fisher would blur the object
    the project is studying.
    """
    import torch

    rng = np.random.default_rng(seed)
    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    fisher = torch.zeros_like(model.theta)
    lossf = torch.nn.CrossEntropyLoss()
    for _ in range(n_batches):
        idx = rng.integers(0, len(Y), size=min(32, len(Y)))
        traj = model(U[idx], None)
        logits = readout(traj[:, -1, :][:, task.readout_neurons])
        loss = lossf(logits, Y[idx])
        model.zero_grad()
        loss.backward()
        if model.theta.grad is not None:
            fisher += model.theta.grad.detach() ** 2
    model.zero_grad()
    return (fisher / n_batches).cpu().numpy()


def run_method(conn_net, suite, method: str, args, seed: int) -> dict:
    """Train sequentially and record the full retention matrix.

    ``R[k, j]`` = accuracy on task ``j`` after training through task ``k``, so the
    diagonal is "how well did it learn" and the lower-left block is retention.

    The decoders are **per task**, which makes this a task-incremental setup: the
    shared recurrent body is retrained on every task and is where forgetting happens,
    while a decoder belonging to a finished task is never touched again.  That is the
    standard first benchmark, and it isolates the body's forgetting from the head's.
    """
    import torch

    model = conn_net.torch_model()
    heads = [torch.nn.Linear(t.n_readout, t.n_classes) for t in suite]
    fisher = None
    anchor = None
    replay: list = []
    T = len(suite)
    R = np.full((T, T), np.nan)
    losses = []

    for k, task in enumerate(suite):
        losses.append(train_task(model, heads, suite, k, iters=args.iters, lr=args.lr,
                                 batch=args.batch, seed=seed + k,
                                 ewc=(fisher, anchor, args.lam) if (
                                     method == "ewc" and fisher is not None) else None,
                                 replay=(replay if method == "replay" else None)))
        for j in range(k + 1):
            R[k, j] = evaluate(model, heads[j], suite[j])

        if method == "ewc":
            f = diagonal_fisher(model, heads[k], task, seed=seed + k)
            fisher = f if fisher is None else fisher + f
            anchor = model.theta.detach().clone()
        if method == "replay":
            n = min(args.replay_per_task, len(task.y_train))
            idx = np.random.default_rng(seed + k).choice(len(task.y_train),
                                                              size=n, replace=False)
            replay.extend((task.u_train[i], int(task.y_train[i]), k) for i in idx)

    T = len(suite)
    final = R[T - 1]
    per_task_forgetting = [float(np.nanmax(R[: j + 1, j]) - R[T - 1, j])
                           for j in range(T)]
    # The last task cannot be forgotten yet, so it is excluded from the mean; it is
    # reported separately as "how well did it end up learning the final task".
    return {
        "method": method,
        "retention": R.tolist(),
        "final_accuracy": float(np.nanmean(final)),
        "forgetting_per_task": per_task_forgetting,
        "mean_forgetting": float(np.mean(per_task_forgetting[:-1])) if T > 1 else 0.0,
        "learned": [float(R[j, j]) for j in range(T)],
        "final_per_task": [float(x) for x in final],
        "losses": losses,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--circuit-size", type=int, default=800)
    p.add_argument("--iters", type=int, default=400)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lam", type=float, default=1.0, help="EWC strength")
    p.add_argument("--replay-per-task", type=int, default=16)
    p.add_argument("--methods", default="naive,ewc,replay")
    p.add_argument("--train", type=int, default=96)
    p.add_argument("--test", type=int, default=48)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--repeats", type=int, default=1,
                   help="independent training runs per method, for a standard error")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    suite = rate_tasks.make_suite(circ, n_train=args.train, n_test=args.test)
    net = build_net(circ, RateConfig(seed=args.seed0))

    print(f"circuit {circ.name}: {circ.n_neurons} neurons, "
          f"{net.n_params:,} trainable recurrent weights")
    for t in suite:
        print(f"  task {t.name:16} in={t.n_input:5} readout={t.n_readout:5} "
              f"classes={t.n_classes}")

    out = {"config": vars(args), "circuit": circ.name, "n_params": net.n_params,
           "tasks": [t.summary() for t in suite], "methods": {}}
    for method in args.methods.split(","):
        reps = [run_method(net, suite, method, args, seed=args.seed0 + 100 * r)
                for r in range(args.repeats)]
        agg = {
            "mean_forgetting": float(np.mean([x["mean_forgetting"] for x in reps])),
            "forgetting_sem": float(np.std([x["mean_forgetting"] for x in reps],
                                           ddof=1) / np.sqrt(len(reps))) if len(reps) > 1 else 0.0,
            "final_accuracy": float(np.mean([x["final_accuracy"] for x in reps])),
            "final_sem": float(np.std([x["final_accuracy"] for x in reps],
                                      ddof=1) / np.sqrt(len(reps))) if len(reps) > 1 else 0.0,
            "learned": [float(x) for x in np.mean([r["learned"] for r in reps], axis=0)],
            "forgetting_per_task": [float(x) for x in
                                    np.mean([r["forgetting_per_task"] for r in reps], axis=0)],
            "replicates": reps,
        }
        out["methods"][method] = agg
        print(f"\n  --- {method} (n={args.repeats}) ---")
        print(f"    retention after the final task: "
              f"{['%.3f' % v for v in np.mean([r['retention'][-1] for r in reps], axis=0)]}")
        print(f"    learned (diagonal):  {['%.3f' % x for x in agg['learned']]}")
        print(f"    forgetting per task: {['%+.3f' % x for x in agg['forgetting_per_task']]}")
        print(f"    -> final accuracy {agg['final_accuracy']:.3f} ± {agg['final_sem']:.3f},  "
              f"mean forgetting {agg['mean_forgetting']:+.3f} ± {agg['forgetting_sem']:.3f}")
    out["timing_s"] = time.time() - t0

    print(f"\n  chance = {1.0 / suite[0].n_classes:.3f}   ({time.time()-t0:.0f}s)")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(out, indent=1, default=str))
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
