"""The oracle reference line, and the task-geometry readings.

Every experiment in the project must report its result against the exact Kalman /
RTS information limit, so that "better than baseline" is always readable as a
fraction of the gap that actually exists rather than as a free-standing number.
Putting that here means an experiment cannot accidentally omit it, and that the
definition of "the gap" is identical everywhere.

Three functions, all of which were previously copy-pasted into each experiment:

``gap_vs_oracle``     excess error of a basis-anchored filter over the exact
                      Kalman oracle, as a relative fraction.
``task_subspaces``    the leading precision subspace of each task.
``task_geometry``     how much the tasks overlap and how rich their spectra are
                      -- the quantities a topology null is supposed to move.
"""

from __future__ import annotations

import numpy as np

from ..lgcl.bases import Full, alignment_score
from ..lgcl.kalman import filter_sequence
from ..lgcl.methods import AnchoredFilter
from ..lgcl.model import error_tensor, summarize


def oracle_errors(seq) -> dict:
    """The exact filter's final average error and forgetting -- the reference line."""
    return summarize(error_tensor(filter_sequence(seq, Full(seq.d))[0], seq))


def gap_vs_oracle(seq, basis, keys=("final_avg_error",)) -> dict | float:
    """Excess error of ``basis``'s filter over the oracle, as a relative fraction.

    Returns a single float when one key is requested and a dict otherwise.
    ``seq`` must be a :class:`~clfly.lgcl.model.Sequence`; the oracle is
    recomputed per call, which is cheap next to the filter itself and makes the
    reference impossible to forget.
    """
    ref = oracle_errors(seq)
    got = summarize(error_tensor(AnchoredFilter(basis).run(seq), seq))
    out = {}
    for key in keys:
        r = ref[key]
        out[key] = (got[key] - r) / r if r else float("nan")
    return out[keys[0]] if len(keys) == 1 else out


def task_subspaces(seq, ranks, top: int | None = None) -> list[np.ndarray]:
    """Leading precision subspace of each task, strongest directions first.

    **``top`` is not cosmetic.**  Passing the task's *numerical rank* returns the
    task's entire range space, and for these tasks that space is set by which
    neurons the assembly recruited -- it is independent of how strongly each is
    driven.  Measured: the subspaces are bit-identical across a 15x change in the
    drive concentration that moves the effective rank from 55 to 3.5.  A predictor
    built on that space therefore cannot see the spectral structure it is supposed
    to be testing, which is the most likely reason the principal-angle alignment
    scalar failed to rank the anchoring bases in ``e3``.

    Pass ``top`` to use a spectrally *selected* subspace (``top << rank``) instead.
    The default keeps the historical behaviour so recorded runs stay comparable.
    """
    out = []
    for k in range(seq.T):
        w, V = np.linalg.eigh(seq.J[k])
        take = ranks[k] if top is None else min(int(top), ranks[k])
        out.append(V[:, np.argsort(w)[::-1][:take]])
    return out


def task_geometry(seq, ranks) -> dict:
    """Overlap and spectral richness of the task sequence.

    Four readings, because "interference" is easy to assert and hard to pin down,
    and because Phase 1 identified a *different* driver than overlap:

    ``consecutive_alignment`` / ``all_pairs_alignment``  mean ``cos²`` between task
        precision subspaces.  High means tasks live where the last one did.
    ``effective_rank``  participation ratio ``1 / Σ w_i²`` of each task's
        normalised precision spectrum, averaged.  Equals the support size for a
        flat spectrum, falls toward 1 as it concentrates, so
        ``flattening = effective_rank / rank`` measures concentration *within* the
        observed subspace.
    ``top_eig_share``  share carried by the single strongest direction, the
        crudest anisotropy reading.
    """
    V = task_subspaces(seq, ranks)
    consec = [alignment_score(V[k], V[k + 1]) for k in range(len(V) - 1)]
    pairs = [alignment_score(V[j], V[k])
             for j in range(len(V)) for k in range(j + 1, len(V))]

    eff, top = [], []
    for k in range(seq.T):
        w = np.linalg.eigvalsh(seq.J[k])
        w = w[w > 1e-12 * max(1.0, float(w.max()))] if w.size else w
        if w.size == 0:
            continue
        w = w / w.sum()
        eff.append(1.0 / float(np.sum(w ** 2)))
        top.append(float(w.max()))

    mean_rank = float(np.mean(ranks))
    return {
        "consecutive_alignment": float(np.mean(consec)) if consec else float("nan"),
        "all_pairs_alignment": float(np.mean(pairs)) if pairs else float("nan"),
        "mean_rank": mean_rank,
        "mean_rank_fraction": mean_rank / seq.d,
        "effective_rank": float(np.mean(eff)) if eff else float("nan"),
        "flattening": float(np.mean(eff)) / mean_rank if eff and mean_rank else float("nan"),
        "top_eig_share": float(np.mean(top)) if top else float("nan"),
        "chance_alignment": mean_rank / seq.d,
    }


def rank_of(seq, k: int, tol: float = 1e-10) -> int:
    """Numerical rank of task ``k``'s precision."""
    w = np.linalg.eigvalsh(seq.J[k])
    return int(np.sum(w > tol * max(1.0, float(w.max()))))


