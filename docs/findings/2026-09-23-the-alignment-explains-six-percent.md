# E75 — the fourth candidate fails, and this one asked the right question: the alignment explains **6.6%** of the control's draw-to-draw variance

**Date:** 2026-09-23
**Script:** `experiments/e75_task_pair_spread.py`
**Artifact:** `runs/e75_task_pair_spread.json` (9 partitions × 6 draws × 3 task seeds, d = 1307)
**Context:** `2026-09-23-the-alignment-predictor-is-refuted.md` (e72), `2026-09-23-side-draw-sd-refutes-the-concentration-model.md` (e67), `2026-09-22-draw-sd-mechanism.md`

---

## 1. The prediction, and what the design fixed

`e67` refuted the project's one-scalar model of the control's draw spread and `e72` refuted its
pre-registered replacement. Three candidates had failed — group count, concentration, the alignment
spread — and `e72` diagnosed two distinct things wrong with how the third had been posed:

* it **divided by a chance level** (`alignment_of` reports `raw / chance` against a *generic* random
  subspace), which strips each partition's free size advantage and, on that measurement, the task
  information with it;
* it measured a **spread**, and a quantity can have a large spread and no relationship to the excess at
  all — which is exactly what `e72` found, the normalised spread being a monotone re-expression of the
  span size (ρ = −0.904) and scoring **−0.500** against the target.

