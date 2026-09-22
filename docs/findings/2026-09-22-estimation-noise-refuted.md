# E8h — the estimation-noise explanation is refuted, and the ordering reversal weakens

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --fisher-batches N` on the hardened configuration
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 3 replicates, shared head, read-out 32 neurons, λ = 0.003, chance 0.25

---

## 1. The prediction being tested

The previous fire found that the basis ordering **reverses** on a trained network: the plain
neuron diagonal beats the block-diagonal over cell-class synapse pairs by +0.039 ± 0.025
(1.6σ), where on the *linear* substrate the coarse partition had beaten the diagonal by 80%
of the excess error. The proposed mechanism was **estimation noise**: the block Fisher has
`Σ s_g² = 5.3e7` entries to fill from 1024 observations, against the diagonal's 26,568, so a
coarse block accumulates its within-group off-diagonals as noise and acts as a strong random
constraint.

That made a specific, falsifiable prediction: **a better-estimated Fisher should improve the
block variants relative to the diagonal.** The earlier batch sweep that appeared to rule this
out had been run on the *unhardened* benchmark, where nothing resolved, so it had to be redone
here.

## 2. Result: refuted

| Fisher batches | naive | **EWC diagonal** | block — biological | block — random |
|---|---|---|---|---|
| 8 | +0.066 ± 0.019 | **+0.010 ± 0.010** | +0.031 ± 0.021 | +0.073 ± 0.006 |
| 32 | +0.066 ± 0.019 | **+0.028 ± 0.009** | +0.073 ± 0.033 | +0.059 ± 0.023 |
| 128 | +0.066 ± 0.019 | **+0.035 ± 0.015** | +0.038 ± 0.027 | +0.052 ± 0.024 |

*(mean forgetting; `naive` is constant at +0.066 ± 0.019 as it must be, since it uses no
Fisher.)*

**The diagonal is the best method at every batch count**, and the block variants never
overtake it. The diagonal-minus-biological-block gap runs +0.021 → +0.045 → +0.003: not
monotone in the direction the mechanism requires, and at 128 batches it is gone — but
because the **diagonal got worse**, not because the block got better. A better estimate of
the coarse structure does not rescue it.

**So the estimation-noise mechanism is refuted.** The block Fisher's disadvantage on this
substrate is not an artefact of estimating 5.3e7 entries from 1024 observations; if it were,
128 batches — an 16-fold better estimate — would have shown it.

## 3. And the ordering reversal it was explaining weakens

| Fisher batches | diagonal | biological block | gap | significance |
|---|---|---|---|---|
| 8 | +0.010 | +0.031 | +0.021 | 0.9σ |
| 32 | +0.028 | +0.073 | +0.045 | 1.6σ |
| 128 | +0.035 | +0.038 | +0.003 | 0.1σ |

The "diagonal beats the block" claim was 1.6σ in the previous fire at 32 batches, and it is
0.9σ at 8 and **absent** at 128. It was never above 2σ, and it does not survive varying the
one hyperparameter that the mechanism said should matter most. **The reversal is suggestive,
not established** — and the paper's §4.6 has been corrected to say so rather than presenting
it as a measured difference in direction.

What *does* survive is narrower and still interesting: on a trained connectome-constrained
network, **the biological synapse partition shows no advantage over its size-matched random
control at any of the five settings now tested** (Fisher batches 8/32/128, λ 0.003/0.01/0.1),
and its ordering against that control **flips sign between them** — the same null-effect
signature the linear work used to identify non-effects. The linear substrate's 12.1σ
advantage for the same grouping does not reproduce here under any setting tried.

## 4. What is robust, and the best configuration found

**The diagonal degrades as its Fisher estimate improves** — +0.010 → +0.028 → +0.035,
monotone — reproducing on the hardened benchmark the effect first seen on the unhardened one
(+0.063 → +0.250). A better-estimated Fisher is a *stronger* penalty at fixed λ, so EWC walks
into over-constraint. This is now confirmed in two configurations and is the most robust
statement in the network line.

**The best configuration found is the diagonal with a weak penalty *and* a coarse estimate**:

| | value |
|---|---|
| λ | 0.003 |
| Fisher batches | 8 |
| diagonal forgetting | **+0.010 ± 0.010** |
| naive forgetting | +0.066 ± 0.019 |
| **advantage** | **−0.056 ± 0.021, 2.6σ** |

Both "less is more" directions: a weak penalty, and a Fisher estimated from few batches.
Neither is a satisfying answer for a method — it amounts to "anchor gently and do not
estimate the curvature too carefully" — but it is what the measurements say, and the
mechanism is consistent: on this substrate EWC's value comes from supplying a small amount
of memory, and the more confidently that memory is estimated the more it over-constrains.

## 5. Where the network line stands

| claim | status |
|---|---|
| the benchmark contains a real CL problem | **yes**, with a narrow read-out (plastic − frozen gap +0.102) |
| diagonal EWC helps | **yes, and best at a weak penalty with a coarse Fisher estimate**: +0.010 vs naive's +0.066, **2.6σ** |
| replay helps | **no** on the hardened benchmark |
| the biological synapse partition beats a matched random one | **no**, in five settings, with the sign flipping between them |
| the diagonal beats the block-diagonal (reversing the linear substrate) | **weakened to suggestive** — 1.6σ at one batch count, absent at another, never above 2σ |
| the reversal is caused by estimation noise | **refuted** — 128 batches (16× better estimate) does not recover it |
| a better Fisher estimate improves any EWC variant | **no, the opposite** — the diagonal degrades monotonically |

## 6. Next

1. **Why replay stopped helping** is now the most interesting open inversion: it contradicts
   the LGCL v7 expectation that content memory dominates regularisation in the
   partially-observed regime, and the narrow read-out makes the regime *more* partially
   observed while replay loses its edge. The replay budget (16 stimuli/task) was never tuned.
2. **An honest account of the reversal** is still missing. Estimation noise is out; the
   remaining candidates are structural — the block penalty constrains *groups of synapses*,
   which for a weight matrix generated by propagating activity may simply not be the right
   shape, the same way `e7` found that interference must be measured post-propagation rather
   than from the anatomy.
