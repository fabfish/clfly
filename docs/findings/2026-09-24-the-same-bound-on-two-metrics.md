# The same bound on two metrics: `replay`'s own forgetting is ±0.008 on accuracy and 0.0000–0.0005 on the training loss

**Date:** 2026-09-24
**Script:** none — the loss-valued series were already recorded by the runner and read with `e123`'s
`loss_forgetting`. **Artifacts:** the four configurations of the pooled bound
(`e140` plastic, `e148`, `e140` frozen, `e155` read-out 128), forty replicates each.
**Why it is worth a finding:** yesterday's pooled bound (**−0.0007 ± 0.0038**, 2σ ±0.0076) was measured on **one**
metric and said so as its last limitation. The other metric is in the same files, and it says something different.

---

## 1. The two metrics, four configurations

| configuration | accuracy: `replay`'s own forgetting | per-seed sd | **training loss: the same quantity** | per-seed sd |
|---|---|---|---|---|
| base family, read-out 32 | −0.0034 | 0.0214 | **+0.0000** | **0.0001** |
| shared-input family | +0.0083 | 0.0230 | **+0.0005** | **0.0023** |
| base family, channel frozen | +0.0018 | 0.0200 | **+0.0000** | **0.0000** |
| base family, read-out 128 | −0.0096 | 0.0198 | **+0.0000** | **0.0000** |

**On the loss-valued metric the quantity is zero to four decimals in three configurations and 0.0005 in the
fourth, with per-seed sds of 0.0000 to 0.0023 against the accuracy metric's 0.0198–0.0230 — a factor of 10 to 200.**

**And the metric is not degenerate**: the same expression on the *baseline* arm reads **+0.1767**, **+0.0567** and
**+0.0956** in three of these configurations. So the loss metric discriminates between arms by two orders of
magnitude while resolving replay's own value to five decimals.

## 2. Why they differ, and it is the benchmark rather than the method

**The accuracy metric's per-seed sd is ≈ 0.02 for every arm in this suite**, which is the evaluation's granularity:
48 held-out examples per task, and the runner's own per-replicate check prints *"per-replicate sd 0.0149 is at or
below the test-set floor 0.0161"* for enough arms that it is a standing warning. **So the ±0.008 bound the paper
now quotes is a statement about the accuracy metric's noise, not about `replay`.**

**The training loss has no such granularity and the benchmark interpolates** — `e121` measured that the substrate
reaches its training loss floor at every read-out — so a task's training loss, once driven to its floor, has
nowhere to go, and `replay`'s value is the floor difference rather than a noisy estimate of zero.

**Which makes this an instance of the project's own "the metric decides the threshold" rule, in the one direction
it has not appeared in before.** Rule 37 exists because the loss-valued form answered a question the accuracy form
could not (`e141`'s P2: **+0.0156 ± 0.0098 = 1.60σ** on accuracy against **4.24σ** on the loss). Here it is the
same asymmetry with the *loss* form tighter by two orders of magnitude — **and the reason it is not the metric to
quote is the interpolation**: a training-split bound on an interpolating benchmark is a bound on the *fit*, not on
what the model would do on held-out data. Both numbers belong in the sentence, with their mechanisms.

## 3. What the sentence should therefore be

> `replay`'s own forgetting is **zero on the training-loss metric** (0.0000–0.0005 across four configurations) and
> **within ±0.008 on the accuracy metric** (2σ), where the second number is the test set's granularity rather than
> the method's — 48 held-out examples per task make every accuracy-valued bound in this paper ±0.008, and `e119`
> measured that enlarging the test set is what changes it.

## 4. What this cannot settle

- **The loss-valued series is the training split** (`full_split_loss(..., "train")`), so its tightness is partly
  structural: the benchmark interpolates (`e121`), and a held-out loss would carry evaluation noise and land
  between the two columns above. This is the caveat that keeps the loss number from being the headline.
- **Four configurations, one suite, one metric pair**: the two metrics' windows also differ in *form* — the
  accuracy forgetting is the diagonal form since the window holds only the diagonal (`e154`), while the loss form
  takes the minimum over all later checkpoints — so the two columns are not the same statistic in two units even
  where both are "the same" forgetting.
- **It says nothing about the other arms**: the loss metric's own resolution for the *constrained* arms (where
  the newest-task cost lives) is not computed here, and the accuracy column is the one the paper prints.
- And the pooled accuracy bound's limitation stands as written: four configurations, not independent, one base
  model.
