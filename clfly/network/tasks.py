"""Behavioural task suite for the connectome-constrained rate network.

Each task is a **classification problem delivered to a circuit**: a stimulus is
injected into a task's input population, the network runs its recurrent dynamics, and a
linear decoder reads out a task-specific output population.  Class identity is carried
by the input templates plus noise, which is the minimal object that gives a task
learnable structure without hand-designing features.

**Two kinds of stimulus live here, and the difference is the trial's time axis.**
`make_task` delivers a **sustained** drive -- the same pattern at every one of the
``tau`` steps -- which is what the assembly and overlap suites are built from.
`make_sequence_task` delivers a **sequence** -- one sub-stimulus for the first half of
the trial and another for the second, with the label their ordered pair -- which is the
first stimulus in this repository that changes with time.  `e322` measured the first
kind across both older builders, both splits and two circuit sizes and found a
deviation of exactly zero; the second is what that finding named as missing.

Three design choices that matter for the continual-learning question.

**The stimulus lives over the whole neuron index**, nonzero only on the input
population, so there is no separate input projection to absorb task structure.  The
project's question concerns the recurrent wiring, and an input pathway with its own
free parameters would confound it.

**Read-out populations are distinct per task** (MBONs for odour identity, central
complex output for heading, Kenyon cells for odour input).  That mirrors the
connectome's own separation and gives the interference question somewhere to live.

**Templates are held fixed across tasks**, drawn from one seed, so differences between
tasks are architectural rather than a matter of how lucky a draw was.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..connectome.circuits import Circuit
from ..connectome.tasks import overlap_controlled_supports


@dataclass
class RateTask:
    """One classification task: where the stimulus enters, where it is read out."""

    name: str
    input_neurons: np.ndarray
    readout_neurons: np.ndarray
    n_classes: int
    n_neurons: int
    tau: int
    u_train: np.ndarray        # (n_train, tau, n_neurons)
    y_train: np.ndarray        # (n_train,)  local labels, 0 .. n_classes-1
    u_test: np.ndarray
    y_test: np.ndarray
    class_offset: int = 0      # where this task's classes sit in a shared head

    @property
    def n_input(self) -> int:
        return len(self.input_neurons)

    @property
    def n_readout(self) -> int:
        return len(self.readout_neurons)

    def summary(self) -> dict:
        return {"name": self.name, "n_classes": self.n_classes,
                "n_input": self.n_input, "n_readout": self.n_readout,
                "n_train": len(self.y_train), "n_test": len(self.y_test)}


def _population(circ: Circuit, column: str, prefixes: tuple[str, ...],
                cap: int | None = None, seed: int = 0) -> np.ndarray:
    """Indices of neurons whose group name starts with any of ``prefixes``."""
    names = circ.neuron_names(column)
    matched = np.array([any(n.startswith(p) for p in prefixes) for n in names])
    idx = np.flatnonzero(matched)
    if len(idx) == 0:
        raise ValueError(f"no neurons matched {prefixes} in {column!r}")
    if cap is not None and len(idx) > cap:
        idx = np.sort(np.random.default_rng(seed).choice(idx, size=cap, replace=False))
    return idx


def _heads(circ: Circuit, input_spec, readout_spec, cap: int, seed: int,
           readout_all: bool, readout_subset, input_support) -> tuple[np.ndarray, np.ndarray]:
    """The two populations a task is defined by: where the stimulus enters, where the state is read out.

    Extracted from :func:`make_task` unchanged when :func:`make_sequence_task` needed the same two draws,
    because a sequence task differs only in **what** is delivered, never in **where**.
    """
    n = circ.n_neurons
    if input_support is not None:
        inp = np.asarray(input_support, dtype=np.int64)
    else:
        cols_in, vals_in = input_spec
        inp = _population(circ, cols_in, vals_in, cap=cap, seed=seed)
    if readout_subset is not None:
        out = np.asarray(readout_subset, dtype=np.int64)
    elif readout_all:
        out = np.arange(n)
    else:
        cols_out, vals_out = readout_spec
        out = _population(circ, cols_out, vals_out, cap=cap, seed=seed + 1)
    return inp, out


def make_task(circ: Circuit, name: str, input_spec: tuple[str, tuple[str, ...]],
              readout_spec: tuple[str, tuple[str, ...]] | None, n_classes: int = 4,
              n_train: int = 96, n_test: int = 48, tau: int = 12,
              noise: float = 1.0, cap: int = 220, seed: int = 0,
              class_offset: int = 0, readout_all: bool = False,
              readout_subset: np.ndarray | None = None,
              input_support: np.ndarray | None = None) -> RateTask:
    """Build one task: fixed class templates, injected over ``tau`` timesteps.

    The stimulus is sustained rather than instantaneous, so the network's recurrent
    dynamics have time to propagate it from the input population to the readout —
    which is the whole point of using the connectome as the substrate rather than a
    feedforward readout.  **Sustained means constant**: the same pattern is delivered
    at every one of the ``tau`` steps, which `e322` measured across both builders,
    both splits and two circuit sizes as a deviation of exactly zero.  The trial's
    time axis therefore carries no information here; :func:`make_sequence_task` is
    the builder that gives it one.

    ``readout_all`` makes the read-out the whole circuit state and is what the
    **shared-head** (class-incremental) mode uses: with a single decoder serving every
    task, the tasks can no longer be separated by their read-out population and must
    differ only in where the stimulus enters.  Labels stay local (``0 .. n_classes-1``)
    and ``class_offset`` records where they sit in the shared head, so the loss is over
    the task's own class subset — the standard class-incremental protocol, where the
    learner never sees a future task's classes.
    """
    rng = np.random.default_rng(seed)
    n = circ.n_neurons
    inp, out = _heads(circ, input_spec, readout_spec, cap, seed, readout_all, readout_subset, input_support)

    templates = rng.standard_normal((n_classes, len(inp)))

    def make(count: int, seed_off: int):
        r = np.random.default_rng(seed + 1000 + seed_off)
        y = r.integers(0, n_classes, size=count)
        u = np.zeros((count, tau, n))
        stim = templates[y] + noise * r.standard_normal((count, len(inp)))
        u[:, :, inp] = stim[:, None, :]
        return u, y

    u_tr, y_tr = make(n_train, 0)
    u_te, y_te = make(n_test, 1)
    return RateTask(name=name, input_neurons=inp, readout_neurons=out,
                    n_classes=n_classes, n_neurons=n, tau=tau,
                    u_train=u_tr, y_train=y_tr, u_test=u_te, y_test=y_te,
                    class_offset=class_offset)


def make_sequence_task(circ: Circuit, name: str, input_spec: tuple[str, tuple[str, ...]],
                       readout_spec: tuple[str, tuple[str, ...]] | None, k: int = 2,
                       n_train: int = 96, n_test: int = 48, tau: int = 12,
                       noise: float = 1.0, cap: int = 220, seed: int = 0,
                       class_offset: int = 0, readout_all: bool = False,
                       readout_subset: np.ndarray | None = None,
                       input_support: np.ndarray | None = None) -> RateTask:
    """Build one task whose trial is a **sequence**: two sub-stimuli, one per half, and the label their pair.

    This is the first builder in the repository that writes a stimulus which **changes with time**, and it is
    the change `e322`'s own "what it cannot do" named: that unit measured the trial's time axis across both
    older builders -- assembly and overlap, two circuit sizes, both splits -- and found the stimulus equal to
    its first step exactly, everywhere, and concluded that a temporal task needs *either a second writer with
    a time index or an environment in the training loop*. This is the first of the two, chosen because it fits
    the `(n, tau, n_neurons)` contract the runner already consumes: **no training-loop change is needed to
    train on it**, only to close a loop around it.

    **Why the label is the ordered pair.** Each example draws two symbols ``a`` and ``b`` from a ``k``-way
    alphabet and delivers ``a``'s template for the first ``tau // 2`` steps and ``b``'s for the rest, with
    fresh noise at every step. The class is ``a * k + b``. So the second half's identity is available from
    the second half's drive alone, and the **first** half's identity is not in the drive any more once the
    boundary is crossed: a decoder that is to report the pair from the last step has to have carried ``a``
    there through the recurrent state. A task whose label were the unordered pair, or ``b`` alone, would need
    no memory and is not what this builds.

    The alphabet is separate from the class count: ``k`` templates, ``k * k`` classes, so ``k = 2`` gives the
    four classes the runner's default head already has. The same symbol is the same pattern at either
    position, which is what makes the two halves comparable inside one trial.
    """
    rng = np.random.default_rng(seed)
    n = circ.n_neurons
    inp, out = _heads(circ, input_spec, readout_spec, cap, seed, readout_all, readout_subset, input_support)
    half = max(1, tau // 2)
    n_classes = k * k
    templates = rng.standard_normal((k, len(inp)))

    def make(count: int, seed_off: int):
        r = np.random.default_rng(seed + 1000 + seed_off)
        first = r.integers(0, k, size=count)
        second = r.integers(0, k, size=count)
        u = np.zeros((count, tau, n))
        #: **the second writer**, and the noise is drawn **once per half rather than once per step**: a half has
        #: to be a constant pattern for the boundary to be the trial's only temporal event, which is what
        #: :func:`make_task` already does for the whole trial (one draw, broadcast over ``tau``). Resampling it
        #: per step was the first version's behaviour and made the stimulus vary within a half as well, so it
        #: measured as a within-half deviation of 5.9 rather than 0 until it was fixed.
        eps = [noise * r.standard_normal((count, len(inp))) for _ in range(2)]
        for t in range(tau):
            symbol, which = (first, 0) if t < half else (second, 1)
            u[:, t, inp] = templates[symbol] + eps[which]
        return u, first * k + second

    u_tr, y_tr = make(n_train, 0)
    u_te, y_te = make(n_test, 1)
    return RateTask(name=name, input_neurons=inp, readout_neurons=out,
                    n_classes=n_classes, n_neurons=n, tau=tau,
                    u_train=u_tr, y_train=y_tr, u_test=u_te, y_test=y_te,
                    class_offset=class_offset)


#: The default suite.  Three tasks on distinct circuits, so the interference question
#: has structure to find and the runtime stays tractable.
#:
#: **`e186` measures what this suite is against the analytic line's five assemblies**, and two differences are
#: worth knowing at the point of reading it: `heading`'s input list used to carry `"PB"`, which **selected no
#: neuron in any column of the annotation** (counted by `e186`: 0 whole brain, 0 in the circuit, so the task's
#: input is the 55 EPG/PFN/PEN/ER neurons and always has been) -- dropped, and the intent noted rather than lost;
#: and `odour_input` omits `"ALIN"`, which the analytic assembly of the
#: same name includes (24 neurons whole brain, 10 in the circuit). With `--shared-head` the *read-out* populations
#: below are inert and every task differs only in where the stimulus enters; they are the read-outs in the 17
#: corpus runs that used per-task heads.
SUITE_SPECS = (
    ("odour_identity", ("cell_type", ("KC",)), ("cell_class", ("MBON",))),
    ("heading", ("cell_type", ("EPG", "PFN", "PEN", "ER")),
     ("cell_class", ("CX",))),
    ("odour_input", ("cell_class", ("ALPN", "ALLN")), ("cell_type", ("KC",))),
)


def make_suite(circ: Circuit, specs=SUITE_SPECS, shared_head: bool = False,
               readout_subset: np.ndarray | None = None, **kwargs) -> list[RateTask]:
    """Build the default behavioural suite against a circuit.

    ``shared_head`` switches to the **class-incremental** configuration: every task is
    read out through a single decoder, and the tasks' label sets are made disjoint
    (``class_offset``).

    ``readout_subset`` is what makes that setting *test the connectome*.  Reading out
    from the whole circuit state gives a 12-way linear decoder every one of ~1300
    features, and a frozen-body diagnostic showed that such a decoder solves the tasks
    with the recurrent weights untouched — accuracy 0.944 frozen against 0.951 plastic,
    with forgetting falling to exactly zero.  Restricting the read-out to a narrow
    population forces the recurrent weights to *route* information to those neurons,
    which is the condition under which they become load-bearing and forgetting can
    arise.
    """
    return [make_task(circ, name, inspec, outspec, seed=i,
                      class_offset=i * kwargs.get("n_classes", 4),
                      readout_all=shared_head and readout_subset is None,
                      readout_subset=readout_subset, **kwargs)
            for i, (name, inspec, outspec) in enumerate(specs)]


def make_overlap_suite(circ: Circuit, n_tasks: int = 3, support: int = 80,
                       overlap: float = 0.0, shared_head: bool = True,
                       readout_subset: np.ndarray | None = None,
                       seed: int = 0, **kwargs) -> list[RateTask]:
    """Tasks whose **input populations** have an exact, uniform overlap.

    The default suite separates the tasks at the input by construction — each is driven
    into a different circuit — and `e8e` found that this is why forgetting is mild even
    under a shared decoder: the tasks' representations land in distinct parts of state
    space, so the decoder can allocate near-orthogonal directions per task and nothing
    competes.  This suite removes that separation in a controlled way, using the same
    pool-plus-private-complement construction as `e7`, so the question can be asked
    directly: **does raising input overlap raise forgetting?**

    ``overlap = 0`` gives fully disjoint inputs (the default suite's structure, but with
    randomly chosen neurons rather than identified circuits) and ``overlap = 1`` gives
    every task the same input population — identical inputs, differing only in their
    class templates.
    """
    rng = np.random.default_rng(seed)
    supports = overlap_controlled_supports(circ.n_neurons, n_tasks, support, overlap, rng)
    n_classes = kwargs.get("n_classes", 4)
    return [make_task(circ, f"ov{overlap:g}_t{i}", None, None, seed=i,
                      class_offset=i * n_classes, readout_all=shared_head and readout_subset is None,
                      readout_subset=readout_subset,
                      input_support=sup, **kwargs)
            for i, sup in enumerate(supports)]


def make_sequence_suite(circ: Circuit, specs=SUITE_SPECS, k: int = 2, shared_head: bool = False,
                        readout_subset: np.ndarray | None = None, **kwargs) -> list[RateTask]:
    """The assembly suite's three circuits, driven by :func:`make_sequence_task` instead of :func:`make_task`.

    Same circuits, same heads, same seeds, same order: the only field that differs from `make_suite` is the kind
    of stimulus, so a comparison between the two is a comparison of the time axis and not of the substrate. Its
    task names carry the ``seq`` family so an artifact can be assigned to the right builder without loading it,
    the way e187 reads the assembly and overlap families apart.
    """
    return [make_sequence_task(circ, f"seq_{name}", inspec, outspec, k=k, seed=i,
                               class_offset=i * k * k,
                               readout_all=shared_head and readout_subset is None,
                               readout_subset=readout_subset, **kwargs)
            for i, (name, inspec, outspec) in enumerate(specs)]
