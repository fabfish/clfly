# The valley's shape: the dip does not turn inside the first five updates, and the second update takes 68% of it

*2026-10-03. `experiments/e385_the_valleys_shape.py` samples the wide step's first task at budgets **2**, **3** and
**4** -- the three that sit inside the valley `e384` found -- and rolls budgets **1** and **5** again as well, so the
overlap with that unit's series is a measurement of two instruments rather than of one artifact against itself. Five
runs of five replicates, seconds each; the reader is `runs/e385_the_valleys_shape.json`. Five claims, registered
before any of the new runs' readings was opened.*

## 1. The series

| iterations | probe on task 0's examples | trained head, task 0 |
|---|---|---|
| **1** | **0.6792** | 0.0833 |
| **2** | **0.5917** | 0.0625 |
| **3** | **0.5750** | 0.1667 |
| **4** | **0.5625** | 0.1875 |
| **5** | **0.5500** | 0.2083 |
| 20 | 0.5875 | 0.2500 |
| 100 | 0.7000 | 0.3333 |
| 500 | **0.7792** | 0.7500 |

chance 0.2500; the connectome's own weights read **0.6875** on these examples at every budget where they were rolled.

| claim | measured | verdict |
|---|---|---|
| F1 one configuration, and the overlap agrees | `iters` alone differing, and the shared budgets' rolls **0.0000** from `e384`'s | **MET** |
| F2 the valley turns at a single step | the minimum is at **5**, the last budget sampled | **FALSIFIER FIRED** |
| F3 the dip is a tenth deep | **+0.1292** | **MET** |
| F4 the recovery has started by five | **+0.0000** | **FALSIFIER FIRED** |
| F5 the dip happens while the head is unfitted | at the minimum the head reads **-0.0417** over chance | **MET** |

## 2. What fired, and what it answers

**The valley does not turn inside the first five updates.** `e384` registered that its five budgets bounded the dip
"between one and five iterations and not located", and the three budgets inside that interval show a series that
**falls the whole way**: 0.6792, 0.5917, 0.5750, 0.5625, 0.5500. The minimum is at the last budget sampled, so F2's
"exactly one minimum below five" is false and F4's "the recovery has started by five" is false. **The floor is
between five and twenty updates**, since by twenty the reading has come back to 0.5875 and by five hundred to 0.7792.

**And the dip is front-loaded.** The drop from one update to two is **0.0875**, which is **68%** of the whole
**0.1292**; the next three updates add 0.0167, 0.0125 and 0.0125 between them. So the wide step's damage is mostly
one update's worth of perturbation plus a second, and then the world creeps downward for the rest of the early
training before the head begins to steer it back.

**And the head is nowhere near steering while the world falls.** At the minimum, a budget of five, the head reads
**0.2083**, which is **below** a chance of 0.25, and it has wandered 0.0833, 0.0625, 0.1667, 0.1875 to get there. So
the whole visible dip happens while the head is still an unfitted linear layer, which is the
mechanism `e384` reported and this unit's F5 puts a bar under.

**And the two units rolled one instrument.** Budgets 1 and 5 were rolled again here and reproduce `e384`'s readings
**0.0000** apart, on the same seed stream, the same bodies and the same probe -- so the series above is one
trajectory read by two units and not two trajectories spliced. That is the check the claim was registered for, and
it is also the strongest evidence in this line that a saved body plus a fixed probe gives the same number twice.

## 3. What it means

**The wide step's first task is a fall and a recovery with the fall in front.** One update costs 0.0083, the second
0.0875, and the last three of the first five 0.0417 between them; the floor is somewhere in the next fifteen updates
and by five hundred the world carries **0.0917 more** of the label than the connectome did. Against the tight step,
where one update costs **0.4792** and nothing moves afterwards, the two ends differ in **shape** and not only in
size: the wide end has a trajectory to resolve and the tight end has a step.

**And it leaves the middle unsampled.** The floor is bounded between five and twenty and the recovery between twenty
and five hundred, so the shape still has two gaps -- and unlike the first, those are gaps of tens of updates rather
than of one, which is where a trajectory stops being a list of steps and starts being a curve.

**Reported and not claimed**: the connectome's own weights read **0.6875** at every budget where they were rolled,
which is the roll's internal check that `theta_initial` is one body, and the head's readings 0.0833, 0.0625, 0.1667,
0.1875 and 0.2083 are below chance throughout, so the early head is not fitted and its agreement with the world at the
first budget (`e384`) is two constants and not two readers.

## 4. What it cannot do

*Eight budgets*: so the floor is bounded between five and twenty and the recovery between twenty and five hundred,
and neither is located -- a turn inside a single update is invisible at any resolution this unit has. *And a smaller
budget is a different run*: the batch order and the head's fitting depend on how many steps were taken, so this is a
sequence of runs and not one run's history. *One cell and one draw*: the action source at `cue@0`, so the cue source
and the tight end are not resolved this way. *And a probe is not a mechanism*: the valley is a shape in what a linear
fit can recover from the world's eight numbers, so "front-loaded damage" is about recoverability and not about the
size of the weight change that produced it.