`e75` fixes both: the quantity is the **bare `alignment_score`** (mean `cos²θ` between the indicator span
and the task's own top-16 spectral subspace), and the question is **co-movement** — do the alignment and
the control's excess move *together* when the labels are reshuffled?

**And the task draw is held fixed, which is the design decision that makes the number mean anything.**
Both variables move a great deal with the task geometry, so a correlation pooled over `(draw, seed)`
pairs would be dominated by the seed dimension and would answer a question about the tasks. Every
correlation here is therefore computed **within a seed**, across draws, after centring each variable by
its own seed mean — isolating the one dimension a relabelling moves.

The pre-registered prediction: within-partition co-movement **≥ +0.5**, its ordering across the nine
partitions tracking the measured draw spread at **Spearman ≥ +0.8**, with a concentration correlation
below +0.5. Falsifier: **a co-movement at or below zero.**

## 2. The result: +0.17, and the sign flips for the rungs the claims lean on

| partition | concentration | measured draw sd | within-seed **r** | within-seed ρ | seeds positive |
|---|---|---|---|---|---|
| `cell_type` min 3 | 0.395 | 1.01e-3 | **+0.568** | +0.546 | 3/3 |
| `cell_type` min 4 | 0.459 | 6.13e-4 | +0.315 | +0.158 | 2/3 |
| `supertype` | 0.026 | 8.35e-5 | +0.233 | +0.234 | 2/3 |
| `cell_type` min 1 | 0.020 | 6.80e-5 | +0.232 | +0.278 | 2/3 |
| `cell_type` min 6 | 0.536 | 7.28e-4 | +0.215 | **−0.061** | 2/3 |
| `cell_type` min 2 | 0.325 | 9.29e-4 | +0.112 | +0.176 | 3/3 |
| `ito_lee_hemilineage` | 0.032 | 4.16e-5 | +0.008 | +0.040 | 2/3 |
| **`cell_class`** | 0.171 | 2.37e-4 | **−0.031** | **−0.102** | **1/3** |
| **`side`** | 0.498 | 2.16e-4 | **−0.127** | **−0.096** | 2/3 |

| quantity | result | predicted |
|---|---|---|
| within-partition co-movement, mean ρ | **+0.130** (mean *r* +0.170) | ≥ +0.5 |
| **variance it explains, mean *r*²** | **0.066** | — |
| Spearman(co-movement, measured draw sd) | **+0.150** (Pearson version +0.350, p = 0.36) | ≥ +0.8 |
| Spearman(concentration, measured draw sd) | **+0.617** | < +0.5 |
| partitions with a **non-positive** co-movement | **3 of 9** | 0 |

**So the prediction fails on every clause, the falsifier fires three times, and the scalar it was meant
to improve on scores four times better against the target.** The three non-positive partitions include
`cell_class` and `side` — the two rungs the paper's C2 claims actually rest on.

**And the mean +0.17 is not distinguishable from zero at this sample size.** With 18 seed-centred points
the standard error on a correlation near 0.17 is about 0.24, so the honest form is **+0.17 ± 0.24**,
against a pre-registered +0.5 — the prediction is refuted by being *too small to see*, not by being
backwards, and the one partition that does stand out (`cell_type` min 3 at +0.568) is also the one with
the largest draw sd, which is what a real relationship would look like if there were more of it.

## 3. Why this failure matters more than the previous three

The three earlier candidates were all **functions of the partition alone**, so their failure was
explained by that: a `(partition, task)` property cannot be read off a partition scalar. `e75`'s
candidate is the opposite — it is computed *against* the task subspace, with no normalisation, and it
asks about co-movement rather than spread. **It had every structural advantage the diagnosis could give
it and it still explains 6.6% of the variance.**

The consequence is a substantive statement about the mechanism, not just another closed door:

> The control's excess does **not** move across relabellings because the relabelled span sits
> differently against the **task's precision subspace**. Whatever drives the draw spread, it is not the
> subspace geometry the whole anchoring story is phrased in.

So the mechanism story needs a different carrier. Two things the four failures now point at together:

* the two candidates that came closest to the target are the two **plainest partition-size scalars**
  (concentration +0.617, and `e72`'s normalised spread at +0.85 *with* concentration, i.e. the same
  thing);
* and the only quantity in the project that has ever ranked anything correctly is
  **`projection_pressure`**, which is not a subspace-overlap at all — it is the amount of each *predicted
  prior* a basis would discard, **weighted by the task's measurement information `J_k`**.

That is a different object from all four failures: it uses the **precision**, not the subspace, and it is
a `(partition, task)` quantity by construction. So the next pre-registration is the natural one:

> **`e80`: does the draw-to-draw spread of `projection_pressure` predict the draw-to-draw spread of the
> control's excess?** Prediction: Spearman ≥ +0.8 across the nine partitions *and* a Spearman below +0.5
> with concentration, since pressure is weighted by the task's information and the failures so far have
> all been unweighted partition geometry. Falsifier: a concentration correlation as high as +0.85, which
> would make it a fifth re-expression of size.

## 4. What this does to the project's numbers

**Nothing.** No σ, no claim about the substrate, the basis or the predictor moves — this is the
draw-*spread* line, which exists to make error bars honest. What it does change is what the project may
say about *why* the matched-random control is one draw:

* the paper's §4.3 says the mechanism is "permuting labels barely changes a partition made of singletons
  and changes a great deal when there are two to ten groups". **That reading is now four times refuted**,
  and the replacement is honest ignorance with a shape: the spread is ≈ 0.003-equivalent in size for
  coarse partitions, the two best predictors of it are partition-size scalars, and no task-relative
  quantity tried has improved on them.
* Every σ in the paper that folds the draw component in keeps the value it has, because the component
  itself is *measured per rung* in each of those places (`e14`, `e17`, `e17b`, `e67`, `e74`) rather than
  predicted. That is why four failed predictors cost the paper nothing: the project stopped predicting
  this quantity and started measuring it.

## 5. Limits

- **Eighteen seed-centred points per partition, but the six draws are shared across seeds**, so the
  effective degrees of freedom are nearer four or five than sixteen and every interval above is wider
  than its nominal width. The design chose to hold the tasks fixed — the alternative, redrawing tasks
  too, would have made the measurement a statement about tasks — so this is a real cost of the right
  design and it is why the finding is stated as "too small to see" rather than "absent".
- **Three task seeds, one circuit size (d = 1307), six draws.** `e72` used six seeds and the same nine
  partitions; the two runs agree that the alignment carries almost nothing, from opposite directions
  (spread and co-movement).
- **One alignment functional.** `alignment_score` is mean `cos²θ` over principal angles; a different
  summary of the same subspaces (the smallest angle, the largest, a weighted mean) could behave
  differently. Nothing here rules that out, and the four failures together are a statement about the
  functionals tried.
- **The draw spread itself is unchanged and still measured.** `e67`'s refutation of the concentration
  scalar as a *budgeting* tool stands: +0.617 at n = 9 is not significant and it mispredicts `side` by
  4.8×.
