# E67 — the pre-registered prediction that `side`'s control-draw sd is ~1e-3 is refuted: it is 2.2e-4

**Date:** 2026-09-23
**Script:** `experiments/e12_control_spread.py --column side --min-size 1 --draws 8 --seeds 6`
**Artifact:** `runs/e67_drawsd_side_min1.json`
**Context:** `2026-09-22-draw-sd-mechanism.md` (the prediction), `2026-09-22-control-drawn-once.md`, `2026-09-22-predictor-survives-draw-correction.md`, `2026-09-22-draw-budget.md`

---

## 1. The prediction, which was written down before this run

`2026-09-22-draw-sd-mechanism.md` replaced the project's group-count model of the control's draw
spread with a one-scalar model, `concentration = sum_g s_g^2 / d^2`, and used it to predict the one
partition whose spread had never been measured:

> **`side`'s draw sd is ~1.0e-3, not 9e-5.** Its concentration (0.498) sits above the measured point
> at 0.325 (9.3e-4) and below the plateau at 0.678–0.754 (1.1e-3), so ~1.0e-3 is the interpolation;
> and the mechanism — which neurons share the large group — is fully present at 0.498.

That document also set the alternative it expected to fail: a **two-draw** smoke run of
`--column side` at d = 952 had given **9e-5**, and the prediction was that this value "is predicted
**not to replicate**; it was two draws, and the sd of two points has a standard error of order 50%".
The prediction was recorded as a prediction rather than a conclusion, and the measurement it named as
the test is this run.

## 2. The measurement

`side` at d = 1307 (cs = 800, support 80), 4 groups, constrained 0.5011, 6 task seeds, **8 independent
control draws**:

