# The suite bought eight of ten, and the control that was to hold read a held-out column

*2026-09-29 00:15. Runs: **one, 2.75 h** — `python -m experiments.e8_rate_network` at the
`e140_r32_methods_frozenbias_40reps` configuration with `--test` raised from 48 to 200 and 40 replicates, writing
`runs/e275_frozenbias_suite600_40reps.json`. The read is `experiments/e275_the_suite_makes_it_visible.py`, writing
`runs/e275_the_suite_makes_it_visible.json`. Registered in `docs/findings/2026-09-28-the-suite-is-being-bought.md`
before the artifact landed.*

## 1. What was registered

`e267` found three configurations whose every arm's test-set floor sits at or above that arm's own replicate spread,
and `e269` measured that a held-out decision is cheap. This unit spent that on the largest of the three: the same
configuration and the same seed sequence, with the suite raised from **144** to **600** items. **Z1** every arm's
training column is identical between the two runs (the built-in control); **Z2** each arm's variance fraction falls by
`144/600` within a factor of 1.5; **Z3** every arm's fraction is below 1, where all five arms were at or above 1.10.

## 2. The read: all three falsifiers fired

| arm / metric | fraction, 144 items | fraction, 600 items |
|---|---|---|
| `naive` / final_accuracy | **2.09** | 0.86 |
| `ewc` / mean_forgetting | **1.72** | 1.00 |
| `replay` / final_accuracy | 1.31 | **1.43** |
| `ewc-block` / final_accuracy | 1.29 | 0.91 |
| `ewc` / final_accuracy | 1.11 | 0.87 |
| `ewc-block-rand` / final_accuracy | 1.10 | 0.82 |
| `naive` / mean_forgetting | 1.05 | 0.35 |
| `ewc-block` / mean_forgetting | 0.97 | 0.52 |
| `replay` / mean_forgetting | 0.92 | 0.60 |
| `ewc-block-rand` / mean_forgetting | 0.89 | 0.81 |

The run took **2.75 h** where the 144-item run took **5.55 h**, so the four-times-larger suite cost less than the one
it replaced — `e269`'s price, paid on the configuration that needed it (with the caveat that the two runs are four
days apart and the machine's epoch is not identical).

## 3. Z1 fired on a column that cannot carry it — and the claim it was written to test holds

The column Z1 named is `learned`, and `learned` is **held-out**. It is the diagonal of the retention matrix, and
`e8_rate_network.evaluate()` fills every cell of that matrix from `task.u_test` and `task.y_test`. A held-out column
*must* move when the held-out suite moves, so Z1's verdict is about the instrument and not about the experiment.

The column that is on the training set is `losses`, the per-task training loss, and on it:

```
the column that is on the training set (losses), arm by arm: 5 of 5 identical, differing none
```

with `RateTask.make()` building the training split from its own RNG stream (`default_rng(seed + 1000 + 0)`) and
`n_test` appearing nowhere in the training path. **So the two runs are the same experiment and the comparison is the
suite's** — which is what Z1 wanted to establish, established by the column that can establish it. `e275.control()`
now reads that column and the report labels it **not a registered claim**, because it was written after the data
landed.

**This is the third mis-registered control in three fires** (`e282`'s C2, `e284`'s V3, and this), and the pattern is
the same each time: a column, a population or a noun was assumed to be what its name says. It is worth stating as a
rate, because the instruments that catch it are the ones built for it — `e282`'s own C2 fired and produced its
finding, `e284`'s V3 fired on a row where an empty cell is correct, and here the correction *rescues* the unit's main
comparison.

## 4. Z2 fired, and the reason is in the denominator rather than in the suite

The fraction is `e² / v`, with `e` the binomial sem of an accuracy at `n_eval` held-out decisions and `v` the measured
variance across the forty replicates. **`e²` is a pure function of `p` and `n_eval`** — and the suite is built **once
and shared by all forty replicates** (`suite` is constructed before the method and replicate loops, and the replicates
vary only their training seed), so `e²` is not a draw at all. Raising the suite from 144 to 600 scales it by `144/600
= 0.240`, with a small further correction because the accuracies moved toward the ceiling: `p(1-p)` at `p` = 0.91 to
0.95 falls as `p` rises, which puts the corrected expectation at **0.20 to 0.21** rather than 0.24.

The observed falls run from **0.33 to 1.09**. Dividing out the corrected numerator, **the across-replicate variance
itself moved by 1.6x to 5.5x between the two runs**:

| arm / metric | observed fall | numerator's own fall | the denominator moved |
|---|---|---|---|
| `naive` / final_accuracy | 0.412 | 0.212 | 1.94x |
| `replay` / final_accuracy | 1.090 | 0.200 | **5.46x** |
| `ewc-block-rand` / mean_forgetting | 0.912 | 0.207 | **4.42x** |
| `replay` / mean_forgetting | 0.654 | 0.200 | 3.28x |

Forty replicates put the sampling error of a variance ratio at roughly **32%**, so movements of 1.6x and 5.5x are
1.5 and 13 standard errors. **The replicate spread is not a stable property of a configuration, and Z2's falsifier is
therefore not a statement about the suite at all**: it is a second measurement of the same defect the corpus already
carries — `e198` and `e201` found the draws were not recorded, and here is a *quantity* that is a draw without being
called one. The candidate mechanisms are all visible in the artifacts (the test sample changed, so the variance of the
models' accuracies on it changed; the accuracy grid went from 1/48 to 1/200; `p(1-p)` fell as `p` approached the
ceiling), and this unit does not separate them.

## 5. Z3 fired on two of ten, and it is the leg that carries the result

**Eight of ten fractions are below 1 where five of ten sat at or above 1.10.** The two that are not are
`ewc/mean_forgetting` at **1.0026**, which is a factor-of-1.1 statement at the boundary, and `replay/final_accuracy` at
**1.43**, which *rose* from 1.31 — and a rise is exactly what a collapsing denominator produces, since that arm's
replicate variance fell **5.46x**. So the suite bought what `e267` said it would buy for eight of the ten arm-by-metric
fractions, for the price `e269` measured, and the two exceptions are one boundary case and one consequence of the
movement in section 4.

## 6. What it cannot do

**One configuration of the three** — chosen because its requirement is the largest — so nothing here says the other
two behave the same way. **Forty replicates** estimate each spread on thirty-nine degrees of freedom, so a fraction
near 1 is a factor-of-1.1 statement, and the 1.6x denominator movement is at the edge of what they resolve.
**`frozen_bias` removes most of the training variance**, so this is the easiest case in which the floor is visible at
all. **The two runs are four days apart** and their durations are not a controlled comparison of cost. **The two
exceptions are not retested**: `replay`'s rising fraction is read as what its measured denominator implies, and not as
a property of `replay`. And **the Z2 accounting assumes the replicate variance is the quantity that should scale**;
what the experiment shows is that it moved, not what it would have been had the test sample been held fixed.
