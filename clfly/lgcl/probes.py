"""Mechanism probes for the diagonalisation penalty.

These are not reproductions -- they are experiments.  Each probes *when* the
diagonal projection that defines EWC actually costs anything, because the
published result says "almost never in d=20" and the whole project depends on
understanding that boundary.

Run ``python -m clfly.lgcl.probes`` for the report.

The headline finding (see ``docs/findings/``): the two-task one-shot
diagonalisation loss is *exactly* zero, confirming the LGCL lemma, and the
penalty stays below ~2% across a wide sweep of measurement strength, drift, and
rotation angle.  The diagonal projection discards a large share of the
covariance's Frobenius mass and almost none of the *error*.  That gap between
"information discarded" and "error caused" is precisely what a structured,
non-random substrate is supposed to close -- which is why the next step is a
real connectome rather than a better synthetic family.
"""

from __future__ import annotations

import numpy as np

from .bases import Diagonal
from .methods import run
from .model import error_tensor, sample_full, summarize

DEFAULT_CFG = dict(d=2, T=10, n=40, sigma2=1.0, q=0.05)


def relative_gap(seq, metric: str = "final_avg_error") -> float:
    """``(EWC - Kalman) / Kalman`` on the chosen error metric.

    Positive means the diagonal projection *hurt*; negative means it helped,
    which happens because the projection also shrinks the posterior and that
    shrinkage is not always harmful.  Reporting the signed quantity matters --
    the CL literature's forgetting metric is known to reward shrinkage, and a
    one-sided gap would hide that.
    """
    e = summarize(error_tensor(run("ewc", seq), seq))[metric]
    k = summarize(error_tensor(run("kalman", seq), seq))[metric]
    return (e - k) / k if k else 0.0


def two_task_lemma(alpha_degs=(5, 12, 30, 60), T: int = 2, seed: int = 0) -> dict:
    """With a single task-boundary there is no diagonalisation loss at all.

    LGCL v8's lemma: task 1's precision is diagonal in its own basis, so the
    first projection is exact; every bit of the gap comes from *recursive*
    diagonalisation after a rotation has made the posterior dense.  A T=2 run
    must therefore give exactly zero, and a T=3 run must not.
    """
    out = {}
    for T_ in (2, 3, 4):
        for a in alpha_degs:
            rng = np.random.default_rng(seed)
            seq = sample_full(rng=rng, alpha=np.deg2rad(a), rotation="cumulative",
                              **{**DEFAULT_CFG, "T": T_})
            out[f"T={T_},alpha={a}"] = relative_gap(seq)
    return out


def recursion_is_the_mechanism(alphas_deg=(12,), Ts=(2, 3, 5, 10, 20), seed: int = 0) -> dict:
    """Gap as a function of how many times the posterior gets re-diagonalised.

    If the recipe is "rotation x recursive projection", the gap must grow with
    the number of projections -- flat at T=2, then increasing.
    """
    out = {}
    for a in alphas_deg:
        for T in Ts:
            rng = np.random.default_rng(seed)
            seq = sample_full(rng=rng, alpha=np.deg2rad(a), rotation="cumulative",
                              **{**DEFAULT_CFG, "T": T})
            out[f"alpha={a},T={T}"] = relative_gap(seq)
    return out


def measurement_dominance(ns=(1, 2, 5, 10, 20, 40, 100), qs=(0.05, 0.5), alpha_deg: float = 12.0,
                          seed: int = 0) -> dict:
    """Gap vs measurement strength ``n`` and drift ``q``.

    Prediction from LGCL finding 1: when each task re-measures everything
    strongly, the current measurement dominates the prior and the discarded
    off-diagonal information is irrelevant.  The gap should collapse as ``n``
    rises -- which is exactly why random-rotation benchmarks make the diagonal
    approximation look free.
    """
    out = {}
    for n in ns:
        for q in qs:
            rng = np.random.default_rng(seed)
            seq = sample_full(rng=rng, alpha=np.deg2rad(alpha_deg), rotation="cumulative",
                              **{**DEFAULT_CFG, "n": n, "q": q})
            out[f"n={n},q={q}"] = relative_gap(seq)
    return out


def alpha_sweep(alpha_degs=tuple(range(0, 91, 6)), n: int = 2, q: float = 0.05,
                seed: int = 0) -> dict:
    """Search for the published unimodal peak in the coordinate basis.

    Endpoints are pinned by geometry: 0 deg is aligned, and 90 deg per task is
    an axis swap, which in 2-D is still diagonal, so both must vanish.  Anything
    in between is the question.  We find no interior peak here.
    """
    out = {}
    for a in alpha_degs:
        rng = np.random.default_rng(seed)
        seq = sample_full(rng=rng, alpha=np.deg2rad(a), rotation="cumulative",
                          **{**DEFAULT_CFG, "n": n, "q": q})
        out[f"{a}deg"] = relative_gap(seq)
    return out


