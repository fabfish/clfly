# The collapse at two step sizes: both lose the cue in one gradient step, so the rate is not the variable

*2026-10-03. `experiments/e383_the_collapse_at_two_step_sizes.py` runs `e382`'s five budgets again at the corpus's
own learning rate, keeps the bodies, and reads them with the same probe on the same examples against the same
connectome weights -- so two rates give two series at one cell, one draw, one arm and one source. Five runs of five
replicates, the last of them 500 iterations; the reader is `runs/e383_the_collapse_at_two_step_sizes.json`. Five
claims, registered before any of the new runs' readings was opened.*

## 1. The two series

| iterations | probe at 0.003 | probe at 0.03 | head at either | connectome's own weights |
|---|---|---|---|---|
| **1** | **0.2083** | **0.2083** | 0.2083 | 0.6875 |
| 5 | 0.2083 | 0.2083 | 0.2083 | 0.6875 |
| 20 | 0.2083 | 0.2083 | 0.2083 | 0.6875 |
| 100 | 0.2083 | 0.2083 | 0.2083 | 0.6875 |
| 500 | 0.2292 | 0.2083 | 0.2083 | 0.6875 |

chance 0.2500.

| claim | measured | verdict |
|---|---|---|
| D1 one configuration across the two sweeps | `lr` alone differing at every budget, and `repeats` at the 500 point | **MET** |
| D2 the smaller step loses the cue by five hundred | **+0.4583** | **MET** |
| D3 but not in the first step | **-0.0208** | **FALSIFIER FIRED** |
| D4 it loses the rest over many steps | a total drop of **-0.0208** | **FALSIFIER FIRED** |
| D5 the larger rate costs more at the first update | **+0.0000** | **FALSIFIER FIRED** |

## 2. What fired, and what it answers

**Both step sizes lose the cue in the first gradient step.** At `0.003` the body after **one** update reads
**0.2083**, which is where it reads after five, twenty, a hundred and five hundred -- the same number, on the same
examples, as the larger rate reaches in one step. D3 asked whether the corpus's own rate keeps the cue at a budget of
one and the answer is that it does not; D4 asked whether the rest is lost over many steps and the answer is that
there is no rest to lose; D5 asked whether the larger rate takes more out in one step and the answer is that the two
are **0.0000** apart.

**So `e382`'s follow-up is answered in the negative, and its own headline generalises.** That unit found the whole
0.4792 gone after one update at `0.03` and named the obvious next question -- whether the smaller rate collapses at
the first update or drifts there over hundreds. It collapses at the first update. Ten times less movement per
coordinate, the same outcome, on the same examples: **the tight step's failure is not about how far a step moves.**

**And the rate is not the variable, which leaves the world's own scale as the candidate.** `e368`'s curve puts the
world's spread at `cue@8` at **0.0478** and at `cue@0` at **0.2780**, six times larger, and one Adam step moves a
coordinate by about `lr`. So at `0.003` a single step's perturbation is of the **same order** as the tight step's
whole signal, while at the wide step the same perturbation is a fraction of it -- which is what `e380` found from the
other side, since there the training **improves** every diagonal rather than erasing them. **That is a hypothesis
this unit does not test**, and the run that would is the same five budgets at `cue@0`, where the prediction is a
series that **rises** from the first step rather than falling to the floor.

**Reported and not claimed**: the connectome's own weights read **0.6875** in all ten rolls of both sweeps, at every
budget and both rates, which is an internal check that `theta_initial` is one body and the roll is deterministic.
And the trained head reads **0.2083** at every budget and both rates: one step cannot fit anything, so that is the
floor a constant classifier gets on that split and not learning, so the head's agreement with the probe here says
both are reading a constant.

## 3. The bug this unit's first reading had

**Its configuration claim could not see the manipulation.** `e367`'s `_facts` records the environment, the cue's step
and the budget, and **not the learning rate**, so the first reading of D1 compared each `0.003` run against its
`0.03` counterpart over a field list in which the two are **identical**, and reported an empty difference at four of
the five budgets. The claim's falsifier fired on the 500 point's replicate count -- the only thing the list could
see -- which is how the omission surfaced. The rate and the batch are now added to the compared fields and D1 reads
`['lr']` at every budget. **The lesson is the same shape as `e381`'s**: a configuration check is only as strong as
the field list it is given, and a claim whose manipulation is not in that list passes vacuously.

## 4. What it cannot do

*Five budgets per rate*: so the trajectory between samples is not measured, and a collapse at the first update is
established and the update it happened in is not -- the reading is already at the floor at the first sample, which
means the loss happened at or before it. *And a smaller budget is a different run*: the batch order and the head's
fitting depend on how many steps were taken. *And one cell, one draw, one source*: the action source at `cue@8`, so
neither the cue source nor the wide end is compared at either rate. *And a probe is not a mechanism*: a reading at
the floor says a linear fit recovers nothing of the label from the world's eight numbers, so the scale account above
is a candidate and not a measurement, and a body that has lost the label to a linear fit may still hold it in a form
a different read-out could reach.
