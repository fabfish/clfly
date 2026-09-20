"""The LGCL generative model — Linear-Gaussian Continual Learning.

A learner sees tasks one at a time.  Between tasks the true parameter drifts
as a Gaussian random walk of rate ``q``; each task supplies a single Gaussian
measurement of the current parameter with precision ``J_k``.  Everything
downstream -- EWC, replay, spectral truncation, the Kalman oracle -- is a
different way of fusing those measurements, so this module *is* the substrate
the rest of the project reasons on.

Ported from ``reference/lgcl_source/lgcl_toy.py`` (the author's original
experiment script).  The RNG call order is preserved deliberately, so published
reference numbers reproduce exactly rather than approximately.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_DECAY = 0.85


@dataclass(frozen=True)
class Sequence:
    """One realised LGCL problem instance.

    Attributes
    ----------
    d : parameter dimension.
    q : drift rate (process noise per task transition).
    theta : ``(T, d)`` true parameter at the moment task ``k`` is observed.
    J : ``(T, d, d)`` task precision (= expected Fisher) matrices.
    Sigma : ``(T, d, d)`` task input covariances, i.e. the weights the error
        metric is measured in.  ``Sigma_k`` is the task's *own* notion of which
        directions matter.
    y : ``(T, d)`` sufficient statistic (the OLS estimate) for each task.
    U : ``(T, d, d)`` eigenbases of the task covariances, when the generator
        is geometric rather than random.
    """

    d: int
    q: float
    theta: np.ndarray
    J: np.ndarray
    Sigma: np.ndarray
    y: np.ndarray
    U: np.ndarray | None = None

    def __len__(self) -> int:
        return len(self.J)

    @property
    def T(self) -> int:
        return len(self.J)

    def precision_basis(self, k: int, rank: int | None = None, tol: float = 1e-8):
        """Eigenvectors of ``J_k``, strongest first — the task's own basis.

        ``rank`` keeps only directions with eigenvalue above ``tol * max``.
        This is the object the whole "which basis should you anchor in?"
        question is phrased against.
        """
        w, V = np.linalg.eigh(self.J[k])
        order = np.argsort(w)[::-1]
        w, V = w[order], V[:, order]
        if rank is None:
            rank = int((w > tol * w[0]).sum())
        return V[:, :rank], w[:rank]


# --------------------------------------------------------------------------
# task generators
# --------------------------------------------------------------------------
def spectrum(d: int, decay: float = DEFAULT_DECAY) -> np.ndarray:
    """Decaying eigenvalue spectrum ``decay ** arange(d)`` -> low effective rank."""
    return decay ** np.arange(d)


def _covariances_from_bases(U: np.ndarray, s: np.ndarray, n: float, sigma2: float):
    """``Sigma_k = U_k diag(s) U_k^T`` and ``J_k = n Sigma_k / sigma2``."""
    J = np.einsum("kij,j,klj->kil", U, s, U) * (n / sigma2)
    Sigma = np.einsum("kij,j,klj->kil", U, s, U)
    return Sigma, J


def random_bases(d: int, T: int, rng: np.random.Generator) -> np.ndarray:
    """``T`` independent Haar-random orthonormal bases (consumes ``T`` QR draws)."""
    return np.stack([np.linalg.qr(rng.standard_normal((d, d)))[0] for _ in range(T)])


def rotated_bases(d: int, T: int, alpha: float, plane=(0, 1)) -> np.ndarray:
    """``T`` copies of a rotation by ``alpha`` inside a single 2-D plane.

    ``alpha = 0`` gives the aligned case; a fixed ``alpha`` gives one constant
    misalignment (this is the exp-3 family when paired with constant bases).
    """
    i, j = plane
    R = np.eye(d)
    c, s = np.cos(alpha), np.sin(alpha)
    R[i, i], R[i, j], R[j, i], R[j, j] = c, -s, s, c
    return np.stack([R] * T)


def cumulative_rotation_bases(d: int, T: int, alpha_step: float) -> np.ndarray:
    """Task ``k``'s basis is the axis basis rotated by ``k * alpha_step``.

    This is the exp-3 / v8-Gram family: a *sequence* of small misalignments
    rather than one fixed one.  The reference implementation rotates inside the
    first two coordinates.
    """
    bases = []
    for k in range(T):
        a = k * alpha_step
        R = np.eye(d)
        c, s = np.cos(a), np.sin(a)
        R[0, 0], R[0, 1], R[1, 0], R[1, 1] = c, -s, s, c
        bases.append(R)
    return np.stack(bases)


def partial_observation_bases(d, T, obs_dim, rng):
    """Bases whose leading ``obs_dim`` columns span the observed subspace.

    Used by the partial-observability regime: the task only ever sees ``obs_dim``
    directions, so its precision is low rank and old directions can only be
    remembered, never re-measured.
    """
    U = random_bases(d, T, rng)
    return U


# --------------------------------------------------------------------------
# sampling
# --------------------------------------------------------------------------
def simulate(theta0: np.ndarray, J: np.ndarray, q: float, rng: np.random.Generator):
    """Sample the drift trajectory and one sufficient statistic per task.

    Faithful to the reference: ``theta`` is recorded *before* the drift for
    task ``k``, and the measurement noise is drawn from ``N(0, J_k^{-1})``.
    """
    T, d = J.shape[0], J.shape[1]
    theta = theta0.copy()
    thetas, hats = [], []
    for k in range(T):
        thetas.append(theta.copy())
        L = np.linalg.cholesky(np.linalg.inv(J[k]))
        hats.append(theta + L @ rng.standard_normal(d))
        theta = theta + np.sqrt(q) * rng.standard_normal(d)
    return np.stack(thetas), np.stack(hats)


def sample_full(d, T, n, sigma2, q, rng, *, decay=DEFAULT_DECAY,
                rotation="random", alpha=None) -> Sequence:
    """Fully observed regime: every task measures all ``d`` directions.

    ``rotation`` is ``"random"`` (exp 1), ``"axis"`` (aligned) or ``"cumulative"``
    (exp 3, ``alpha`` is the per-step rotation in radians).
    """
    s = spectrum(d, decay)
    if rotation == "random":
        U = random_bases(d, T, rng)
    elif rotation == "axis":
        U = np.stack([np.eye(d)] * T)
    elif rotation == "angle":
        if alpha is None:
            raise ValueError("rotation='angle' needs alpha")
        U = rotated_bases(d, T, alpha)
    elif rotation == "cumulative":
        U = cumulative_rotation_bases(d, T, alpha)
    else:
        raise ValueError(f"unknown rotation mode {rotation!r}")
    Sigma, J = _covariances_from_bases(U, s, n, sigma2)
    theta, hats = simulate(rng.standard_normal(d), J, q, rng)
    return Sequence(d=d, q=q, theta=theta, J=J, Sigma=Sigma, y=hats, U=U)


def sample_partial(d, T, n, sigma2, q, rng, *, obs_dim) -> Sequence:
    """Partially observed regime: each task measures an ``obs_dim`` subspace.

    ``Sigma_k`` is the projection onto that subspace (so the error metric only
    cares about the directions the task actually used) and ``J_k`` is a scaled
    projection, hence rank ``obs_dim`` and non-invertible.
    """
    U = random_bases(d, T, rng)
    P_obs = U[:, :, :obs_dim] @ np.transpose(U[:, :, :obs_dim], (0, 2, 1))
    Sigma = P_obs
    J = (n / sigma2) * P_obs

    theta = rng.standard_normal(d)
    thetas = np.stack([theta.copy()] * T)
    hats = []
    for k in range(T):
        w, V = np.linalg.eigh(J[k])
        idx = np.argsort(w)[::-1][:obs_dim]
        Uo = V[:, idx]
        hats.append(theta + Uo @ (rng.standard_normal(obs_dim) / np.sqrt(n / sigma2)))
    return Sequence(d=d, q=q, theta=thetas, J=J, Sigma=Sigma,
                    y=np.stack(hats), U=U)


def error_tensor(ests: np.ndarray, seq: Sequence) -> np.ndarray:
    """``E[k, j]`` = error of the estimate after task ``k`` on task ``j``.

    Measured in the *function* space of task ``j`` -- weighted by ``Sigma_j`` --
    not in parameter space.  Entries with ``j > k`` are zero (not yet seen).
    """
    T = len(seq)
    E = np.zeros((T, T))
    for k in range(T):
        for j in range(k + 1):
            diff = ests[k] - seq.theta[j]
            E[k, j] = diff @ seq.Sigma[j] @ diff
    return E


def summarize(E: np.ndarray) -> dict:
    """Final average error and the standard forgetting measure.

    ``forgetting`` averages ``E[T-1, j] - E[j, j]`` over the first ``T-1``
    tasks, i.e. how much worse each old task got by the end.

    NOTE: this metric rewards shrinkage bias -- an estimator that pulls toward
    zero can score well on it while being wrong (LGCL v8 audit note).  Use
    :func:`clfly.lgcl.metrics.decompose_forgetting` when that matters.
    """
    T = E.shape[0]
    final_avg = float(np.mean([E[T - 1, j] for j in range(T)]))
    forgetting = float(np.mean([E[T - 1, j] - E[j, j] for j in range(T - 1)]))
    return {"final_avg_error": final_avg, "forgetting": forgetting}
