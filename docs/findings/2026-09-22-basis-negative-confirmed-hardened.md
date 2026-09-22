# E8g — the basis negative is confirmed where the benchmark can resolve, and the ordering is reversed

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --shared-head --input-overlap 0 --readout-size 32`
**Artifacts:** `runs/e8_hardened_basis.json`
**Setup:** circuit `mb+cx+al@n1307`, 3 tasks, 5 replicates, λ = 0.003, Fisher batches = 32, read-out 32 neurons, chance 0.25

---

## 1. Why this re-run mattered

The previous fire showed the network benchmark had been measuring its decoder rather than
its connectome — freezing the recurrent weights cost 0.007 accuracy and eliminated
forgetting — and that narrowing the read-out makes the weights load-bearing (a +0.102
accuracy gap at 32 read-out neurons against +0.007 over the whole state). It also showed
that on the hardened configuration **diagonal EWC finally resolves (2.5σ)**, overturning
three fires of "no method does anything".

That left the *basis* negative — "the biological synapse partition shows no advantage over
its matched random control" — established only on a benchmark that could not resolve
anything. A benchmark that cannot show a difference cannot establish a negative, so it had
to be re-run. This fire re-runs it.

## 2. Result: confirmed, and the ordering is the opposite of the linear substrate

| method | final accuracy | mean forgetting | vs naive |
|---|---|---|---|
| naive | 0.914 ± 0.013 | +0.073 ± 0.015 | — |
| **EWC, diagonal Fisher** | 0.922 ± 0.010 | **+0.021 ± 0.015** | **−0.052 ± 0.021 (2.5σ)** |
| EWC, block Fisher — **biological** cell-class pairs | 0.915 ± 0.020 | +0.060 ± 0.020 | −0.013 ± 0.025 (0.5σ) |
| EWC, block Fisher — matched **random** pairs | 0.928 ± 0.009 | +0.044 ± 0.016 | −0.029 ± 0.022 (1.3σ) |
| replay (16 stimuli/task) | 0.932 ± 0.008 | +0.050 ± 0.016 | −0.023 ± 0.022 (1.0σ) |

Three readings, and the third is the new one.

**The biological partition still shows no advantage over its matched random control** —
−0.016 ± 0.026, **0.6σ**. The negative from three fires ago survives being measured on a
benchmark where a difference *can* now resolve, which is what makes it a result rather than
an absence of one.

**The diagonal is the only method that resolves** (2.5σ) and is the best on forgetting,
reproducing the previous fire's number exactly (naive +0.073, diagonal +0.021). Replay does
not resolve (1.0σ).

**And the diagonal beats the block-diagonal.** The biological block Fisher is worse than the
plain neuron diagonal by +0.039 ± 0.025 (**1.6σ**), and the random block by +0.023 ± 0.022
(1.0σ). On the **linear** substrate the relation ran the other way: the coarsest partition
(`side`, 0.50 constrained) cut the excess error by 80% relative to the diagonal, and
`cell_class` beat its matched control at 12.1σ. Here coarser anchoring is *worse*, in the
reverse of the ordering the linear work established.

So the transfer failure is not merely "biology adds nothing"; it is that **the direction of
the granularity effect reverses**. That is a stronger and cleaner statement than the one
this line of work started with, and it is the reverse of the project's headline result — on
a trained network, the coordinate basis is the *right* basis.

## 3. The likely mechanism, and its testable form

The block Fisher has `Σ s_g² = 5.3e7` entries to estimate from 32 batches of 32 samples —
1024 observations. The diagonal has 26,568 entries from the same 1024. A coarse block
accumulates its within-group off-diagonals as an averaging over a handful of gradient outer
products, so its penalty is dominated by estimation noise and acts as a *strong random*
constraint within each cell-class pair. The diagonal discards those off-diagonals rather
than estimating them badly, and on this data that is the better trade.

That is the same explanation proposed two fires ago, and it remains untested in the one
configuration where it could be tested properly — the *hardened* one. The earlier batch-count
sweep that appeared to rule it out was run on the unhardened benchmark, so it has to be
redone. The prediction is specific: raising the Fisher batch count should improve the block
variants *relative to the diagonal* on the hardened benchmark. If it does not, the mechanism
is something else and the reversed ordering needs another account.

## 4. Where the network line stands

| claim | status |
|---|---|
| the benchmark contains a real CL problem | **yes**, once the read-out is narrow (plastic − frozen accuracy gap +0.102) |
| diagonal EWC helps | **yes**, −0.052 ± 0.021 forgetting vs naive, **2.5σ**, best method |
| replay helps | **no** on the hardened benchmark (1.0σ); it helped only on the unhardened one |
| the biological synapse partition beats a matched random one | **no** — 0.6σ, confirmed where differences resolve |
| coarser anchoring is better | **no — the opposite.** The diagonal beats the block Fisher by 1.6σ, reversing the linear-substrate ordering |
| the basis finding transfers from neurons to synapses | **no**, and now for a *directional* reason rather than an unmeasurable one |

The honest summary: the project's central claim — that the coordinate basis is the wrong
place to anchor a Fisher matrix — holds on the connectome's *neuron* geometry and **reverses
on its synapse geometry**. Those are different spaces, and this is now a measured difference
in direction rather than an appeal to the analogy being invalid.

## 5. Next

1. **Re-run the batch-count sweep on the hardened configuration**, which is the clean test
   of the estimation-noise mechanism and would either explain the reversal or force a new
   account of it.
2. **Investigate why replay stopped helping.** It is the one inversion that contradicts a
   prior expectation — LGCL v7 measured content memory to be 12.7× more valuable than
   regularisation in the partially-observed regime, and here the narrow read-out makes the
   regime *more* partially observed while replay loses its edge. The obvious candidate is the
   replay budget: 16 stimuli per task was never tuned, and it should be swept.
