"""Tasks whose geometry comes from the wiring.

LGCL's synthetic task families draw their precision bases from random rotations.
That is precisely what makes the diagonal approximation look free, and it is the
assumption this project exists to break.  Here a task's covariance is
*propagated through the connectome*, so its eigenbasis is a property of the fly's
wiring rather than of a random draw.

**Construction.** A linearised rate model around a fixed point satisfies
``x = W x + u``, so an input drive ``u`` maps to ``x = G u`` with the propagator

    G = (I - W)^{-1}.

A task is a *functional assembly* -- an input population specified by cell types,
with sparse coding within it (a fly does not activate a whole cell type at once;
a given odour drives a few percent of Kenyon cells).  Its observation covariance
is the propagated drive covariance

    Sigma_k = G D_k G^T,   D_k = diag(weights on the task's input neurons).

**Two properties that make the basis question well-posed.**

1. ``Sigma_k`` is dense, and its eigenbasis is set by the connectome's propagator.
   Whether a cell-type partition aligns with it is then a fact about the fly, not
   a construction -- which is the whole point.
2. Different assemblies are oriented differently, so the *rotation between tasks*
   -- the quantity LGCL's unimodal prediction is a function of -- comes out of the
   wiring.  No synthetic rotation is imposed anywhere.

**Why the regime is the interesting one.** ``D_k`` has rank equal to the assembly
size, so ``Sigma_k`` has that same rank and ``J_k`` is singular whenever the
assembly is smaller than the circuit.  The tasks are therefore *partially
observed* by construction, which LGCL v7 measured to be the regime where memory
matters by a factor of 12.7 over the fully-observed one.  We land there because
sparse coding is real, not because a parameter was tuned to get there.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from ..lgcl.model import Sequence, sample_measurement
from .circuits import Circuit
from .graph import Connectome


@dataclass(frozen=True)
class Assembly:
    """An input population, named by the cell types that make it up."""

    name: str
    column: str
    values: tuple[str, ...]
    note: str = ""


#: Functional assemblies, chosen to cover distinct circuits.  ``cell_type``
#: entries are matched by prefix, so a family (all Kenyon cell subtypes, all ring
#: neurons) is one entry.
TASK_ASSEMBLIES: tuple[Assembly, ...] = (
    Assembly(
        name="odour_identity",
        column="cell_type",
        values=("KC",),
        note="Kenyon cells: sparse combinatorial odour code, mushroom body input",
    ),
    Assembly(
        name="odour_valence",
        column="cell_class",
        values=("MBON", "DAN"),
        note="mushroom body output + dopaminergic teaching signal",
    ),
    Assembly(
        name="heading",
        column="cell_type",
        values=("EPG", "PFN", "PEN", "ER", "PB", "NO"),
        note="central complex ring attractor: the fly's compass",
    ),
    Assembly(
        name="odour_input",
        column="cell_class",
        values=("ALPN", "ALLN", "ALIN"),
        note="antennal lobe projection / local neurons: upstream odour drive",
    ),
    Assembly(
        name="innate_odour",
        column="cell_class",
        values=("LHLN", "LHCENT"),
        note="lateral horn: the innate, unlearned odour pathway",
    ),
)


@dataclass
class WiringTasks:
    """A realised task sequence, plus the metadata needed to interpret it."""

    sequence: Sequence
    assemblies: list[Assembly]
    support_sizes: list[int]
    ranks: list[int]
    spectral_gap: list[float] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "n_neurons": self.sequence.d,
            "T": self.sequence.T,
            "q": self.sequence.q,
            "support_sizes": self.support_sizes,
            "ranks": self.ranks,
            "rank_fraction": [r / self.sequence.d for r in self.ranks],
        }


# --------------------------------------------------------------------------
def stable_weights(conn: Connectome, rho: float = 0.9, scale: str = "log1p",
                   maxiter: int = 2000) -> sp.csr_matrix:
    """Connectome weights rescaled to spectral radius ``rho < 1``.

    Stability is not a detail: ``G = (I - W)^{-1}`` only exists, and the linear
    rate model only has a fixed point, when the spectral radius is below one.
    The connectome's raw signed weights are far from that, so the dynamics are
    normalised rather than the threshold being fiddled per experiment.
    """
    W = conn.weights(scale).astype(np.float64).tocsr()
    n = W.shape[0]
    k = min(2, n - 1)
    try:
        lam = spla.eigs(W, k=k, which="LM", return_eigenvectors=False, maxiter=maxiter)
        radius = float(np.abs(lam).max())
    except Exception:  # pragma: no cover - fall back to power iteration
        v = np.ones(n)
        radius = 0.0
        for _ in range(200):
            v = W @ v
            nv = np.linalg.norm(v)
            if nv == 0:
                break
            v /= nv
            radius = nv
    if radius <= 0:
        raise ValueError("weight matrix has zero spectral radius")
    return (W * (rho / radius)).tocsr()


def propagator_solver(W: sp.spmatrix):
    """Sparse LU factorisation of ``I - W``.

    Returned as a reusable solver rather than an explicit inverse: the task
    covariances only ever need the propagator's *columns* on each assembly, and
    ``n x s`` solves are far cheaper than forming a dense ``n x n`` inverse.
    """
    A = (sp.identity(W.shape[0], format="csc") - W.tocsc()).tocsc()
    return spla.splu(A)


def assembly_support(circ: Circuit, assembly: Assembly,
                     support_size: int | None, sparsity: float | None,
                     rng: np.random.Generator,
                     weight_concentration: float | None = None):
    """Neurons driven by an assembly, and their sparse drive weights.

    Prefix-matches ``assembly.values`` against the circuit's per-neuron group
    names, then keeps a random subset -- the sparse-coding step, since a fly does
    not activate a whole cell type at once.

    Sizing is by **absolute count** (``support_size``) when given, and only falls
    back to a fraction (``sparsity``) otherwise.  That matters: a fraction applied
    on top of an already-subsampled circuit compounds, and small assemblies
    (mushroom body output neurons, ring neurons) collapse to a handful of neurons
    -- tasks too thin to be read as tasks at all.

    ``weight_concentration`` controls the *shape* of the drive, and exists to
    decouple an axis that is otherwise confounded.  ``None`` draws
    ``Uniform(0.5, 1.5)`` (the original behaviour, kept bit-identical so recorded
    runs stay valid).  A float draws ``exp(kappa * z)`` for ``z ~ N(0, 1)``,
    normalised to mean one: at ``kappa = 0`` all neurons are driven equally, and
    large ``kappa`` concentrates the drive on a few.  Because every ``kappa``
    reuses the same ``z``, the sweep varies the task's spectral richness at fixed
    topology, fixed support size and fixed rank.
    """
    names = circ.neuron_names(assembly.column)
    matched = np.array([any(n.startswith(v) for v in assembly.values) for n in names])
    idx = np.flatnonzero(matched)
    if len(idx) == 0:
        raise ValueError(
            f"assembly {assembly.name!r} matched no neurons; "
            f"values {assembly.values} not present in column {assembly.column!r}. "
            f"available names: {sorted(set(names))[:12]}..."
        )

    if support_size is not None:
        n_keep = min(len(idx), support_size)
    elif sparsity is not None:
        n_keep = max(1, int(round(len(idx) * sparsity)))
    else:
        n_keep = len(idx)
    n_keep = min(n_keep, len(idx))
    if n_keep < len(idx):
        idx = np.sort(rng.choice(idx, size=n_keep, replace=False))

    if weight_concentration is None:
        weights = rng.uniform(0.5, 1.5, size=len(idx))
    else:
        z = rng.standard_normal(len(idx))
        weights = np.exp(weight_concentration * z)
        weights = weights / weights.mean()
    return idx, weights


def task_covariance(solver, support: np.ndarray, weights: np.ndarray,
                    normalize: bool = True) -> np.ndarray:
    """``G D G^T`` for a diagonal drive covariance on ``support``.

    Symmetrised and (optionally) scaled to unit trace, so tasks are comparable in
    magnitude and the only thing that varies between them is *orientation*.
    """
    n = solver.shape[0]
    E = np.zeros((n, len(support)))
    E[support, np.arange(len(support))] = 1.0
    Gs = solver.solve(E)                       # (n, s) propagator columns
    S = (Gs * weights) @ Gs.T
    S = (S + S.T) * 0.5
    if normalize:
        tr = np.trace(S)
        if tr > 0:
            S /= tr
    return S


def build_tasks(
    circ: Circuit,
    assemblies=TASK_ASSEMBLIES,
    rho: float = 0.9,
    support_size: int | None = 300,
    sparsity: float | None = None,
    measurement_strength: float = 1.0,
    q: float = 0.02,
    seed: int = 0,
    weight_concentration: float | None = None,
    verbose: bool = False,
) -> WiringTasks:
    """Assemble a :class:`Sequence` whose tasks are propagated through the wiring.

    ``measurement_strength`` sets ``tr(J_k) = strength * n``: at 1.0 a task's
    total information is comparable to the unit prior, the calibrated middle
    ground between "the prior decides everything" and "the measurement does".
    Because ``J_k`` has rank equal to the assembly support, every task is
    partially observed regardless of this setting.
    """
    rng = np.random.default_rng(seed)
    n = circ.n_neurons
    W = stable_weights(circ.net, rho=rho)
    solver = propagator_solver(W)

    Sigmas, Js, supports, ranks = [], [], [], []
    for asm in assemblies:
        support, weights = assembly_support(circ, asm, support_size, sparsity, rng,
                                           weight_concentration=weight_concentration)
        S = task_covariance(solver, support, weights)
        Sigmas.append(S)
        Js.append(measurement_strength * n * S)
        supports.append(len(support))
        ranks.append(int(np.sum(np.linalg.eigvalsh(S) > 1e-10 * np.trace(S))))
        if verbose:
            print(f"  {asm.name:20} support={len(support):5,}  rank={ranks[-1]:5,}")

    J = np.stack(Js)
    Sigma = np.stack(Sigmas)

    theta = rng.standard_normal(n)
    thetas, ys = [], []
    for k in range(len(assemblies)):
        thetas.append(theta.copy())
        ys.append(sample_measurement(theta, J[k], rng))
        theta = theta + np.sqrt(q) * rng.standard_normal(n)

    seq = Sequence(d=n, q=q, theta=np.stack(thetas), J=J, Sigma=Sigma,
                   y=np.stack(ys), U=None)
    return WiringTasks(sequence=seq, assemblies=list(assemblies),
                       support_sizes=supports, ranks=ranks)
