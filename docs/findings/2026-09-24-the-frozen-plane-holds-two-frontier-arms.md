# The third plane: with the channel removed from every arm, the frontier holds two arms and the diagonal is one of them

**Date:** 2026-09-24
**Script:** `experiments/e152_stability_plasticity_trade.py`, **third plane added** — analysis only.
**Artifact:** `runs/e140_r32_methods_frozenbias_40reps.json`, the five-method table with `--frozen-bias` in every
arm, which landed after this script was written; its own `naive` is the reference, and it is per-replicate
identical to `e125`'s (that arm's C0b probe, worst difference 0).
**Why it is a separate plane and not four more rows in the first one:** in the base and shared-input planes each
arm is a *different* configuration, so "dominated" compares configurations. **Here every arm was run under one
manipulation on one seed stream**, so the frontier is a statement about methods under a channel that has been
removed from all of them.

---

## 1. The plane

| arm (channel removed from every arm) | Δ forgetting | σ | Δ newest accuracy | σ | newest level | index |
|---|---|---|---|---|---|---|
| **`ewc` (diagonal)** | **−0.0247** | 5.85 | −0.0651 | **8.95** | 0.8750 | 0.38 |
| **`replay`** | −0.0208 | 5.89 | **+0.0005** | **0.15** | 0.9406 | **40.00** |
| `ewc-block` | −0.0164 | 4.47 | −0.0104 | 2.24 | 0.9297 | 1.57 |
| `ewc-block-rand` | −0.0135 | 3.26 | −0.0083 | 1.77 | 0.9318 | 1.63 |

**Frontier: two arms, `ewc` and `replay`** — and neither dominates the other, because their advantages are on
different axes: `ewc` is better on forgetting by 0.0039 (**1.04σ, unresolved**) and worse on the newest task by
0.0656 (**6.5σ, resolved**). The two `block` arms are **dominated by `replay`**, `block-rand` **resolved on both
axes** (2.04σ forgetting, 2.07σ newest) and `block` resolved on one (1.26σ, 2.09σ) — the first time in this
project that a `block` arm is dominated with **both** axes resolved.

## 2. Three things this plane says that the other two cannot

**First, it is the only configuration so far in which the diagonal penalty is not dominated.** In the base plane
`ewc` λ = 3e-4 is dominated by both `frozen offsets` and `replay`; in the shared-input plane the diagonal is
dominated by the freeze and by `replay`. **Here, with the channel the penalty cannot press removed from every arm,
the diagonal's forgetting is the best of the four** — so its position on the frontier is bought by the same
manipulation that removed its confound, which is the plane's own subject.

**Second, `replay`'s index reaches 40.0, four times its value anywhere else** (21.5 on the base plane, 21.0 on the
shared-input plane), because its plasticity cost is **+0.0005 at 0.15σ** — literally nothing — while its forgetting
gain is 5.89σ. The index is `abs(Δforgetting)/abs(Δnewest)` and remains unitless, but the ordering it produces
here is unambiguous: **on this plane every constrained method pays a resolved price and the unconstrained one
pays none.**

**Third, and it is the sharpest form of the two-axis asymmetry so far**: the arm with the *best* forgetting has the
*worst* newest-task accuracy — `ewc` at **8.95σ** below its own baseline against `block`'s 2.24σ, `block-rand`'s
1.77σ and `replay`'s 0.15σ. In the base and shared-input planes the penalty arms also paid, but there a *different*
arm was best on forgetting; here the two rankings are **opposite at the top of the same table**, which is the same
statement `e140`'s finding makes from the ordering side and this makes from the frontier side.

## 3. What this cannot settle

- **The plane's axes are two and the arms are four.** Mean accuracy, per-task accuracy, the loss-valued metric and
  the training cost are all outside it; on the mean-accuracy axis the four arms run 0.9102 (`ewc`), 0.9436
  (`replay`), 0.9345 and 0.9344 (the blocks), so adding it changes no dominance — `replay` is highest there too.
- **`ewc`'s frontier position rests on an unresolved advantage** (1.04σ on forgetting). By rule 40's grade it is a
  frontier position in name and not in evidence, and the licensed sentence is *"the diagonal's forgetting is the
  lowest of the four by a difference this design does not resolve"*.
- **`--frozen-bias` is a diagnostic, not a method**: freezing the offsets changes the model class, so the plane is
  a statement about which method's advantage survives the removal of that channel, not a recommendation.
- And the arms are **not independent**: they are one run's five rows on one seed stream, which is exactly what
  makes the frontier meaningful here and also means the four rows are not four experiments.
