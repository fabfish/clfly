# E3 — the anchoring basis on wiring-derived tasks

**Date:** 2026-09-22
**Script:** `experiments/e3_basis_selection.py`
**Artifacts:** `runs/e3_real.json`
**Setup:** circuit `mb+cx+al@n1307` (d=1307), 5 tasks propagated through the wiring,
2 seeds, matched-budget controls throughout

---

## 1. How the tasks were built

Each task is a *functional assembly* — an input population named by cell types —
driven through the connectome's propagator `G = (I − W)^{-1}`:

    Sigma_k = G D_k G^T

with `D_k` diagonal on the assembly's neurons, sparse-coded, and `W` rescaled to
spectral radius 0.9 so the linear rate model has a fixed point. Five tasks:
odour identity (Kenyon cells), odour valence (MBON + DAN), heading (central
complex ring neurons), odour input (antennal lobe), innate odour (lateral horn).

Nothing is imposed by hand. The **orientation** of each task's covariance is
determined by the wiring, and each task's precision `J_k` has rank equal to its
assembly size (127–300 of 1307), so every task is **partially observed** — the
regime LGCL v7 measured to make memory 12.7× more valuable than in the
fully-observed one. We land there because sparse coding is real.

Two facts about the resulting task set that turned out to be the whole story:

- Consecutive tasks are **near-orthogonal**: median principal angle 88–90°.
- Their supports are **disjoint** (overlap 0.000).

That is the fly's modularity, visible directly in the task geometry. Different
behaviours recruit different cell types, and the wiring does not scramble them
together.

## 2. Result 1 — the gap is one to two orders of magnitude larger than in the synthetic family

| | final-error gap vs oracle |
|---|---|
| LGCL `exp1` (d=20, random task rotations) | **< 1%** |
| EWC diagonal on wiring-derived tasks (d=1307) | **+45.5%** |

The oracle's own final error is 0.0513; the diagonal-anchored filter's is 0.0747.
This is the substrate effect (claim C1) in its strongest form. LGCL finding 1's
"the diagonal approximation is almost free" is not a property of EWC — it is a
property of random task geometry, and it does not survive contact with a real
connectome.

## 3. Result 2 — biological partitions beat size-matched random partitions, at 4 of 5 rungs

Paired contrast at **matched parameter count** (identical group-size
distribution, so identical capacity; only the *grouping* differs):

| biological rung | constrained | bio gap | random gap | delta |
|---|---|---|---|---|
| `side` | 0.501 | +0.123 | +0.245 | **−0.121** |
| `cell_class` | 0.828 | +0.282 | +0.386 | **−0.103** |
| `ito_lee_hemilineage` | 0.967 | +0.363 | +0.439 | **−0.075** |
| `supertype` | 0.974 | +0.397 | +0.446 | **−0.049** |
| `cell_type` | 0.979 | +0.455 | +0.451 | +0.004 |

Four of five in the same direction, with the largest effects on the coarser
rungs. A fly's own cell groupings are a better place to anchor a Fisher matrix
than an arbitrary partition of the same size — which is claim C2, supported but
**modest**: the gain is 5–12 points of gap against a baseline gap of 24–45, so
biology buys roughly a quarter of the available improvement, not all of it.

Note also that `cell_type` — the rung fly neuroscience would reach for first —
shows **no gain at all**. At 0.979 constrained it is nearly the diagonal, and
there is nothing left for its structure to buy.

## 4. Result 3 — the gap is governed by constrained_fraction, and that is the trap

Ordering the bases by how much of the covariance they discard:

| constrained_fraction | basis | gap |
|---|---|---|
| 0.501 | `side` | +0.123 |
| 0.828 | `cell_class` | +0.282 |
| 0.967 | `ito_lee_hemilineage` | +0.363 |
| 0.974 | `supertype` | +0.397 |
| 0.979 | `cell_type` | +0.455 |
| 0.999 | `diagonal` (EWC) | +0.455 |

Monotone. The single best predictor of how much a basis loses is **how much of
the covariance it throws away** — not which neurons it groups. That is why the
biological advantage can only be read at matched `constrained_fraction`, and why
the ladder's real problem is that most of its rungs sit at the extremes.

## 5. Negative result — the LGCL v8 alignment scalar does not predict the ranking

The mechanism story said the anchoring penalty is a geometric resonance between
the anchoring basis and the task's precision basis, so the mean `cos²` of the
principal angles between a partition's indicator span and the task subspaces
should order the bases. It does not.

First finding: the **raw** alignment is anti-correlated with the gap, because a
finer partition has a *larger* indicator span and therefore overlaps every
subspace more for free. `cell_type` scored 0.667 (highest) and lost the most.
Any use of this scalar must be dimension-normalised.

Second finding: even after adding an **empirically measured chance level** (mean
alignment against random subspaces of the same dimension), the ordering is only
partly recovered:

| rung | excess alignment | gap rank |
|---|---|---|
| `side` | 1.52 | 1 (best) ✓ |
| `cell_class` | 1.22 | 2 ✓ |
| `cell_type` | 1.08 | 5 (worst) ✗ |
| `supertype` | 0.96 | 4 ✓ |
| `ito_lee_hemilineage` | 0.37 | 3 ✗ |

3 of 5. And `ito_lee_hemilineage` is the informative failure: it is aligned
**below chance** (0.37) yet still beats its own random control by 0.075. So for
that rung the alignment mechanism is not what is doing the work — something else
about the biological grouping is.

This is the most useful thing the experiment produced, because it is a
well-posed negative: the v8 resonance is real for a *single* partition against a
*single* task basis, but it does not compose into a predictor over a ladder of
partitions against a sequence of tasks. Either the right scalar is different, or
the benefit has a second source.

## 6. A metric warning, re-confirmed

The forgetting *ratio* against the oracle is enormous (+21 to +77) and useless.
The oracle's forgetting is 0.0004 — the exact filter barely forgets these tasks —
so the ratio is a division by near-zero. Absolute values: oracle 0.0004, EWC
0.0341. A real 80× difference in a quantity that is itself tiny.

This is the shrinkage-bias trap the LGCL audit note flagged, showing up
independently on the connectome. **Report absolute forgetting, and report the
oracle's level next to it**; a ratio against a near-zero reference manufactures
impressive-looking numbers out of nothing.

## 7. Status and what's next

Supported: C1 (substrate effect, strongly), C2 (biological > matched random, 4/5,
modestly). Not supported as stated: the v8 alignment predictor (C2's mechanism).

Next:

1. **The topology contrast (C1 proper).** The near-orthogonality of the tasks is
   *because of* the modularity. Rewiring the circuit (degree-preserving,
   target-shuffled, Erdős–Rényi) should scramble the assemblies together and make
   the tasks interfere — if the gap grows monotonically along that axis, C1 has
   its mechanism, and it becomes a statement about why real brains resist
   forgetting rather than a table of gaps.
2. **Where does the hemilineage gain come from?** Its excess alignment is below
   chance and it still wins. Candidates: developmental lineage correlates with
   shared neuromodulatory or input structure that the partition's *within-block*
   covariance happens to capture. Testable by comparing the biological partition
   against random partitions that are matched not only on size but on within-block
   wiring density.
3. **Granularity interpolation.** The useful regime is between `cell_class` (0.83)
   and `cell_type` (0.98) — a partial cell-type partition that pools the smallest
   types. The annotation vocabulary does not provide it, so it has to be
   constructed, and it is where the biological advantage is largest.
4. Scale to `d ≈ 3000` to check the result is not a small-circuit artefact.
