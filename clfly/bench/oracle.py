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


def task_subspaces(seq, ranks) -> list[np.ndarray]:
    """Leading precision subspace of each task, strongest directions first."""
    out = []
    for k in range(seq.T):
        w, V = np.linalg.eigh(seq.J[k])
        out.append(V[:, np.argsort(w)[::-1][: ranks[k]]])
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
