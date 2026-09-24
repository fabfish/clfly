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
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from clfly.bench.artifacts import write_json
from clfly.bench.control import evaluation_noise, paired_contrast
from clfly.connectome import annotate, circuits, graph
from clfly.network import tasks as rate_tasks
from clfly.network.fisher import SynapsePartition
from clfly.network.model import RateConfig, build_net

REPO_ROOT = Path(__file__).resolve().parents[1]


def train_task(model, heads, suite, k: int, iters: int, lr: float, batch: int,
               seed: int, ewc=None, block_ewc=None, replay: list | None = None,
               replay_batch: int = 16, shared: bool = False,
               frozen_body: bool = False, frozen_bias: bool = False):
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
    #
    # `frozen_bias` splits that question, because the body is two parameter sets with very
    # different status: 26,568 masked weights that ARE the connectome, and 800 per-neuron
    # offsets whose blocks carry no wiring semantics. Both are trained, and neither EWC
    # penalty covers the bias (`diagonal_fisher`'s docstring justifies that for the decoder
    # and not for the bias -- "the bias is shared" is equally true of `theta`, which IS
    # anchored). So a naive-vs-EWC contrast includes an unpenalised 800-parameter channel,
    # and this flag is what says whether that channel matters. Freezing it holds it at its
    # zero initialisation, which is the only value it has ever had before task 0.
    if frozen_body:
        params = list(readout.parameters())
    elif frozen_bias:
        params = [model.theta] + list(readout.parameters())
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
            fisher, anchor, lam = ewc[:3]
            loss = loss + 0.5 * lam * torch.sum(
                torch.from_numpy(fisher).float() * (model.theta - anchor) ** 2)
            # The bias's own anchor, when the caller has supplied one -- the channel no penalty in this project
            # used to cover, and the one `e137` measured the adaptation relocating INTO. The Fisher is
            # unit-mean-normalised (`normalise_fisher`) and then scaled by the caller, so that the *share* of the
            # penalty's mass the bias carries is an explicit number rather than an accident of the raw Fisher's
            # magnitude.
            if len(ewc) > 3 and ewc[3] is not None:
                fisher_b, anchor_b, bias_scale = ewc[3]
                if bias_scale:
                    loss = loss + 0.5 * lam * bias_scale * torch.sum(
                        torch.from_numpy(fisher_b).float() * (model.bias - anchor_b) ** 2)
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


def environment() -> dict:
    """What the numbers were measured *in*, recorded in the artifact rather than inferred later.

    Rule 21 is the project's standing complaint that the torch path is deterministic given an environment and
    not across environments, and that the environment is **recorded nowhere** -- so a missing artifact cannot
    be restored across one, and a two-vector difference among runs of one configuration cannot be attributed.
    This session paid for that directly: the question "is the thread count the variable?" needed a 58-minute
    `OMP_NUM_THREADS=1` run at a full five-replicate sweep, and the answer was *no*, which a recorded
    environment would have shown for free on the runs already on disk.

    Torch's own thread count is read *after* the first tensor operation, because `torch.get_num_threads()`
    reflects what the runtime settled on rather than what was requested; `OMP_NUM_THREADS` and its two
    siblings are recorded as strings exactly as the process saw them, including "unset", because "unset" is
    the value most of this project's artifacts were produced under.
    """
    import os
    import platform

    import torch

    return {
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS", "unset"),
        "mkl_num_threads": os.environ.get("MKL_NUM_THREADS", "unset"),
        "torch_num_threads": int(torch.get_num_threads()),
        "torch_num_interop_threads": int(torch.get_num_interop_threads()),
        "torch_version": torch.__version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
        # A **calibration**: one fixed matmul, timed, so that two artifacts' costs can be compared in the same
        # units. The costs already are environment-shaped (rule 21, and §9 says so about the figures themselves)
        # and today's per-replicate costs span **44.6 s to 132 s** across sixteen artifacts of this session with
        # nothing in the record to attribute the 3.0× to -- the thread counts are recorded and the *load* is not,
        # and no artifact says how fast the machine was at that moment. A calibration is the honest instrument:
        # it measures the machine rather than asking the run to describe its own queue.
        "calibration_matmul_s": calibration(),
    }


def code_revision() -> dict:
    """Which revision of the code produced the artifact, recorded beside the environment.

    Rule 45: `config` and `environment` are two of the three things two runs of one command can differ in, and the
    third is the code itself -- so a difference between two executions is only attributable if the artifact says
    which revision it ran. The corpus this session read had no such field, and the price is on disk: seven
    repeated runs of two configurations from 09-23 afternoon differ on `replay` and the two block arms, the two
    *later* executions among them agree with each other to the last digit, no commit touching `experiments/` or
    `clfly/` falls in the window, the thread knob is excluded because `naive` did not move (and a thread
    difference does move it) -- and **nothing can say which code produced the earlier ones**, so an afternoon's
    worth of working tree is unrecoverable while being the most likely cause.

    `dirty` is the field that carries the force: a run launched from an uncommitted tree records the commit it was
    *based* on, which is not the code that ran. Both are reported, and neither is guessed -- a checkout without
    `git` gets `"unknown"` with the exception's name rather than a fabricated hash, because a provenance field
    that invents a value is worse than one that is absent.
    """
    import subprocess
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]

    def git(*argv: str) -> str:
        return subprocess.run(["git", "-C", str(root), *argv], capture_output=True, text=True,
                              timeout=20, check=True).stdout

    try:
        porcelain = git("status", "--porcelain")
        revision = {"commit": git("rev-parse", "HEAD").strip(), "dirty": bool(porcelain.strip())}
        if revision["dirty"]:
            # the paths that differ, not their contents: enough to see whether a runner was edited mid-run
            revision["dirty_paths"] = sorted(p for p in porcelain.split("\n") if p)[:20]
        return revision
    except Exception as exc:                                   # noqa: BLE001  (any failure is "unknown")
        return {"commit": "unknown", "dirty": None, "error": type(exc).__name__}


