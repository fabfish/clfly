# E7 — circuit overlap and interference: the sign is wrong, but the representation predicts

**Date:** 2026-09-22
**Script:** `experiments/e7_interference.py`
**Artifacts:** `runs/e7_interference.json`
**Setup:** circuit `mb+cx+al@n1307`, 5 tasks, 3 seeds, analytic error matrix

---

## 1. The claim being tested

The research plan's C4: FlyCL's tasks engage different circuits, so *which* tasks
interfere should be predictable from how much those circuits overlap. If it holds, a
continual-learning benchmark gets something no existing suite has — a biology-derived
prior on the interference matrix, readable before any training run.

E2 had already refuted the *aggregate* version of this story (the total EWC excess
moves opposite to mean task overlap). But aggregate trends can hide pairwise
structure, so C4 deserved a direct test. Interference is read off the exact analytic
error matrix as the **marginal damage** to task `j` from learning task `k`:

    I[j, k] = E[k, j] - E[k-1, j]

which the analytic machinery provides exactly, with no sampling noise.

## 2. Test 1 — controlled overlap: more overlap means *less* interference

Supports are built from a shared pool plus disjoint private complements, so every pair
has **exactly** the same input overlap by construction. Sweeping the pool size sweeps
one number with nothing else moving.

| target overlap | achieved (Jaccard) | mean interference | adjacent pairs (d=1) | distant pairs (d>1) |
|---|---|---|---|---|
| 0.00 | 0.000 | +0.015347 | +0.025751 | +0.008411 |
| 0.10 | 0.053 | +0.013057 | +0.022033 | +0.007073 |
| 0.25 | 0.143 | +0.010680 | +0.014882 | +0.007879 |
| 0.50 | 0.333 | +0.007330 | +0.005050 | +0.008850 |
| 0.75 | 0.600 | +0.006812 | +0.002334 | +0.009798 |
| 1.00 | 1.000 | +0.006111 | **−0.001327** | +0.011069 |

> **Spearman(overlap, mean interference) = −1.000**, perfectly monotone.

**C4's direction is refuted**, and by a clean controlled manipulation rather than an
aggregate trend. Sharing input populations *reduces* interference, and at full overlap
adjacent tasks **help** — interference goes slightly negative. The mechanism is
visible in the split: adjacent pairs fall steeply (+0.0258 → −0.0013) while distant
pairs drift slightly *up* (+0.0084 → +0.0111). Sharing measurement directions lets
the next task confirm rather than compete; it is competing *directions*, not shared
ones, that cost capacity under a diagonal projection.

This agrees with E2, which found the excess falling as rewiring *raised* task overlap
— two independent manipulations, same sign, same conclusion.

*(The `achieved` column is Jaccard, `|A∩B|/|A∪B|`; the construction controls
`|A∩B|/size`, and for equal-size sets the two are related by `J = f/(2−f)`. The
construction is exact in its own terms.)*

## 3. Test 2 — real assemblies: anatomy carries no signal at all

The actual mushroom body / central complex / antennal lobe assemblies at the standard
scale:

| quantity | Spearman with interference |
|---|---|
| anatomical support overlap | **+0.103** |
| **propagated subspace alignment** | **+0.939** |
| support overlap vs propagated alignment | +0.261 |
| task size (support) vs interference — confound | +0.164 |
| task size vs propagated alignment — confound | +0.297 |

Two things to read off this.

**All ten pairs have exactly zero anatomical overlap.** The assemblies recruit
disjoint cell types, so "circuit overlap" is not a variable in the real circuit at
all — the +0.103 is noise around a constant. The original C4 phrasing, "tasks engage
different circuits", is *false in the sense that matters*: they engage different
circuits, which is precisely why their anatomical overlap carries no information.

**What does predict interference is the propagated representation**, at +0.939. The
propagator mixes disjoint input populations, so two tasks that share no neurons can
still drive overlapping directions once activity spreads — and that is what competes.

**The +0.939 is robust, not one pair.** Leave-one-out over the ten pairs spans
**[+0.917, +0.983]**, so no single pair carries it. And the obvious confound — that
interference might simply track how much information each task carries — is weak:
task size correlates +0.164 with interference and +0.297 with propagated alignment,
neither enough to explain +0.939.

## 4. What C4 becomes

Refuted as stated, supported in a corrected form:

> **An interference prior for a connectome-constrained benchmark must be read from the
> propagated representation, not from the anatomy.** Anatomical overlap between task
> circuits is exactly zero in the real circuit (and carries the *wrong sign* when
> controlled experimentally), while the alignment of the tasks' precision subspaces
> after propagation predicts pairwise interference at ρ = +0.94, leave-one-out robust
> and not a size artefact.

That is a better result than the original claim, because "circuit overlap" was
ambiguous between the two readings and the ambiguity turns out to be the whole
finding. It is also immediately actionable for benchmark design: compute the task
covariances, measure their subspace alignment, and you have an interference prior —
no training runs needed.

The remaining limitation is that ten pairs is a small sample, and only five tasks are
involved. A benchmark with more tasks would test the prior on more pairs; that is the
natural next step, and it is the same step that would build the behavioural task suite
the substrate was motivated by.

## 5. Status of the plan's claims

| claim | status |
|---|---|
| **C1 geometry** | solid (deterministic, 7× vs chance) |
| **C1 mechanism** | refuted; the penalty does not track interference |
| **C2** | resolved at 4 of 5 rungs, up to 28.8σ; predictor at ρ = +0.99 |
| **C3 modularity** | untested, and weakened by C1's refutation |
| **C4 interference prior** | **refuted as stated, supported post-propagation** (ρ = +0.94) |
