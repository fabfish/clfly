"""Kalman machinery for the LGCL model.

Two families live here:

*Filters* — causal, one pass forward, optionally with the posterior covariance
projected onto an anchoring basis at every step.  This is the single mechanism
that unifies every method in the project: EWC is ``basis=Diagonal()``, spectral
truncation is ``basis=Rank(r)``, the oracle is ``basis=Full()``.

*Smoothers* — non-causal, use all data.  The RTS smoother is the **information
limit** of the model: the best any learner with unlimited memory and unlimited
compute could do.  It is the reference line that separates "error the
environment forces on you" from "error your method caused", which the LGCL memo
argues every continual-learning paper should report.
"""

from __future__ import annotations

import numpy as np

from .bases import Basis
from .linalg import symmetric_inverse


def kalman_update(theta, P, J, y, basis: Basis | None = None):
    """Information-form measurement update, then optional covariance projection.

    ``P`` is the *predicted* prior covariance; ``J`` the measurement precision;
    ``y`` the sufficient statistic.  The projection is applied to the posterior
    covariance only — the mean is left alone, matching the reference
    implementation and the "EWC = diagonalised covariance" reading.
    """
    Pinv = symmetric_inverse(P)
    Pn = symmetric_inverse(Pinv + J)
    thn = Pn @ (Pinv @ theta + J @ y)
    if basis is not None:
        Pn = basis.project(Pn)
    return thn, Pn


def filter_sequence(seq, basis: Basis | None = None, P0_scale: float = 1.0):
    """Run one causal pass; return ``(T, d)`` estimates and covariances.

    Every task is preceded by the drift prediction ``P <- P + qI``, which is what
    turns the environment's non-stationarity into the learner's stability /
    plasticity trade-off.
    """
    d = seq.d
    theta = np.zeros(d)
    P = P0_scale * np.eye(d)
    ests, covs = [], []
    for k in range(seq.T):
        P = P + seq.q * np.eye(d)
        theta, P = kalman_update(theta, P, seq.J[k], seq.y[k], basis)
        ests.append(theta.copy())
        covs.append(P.copy())
    return np.stack(ests), np.stack(covs)


def rts_smoother(seq, P0_scale: float = 1.0):
    """Exact RTS smoother — the information limit of the LGCL model.

    Returns ``(estimates, covariances)``.  Because the model is linear-Gaussian
    this is exact, so ``tr(P_s[k] Sigma_k)`` is the *irreducible* error on task
    ``k``: no learner can beat it, whatever its memory or compute.
    """
    d = seq.d
    T = seq.T
    I = np.eye(d)

    theta_f = np.zeros((T, d))
    P_f = np.zeros((T, d, d))
    theta_pred = np.zeros((T, d))
    P_pred = np.zeros((T, d, d))

    theta, P = np.zeros(d), P0_scale * I
    for k in range(T):
        P = P + seq.q * I
        theta_pred[k], P_pred[k] = theta, P
        theta, P = kalman_update(theta, P, seq.J[k], seq.y[k])
        theta_f[k], P_f[k] = theta, P

    theta_s = theta_f.copy()
    P_s = P_f.copy()
    for k in range(T - 2, -1, -1):
        C = P_f[k] @ symmetric_inverse(P_pred[k + 1])
        theta_s[k] = theta_f[k] + C @ (theta_s[k + 1] - theta_pred[k + 1])
        P_s[k] = P_f[k] + C @ (P_s[k + 1] - P_pred[k + 1]) @ C.T
    return theta_s, P_s


def irreducible_error(seq, P0_scale: float = 1.0) -> np.ndarray:
    """``(T, T)`` analytic error floor: ``tr(P_s[j] Sigma_j)`` after task ``k``.

    Since the smoother at time ``k`` only sees data up to ``k``, the floor for
    task ``j`` after task ``k`` is ``tr(P_s[j|k] Sigma_j)``.  Here we use the
    full-horizon smoother, which is the usual "genie with all the data" reading.
    """
    _, P_s = rts_smoother(seq, P0_scale)
    return np.array([np.trace(P_s[j] @ seq.Sigma[j]) for j in range(seq.T)])


def gain_mismatch_excess(seq, basis: Basis, P0_scale: float = 1.0) -> np.ndarray:
    """Per-step MSE excess attributable to the basis projection.

    Diagnostic that decomposes an anchoring basis's cost into per-task steps,
    instead of only reporting the endpoint.  Uses the optimal-gain identity: the
    projected covariance becomes the next step's prior, and the induced gain
    error is priced exactly.
    """
    d = seq.d
    P = P0_scale * np.eye(d)
    out = []
    for k in range(seq.T):
        P = P + seq.q * np.eye(d)
        R = np.linalg.pinv(seq.J[k])
        S = P + R
        K_opt = P @ symmetric_inverse(S)
        P_hat = basis.project(P)
        K_basis = P_hat @ symmetric_inverse(P_hat + R)
        dK = K_basis - K_opt
        out.append(float(np.trace(seq.J[k] @ dK @ S @ dK.T)))
        _, P = kalman_update(np.zeros(d), P, seq.J[k], seq.y[k], basis)
    return np.array(out)
