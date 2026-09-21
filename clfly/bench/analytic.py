"""Analytic expected error for LGCL filters — the effect size without sampling noise.

The realized error used everywhere else is a *single draw*: one trajectory of
``theta`` and one set of measurement noises.  On the connectome substrate that
sampling deviation dominates everything — the task geometry is reproducible to four
decimals across seeds while the realized gap swings by more than its own mean (see
``docs/findings/2026-09-22-metric-instability.md``).  Reporting an effect size from
such a quantity needs dozens of seeds to resolve anything, and the seeds are
expensive.

But the LGCL model is linear-Gaussian, and every filter in this project is a
*linear* function of the observations.  So the expected error can be computed in
closed form, exactly, with no draws at all.  What remains varying across seeds is
then only the task geometry — the quantity the experiments are actually about —
rather than a nuisance sampling term.

**Derivation.**  Write the filter's total linear response as
``theta_hat_k = sum_{j<=k} R_kj y_j`` (the prior mean is zero, so there is no affine
term).  Substituting ``y_j = theta_j + eps_j``::

    e = theta_hat_k - theta_m
      = [ sum_j R_kj theta_j - theta_m ]  +  [ sum_j R_kj eps_j ]

The two brackets are independent, so

    E[e e^T] = E[a a^T] + E[b b^T]
    E[a a^T] = sum_{j,l} R_kj S_jl R_kl^T  -  2 sum_j R_kj S_jm  +  S_mm I
    E[b b^T] = sum_j R_kj pinv(J_j) R_kj^T

with ``S_jl = (P0 + min(j,l) q) I`` the trajectory covariance and ``pinv(J_j)`` the
measurement-noise covariance.  Taking ``tr(Sigma_m .)`` gives the expected error on
task ``m`` after task ``k``.

The response matrices come from one filter pass.  With
``Pn_k = (P_prior,k^{-1} + J_k)^{-1}`` the *unprojected* posterior that the mean
update uses, and ``M_k = Pn_k P_prior,k^{-1}``::

    R_kk = Pn_k J_k,     R_kj = M_k R_{k-1,j}  for j < k

Note ``M_k`` uses the *unprojected* posterior because ``kalman_update`` applies the
basis projection to the stored covariance only, after the mean has been formed —
which is exactly the "EWC = diagonalised covariance" convention the project uses.
"""

from __future__ import annotations

import numpy as np

from ..lgcl.bases import Basis
from ..lgcl.linalg import symmetric_inverse


def response_matrices(seq, basis: Basis | None = None, P0_scale: float = 1.0):
    """``R[k][j]`` = d(theta_hat_k) / d(y_j), for j <= k.

    One pass over the tasks.  Also returns the unprojected posteriors ``Pn`` and the
    projected ones ``P_post``, which the variance diagnostics need.
    """
    T, d = seq.T, seq.d
    R: list[list[np.ndarray]] = [[] for _ in range(T)]
    Pn, P_post = [], []
    P = P0_scale * np.eye(d)
    for k in range(T):
        P_prior = P + seq.q * np.eye(d)
        Pinv = symmetric_inverse(P_prior)
        Pn_k = symmetric_inverse(Pinv + seq.J[k])
        M_k = Pn_k @ Pinv
        for j in range(k):
            R[k].append(M_k @ R[k - 1][j])
        R[k].append(Pn_k @ seq.J[k])
        Pn.append(Pn_k)
        P = basis.project(Pn_k) if basis is not None else Pn_k
        P_post.append(P)
    return R, Pn, P_post


def trajectory_cov(seq, P0_scale: float = 1.0) -> np.ndarray:
    """``S[j, l] = Cov(theta_j, theta_l)`` as a scalar matrix, i.e. ``s_jl * I``.

    ``P0 + min(j,l) * q`` when the parameter actually drifted, ``P0`` when it did
    not.  See :attr:`clfly.lgcl.model.Sequence.drifted` — the filter always *believes*
    in the drift, which is what makes the stability/plasticity trade-off, but the
    reference partial-observation family holds ``theta`` fixed.
    """
    idx = np.arange(seq.T)
    if seq.drifted:
        return P0_scale + seq.q * np.minimum.outer(idx, idx)
    return P0_scale * np.ones((seq.T, seq.T))


