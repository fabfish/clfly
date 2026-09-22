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

from clfly.bench.artifacts import write_json
from clfly.connectome import annotate, circuits, graph
from clfly.network import tasks as rate_tasks
from clfly.network.fisher import SynapsePartition
from clfly.network.model import RateConfig, build_net

REPO_ROOT = Path(__file__).resolve().parents[1]


def train_task(model, heads, suite, k: int, iters: int, lr: float, batch: int,
               seed: int, ewc=None, block_ewc=None, replay: list | None = None,
               replay_batch: int = 16, shared: bool = False,
               frozen_body: bool = False):
    """Train on task ``k``; optionally with an EWC penalty or a replay buffer.

    ``heads`` is the list of decoders: one per task in the task-incremental default (the
    read-out populations differ in size), or a single shared decoder over the whole
    circuit state in the class-incremental mode, where every task is trained through
    ``heads[0]`` and only the current task's class logits receive gradient.

    ``ewc`` is ``(fisher, anchor, lam)`` with a per-parameter diagonal Fisher over the
    masked recurrent weights, and ``replay`` a list of ``(u, y, task_index)`` from
    earlier tasks.  Both live here rather than in separate scripts so the *training
    procedure* is identical across methods and a difference cannot come from the loop.
    """
    import torch

    task = suite[k]
    readout = heads[0] if shared else heads[k]
    rng = np.random.default_rng(seed)
    # `frozen_body` is a diagnostic, not a method: it asks whether the plastic recurrent
    # weights are being used at all. If a benchmark's accuracy is the same with the body
    # frozen, it is measuring the decoder rather than the connectome.
    if frozen_body:
        params = list(readout.parameters())
    else:
        params = [model.theta, model.bias] + list(readout.parameters())
    opt = torch.optim.Adam(params, lr=lr)
    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    lossf = torch.nn.CrossEntropyLoss()

    for step in range(iters):
        idx = rng.integers(0, len(Y), size=min(batch, len(Y)))
        traj = model(U[idx], None)
        x = traj[:, -1, :][:, task.readout_neurons]
        loss = lossf(_logits(readout, x, task, shared), Y[idx])

        if ewc is not None:
            fisher, anchor, lam = ewc
            loss = loss + 0.5 * lam * torch.sum(
                torch.from_numpy(fisher).float() * (model.theta - anchor) ** 2)
        if block_ewc is not None:
            # already bound to the blocks, anchor and lambda -- see `make_penalty`
            loss = loss + block_ewc(model.theta)
        if replay:
            n = min(replay_batch, len(replay))
            pick = rng.integers(0, len(replay), size=n)
            ru = torch.from_numpy(np.stack([replay[i][0] for i in pick])).float()
            ry = torch.from_numpy(np.array([replay[i][1] for i in pick])).long()
            rtask = [replay[i][2] for i in pick]
            rtraj = model(ru, None)
            rloss = 0.0
            # Each replayed sample is scored through its own task's logits: with per-task
            # heads that means its own decoder, and with a shared head its own class
            # slice.  Either way the old labels are interpreted in the space they were
            # trained in.
            for t_idx in set(rtask):
                sel = torch.tensor([i for i, t in enumerate(rtask) if t == t_idx])
                tk = suite[t_idx]
                head = heads[0] if shared else heads[t_idx]
                rloss = rloss + lossf(
                    _logits(head, rtraj[sel, -1, :][:, tk.readout_neurons], tk, shared),
                    ry[sel])
            loss = loss + rloss / max(1, len(set(rtask)))

        opt.zero_grad()
        loss.backward()
        opt.step()
    return float(loss.item())


def _logits(readout, x, task, shared: bool):
    """Task logits, from a shared head or a task's own.

    With a shared head the logits are ``(total_classes,)`` and the task's own classes
    occupy a contiguous slice, so the loss is taken over that slice and the labels stay
    local.  This is the standard class-incremental protocol: the learner is never shown
    a future task's classes.
    """
    out = readout(x)
    if not shared:
        return out
    return out[:, task.class_offset: task.class_offset + task.n_classes]


def evaluate(model, readout, task, shared: bool = False) -> float:
    """Held-out accuracy at the final timestep."""
    import torch

    with torch.no_grad():
        U = torch.from_numpy(task.u_test).float()
        Y = torch.from_numpy(task.y_test).long()
        traj = model(U, None)
        logits = _logits(readout, traj[:, -1, :][:, task.readout_neurons], task, shared)
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


