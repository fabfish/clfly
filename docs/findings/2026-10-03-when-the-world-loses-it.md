# When the world loses it: the collapse costs 0.4792 and takes exactly one gradient step

*2026-10-03. `experiments/e382_when_the_world_loses_it.py` stops `e379`'s cell -- the action source at `cue@8`, the
larger step size -- at five training budgets, 1, 5, 20, 100 and 500 iterations, and reads the body after task 0 with
the corpus's own probe on every task's examples. Four new runs, five replicates each, nine to eleven seconds apiece;
the 500 point is `e379`'s own twenty-replicate run. The reader is `runs/e382_when_the_world_loses_it.json`. Five
claims, registered before any of the new runs' readings was opened.*

## 1. The series

| iterations | probe on task 0's examples, after task 0 | connectome's own weights, same examples | trained head, task 0 |
|---|---|---|---|
| **1** | **0.2083** | 0.6875 | 0.2083 |
| 5 | **0.2083** | 0.6875 | 0.2083 |
| 20 | **0.2083** | 0.6875 | 0.2083 |
| 100 | **0.2083** | 0.6875 | 0.2083 |
| 500 | **0.2083** | 0.6875 | 0.2083 |

chance 0.2500.

| claim | measured | verdict |
|---|---|---|
| C1 one configuration except the budget | only `iters` and `repeats` differ, on all four runs | **MET** |
| C2 the collapse is complete by twenty iterations | **+0.0000** from the 500-iteration value | **MET** |
| C3 it is monotone in the budget | `[0.2083, 0.2083, 0.2083, 0.2083, 0.2083]`, no rise | **MET** |
| C4 the first step already costs it | one step costs **+0.4792** | **MET** |
| C5 the head tracks the world down | **0.0000** apart at every budget | **MET** |

## 2. What it says

**The whole loss happens in the first update.** The connectome's own weights carry task 0 at **0.6875** on these
examples. After **one** gradient step -- one batch of thirty-two examples, one Adam update at the corpus's larger
step size -- the body reads **0.2083**, and it reads the same number after five, twenty, a hundred and five hundred.
So the tight step's failure is not a slow drift out of a working regime and not a competition between tasks: it is an
**immediate** collapse, and everything `e374`, `e375`, `e379` and `e381` measured is what one update left behind.

**And the head is already at the floor with it.** The trained head's own accuracy for task 0 is **0.2083** at every
budget, exactly the probe's number, so the head and a closed-form fit agree from the first step on. One step at the
corpus's learning rate is not enough to fit anything, so both are reading the same constant: the head's
**0.2083** there is not learning, it is the floor a constant classifier gets on that split.

**It also explains `e381`'s frozen matrix.** That unit found the tight step's retention matrix identical at every
checkpoint from the first one on, and read it as a collapse "during the first task's training that never recovers and
never worsens". This says how much of that task's training it took: one step. The matrix is frozen because it was
already frozen before the second iteration.

**And it makes the size of the step the thing to look at.** The sweep is at the corpus's larger learning rate, and
`e377` showed the smaller one reaches the same end state after five hundred steps. A single Adam update at `0.03`
moves a coordinate by about **0.03**, which is a large fraction of a connectome weight; at `0.003` the same one step
moves it by a tenth of that. So the natural next question is whether the **smaller** step also collapses at the first
update or drifts there over hundreds -- this unit samples only the larger rate, and the same four runs at the
corpus's default are a minute of compute.

## 3. What it cannot do

*Five budgets are five samples*: the trajectory between them is not measured, so a collapse inside a single step is
invisible here -- and since the reading is already at chance at one step, what this unit establishes is that the
loss is complete by the **first** sample and not that it happened **in** the first update rather than in the
evaluation that followed it. *And a smaller budget is a different run*: the batch order, the head's fitting and any
schedule depend on how many steps were taken, so a body stopped at one step is the body a one-step run produces and
not necessarily the body a 500-step run passed through. *And one cell, one draw, one source*: the action source at
`cue@8` with the larger step size; the cue source, the wide end and the corpus's own default rate are not sampled.
*And a probe is not a mechanism*: 0.2083 says a linear fit recovers nothing of task 0 from the world's eight numbers,
not that the label is absent from them in every form.
