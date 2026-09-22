"""Tests for the `e44` cost-model helpers and the claim they support.

Two things in `e44` are easy to get wrong in ways that would publish a wrong number, and both
happened while writing it:

* the cost is a **two-term** model (`G` dispatches plus the footprint `sum_g s_g^2`), and a pure
  `G^a` fit looks plausible while mispredicting by ~4.6x -- so the terms are pinned here;
* the numerical comparison between the loop penalty and the block-diagonal sparse one is **vacuous
  at `theta = 0`** (both routes return exactly zero), which is what the first version measured. The
  test requires a non-zero probe.
"""

from __future__ import annotations

import numpy as np
import pytest
import scipy.sparse as sp
import torch

from clfly.network.fisher import SynapsePartition
from experiments.e44_penalty_cost_scaling import bound_sparse, blocks_for, equal_groups


def _part_and_blocks(d, g, seed=0):
    groups = equal_groups(d, g, seed=seed)
    return SynapsePartition(groups=groups, name="t"), blocks_for(groups, seed=seed)


def test_equal_groups_partitions_the_index_range():
    groups = equal_groups(50, 7)
    assert len(groups) == 7
    assert sorted(np.concatenate(groups).tolist()) == list(range(50))
    assert all(g.size and len(set(g.tolist())) == g.size for g in groups)


def test_blocks_layout_matches_sum_of_squared_group_sizes():
    groups = equal_groups(50, 7)
    assert blocks_for(groups).size == sum(len(g) ** 2 for g in groups)


@pytest.mark.parametrize("g", [1, 3, 10])
def test_sparse_route_agrees_with_the_loop_route_on_a_nonzero_probe(g):
    d = 40
    part, blocks = _part_and_blocks(d, g)
    # non-zero on both sides: with zeros the two routes agree trivially and the check is vacuous
    rng = np.random.default_rng(3)
    theta = torch.tensor(rng.standard_normal(d), dtype=torch.float64)
    anchor = rng.standard_normal(d) * 1e-2
    ref = float(part.make_penalty(blocks, anchor, theta, lam=1.0, torch_mod=torch)(theta))
    B = bound_sparse(part, blocks)
    got = 0.5 * float((theta.numpy() - anchor) @ (B @ (theta.numpy() - anchor)))
    assert ref != 0.0  # the probe must not be degenerate
    assert abs(got - ref) / abs(ref) < 1e-12


def test_sparse_route_is_vacuous_at_zero_which_is_why_the_probe_must_not_be_zero():
    d = 40
    part, blocks = _part_and_blocks(d, 5)
    zero = torch.zeros(d, dtype=torch.float64)
    B = bound_sparse(part, blocks)
    assert float(part.make_penalty(blocks, np.zeros(d), zero, lam=1.0,
                                  torch_mod=torch)(zero)) == 0.0
    assert 0.5 * float(zero.numpy() @ (B @ zero.numpy())) == 0.0


def test_bound_sparse_is_block_diagonal_with_the_expected_nonzeros():
    part, blocks = _part_and_blocks(40, 5)
    B = bound_sparse(part, blocks)
    assert B.shape == (40, 40)
    assert B.nnz == sum(len(g) ** 2 for g in part.groups)
    # block-diagonal: every nonzero sits inside one group
    rows, cols = B.nonzero()
    for g in part.groups:
        member = np.zeros(40, dtype=bool)
        member[g] = True
        assert not (member[rows] ^ member[cols]).any()
    assert sp.issparse(B)


def test_the_two_term_model_beats_a_pure_power_law_on_the_measured_points():
    # The five measured points from e44 section 1, in the ladder's order.
    groups = np.array([10, 100, 2148, 9938, 19618], dtype=float)
    footprint = np.array([70585864, 7058608, 329112, 73212, 40468], dtype=float)
    cost = np.array([53649.2, 9274.0, 66493.6, 323971.0, 533582.2])
    two = np.column_stack([groups, footprint])
    coef, *_ = np.linalg.lstsq(two, cost, rcond=None)
    assert coef[0] > 0 and coef[1] > 0  # both terms positive
    rel_two = np.abs(two @ coef - cost) / cost
    # a pure power law, for contrast
    slope, intercept = np.polyfit(np.log(groups), np.log(cost), 1)
    rel_pow = np.abs(np.exp(intercept + slope * np.log(groups)) - cost) / cost
    assert rel_two.max() < 0.2
    assert rel_pow.max() > rel_two.max()  # the power law is the worse model
    # and the fit says the dispatch term is tens of microseconds per group
    assert 5 < coef[0] < 200