def calibration(side: int = 512, reps: int = 50) -> float:
    """Time a fixed matmul, and report the **minimum** of the repetitions.

    A cheaper, portable proxy for "how fast was this machine just now". Not a load count: the runner cannot see
    what else is running. It is a rate, so a 3× slower artifact can be compared against a 3× slower calibration
    and the two costs become commensurable -- which is what §9 means by quoting a cost beside the environment it
    was measured in.

    **The minimum rather than the mean, and the sizes are measured rather than chosen.** The first version of
    this (256², 8 reps, mean) spanned **2.75× within one process** over five calls -- useless as a rate, since it
    cannot separate a 2× slower machine from its own noise. Contention only ever *adds* time, so the minimum is
    the least-contaminated estimate of the machine's speed, and it is measurably better: five calls give a
    max/min of **1.59** at 256²/8 (mean), **1.26** at 256²/8 (min), **1.14** at 512²/25 (min) and **1.08** at
    512²/50 (min). The default is the last of those, at a cost of about 20 ms.
    """
    import time

    import torch

    a = torch.randn(side, side)
    b = torch.randn(side, side)
    a @ b                                        # warm-up, excluded from the timing
    fastest = float("inf")
    for _ in range(reps):
        t0 = time.perf_counter()
        a @ b
        fastest = min(fastest, time.perf_counter() - t0)
    return round(fastest, 6)


def full_split_loss(model, readout, task, shared: bool = False, split: str = "train") -> float:
    """Mean cross-entropy over a whole split, at the current weights.

    The honest counterpart of the minibatch loss the training loop returns: **the last step's loss on 32 of the
    task's 96 training samples is a sample, and whether it represents the task is a question rather than an
    assumption.** Measured at read-out 128, the full training-set loss at the end of a task is **0.00179 /
    0.00141 / 0.00124** across three replicates while the last minibatch's is **0.00158** — a ratio of about
    1.1 — so at this configuration the minibatch *is* representative and a claim about what the model has
    fitted can be read off it. That is the second instrument behind `e121`'s interpolation result.

    (This note said the full-set loss was "0.077–0.159 ... a factor of 49 to 101" higher, which was `e122`'s
    first run printing a *zero-bias* body — the recurrent bias is trained but was not among the saved
    parameters, so the chord was evaluating a configuration the benchmark never produces. The correction is what
    `e122`'s endpoint control now checks automatically: the chord's ends must reproduce these numbers exactly.)
    """
    import torch

    U = torch.from_numpy(getattr(task, f"u_{split}")).float()
    Y = torch.from_numpy(getattr(task, f"y_{split}")).long()
    with torch.no_grad():
        traj = model(U, None)
        logits = _logits(readout, traj[:, -1, :][:, task.readout_neurons], task, shared)
        return float(torch.nn.functional.cross_entropy(logits, Y).item())


def relative_drift(before: np.ndarray, after: np.ndarray) -> float:
    """``||after - before|| / ||before||`` -- how far a weight vector moved, in units of its own size.

    Every network-line claim in this paper is about *accuracy*, and none of them has measured how far the
    recurrent body actually moves between tasks. That is the quantity the forgetting has to come from, and it
    is cheap to record: the body is 26,568 numbers and the drift is one subtraction. Relative rather than
    absolute, because the connectome's weight scale is a property of the circuit rather than of the training,
    and because a drift of 0.7 in units of ``||theta||`` is comparable across configurations while an absolute
    one is not.
    """
    before = np.asarray(before, dtype=np.float64)
    after = np.asarray(after, dtype=np.float64)
    scale = float(np.linalg.norm(before))
    delta = float(np.linalg.norm(after - before))
    return delta / scale if scale else float("nan")


def task_grad(model, readout, task, shared: bool = False):
    """The task's mean loss and its gradient with respect to the body, at the current weights.

    The gradient is of the *task's own* training loss, which is the object whose change a later task's
    displacement first-order predicts. Returned flat and in float64, because the inner products it feeds are
    differences between vectors of 26,568 numbers whose individual magnitudes are small.
    """
    import torch

    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    traj = model(U, None)
    logits = _logits(readout, traj[:, -1, :][:, task.readout_neurons], task, shared)
    loss = torch.nn.functional.cross_entropy(logits, Y)
    model.zero_grad()
    loss.backward()
    grad = (model.theta.grad.detach().cpu().numpy().astype(np.float64).copy()
            if model.theta.grad is not None else np.zeros_like(model.theta.detach().cpu().numpy()))
    model.zero_grad()
    return grad, float(loss.item())


def whole_body_grad(model, readout, task, shared: bool = False):
    """The task's gradient with respect to **both** halves of the body, at the current weights.

    `task_grad` reaches `theta` alone, and `e139` measured what that costs: at forty paired seeds diagonal EWC
    cuts the first-order interference term built from `theta` by **98%** (**10.34σ**) while its forgetting moves
    **1.21σ** — so an instrument that reads one channel cannot see the effect when `e125` showed the effect lives
    mostly in the other. This returns the bias's gradient beside the weights', so that the same one-line account
    can be evaluated over the body the perturbation actually moved.
    """
    import torch

    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    traj = model(U, None)
    logits = _logits(readout, traj[:, -1, :][:, task.readout_neurons], task, shared)
    loss = torch.nn.functional.cross_entropy(logits, Y)
    model.zero_grad()
    loss.backward()

    def flat(param):
        g = param.grad
        return (g.detach().cpu().numpy().astype(np.float64).copy() if g is not None
                else np.zeros(param.detach().cpu().numpy().shape))

    g_theta, g_bias = flat(model.theta), flat(model.bias)
    model.zero_grad()
    return g_theta, g_bias


