# The abstract's realization-based range `+45–63%` matches no run in `runs/`

**Date:** 2026-09-23
**Method:** an exhaustive scan of every `gap_of_means` and `gap_mean` value under topology `real` in
`runs/*.json`, plus a read of the four runs that measure the same contrast.
**Artifacts:** `runs/e3_analytic.json`, `runs/e2_analytic.json`, `runs/e21_e2_paired.json`,
`runs/e48_cs800_perseed.json`, `runs/e26_size700.json`, `runs/e3_seeds18.json`, `runs/e3_large.json`.
**Context:** this is rule 22's check applied to a number that had never been traced — *ask where the number
should come from and go there*.

---

## 1. The claim, and why it is worth tracing

The paper's first contribution states the substrate effect as the analytic excess **+33–34%** against
LGCL's <1%, and then, in parentheses, notes that *"an earlier realization-based estimate of the same
contrast gave `+45–63%`, and the two were once mixed into a single `33–63%` range in a projection audit,
which is corrected here"*. The same sentence appears again in §4.1, and the range also stands in the plan's
C1 status line and in three daily findings.

So `+45–63%` is load-bearing twice over: it is the stated reason the *earlier* number was not used, and the
contrast between it and `+33–34%` is what justifies the analytic estimator everywhere else in the paper.
A range that no artifact supports would make that justification circular, so the check is not cosmetic.

## 2. Every value of the contrast that exists on disk

`gap_of_means` is `excess_mean / oracle_mean` — the excess as a fraction of the oracle's own error, which is
the quantity the paper quotes. The `diagonal(EWC)` basis is the contrast in question. Across every
artifact in `runs/`, on the `real` wiring:

| run | circuit-size | d | seeds | estimator | `gap_of_means` | per-seed sd of the ratio |
|---|---|---|---|---|---|---|
| `e21_e2_paired.json` | 300 | 952 | 3 | realized | **0.6570** | 0.2584 |
| `e21_e2_paired.json` | 300 | 952 | 3 | analytic | 0.3021 | 0.0300 * |
| `e2_analytic.json` | 800 | 1307 | 3 | realized | **0.6009** | 0.7597 |
| `e2_analytic.json` | 800 | 1307 | 3 | analytic | 0.3523 | 0.0383 * |
| `e3_analytic.json` | 800 | 1307 | 5 | realized | **0.3580** | 0.3013 |
| `e3_analytic.json` | 800 | 1307 | 5 | analytic | 0.3346 | 0.0374 * |
| `e48_cs800_perseed.json` | 800 | 1307 | 6 | analytic | 0.3665 | — |
| `e3_seeds18.json` | 800 | 1307 | 18 | analytic | 0.3392 | — |
| `e26_size700.json` | 700 | 1229 | 6 | analytic | 0.3687 | — |
| `e3_large.json` | 3000 | 3150 | 2 | analytic | 0.3382 | — |

\* the analytic rows carry `excess_sd` in absolute error units, not a per-seed ratio sd; the column is
`excess_sd / oracle_mean`, so it is a derived approximation and is marked as one. The realized rows carry
`gap_sd`, which *is* the sd of the per-seed ratios, and it is the field that matters below.

**There is nothing between 0.3687 and 0.6009.** Every `real`-topology entry in `runs/` was scanned — 143
values at or above 0.20 — and no `gap_of_means` for any basis or any circuit size falls in that interval.
So the claimed low endpoint, **45%**, is not in the record at all, and the claimed high endpoint, **63%**,
is not a `gap_of_means` either: 0.6338 is `gap_mean` — the **mean of the per-seed ratios**, a different
statistic — for the *same* cell whose `gap_of_means` is 0.6009. `e2_topology.json` carries both fields side
by side, so the two are one key apart.

**The range is therefore a hybrid of two statistics, and its low end has no artifact behind it.** That is
the third instance of this exact failure in this project's audit record, after the abstract's `+33–63%`
(joining a measured 33% to a realization-based 63%) and §6's "1.38 standard deviation" (a *range* paired
with another run's mean).

## 3. What the realization-based estimate actually is, and why the paper's choice is right

The two runs of the *same configuration* at cs = 800 differ only in the seed count, and they do not agree:

| seeds | realized `gap_of_means` | `gap_sd` | sem | one-sem interval |
|---|---|---|---|---|
| 3 | +60.1% | 0.7597 | ±43.9% | **+16% to +104%** |
| 5 | +35.8% | 0.3013 | ±13.5% | **+22% to +49%** |

The per-seed sd of the realized estimator is **comparable to its own mean** at three seeds — 0.76 against
0.60 — and the estimate moves by a factor of **1.68** when two seeds are added. The two runs are of course
mutually consistent once their error bars are admitted, which is the point: the quantity is not a value, it
is a draw from a distribution whose spread is as large as its location. (At the *other* circuit size,
cs = 300 with three seeds, the realized estimate is +65.7% with `gap_sd` 0.2584, so it is not the small
circuit that is stable either.)

**Quoting a range for it therefore implies a precision that does not exist**, and the honest statement is
not "+45–63%" but "+36% ± 13% at five seeds, +60% ± 44% at three, and not stable in the seed count". That
is a *stronger* justification for the analytic estimator than the sentence it replaces, because it names
the mechanism rather than asserting a discrepancy.

**For the record, the analytic estimate at d = 1307 is also not a single value** — four runs at 3, 5, 6 and
18 seeds give 0.3523, 0.3346, 0.3665 and 0.3392, a 10% relative spread — but every one of them lies inside
the three-seed realized estimate's own error bar, and their whole spread (0.032) is about a **tenth** of the
realized one's (0.299). The paper's `+33%` is `e3_analytic.json`'s five-seed value, and it should be read
as *the middle of 0.335–0.367* rather than as the measurement.

## 4. Corrections applied

- `docs/paper/clfly-v1.md`, contribution 1 and §4.1: the parenthetical now states the artifact-backed
  values, the per-seed sd that makes the estimator unusable, and that the old range mixed two statistics.
- `docs/research_plan.md`, C1's status line: the `+45–63%` is replaced by the traceable comparison.
- The three daily findings that carry the old number (`2026-09-22-e3-basis-selection.md`'s **+45.5%**,
  `2026-09-22-e2-topology-contrast.md`, `2026-09-22-e5-anisotropy-axis.md`) get a one-line correction
  pointer rather than a rewrite, because they are dated records of what was believed then and the
  project's convention is to leave the record readable.

**And the `+45.5%` in the e3 finding is itself untraceable, which is a separate and worse problem.** That
finding says "the oracle's own final error is 0.0513; the diagonal-anchored filter's is 0.0747", i.e.
0.0747 / 0.0513 − 1 = **+45.6%**. The artifact it names, `runs/e3_analytic.json`, records oracle 0.05196 and
`ewc_mean` 0.06934 for the analytic estimator (+33.5%) and 0.05278 / 0.07167 for the realized one (+35.8%).
**Neither pair is the pair in the finding**, so either the finding was written from an earlier run of `e3`
whose artifact was overwritten, or from the rung table's other column. It cannot be reproduced now, and the
number that the paper inherited from it was already drifting before it became a range.