def error_levels(seq, basis) -> dict:
    """Absolute errors for ``basis`` and for the oracle -- report these alongside the gap.

    The gap is a ratio of two small, close quantities, and that ratio is where the
    instability lives: the *errors* are stable to ~1e-3 while their relative
    difference is not (see :func:`gap_bandwidth`).  Quoting only the ratio hides
    that, so experiments should carry both.
    """
    oracle = oracle_errors(seq)
    got = summarize(error_tensor(AnchoredFilter(basis).run(seq), seq))
    return {
        "ewc_final": got["final_avg_error"],
        "oracle_final": oracle["final_avg_error"],
        "excess_final": got["final_avg_error"] - oracle["final_avg_error"],
        "ewc_forgetting": got["forgetting"],
        "oracle_forgetting": oracle["forgetting"],
    }


def paired_excess(sequences, basis) -> dict:
    """Effect size across seeds, on the scale that is actually stable.

    The gap is a ratio of two small, close numbers, so it inherits the *relative*
    variance of the EWC error.  Measured on the connectome tasks, the gap's
    standard deviation across seeds reaches 1.06 while its mean is 0.87 -- the
    ratio is not a usable statistic at all, and an apparent non-monotonicity in it
    can be pure noise.

    The stable quantity is the **absolute excess error** (EWC minus oracle): its
    spread is ~1e-3 where the oracle's own error is stable to ~1e-3, and it varies
    smoothly.  This returns both, with the ratio kept only for continuity and
    always accompanied by its spread so it cannot be quoted bare.
    """
    excess, gap, orc, ewc = [], [], [], []
    for seq in sequences:
        lv = error_levels(seq, basis)
        excess.append(lv["excess_final"])
        orc.append(lv["oracle_final"])
        ewc.append(lv["ewc_final"])
        gap.append(lv["excess_final"] / lv["oracle_final"] if lv["oracle_final"] else np.nan)
    excess, gap = np.asarray(excess), np.asarray(gap)
    orc, ewc = np.asarray(orc), np.asarray(ewc)
    return {
        "n": len(sequences),
        "excess_mean": float(excess.mean()),
        "excess_sem": float(excess.std(ddof=1) / np.sqrt(len(excess))) if len(excess) > 1 else 0.0,
        "excess_sd": float(excess.std(ddof=1)) if len(excess) > 1 else 0.0,
        "ewc_mean": float(ewc.mean()),
        "oracle_mean": float(orc.mean()),
        # A ratio whose denominator is the *averaged* oracle error is far calmer
        # than the per-seed ratio, and is the form to quote if a ratio is wanted.
        "gap_of_means": float(excess.mean() / orc.mean()) if orc.mean() else float("nan"),
        "gap_mean": float(np.nanmean(gap)),
        "gap_sd": float(np.nanstd(gap, ddof=1)) if len(gap) > 1 else 0.0,
    }


def gap_bandwidth(seq, basis, rel: float = 1e-12, n: int = 6,
                  seed: int = 0) -> dict:
    """The gap, plus the spread it shows under a ``rel``-relative input perturbation.

    **Why every quoted gap needs this.**  These tasks are rank-deficient (a
    precision of rank ~40 inside 1307 dimensions), so the Kalman recursion is
    severely ill-conditioned and the gap is a *chaotic* functional of its inputs.
    Measured on this substrate: a 1-ULP change in the connectome's spectral-radius
    estimate -- exactly what a random-start ARPACK call produces -- propagates to
    ~1e-12 in ``J`` and moves the reported gap by ±0.02-0.04, which is the same
    size as several of the effects the project is trying to measure.

    So a gap without a band is uninterpretable at that scale.  The band is measured
    empirically by perturbing the task precisions relatively and re-running, rather
    than derived, because the ill-conditioning is a property of the assembled
    system rather than of any one matrix.
    """
    from ..lgcl.model import Sequence

    rng = np.random.default_rng(seed)
    base = gap_vs_oracle(seq, basis)
    vals = []
    for _ in range(n):
        jitter = 1.0 + rel * rng.standard_normal(seq.J.shape)
        perturbed = Sequence(d=seq.d, q=seq.q, theta=seq.theta,
                             J=seq.J * jitter, Sigma=seq.Sigma, y=seq.y, U=seq.U)
        vals.append(gap_vs_oracle(perturbed, basis))
    vals = np.asarray(vals)
    return {
        "gap": float(base),
        "band_std": float(vals.std()),
        "band_max": float(np.max(np.abs(vals - base))),
        "band_vals": vals.tolist(),
    }


def diagonalisation_pressure(seq, basis) -> dict:
    """How much a basis projection throws away, and what the loss costs per step.

    The gap tells you a basis lost; this says *where*.  Two readings, one cheap and
    one grounded:

    ``mean_discarded``  ``||P - Pi(P)||_F^2 / ||P||_F^2`` averaged over the task
        precisions.  Purely descriptive -- it measures the size of what the
        projection removes, not its consequence.
    ``gain_excess``     the per-step MSE excess from the optimal-gain identity,
        which prices the discarded covariance *as a gain error* rather than as a
        norm.  This is the principled version, and the two can disagree: a
        projection can remove a large share of the mass while barely moving the
        gain, which is the whole reason the diagonal approximation is ever
        acceptable.
    """
    from ..lgcl.kalman import gain_mismatch_excess

    discarded = [basis.discarded_fraction(seq.Sigma[k]) for k in range(seq.T)]
    excess = gain_mismatch_excess(seq, basis)
    return {
        "mean_discarded": float(np.mean(discarded)),
        "max_discarded": float(np.max(discarded)),
        "gain_excess_sum": float(np.sum(excess)),
        "gain_excess_mean": float(np.mean(excess)),
    }
