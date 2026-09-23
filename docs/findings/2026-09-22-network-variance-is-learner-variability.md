# E38 — the network benchmark's variance is *learner* variability, not measurement noise, and the two claims built on the noise floor do not survive

**Date:** 2026-09-22
**Script:** `experiments/e38_variance_budget.py` (read-only over `runs/`)
**Artifacts:** `runs/e38_variance_budget.json`
**Context:** `2026-09-22-e10-side-rung-underpowered.md`, `2026-09-22-rung-question-resolved-at-lambda-0.1.md`, `2026-09-22-evaluation-noise.md`

---

## 1. The cheapest available control: the `naive` arm is bit-for-bit identical in every run

`naive` carries no penalty and no basis, so it does the same arithmetic in every rung run. It is
therefore a free cross-run determinism check, of the same kind as `e31`'s method-list check — and it
passes exactly:

```
e10_rung_side / e10_rung_cell_class / e10_rung_ito_lee / e28_side_lam0.1 / e25_cell_class_lam0.003
  naive final_accuracy = 0.8240740763 in all five
  per replicate        = [0.895833, 0.791667, 0.784722] in all five
```

Two consequences, and the second is the point of this finding.

- **The seed sequence really is shared across runs**, which is what licenses every cross-run paired
  contrast in this line. That assumption was previously asserted, and it is now demonstrable for
  free.
- **The benchmark is deterministic given the seed.** The 0.0622 per-replicate spread of the `naive`
  arm is not measurement noise and not run-to-run irreproducibility: it is three *training seeds*
  landing on three different accuracies, exactly reproduced on every run. So the plan's "settling
  C2b is a benchmark-variance problem" is right in its arithmetic and wrong in its diagnosis — the
  thing to be averaged over is **the learner's seed-to-seed variability**, which no measurement
  improvement can reduce. There is no shortcut here; more seeds means training more seeds.

## 2. The decomposition was quoted as a point, from three replicates

`e8` reports, per arm, a `replicate_sd`, an analytic `binomial_sem`, and their difference as
`residual_sd` — read in the plan as "44% of the variance, and removable". The sample sd in that
subtraction has **2 degrees of freedom**, where the 95% interval on a sd spans a factor of ~12:

| run | arm | n | replicate sd | floor | 95% CI on replicate sd | 95% CI on the training remainder |
|---|---|---|---|---|---|---|
| `ito_lee` λ=1.0 | `ewc-block` | 3 | 0.0422 | 0.0311 | [0.0220, 0.2655] | **[0, 0.2637]** |
| `e8_tuned_lambda` λ=0.003 | `ewc-block` | **9** | 0.0363 | 0.0285 | [0.0245, 0.0695] | **[0, 0.0634]** |

At n = 3 the "training" remainder is bounded only as *somewhere between nothing and 0.26*, so the
decomposition cannot distinguish a test-set-limited benchmark from a training-limited one. The n = 9
run, which already existed in this repository, narrows it by 4×. Nothing in the plan's use of the
number is *wrong*, but it is quoted with a resolution the data does not have.

**And a floor violation is unreported.** `ito_lee`'s `ewc-block-rand` has a replicate sd of 0.0250
against its own binomial floor of 0.0311, and `cell_class` λ=1.0's `ewc-block` has 0.0175 against
0.0303. The script clamps the remainder to 0 and prints "this run cannot separate them", which is
honest, but `variance_fraction` then reads 154% and 302% — a number above 100% means the
decomposition is **unresolved**, not that training contributes nothing. At n = 3 that outcome has
probability ≈ 0.48 even when the floor is exactly right, so it is not evidence of anything either
way, and it should be reported as "unresolved" rather than as a floor share.

## 3. The pairing claim has never been measurable, and the one run that can measure it says nothing

The plan states that the biological arm and its size-matched control "share a seed sequence", so the
paired sem is the right error bar (1.5× tighter at `side`, 2.3× on the neuron ladder). The
correlation that determines the pairing gain is directly computable from the stored replicates:

| run | n | Δ accuracy | corr between arms | 95% CI on corr | pairing gain |
|---|---|---|---|---|---|
| λ=1.0 `side` | 3 | −0.0116 | +0.64 | n/a | 1.52× |
| λ=1.0 `cell_class` | 3 | −0.0185 | **−0.98** | n/a | **0.83×** (pairing hurts) |
| λ=1.0 `ito_lee` | 3 | +0.0000 | −0.16 | n/a | 0.94× |
| λ=0.1 `side` | 3 | +0.0069 | +0.97 | n/a | 3.97× |
| λ=0.1 `cell_class` | 3 | −0.0648 | +0.57 | n/a | 1.20× |
| λ=0.003 `cell_class` | 3 | −0.0231 | +0.42 | n/a | 1.31× |
| **λ=0.003 `cell_class`** | **9** | **+0.0201** | **+0.02** | **[−0.65, +0.67]** | **1.01×** |

At n = 3 the correlation is estimated with a standard error near 0.7, so the spread from −0.98 to
+0.97 is what a *single* true correlation would produce; those six numbers are not evidence of
heterogeneity, and they are not evidence of pairing either. The only run with enough replicates to
say anything gives **+0.02, CI [−0.65, +0.67]** — an interval that contains every one of the n = 3
estimates and spans pairing gains from 0.83× to ~4×.

