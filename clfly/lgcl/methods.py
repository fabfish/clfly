"""The method zoo, expressed as anchoring choices.

Each method here is a different answer to "what do I fuse, and in what basis":

``Naive``           fuse nothing — take the current task's measurement and go.
``AnchoredFilter``  fuse everything recursively, but project the covariance onto
                    a basis after every step.  ``Diagonal`` reproduces EWC's
                    approximation, ``Full`` is the oracle, and any partition is
                    the biologically-anchored variant this project is about.
``EWCPenalty``      the operational EWC people actually run: a running Fisher
                    accumulator plus a quadratic anchor to past solutions.
``Replay``          keep a few raw old measurements and refit, with staleness
                    inflation for the drift since they were taken.

The point of having both ``AnchoredFilter`` and ``EWCPenalty`` is that the LGCL
correspondence table claims they are the same object up to approximation.  Having
them side by side makes that claim executable instead of rhetorical.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .bases import Basis, Diagonal, Full, Rank
from .kalman import kalman_update


class Method:
    """A learner: consumes a :class:`~clfly.lgcl.model.Sequence`, emits estimates."""

    name = "method"

    def run(self, seq) -> np.ndarray:  # pragma: no cover - interface
        raise NotImplementedError


# --------------------------------------------------------------------------
class Naive(Method):
    """Sequential fine-tuning: keep only the current task's measurement.

    For a rank-deficient ``J`` (partially observed task) this learning rule can
    only move inside the observed subspace, which is exactly the pathology the
    partial-observability regime is built to expose.
    """

    name = "naive"

    def run(self, seq):
        return np.stack([np.linalg.pinv(seq.J[k]) @ (seq.J[k] @ seq.y[k])
                         for k in range(seq.T)])


# --------------------------------------------------------------------------
class AnchoredFilter(Method):
    """Recursive Kalman filter with the posterior projected onto a basis.

    The single most important object in the project: swapping ``basis`` sweeps
    the whole spectrum from "no memory" (``Naive``, roughly) through EWC to the
    exact oracle, and each ``basis`` is a claim about where information lives.
    """

    def __init__(self, basis: Basis, name: str | None = None):
        self.basis = basis
        self.name = name or f"anchored[{basis.name}]"

    def run(self, seq):
        from .kalman import filter_sequence
        ests, _ = filter_sequence(seq, self.basis)
        return ests


def kalman_oracle(seq):
    return AnchoredFilter(Full(seq.d), name="kalman").run(seq)


def ewc_diagonal(seq):
    return AnchoredFilter(Diagonal(seq.d), name="ewc").run(seq)


def spectral_truncation(seq, r):
    return AnchoredFilter(Rank(seq.d, r), name=f"spectral[r={r}]").run(seq)


# --------------------------------------------------------------------------
@dataclass
class EWCPenalty(Method):
    """Operational EWC: running Fisher accumulator + quadratic anchor.

    At task ``k`` it minimises::

        (th - y_k)^T J_k (th - y_k)
            + lam * (th - th*)^T [ sum_{j<k} Pi(J_j) ] (th - th*)

    with ``Pi`` set by ``basis`` and ``th*`` the solution at the end of the
    previous task.  ``basis=Diagonal()`` is textbook EWC; ``Full()`` is the
    limit it approximates; ``Partition(cell_types)`` is the fly-anchored variant.

    Note the single shared anchor.  Kirkpatrick et al. anchor every accumulated
    task precision to the *most recent* solution, which is what this reproduces
    — and which the LGCL memo flags as not strictly the correct Bayesian
    update (online EWC / Progress & Compress fixed that later).  Keeping the
    original form here is deliberate: it is the baseline people actually run.

    ``average=True`` divides the penalty by the number of accumulated tasks.
    Without it the penalty grows linearly in ``T`` and eventually freezes every
    parameter — the rigidity blow-up the reference implementation hit in
    practice (see LGCL v7 engineering note).
    """

    basis: Basis
    lam: float = 1.0
    average: bool = True
    name: str = field(default="ewc-penalty")

    def run(self, seq):
        d = seq.d
        acc = np.zeros((d, d))
        theta = np.zeros(d)
        ests = []
        for k in range(seq.T):
            J = seq.J[k]
            if k == 0:
                theta = np.linalg.pinv(J) @ (J @ seq.y[k])
            else:
                scale = self.lam / (k if self.average else 1.0)
                theta = np.linalg.pinv(J + scale * acc) @ (J @ seq.y[k] + scale * acc @ theta)
            ests.append(theta.copy())
            acc = acc + self.basis.project(J)
        return np.stack(ests)


# --------------------------------------------------------------------------
@dataclass
class Replay(Method):
    """Keep the last ``budget`` raw measurements; refit with staleness inflation.

    A measurement taken ``k - j`` steps ago has been corrupted by ``(k - j) q I``
    of accumulated drift, so its precision is inflated before fusion::

        J_eff^{-1} = J_j^{-1} + (k - j) q I

    This is the honest accounting LGCL insists on — replay stores *content*, not
    covariance, and pays for the age of what it stores.
    """

    budget: int = 3
    name: str = field(default="replay")

    def run(self, seq):
        d, q = seq.d, seq.q
        theta, P = np.zeros(d), np.eye(d)
        store: list[tuple[int, np.ndarray, np.ndarray]] = []
        ests = []
        for k in range(seq.T):
            P = P + q * np.eye(d)
            theta, P = kalman_update(theta, P, seq.J[k], seq.y[k])
            if self.budget:
                for (j, Jj, yj) in store[-self.budget:]:
                    Je = np.linalg.pinv(np.linalg.pinv(Jj) + (k - j) * q * np.eye(d))
                    theta, P = kalman_update(theta, P, Je, yj)
            store.append((k, seq.J[k], seq.y[k]))
            ests.append(theta.copy())
        return np.stack(ests)


# --------------------------------------------------------------------------
REGISTRY = {
    "naive": lambda seq, **kw: Naive().run(seq),
    "kalman": lambda seq, **kw: kalman_oracle(seq),
    "ewc": lambda seq, **kw: ewc_diagonal(seq),
    "replay": lambda seq, budget=3, **kw: Replay(budget=budget).run(seq),
    "sketch": lambda seq, r=4, **kw: spectral_truncation(seq, r),
}


def run(method: str, seq, **kwargs):
    """Run a registered method by name."""
    if method not in REGISTRY:
        raise KeyError(f"unknown method {method!r}; have {sorted(REGISTRY)}")
    return REGISTRY[method](seq, **kwargs)