def block_fisher(model, heads, suite, k: int, part, n_batches: int = 8,
                 seed: int = 0, shared: bool = False) -> np.ndarray:
    """Block-diagonal Fisher over a synapse partition, accumulated on task ``k``.

    The within-group second moments ``E[g_g g_g^T]``, stored densely per group.  This is
    the network analogue of ``Partition.project`` keeping within-group covariance: it
    retains strictly more than the diagonal does, and only the *between*-group
    structure is discarded.
    """
    import torch

    task = suite[k]
    readout = heads[0] if shared else heads[k]
    rng = np.random.default_rng(seed)
    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    lossf = torch.nn.CrossEntropyLoss()
    blocks = part.new_blocks()
    for _ in range(n_batches):
        idx = rng.integers(0, len(Y), size=min(32, len(Y)))
        traj = model(U[idx], None)
        loss = lossf(_logits(readout, traj[:, -1, :][:, task.readout_neurons], task, shared),
                     Y[idx])
        model.zero_grad()
        loss.backward()
        if model.theta.grad is not None:
            part.accumulate(blocks, model.theta.grad.detach().cpu().numpy().astype(np.float64))
    model.zero_grad()
    return blocks / n_batches


def run_method(conn_net, suite, method: str, args, seed: int,
               partitions: dict | None = None) -> dict:
    """Train sequentially and record the full retention matrix.

    ``R[k, j]`` = accuracy on task ``j`` after training through task ``k``, so the
    diagonal is "how well did it learn" and the lower-left block is retention.

    The decoders are **per task**, which makes this a task-incremental setup: the
    shared recurrent body is retrained on every task and is where forgetting happens,
    while a decoder belonging to a finished task is never touched again.  That is the
    standard first benchmark, and it isolates the body's forgetting from the head's.
    """
    import torch

    # Seed torch's *global* RNG.  The recurrent weights come from the connectome and
    # the bias is zeros, both deterministic -- but `nn.Linear` initialises from the
    # global torch RNG, which is otherwise seeded from entropy at process start.  That
    # made the whole benchmark non-reproducible: identical commands gave different
    # readout initialisations, and therefore different forgetting, with no way to tell
    # that from a real effect.  The earlier `eigs`-with-a-random-start bug was the same
    # class of failure in a different library.
    torch.manual_seed(seed)

    model = conn_net.torch_model()
    shared = bool(getattr(args, "shared_head", False))
    if shared:
        total = sum(t.n_classes for t in suite)
        heads = [torch.nn.Linear(suite[0].n_readout, total)]
    else:
        heads = [torch.nn.Linear(t.n_readout, t.n_classes) for t in suite]
    fisher = None
    anchor = None
    blocks = None
    anchor_b = None
    part = None
    if partitions:
        key = "rand" if method.endswith("-rand") else "bio"
        part = partitions[key]
    replay: list = []
    T = len(suite)
    R = np.full((T, T), np.nan)
    losses = []

    for k, task in enumerate(suite):
        # Bind the block penalty ONCE per task, not once per training step. The Fisher and
        # the anchor are constants while a task is trained; converting them inside the step
        # loop is what made a coarse partition take hours rather than minutes.
        block_pen = None
        if method.startswith("ewc-block") and blocks is not None:
            block_pen = part.make_penalty(blocks, anchor_b, model.theta, args.lam, torch)
        losses.append(train_task(
            model, heads, suite, k, iters=args.iters, lr=args.lr,
            batch=args.batch, seed=seed + k,
            ewc=(fisher, anchor, args.lam) if (
                method == "ewc" and fisher is not None) else None,
            block_ewc=block_pen,
            replay=(replay if method == "replay" else None), shared=shared,
            replay_batch=args.replay_batch,
            frozen_body=args.frozen_body))
        for j in range(k + 1):
            R[k, j] = evaluate(model, heads[0] if shared else heads[j], suite[j], shared)

        if method == "ewc":
            f = diagonal_fisher(model, heads[0] if shared else heads[k], task,
                                n_batches=args.fisher_batches, seed=seed + k)
            # Normalise the diagonal the same way `trace_normalise` normalises the
            # blocks.  Without this the two families sit at different effective
            # strengths for the same lambda -- the block Fishers are rescaled to unit
            # mean weight and the diagonal is not -- so comparing them would compare
            # granularity against penalty strength.  Normalising per task also keeps
            # tasks equally weighted as the Fisher accumulates.
            if args.normalise_fisher and f.mean() > 0:
                f = f / f.mean()
            fisher = f if fisher is None else fisher + f
            anchor = model.theta.detach().clone()
        if method.startswith("ewc-block"):
            b = block_fisher(model, heads, suite, k, part,
                             n_batches=args.fisher_batches, seed=seed + k, shared=shared)
            if args.normalise_fisher:
                b = part.trace_normalise(b)
            blocks = b if blocks is None else blocks + b
            anchor_b = model.theta.detach().clone()
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
    p.add_argument("--replay-per-task", type=int, default=16,
                   help="replay pool size per finished task -- the memory budget")
    p.add_argument("--replay-batch", type=int, default=16,
                   help="replayed samples mixed into each training step; distinct "
                        "from the pool size, and the two are confounded if only one "
                        "is swept")
    p.add_argument("--methods", default="naive,ewc,replay")
    p.add_argument("--train", type=int, default=96)
    p.add_argument("--test", type=int, default=48)
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--input-overlap", type=float, default=None,
                   help="drive every task into input populations with this exact "
                        "uniform overlap, instead of the default suite's disjoint "
                        "circuits; the arm that tests whether input-level separation "
                        "is why forgetting is mild")
    p.add_argument("--noise", type=float, default=1.0, help="stimulus noise")
    p.add_argument("--classes", type=int, default=4, help="classes per task")
    p.add_argument("--readout-size", type=int, default=0,
                   help="restrict the shared read-out to this many neurons; 0 keeps "
                        "the whole state, which lets a linear decoder solve the tasks "
                        "without the recurrent weights changing at all")
    p.add_argument("--frozen-body", action="store_true",
                   help="diagnostic: train only the decoder, to test whether the "
                        "plastic recurrent weights are used at all")
    p.add_argument("--support", type=int, default=80,
                   help="input population size for the overlap suite")
    p.add_argument("--shared-head", action="store_true",
                   help="class-incremental: one decoder for every task read out from "
                        "the whole circuit, with disjoint class ranges")
    p.add_argument("--basis", default="cell_class",
                   help="annotation column for the synapse partition")
    p.add_argument("--fisher-batches", type=int, default=8,
                   help="minibatches used to estimate the Fisher; the block Fisher has "
                        "5.3e7 entries to fill against the diagonal's 2.7e4, so this "
                        "is the knob that tests whether its failure is estimation noise")
    p.add_argument("--normalise-fisher", action="store_true", default=True,
                   help="rescale block Fishers so lambda is comparable across "
                        "partitions; without it coarse partitions get a larger "
                        "penalty at the same lambda")
    p.add_argument("--pool-below", type=int, default=0,
                   help="merge annotation labels appearing in fewer than N neurons")
    p.add_argument("--pool-buckets", type=int, default=1,
                   help="split the merged sub-threshold labels over B groups instead of "
                        "one; bounds the block Fisher's storage, which is sum_g s_g^2 and "
                        "is otherwise dominated by a single (pooled x pooled) block")
    p.add_argument("--repeats", type=int, default=1,
                   help="independent training runs per method, for a standard error")
    p.add_argument("--json-out", type=Path, default=None)
    args = p.parse_args(argv)

    t0 = time.time()
    conn = graph.build()
    ann = annotate.load_annotations()
    circ = circuits.extract(conn, ann, hops=0, max_neurons=args.circuit_size)
    # A narrow read-out is what makes the plastic recurrent weights load-bearing; see
    # the docstring of `rate_tasks.make_suite`.  None keeps the whole state.
    rs = None
    if args.readout_size and args.readout_size < circ.n_neurons:
        rs = np.sort(np.random.default_rng(args.seed0).choice(
            circ.n_neurons, size=args.readout_size, replace=False))
    common = dict(n_train=args.train, n_test=args.test, noise=args.noise,
                  n_classes=args.classes)
    if args.input_overlap is None:
        suite = rate_tasks.make_suite(circ, shared_head=args.shared_head,
                                      readout_subset=rs, **common)
        suite_label = "default (disjoint circuits)"
    else:
        suite = rate_tasks.make_overlap_suite(
            circ, n_tasks=len(rate_tasks.SUITE_SPECS), support=args.support,
            overlap=args.input_overlap, shared_head=args.shared_head,
            readout_subset=rs, **common)
        suite_label = f"overlap={args.input_overlap:g}"
    net = build_net(circ, RateConfig(seed=args.seed0))

    # Synapse partitions for the block-EWC variants, plus the matched random control.
    partitions = None
    pre, post = net.synapse_endpoints()
    if any(m.startswith("ewc-block") for m in args.methods.split(",")):
        labels = circ.labels[args.basis]
        bio = SynapsePartition.from_labels(labels, pre, post, name=args.basis,
                                           pool_below=args.pool_below,
                                           pool_buckets=args.pool_buckets)
        partitions = {"bio": bio,
                      "rand": SynapsePartition.random_matched(
                          bio, np.random.default_rng(args.seed0))}
        print(f"  block partition ({args.basis}): {bio.n_groups} groups, "
              f"{bio.n_entries:,} block entries ({bio.describe()['block_gb']:.2f} GB), "
              f"constrained {bio.constrained_fraction():.4f}")

    print(f"circuit {circ.name}: {circ.n_neurons} neurons, suite: {suite_label}, "
          f"{net.n_params:,} trainable recurrent weights")
    for t in suite:
        print(f"  task {t.name:16} in={t.n_input:5} readout={t.n_readout:5} "
              f"classes={t.n_classes}")

    out = {"config": vars(args), "circuit": circ.name, "n_params": net.n_params,
           "tasks": [t.summary() for t in suite], "methods": {}}
    for method in args.methods.split(","):
        reps = [run_method(net, suite, method, args, seed=args.seed0 + 100 * r,
                           partitions=partitions)
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
        write_json(args.json_out, out)
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
