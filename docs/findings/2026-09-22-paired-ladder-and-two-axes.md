# E24 — the paired ladder resolves every step on the seed axis, the draw axis kills all but one, and nothing is infeasible

**Date:** 2026-09-22
**Script:** `experiments/e3_basis_selection.py --ladder --seeds 12` (v2, per-seed storage)
**Artifacts:** `runs/e3_ladder_v2.json` vs `runs/e3_ladder.json`

---

## 1. Determinism, first

Two independent 12-seed runs of the same configuration, all 18 bases:

**largest absolute difference: 0.000e+00.** The published headline numbers reproduce bit-for-bit,
which is the check the first run could not provide and the reason this run was made.

## 2. The paired seed axis resolves *every* adjacent step

`e3_ladder_v2.json` stores per-seed excesses, so the adjacent-rung contrasts can be computed the
way the design implies — paired, since every basis sees the same task geometries in the same seed
order:

| contrast | Δ of deltas | σ unpaired | **σ paired** |
|---|---|---|---|
| `pool1 − pool2` | +0.00820 | 13.6 | **23.7** |
| `pool2 − pool4` | +0.00084 | 2.2 | **3.6** |
| `pool4 − pool8` | −0.00199 | 6.4 | **10.9** |
| `pool8 − pool16` | +0.00080 | 2.7 | **4.5** |
| `pool16 − pool32` | −0.00067 | 2.5 | **4.8** |
| `pool32 − pool64` | −0.00150 | 4.7 | **6.8** |
| `pool64 − pool128` | −0.00139 | 4.0 | **7.3** |

**Every step clears 3.6σ.** On the evidence this table contains, the curve is *not* a flat
plateau — it has resolved structure and its largest steps alternate in sign.

Note what did **not** matter. The rung-level σ barely move under pairing (correlations between a
rung's biological and random arms are −0.17 to +0.23, so those two are nearly independent across
seeds), yet the *contrasts of deltas* gain 1.6–1.8×. Both are correct: the biological-vs-random
comparison is nearly unpaired, while two rungs' deltas are strongly correlated across seeds because
the task draw drives both. **It is the contrast, not the rung, that pairing helps.**

## 3. But the draw axis is not in that variance, and it dominates

A fixed control draw is a **per-rung offset**: it moves a delta's mean and contributes nothing to
its across-seed variance. So the paired sem above is *purely* the seed axis, and the draw axis — two
independent draws for a contrast — has to be added separately. Using the measured draw sds where
they exist (`pool1` 3.9e-5, `pool2` 9.29e-4, `pool4` 6.13e-4) and the budget constant 1.1e-3
elsewhere:

| contrast | Δ | paired sem (seed) | draw sd (independent) | σ seed | **σ combined** | **K for 3σ** |
|---|---|---|---|---|---|---|
| `pool1 → pool2` | +0.00820 | 3.45e-4 | 9.30e-4 | 23.7 | **8.27** | ≤1 |
| **`pool2 → pool4`** | +0.00084 | 2.31e-4 | 1.11e-3 | 3.6 | **0.74** | **51** |
| `pool4 → pool8` | −0.00199 | 1.83e-4 | 1.26e-3 | 10.9 | **1.57** | **4** |
| `pool8 → pool16` | +0.00080 | 1.79e-4 | 1.56e-3 | 4.5 | 0.51 | 62 |
| `pool16 → pool32` | −0.00067 | 1.40e-4 | 1.56e-3 | 4.8 | 0.43 | 82 |
| `pool32 → pool64` | −0.00150 | 2.20e-4 | 1.56e-3 | 6.8 | 0.96 | 12 |
| `pool64 → pool128` | −0.00139 | 1.90e-4 | 1.56e-3 | 7.3 | 0.89 | 14 |

**Combined, only one step resolves** (`pool1 → pool2` at 8.3σ). The draw sd is 3–8× the paired sem
for every internal step, so it is the draw axis, not the seed axis, that makes the curve's interior
unreadable. **The plateau conclusion therefore stands — but on different grounds than it was
originally stated**, and §4 says what those grounds change.

## 4. Two corrections this forces

**(a) Nothing is infeasible.** The draw-budget finding declared `pool4 → pool2` **infeasible at any
``K``** because its *floor* — the best achievable if the draw noise vanished — was 2.2σ. That floor
was computed with the **unpaired** seed sem. With the paired sem it is **3.6σ**, so the claim is
feasible: it needs **K ≈ 51** control draws. The same applies to every other row: the paired floors
are 3.6–23.7σ, all above 3.

So the earlier picture — "the curve's fine structure is not a resolvable claim at all" — was wrong in
its reason. **Everything is resolvable in principle; the shape question is a matter of budget**, and
the budget for the headline contrast is 51 draws per rung.

**(b) The cheapest entry point is K = 4.** `pool4 → pool8` needs only four draws per rung, and it is
one of the two contrasts that decide peak-versus-plateau (the other being `pool2 → pool4` at 51).
So **the question "does the curve rise again on the coarse side of `pool4`?" costs about
``3 rungs × 5 bases × 12 seeds × 37 s ≈ 2 h``** — while the fine-side half of the same question costs
K = 51, about 19 h over three rungs. The cheap half of the peak question has never been run.

## 5. Where the three successive readings of this curve now stand

| reading | basis | verdict |
|---|---|---|
| "a peak at ~0.54 constrained" (original) | unpaired seed σ, no draw term | right conclusion, wrong arithmetic — see below |
| "a flat-topped plateau over 0.32–0.67" (`f2d7486`) | unpaired seed σ, no draw term | right conclusion, but for the wrong reason |
| **seed-paired and draw-combined (here)** | paired σ *and* the draw axis | **the plateau conclusion survives; the peak is not established at a combined 0.74σ** |

The original peak claim and the plateau correction differ only in which error bar they used, and
neither included the draw axis. With it included, the interior steps are 0.4–1.6σ and the region is
**a plateau in the sense that no internal step is resolved** — which is what the project says, now
for a reason that will survive the next audit.

Two things do change. The *easiest* internal step (`pool4 → pool8`, K = 4) is cheap enough to
actually buy, and buying it would be the first direct test of whether the plateau has structure. And
the *statement* of the shape needs the two axes named separately, because a reader who sees
"3.6σ paired" for `pool2 → pool4` and a separate statement that the shape is unresolved will
reasonably ask which is right: both are, on different axes.

## 6. Limits

- The paired sem is estimated from 12 differences, so it carries ~21% relative error; the
  combined σ inherits that.
- The draw sds for `pool8`, `pool16`, `pool32`, `pool64` and `pool128` are the budget **constant**,
  not measurements. Every one of them is a coarse partition, and the constant is the top of the
  observed coarse range, so the combined σ are conservative — the required ``K`` are upper bounds.
- `pool32` and `pool64` are the **same partition**, so their contrast is a pure noise probe; it
  appears here as `K = 12` and is not a claim.
- All of this is still one circuit, one connectome, d = 1307, support 80.

## 7. What to run

1. **`e12_control_spread --column <pool4, pool8 configs>`** measures the two draw sds that the
   cheapest contrast needs, replacing constants with measurements.
2. **A K = 4 ladder over `pool2`, `pool4`, `pool8`** (~2 h) settles whether the plateau's coarse side
   has structure — the first internal step this project can afford.
3. **Investigate the `swap2` non-replication before any of this** (`2026-09-22-c1-refutation-does-
   not-replicate.md`), which is now a larger question than the curve's shape.
