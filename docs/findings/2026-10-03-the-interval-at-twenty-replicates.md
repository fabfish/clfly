# The interval at twenty replicates: the floor is at fourteen, and the rise off it flattens

*2026-10-03. `experiments/e389_the_interval_at_twenty_replicates.py` rolls the wide step's first task again at
eleven budgets -- **1**, **2**, **3**, **4**, **5**, **6**, **8**, **11**, **14**, **17**, **20** -- at **twenty**
replicates, the count `e388` registered as what the interval's resolution needed. Same cell, same rate, same seed
stream, wider: the series is one instrument at one resolution. The reader is
`runs/e389_the_interval_at_twenty_replicates.json`. Five claims, registered before any of the new runs' readings was
opened.*

## 1. The series, and what the wider roll does to it

| iterations | 20 replicates | sem | 5 replicates | difference |
|---|---|---|---|---|
| 1 | 0.6792 | 0.0087 | 0.6792 | 0.0000 |
| 2 | **0.6281** | 0.0134 | 0.5917 | **+0.0364** |
| 3 | **0.6323** | 0.0188 | 0.5750 | **+0.0573** |
| 4 | **0.6062** | 0.0193 | 0.5625 | **+0.0437** |
| 5 | **0.5979** | 0.0224 | 0.5500 | **+0.0479** |
| 6 | 0.5938 | 0.0250 | 0.5667 | +0.0271 |
| 8 | 0.5750 | 0.0200 | 0.5542 | +0.0208 |
| 11 | 0.5719 | 0.0188 | 0.5875 | -0.0156 |
| 14 | **0.5479** | 0.0228 | 0.5292 | +0.0187 |
| 17 | 0.5740 | 0.0260 | 0.5750 | -0.0010 |
| 20 | 0.5740 | 0.0243 | 0.5875 | -0.0135 |

chance 0.2500; the connectome's own weights read **0.6875** on these examples. The reference column is the series
`e385` and `e388` read at five replicates, which is the first five of this unit's own seed stream, so the difference
is the replicate count and nothing else.

| claim | measured | verdict |
|---|---|---|
| J1 one configuration except the budget and the replicates | `iters` and `repeats` alone differing, on all eleven runs | **MET** |
| J2 the resolution improved | errors **0.0188** to **0.0260**, against the five-replicate worst of **0.0546** | **MET** |
| J3 the interval's spread is above the instrument | the band is **1.92** times the widest error | **NULL** |
| J4 with the noise under it, the interval turns | the minimum is at **14** and the descent into it is strict, but the rise out of it is not | **FALSIFIER FIRED** |
| J5 the floor is a fifth of the way below five | **+0.0500** | **MET** |

## 2. What fired, and what it answers

**The floor is at fourteen and the descent into it is real.** The readings over the interval are 0.5979, 0.5938,
0.5750, 0.5719, **0.5479**, 0.5740, 0.5740. Over five consecutive budgets -- 5, 6, 8, 11, 14 -- the series falls
strictly, which is the monotone descent `e388` could not see at five replicates. J4 nevertheless **fired**, on its
other half: the rise out of the floor is not strict, because 17 and 20 both read **0.5740**. So the turn exists and
the recovery off it flattens rather than climbing. The floor is located between 11 and 17, against the interval 5
to 20 `e388` left it in.

**Half of `e385`'s dip was the replicate count.** This is reported and not claimed, because it was not registered:
at twenty replicates the readings at budgets 2, 3, 4 and 5 are **0.6281**, **0.6323**, **0.6062** and **0.5979**,
against the **0.5917**, **0.5750**, **0.5625** and **0.5500** the same seeds' first five gave -- higher by
**0.0364, 0.0573, 0.0437** and **0.0479**. The five-replicate series `e384` and `e385` built falls to 0.5500 by
five and this one falls to 0.5979, so the depth of the wide step's dip at five updates is **0.0813** where `e385`
recorded **0.1292**, and the last three of `e385`'s steps were already inside its own standard errors. The
front-loading `e385` found -- most of the drop in the first two updates -- survives (0.6792 to 0.6281 is 0.0511 of
the 0.0813), but its size does not.

## 3. What the wider roll leaves

The errors came down as the square root predicted: the worst over the interval is 0.0260 against 0.0546, and every
budget is inside 0.030, so J2's face of the resolution claim met. The band from 5 to 20 is 0.0500 wide against that
0.0260, **1.92 times** it -- J3's registered bar was 2.0 and it returned **NULL**, so the interval's spread is above
the instrument by the falsifier's margin but not by the claim's. The trained head still sits at 0.2083 through the
whole floor and reaches 0.2500 only by twenty, so the descent and the flat recovery both happen while the head is
at chance.

## 4. What it cannot settle, and what it registers

- **The floor is bounded, not located.** The strict descent runs to 14 and turns by 17, so the floor is between 11
  and 17; a turn inside one update is invisible and a smaller budget is a different run.
- **The recovery off the floor is flat over at least three budgets** (17 and 20 both 0.5740), which is a shape the
  twenty-replicate series shows and the five-replicate one hid: `e385` read 0.5750 and 0.5875 at those budgets and
  called it a recovery. Where the climb to 0.7000 at a hundred starts is the next question this leaves.
- *One cell and one draw*: the action source at `cue@0`, so the cue source and the tight end are not resolved this
  way. *And a probe is not a mechanism*: a reading says how much of the label a linear fit recovers from the world's
  eight numbers, so the floor is a shape in what is recoverable and not a named process.
