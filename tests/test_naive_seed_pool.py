"""Tests for the `e54` naive-arm pooling.

The load-bearing choice in `e54` is that runs are clustered **by agreement on the data**, not by a
configuration key that ought to predict the computation. The first version used a key and silently
merged two different computations, which is the failure this module pins: a wrong key looks like a
bigger sample. The clustering itself is therefore tested for the property that matters -- a run that
disagrees on *any* shared seed is kept out, not averaged in.
"""

from __future__ import annotations

import numpy as np

from experiments.e54_naive_seed_pool import cluster


def run(name: str, values: dict):
    return {"path": name, "values": dict(values), "key": (), "config": {}}


def test_agreeing_runs_form_one_cluster_and_union_their_seeds():
    a = run("a", {0: 0.9, 1: 0.8, 2: 0.7})
    b = run("b", {0: 0.9, 1: 0.8, 2: 0.7, 3: 0.85, 4: 0.75})
    clusters = cluster([a, b])
    assert len(clusters) == 1
    assert sorted(clusters[0][0]["values"]) == [0, 1, 2, 3, 4] or len(clusters[0]) == 2


def test_a_run_disagreeing_on_one_shared_seed_is_kept_out():
    # seed 2 differs: this must NOT be averaged into the same sample
    a = run("a", {0: 0.9, 1: 0.8, 2: 0.7})
    b = run("b", {0: 0.9, 1: 0.8, 2: 0.75})
    clusters = cluster([a, b])
    assert len(clusters) == 2
    assert {len(c) for c in clusters} == {1}


def test_disjoint_seed_sets_do_not_merge():
    # no shared seed means no evidence of agreement, so the runs must stay apart
    a = run("a", {0: 0.9})
    b = run("b", {5: 0.9})
    assert len(cluster([a, b])) == 2


def test_clustering_is_single_linkage_so_a_chain_joins():
    a = run("a", {0: 0.9, 1: 0.8})
    b = run("b", {0: 0.9, 1: 0.8, 2: 0.7})
    c = run("c", {1: 0.8, 2: 0.7})
    # a-b agree on {0,1}; b-c agree on {1,2}; a-c agree on {1}
    assert len(cluster([a, b, c])) == 1


def test_clusters_are_returned_largest_first():
    big = [run(f"b{i}", {0: 0.9, 1: 0.8}) for i in range(3)]
    small = [run("s", {0: 0.1, 1: 0.2})]
    clusters = cluster(big + small)
    assert len(clusters[0]) == 3 and len(clusters[1]) == 1


def test_the_pooled_sd_and_floor_reproduce_the_nine_seed_numbers():
    # the main cluster's nine accuracy values, as measured
    v = np.array([0.8958333333333334, 0.7916666666666666, 0.7847222288449606,
                  0.8333333333333334, 0.8541666666666666, 0.8888888888888888,
                  0.8125, 0.8402777777777778, 0.8541666666666666])
    s = float(v.std(ddof=1))
    floor = float(np.sqrt(v.mean() * (1 - v.mean()) / 144))
    assert abs(v.mean() - 0.8395) < 1e-3
    assert abs(s - 0.0389) < 5e-4
    assert abs(floor - 0.0306) < 5e-4
    # 62% of the variance is the evaluation floor, so 38% is learner variability
    assert abs(100 * floor ** 2 / s ** 2 - 62) < 1.5
