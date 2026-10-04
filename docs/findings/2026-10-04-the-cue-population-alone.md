# The cue population alone: two cue draws at the same distance behave differently, so the distance is not what decides it

*2026-10-04. `experiments/e398_the_cue_population_alone.py` adds the engine's missing seed. `cue_seed` draws the cue's
twelve neurons from a second generator that consumes nothing from the environment's, so the action and feedback
populations and the world's three maps stay exactly the card's -- and `e397`'s finding named precisely this as what
would turn its separation into a mechanism. Sixteen cue draws are measured for their cue-to-action distance and two
are trained, chosen by a **geometric criterion registered before any training**: the first at distance 2 and the
first at 1. Five claims, registered before any run's reading was opened.*

## 1. Sixteen cue draws, two of them trained

The search's cue-to-action distances over seeds 1 to 16: **2** at seeds 3, 9 and 14; **1** at the other thirteen.
So of sixteen cue populations drawn against the card's own action, feedback and maps, three put the cue two hops
from the action and thirteen put it one.

| world | cue seed | connectome's own reading | body after 20 updates | body after 500 updates | gain over the connectome | trained head at 500 |
|---|---|---|---|---|---|---|
| the card's | -- | 0.6875 | 0.5740 | **0.7729** | **+0.0854** | 0.7500 |
| the first **two-hop** cue draw | 3 | 0.6875 | 0.5219 | **0.5240** | **−0.1635** | 0.8333 |
| the first **one-hop** cue draw | 1 | 0.6875 | 0.4990 | **0.5062** | **−0.1813** | 0.7500 |

chance 0.2500. The head column is the first replicate's own accuracy, not a mean.

| claim | measured | verdict |
|---|---|---|
| T1 only the cue population moved | 0 of the two draws moved a driven field, both differ in the cue's | **MET** |
| T2 the search found both geometries | **3** draws at distance 2, **13** at 1, over 16; the chosen are the first of each | **MET** |
| T3 the outcome follows the distance | **−0.1635** and **−0.1813**, both below the bar | **FALSIFIER FIRED** |
| T4 the initial reading does not move | **0.6875** three times, spread **0.0000** | **MET** |
| T5 the near point does not separate them and the far point does | **0.0229** apart at twenty, **0.0177** at five hundred | **FALSIFIER FIRED** |

## 2. What fired, and what it takes back

**The distance is not what decides it.** The card's world is at distance **2** and recovers by **+0.0854**; a
**different** cue population at the same distance **2** loses the cue by **−0.1635** -- as much as the one-hop draw's
**−0.1813**. And the two trained draws differ from the card's world in **nothing but which twelve neurons carry the
cue**: their action and feedback populations and all three of their world maps are the card's own, verified
fingerprint by fingerprint. So the decision lives in the **cue population's identity**, and not in its distance to
the action population -- `e397`'s caveat, that its separation was *"an association and not a mechanism"* and that
the distance could be *"a marker of the draw that happened to carry it"*, is now a measurement rather than a
qualification.

**And moving the cue population alone does not reproduce the redraw's spread either.** T5 fired on its second half:
the two chosen draws read **0.0229** apart after twenty updates and **0.0177** apart after five hundred. Both lose
the cue by about a sixth, so the far-point difference of a third of the reading that `e396` measured across the
engine's own redraws is **not** carried by the cue population alone. Whatever moves the far point between the card's
world and the four redraws is therefore spread over the fields the redraw moves together -- the populations and the
maps -- and not isolated in either half of them.

**And the invariance holds on a third axis.** Three more readings at **0.6875** -- the card's cue draw and the two
new ones -- for **twenty** in all across two budgets, five engine draws, four streams and now three cue populations.
The initial reading does not depend on the cue's twelve neurons either.

## 3. What the engine now has, and what it cannot settle

- **The engine has the seed its redraw series has been missing.** `cue_seed` is a keyword on `fly_env.build` and a
  flag on the runner, defaulting to nothing so every earlier artifact is bit-identical through it: only the cue's
  population is redrawn, and `drive_from_cue` refuses it because there the action population *is* the cue's.
- **Two draws are two points.** One at each distance, so what is measured is that *these* two behave as they do and
  not that every two-hop draw fails; the other fourteen cue draws are measured for their distance and not trained.
- **And the two-hop population is not one class.** Among the three draws at distance 2 the card's recovers and seed
  3 does not, so the distance-2 set contains at least one of each behaviour and the next question is what separates
  them -- a property of the twelve neurons themselves, which this unit does not name.
- **The criterion is a selection**: the draws were chosen by their distance, so what a training run would show
  without that choice is not measured.
- *And a probe is not a mechanism*: the readings say how much of the label a linear fit recovers from the world's
  eight numbers.
