# The arm ladder over the corpus: the ordering `e264` read does not reproduce, and "the same configuration" is not the same experiment

*2026-09-28 18:35. Runs: **none new** — `experiments/e265_the_arm_ladder_over_the_corpus.py` scans every artifact
carrying the three pairs of the line's contrast (35 of them), writing `runs/e265_the_arm_ladder_over_the_corpus.json`.
Seconds.*

## 1. The item: a reading that rest on one artifact

`e264` asked the corpus's third arm what the shared component is and answered: at the largest budget the two arms that
differ only in their basis correlate about 2.3× as much as either does with the naive arm, so what the pairing
exploits is the penalty's machinery rather than the task. That reading rests on **one artifact** (`e178`, cs 300 with
144 replicates). Its own text scopes the claim to "the largest budget of each metric", but the *interpretation* — the
penalty, not the task — travelled as a property of the corpus.

**Thirty-five artifacts carry all three pairs**, and the census says two things the single artifact could not.

## 2. W1: the device has a precondition, and one configuration fails it

`e263`/`e264` measure a pair's correlation against the most a perfectly shared test set could give it, which is a
bound only where an arm's test-set floor sits **below** its own replicate spread. `e140_r32_methods_frozenbias_40reps`
violates that for **every** arm at once:

| arm | variance fraction (test-set floor against the arm's own spread), frozen bias | its plastic twin |
|---|---|---|
| `naive` | **2.09** | 0.45 |
| `ewc` | **1.11** | 0.60 |
| `ewc-block` | **1.29** | 0.53 |
| `ewc-block-rand` | **1.10** | 0.36 |
| `replay` | **1.31** | 1.26 |

All five fractions are above 1, which is the case `e8`'s own print calls a signal: the 40 replicates of that
configuration are so alike that the 144-item test set's binomial noise **exceeds their whole spread**, so no ceiling
can be formed for any pair and the run cannot separate the test set from the training at all. Its plastic twin at the
same cell, arms and replicate count has four of five below 1. So freezing the bias collapses the run-to-run spread to
below the test set's own noise, and every conclusion of the ceiling device silently does not apply there.

## 3. W2: the ordering is a coin flip over the corpus

Of the **70** (artifact, metric) matrices, **50** are readable by W1's precondition. Ranked by which of the three
C2b pairs is most correlated:

| the pair the contrast is about (`ewc-block` against `ewc-block-rand`) | count of the 50 |
|---|---|
| highest of the three | **21** (42%) |
| middle | 14 |
| lowest | 15 |

A third is the chance baseline, so the basis pair leads in a **42%** event: the ordering `e264` read at cs 300 with
144 replicates is a property of that configuration and not of the corpus. The corpus's three 40-replicate cs-800
matrices put the same pair **lowest** on both metrics.

## 4. W3 and W4: and the corpus's own replications do not settle it either

Four configurations were run more than once, which gives a within-configuration check rather than a
between-configuration one. The `fb8` group — **five artifacts sharing every configuration field** — gives the basis
pair ranks 1, 0, 1, 0, 0: one configuration, no single ordering.

And the reason is not noise. In that group **only two runs are bit-identical** (`e102_rate_fb8_rerun` against
`e102_rate_fb8_rerun2`) while the other three each carry different replicate lists, with runtimes spanning **963 s to
3487 s** — a factor of 3.6 — and **no artifact records the thread count** that three of the filenames name
(`omp1`, `omp4`). Two runs of "the same configuration" are therefore different experiments, and the only evidence is
that their numbers differ and their clocks do. The corpus's one *complete* reproduction, `e153` against `e159`, holds
the thread count fixed and is bit-identical down to the digit — which is what makes the other three readable as an
unrecorded setting rather than as noise.

## 5. The registered claims (W1-W4, all MET)

| claim | measured |
|---|---|
| **W1** | all five arms of the frozen-bias run over their floor (1.10 to 2.09); its plastic twin four of five below (0.36 to 0.60) |
| **W2** | the basis pair highest in 21 of 50 readable matrices, middle in 14, lowest in 15 |
| **W3** | the `fb8` group's five repeats give ranks 1, 0, 1, 0, 0 |
| **W4** | one bit-identical pair out of ten in that group; runtimes 963 s to 3487 s; the thread count unrecorded |

## 6. What this does to `e264`

**It demotes the interpretation without touching the measurement.** `e264`'s T1 (the EWC pair alone clears its ceiling
on accuracy in two of three runs) and its T2/T3 numbers at cs 300 are as read — but they are a statement about that
configuration, and the corpus's other matrices disagree with their ordering. The honest form of "the shared component
belongs to the penalty and not to the task" is **"at cs 300 with 144 replicates it does, and the corpus's cs-800
40-replicate matrices put the same pair last of three"**. A reader who wants the general statement needs a
configuration the corpus has not run at matched settings more than once — which is exactly what W4 says is missing,
since the four configurations that were repeated were repeated with an unrecorded setting changed.

## 7. What it cannot do

The census is over artifacts carrying the three pairs, so a configuration that never ran all three arms is invisible
to W2, and the five arms are unevenly represented (only 22 of the 35 artifacts carry the plain `ewc` arm, so the
penalty form cannot be separated from the basis by arm counts alone). A pair's rank is a coarse statistic and the
module reports it rather than a distribution of correlations. W4 identifies the *effect* of an unrecorded setting and
not the setting: the thread counts are inferred from filenames and from the runtimes, which is what the artifacts
offer. And an arm that does not move at all makes its whole matrix unreadable, which the scan now reports rather than
dividing by zero.

**One defect the gates caught, for the third fire running.** This module's first version read each run's clock with
`d.get("timing_s")` — the spelling the trained runners write and not the quantity — and `e205` fired on it, as it did
on `e261` and on `e262`. The clock enters nothing but the table W4 prints, so no number here changes; the module now
goes through `clfly.bench.artifacts.duration_seconds`, which reads all three spellings. Three fires, three modules,
the same mistake, by a reader who has now read `e205`'s finding three times: the gate is the only thing that has
caught it, and it catches it every time.
