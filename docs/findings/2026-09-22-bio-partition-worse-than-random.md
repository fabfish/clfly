# E27 — at the ladder's own configuration the biological synapse partition is *significantly worse* than a random one, and the published analysis called it a null

**Date:** 2026-09-22
**Script:** analysis over `runs/e8_basis.json` and `runs/e10_rung_cell_class.json` (no new compute)
**Context:** `2026-09-22-e10-lambda-not-set.md`, `2026-09-22-lambda-tuning-negative.md`, `2026-09-22-evaluation-noise.md`

---

## 1. What made this possible

The previous fire found that the rung ladder runs at λ = 1.0 while the published basis comparison
ran at λ = 0.1, and that the project's λ sweep is a *line* at Fisher batches = 32 — so the λ arm at
batches = 8, where the ladder lives, had never been measured. It turns out two of its three points
**already exist**:

| λ | batches | artifact | status |
|---|---|---|---|
| 0.1 | 8 | `e8_basis.json` | the published basis comparison |
| 1.0 | 8 | `e10_rung_cell_class.json` | the rung ladder |
| 0.003 | 8 | `e25` | running |

All three share seeds, task draws, repeats and batch count, so they are directly comparable — and
the first two can be analysed now.

## 2. The result at (λ = 0.1, batches = 8)

| metric | biological | matched random | delta | σ unpaired | **σ paired** | r |
|---|---|---|---|---|---|---|
| final accuracy | 0.7755 | 0.8403 | **−0.0648** | 2.21 | **2.65** | +0.569 |
| mean forgetting | +0.1771 | +0.0868 | **+0.0903** | 1.89 | **2.73** | +0.558 |

Per replicate, the biological arm is worse in **all three**, on both metrics:

```
accuracy   bio 0.8264 0.7708 0.7292   rand 0.8542 0.8264 0.8403
forgetting bio +0.104 +0.188 +0.240   rand +0.042 +0.135 +0.083
```

**This is not a null.** The biological synapse partition is worse than a group-size-matched random
partition of the same size, on both metrics, and the pairing on the shared seeds — r ≈ 0.56, worth
1.20× and 1.44× in sem — turns a marginal 2.2σ/1.9σ into a resolved **2.65σ/2.73σ**.

The published analysis of this exact run was **unpaired** (that is the omission found in
`2026-09-22-evaluation-noise.md` §1), so it read the same numbers as within-noise and the project's
standing conclusion became "the biological partition shows **no advantage**". The correct reading at
this setting is stronger and in the same direction: it shows a **disadvantage**.

## 3. And λ moves it, in the direction opposite to the naive expectation

| λ (batches = 8) | accuracy delta | σ paired | forgetting delta | σ paired |
|---|---|---|---|---|
| 0.1 | **−0.0648** | **2.65** | **+0.0903** | **2.73** |
| 1.0 | −0.0185 | 0.35 | +0.0243 | 0.45 |

Raising λ from 0.1 to 1.0 **shrinks the random control's advantage** and makes the comparison
indistinguishable. A stronger penalty was expected to hurt both arms; instead it flattens the
difference. That is a second place in this project where the penalty strength does not do what the
obvious story says, and it means the "no advantage" reading at λ = 1.0 is a **null at one λ**, not a
λ-robust statement.

## 4. Assembling every cell the project has measured

Across the cells where the biological-versus-random contrast has been measured with 3 or more
replicates:

| cell | replicates | biological − random (accuracy) | verdict |
|---|---|---|---|
| (0.003, 32) | 3 | +0.037 | biology better, nothing clears 1σ |
| (0.003, 32) | **9** | +0.020 ± 0.021 | **0.5σ** — the win shrank on replication |
| (0.01, 32) | 3 | −0.037 | random better |
| (0.1, 32) | 1 | −0.035 | random better |
| **(0.1, 8)** | **3** | **−0.0648, 2.65σ paired** | **resolved: random better** |
| (1.0, 8) | 3 | −0.0185, 0.35σ | indistinguishable |

**Biology shows an advantage in exactly one cell, and that cell's own replication reduced it to
0.5σ. In every other measured cell the random control matches or beats it.** The honest headline for
the network line is therefore stronger than the published one:

> not *"the biological synapse partition shows no advantage over a size-matched random one"*, but
> **it is significantly worse than one at (λ = 0.1, batches = 8), and never reliably better in any
> configuration measured.**

## 5. What this does not say

- `e25` at (0.003, 8) is still running, and it is the cell that would matter most: the λ sweep's
  only biology-favouring cell was (0.003, **32**). If (0.003, 8) also favours biology, then the
  ordering depends on **batches** at fixed λ, and the map is two-dimensional in a way that matters.
- The (0.1, 8) negative is 3 replicates, so it is a 2.65σ result from three paired observations —
  real, but a long way from settled. Its `min_detectable` is 0.049 accuracy, so an advantage smaller
  than that would not have been seen; what *is* seen is a disadvantage of 0.065.
- Nothing here touches the *rung* question (whether `side` would beat `cell_class`). It is about the
  `cell_class` rung at three λ values, which is one point on the granularity axis.

## 6. The transferable part

Three separate omissions concentrated on one comparison and all pushed it the same way:

1. the **unpaired formula** on a comparison that shares seeds — cost about half a sigma here;
2. **λ never set**, so the ladder sat 300× above the published value;
3. and until this fire, nobody had noticed that the λ arm the ladder belongs to **was never
   measured**, even though two of its three points were already on disk.

Each was invisible from inside its own artifact, and the third was invisible because the two points
lived in files with no reason to be compared — one from the basis study, one from the rung ladder.
**A run's λ is not a property of the run; it is a coordinate, and coordinates have to be plotted
before they can be read.** That is plan rule 14's lesson one level up.