def discarded_energy_vs_error(T: int = 10, alpha_deg: float = 12.0, seed: int = 0) -> dict:
    """How much covariance mass the diagonal projection throws away, per step.

    The punchline of the probe suite: the projection discards a *large* fraction
    of the posterior's Frobenius mass and causes a *tiny* amount of extra error.
    Those two numbers are the quantitative statement of "the coordinate basis is
    the wrong basis but random tasks do not care", and closing that gap is the
    job of a structured substrate.
    """
    from .kalman import kalman_update

    d = DEFAULT_CFG["d"]
    rng = np.random.default_rng(seed)
    seq = sample_full(rng=rng, alpha=np.deg2rad(alpha_deg), rotation="cumulative",
                      **{**DEFAULT_CFG, "T": T})
    basis = Diagonal(d)
    theta, P = np.zeros(d), np.eye(d)
    discarded, norm = [], []
    for k in range(seq.T):
        P = P + seq.q * np.eye(d)
        theta, P = kalman_update(theta, P, seq.J[k], seq.y[k])
        discarded.append(basis.discarded_fraction(P))
        norm.append(float(np.linalg.norm(P, "fro")))
    return {
        "mean_discarded_fraction": float(np.mean(discarded)),
        "max_discarded_fraction": float(np.max(discarded)),
        "discarded_fraction_by_step": discarded,
        "median_cov_frobenius": float(np.median(norm)),
        "relative_error_gap": relative_gap(seq),
    }


def anisotropy_drives_the_gap(
    decays=(0.85, 0.25, 0.05),
    alpha_degs=tuple(range(0, 91, 9)),
    runs: int = 60,
    T: int = 10,
    seed0: int = 0,
) -> dict:
    """The penalty is a function of task *anisotropy*, not of rotation alone.

    A task precision ``J_k = U diag(s) U^T`` with a flat spectrum is nearly
    isotropic, so rotating it changes almost nothing and the diagonal projection
    is exact regardless of angle.  As the spectrum steepens, the same rotation
    starts to cost something.

    Measured (d=2, T=10, n=40, q=0.05, 60 seeds, mean +/- s.e.):

    ===========  ==========================  ==================
    decay (s2)   largest |gap|               reading
    ===========  ==========================  ==================
    0.85 (0.85)  0.0002 +/- 0.0003           exactly zero
    0.25 (0.25)  0.0135 +/- 0.0065           sign-unstable
    0.05 (0.05)  0.0942 +/- 0.0363           systematic, positive
    ===========  ==========================  ==================

    Together with :func:`alpha_sweep` this pins down the negative result in
    ``docs/findings/``: the published unimodal peak does not appear in the
    coordinate basis, but the *ingredient* it needs -- an anisotropic, low
    effective-rank task -- does drive the penalty, which is exactly the
    ingredient a real connectome supplies.
    """
    out = {}
    for decay in decays:
        per_angle = {}
        for a in alpha_degs:
            vals = []
            for s in range(seed0, seed0 + runs):
                rng = np.random.default_rng(s)
                seq = sample_full(rng=rng, alpha=np.deg2rad(a), rotation="cumulative",
                                  **{**DEFAULT_CFG, "T": T, "decay": decay})
                vals.append(relative_gap(seq))
            per_angle[a] = (float(np.mean(vals)), float(np.std(vals) / np.sqrt(runs)))
        gaps = {a: m for a, (m, _) in per_angle.items()}
        peak_a = max(gaps, key=lambda a: abs(gaps[a]))
        out[f"decay={decay}.max_abs_gap"] = abs(gaps[peak_a])
        out[f"decay={decay}.max_at_deg"] = float(peak_a)
        out[f"decay={decay}.sem_at_peak"] = per_angle[peak_a][1]
        out[f"decay={decay}.gap_at_0deg"] = gaps[alpha_degs[0]]
        out[f"decay={decay}.gap_at_90deg"] = gaps[alpha_degs[-1]]
    return out


PROBES = {
    "two_task_lemma": two_task_lemma,
    "recursion_is_the_mechanism": recursion_is_the_mechanism,
    "measurement_dominance": measurement_dominance,
    "alpha_sweep": alpha_sweep,
    "discarded_energy_vs_error": discarded_energy_vs_error,
    "anisotropy_drives_the_gap": anisotropy_drives_the_gap,
}


def main(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--only", default=None)
    args = p.parse_args(argv)

    names = args.only.split(",") if args.only else list(PROBES)
    for name in names:
        print(f"\n=== {name} ===")
        for k, v in PROBES[name]().items():
            print(f"  {k:24} {v:+.6f}" if isinstance(v, float) else f"  {k:24} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
