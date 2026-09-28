# The pairing is not uniformly a gain: a median 1.18× on the sem, negative in a seventh of the rows

*2026-09-28 20:50. Runs: **none new** — `experiments/e271_the_pairing_is_not_uniformly_a_gain.py` censuses the
`matched_pair` block the runner writes into every artifact that ran both EWC arms, writing
`runs/e271_the_pairing_is_not_uniformly_a_gain.json`. Seconds.*

## 1. The item: a number the line relies on everywhere and never censused

The network line quotes its central contrast **paired**. `paired_contrast` returns `sem_paired` beside the unpaired
figure on the strength of the arm-to-arm correlation of the replicates, and three fires went into what that
correlation means on three artifacts (`e263`, `e264`, `e265`). **Nobody has censused it**, and every artifact that ran
both EWC arms carries the number in its own block — `corr`, both sems and their ratio — so the census is a read of the
register rather than a new measurement.

## 2. What the census says

**32 artifacts** carry the block, giving **64** (artifact, metric) rows.

| replicate count | rows | median correlation | most negative | negative rows |
|---|---|---|---|---|
| 3 | 12 | +0.419 | −0.500 | 2 |
| 5 | 28 | +0.302 | −0.233 | 5 |
| 16 | 6 | +0.473 | +0.321 | 0 |
| 40 | 16 | +0.194 | −0.063 | 2 |
| 144 | 2 | +0.317 | +0.282 | 0 |

**W1 MET — the correlation is positive on the median (+0.302) and negative in 9 of the 64 rows.** But the rows are not
nine independent findings: they come from **6 distinct configurations**, one of which supplies **two** rows, and the
`fb8` family appears twice among them with the same −0.210. So the honest rate is a rate over *rows*, and the census
states the row-to-configuration ratio beside it.

**W2 MET — at the budgets the register reads, the gain is bounded.** Over the **24** rows at sixteen replicates or
more, the unpaired-over-paired sem ratio runs **0.970 to 1.645** with a **median of 1.180**. So the pairing never buys
more than 65% and never — until W3 — costs more.

**W3 MET — and an unpaired report is not uniformly conservative.** In **2 of the 24** powered rows the paired sem is
*wider* than the unpaired one: `e193_r32_overlap075_methods_40reps` at **0.970** on accuracy and **0.978** on
forgetting, i.e. the arms are anti-correlated across replicates there and quoting the paired figure makes the contrast
look 2 to 3% tighter than it is. The direction is the one nobody checks, because the line's habit is to read `corr` as
a reason to trust the paired number rather than as a sign to test.

## 3. What follows

**The practice is right on the median and wrong in a twelfth of the powered record.** 1.18× is a real gain — the
unpaired figure would be 18% looser — but it is not a property of the design, it is a property of each contrast, and
the corpus contains configurations where it reverses. The actionable form is cheap: the block already carries `corr`,
so a reader can look at its sign before quoting the paired sem, and the two rows where it is negative are the two
where the honest figure is the unpaired one.

## 4. What it cannot do

The census reads the block the runner computes, so an artifact that ran a single arm, or that predates
`paired_contrast`, is invisible rather than neutral — 32 artifacts of the corpus's 140 with an `evaluation_noise`
block carry it. The ratio is a ratio of sems and says nothing about whether either figure is right for the question.
`corr` is computed from the same replicates as the contrast, so a seed that moves both arms is counted once as
agreement, and nothing here separates shared seeds from shared evaluation noise — that is `e263`'s question and this
unit only sizes its consequences. The negative rows are **named and not explained**: the cause of an anti-correlated
arm pair is a question for a run, and `e193_r32_overlap075` at forty replicates is the one to run it on. And the rate
is over rows, so a configuration written twice counts twice, which is why the count of distinct configurations is
reported with it.