def first_order_damage(grad: np.ndarray, displacement: np.ndarray) -> dict:
    """``<grad, displacement>`` and the two magnitudes it is the product of.

    This is the interference account's prediction in its one-line form: the change in a task's loss caused by
    moving the body along a displacement, to first order. **Reported with its factors rather than alone**,
    because `e107` showed the two candidate explanations of network forgetting -- how far the body moved, and
    how much the task needed it -- are both monotone in the read-out and neither orders the forgetting. A
    first-order term that orders it could be doing so through either factor, and a term that does not cannot be
    rescued by one of them, so the magnitudes and the cosine are stored beside the product.
    """
    grad = np.asarray(grad, dtype=np.float64)
    displacement = np.asarray(displacement, dtype=np.float64)
    g_norm = float(np.linalg.norm(grad))
    d_norm = float(np.linalg.norm(displacement))
    inner = float(grad @ displacement)
    cosine = inner / (g_norm * d_norm) if g_norm and d_norm else 0.0
    return {"first_order": inner, "cosine": cosine, "grad_norm": g_norm, "disp_norm": d_norm}


def directional_curvature(model, theta0, readout, task, direction: np.ndarray,
                          shared: bool = False, eps: float | None = None) -> dict:
    """``dᵀHd`` and the Rayleigh quotient ``dᵀHd / ‖d‖²`` along ``direction``.

    The *second*-order term of the interference account, and the reason it is the natural next instrument is
    `e108`'s own result: the first-order term is nearly **orthogonal** to the loss direction (cosines
    +0.003 to +0.048) and yet the earlier task forgets 0.06–0.08 of accuracy, which is what a **second**-order
    effect looks like -- and a quadratic form is **positive by construction** for a positive-semidefinite
    Hessian, so it cannot get the sign wrong where the first-order term did.

    **Both the product and the quotient are returned, because they answer different questions.** ``quad`` is
    linear in the directional curvature and quadratic in the displacement, so it inherits the read-out
    monotonicity that the displacement, the load-bearing gap and the first-order term all share. The
    **Rayleigh quotient divides the magnitude out** and is therefore the first candidate in this line that is a
    property of the *direction* rather than of how far the body moved -- which is what `e108` said the next
    candidate had to be.

    ``eps is None`` uses an **exact double backward** (``autograd.grad`` of ``gradient·d``), which is the
    default because the first version of this function was a central finite difference and **it was not
    converged**: at the same weights it returned `8.51e-01` at a step of `1e-3‖θ‖` and `1.71e-01` at `1e-2‖θ‖`.
    A finite difference whose two steps disagree by a factor of five has not measured anything, so the step is
    kept as an argument only so that the two can be compared -- and that comparison is what the caller should
    report beside the exact value.
    """
    import torch

    theta = model.theta
    direction = np.asarray(direction, dtype=np.float64)
    d_norm = float(np.linalg.norm(direction))
    if not d_norm:
        return {"quad": 0.0, "curvature": 0.0, "d_norm": 0.0, "loss": float("nan"), "method": "trivial"}

    d_t = torch.from_numpy(direction.astype(np.float32)).to(theta.device)
    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    traj = model(U, None)
    logits = _logits(readout, traj[:, -1, :][:, task.readout_neurons], task, shared)
    loss = torch.nn.functional.cross_entropy(logits, Y)
    model.zero_grad()
    (grad,) = torch.autograd.grad(loss, theta, create_graph=True)
    if eps is None:
        (hessian_d,) = torch.autograd.grad((grad * d_t).sum(), theta, retain_graph=False)
        quad = float((d_t * hessian_d).detach().cpu().sum())
        method = "double backward"
    else:
        magnitude = float(np.linalg.norm(np.asarray(theta0, dtype=np.float64)))
        step = eps * magnitude / d_norm
        step_vec = (step * d_t).detach()
        with torch.no_grad():
            theta.add_(step_vec)
        g_plus, _ = task_grad(model, readout, task, shared)
        with torch.no_grad():
            theta.sub_(2.0 * step_vec)
        g_minus, _ = task_grad(model, readout, task, shared)
        with torch.no_grad():
            theta.add_(step_vec)                          # restore, exactly
        quad = float(direction @ ((g_plus - g_minus) / (2.0 * step)))
        method = f"central difference, eps={eps:g}"
    model.zero_grad()
    return {"quad": quad, "curvature": quad / (d_norm * d_norm), "d_norm": d_norm,
            "loss": float(loss.item()), "method": method}


def evaluate(model, readout, task, shared: bool = False) -> float:
    """Held-out accuracy at the final timestep."""
    import torch

    with torch.no_grad():
        U = torch.from_numpy(task.u_test).float()
        Y = torch.from_numpy(task.y_test).long()
        traj = model(U, None)
        logits = _logits(readout, traj[:, -1, :][:, task.readout_neurons], task, shared)
        return float((logits.argmax(dim=1) == Y).float().mean())


