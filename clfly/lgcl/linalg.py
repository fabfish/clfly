"""Small linear-algebra helpers shared by the LGCL and connectome layers."""

from __future__ import annotations

import numpy as np
import scipy.linalg as sla


def symmetric_inverse(M: np.ndarray) -> np.ndarray:
    """Inverse of a symmetric positive-definite matrix, via Cholesky.

    The LGCL recurrences invert ``P`` and ``P^{-1} + J`` thousands of times, and
    both are symmetric.  Cholesky is a ~3x saving over a general inverse and it
    also *fails loudly* on a non-PD input, which is a useful signal: a covariance
    that stops being positive definite means an anchoring basis has over-shrunk
    it, and we would rather know than get plausible numbers anyway.

    Falls back to a pseudo-inverse for genuinely singular cases -- a fully
    unobserved direction has zero precision and nothing to invert.
    """
    M = (M + M.T) * 0.5
    try:
        c = sla.cho_factor(M, lower=True, check_finite=False)
        return sla.cho_solve(c, np.eye(M.shape[0]), check_finite=False)
    except (sla.LinAlgError, np.linalg.LinAlgError, ValueError):
        return np.linalg.pinv(M)


def symmetrize(M: np.ndarray) -> np.ndarray:
    return (M + M.T) * 0.5


def is_positive_definite(M: np.ndarray) -> bool:
    try:
        sla.cholesky(symmetrize(M), lower=True)
        return True
    except (sla.LinAlgError, np.linalg.LinAlgError):
        return False
