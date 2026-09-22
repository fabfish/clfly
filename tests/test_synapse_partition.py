"""Tests for the synapse partition that the network's block Fisher anchors in.

Kept out of ``test_network.py`` on purpose: ``clfly/network/fisher.py`` is torch-free, so
these must run in an install without the optional ``network`` extra.
"""

from __future__ import annotations

import numpy as np
import pytest

from clfly.network.fisher import SynapsePartition


def _toy():
    """Eight neurons, four of them the only member of their label, and all 64 ordered pairs."""
    labels = np.array([0, 0, 0, 0, 1, 2, 3, 4])
    pre = np.repeat(np.arange(8), 8)
    post = np.tile(np.arange(8), 8)
    return labels, pre, post


# --------------------------------------------------------------------------
# pooling
# --------------------------------------------------------------------------
def test_without_pooling_every_ordered_label_pair_is_its_own_group():
    labels, pre, post = _toy()
    part = SynapsePartition.from_labels(labels, pre, post)
    assert part.n_groups == 25          # 5 labels -> 5^2 ordered pairs, all present
    assert part.n_params == 64


def test_pool_below_merges_the_rare_labels_into_one_shared_group():
    labels, pre, post = _toy()
    part = SynapsePartition.from_labels(labels, pre, post, pool_below=2)
    # label 0 (4 neurons) survives; labels 1..4 (one neuron each) collapse to one
    assert part.n_groups == 4           # 2 labels -> 2^2 ordered pairs, all present


def test_pool_buckets_splits_the_merged_mass_into_b_separate_groups():
    labels, pre, post = _toy()
    one = SynapsePartition.from_labels(labels, pre, post, pool_below=2)
    two = SynapsePartition.from_labels(labels, pre, post, pool_below=2, pool_buckets=2)
    # the single pooled label becomes two, so the pooled x pooled block becomes 2x2
    assert two.n_groups == 9            # 3 labels -> 3^2 ordered pairs, all present
    assert two.n_groups > one.n_groups
    # and the point of the whole exercise: storage is sum_g s_g^2, so it falls
    assert two.n_entries < one.n_entries
    assert two.n_params == one.n_params == 64


def test_bucketing_does_not_redistribute_the_kept_labels():
    labels, pre, post = _toy()
    # the four neurons in label 0 are 0..3 and the edges are pre*8 + post
    kept_pair = sorted(p * 8 + q for p in range(4) for q in range(4))
    for buckets in (1, 2, 3, 4, 8):
        part = SynapsePartition.from_labels(labels, pre, post, pool_below=2,
                                            pool_buckets=buckets)
        groups = sorted(sorted(g.tolist()) for g in part.groups)
        assert kept_pair in groups, f"B={buckets} moved the kept label x kept label group"
        assert part.n_params == 64


def test_more_buckets_never_increase_storage():
    labels, pre, post = _toy()
    sizes = [SynapsePartition.from_labels(labels, pre, post, pool_below=2,
                                          pool_buckets=b).n_entries
             for b in (1, 2, 3, 4, 5, 8, 16)]
    assert sizes == sorted(sizes, reverse=True), sizes


def test_bucketing_is_deterministic():
    labels, pre, post = _toy()
    a = SynapsePartition.from_labels(labels, pre, post, pool_below=2, pool_buckets=3)
    b = SynapsePartition.from_labels(labels, pre, post, pool_below=2, pool_buckets=3)
    assert [sorted(g.tolist()) for g in a.groups] == [sorted(g.tolist()) for g in b.groups]


def test_pool_below_with_nothing_rare_is_a_no_op():
    labels, pre, post = _toy()
    part = SynapsePartition.from_labels(labels, pre, post, pool_below=1, pool_buckets=8)
    assert part.n_groups == 25


def test_every_synapse_lands_in_exactly_one_group():
    labels, pre, post = _toy()
    for buckets in (1, 2, 4):
        part = SynapsePartition.from_labels(labels, pre, post, pool_below=2,
                                            pool_buckets=buckets)
        flat = np.concatenate(part.groups)
        assert sorted(flat.tolist()) == list(range(len(pre)))


# --------------------------------------------------------------------------
# the matched-random control
# --------------------------------------------------------------------------
def test_random_matched_preserves_the_group_sizes_and_permutes_the_synapses():
    labels, pre, post = _toy()
    bio = SynapsePartition.from_labels(labels, pre, post, pool_below=2, pool_buckets=2)
    rand = SynapsePartition.random_matched(bio, np.random.default_rng(0))
    assert sorted(rand._sizes.tolist()) == sorted(bio._sizes.tolist())
    assert rand.n_entries == bio.n_entries      # capacity is matched by construction
    assert sorted(np.concatenate(rand.groups).tolist()) == list(range(len(pre)))
    assert rand.name.startswith("rand:")


def test_constrained_fraction_is_the_share_of_the_pair_matrix_that_is_dropped():
    labels, pre, post = _toy()
    part = SynapsePartition.from_labels(labels, pre, post)
    m = part.n_params
    assert part.constrained_fraction() == 1.0 - sum(len(g) ** 2 for g in part.groups) / (m * m)


# --------------------------------------------------------------------------
# the penalty: bound once per task, not per training step
# --------------------------------------------------------------------------
def test_make_penalty_agrees_with_penalty_tensor_bit_for_bit():
    torch = pytest.importorskip("torch", reason="the penalty is a torch object")
    labels, pre, post = _toy()
    part = SynapsePartition.from_labels(labels, pre, post, pool_below=2, pool_buckets=2)
    rng = np.random.default_rng(0)
    theta = torch.tensor(rng.normal(size=part.n_params), dtype=torch.float32)
    anchor = rng.normal(size=part.n_params)
    blocks = rng.normal(size=part.n_entries)

    for lam in (0.0, 0.003, 1.0):
        per_step = part.penalty_tensor(blocks, theta, anchor, lam, torch)
        bound = part.make_penalty(blocks, anchor, theta, lam, torch)(theta)
        assert bound.item() == per_step.item()


def test_bound_penalty_tracks_theta_and_is_zero_at_the_anchor():
    torch = pytest.importorskip("torch", reason="the penalty is a torch object")
    labels, pre, post = _toy()
    part = SynapsePartition.from_labels(labels, pre, post, pool_below=2)
    rng = np.random.default_rng(1)
    anchor = rng.normal(size=part.n_params)
    blocks = np.abs(rng.normal(size=part.n_entries))
    theta = torch.tensor(anchor.copy(), dtype=torch.float64).requires_grad_(True)
    p = part.make_penalty(blocks, anchor, theta, 0.5, torch)
    assert p(theta).item() == pytest.approx(0.0)
    shifted = torch.tensor(anchor + 0.3, dtype=torch.float64).requires_grad_(True)
    out = p(shifted)
    assert out.item() > 0
    out.backward()
    assert shifted.grad is not None and float(shifted.grad.abs().sum()) > 0
