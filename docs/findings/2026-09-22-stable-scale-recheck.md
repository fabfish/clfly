# Re-checking e2 and e3 on the stable scale

**Date:** 2026-09-22
**Scripts:** `experiments/e3_basis_selection.py`, `experiments/e2_topology_gap.py`
**Artifacts:** `runs/e3_real.json`, `runs/e2_topology.json`

Both experiments were re-run after the previous fire found the headline metric to be
chaotic. Three changes to the design, all forced by that finding:

1. **Absolute excess error instead of the ratio**, with a standard error across
   seeds (`paired_excess`).
2. **Paired task draws.** One set of task sequences per condition, with every basis
   scored on *the same* sequences. Previously each basis got its own task draw
   inside the seed loop, so basis differences were contaminated by task
   differences — and on this substrate the task-to-task spread is larger than most
   of the effects.
3. **A fix to e2's condition structure.** The circuit was re-extracted *inside* the
   seed loop, so each seed got a differently-rewired graph and the seeds were not
   replicates of the same condition. The circuit and its rewiring now belong to the
   topology.

---

## 1. e3 — the biological-basis advantage is directionally real but not resolvable

d=1307, 5 seeds, oracle final error 0.0528, matched capacity throughout.

| basis | constrained | **excess** | sem | vs matched random | sem(delta) | verdict |
|---|---|---|---|---|---|---|
| `bio:side` | 0.501 | **+0.00404** | 0.00176 | −0.00540 | 0.00413 | not resolvable |
| `bio:cell_class` | 0.828 | +0.01119 | 0.00392 | −0.00441 | 0.00717 | not resolvable |
| `bio:ito_lee_hemilineage` | 0.967 | +0.01475 | 0.00524 | −0.00361 | 0.00839 | not resolvable |
| `bio:supertype` | 0.974 | +0.01625 | 0.00561 | −0.00214 | 0.00862 | not resolvable |
| `bio:cell_type` | 0.979 | +0.01880 | 0.00672 | +0.00042 | 0.00941 | not resolvable |
| `diagonal(EWC)` | 0.999 | +0.01889 | 0.00674 | — | — | — |

**Zero of five rungs resolve.** Every delta is about 1.3 standard errors. The
*directions* are consistent with e3's original claim (four of five negative, and
`cell_type` — the rung that is nearly the diagonal — at zero), so the effect is
probably real, but **e3's "4 of 5 rungs beat their matched random control" does not
survive a stable metric.** At this effect size and spread, resolving a delta at 2σ
needs roughly 12 seeds, and at 3σ roughly 27.

That is the honest statement of where C2 stands: a consistent direction, a
plausible mechanism, and no statistical resolution at feasible budget.

## 2. e3 — what *is* resolved: the granularity trade-off

Ordering the same bases by how much covariance they constrain gives a monotone
trend on the stable metric:

| constrained_fraction | basis | excess |
|---|---|---|
| 0.501 | `bio:side` | +0.00404 ± 0.00176 |
| 0.828 | `bio:cell_class` | +0.01119 ± 0.00392 |
| 0.967 | `bio:ito_lee_hemilineage` | +0.01475 ± 0.00524 |
| 0.974 | `bio:supertype` | +0.01625 ± 0.00561 |
| 0.979 | `bio:cell_type` | +0.01880 ± 0.00672 |
| 0.999 | `diagonal(EWC)` | +0.01889 ± 0.00674 |

Five of six points in order, and the extremes are separated by
`0.01485 ± 0.00697` — **2.1σ, resolved.** So the one performance claim this
substrate supports is:

> Anchoring the Fisher in the coarsest basis (`side`, 0.50 constrained) rather than
> the neuron diagonal (0.999) cuts the excess error over the exact oracle by about
> 80% (0.0189 → 0.0040), and the reduction is monotone in how little the basis
> throws away.

This is a real result and it is *not* about biology — it is about granularity. Which
is the uncomfortable companion to C2: the thing that reliably helps is anchoring in
*broader* groups, and the fly's own annotation ladder happens to supply its best
rungs (side, cell_class) at the coarse end.

## 3. e3 — the alignment predictor still fails, with truncation

The previous fire identified the likely cause of the failed principal-angle
predictor: taking the top-*rank* subspace returns the task's whole range space,
which is blind to drive strength. The predictor was therefore re-run on a
spectrally **truncated** subspace (`top=16`).

| rung | alignment excess (top=16) | excess rank | alignment rank |
|---|---|---|---|
| `side` | 3.19 | 1 | 1 ✓ |
| `cell_class` | 1.98 | 2 | 2 ✓ |
| `cell_type` | 1.06 | 5 | 3 ✗ |
| `supertype` | 1.05 | 4 | 4 ✓ |
| `ito_lee_hemilineage` | 0.42 | 3 | 5 ✗ |

Three of five — **the same score as the untruncated version.** The truncation does
help in one respect: `side` and `cell_class`, the two rungs with a resolved
performance advantage, are now the two best-aligned, which they were not before.
But `hemilineage` is again the informative failure, sitting last on alignment and
third on performance.

So the range-space degeneracy was a genuine defect worth fixing, and it was not the
main reason the predictor fails. **C2 still has no working a-priori predictor.**

---

## 4. e2 — geometry is solid, everything downstream is underpowered

