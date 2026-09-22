# E28 — the rung question, answered at the λ where the effect is resolved: the coarser rung wins, and it wins because the finer one *loses*

**Date:** 2026-09-22
**Script:** `experiments/e8_rate_network.py --basis side --lam 0.1 --methods naive,ewc-block,ewc-block-rand --repeats 3`
**Artifacts:** `runs/e28_side_lam0.1.json`, `runs/e8_basis.json` (both λ = 0.1, batches = 8, same seeds)

---

## 1. What was missing, and why this run supplies it

The e10 rung ladder measured three synapse rungs at λ = 1.0 and found all three to be nulls against
their own matched controls — and λ = 1.0 is the λ at which the `cell_class` contrast is *smallest*
(−0.0185 against −0.0648 at λ = 0.1). So the rungs had been sampled where the effect is weakest, and
the **rung question** — does a coarser anchoring basis do better? — was never asked at a λ where
anything resolves.

`e28` puts the **coarsest** rung, `side` (0.6947 constrained), at λ = 0.1, where `cell_class`'s
contrast is a resolved 2.65σ. Both runs share `seed0 = 0` and 3 repeats, so their replicates
correspond exactly (each `run_method` reseeds `torch` and NumPy from `seed`, independently of which
other methods the run contains — the naive arms of five different runs are identical to four
decimals, which is what makes this checkable).

## 2. The two rungs at the same λ

| rung | constrained | biological | matched random | Δ accuracy | σ paired |
|---|---|---|---|---|---|
| **`side`** | **0.6947** | 0.8264 | 0.8194 | **+0.0069 ± 0.0145** | 0.48 |
| `cell_class` | 0.9250 | 0.7755 | 0.8403 | **−0.0648 ± 0.0245** | **2.65** |

**Opposite signs at the same λ.** `side` shows a small unresolved advantage; `cell_class` shows a
resolved disadvantage. Per replicate they are cleanly separated:

```
side        Δ accuracy   +0.0139  −0.0208  +0.0278
cell_class  Δ accuracy   −0.0278  −0.0556  −0.1111
```

## 3. The rung contrast, paired on the shared seeds

Subtracting the two *deltas* per replicate — which is the matched comparison, since each rung is
scored against its own size-matched control:

| metric | `side` − `cell_class` per replicate | mean | σ paired |
|---|---|---|---|
| accuracy | **+0.0417, +0.0347, +0.1389** | **+0.0718 ± 0.0336** | **2.13** |
| forgetting | −0.0208, +0.0208, −0.1979 | −0.0660 ± 0.0671 | 0.98 |

**The coarser rung is better by 0.072 accuracy at 2.13σ, and the sign is the same in all three
replicates.** That is the first *positive* rung-level evidence in the network line, and its direction
is the one the neuron result predicts — on neurons, `side` was the strongest rung (28.8σ) and the
fine rungs bought nothing.

## 4. But the reading matters: the coarse rung wins because the fine one *loses*

The contrast is between two **deltas**, not two absolute accuracies. `side`'s own delta is
**+0.0069 (0.48σ)** — nothing. `cell_class`'s is **−0.0648 (2.65σ)** — a resolved *disadvantage*
against its own control. So the 2.13σ rung difference is carried almost entirely by the finer rung
**losing to its random control**, not by the coarser rung gaining.

That is not the neuron-level story. On neurons, the coarse rung beat a matched random partition
because the biological grouping was *better*; here, the coarse rung beats the fine one because the
fine one is *worse than random*. Same ordering, different mechanism, and the difference is worth
stating because the two would be conflated by quoting "the coarser rung wins at 2.13σ".

The mechanism distinction also suggests a test: if the effect is "fine partitions anchor badly",
it should degrade smoothly between 0.6947 and 0.9250 rather than appearing as a step, and the two
intermediate rungs (`ito_lee_hemilineage` 0.9945 and `supertype` 0.9988) should be at least as bad
as `cell_class`. Both are measured — **at λ = 1.0 only**, so the test needs one more run each.

## 5. What this does to C2b

The previous fire's conclusion — *the rung hypothesis is not supported* — was drawn from `side`'s
null against its own control at λ = 1.0. That remains true and is not contradicted here. What
changes is that the **rung comparison itself** now has a direction and a significance at a λ where
the effects resolve:

