# The floor between five and twenty is a band, and the band is one standard error wide

*2026-10-03. `experiments/e388_the_floor_between_five_and_twenty.py` samples the wide step's first task at five
budgets inside the interval `e385` registered as holding its floor -- **6**, **8**, **11**, **14**, **17** -- the
same cell, rate and seed stream, five replicates each, with `e385`'s own series read from its artifact as the ends
the new samples join. Five short runs; the reader is `runs/e388_the_floor_between_five_and_twenty.json`. Five
claims, registered before any of the new runs' readings was opened.*

## 1. The series, and the interval's own resolution

| iterations | probe on task 0's examples | trained head, task 0 | standard error of the probe |
|---|---|---|---|
| 1 | 0.6792 | 0.0833 | 0.0193 |
| 2 | 0.5917 | 0.0625 | 0.0182 |
| 3 | 0.5750 | 0.1667 | 0.0141 |
| 4 | 0.5625 | 0.1875 | 0.0395 |
| 5 | 0.5500 | 0.2083 | 0.0440 |
| **6** | 0.5667 | 0.2083 | **0.0232** |
| **8** | 0.5542 | 0.2083 | **0.0546** |
| **11** | 0.5875 | 0.2083 | **0.0541** |
| **14** | **0.5292** | 0.2083 | **0.0409** |
| **17** | 0.5750 | 0.2292 | **0.0538** |
| 20 | 0.5875 | 0.2500 | 0.0434 |
| 100 | 0.7000 | 0.3333 | -- |
| 500 | 0.7792 | 0.7500 | -- |

chance 0.2500; the connectome's own weights read **0.6875** on these examples at every budget where they were
rolled. The **bold** budgets are this unit's; the others are read from `e385`'s artifact, whose own per-replicate
spread is shown where the saved weights allow it. The standard error is over the five replicates, each of which is a
different world draw, a different test set and a different training seed.

| claim | measured | verdict |
|---|---|---|
| I1 one configuration except the budget | `iters` alone differing, on all five runs | **MET** |
| I2 the floor is interior, not at either end | the minimum is at **14**, interior, but the series rises at 5 to 6 and again at 8 to 11 | **FALSIFIER FIRED** |
| I3 the dip continues past five | **+0.0208** | **MET** |
| I4 the recovery has begun by twenty | **+0.0583** | **MET** |
| I5 the floor happens while the head is unfitted | at a budget of 14 the head reads **-0.0417** over chance | **MET** |

## 2. What fired, and what it answers

**The floor is not a turn.** I2 asked the interval to fall into a single minimum and rise out of it. It does not:
the readings are 0.5500, **0.5667**, 0.5542, **0.5875**, **0.5292**, 0.5750, 0.5875 -- up between 5 and 6, up
again between 8 and 11, down to the minimum at 14, up again at 17. There is no monotone approach to the minimum
from either side, so what `e385` registered as a floor to locate is not a point the series descends to.

**And the interval is flat within the instrument.** This was not a registered claim, and it is reported rather than
claimed: the whole band from 5 to 20 spans **0.0583**, and the standard error of the new budgets' means over their
five replicates runs **0.0232** to **0.0546**. The band is therefore **1.07 times the widest** of those standard
errors -- the entire excursion from the lowest to the highest reading in the interval is about one standard error
wide. At five replicates there is no turn to locate inside this interval, because the instrument cannot resolve one
that size.

**That re-reads `e385`'s registered interval.** `e385` found the series falls the whole way to five and registered
"the floor is between five and twenty updates". The last three of its own steps -- 0.0167, 0.0125, 0.0125 between
budgets 2 and 3, 3 and 4, 4 and 5 -- are all smaller than the standard errors of the means they join (0.0182 and
0.0141, 0.0141 and 0.0395, 0.0395 and 0.0440), so the part of that fall which is robust is the first step or two
(1 to 2 is 0.0875 against 0.0193 and 0.0182 there) and not the monotone tail. The reading at 20 exceeds the reading
at 5 by 0.0375, against a standard error of 0.0440 at 5 and 0.0434 at 20; I4 met its registered bar of 0.02 and is
nonetheless inside the noise.

## 3. What the head does across the interval

The trained head walks from 0.0833 at one update to 0.2500 at twenty and 0.7500 at five hundred, while the world
sits in the band the whole time and reads 0.2083 at the floor's budget, **below chance**. So the valley's bottom is
a stretch where the connectome's body has lost most of the cue and the head has not yet taken over: at a budget of
14 the world reads 0.5292 against its own initial 0.6875, and the head reads 0.2083. I5's face of that met.

## 4. What it cannot settle, and what it registers

- **The resolution is the finding.** The turn is not located because it is smaller than five replicates can
  resolve; a series at this interval needs enough replicates to put the standard error of the mean well below the
  differences being compared. Twenty replicates, the corpus's own replicate count for a decisive cell, would halve
  it.
- *Five more budgets are five more samples*: even resolved, the floor would be bounded between two budgets and not
  located to a step, and a turn inside a single update stays invisible.
- *And a smaller budget is a different run*, *one cell and one draw*, and *a probe is not a mechanism* -- the
  readings say how much of the label a linear fit recovers from the world's eight numbers and not what process put
  it there.
