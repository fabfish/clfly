"""Anchoring bases: what "diagonal EWC" generalises to.

LGCL's central identity is that EWC is a Kalman filter whose posterior
covariance is projected onto the coordinate basis at every step -- the diagonal
projection.  The information it discards is the off-diagonal part, and the whole
question of this project is *which projection you should have used instead*.

This module makes that question precise by introducing a family of projections
``Pi : Sym(d) -> Sym(d)``, all idempotent, all sitting between two extremes:

    Full  (keep everything, = the Kalman oracle)
      |
    Partition(labels)      keep within-group covariance, discard across-group
      |
    Diagonal               keep only the diagonal (labels = singletons, = EWC)

``RotatedDiagonal(U)`` is the other axis of the family: diagonal, but in the
coordinates of ``U`` rather than of the neurons.  With ``U = I`` it *is*
``Diagonal``; with ``U`` the task eigenbasis it is the spectral anchoring that
LGCL v8 found restores the unimodal gap.

The practical upshot for the fly work: a partition is a *biological* object
(cell type, hemilineage, nerve, neuropil), so ``Partition`` turns a cell-type
annotation table into a candidate Fisher anchoring basis -- the comparison no
one has run.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .linalg import symmetric_inverse


# --------------------------------------------------------------------------
# projections on the space of symmetric matrices
# --------------------------------------------------------------------------
class Basis:
    """A projection of posterior covariances onto an 'allowed' structure."""

    name: str = "basis"
    dim: int = 0

    def project(self, P: np.ndarray) -> np.ndarray:  # pragma: no cover - interface
        raise NotImplementedError

    def __call__(self, P: np.ndarray) -> np.ndarray:
        return self.project(P)

    @property
    def n_parameters(self) -> int:
        """Free entries of the retained structure -- the matched budget.

        Comparability between bases is only meaningful at matched budget,
        otherwise the richer basis wins for free.  For a partition this is the
        sum of per-group triangular numbers, so a biological partition and a
        group-size-matched random control come out identical by construction.

        Note the honest accounting for :class:`RotatedDiagonal`: a rotation is
        itself ``d(d-1)/2`` numbers to specify, so unless the basis is *shared
        across tasks* (which is the normal case, and what
        :attr:`n_shared_parameters` tracks) a rotated diagonal costs as much as
        the full matrix it is meant to be compressing.
        """
        raise NotImplementedError

    @property
    def n_shared_parameters(self) -> int:
        """Entries amortised across all tasks rather than stored per task."""
        return 0

    def discarded_fraction(self, P: np.ndarray) -> float:
        """``||P - Pi(P)||_F^2 / ||P||_F^2`` -- how much this basis throws away.

        Cheap, basis-agnostic, and the quantity the theory says the excess
        forgetting is made of.
        """
        num = np.linalg.norm(P - self.project(P), "fro") ** 2
        den = np.linalg.norm(P, "fro") ** 2
        return float(num / den) if den > 0 else 0.0


class Full(Basis):
    """The identity: no projection.  This is the Kalman oracle."""

    name = "full"

    def __init__(self, dim: int):
        self.dim = dim

    @property
    def n_parameters(self) -> int:
        return self.dim * (self.dim + 1) // 2

    def project(self, P):
        return P


class Diagonal(Basis):
    """Keep only the diagonal -- precisely EWC's diagonal-Fisher approximation."""

    name = "diagonal"

    def __init__(self, dim: int):
        self.dim = dim

    @property
    def n_parameters(self) -> int:
        return self.dim

    def project(self, P):
        return np.diag(np.diag(P))


