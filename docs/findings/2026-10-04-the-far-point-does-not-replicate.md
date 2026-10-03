# The far point does not replicate: on two other worlds 500 updates leave the body below where it started

*2026-10-04. `experiments/e395_the_far_point_on_more_worlds.py` takes two of the worlds `e393` drew at the near
point -- `--loop-seed 1` and `2` -- and runs them to the card's **far** point instead: **500** updates, twenty
replicates, everything else the card's. `e380`'s own 500-update run is the card's world, so two of the five worlds
now carry a reading at each end of the trajectory. Five claims, registered before any of the new runs' readings was
opened.*

## 1. Three worlds at the far point

| world | connectome's own reading | body after 500 updates | gain over the connectome | trained head, task 0 |
|---|---|---|---|---|
| the card's | **0.6875** | **0.7729** | **+0.0854** | 0.7500 |
| **1** | **0.6875** | **0.4854** | **−0.2021** | 0.8333 |
| **2** | **0.6875** | **0.4677** | **−0.2198** | 0.7292 |

chance 0.2500. The head column is the first replicate's own accuracy, not a mean.

| claim | measured | verdict |
|---|---|---|
| P1 one configuration except the draw | 17 placed, 11 drawn, **none** in neither list, **none** moved | **MET** |
| P2 the three runs are three worlds | three fingerprints, **three** distinct values each | **MET** |
| P3 the connectome's own reading does not move | **0.6875** three times, spread **0.0000** | **MET** |
| P4 the far point replicates | spread **0.3052** | **FALSIFIER FIRED** |
| P5 the far-end headline replicates | **−0.2021** and **−0.2198**, both below the bar | **FALSIFIER FIRED** |

## 2. What fired, and what it says

**The card's far end is its world's.** The card's own world climbs from 0.6875 to **0.7729** by five hundred
updates, and that climb is what `e390` and `e391` measured as the recovery. On the two redraws the same five hundred
updates leave the body at **0.4854** and **0.4677** -- **below** where the connectome started, by 0.20 and 0.22, and
below where those same worlds sat after **twenty** updates (`e393`: 0.5208 and 0.5010). So on two of the five worlds
the far point is not a recovery at all: the world ends up holding *less* of the task than an untrained body did, and
four hundred and eighty more updates on top of twenty move it by **−0.0354** and **−0.0333** where the card's world
moves by **+0.1989**.

**And the head carries the task instead.** The trained heads on the redraws read **0.8333** and **0.7292**, against
**0.7500** on the card's world, while the bodies read 0.4854 and 0.4677. So the two redraws are in the state `e379`
and `e380` described at the tight step: the world holds almost nothing and the head has the answer. What those units
found by freezing the body, this unit finds by redrawing the world.

**So the near point's result does not extend to the far one.** `e393` found the twenty-update headline replicating
on four redraws with the card's world the *mildest*, and its spread was 0.0906. At five hundred updates the same
axis spreads the body **0.3052**, three times as much, and the card's world is the *only* one above the starting
reading. The benchmark's near point is a property of the game; its far point is a property of the world. That is the
second revision's most important line, and it reverses the direction `e390`'s and `e391`'s trajectory suggested.

**And the invariance holds again.** Three more draws at **0.6875** exactly -- twelve in all now, across two budgets,
five worlds and four streams, with a spread of 0.0000 every time. The reading still does not depend on the draw, and
this unit adds nothing to the explanation except that the first and last readings of the trajectory are now measured
on the same worlds.

## 3. What it cannot settle, and what it registers

- **Two redraws are two samples**, and both are two of `e393`'s four -- so the far end is measured on a subset of
  the near end's worlds and not on a fresh draw. Whether the other two of the four behave like 1 and 2 or like the
  card's world is not measured, and it is the first thing to run.
- **And the far end's dependence is not located.** The redraw moves the cue and action populations and the three
  maps together, so nothing separates which of them makes a world one where the world keeps the cue from one where
  the head does; `e369`'s distance and `e368`'s horizon are the candidates and neither is varied here.
- **One budget and one axis**: 500 updates is the far point, `seed0` is 0 and the stream is not redrawn.
- *And a probe is not a mechanism*: a reading says how much of the label a linear fit recovers from the world's
  eight numbers, so "the world keeps the cue" is a statement about recoverability and not about where a body put it.