def expected_error_matrix(seq, basis: Basis | None = None,
                          P0_scale: float = 1.0) -> np.ndarray:
    """``E[k, m]`` = expected error on task ``m`` of the estimate after task ``k``.

    Exact, and free of Monte Carlo noise.  Same convention as
    :func:`clfly.lgcl.model.error_tensor`: entries with ``m > k`` are zero, and the
    metric is the task's own ``Sigma_m``.
    """
    T, d = seq.T, seq.d
    R, _, _ = response_matrices(seq, basis, P0_scale)
    q, P0 = seq.q, P0_scale
    S = trajectory_cov(seq, P0_scale)
    Jpinv = [np.linalg.pinv(seq.J[j]) for j in range(T)]

    E = np.zeros((T, T))
    for k in range(T):
        # U[t] = sum_{j>=t} R_kj, so that sum_{j,l} s_jl R_kj R_kl^T decomposes as
        # P0 * U[0] U[0]^T + q * sum_{t>=1} U[t] U[t]^T, using
        # min(j,l) = sum_{t>=1} [j>=t] [l>=t].  O(k) matrix products instead of O(k^2).
        #
        # The q-term comes from the min(j,l) structure, which exists only when theta
        # actually drifted.  Adding it unconditionally was a bug: it inflated the
        # expected error by ~3x for the non-drifting partial-observation family while
        # leaving the drifting case correct, so the Monte Carlo validation (which
        # checks both) is what caught it.
        U = [None] * (k + 1)
        acc = np.zeros((d, d))
        for t in range(k, -1, -1):
            acc = acc + R[k][t]
            U[t] = acc

        G = P0 * (U[0] @ U[0].T)
        if seq.drifted:
            for t in range(1, k + 1):
                G += q * (U[t] @ U[t].T)
        N = np.zeros((d, d))
        for j in range(k + 1):
            N += R[k][j] @ Jpinv[j] @ R[k][j].T

        for m in range(k + 1):
            Sm = seq.Sigma[m]
            total = float(np.sum(Sm * (G + N).T))          # tr(Sm @ (G+N))
            cross = np.zeros((d, d))
            for j in range(k + 1):
                if S[j, m]:
                    cross += S[j, m] * R[k][j]
            total -= 2.0 * float(np.sum(Sm * cross.T))
            total += S[m, m] * float(np.trace(Sm))
            E[k, m] = total
    return E


def summarize_expected(E: np.ndarray) -> dict:
    """Final average error and forgetting, from an expected-error matrix."""
    T = E.shape[0]
    return {
        "final_avg_error": float(np.mean([E[T - 1, j] for j in range(T)])),
        "forgetting": float(np.mean([E[T - 1, j] - E[j, j] for j in range(T - 1)])),
    }


def expected_oracle(seq, P0_scale: float = 1.0) -> dict:
    """The oracle's expected error — the reference line, analytically."""
    return summarize_expected(expected_error_matrix(seq, None, P0_scale))