@dataclass
class Partition(Basis):
    """Keep within-group covariance, discard across-group covariance.

    ``labels`` assigns every neuron to a group; the projection zeroes exactly
    the entries whose two neurons are in different groups.  Singleton groups
    reproduce :class:`Diagonal` (EWC); one big group reproduces :class:`Full`.

    This is the object that makes a connectome annotation table into a
    candidate anchoring basis.
    """

    labels: np.ndarray
    name: str = "partition"
    _groups: np.ndarray = field(default=None, repr=False)

    def __post_init__(self):
        self.labels = np.asarray(self.labels)
        self.dim = len(self.labels)
        # group ids normalised to 0..m-1
        _, self._groups = np.unique(self.labels, return_inverse=True)

    @property
    def n_groups(self) -> int:
        return int(self._groups.max()) + 1 if len(self._groups) else 0

    @property
    def group_sizes(self) -> np.ndarray:
        return np.bincount(self._groups, minlength=self.n_groups)

    @property
    def n_parameters(self) -> int:
        """Free entries = sum over groups of triangular numbers."""
        s = self.group_sizes.astype(np.int64)
        return int(np.sum(s * (s + 1) // 2))

    def project(self, P):
        g = self._groups
        return np.where(g[:, None] == g[None, :], P, 0.0)

    def indicator_span(self) -> np.ndarray:
        """Orthonormal basis of the group-indicator span (``d x n_groups``).

        Used for the principal-angle analysis: a partition is 'aligned' with a
        task when this span sits inside the task's dominant precision subspace.
        """
        C = np.zeros((self.dim, self.n_groups))
        C[np.arange(self.dim), self._groups] = 1.0
        Q, R = np.linalg.qr(C)
        keep = np.abs(np.diag(R)) > 1e-12 * max(1.0, np.abs(R).max())
        return Q[:, keep]


class RotatedDiagonal(Basis):
    """Diagonal in the coordinates of ``U`` instead of the neuron coordinates.

    ``project(P) = U diag(U^T P U) U^T``.  With ``U = I`` this is exactly
    :class:`Diagonal`; with ``U`` the task eigenbasis it is spectral anchoring.
    """

    name = "rotated-diagonal"

    def __init__(self, U: np.ndarray, name: str | None = None):
        self.U = np.asarray(U)
        self.dim = self.U.shape[0]
        if name:
            self.name = name

    @property
    def n_parameters(self) -> int:
        """Just the diagonal it keeps -- the rotation is amortised, not per task."""
        return self.dim

    @property
    def n_shared_parameters(self) -> int:
        return self.dim * (self.dim - 1) // 2

    def project(self, P):
        M = self.U.T @ P @ self.U
        return self.U @ np.diag(np.diag(M)) @ self.U.T


class Rank(Basis):
    """Truncate to the top ``r`` eigen-directions of ``P``.

    ``mode='flatten'`` spreads the discarded eigenvalues back as their mean
    (the reference implementation's water-filling choice); ``mode='drop'``
    zeroes them.  Unlike the partitions this basis is *state dependent* -- it
    re-picks its directions every step.
    """

    name = "rank"

    def __init__(self, dim: int, r: int, mode: str = "flatten"):
        self.dim, self.r, self.mode = dim, int(r), mode

    @property
    def n_parameters(self) -> int:
        # r eigenvectors (d*r) plus r eigenvalues -- a state-dependent basis
        # cannot be amortised across tasks the way a fixed one can.
        return int(self.r * (self.dim + 1))

    def project(self, P):
        if self.r >= self.dim:
            return P
        w, V = np.linalg.eigh(P)
        order = np.argsort(w)[::-1]
        keep = order[: self.r]
        Vk = V[:, keep]
        Pk = (Vk * w[keep]) @ Vk.T
        if self.mode == "drop":
            return Pk
        c = float(np.mean(w[order[self.r:]]))
        return Pk + c * (np.eye(self.dim) - Vk @ Vk.T)


# --------------------------------------------------------------------------
# constructors from data
# --------------------------------------------------------------------------
def partition_from_labels(labels) -> Partition:
    """Build a :class:`Partition` from any per-neuron annotation column."""
    return Partition(np.asarray(labels))


def random_partition(labels, rng: np.random.Generator) -> Partition:
    """Group-size-matched random control for a given partition.

    Permuting the labels keeps every group's size identical, so the random
    control has exactly the same number of free parameters as the biological
    basis it is compared against.  Without this the comparison is uninterpretable.
    """
    return Partition(rng.permutation(np.asarray(labels)))


def gram_basis(features: np.ndarray, rank: int | None = None) -> np.ndarray:
    """Eigenbasis of the feature Gram matrix -- the basis LGCL v8 used.

    ``features`` is ``(N, d)``; returns the ``(d, k)`` eigenvector matrix of
    ``features^T features / N``, strongest first.
    """
    C = features.T @ features / len(features)
    w, V = np.linalg.eigh(C)
    order = np.argsort(w)[::-1]
    V, w = V[:, order], w[order]
    if rank is None:
        rank = int((w > 1e-8 * w[0]).sum())
    return V[:, :rank]


# --------------------------------------------------------------------------
# alignment diagnostics
# --------------------------------------------------------------------------
def principal_angles(A: np.ndarray, B: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    """Principal angles (radians) between the column spans of ``A`` and ``B``."""
    Qa = np.linalg.qr(A)[0]
    Qb = np.linalg.qr(B)[0]
    s = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    return np.arccos(np.clip(s[: min(Qa.shape[1], Qb.shape[1])], -1.0, 1.0))


def alignment_score(A: np.ndarray, B: np.ndarray) -> float:
    """``mean(cos^2 theta)`` over principal angles -- 1 means perfectly aligned.

    This is the scalar the theory predicts the anchoring benefit from: LGCL v8
    showed the diagonalisation penalty is a *geometric* function of how the
    anchoring basis sits relative to the task's precision basis.
    """
    Qa = np.linalg.qr(A)[0]
    Qb = np.linalg.qr(B)[0]
    s = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    m = min(Qa.shape[1], Qb.shape[1])
    return float(np.mean(s[:m] ** 2))


def gain_mismatch_cost(P_prior: np.ndarray, J: np.ndarray, K_hat: np.ndarray) -> float:
    """Excess MSE of using a suboptimal Kalman gain.

    Implements the identity from the LGCL appendix::

        M(K) - M(K*) = tr(J (K - K*) (P_prior + J^{-1}) (K - K*)^T)

    so *any* covariance-compression scheme is analysable as a gain error.  The
    optimal gain here is ``K* = P_prior (P_prior + J^{-1})^{-1}``.
    """
    R = np.linalg.pinv(J)
    S = P_prior + R
    K_opt = P_prior @ symmetric_inverse(S)
    dK = K_hat - K_opt
    return float(np.trace(J @ dK @ S @ dK.T))
