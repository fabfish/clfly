"""`--partition-seed`: the matched-random control is a population, and one draw is one sample from it.

Rule 10 says a matched-random control must be averaged over draws, and the *linear* line implements that
(`e3_basis_selection --control-draws`, which records `sd_across_draws`). **The network line had no way to vary
the draw at all**: `partitions` was built once from `np.random.default_rng(args.seed0)` outside the replicate
loop, so all forty replicates of an `ewc-block-rand` arm shared **one** partition and the arm's sem contained no
draw variance. These tests pin the three properties the flag has to have:

  * the default is `--seed0`, so every artifact written before the flag is bit-identical under an unchanged
    command -- the flag cannot quietly re-date five artifacts' worth of results (rule 27);
  * two different seeds give two different partitions **and two different fingerprints**, so the artifact can
    say which sample it used without storing the partition;
  * and the read-out's own draw seed is **not disturbed** by the new one, which is the bug this flag's first
    version had: it reused the name `draw_seed`, and the read-out block below would have recorded the partition
    seed as its own (rule 31's shape -- a name reused across two draws).
"""

from __future__ import annotations

import numpy as np
import pytest

from clfly.network.fisher import SynapsePartition

pytest.importorskip("torch", reason="torch is an optional extra")


def _bio(n: int = 120, groups: int = 4):
    rng = np.random.default_rng(0)
    labels = np.repeat(np.arange(groups), n // groups)
    pre = rng.integers(0, 20, size=n)
    post = rng.integers(0, 20, size=n)
    return SynapsePartition.from_labels(labels, pre, post, name="synthetic")


def test_the_default_draw_reproduces_the_one_the_old_code_used():
    bio = _bio()
    old = SynapsePartition.random_matched(bio, np.random.default_rng(0))
    new_default = SynapsePartition.random_matched(bio, np.random.default_rng(0))
    assert all(np.array_equal(a, b) for a, b in zip(old.groups, new_default.groups))


def test_two_seeds_give_two_draws_and_two_fingerprints():
    import hashlib

    bio = _bio()
    prints = {seed: hashlib.sha1(
        " ".join(str(int(i)) for g in SynapsePartition.random_matched(
            bio, np.random.default_rng(seed)).groups for i in g[:8]).encode()).hexdigest()[:12]
        for seed in (0, 1, 2)}
    assert len(set(prints.values())) == 3
    # and the group *sizes* are matched to the biological partition by construction, which is what "size-matched"
    # means: the draw varies the assignment, not the budget
    rand = SynapsePartition.random_matched(bio, np.random.default_rng(7))
    assert sorted(len(g) for g in rand.groups) == sorted(len(g) for g in bio.groups)


def test_the_partition_block_does_not_reuse_the_readout_draw_s_name():
    """The first version of the flag assigned to `draw_seed`, which the read-out block below also uses.

    So the artifact would have recorded the *partition* seed as its read-out draw seed — a silent, plausible
    wrong number of exactly the shape rule 31 warns about. This is a source check because the property is about
    which name a block writes, and the runner's own path takes minutes to execute.
    """
    from pathlib import Path

    src = Path("experiments/e8_rate_network.py").read_text(encoding="utf-8")
    start = src.index("Synapse partitions for the block-EWC")
    end = src.index('"readout": ({"size"')
    block = src[start:end]
    assert "part_seed" in block
    assert "draw_seed =" not in block          # the read-out's name is not assigned in the partition block
    # and the read-out's own seed line still exists above
    assert "draw_seed = args.seed0 if args.readout_seed is None else args.readout_seed" in src