def diagonal_fisher(model, readout, task, n_batches: int = 8, seed: int = 0,
                    with_bias: bool = False):
    """Diagonal Fisher over the masked recurrent weights, and optionally over the recurrent bias.

    Accumulated over the task's own training data after training on it, which is the EWC construction. **Only
    ``theta`` is differentiated by default**: the decoder is task-specific and letting it into the Fisher would
    blur the object the project is studying.

    **The bias is a different case and the original justification did not cover it.** *"The bias is shared"* is
    equally true of ``theta``, which **is** anchored — and `e125` measured that holding the 800 offsets at their
    initialisation removes **70%** of this configuration's forgetting while `e137` measured that diagonal EWC
    *relocates* 28% of the adaptation out of the weights and **into** them. So ``with_bias=True`` returns
    ``(fisher_theta, fisher_bias)`` and lets the caller decide what to do about a channel that carries most of
    the effect and is covered by nothing.
    """
    import torch

    rng = np.random.default_rng(seed)
    U = torch.from_numpy(task.u_train).float()
    Y = torch.from_numpy(task.y_train).long()
    fisher = torch.zeros_like(model.theta)
    fisher_b = torch.zeros_like(model.bias) if with_bias else None
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
        if with_bias and model.bias.grad is not None:
            fisher_b += model.bias.grad.detach() ** 2
    model.zero_grad()
    f = (fisher / n_batches).cpu().numpy()
    if not with_bias:
        return f
    return f, (fisher_b / n_batches).cpu().numpy()


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
    fisher_b_ = None                                       # the bias's accumulated Fisher, when `--anchor-bias`
    anchor_b = None
    blocks = None
    anchor_b = None
    part = None
    if partitions:
        key = "rand" if method.endswith("-rand") else "bio"
        part = partitions[key]
    replay: list = []
    T = len(suite)
    R = np.full((T, T), np.nan)
    L = np.full((T, T), np.nan)                            # the retention matrix in LOSS, not accuracy
    losses = []
    drifts = []                                            # ||theta after - before|| / ||before|| per task
    bias_norms = []                                        # the bias's absolute movement, which has no relative form
    full_train_losses = []                                 # mean loss over the task's whole train split
    decoder_states = []                                    # the decoders after each task
    thetas = []                                            # the body after each task, for the interference terms
    biases = []                                             # the body's recurrent bias after each task (see save block)

    theta_initial = model.theta.detach().cpu().numpy().copy()

    #: the penalty's inputs **as they stood when each task was trained** -- recorded at the top of the loop body,
    #: which is exactly where the penalty for that task is defined. Task 0 has none (`ewc` is `None` until a
    #: Fisher exists), and the entries are stored as empty arrays so a replay knows that.
    stored: list | None = None
    # `getattr` rather than attribute access: a caller that builds its own `Namespace` (the tests do, and
    # `e122`'s geometry line did) knows nothing about a flag added later, and the project's convention is that a
    # new flag must not break such a caller.
    if getattr(args, "fisher_from", None) is not None:
        if str(args.methods).startswith("ewc-block") or "ewc-block" in str(args.methods):
            raise SystemExit("--fisher-from is implemented for the diagonal penalty: a block run's inputs are a "
                             "partition and a trace-normalised matrix, so a stored diagonal would silently be a "
                             "different object")
        with np.load(args.fisher_from) as z:
            stored = [(z[f"f{k}"], z[f"a{k}"]) for k in range(len(suite))]
    fisher_trace: list = []

    for k, task in enumerate(suite):
        fisher_trace.append((fisher, anchor if fisher is not None else None))
        if stored is not None and stored[k][0].size:
            fisher, anchor = stored[k][0], torch.from_numpy(stored[k][1])
        # Bind the block penalty ONCE per task, not once per training step. The Fisher and
        # the anchor are constants while a task is trained; converting them inside the step
        # loop is what made a coarse partition take hours rather than minutes.
        block_pen = None
        if method.startswith("ewc-block") and blocks is not None:
            block_pen = part.make_penalty(blocks, anchor_b, model.theta, args.lam, torch)
        theta_before = model.theta.detach().cpu().numpy().copy()
        bias_before = model.bias.detach().cpu().numpy().copy()
        losses.append(train_task(
            model, heads, suite, k, iters=args.iters, lr=args.lr,
            batch=args.batch, seed=seed + k,
            ewc=((fisher, anchor, args.lam,
                  (fisher_b_, anchor_b, getattr(args, "anchor_bias", 1.0))
                  if getattr(args, "anchor_bias", None) is not None and fisher_b_ is not None else None)
                 if (method == "ewc" and fisher is not None) else None),
            block_ewc=block_pen,
            replay=(replay if method == "replay" else None), shared=shared,
            replay_batch=args.replay_batch,
            frozen_body=args.frozen_body, frozen_bias=getattr(args, "frozen_bias", False)))
        drifts.append(relative_drift(theta_before, model.theta.detach().cpu().numpy()))
        # The bias starts at exactly zero, so a relative drift is undefined (||before|| = 0) and the honest
        # record is absolute: how far it moved from zero, and how far it moved on this task. Recorded because
        # no EWC penalty in this project covers the bias, so how far it travels is how much of the forgetting
        # hangs off a channel the penalty does not see.
        bias_step = model.bias.detach().cpu().numpy() - bias_before
        bias_norms.append({"step": float(np.linalg.norm(bias_step)),
                           "from_zero": float(np.linalg.norm(model.bias.detach().cpu().numpy()))})
        full_train_losses.append(full_split_loss(
            model, heads[0] if shared else heads[k], task, shared, "train"))
        thetas.append(model.theta.detach().cpu().numpy().copy())
        biases.append(model.bias.detach().cpu().numpy().copy())
        # The decoders after this task, not only at the end: a chord through a mid-run body needs the decoder
        # that was in place then. Pairing a body from after task 0 with the head from after task 2 is not a
        # configuration the benchmark ever produces, and `e122`'s first version did exactly that.
        decoder_states.append([{q: getattr(h, q).detach().cpu().numpy().copy()
                                for q in ("weight", "bias")} for h in heads])
        for j in range(k + 1):
            readout_j = heads[0] if shared else heads[j]
            R[k, j] = evaluate(model, readout_j, suite[j], shared)
            # The same retention matrix in loss. `e122`'s geometry needs it: the loss along a chord through
            # checkpoint k has to be comparable to *something the runner recorded at checkpoint k*, and
            # `full_train_loss[j]` is recorded at checkpoint j -- a different body for every j < T-1. This is
            # the diagonal-and-below counterpart, so the chord's t = 0 endpoint is checkable on every task
            # rather than only on the last one. It is also the first loss-valued retention record in this
            # project; every retention figure before it is an accuracy.
            L[k, j] = full_split_loss(model, readout_j, suite[j], shared, "train")

        if method == "ewc":
            anchor_bias = getattr(args, "anchor_bias", None)
            got = diagonal_fisher(model, heads[0] if shared else heads[k], task,
                                  n_batches=args.fisher_batches, seed=seed + k,
                                  with_bias=anchor_bias is not None)
            if anchor_bias is None:
                f, fb = got, None
            else:
                f, fb = got
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
            if fb is not None:
                # Unit-mean normalised, exactly as the weights' Fisher is, so that the two are at comparable
                # per-parameter strengths and the *share* of the penalty's mass the bias carries is set by
                # `--anchor-bias` rather than by the raw Fishers' relative magnitudes -- which differ across
                # tasks and circuits and would make the flag's meaning configuration-dependent.
                if args.normalise_fisher and fb.mean() > 0:
                    fb = fb / fb.mean()
                fisher_b = fb if fisher_b_ is None else fisher_b_ + fb
                fisher_b_ = fisher_b
                anchor_b = model.bias.detach().clone()
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
    # The interference account, in its one-line form, for every pair the run makes available. Task j's
    # gradient at the *final* body against each task's own displacement: the last task has no forgetting to
    # explain, so the gradients are taken for j < T-1, and the displacement a task j actually experienced is
    # the cumulative one, theta_final - theta_after_j, which is stored as "cumulative" beside the per-task
    # products. A frozen body makes every displacement zero, so every term is zero -- the same control that
    # validates theta_drift.
    interference = []
    theta_final = model.theta.detach().cpu().numpy()
    bias_final = model.bias.detach().cpu().numpy()
    for j in range(max(T - 1, 0)):
        readout = heads[0] if shared else heads[j]
        grad, loss_j = task_grad(model, readout, suite[j], shared)
        # The first task's displacement is from the *initial* body, not from zero: the earlier version wrote
        # `np.zeros_like(theta_final)` for k = 0, which is the absolute weight vector rather than a
        # displacement. Nothing reported from e108 depended on it -- every quoted number came from the
        # `cumulative` term, which is `theta_final - thetas[j]` -- but the stored `per_task[0]` entries were
        # wrong and are now right.
        deltas = [thetas[k] - (thetas[k - 1] if k else theta_initial)
                  for k in range(T)]
        # The SAME one-line account over the whole body, because `e139` measured that the `theta`-only form is
        # cut by 98% under a penalty whose forgetting moves 1.21σ: the instrument reads one channel and the
        # effect lives mostly in the other (`e125`, `e137`). `bias_initial` is zero by construction, so the
        # displacement's bias half is just the bias itself at each checkpoint.
        g_theta, g_bias = whole_body_grad(model, readout, suite[j], shared)
        bias_deltas = [biases[k] - (biases[k - 1] if k else np.zeros_like(biases[0]))
                       for k in range(T)]
        interference.append({
            "task": j, "loss_at_final": loss_j,
            "per_task": [first_order_damage(grad, d) for d in deltas],
            "cumulative": first_order_damage(grad, theta_final - thetas[j]),
            "whole_body": {
                "per_task": [first_order_damage(g_theta, d)["first_order"]
                             + first_order_damage(g_bias, bd)["first_order"]
                             for d, bd in zip(deltas, bias_deltas)],
                "cumulative": float(g_theta @ (theta_final - thetas[j])
                                    + g_bias @ (bias_final - biases[j])),
                "theta_only_cumulative": float(g_theta @ (theta_final - thetas[j])),
                "bias_only_cumulative": float(g_bias @ (bias_final - biases[j])),
                "bias_grad_norm": float(np.linalg.norm(g_bias)),
                "bias_disp_norm": float(np.linalg.norm(bias_final - biases[j])),
            },
            # Second order: `quad` is a product (magnitude x curvature, so read-out-shaped) and `curvature`
            # is the Rayleigh quotient with the magnitude divided out (a direction quantity). The exact
            # double backward is the value; the two finite differences are the cross-check, because the first
            # version of this instrument reported them disagreeing by a factor of five.
            "second_order": {
                **{"exact": directional_curvature(model, theta_initial, readout, suite[j],
                                                  theta_final - thetas[j], shared)},
                **{f"fd_{e:g}": directional_curvature(model, theta_initial, readout, suite[j],
                                                      theta_final - thetas[j], shared, eps=e)
                   for e in (1e-3, 1e-2)},
            },
        })
    # The bodies, on request, so that the *geometry* can be asked about rather than only the trajectory. Every
    # seed starts from the same connectome-initialised body, so a pair of endpoints is a chord through the
    # landscape, and the loss along it says whether the solutions are connected. `runs/` is gitignored and
    # `*.npz` with it, so this writes nothing into the repository.
    #
    # The *whole* body has to be saved, and that is `theta` **and the recurrent bias**: `train_task` optimises
    # `[model.theta, model.bias]`, so a chord evaluated from `theta` alone sits on top of a zero bias -- a
    # configuration the benchmark never produces. `e122`'s first version did exactly that and reported endpoint
    # losses of ~0.105 where the benchmark's own full-train-set loss is 0.0017, a factor of sixty, on the same
    # body: the instrument was measuring an untrained network's bias. Second time in one fire that a mid-run
    # quantity was paired with a final one; the rule is to save every input the forward pass reads.
    #: the penalty's inputs, written so a later run can be penalised by the SAME term. `e173`'s finding is that
    #: the Fisher is measured after each task's training, so a level knob moves it; this is what lets two levels
    #: of forgetting share one penalty, which is the only way the room account can be separated from a weaker
    #: penalty in this runner.
    if getattr(args, "save_fisher", None) is not None:
        out: dict = {}
        for k, (f, a) in enumerate(fisher_trace):
            out[f"f{k}"] = np.zeros(0) if f is None else np.asarray(f)
            out[f"a{k}"] = np.zeros(0) if a is None else a.detach().cpu().numpy()
        np.savez_compressed(args.save_fisher, **out)

    save_dir = getattr(args, "save_theta", None)
    if save_dir:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(save_dir / f"{method}_seed{seed}.npz",
                            theta_initial=theta_initial,
                            **{f"after_task_{k}": thetas[k] for k in range(T)},
                            **{f"bias_after_task_{k}": biases[k] for k in range(T)},
                            **{f"head_{i}_{p}_after_task_{k}": decoder_states[k][i][p]
                               for k in range(T) for i in range(len(heads)) for p in ("weight", "bias")})

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
        "retention_loss": L.tolist(),
        "theta_drift": drifts,
        "bias_norms": bias_norms,
        "full_train_loss": full_train_losses,
        "interference": interference,
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
    p.add_argument("--readout-seed", type=int, default=None,
                   help="seed for drawing the read-out subset; defaults to --seed0. Separate from --seed0 "
                        "because the sizes are drawn INDEPENDENTLY -- `choice(size=300)` is not a superset of "
                        "`choice(size=32)` -- so the 'read-out axis' is a sequence of unrelated neuron "
                        "samples, and the only way to test whether a shape along it is about the SIZE rather "
                        "than about WHICH neurons were drawn is to hold one fixed while the other moves")
    p.add_argument("--partition-seed", type=int, default=None,
                   help="seed for the matched-random partition draw; defaults to --seed0, so every artifact "
                        "written before this flag existed is unaffected. A matched-random control is the "
                        "POPULATION of size-matched random partitions and one draw is one sample from it "
                        "(rule 10, which the linear line implements with `--control-draws` and this line had no "
                        "way to vary at all), so independent draws are run as independent artifacts and averaged "
                        "in analysis with the between-draw sd reported beside the mean")
    p.add_argument("--frozen-body", action="store_true",
                   help="diagnostic: train only the decoder, to test whether the "
                        "plastic recurrent weights are used at all")
    p.add_argument("--anchor-bias", type=float, default=None,
                   help="also penalise the recurrent bias, whose 800 offsets carry 70%% of this "
                        "configuration's forgetting and are covered by no penalty (e125). The bias's "
                        "diagonal Fisher is unit-mean normalised like the weights' and then scaled by "
                        "this number, so the value is the RATIO of per-parameter anchoring strength; "
                        "1.0 treats every parameter alike (the bias then carries 800/27368 = 2.9%% of "
                        "the penalty's mass) and 26568/800 = 33.2 gives the two sets equal total mass")
    p.add_argument("--frozen-bias", action="store_true",
                   help="diagnostic: freeze the recurrent bias and train the weights, the "
                        "complement of --frozen-body, which freezes both. Both penalties in this "
                        "project cover only theta, so the bias is the one trained parameter no "
                        "penalty sees; this asks whether the forgetting hangs off it")
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
    p.add_argument("--save-fisher", type=Path, default=None,
                   help="write the EWC penalty's OWN INPUTS, one entry per task: the diagonal Fisher and the "
                        "anchor it is paired with, as they stood when that task was trained. `e173`'s finding is "
                        "that the Fisher is measured after each task's training, so EVERY knob that moves the "
                        "forgetting level moves the penalty's inputs too -- which means no single-field "
                        "manipulation can separate \"less room to forget\" from \"a weaker penalty\". Storing the "
                        "inputs is what makes that separation available: two runs at different levels can then be "
                        "penalised by ONE term")
    p.add_argument("--fisher-from", type=Path, default=None,
                   help="use the inputs written by --save-fisher INSTEAD of computing them, so that two runs "
                        "differing in a level knob are penalised identically. Refused for the block methods: "
                        "their inputs are a partition and a trace-normalised matrix, and a stored diagonal would "
                        "silently be a different object")
    p.add_argument("--save-theta", type=Path, default=None,
                   help="write each replicate's body — the initial one and the one after each task — as a "
                        "compressed .npz into this directory. Every seed starts from the same "
                        "connectome-initialised body, so a pair of endpoints is a chord through the loss "
                        "landscape; `runs/` and `*.npz` are gitignored, so this leaves nothing in the repository")
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
        # The draw is *independent per size*: `choice(size=300)` is not a superset of `choice(size=32)`. So the
        # read-out "axis" is a sequence of unrelated neuron samples, and a shape along it can be a property of
        # the sizes or of which neurons happened to be drawn -- `--readout-seed` is the control that separates
        # them, and it defaults to `--seed0` so every artifact written before the flag existed is unaffected.
        draw_seed = args.seed0 if args.readout_seed is None else args.readout_seed
        rs = np.sort(np.random.default_rng(draw_seed).choice(
            circ.n_neurons, size=args.readout_size, replace=False))
        draw_hash = hashlib.sha1(" ".join(str(int(x)) for x in rs).encode()).hexdigest()[:12]
        print(f"  read-out: {len(rs)} neurons of {circ.n_neurons}, draw seed {draw_seed}, subset {draw_hash}")
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
    partition_draw = None
    pre, post = net.synapse_endpoints()
    if any(m.startswith("ewc-block") for m in args.methods.split(",")):
        labels = circ.labels[args.basis]
        bio = SynapsePartition.from_labels(labels, pre, post, name=args.basis,
                                           pool_below=args.pool_below,
                                           pool_buckets=args.pool_buckets)
        # The matched-random control is the POPULATION of size-matched partitions and one draw is one sample
        # from it (rule 10, which the linear line implements with `--control-draws` and this one did not have a
        # way to vary at all): `--partition-seed` names the draw, defaults to `--seed0` so every artifact written
        # before the flag is unaffected, and the artifact records a fingerprint of it. Independent draws are run
        # as independent artifacts and averaged in analysis, with the between-draw sd reported beside the mean.
        part_seed = args.seed0 if args.partition_seed is None else args.partition_seed
        rand = SynapsePartition.random_matched(bio, np.random.default_rng(part_seed))
        partitions = {"bio": bio, "rand": rand}
        rand_sha1 = hashlib.sha1(
            " ".join(str(int(i)) for g in rand.groups for i in g[:8]).encode()).hexdigest()[:12]
        partition_draw = {"matched_random_draw_seed": int(part_seed), "n_groups": int(rand.n_groups),
                          "fingerprint_sha1": rand_sha1}
        print(f"  block partition ({args.basis}): {bio.n_groups} groups, "
              f"{bio.n_entries:,} block entries ({bio.describe()['block_gb']:.2f} GB), "
              f"constrained {bio.constrained_fraction():.4f}")
        print(f"  matched-random control: draw seed {part_seed}, {rand.n_groups} groups, "
              f"fingerprint {rand_sha1}")

    print(f"circuit {circ.name}: {circ.n_neurons} neurons, suite: {suite_label}, "
          f"{net.n_params:,} trainable recurrent weights")
    for t in suite:
        print(f"  task {t.name:16} in={t.n_input:5} readout={t.n_readout:5} "
              f"classes={t.n_classes}")

    out = {"config": vars(args), "circuit": circ.name, "n_params": net.n_params,
           # The read-out subset is an RNG draw, and until this fire no artifact identified which one it used --
           # `config` has `readout_size` and not the neurons. Every "bit-identical over seven executions" result
           # in this project's record is conditional on a draw that was never varied, and this block is what
           # makes the next artifact's draw checkable without storing 300 integers. `draw_seed` falls back to
           # `seed0` so an artifact written before `--readout-seed` existed still identifies its draw.
           "readout": ({"size": int(len(rs)), "draw_seed": int(draw_seed), "subset_sha1": draw_hash}
                       if rs is not None else
                       {"size": int(circ.n_neurons), "draw_seed": None, "subset_sha1": None}),
           "environment": environment(), "code_revision": code_revision(),
           "tasks": [t.summary() for t in suite], "methods": {},
           # Which matched-random partition this run used, when it used one: the control is a population and
           # this is the sample, so two artifacts whose block-rand rows differ are not comparable unless their
           # fingerprints agree (or unless the draws are averaged, which is what rule 10 asks for).
           **({"partition_draw": partition_draw} if partition_draw is not None else {})}
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
            "theta_drift": [float(x) for x in np.mean([r["theta_drift"] for r in reps], axis=0)],
            "bias_step": [float(x) for x in np.mean([[b["step"] for b in r["bias_norms"]]
                                                     for r in reps], axis=0)],
            "bias_from_zero": [float(x) for x in np.mean([[b["from_zero"] for b in r["bias_norms"]]
                                                          for r in reps], axis=0)],
            "full_train_loss": [float(x) for x in np.mean([r["full_train_loss"] for r in reps], axis=0)],
            "retention_loss": np.nanmean([r["retention_loss"] for r in reps], axis=0).tolist(),
            "interference": [{
                "task": j,
                "cumulative_first_order": float(np.mean(
                    [r["interference"][j]["cumulative"]["first_order"] for r in reps])),
                "cumulative_cosine": float(np.mean(
                    [r["interference"][j]["cumulative"]["cosine"] for r in reps])),
                "grad_norm": float(np.mean([r["interference"][j]["cumulative"]["grad_norm"]
                                            for r in reps])),
                "disp_norm": float(np.mean([r["interference"][j]["cumulative"]["disp_norm"]
                                            for r in reps])),
                # The same account over the whole body: `e139` measured that the theta-only form is cut 98% by a
                # penalty whose forgetting moves 1.21σ, so the two forms are stored side by side.
                "whole_body_cumulative": float(np.mean(
                    [r["interference"][j]["whole_body"]["cumulative"] for r in reps])),
                "whole_body_bias_only": float(np.mean(
                    [r["interference"][j]["whole_body"]["bias_only_cumulative"] for r in reps])),
                "second_order": {
                    k: {"quad": float(np.mean([r["interference"][j]["second_order"][k]["quad"]
                                               for r in reps])),
                        "curvature": float(np.mean([r["interference"][j]["second_order"][k]["curvature"]
                                                    for r in reps]))}
                    for k in sorted(reps[0]["interference"][j]["second_order"])},
            } for j in range(len(reps[0]["interference"]))],
            "replicates": reps,
        }
        out["methods"][method] = agg
        print(f"\n  --- {method} (n={args.repeats}) ---")
        print(f"    retention after the final task: "
              f"{['%.3f' % v for v in np.mean([r['retention'][-1] for r in reps], axis=0)]}")
        print(f"    learned (diagonal):  {['%.3f' % x for x in agg['learned']]}")
        print(f"    forgetting per task: {['%+.3f' % x for x in agg['forgetting_per_task']]}")
        print(f"    theta drift per task: {['%.3f' % x for x in agg['theta_drift']]}")
        print(f"    bias step / from zero: {['%.4f' % x for x in agg['bias_step']]} / "
              f"{['%.4f' % x for x in agg['bias_from_zero']]}")
        print(f"    full train loss per task: {['%.5f' % x for x in agg['full_train_loss']]}")
        rl = np.array(agg["retention_loss"])
        print(f"    retention loss (row=checkpoint, lower triangle): "
              f"{[[None if np.isnan(v) else round(v, 5) for v in row] for row in rl]}")
        if agg["interference"]:
            print(f"    interference per task (cumulative): "
                  f"{['%+.2e (cos %+.3f)' % (i['cumulative_first_order'], i['cumulative_cosine']) for i in agg['interference']]}")
            print(f"    second order per task (exact quad / curvature): "
                  f"{['%.3e / %.3e' % (i['second_order']['exact']['quad'], i['second_order']['exact']['curvature']) for i in agg['interference']]}")
            print(f"    cross-check, finite difference at eps 1e-3 and 1e-2 (quad): "
                  f"{['%.3e %.3e' % (i['second_order']['fd_0.001']['quad'], i['second_order']['fd_0.01']['quad']) for i in agg['interference']]}")
        print(f"    -> final accuracy {agg['final_accuracy']:.3f} ± {agg['final_sem']:.3f},  "
              f"mean forgetting {agg['mean_forgetting']:+.3f} ± {agg['forgetting_sem']:.3f}")

    # How much of the run-to-run spread is just the test set? The final accuracy averages one
    # evaluation per task over `n_test` held-out samples each, so it carries a binomial se; next
    # to training, enlarging that test set is free. A benchmark that does not say this invites
    # reading a null as a measurement of zero.
    n_eval = sum(len(t.y_test) for t in suite)
    print(f"\n  --- noise floor (n_eval = {n_eval} held-out decisions per replicate) ---")
    out["evaluation_noise"] = {"n_eval": n_eval}
    for name, m in out["methods"].items():
        ev = evaluation_noise(m["final_accuracy"], n_eval)
        rep_sd = m["final_sem"] * np.sqrt(max(args.repeats, 1))
        resid = float(np.sqrt(max(rep_sd ** 2 - ev ** 2, 0.0)))
        out["evaluation_noise"][name] = {
            "binomial_sem": ev, "replicate_sd": rep_sd, "residual_sd": resid,
            "variance_fraction": (ev ** 2 / rep_sd ** 2) if rep_sd else float("nan")}
        if rep_sd and ev < rep_sd:
            print(f"    {name:16} per-replicate sd {rep_sd:.4f}  of which evaluation "
                  f"{ev:.4f} ({ev**2/rep_sd**2:.0%} of the variance, and removable); "
                  f"training {resid:.4f}")
        else:
            # the floor can dominate when replicates are nearly identical (a very short run) or
            # when the 144 held-out decisions are not independent. Saying so is the point of
            # printing this at all -- a fraction above 100% is a signal, not a number.
            print(f"    {name:16} per-replicate sd {rep_sd:.4f} is at or below the test-set "
                  f"floor {ev:.4f}: this run cannot separate them (short training, or the "
                  f"held-out decisions are correlated)")

    # The comparison the whole network line is about: the biological partition against its
    # size-matched random control. It was previously done by hand in the findings, and unpaired --
    # but the two arms share a seed sequence, so their replicates are matched and the paired sem is
    # the right one (1.5x tighter at `side`). The detection floor is printed because the binding
    # constraint on this question is the benchmark's own run-to-run spread, not the effect size.
    if {"ewc-block", "ewc-block-rand"} <= set(out["methods"]):
        bio, rnd = out["methods"]["ewc-block"], out["methods"]["ewc-block-rand"]
        print("\n  --- matched pair: biological partition vs its size-matched random control ---")
        out["matched_pair"] = {}
        for key in ("final_accuracy", "mean_forgetting"):
            pc = paired_contrast([r[key] for r in bio["replicates"]],
                                 [r[key] for r in rnd["replicates"]])
            out["matched_pair"][key] = pc
            line = (f"    {key:18} delta {pc['delta']:+.4f} +- "
                    f"{pc['sem_unpaired']:.4f} unpaired ({pc['sigma_unpaired']:.2f} sigma)")
            if "sem_paired" in pc:
                line += (f"   {pc['sem_paired']:.4f} paired ({pc['sigma_paired']:.2f} sigma)")
            print(line)
            if "sem_paired" in pc and pc["sem_paired"] > 0 and abs(pc["delta"]) < pc["sem_paired"]:
                # a near-zero delta makes sigma degenerate: it goes to 0 however *uncertain* the
                # measurement is, so "0.00 sigma" reads as "nothing there" when it means "measured
                # zero with an interval of +/- this sem". Report the interval, which is the
                # informative thing. Seen on the ito_lee_hemilineage rung, where the three
                # per-replicate deltas are -0.056, +0.049, +0.007 and their mean is 0.000000.
                print(f"    {'':18} the mean is inside its own sem, so sigma is degenerate; "
                      f"the measurement is {pc['delta']:+.4f} +- {pc['sem_paired']:.4f}")
            if "min_detectable" in pc:
                print(f"    {'':18} this run detects effects above {pc['min_detectable']:.3f}; "
                      f"0.03 would need {pc['repeats_for_0.03']:.0f} repeats and 0.01 "
                      f"{pc['repeats_for_0.01']:.0f}")

    out["timing_s"] = time.time() - t0

    print(f"\n  chance = {1.0 / suite[0].n_classes:.3f}   ({time.time()-t0:.0f}s)")
    if args.json_out:
        write_json(args.json_out, out)
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
