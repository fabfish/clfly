"""Anchoring bases for the rate network: block-diagonal Fisher over synapse groups.

The linear-Gaussian work found that the *coordinate* basis is the wrong place to
anchor a Fisher matrix, and that coarser biological groupings — cell class, and the
wiring's own eigenbasis — cut the excess error substantially at matched capacity.  That
finding has never been tested on a network that is actually *trained*, because the
network's parameters are synapses and the linear machinery does not apply to them.

This module supplies the missing object: a **partition of the synapse parameters**, and
the block-diagonal Fisher that goes with it.

A partition groups synapses — by (pre cell class, post cell class) for a biological
basis, or by a size-matched random assignment for the control — and the block-diagonal
Fisher keeps the *within-group* second-moment structure while discarding the
between-group structure, exactly as :meth:`clfly.lgcl.bases.Partition.project` keeps
within-group covariance.  The penalty is then

    lam/2 * sum_g (theta_g - anchor_g)^T F_g (theta_g - anchor_g)

so ``Diagonal``-EWC is the special case where every group is a singleton, and the
whole thing is the network analogue of "anchor the precision in basis B".

**Cost.** The block Fisher stores ``sum_g s_g^2`` entries, so granularity is a real
budget rather than a free choice. On the standard circuit the (pre cell class, post
cell class) partition is 100 groups over 26,568 synapses with ``sum s^2 = 5.3e7``
(0.42 GB), while a cell-type-pair partition is 19,618 groups whose median size is 1 —
which is just the diagonal wearing a finer label. Both numbers are reported by
:meth:`describe`, because the linear work showed that a near-singleton partition
*silently is* the diagonal and needs to be visible.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class SynapsePartition:
    """A partition of the ``nnz`` synapse parameters into groups."""

    groups: list[np.ndarray]          # each an int array of theta indices
    name: str = "partition"
    _sizes: np.ndarray = field(default=None, repr=False)
    _offsets: np.ndarray = field(default=None, repr=False)

    def __post_init__(self):
        self._sizes = np.array([len(g) for g in self.groups], dtype=np.int64)
        self._offsets = np.concatenate([[0], np.cumsum(self._sizes ** 2)])

    # -- constructors -------------------------------------------------------
    @classmethod
    def from_labels(cls, labels: np.ndarray, pre: np.ndarray, post: np.ndarray,
                    name: str = "partition", pool_below: int | None = None,
                    pool_buckets: int = 1
                    ) -> "SynapsePartition":
        """Group synapses by the ordered pair ``(labels[pre], labels[post])``.

        ``pool_below`` merges every label appearing in fewer than that many neurons
        into one shared group.  Without it a fine annotation column produces a
        near-singleton partition — cell-type pairs have median group size 1 on this
        circuit — which is not a coarser basis at all but the diagonal.

        ``pool_buckets`` splits that merged mass over ``B`` groups instead of one.  It
        exists because the storage is ``sum_g s_g^2`` and a single shared pooled label
        manufactures a single ``(pooled, pooled)`` group holding every synapse between
        two rare cell types: on the standard circuit that one block is 16,342 of 26,568
        synapses at ``pool_below=2``, i.e. **98.7%** of the partition's 2.165 GB.  With
        ``B`` buckets the block becomes ``B^2`` blocks of a ``B``-th the side each, so
        storage falls roughly as ``1/B`` and the mid-granularity range becomes
        affordable.  The buckets carry no biological meaning; their only job is to bound
        the projection's storage, and the matched-random control is built from the same
        bucket sizes so the comparison stays capacity-matched.
        """
        if pool_below:
            counts = np.bincount(labels)
            keep = counts >= pool_below
            remap = np.cumsum(keep) - 1
            if pool_buckets > 1:
                rare = np.nonzero(~keep)[0]
                newlab = np.empty(keep.size, dtype=np.int64)
                newlab[keep] = remap[keep]
                newlab[rare] = int(remap.max()) + 1 + np.arange(rare.size) % pool_buckets
                labels = newlab[labels]
            else:
                labels = np.where(keep, remap, int(remap.max()) + 1)[labels]
        pair = labels[pre].astype(np.int64) * (labels.max() + 1) + labels[post]
        _, inv = np.unique(pair, return_inverse=True)
        order = np.argsort(inv, kind="stable")
        bounds = np.searchsorted(inv[order], np.arange(inv.max() + 2))
        groups = [order[bounds[g]:bounds[g + 1]] for g in range(len(bounds) - 1)]
        return cls(groups=[g for g in groups if len(g)], name=name)

    @classmethod
    def random_matched(cls, base: "SynapsePartition", rng: np.random.Generator
                       ) -> "SynapsePartition":
        """Size-matched random control: identical group sizes, no biology.

        The essential control. Without it a biological partition could "win" merely by
        having larger groups, which changes how much structure the projection keeps.
        """
        flat = np.concatenate(base.groups)
        shuffled = rng.permutation(flat)
        out, pos = [], 0
        for s in base._sizes:
            out.append(shuffled[pos:pos + s])
            pos += s
        return cls(groups=out, name=f"rand:{base.name}")

    # -- geometry -----------------------------------------------------------
    @property
    def n_groups(self) -> int:
        return len(self.groups)

    @property
    def n_params(self) -> int:
        return int(self._sizes.sum())

    @property
    def n_entries(self) -> int:
        """Dense storage the block Fisher needs, in entries."""
        return int(self._offsets[-1])

    def constrained_fraction(self) -> float:
        """Share of the full parameter-pair matrix the block projection zeroes."""
        m = self.n_params
        return 1.0 - self.n_entries / (m * m) if m else 0.0

    def describe(self) -> dict:
        return {
            "name": self.name,
            "n_groups": self.n_groups,
            "n_params": self.n_params,
            "largest_group": int(self._sizes.max()) if self.n_groups else 0,
            "median_group": float(np.median(self._sizes)) if self.n_groups else 0.0,
            "block_entries": self.n_entries,
            "block_gb": self.n_entries * 8 / 1e9,
            "constrained_fraction": self.constrained_fraction(),
        }

    # -- the block Fisher ---------------------------------------------------
    def new_blocks(self) -> np.ndarray:
        return np.zeros(self.n_entries, dtype=np.float64)

    def accumulate(self, blocks: np.ndarray, grad: np.ndarray) -> None:
        """Add each group's outer product ``grad_g grad_g^T`` into its block."""
        for g, idx in enumerate(self.groups):
            gg = grad[idx]
            s = len(gg)
            off = self._offsets[g]
            blocks[off:off + s * s] += np.outer(gg, gg).ravel()

    def trace_normalise(self, blocks: np.ndarray) -> np.ndarray:
        """Rescale blocks so the mean per-parameter diagonal weight is 1.

        **Without this a coarse partition is not comparable to a diagonal one at the
        same lambda.**  A block Fisher accumulates ``sum_{i in g} g_i^2`` on its
        diagonal, so a group of a thousand synapses carries a thousand times the
        magnitude of a singleton — the same nominal ``lambda`` is a thousand times the
        penalty, and "granularity" would be confounded with "strength".  Normalising by
        ``sum_g tr(F_g) / n_params`` gives every partition the same mean weight, so
        lambda means the same thing across bases.

        (It does *not* equalise the off-diagonal content, which is the thing under
        test — only the overall scale.)
        """
        tr = 0.0
        for g, idx in enumerate(self.groups):
            s = len(idx)
            off = self._offsets[g]
            tr += float(np.trace(blocks[off:off + s * s].reshape(s, s)))
        mean = tr / self.n_params if self.n_params else 1.0
        return blocks / mean if mean > 0 else blocks

    def penalty_tensor(self, blocks: np.ndarray, theta, anchor, lam: float, torch_mod):
        """The penalty as a ``torch`` tensor, so it can be added to a loss.

        Written to flow a gradient through ``theta``: the block ``F_g`` is a constant
        and only the difference ``(theta_g - anchor_g)`` is differentiated, which is the
        EWC construction.
        """
        total = torch_mod.zeros((), dtype=theta.dtype, device=theta.device)
        for g, idx in enumerate(self.groups):
            s = len(idx)
            off = self._offsets[g]
            blk = torch_mod.from_numpy(
                blocks[off:off + s * s].reshape(s, s)).to(theta.device).to(theta.dtype)
            d = theta[idx] - anchor[idx]
            total = total + d @ (blk @ d)
        return 0.5 * lam * total
