# `e119`: the metric's removable noise is 94% removed by a tenfold test set, and the rest is the substrate's

**Date:** 2026-09-24
**Script:** `experiments/e8_rate_network.py`, two runs; artifacts `runs/e119_r{128,300}_test480.json` (40
replicates, `--test 480` against the 48 of every run so far).
**Artifacts:** the two above, plus `runs/e116_r128_40reps.json` and `runs/e115_r300_40reps.json`.
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, `--repeats 40`, read-out 128 and 300.
**Pre-registration:** `docs/findings/2026-09-24-enlarging-the-test-set-preregistered.md`, committed before the
runs.
**Context:** `docs/findings/2026-09-24-the-metric-is-thirty-times-noisier.md`, which measured the forgetting to
74–134% of its own value while the drift is measured to 2.6–3.5%, and named **a metric with a better SNR** as one
of two routes out.

---

## 1. The result: the fall is real, at both read-outs, and just below the predicted band

| run | mean | sem | **per-repeat sd** |
|---|---|---|---|
| read-out 128, test 48 | +0.0370 | 0.0051 | **0.0325** |
| read-out 128, **test 480** | +0.0402 | 0.0035 | **0.0221** |
| read-out 300, test 48 | +0.0232 | 0.0040 | **0.0252** |
| read-out 300, **test 480** | +0.0269 | 0.0030 | **0.0188** |

**P1 fails at both**: the sd falls by **1.47×** (128) and **1.34×** (300), against a pre-registered band of
1.5–3.2 and a predicted 2.1. The failure is marginal and it is the informative kind, because the *reason* is a
property of the metric that the runner's own reporting had been overstating — §2.

**P3 holds**: the plateau-to-128 step at the larger test set is **+0.0133 at 2.90σ**, against 2.12σ before. The
axis's one resolved step survives a better metric and sharpens.

**P2 holds at 128 and marginally fails at 300**: the mean moved +0.0032 at 128 (within the new sem of 0.0035) and
+0.0037 at 300 (1.23 of its new sem). Both moves are upward and small, and neither is what a test-set change is
supposed to do — a larger test set changes the noise, not the physics. The honest reading is that the two moves
are **not** resolvable at this precision, which is the same statement as before: this metric cannot separate a
0.003 movement from zero even at 40 replicates.

## 2. The correction: the removable share of the *forgetting* is not the accuracy's

`evaluation_noise` is computed on the arm's **accuracy** — that is what its docstring says, and it is right about
the accuracy — but the two runs let the **forgetting's** own split be solved for, because the binomial component
must fall by exactly √10 = 3.16 while the training-trajectory part does not move:

| read-out | **evaluation** component | **training** component | ceiling if evaluation were removed entirely |
|---|---|---|---|
| **128** | 0.0251 — **60% of the variance** | 0.0207 — 40% | sd 0.0207, a **1.57× gain** |
| **300** | 0.0178 — **49%** | 0.0179 — 51% | sd 0.0179, a **1.41× gain** |

**At read-out 128 the accuracy's removable share is 85% and the forgetting's is 60%** — the same block, read for
a different quantity. **The reason is structural and worth stating**: the forgetting is a *difference of two
accuracies evaluated on the same test set*, and a test item that is hard is hard in both, so the test-set errors
are **positively correlated** and **partly cancel in the difference**. The binomial arithmetic that governs a
single accuracy therefore overstates what a bigger test set can do for a difference of them. **This is a
correction to how that block should be read outside the arm it describes**, and it is measured rather than
argued: 85% predicted a 2.6× fall and the fall was 1.47×.

## 3. And the test-set route is essentially exhausted

**The tenfold test set captured 94% of the available gain at read-out 128 (1.47 of a possible 1.57) and 95% at
300 (1.34 of 1.41).** There is almost nothing left on that route: an *infinite* test set would buy 1.57×, and the
metric's remaining spread — **0.0207 and 0.0179** — is the substrate's own run-to-run variation, which is exactly
what §4.7 names as the binding limit. **So the route "improve the metric" is real, sufficient to be worth
taking, and insufficient to solve the problem**, and the reason is no longer a sentence: it is 40% and 51% of the
variance.

**The handicap narrows from thirtyfold to eighteenfold.** At the larger test set the forgetting's per-repeat sd is
**55%** of its own value at read-out 128 (was 88%) and **70%** at 300 (was 109%), against the drift's **3%** — so
the comparison that five fires of mechanism search could not make is now being made at 18–23× rather than 30×.
**A factor of two of headroom was available and has been taken; the rest is not noise.**

## 4. What that points at, and it is a hypothesis about the substrate

**If the residual is the training trajectory's, then it is a statement about the optimisation rather than about
the measurement.** Five hundred iterations of SGD from a connectome-masked initialisation land in materially
different places for different seeds, and **the test is whether converging further reduces that spread** — more
iterations, or a step size that reaches the same neighbourhood, would collapse the residual if it is
under-convergence rather than a genuinely multi-modal landscape. **That is a cheap and falsifiable next step**
(4× the iterations at 40 replicates, ≈1 hour) and it is the first one this sequence has proposed that aims at
the *substrate* rather than at the axis, the metric or the statistic.

**And it is a different kind of claim from everything before it**: the previous fires asked what orders the
forgetting, and this asks **why two runs of one configuration disagree at all** — a question whose answer is
worth having independently of whether the axis ever resolves.

## 5. What this cannot settle

- **The decomposition assumes the evaluation component scales exactly as √10**, which holds for a binomial
  count and is approximate here because the two accuracies in the difference are correlated; §2's 60/40 split is
  therefore an estimate from two runs, not a measurement of two components.
- **Two read-outs.** Both show the same pattern (49–60% removable, 94–95% of it captured), which is consistent
  but not a law.
- **It does not touch the mechanism question.** Every mechanical quantity measured remains monotone in the
  read-out while both reported metrics are a plateau, and this fire narrows the handicap without changing that.