def projection_pressure(seq, basis: Basis | None = None, P0_scale: float = 1.0) -> float:
    """How much of the *exact* filter's posterior trajectory the basis discards.

    A candidate a-priori predictor for the anchoring benefit, and the most direct
    formalisation of LGCL's mechanism: the penalty is the off-structure covariance
    the projection removes.  Two design choices make it a fair candidate.

    It runs the **full** filter, whose prior trajectory is basis-independent.  So
    the number is a property of (partition, tasks) alone and can be computed before
    any anchored filter is run — which is what "predictor" has to mean.

    It weights the discarded part by the task's measurement information, in the
    metric that makes it dimensionless::

        pressure = sum_k  || J_k^{1/2} disc_k J_k^{1/2} ||_F^2
                        / || J_k^{1/2} P_pred,k J_k^{1/2} ||_F^2

    without the weighting it would merely re-derive ``constrained_fraction``, which
    is already known to order the rungs — so the weighting is what gives it a chance
    of also separating a biological partition from a size-matched random one, where
    ``constrained_fraction`` is identical by construction.
    """
    d = seq.d
    P = P0_scale * np.eye(d)
    total = 0.0
    for k in range(seq.T):
        P_pred = P + seq.q * np.eye(d)
        disc = P_pred - (basis.project(P_pred) if basis is not None else P_pred)
        J = seq.J[k]
        Js = _psd_sqrt(J)
        num = float(np.sum((Js @ disc @ Js) ** 2))
        den = float(np.sum((Js @ P_pred @ Js) ** 2))
        if den > 0:
            total += num / den
        # advance the exact filter (basis-independent)
        Pn = symmetric_inverse(symmetric_inverse(P_pred) + J)
        P = Pn
    return total


def _psd_sqrt(M: np.ndarray, tol: float = 1e-12) -> np.ndarray:
    """Symmetric PSD square root, truncating non-positive eigenvalues to zero."""
    w, V = np.linalg.eigh((M + M.T) * 0.5)
    w = np.clip(w, 0.0, None)
    keep = w > tol * max(1.0, float(w.max())) if w.size else w
    if not keep.any():
        return np.zeros_like(M)
    return (V[:, keep] * np.sqrt(w[keep])) @ V[:, keep].T


def predictor_table(sequences, basis_factory) -> list[dict]:
    """Evaluate candidate predictors against the analytic excess, per basis.

    ``basis_factory`` is called with an index to give each replicate its own random
    control.  Returns one row per basis with the analytic excess, the projection
    pressure, and the principal-angle alignment excess, so the three can be ranked
    against each other.
    """
    rows = []
    for i, basis in enumerate(basis_factory()):
        ex = analytic_excess(sequences, basis)
        press = float(np.mean([projection_pressure(s, basis) for s in sequences]))
        rows.append({"basis": getattr(basis, "name", f"basis{i}"),
                     "excess": ex["excess_mean"], "excess_sem": ex["excess_sem"],
                     "pressure": press})
    return rows


def spearman(x, y) -> float:
    """Rank correlation, with ties averaged."""
    x, y = np.asarray(x, float), np.asarray(y, float)

    def rank(v):
        order = np.argsort(np.argsort(v, kind="stable"), kind="stable")
        return order.astype(float)

    rx, ry = rank(x) - rank(x).mean(), rank(y) - rank(y).mean()
    denom = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / denom) if denom else float("nan")


def analytic_excess(sequences, basis: Basis | None = None,
                    P0_scale: float = 1.0) -> dict:
    """Pooled excess error over a list of task sequences, with no sampling noise.

    Each sequence contributes one deterministic number for the filter and one for
    the oracle; the spread reported is the spread of the *excess* across task
    geometries, which is the scientific variable rather than a nuisance term.
    """
    excess, ewc, orc = [], [], []
    for seq in sequences:
        a = summarize_expected(expected_error_matrix(seq, basis, P0_scale))
        o = expected_oracle(seq, P0_scale)
        excess.append(a["final_avg_error"] - o["final_avg_error"])
        ewc.append(a["final_avg_error"])
        orc.append(o["final_avg_error"])
    excess = np.asarray(excess)
    n = len(excess)
    sem = float(excess.std(ddof=1) / np.sqrt(n)) if n > 1 else 0.0
    return {
        "n": n,
        "excess_mean": float(excess.mean()),
        "excess_sem": sem,
        "excess_sd": float(excess.std(ddof=1)) if n > 1 else 0.0,
        "ewc_mean": float(np.mean(ewc)),
        "oracle_mean": float(np.mean(orc)),
        "gap_of_means": float(excess.mean() / np.mean(orc)) if np.mean(orc) else float("nan"),
    }