**So the paired sem is not "the right one"; it is one of two error bars, chosen by an unmeasured
correlation, and the choice moves σ by up to a factor of two in either direction.** Section 5 turns
that into the number that matters.

## 4. `--test 480` buys at most 1.28×, and the arithmetic that said otherwise was unreachable

The plan's lever is the binomial floor: 0.032 of a 0.048 per-replicate spread, "removable by asking
for a bigger test set, which costs almost nothing". The floor's contribution to the *contrast* is
bounded by `2·floor²` (independent evaluation errors) and then capped by the observed contrast
spread. Removing 90% of that capped part is the most `--test 480` can possibly buy:

| run | n | sd(Δ) | 2·floor² | binomial share (upper bound) | independence consistent? | gain bound | replicates for 0.01: now → after |
|---|---|---|---|---|---|---|---|
| λ=1.0 `side` | 3 | 0.0462 | 0.00210 | 98% | yes | 2.91× | 82 → 10 |
| λ=0.1 `side` | 3 | 0.0250 | 0.00199 | 100% | **NO** | *unreachable* | 24 → 2 |
| λ=0.1 `cell_class` | 3 | 0.0424 | 0.00242 | 100% | **NO** | *unreachable* | 69 → 7 |
| **λ=0.003 `cell_class`** | **9** | **0.0612** | **0.00162** | **43%** | **yes** | **1.28×** | **144 → 88** |

A run whose contrast spread is *below* `sqrt(2)·floor` is inconsistent with independent evaluation
errors — the arms must be sharing their errors — so the arithmetic gain bound on that row is not
achievable. Both such rows are n = 3. On the one run where the numbers are trustworthy, the
binomial share of the contrast variance is at most **43%** and `--test 480` buys **1.28×**,
taking 144 replicates to 88.

**It is still worth doing** — it is nearly free next to training and it removes the only part of the
variance that is measurement rather than learner variability — but it is not the lever the plan
called it. The lever does not exist: the remaining variance is seed-to-seed variability of the
learner, and the only way through it is more seeds.

## 5. What the effect size should be set to, since 0.01 is out of reach

Reproducible from the n = 9 per-arm sds, as a function of the correlation nobody measured:

| assumed cross-arm correlation | sd(Δ) | replicates for a 0.03 effect |
|---|---|---|
| 0.00 | 0.0617 | 16 |
| 0.25 | 0.0539 | 12 |
| 0.50 | 0.0447 | 9 |
| 0.75 | 0.0331 | 5 |
| 1.00 | 0.0137 | 1 |

> **Corrected (2026-09-23).** The four completed `e10` rung runs give **5.12 to 22.86 minutes** per
> (arm × replicate) — `ito_lee_hemilineage` 5.12, `cell_class` 7.73, `side` 11.72, **`supertype`
> 22.86** — so this sentence's "1.1–11.7" has an upper end that is `side`'s value alone and a lower
> end that matches none of them, and `supertype`, the dearest rung, is excluded, almost certainly
> because that run was still finishing. The derived range below becomes **0.9–12 hours**, not
> 0.2–6 (`docs/findings/2026-09-23-the-cost-range-excluded-the-expensive-rung.md`).

Measured cost is **5.12–22.86** minutes per (arm × replicate) depending on the rung, so **a 0.03-resolved
rung comparison costs roughly 0.2–0.6 hours at a cheap rung and 2–6 hours at a coarse one** — not
the "50–118 hours per rung" the plan quotes, which is the figure for **0.01** resolution. That
resolution is not affordable here and should not be the target. The honest target is 0.03, at which
the rung question is answerable in a single working session, with the caveat from §3 that the
replicate count needed depends on a correlation that should be measured at the same time.

## 6. What is withdrawn, and what stands

| statement | status |
|---|---|
| "the paired sem is the right one, 1.5× tighter at `side`" | **unresolved** — the correlation is +0.02 [−0.65, +0.67] on the only run that can measure it, and the n = 3 estimates span −0.98 to +0.97 |
| "the evaluation floor is 44% of the variance, removable" | **not resolvable at n = 3** — the training remainder's 95% interval is [0, 0.26]; at n = 9 it is 43% *of the contrast* and [0, 0.063] |
| "`--test 480` is the cheap lever" | **bounded at 1.28×**, on the one well-measured run |
| "50–118 hours per rung" | **true for 0.01, which is the wrong target**; 0.03 costs 0.2–6 hours per rung |
| "settling C2b is a benchmark-variance problem" | **re-diagnosed** — it is learner seed-to-seed variability (the `naive` arm is bit-identical across runs), so no measurement change reduces it |
| the runs share a seed sequence | **confirmed bit-for-bit** via the basis-independent `naive` arm |

## 7. Limits

- The n = 9 run is `cell_class`, λ = 0.003, `fisher_batches` 32 — the *cheapest* rung and a
  different λ from the rung sweep. Its variance structure need not transfer to `side`, and the
  plan's own λ sweep says the λ-dependence is not even monotone.
- Section 5's replicate counts assume the two-arm contrast; adding a third arm costs the same as
  either.
- The per-(arm × replicate) costs differ by 10× across rungs, and `e8_tuned_lambda`'s stored
  `timing_s` gives 1.1 min against `e25`'s 3.0 min for a nearly identical configuration, so the
  upper end of the cost range should be treated as the reliable one.
- §4's "independence consistent" test is a one-sided inequality on a single observed spread; it can
  exclude independence, never confirm it.
