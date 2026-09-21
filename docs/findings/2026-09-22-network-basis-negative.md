# E8b — carrying the basis finding into the trained network: it does not transfer

**Date:** 2026-09-22
**Module:** `clfly/network/fisher.py`
**Script:** `experiments/e8_rate_network.py --methods naive,ewc,ewc-block,ewc-block-rand,replay`
**Artifacts:** `runs/e8_basis.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 3 repeats each, λ = 0.1, 500 iterations, chance 0.25

---

## 1. What was built

The linear-Gaussian work's central result is that the *coordinate* basis is the wrong
place to anchor a Fisher matrix, and that coarser biological groupings cut the excess
error at matched capacity. That has never been tested on a trained network, because the
network's parameters are **synapses** and the linear machinery does not apply to them.

`clfly/network/fisher.py` supplies the missing object: a **partition of the synapse
parameters**, and the block-diagonal Fisher that goes with it. Grouping synapses by
``(pre cell class, post cell class)`` and keeping the *within-group* second moments is
the exact analogue of `Partition.project` keeping within-group covariance; the penalty
becomes `λ/2 Σ_g Δ_gᵀ F_g Δ_g`, with diagonal EWC as the all-singletons special case.
Group sizes on this circuit:

| basis | groups | largest | median | block storage | constrained |
|---|---|---|---|---|---|
| `cell_class` pairs | 100 | 5,509 | 36 | 0.42 GB | 0.925 |
| `ito_lee_hemilineage` pairs | 2,148 | 601 | 2 | 0.03 GB | 0.994 |
| `cell_type` pairs | 19,618 | 421 | **1** | 0.00 GB | 0.999 |

`cell_type` pairs have **median group size 1** — that is the diagonal wearing a finer
label, exactly the trap the linear work identified, and the reason `cell_class` pairs
(0.925 constrained) is the rung worth testing.

## 2. Result: the biological partition is worse than the diagonal *and* worse than its control

| method | final accuracy | **mean forgetting** |
|---|---|---|
| naive | 0.824 ± 0.036 | +0.101 ± 0.049 |
| EWC, diagonal Fisher | 0.859 ± 0.016 | +0.056 ± 0.051 |
| **EWC, block Fisher — biological `cell_class` pairs** | 0.775 ± 0.028 | **+0.177 ± 0.039** |
| EWC, block Fisher — size-matched **random** pairs | 0.840 ± 0.008 | +0.087 ± 0.027 |
| replay (16/task) | 0.903 ± 0.014 | **−0.000 ± 0.021** |

Three readings.

**The basis finding does not transfer.** The biological block partition forgets *more*
than the neuron diagonal (+0.177 against +0.056, difference 0.121 ± 0.064 → 1.9σ) and
more than naive (+0.177 against +0.101). It also costs accuracy (0.775 against 0.824).

**And it is worse than its own matched random control.** +0.177 against +0.087 for the
size-matched random partition — a difference of 0.090 ± 0.047, **1.9σ, in the wrong
direction**. This is the *opposite* of the linear-substrate result, where the same
`cell_class` grouping beat its matched control at 3.7σ (5 seeds) and 12.1σ (18 seeds).
The grouping is not just unhelpful here; it is actively worse than an arbitrary
partition of identical capacity.

**Only replay resolves.** Its forgetting is −0.000 ± 0.021 against naive's
+0.101 ± 0.049 (difference 0.101 ± 0.054, 1.9σ) with the best final accuracy, and it
leaves earlier tasks slightly *better* than when they were learned. No EWC variant
resolves a benefit over naive: the diagonal's apparent edge is 0.045 ± 0.071 (0.6σ).

## 3. Why it probably does not transfer, and what would test that

**The linear finding is about a different object.** It concerns the block structure of
the *precision matrix over neurons* — how a task's measurement covariance is organised
in the space of neural states. The network's analogue groups *synapses* by their
endpoint cell classes. Those are not the same partition of the same space, and nothing in
the linear result says the second must behave like the first. The transfer was an
analogy, and the analogy failed.

**The leading concrete explanation is statistical, not informational.** The block Fisher
is estimated from 8 minibatches of 32 samples — 256 observations — and it has
`Σ s_g² = 5.3e7` entries to fill. The diagonal has 26,568 entries from the same 256
observations. Both are under-determined, but the block one is under-determined by a
factor of two thousand, and a coarse block *accumulates* that estimation noise across
its within-group off-diagonals while the diagonal simply discards them. So the block
Fisher may be trading a real information advantage for a much larger variance.

That is testable and cheap: **raise the number of Fisher batches** and re-run. If the
block partition improves with better-estimated curvature and eventually overtakes the
diagonal and its control, the explanation holds and the negative result is a
statistical-power statement. If it does not improve, the block structure genuinely does
not help on this substrate and the analogy is simply wrong. Either answer is
informative, and this is the next experiment.

**A second candidate: the partition is the wrong shape for a weight parameterisation.**
Grouping by endpoint class assumes the informative structure of the Fisher is
"same source class, same target class". For a *weight* matrix generated by propagating
activity through a connectome, the relevant structure may instead be organised by the
propagation, not by the anatomy — which is exactly what `e7` found for the interference
prior ("measure it post-propagation, not from the anatomy").

## 4. Two bugs found and fixed on the way

**Unseeded torch global RNG.** `nn.Linear` initialises its weights from torch's global
RNG, which is seeded from entropy at process start and was never set. Identical
commands therefore produced different readout initialisations and different forgetting —
naive's mean forgetting came out at +0.135 ± 0.021 in one run and +0.066 ± 0.031 in
another, with nothing changed but the process. Fixed by seeding torch in `run_method`;
verified that two identical commands now give identical output. **This is the same class
of failure as the earlier `scipy.sparse.linalg.eigs` bug** — a library defaulting to a
random start — and it is worth noting that the project has now hit it in two different
libraries.

**λ is not comparable across partitions without normalisation.** A block Fisher
accumulates `Σ_{i∈g} g_i²` on its diagonal, so a group of a thousand synapses carries a
thousand times the magnitude of a singleton: the *same* λ is a far stronger penalty for
a coarse partition. Left uncorrected, "granularity" would be confounded with "strength"
and the coarse basis would look bad for a bookkeeping reason. `trace_normalise` rescales
each partition's blocks so the mean per-parameter weight is 1; all numbers above use it.

## 5. Status

The network now has the full basis machinery available to it — synapse partitions,
matched random controls, block Fisher with a comparable λ — and the first comparison
comes out negative. Combined with the previous fire, the picture on the rate network is:

- **replay works** (forgetting driven to ~0, best accuracy);
- **no Fisher-anchoring variant resolves a benefit over naive**, in the neuron diagonal
  basis or in a biological block basis;
- and the biological basis is, if anything, worse.

That is a coherent outcome for the project even though it is a negative one: LGCL
predicts that the *diagonal* projection costs 33% excess error on this connectome, and
the linear work showed that anchoring in better bases recovers only part of that. A
method built on an approximation that costs a third of the error should not be expected
to beat storing sixteen stimuli, and it does not.
