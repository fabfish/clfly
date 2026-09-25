"""Behavioural task suite for the connectome-constrained rate network.

Each task is a **classification problem delivered to a circuit**: a stimulus is
injected into a task's input population as a sustained drive, the network runs its
recurrent dynamics, and a linear decoder reads out a task-specific output population.
Class identity is carried by a per-class input template plus noise, which is the
minimal object that gives a task learnable structure without hand-designing features.

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
    feedforward readout.

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
