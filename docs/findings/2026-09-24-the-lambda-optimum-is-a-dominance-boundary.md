# The λ optimum is a dominance boundary: above it the knob loses on both axes at once

**Date:** 2026-09-24
**Script:** `experiments/e152_stability_plasticity_trade.py` — **analysis only, no runs.** It places every
constrained arm of the base family in the plane (`mean_forgetting`, the newest task's final accuracy — the
quantity `e151` showed the aggregate cannot contain) and answers with **dominance** rather than with a curve.
**Artifacts:** `runs/e141_r32_ewc_lam3e-{4,2,1}.json`, `e133`'s `ewc` (λ = 3e-3), `runs/e138_r32_ewc_anchorbias{1,33}.json`,
`runs/e125_r32_frozenbias.json`, `runs/e147_r32_frozenbias_ewc_lam3e-4.json`,
`runs/e140_r32_methods_plastic_40reps.json`'s `replay` row; reference `e133`'s `naive`.

---

## 1. The rule

An arm is **dominated** by another when the other is no worse on *both* axes and strictly better on one. **An arm
that is dominated is not a point on a trade-off — it is a worse method, full stop**, and this is the distinction a
one-axis statement like *"λ = 3e-4 is the best point measured"* cannot make. A dominance is also graded: whether
its own two pairwise contrasts resolve (≥ 2σ each), because a frontier drawn from point estimates at a resolution
the pairs do not have is the kind of claim this project keeps retracting.

Along the one-dimensional knob there is a second rule: **if one step of the knob worsens both axes, the knob has
no further use above that point** — which is stronger than *"the benefit stopped growing"*.

## 2. The plane, against `naive`

| arm | Δ forgetting | σ | Δ newest accuracy | σ | newest level | index |
|---|---|---|---|---|---|---|
| **replay** | **−0.0784** | 9.35 | **−0.0036** | **0.79** | **0.9630** | **21.50** |
| frozen + ewc λ = 3e-4 | −0.0724 | 8.61 | −0.0594 | 9.16 | 0.9073 | 1.22 |
| frozen offsets | −0.0523 | 5.90 | −0.0266 | 4.42 | 0.9401 | 1.97 |
| anchored 33.2 | −0.0458 | 4.84 | −0.0620 | 8.88 | 0.9047 | 0.74 |
| anchored 1.0 | −0.0398 | 4.63 | −0.0688 | 9.70 | 0.8979 | 0.58 |
| ewc λ = 3e-4 | −0.0354 | 4.27 | −0.0297 | 6.47 | 0.9370 | 1.19 |
| ewc λ = 3e-3 | −0.0096 | 1.21 | −0.0526 | 6.63 | 0.9141 | 0.18 |
| ewc λ = 3e-2 | **+0.0060** | 0.58 | −0.0755 | 9.45 | 0.8911 | 0.08 |
| ewc λ = 3e-1 | **+0.0096** | 0.85 | −0.0729 | 9.00 | 0.8938 | 0.13 |

`index` is `abs(Δforgetting) / abs(Δnewest)`: a **heuristic ranking with no units** (a retention difference over
an accuracy), quoted only to order arms and never against 1.

## 3. Three results

**First, `replay` is the only arm that is not dominated.** It dominates **all eight** constrained arms, and
**seven of those eight dominances are resolved on both axes** (the weakest resolved pair is `anchored 33.2` at
**5.03σ** on forgetting, and `λ = 3e-4` at **4.52σ** on the newest task); the eighth, over `frozen+ewc`, is
resolved on **one** axis only (newest 8.33σ, forgetting 1.28σ — the pair is the one arm whose forgetting the best
method does not separate itself from here). It is also the highest on the third axis, mean final accuracy (0.9609
against `naive`'s 0.9125), so **the frontier is empty of everything else on two axes and on three**: the one
method this benchmark rewards on every metric is the one that is not a constraint, and its last-task cost is
0.79σ.

**Second — and this is the result that changes a claim already in the plan — the λ optimum is where the knob
stops being free.** `e141`'s sweep concluded a *bracketed interior optimum*: forgetting falls from +0.0750 at
λ = 0 to +0.0396 at 3e-4 and rises afterwards. **The step test says the rise is not a trade.** One step up the
ladder, 3e-4 → 3e-3, worsens **both** axes and **both are resolved**: forgetting **+0.0258 (3.74σ)** and the
newest task's accuracy **−0.0229 (2.97σ)**. The next step, 3e-3 → 3e-2, again worsens both (newest **−0.0229 at
2.84σ** resolved; forgetting +0.0156 at 1.60σ not), and the last step, 3e-2 → 3e-1, is flat (0.36σ and 0.27σ), so
the cost saturates rather than continuing.

**So the licensed sentence about λ is sharper than the sweep's, and it is a different kind of sentence**:
λ = 3e-4 is not merely *the best point measured on the forgetting* (rule 38's phrasing) — it is **the largest λ at
which the knob has not yet started to charge for itself**, and every decade above it moves both metrics the wrong
way. `λ = 3e-2` and `λ = 3e-1` are dominated by **seven** of the other eight arms each, and are worse than
`naive` — which pays no stability for them — on both axes at once.

**Third, the dominance counts are a partial order and not a score.** `replay` > {`frozen`, `frozen+ewc`} >
{`anchored 33.2`, `λ = 3e-4`, `λ = 3e-3`} > … > {`λ = 3e-2`, `λ = 3e-1`}: `frozen` and `frozen+ewc` are the two
constraint arms that dominate each other's neighbours without dominating each other, i.e. **the freeze buys 0.052
of forgetting for 0.027 of newest-task accuracy and the pair buys another 0.020 for another 0.033** — a real
two-point trade, whereas the λ ladder has dominated points on it. And the exchange rate says the pair is the worse
deal of the two (index 1.22 against the freeze's 1.97), which is the "is the pair worth it" question stated as a
number rather than as a preference.

## 4. What this cannot settle

- **Dominance is a comparison of point estimates on the axes chosen.** The grades above are printed because half
  the pairs are resolved on one axis only, and three (`anchored 1.0` by `anchored 33.2`, at 0.88σ and 0.79σ) are
  **point estimates only** — those entries are frontier positions in name and not in evidence.
- **Two or three axes are not the whole of performance.** Mean final accuracy is included as a check and changes
  no dominance, but per-task accuracy, training cost and the retention matrix are all outside the plane, and the
  newest-task axis is a single task out of three.
- **The arms are not independent**: they are nested knobs on one base model (λ, anchor scale, freeze, partition),
  so the dominance counts are not `8 × 9` independent tests, and `frozen+ewc` is literally `frozen` plus a penalty.
- One read-out (32), one circuit, three tasks, forty seeds and one seed set; **`--frozen-bias` is a diagnostic and
  not a method** (`e147`'s caveat), so the two frozen arms are statements about the penalty and the benchmark.
- And the index's ordering is not a claim about welfare: it says what each arm paid per unit of stability, on this
  benchmark's scale, with the units different on the two sides.
