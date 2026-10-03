# The other end of the window: one update costs the wide step 0.0083 where it costs the tight step 0.4792, and the series has a valley in it

*2026-10-03. `experiments/e384_the_other_end_of_the_window.py` runs `e382`'s five budgets at `cue@0` -- the wide end
of the same window, the same drive source, the same step size and the same seed stream -- with the bodies kept and
read by the corpus's own probe, `e380`'s own twenty-replicate run standing as the 500 point, and the tight step's
series read from `e383`'s artifact rather than rolled again. Four runs of five replicates, the last ending in
seconds; the reader is `runs/e384_the_other_end_of_the_window.json`. Five claims, registered before any of the new
runs' readings was opened.*

## 1. The series

| iterations | probe on task 0's examples, after task 0 | connectome's own weights | trained head, task 0 |
|---|---|---|---|
| **1** | **0.6792** | 0.6875 | 0.0833 |
| 5 | **0.5500** | 0.6875 | 0.2083 |
| 20 | 0.5875 | 0.6875 | 0.2500 |
| 100 | 0.7000 | 0.6875 | 0.3333 |
| **500** | **0.7792** | 0.6875 | 0.7500 |

chance 0.2500. The tight step at the same rate and budget reads **0.2083** at one iteration.

| claim | measured | verdict |
|---|---|---|
| E1 one configuration except the budget | `iters` and `repeats` alone differing, with the rate and the batch in the compared fields | **MET** |
| E2 the wide step's series rises | **+0.1000** from a budget of 1 to 500 | **MET** |
| E3 its first update leaves the world above the floor | **+0.4292** over chance | **MET** |
| E4 the two ends differ at the first update | **+0.4708** | **MET** |
| E5 its training adds to what the connectome carried | **+0.0917** | **MET** |

## 2. The mirror

**One update costs the wide step 0.0083 and the tight step 0.4792.** The connectome's own weights carry task 0 at
**0.6875** on these examples; one Adam update at the corpus's rate on the wide step leaves **0.6792**, and the same
one update on the tight step leaves **0.2083**. So `e383`'s registered prediction holds in the part it registered --
the wide step's series **rises** where the tight one falls, and at the first update the two ends are **0.4708**
apart -- and the account it named for that, the six-fold difference in the world's spread, is consistent with the
first update costing a hundredth of what it costs at the tight step.

**And the wide step's series is not a rise but a valley.** Nothing in the claims asked for this: the reading dips to
**0.5500** at five iterations -- a loss of **0.1375** from the connectome's own weights, sixteen times what one
update cost -- and then climbs back through 0.5875 and 0.7000 to **0.7792**, which is **0.0917 above** where it
started. So the wide step's first task is **damage and recovery**: a handful of updates take the label out of the
world and five hundred put more of it back than the connectome had. At the tight step there is no such valley, since
one update reaches the floor and nothing moves after it.

**And at the wide step the world is nearly there long before the head is.** At one update the probe reads **0.6792**
while the trained head reads **0.0833**, which is below chance -- an untrained linear layer. The head climbs 0.2083,
0.2500, 0.3333, 0.7500 across the budgets while the world goes 0.6792, 0.5500, 0.5875, 0.7000, 0.7792. So **the
training's work at this end is fitting the head**, on a representation the connectome already carries: that is the
opposite of the tight end, where the head is at the floor from the first update because the world is, and where
`e379` and `e381` found the two agreeing all the way to five hundred.

## 3. What it means

**The two ends of the window are now the same measurement with opposite signs and a shared mechanism.** `e383`'s
account -- one step perturbs the world by about `lr` per coordinate, which is of the order of the tight step's whole
signal and a fraction of the wide step's -- predicts that the first update costs the tight end much more than the
wide one, and it does, by a factor of **58**. What it did not predict, and this unit finds, is that the wide end pays
for its later gains with an early dip: the perturbation accumulates over the first few updates until the head starts
steering, and then the training recovers the label and adds to it.

**And it makes the game's reading of the window concrete.** A closed-loop task on this connectome at `cue@0` starts
from a world that already reads **0.6875** and ends at **0.7792**, with a dip to 0.55 in between; at `cue@8` it starts
from the same connectome weights at **0.6875** and is at the floor after one update. So the tight end is not a harder
training problem, it is a destroyed one, and the difference is where the cue reaches the drive rather than how the
training is scheduled.

**Reported and not claimed**: the connectome's own weights read **0.6875** in every one of the twenty rolls of both
sweeps, at every budget and both rates, which is the roll's internal check that `theta_initial` is one body.

## 4. What it cannot do

*Five budgets*: so the valley is bounded between one and five iterations and not located -- whether the dip deepens
to five and turns, or turns at three, is not measured. *And a smaller budget is a different run*: the batch order
and the head's fitting depend on how many steps were taken. *And the two ends are not one experiment*: `cue@0` and
`cue@8` differ both in the world's spread and in where the cue reaches the drive, so the factor of 58 is a difference
between two cells and not a measurement of one variable -- `e369`'s formula and `e370`'s sweep are what separate
those. *And a probe is not a mechanism*: a reading above chance says a linear fit recovers some of the label from the
world's eight numbers, so "damage and recovery" is about what is recoverable and not about what the recurrent weights
did between the samples.