> At λ = 0.1, batches = 8, the coarsest synapse rung is 2.13σ better than the second-coarsest
> *relative to their respective size-matched random controls*, in the direction the neuron result
> predicts — with the caveat that the difference is carried by the finer rung being worse than
> random rather than the coarser one being better than it.

So `C2b` moves from "no rung evidence" to "**one rung contrast, at one λ, at 2.13σ, in the predicted
direction, with its mechanism unresolved**".

## 6. Limits

- **n = 3.** 2.13σ with three paired observations, so the sem carries roughly 50% relative error and
  the interval on +0.0718 is wide. It is a signal, not a settled number.
- **The two runs contain different method lists** (3 methods against 5). Each `run_method` reseeds
  from its own `seed`, so the arms should be identical given the seed, and the identical naive arms
  across five runs support it — but **no run has yet reproduced an `ewc-block` arm across method
  lists**, and that check costs one 35-minute run. It is the assumption the whole comparison rests on.
- Two rungs of five, so "the coarse rung is better" is a statement about `side` versus `cell_class`
  and not about the axis.
- The forgetting contrast is 0.98σ, so the accuracy result is the only one carrying the claim.

## 7. What to run next

1. **The method-list check** (§6): `--basis cell_class --methods ewc-block --lam 0.1 --iters 500
   --repeats 3` should reproduce `e8_basis`'s `ewc-block` arm exactly. One run, and it validates the
   cross-run comparison the rung claim depends on.
2. **The two intermediate rungs at λ = 0.1** (`ito_lee_hemilineage`, `supertype`) — two runs — which
   decide between "a smooth gradient in granularity" and "a step", i.e. between §4's two mechanisms.
3. **More repeats on the `side`/`cell_class` contrast**, since 2.13σ from three pairs is the weakest
   part of it.

---

## 8. The method-list assumption is now verified, bit for bit

§6 named one assumption the whole cross-run comparison rests on: that an `ewc-block` arm depends
only on its `seed`, not on which other methods the run contains. `e31` tested it directly —
`--basis cell_class --methods ewc-block,ewc-block-rand --lam 0.1 --iters 500 --repeats 3`, the
2-method version of the 5-method `e8_basis` run — and the arms are **identical to the last decimal
in every replicate**:

| arm | metric | published (5-method run) | `e31` (2-method run) |
|---|---|---|---|
| `ewc-block` | accuracy | 0.8263888756, 0.7708333333, 0.7291666667 | **same** |
| `ewc-block` | forgetting | 0.1041666865, 0.1875, 0.2395833135 | **same** |
| `ewc-block-rand` | accuracy | 0.8541666667, 0.8263888955, 0.8402777712 | **same** |
| `ewc-block-rand` | forgetting | 0.0416666865, 0.1354166865, 0.0833333135 | **same** |

So the caveat is removed: the paired cross-rung contrast of §3 — `side` minus `cell_class`,
+0.0718 ± 0.0336 at 2.13σ — is a comparison of two arms that differ only in their partition.

It also settles a more general question the project had not checked. Every cross-run comparison in
the network line (the λ arm assembled from `e8_basis`, `e10` and `e25`; the three-rung table; the
λ-robustness of the `cell_class` negative) depends on this independence, and none of them could have
detected a violation — because a violation would have looked like a difference between
configurations, which is what they were measuring. **The check has to be run deliberately, and it
had not been.**

## 9. What remains open on the rung claim

- **n = 3.** The 2.13σ rests on three paired replicates; the sem carries ~50% relative error.
- **Mechanism.** The coarse rung wins because the fine one *loses to its own control* (−0.0648,
  2.65σ), not because the coarse one gains (+0.0069, 0.48σ). Which means the next test is whether
  the effect is a smooth gradient in granularity or a step: the two intermediate rungs
  (`ito_lee_hemilineage` 0.9945, `supertype` 0.9988) are measured at λ = 1.0 only, and if the effect
  is "fine partitions anchor badly" they should be at least as bad as `cell_class`.
- **Scope.** Two rungs of five, one λ, one circuit.