| quantity | value |
|---|---|
| biological excess | +0.003904 ± 0.000097 |
| **control sd across draws** | **0.000216** |
| within-draw seed sem (mean of 8) | 0.000293 |
| delta, biological − matched random | **−0.004553** |
| σ with a single control draw (today's protocol) | 14.68 |
| σ with the draw component included | (see §4, and note the two readings) |
| **single-draw overstatement at 6 seeds** | **1.22×** |

## 3. Refuted, by 4.8×, and in the direction that makes the retracted value the better one

| model | predicted for `side` | error |
|---|---|---|
| the concentration model, pre-registered | ~1.0e-3 | **4.8× too high** |
| the two-draw smoke value it was written to overrule | 9e-5 | 2.4× too low |
| **measured, 8 draws** | **2.16e-4** | — |

So the prediction is refuted by a factor of 4.8, and **the number it was written to reject is closer
to the truth than the number it replaced it with.** The two-draw value is still *not* reproduced — 2.4×
might be within two draws' standard error but the point is not to be trusted — yet it does not deserve
to have been overruled by a value twice as far away.

**The single-variable relation is also non-monotone at the one point where it now can be checked.**
Every measured point on `cell_type` at d = 1307, plus this one:

| partition | concentration | measured draw sd | draws |
|---|---|---|---|
| `cell_type` min 1 | 0.020 | 3.9e-5 | 2 |
| `cell_type` min 2 | 0.325 | 9.3e-4 | 5 |
| **`side`** | **0.498** | **2.16e-4** | **8** |
| `cell_type` min 32 | 0.678 | 1.06e-3 | 2 |

Between 0.325 and 0.678 the relation goes **up, then down by 4.3×, then back up** — and `side` is the
point that does it. Concentration is a better axis than group count was, but it is not the axis either.
This is a refutation of a *one-variable* model, not a demonstration that no relation exists: the
obvious missing variable is how the groups sit relative to the task subspaces, since the draw spread
comes from how much the *excess* moves when labels are reshuffled, and a balanced 4-group partition
may reshuffle onto nearly the same indicator span.

## 4. What it moves: `side`'s σ in the predictor's record, and nothing else

The predictor's draw correction (`e16`) is arithmetic over `e6_predictor_6.json`, and it used the
interpolated 1.0e-3 for `side`. That figure is recoverable from the published pair — for
`larger-circuit`/`side`, 15.53σ → 4.47σ at a seed sem of 0.00031 implies an assumed draw sd of
**1.028e-3**, which is what the log-linear interpolation between the 0.325 and 0.678 points gives.
With the *measured* 2.16e-4:

| condition / rung | σ seed-only | σ as published (interpolated sd) | **σ with the measured sd** |
|---|---|---|---|
| larger-circuit / `side` | 15.53 | 4.47 | **12.74** |
| baseline / `side` | 7.48 | 6.73 | unchanged — d = 952, unmeasured |
| wider-tasks / `side` | 18.25 | 13.36 | unchanged — d = 952, unmeasured |
| faster-drift / `side` | 7.25 | — | unchanged — d = 952, unmeasured |
| rewired-swap2 / `side` | 0.09 | — | a null either way |

**So the sentence in the paper's §5 — "`side` at d = 1307 goes from 15.53σ to 4.47σ, the largest
correction in the study" — is wrong by a factor of 2.8.** The correction is 1.22×, exactly the
"single-draw overstatement" the same artifact reports, and `side` is not the largest correction in the
study at all. The four cs = 300 conditions cannot be corrected, because `side`'s spread has not been
measured at d = 952; their published figures stand **unverified** rather than confirmed, and the model
that produced them is now known to mispredict by 4.8× at the one point where it is checkable.

**The predictor's headline is untouched.** The count is over pairs above 2σ, and `side` stays above
12σ in every condition it resolves in; the 2σ line in that analysis runs between
`baseline`/`supertype` at 1.94 and `wider-tasks`/`supertype` at 2.17, both of which are fine-column
measurements this run says nothing about. **13 of 13 stands.**

### 4.1 And the whole five-rung table can now be corrected, because four of its five draw sds are measured

`side` was the last named rung whose draw spread was unknown. With it, the five-rung table of
`e3_seeds18` can be corrected with measurements rather than an interpolation — `cell_class`,
hemilineage and `supertype` already had theirs from `e17`/`e17b`, and `cell_type`'s is still running:

| rung | σ, seed-only (18 seeds) | draw sd, measured | source | **σ with the draw component** | overstatement |
|---|---|---|---|---|---|
| `side` | 28.78 | 2.16e-4 | `e67`, 8 draws | **17.54** | **1.64×** |
| `cell_class` | 12.14 | 2.37e-4 | `e17`, 5 draws | **9.01** | 1.35× |
| `ito_lee_hemilineage` | 9.32 | 4.16e-5 | `e17b`, 5 draws | **9.25** | 1.01× |
| `supertype` | 4.26 | 8.35e-5 | `e17b`, 5 draws | **4.14** | 1.03× |
| `cell_type` | 0.74 | — | unmeasured (`e67` running) | — | — |

All four resolve after the correction — 17.5σ, 9.0σ, 9.3σ, 4.1σ — and the paper's §4.3 rule of thumb,
that a coarse partition's single-draw σ overstates the evidence 3–6×, is wrong for every one of them:
the real overstatements are **1.0–1.6×**. The rule of thumb was derived from *pooled `cell_type`*
partitions, and it is exactly `side` — the named rung with the largest uncorrected σ, and the one whose
σ the paper leans on most — that the rule over-penalises by the largest factor. Which also flips a
comparison the paper makes in the other direction: the granularity ladder's corrected rungs sit at
4–9σ, so the five-rung table's best rung at **17.5σ** is *more* decisive than every corrected ladder
rung, not less.

## 5. What it moves: the budget, in the safe direction

`2026-09-22-draw-budget.md` computed that the `side → pool4` claim needs only K ≈ 1.4 control draws per
rung to clear 3σ, and the mechanism document used the 1.0e-3 prediction to declare that budget intact.
A *smaller* draw sd makes that budget **easier**, not harder, so every conclusion resting on it
survives. What does not survive is the reason: anyone re-deriving a budget for a new circuit on the
concentration scalar would get `side` wrong by 4.8×, and in a case where the true sd were *larger* than
predicted the direction would reverse. The scalar is not yet usable for budgeting.

## 6. Limits

- **One partition, one circuit size.** d = 1307 only. The cs = 300 conditions of the predictor's table
  are not covered, and that is where three of the five published `side` corrections live.
- **Eight draws.** The sd of eight points has a relative standard error near 25%, so "2.16e-4" is
  roughly [1.6e-4, 3.3e-4]. That interval excludes the predicted 1.0e-3 comfortably and contains the
  two-draw 9e-5 at its edge — the refutation is robust to the sample size, the vindication of the
  smoke value is not.
- **The comparison points at concentration 0.325 and 0.678 rest on 5 and 2 draws** respectively. The
  non-monotonicity claim is a statement about those three numbers as measured; if the 0.678 point is
  off, the "up-down-up" shape could be "down-up". Either way, `side` at 0.498 being 4.3× below the
  partition at 0.325 is the measurement that refutes monotonicity, and it is not the 2-draw point.
- **`cell_type` at d = 1307 with 812 groups is running** in the same sweep
  (`runs/e67_drawsd_cell_type_min1.json`), which will give a second measured point from this run
  against the 2-draw 3.9e-5 currently used for the fine end of the calibration.
