"""Tests for the connectome substrate.

These need the downloaded data (``data/``, see
:mod:`clfly.connectome.fetch`) and skip cleanly without it, so the suite stays
runnable on a fresh checkout.  Everything that can be tested without the real
data -- the join semantics, the partition policies, the matched control -- is
tested on small synthetic inputs so those invariants are checked even when the
big files are absent.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import scipy.sparse as sp

from clfly.connectome import annotate, circuits, graph
from clfly.lgcl.bases import Partition, random_partition

DATA = Path(graph.DEFAULT_DATA_DIR)
HAS_DATA = (DATA / graph.CONNECTIVITY_FILE).exists() and (DATA / graph.ANNOTATION_FILE).exists()

needs_data = pytest.mark.skipif(not HAS_DATA, reason="connectome data not downloaded")


@pytest.fixture(scope="module")
def conn():
    return graph.build()


@pytest.fixture(scope="module")
def ann():
    return annotate.load_annotations()


# --------------------------------------------------------------------------
# partition policies (no data needed)
# --------------------------------------------------------------------------
def _fake_annotations():
    import pandas as pd
    return annotate.Annotations(pd.DataFrame(
        {"group": ["a", "a", None, "b", "b", "b", None]},
        index=pd.Index([10, 11, 12, 13, 14, 15, 16], name="root_id"),
    ))


def test_missing_policies_differ_correctly():
    ann = _fake_annotations()
    root_ids = np.array([10, 11, 12, 13, 14, 15, 16, 99])  # 99 absent entirely

    single = ann.labels("group", root_ids, missing="singleton")
    # 'a' and 'b' plus a private group for each of the three unannotated neurons
    assert len(np.unique(single)) == 5
    assert single[0] == single[1]               # 'a' neurons share a group
    assert single[2] != single[6]               # two missing neurons do not

    shared = ann.labels("group", root_ids, missing="shared")
    assert len(np.unique(shared)) == 3          # a, b + one pooled 'unknown'
    assert shared[2] == shared[6] == shared[7]

    drop = ann.labels("group", root_ids, missing="drop")
    assert (drop < 0).sum() == 3
    assert drop[0] == drop[1] and drop[3] == drop[4] == drop[5]


def test_coverage_counts_absent_neurons_as_missing():
    ann = _fake_annotations()
    root_ids = np.array([10, 11, 12, 13, 14, 15, 16, 99])
    assert ann.coverage("group", root_ids) == pytest.approx(5 / 8)


def test_random_control_matches_parameters_exactly():
    """The whole point of the control: same capacity, no biology."""
    labels = np.repeat(np.arange(5), [50, 20, 7, 3, 1])
    ctl = random_partition(labels, np.random.default_rng(0))
    assert ctl.n_parameters == Partition(labels).n_parameters
    assert sorted(ctl.group_sizes) == sorted(Partition(labels).group_sizes)


def test_subsample_preserves_every_group_proportionally():
    labels = np.repeat(np.arange(4), [100, 40, 8, 2])
    for frac in (0.1, 0.5, 1.0):
        keep = circuits.subsample_fraction(labels, frac, np.random.default_rng(0))
        kept = labels[keep]
        assert set(np.unique(kept)) == {0, 1, 2, 3}, "a group disappeared"
        assert len(keep) <= len(labels)
        # relative sizes survive up to rounding (the 2-member group is forced to 1)
        big, small = (kept == 0).sum(), (kept == 1).sum()
        assert big / small == pytest.approx(100 / 40, rel=0.25)


def test_subsample_rejects_bad_fractions():
    with pytest.raises(ValueError):
        circuits.subsample_fraction(np.array([0, 1]), 0.0)


# --------------------------------------------------------------------------
# graph mechanics on synthetic data (no data needed)
# --------------------------------------------------------------------------
def test_subgraph_reindexes_and_carries_root_ids():
    W = sp.csr_matrix(np.array([[0, 1, 0], [0, 0, 2], [3, 0, 0]], dtype=float))
    C = graph.Connectome(n_neurons=3, root_ids=np.array([100, 200, 300]), W=W)
    sub = C.subgraph(np.array([2, 0]))
    assert sub.n_neurons == 2
    np.testing.assert_array_equal(sub.root_ids, [300, 100])
    np.testing.assert_array_equal(sub.W.toarray(),
                                  np.array([[0, 3.0], [0, 0.0]]))


def test_subgraph_rejects_duplicates():
    W = sp.eye(3, format="csr")
    C = graph.Connectome(n_neurons=3, root_ids=np.arange(3), W=W)
    with pytest.raises(ValueError):
        C.subgraph(np.array([0, 0]))


def test_modularity_is_high_for_a_block_graph_and_low_for_a_random_one():
    """A partition must score better on the structure it was built for."""
    rng = np.random.default_rng(0)
    n, g = 200, 4
    labels = np.repeat(np.arange(g), n // g)
    same = labels[:, None] == labels[None, :]
    B = ((rng.random((n, n)) < 0.5) & same).astype(float)
    np.fill_diagonal(B, 0.0)
    B = np.triu(B, 1)
    B = B + B.T
    W = sp.csr_matrix(B)
    assert graph.modularity(W, labels) > 0.5
    assert graph.modularity(W, rng.permutation(labels)) < 0.1


def test_weight_scales_keep_sign_and_compress_the_tail():
    W = sp.csr_matrix(np.array([[0, 1000, -1000]], dtype=float))
    C = graph.Connectome(n_neurons=3, root_ids=np.arange(3), W=W)
    log = C.weights("log1p").toarray()
    assert log[0, 1] > 0 > log[0, 2]
    assert log[0, 1] < 1000                       # tail compressed
    np.testing.assert_allclose(C.weights("sign").toarray(), [[0, 1, -1]])
    np.testing.assert_allclose(C.weights("raw").toarray(), [[0, 1000, -1000]])


# --------------------------------------------------------------------------
# the real data
# --------------------------------------------------------------------------
@needs_data
def test_connectome_shape_matches_the_published_release(conn):
    assert conn.n_neurons == 138_639
    assert conn.n_edges == 15_091_983
    assert 0.35 < conn.stats()["inhibitory_fraction"] < 0.45


@needs_data
def test_index_alignment_is_verified_not_assumed(conn):
    """The loader must refuse a table whose indices are its own enumeration."""
    import pandas as pd
    n = conn.n_neurons
    bad = pd.DataFrame({
        "Presynaptic_Index": np.array([0, 1]),
        "Presynaptic_ID": np.array([n + 1, n + 2]),   # not the completeness ids
        "Postsynaptic_Index": np.array([1, 2]),
        "Postsynaptic_ID": np.array([n + 2, n + 3]),
    })
    with pytest.raises(ValueError, match="not an index into the completeness list"):
        graph._verify_index_alignment(bad, conn.root_ids)


@needs_data
def test_root_ids_are_not_the_boolean_flag(conn):
    """Regression: the id column must be id-like, not the `Completed` flag."""
    assert conn.root_ids.dtype.kind in "iu"
    assert conn.root_ids.min() > 1e12


@needs_data
def test_annotation_coverage_matches_the_published_table(ann, conn):
    for col, expected in (("flow", 1.0), ("super_class", 1.0), ("cell_type", 0.989),
                          ("cell_class", 0.772)):
        assert ann.coverage(col, conn.root_ids) == pytest.approx(expected, abs=0.01)


@needs_data
def test_basis_table_constrained_fraction_rises_with_granularity(ann, conn):
    tab = annotate.basis_table(ann, conn.root_ids).set_index("basis")
    # coarse bases constrain little, fine bases approach the diagonal
    assert tab.loc["flow", "constrained_fraction"] < 0.3
    assert tab.loc["cell_type", "constrained_fraction"] > 0.95
    assert tab.loc["supertype", "constrained_fraction"] > 0.99


@needs_data
def test_circuit_extraction_is_annotated_and_tractable(conn, ann):
    circ = circuits.extract(conn, ann, hops=0, max_neurons=3000)
    # `max_neurons` is a soft budget: every annotational group keeps at least one
    # member, so with hundreds of cell types the floor pushes the total slightly
    # above the target.
    assert circ.n_neurons <= 1.15 * 3000
    assert circ.covariance_gb() < 0.5
    # every basis should have at least a few groups inside the circuit
    for basis, lab in circ.labels.items():
        assert len(np.unique(lab)) >= 2, f"{basis} degenerated inside the circuit"
    # the primary biological basis should be well covered, not mostly singletons
    ct = circ.labels["cell_type"]
    assert len(np.unique(ct)) > 100


@needs_data
def test_matched_control_on_a_real_basis_has_equal_capacity(conn, ann):
    circ = circuits.extract(conn, ann, hops=0, max_neurons=3000)
    ct = Partition(circ.labels["cell_type"])
    ctl = random_partition(circ.labels["cell_type"], np.random.default_rng(0))
    assert ctl.n_parameters == ct.n_parameters
    assert ctl.n_groups == ct.n_groups
