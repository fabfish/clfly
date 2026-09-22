# E81 — the mechanism, at last: `projection_pressure` explains **83%** of the control's draw-to-draw variance, against the alignment's 6.6%

**Date:** 2026-09-23
**Script:** `experiments/e81_pressure_comovement.py`
**Artifact:** `runs/e81_pressure_comovement.json` (9 partitions × 6 draws × 3 task seeds, d = 1307)
**Context:** `2026-09-23-pressure-spread-predicts-the-draw-spread.md` (e80), `2026-09-23-the-alignment-explains-six-percent.md` (e75), `2026-09-23-the-alignment-predictor-is-refuted.md` (e72)

---

## 1. What `e80` left open, and why it mattered

`e80` gave this line its first positive: the **absolute** draw-to-draw spread of `projection_pressure`
ranks the measured draw spread at **+0.767 (p = 0.016)** while correlating only +0.317 with
concentration, after four subspace-overlap candidates had failed. But that is a rank correlation
**across nine partitions** — it says partitions with a bigger pressure spread *tend* to have a bigger
excess spread. It does not say the two quantities move together on the **same relabelling**, and that is
the difference between a lead and a mechanism.

`e81` asks the within-partition question with the design `e75` established: centre each variable by its
own seed mean and correlate **within a seed**, so the task draw is held fixed and only the dimension a
relabelling moves is left. The prediction, written before the run: mean within-seed co-movement
**≥ +0.5**, mean *r*² **≥ 0.25**, and better than the bare alignment's **+0.170**. Falsifier: a mean at or
below +0.170.

## 2. The result, and the cleanest comparison the project has

| partition | **alignment r** (`e75`) | **pressure r** | diff | pressure *r*² | seeds positive |
|---|---|---|---|---|---|
| `cell_type` min 1 | +0.232 | +0.851 | +0.619 | 0.725 | 3/3 |
| `cell_type` min 2 | +0.112 | +0.911 | +0.799 | 0.830 | 3/3 |
| `cell_type` min 3 | +0.568 | +0.949 | +0.380 | 0.900 | 3/3 |
| `cell_type` min 4 | +0.315 | +0.968 | +0.652 | 0.936 | 3/3 |
| `cell_type` min 6 | +0.215 | +0.958 | +0.743 | 0.918 | 3/3 |
| `side` | **−0.127** | +0.681 | +0.809 | 0.464 | 3/3 |
| `cell_class` | **−0.031** | +0.931 | +0.962 | 0.867 | 3/3 |
| `ito_lee_hemilineage` | +0.008 | **+0.980** | +0.972 | 0.961 | 3/3 |
| `supertype` | +0.233 | +0.925 | +0.692 | 0.855 | 3/3 |

| | result | predicted |
|---|---|---|
| mean within-seed co-movement | **+0.906** | ≥ +0.5 → **PASS** |
| mean *r*² (variance explained) | **0.828** | ≥ 0.25 → **PASS** |
| beats the alignment's +0.170 | **YES** | — |
| partitions with a non-positive co-movement | **0 of 9** | falsifier: 0 |
| **paired difference, pressure − alignment** | **+0.736 ± 0.061, 9 of 9 positive, sign p = 0.0039** | — |

**The paired row is the strongest evidence in this line, and it is the same design twice.** The two runs
use the **same nine partitions, the same six relabellings, the same three task seeds, the same
within-seed centring** — the only thing that differs is the quantity being correlated with the control's
excess. `projection_pressure` wins on **every one of the nine**, by an average of **+0.74**, and explains
**83%** of the draw-to-draw variance against the alignment's **6.6%**.

## 3. What the mechanism is, stated plainly

All four failed candidates — group count, concentration, the normalised alignment spread, the bare
alignment — are **subspace overlaps**: they ask where the drive *is*. `projection_pressure` asks how much
of the **predicted prior** the projection discards, **weighted by the task's measurement information
`J_k`** — how strongly each direction is *measured*. And the answer is unambiguous at this sample size:
the control's excess moves across relabellings because the *precision-weighted deficit* moves, and barely
at all because the subspace geometry moves.

So the project can now replace the sentence that was four times refuted:

> The matched-random control is a single draw from a population, its spread is a property of
> *(partition, tasks)*, and the part of it a designer can compute in advance is the
> **precision-weighted projected deficit** — `projection_pressure`, which is also the quantity the
> anchoring predictor already ranks by. The subspace-overlap intuition is not where the spread lives.

## 4. Two things this does *not* say, both of them measured here

**The co-movement and the spread are different facets, and they are almost uncorrelated.** The
per-partition co-movement does **not** rank the measured draw spreads: Spearman is **+0.067**. What
predicts the *spread* is the magnitude of the pressure's own variation across draws (`e80`, +0.767), not
how tightly it tracks the excess. So the two results are complementary and neither implies the other:
`e81` says pressure *explains* the excess's variation, `e80` says pressure's own variation *calibrates*
it. A future predictor needs the second; the *explanation* needs the first.

**`side` is the weakest partition, at +0.681 (*r*² 0.464).** It is the 4-group partition with the
highest concentration, and it is the one where the alignment's co-movement was *negative* — so pressure
does the work even there, at visibly reduced strength. That is consistent with the concentration
non-monotonicity `e67` found, and it is the partition the project's C1 claims lean on most, so the honest
form of the mechanism is "83% on average, 46% for the one partition whose σ the paper leans on".

**Nothing in the paper's numbers moves.** Every σ that folds the draw component in takes it from a
per-rung **measurement** (`e14`, `e17`, `e17b`, `e67`, `e74`) rather than a prediction, so five candidate
predictors — four failures and this one — have cost the paper nothing. What changes is that the draw sd
is now *explained* rather than merely tabulated, and the explanatory sentence in §4.3 can be replaced.

## 5. Limits

- **Nine partitions, eighteen seed-centred points each, and the six draws are shared across seeds**, so
  the effective degrees of freedom are nearer four or five than sixteen and the intervals are wider than
  their nominal width. The *paired* comparison is much better protected than either run alone, because
  both quantities were measured on the same points.
- **Three task seeds, one circuit size (d = 1307), six relabellings.** Nothing here says the mechanism
  transfers to another circuit size or another task family, and `e72`'s lesson is that a quantity that
  looks general can turn out to be a restatement of one of its inputs.
- **`projection_pressure` is not free.** It runs the exact filter — about 4 s per (partition, seed)
  against 11 s for an `analytic_excess` call, so predicting a control's draw spread from it is a ~3×
  saving rather than a 100× one. What it *does* remove is the need for a matched-random control to be
  drawn and scored at all: the prediction needs the partition and the tasks, nothing else.
- **The functional is one choice.** `projection_pressure` sums `||J^{1/2} disc J^{1/2}||² / ||J^{1/2} P_pred
  J^{1/2}||²` over tasks; a different weighting or a per-task maximum could behave differently. Four
  failed functionals and one working one is a statement about the five tried.
