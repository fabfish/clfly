"""`e154`'s three identities and its gap statistic, checked on matrices whose answers are known by construction.

The failure modes worth a test are the ones this reader exists to prevent: **an identity that holds only because
the artifact happens to be tidy** (so it is checked on a matrix built to violate each one), and **a gap statistic
that silently reads the wrong window** -- `nanmax(R[j:, j])` against the diagonal is the whole measurement, and
`R[:j+1, j]` is a different set of checkpoints that a careless implementation would use.
"""

from __future__ import annotations

import json

import numpy as np

from experiments import e154_retention_matrix_audit as e154


def _artifact(tmp_path, name="a.json", R=None, learned=None, final=None, stored=None):
    """One method's replicates, built from the fields the audit reads, with the derived columns supplied."""
    n = len(R)
    reps = []
    for r in range(n):
        mat = np.asarray(R[r], dtype=float)
        reps.append({"retention": mat.tolist(),
                     "learned": (learned[r] if learned is not None
                                 else [mat[j][j] for j in range(mat.shape[0])]),
                     "final_per_task": (final[r] if final is not None else mat[-1].tolist()),
                     "forgetting_per_task": (stored[r] if stored is not None else
                                             [mat[j][j] - mat[-1][j] for j in range(mat.shape[0] - 1)] + [0.0])})
    path = tmp_path / name
    path.write_text(json.dumps({"methods": {"m": {"replicates": reps}}}), encoding="utf-8")
    return path


def _lower_triangle(diag, final, later=None):
    """A 3-task matrix filled for `j <= k`, with the diagonal and the final row as given."""
    T = 3
    R = np.full((T, T), np.nan)
    for k in range(T):
        for j in range(k + 1):
            R[k, j] = diag[j] if k == j else (final[j] if k == T - 1 else 0.5)
    for j in range(T):
        R[T - 1, j] = final[j]
    if later is not None:
        for j, v in later.items():
            R[T - 1, j] = v
    return R


def test_the_three_identities_hold_on_a_matrix_built_to_satisfy_them(tmp_path):
    R = [_lower_triangle([0.9, 0.8, 0.7], [0.6, 0.5, 0.7]) for _ in range(4)]
    _artifact(tmp_path, R=R)
    res = e154.audit(tmp_path)
    assert res["n_methods"] == 1
    assert all(v == 0.0 for v in res["identity_worst_difference"].values())
    assert all(c == 0 for c in res["violation_counts"].values())


def test_each_identity_is_actually_checked_and_not_merely_reported(tmp_path):
    # `learned` off the diagonal -> the first identity must fail
    R = [_lower_triangle([0.9, 0.8, 0.7], [0.6, 0.5, 0.7]) for _ in range(4)]
    learned = [[0.9, 0.8, 0.6] for _ in range(4)]        # the last entry is not the diagonal
    _artifact(tmp_path, name="b.json", R=R, learned=learned)
    assert e154.audit(tmp_path)["violation_counts"]["learned_is_diagonal"] == 1
    # a stored forgetting that is not the diagonal minus the final -> the third identity must fail
    R2 = [_lower_triangle([0.9, 0.8, 0.7], [0.6, 0.5, 0.7]) for _ in range(4)]
    stored = [[0.0, 0.0, 0.0] for _ in range(4)]
    _artifact(tmp_path, name="c.json", R=R2, stored=stored)
    assert e154.audit(tmp_path)["violation_counts"]["forgetting_is_diagonal_minus_final"] == 1


def test_the_gap_uses_the_LATER_checkpoints_and_the_diagonal_it_compares_against(tmp_path):
    # task 0's accuracy is 0.90 at its own diagonal and recovers to 0.95 at the end: a gap of 0.05
    R = []
    for _ in range(3):
        m = _lower_triangle([0.90, 0.80, 0.70], [0.95, 0.50, 0.70])
        R.append(m)
    _artifact(tmp_path, R=R)
    res = e154.audit(tmp_path)
    gap = res["literature_gap"]
    # two forgettable tasks x three replicates = 6 observations; task 0 has a 0.05 gap in each of the three
    assert gap["observations"] == 6
    assert abs(gap["mean"] - 0.05 * 3 / 6) < 1e-12
    assert abs(gap["max"] - 0.05) < 1e-9
    assert abs(gap["strictly_positive_share"] - 0.5) < 1e-12


def test_an_artifact_without_a_matrix_is_skipped_rather_than_counted_as_clean(tmp_path):
    (tmp_path / "nope.json").write_text(json.dumps({"methods": {"m": {"replicates": []}}}), encoding="utf-8")
    (tmp_path / "notjson.json").write_text("{}", encoding="utf-8")
    res = e154.audit(tmp_path)
    assert res["n_artifacts"] == 0 and res["n_methods"] == 0 and res["literature_gap"]["observations"] == 0
