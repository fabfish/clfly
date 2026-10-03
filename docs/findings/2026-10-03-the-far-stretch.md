# The far stretch: a steady climb from a hundred to five hundred, crossing the connectome's own reading on the way

*2026-10-03. `experiments/e391_the_far_stretch.py` samples the wide step's first task at three budgets inside the four
hundred updates `e390` named as the largest unmeasured gap -- **150**, **275**, **425** -- the same cell and rate at
the corpus's twenty replicates, with the hundred point read from `e390`'s artifact and the five-hundred point rolled
from `e380`'s saved bodies. The reader is `runs/e391_the_far_stretch.json`. Five claims, registered before any of the
new runs' readings was opened.*

## 1. The stretch

| iterations | probe on task 0's examples | sem | trained head, task 0 |
|---|---|---|---|
| 100 | 0.6385 | 0.0188 | 0.3333 |
| **150** | **0.6927** | **0.0160** | **0.3542** |
| **275** | **0.7510** | **0.0165** | **0.6458** |
| **425** | **0.7646** | **0.0117** | **0.8333** |
| 500 | 0.7729 | 0.0153 | 0.7500 |

chance 0.2500. **The connectome's own weights read 0.6875 on these examples**, so the body is below where it started
at a hundred and above it at a hundred and fifty. The head column is the first replicate's own accuracy, not a mean.

| claim | measured | verdict |
|---|---|---|
| L1 one configuration except the budget | `iters` and `repeats` alone differing, on all four runs | **MET** |
| L2 the stretch ends higher than it starts | **+0.1344** | **MET** |
| L3 it rises at every sample on the way | **no budget** below its predecessor | **MET** |
| L4 the stretch is above the instrument | **7.16** times the widest error | **MET** |
| L5 the recovery after a hundred is more than half of it | **59.7%** | **MET** |

## 2. What the five claims answer together

**The four hundred updates are a steady climb and not a plateau.** Every sampled budget is above the one before:
0.6385, **0.6927**, **0.7510**, **0.7646**, 0.7729. L4 puts the span at **7.16** times the widest standard error
there, against the **2.92** `e390` measured over the nineteen budgets from twenty to a hundred -- so the far stretch
is a much larger movement than the near one, and the recovery is where `e390` said the mass of it was. L5 measures
that share: **0.1344 of the 0.2250** between the floor and five hundred, **59.7%**, happens after the hundredth
update.

**And the climb is front-loaded inside the stretch.** The two largest steps are the first two -- 100 to 150 is
**+0.0542** and 150 to 275 is **+0.0583**, together 0.1125 of the 0.1344 -- and the last two add **+0.0136** and
**+0.0083**. So the body does most of its recovering by 275 updates and then eases toward 0.7729, which is still
below the 0.7792 `e384`'s five-replicate series recorded for this same run.

**And the body crosses where it started between a hundred and a hundred and fifty.** The connectome's own weights
read **0.6875**; the trained body reads 0.6385 at a hundred and **0.6927** at a hundred and fifty. So the wide
step's training spends its first hundred updates below the starting point and only passes it in the second hundred
-- the same valley the whole line has been about, with its far edge now sampled.

**And the head overtakes while the world is still climbing.** The trained head walks 0.3333, 0.3542, **0.6458**,
**0.8333** and 0.7500 across the stretch, so by 275 updates it is reading the task far better than the world's
recoverable eight numbers encode it. That is the first sample in the trajectory where the head exceeds **0.5** and
it happens inside the far stretch and not before it.

## 3. The trajectory, closed

One update **0.6792**, five **0.5979**, the floor at fourteen **0.5479**, the bottom flat through twenty and thirty
(**0.5740**, **0.5677**), the first climb at 45, 65, 85 and 100 (**0.5844**, **0.6146**, **0.6167**, **0.6385**),
and the far stretch at 150, 275, 425 and 500 (**0.6927**, **0.7510**, **0.7646**, **0.7729**), against the
connectome's own **0.6875** and a chance of 0.2500. Thirteen budgets, one cell, one rate, one seed stream, twenty
replicates each.

## 4. What it cannot settle, and what it registers

- **Three samples are three samples.** The largest gap left is now between **275** and **425**, two hundred updates
  wide, and the whole climb's front-loading sits across it: whether the easing starts before or after 275 is not
  measured.
- **The head's column is one replicate**, so the 0.8333 at 425 against 0.7500 at 500 is not a comparison of means and
  the head's own shape is not measured here.
- *One cell and one draw*: the action source at `cue@0`, so the cue source and the tight end are not resolved this
  way, and every number above is one circuit and one world draw.
- *And a probe is not a mechanism*: a reading says how much of the label a linear fit recovers from the world's eight
  numbers, so the crossing at a hundred and fifty is a crossing of recoverability and not a named process.