d=1307, 3 seeds, 3 bases, the same circuit rewired along the swap family.

| topology | overlap | /chance | flattening | **excess:EWC** | sem | **bio − rand** | sem |
|---|---|---|---|---|---|---|---|
| `real` | 0.0075 | 0.135 | 0.692 | +0.03212 | 0.02169 | −0.00920 | 0.02291 |
| `swap0.1` | 0.0105 | 0.190 | 0.625 | +0.03213 | 0.02627 | −0.00680 | 0.02780 |
| `swap0.5` | 0.0230 | 0.414 | 0.265 | +0.02357 | 0.00903 | −0.00006 | 0.01191 |
| `swap2` | 0.0594 | 1.069 | 0.023 | +0.00943 | 0.00217 | +0.00078 | 0.00315 |
| `erdos_renyi` | 0.2892 | 5.207 | 0.385 | **+0.15236** | 0.01769 | +0.00546 | 0.02226 |

**The geometry result stands, and it was never at risk.** Overlap rises monotonically
0.0075 → 0.2892, and relative to chance 0.135 → 5.207: the real connectome keeps the
task subspaces 7× more orthogonal than random subspaces, and rewiring destroys that.
These quantities are computed from eigenvectors, so they are bit-reproducible and
carry no sampling error. This remains the cleanest positive result in the project.

**The one resolved performance statement is about Erdős–Rényi.** Its excess
(0.152 ± 0.018) exceeds the real connectome's (0.032 ± 0.022) by
0.120 ± 0.028 — **4.3σ.** Destroying the degree sequence as well as the targeting
makes the diagonal anchor far worse. But ER is the separate regime identified
earlier (it also makes `(I − W)` near-singular), so this is not evidence for the
interference mechanism — only that conditioning matters a great deal.

**Everything else is underpowered.** The excess over the swap family moves
0.032 → 0.009 (a decrease, again *opposite* to the interference hypothesis, and only
1.0σ at the largest single comparison). The `bio − rand` contrast is monotone across
all five topologies — a signature that is 1-in-120 under a random ordering — but its
total span, 0.0147, is carried by standard errors of ~0.023, so **the sign flip is
not resolved point-by-point.** Monotone direction plus individual underpowering is a
weak-but-real signal, and it should be reported as such rather than as a result.

## 5. What would fix the power

The standard errors are dominated by **task-to-task variance**: each seed draws a
new support and new drive weights, and the resulting `Σ_k` realisation moves the
excess a lot even though the *geometry* barely moves (flattening spread 0.012 for a
gap spread of 1.38). Required seeds to reach 2σ:

| claim | delta | needs |
|---|---|---|
| e3, `bio:side` vs matched random | 0.0054 | ~12 seeds |
| e2, `bio − rand`, real vs ER | 0.0147 | ~29 seeds per topology |

Both are affordable but not cheap (the e2 run took 9 minutes for 3 seeds).

The better fix is a **lower-variance effect size**, and the structure of the problem
suggests one. The LGCL model is linear-Gaussian, so for *fixed* task precisions the
estimator's error is a quadratic form whose expectation over `θ` and the measurement
noise is computable exactly — no seed needed. The remaining variance would then be
only the task-geometry draw, which is the quantity of interest rather than a
nuisance. Implementing the analytic expected error is the single highest-value
methodological step left, and it is queued.

## 6. Where the claims stand

| claim | status |
|---|---|
| **C1 geometry** — the connectome separates task subspaces, rewiring destroys it | **Solid.** Deterministic, monotone across 5 points, 7× vs chance. |
| **C1 mechanism** — the gap is driven by interference | **Refuted**, twice: the excess moves opposite to overlap, and the anisotropy variant was retracted last fire. |
| **C1 magnitude** — a large diagonalisation penalty on a real connectome | **Supported in direction**, but the excess (0.032) is itself uncertain at ±0.022 with 3 seeds. |
| **C2** — biological bases beat matched random ones | **Directionally consistent, unresolved.** 4/5 rungs negative in e3 and monotone across topologies in e2, everything ~1σ or worse. |
| **C2 predictor** — principal angles rank the bases | **Still fails**, 3/5 with or without spectral truncation. |
| **Granularity** — less constraint means less loss | **Resolved** (2.1σ at the extremes), and it is the only performance claim the substrate currently supports. |

The honest summary: this substrate gives **deterministic geometric answers** and
**noisy performance answers**, and most of the earlier programme was reading the
second kind as though it were the first.


---

## Correction (later): the "not resolved" verdict was about the metric, not the effect

The `bio − rand` contrast is resolved point-by-point on the **analytic** estimator, where the same
five topologies give deltas of −0.00276, −0.00202, +0.00102, +0.00042, +0.00213 at σ 2.27–2.75
(`runs/e2_analytic.json`). The SE ≈ 0.023–0.028 quoted above is the **realized** metric's, so §4's
"the sign flip is not resolved point-by-point" was a statement about the estimator, not about the
underlying effect — the same budget-not-effect pattern as the 3-of-5 → 4-of-5 rungs case.

The claim is nevertheless weaker than the paper's abstract stated, for a different reason: those
σ are seed-only and `cell_class` is a coarse partition, so the control-draw component applies and
leaves four of five points resolved with `swap2` at 1.75σ. See
`docs/findings/2026-09-22-sign-flip-under-draw-correction.md`.
