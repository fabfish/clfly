# Two updates on all six worlds: the card's world falls from first to fourth, and the agreement with the far end weakens

*2026-10-04. `experiments/e406_two_updates_on_all_six_worlds.py` runs the second step on all six measured worlds,
against their one-update bodies (`e405`'s) and their five-hundred-update ones. `e405` found the draw's ordering
already there after one update and registered the next measurement: *"the second step costs [the card's world] twenty
times the first -- whether the six worlds' order survives that is the next measurement."* Five claims, registered
before any of the new runs' readings was opened.*

## 1. Six worlds, three budgets

| world | cue seed | connectome's own reading | body after 1 update | body after 2 updates | body after 500 updates |
|---|---|---|---|---|---|
| **14** | 14 | 0.6875 | 0.6677 | **0.6438** | 0.5396 |
| **6** | 6 | 0.6875 | 0.6729 | **0.6427** | 0.4792 |
| **3** | 3 | 0.6875 | 0.6521 | **0.6375** | 0.5240 |
| **the card's** | -- | 0.6875 | **0.6792** | **0.6281** | **0.7729** |
| **1** | 1 | 0.6875 | 0.6469 | **0.5854** | 0.5062 |
| **9** | 9 | 0.6875 | 0.6188 | **0.5760** | 0.4625 |

The worlds are ordered by their two-update readings, best first, and the two columns beside it are the same worlds at
the two other budgets. **The card's world is first at one update, fourth at two, and first again at five hundred.**

| claim | measured | verdict |
|---|---|---|
| AI1 only the cue population moved, at a budget of two | 3 of 51 fields vary, the cue seed's and the plumbing's | **MET** |
| AI2 the order survives the second step | **+0.600** between the one- and two-update orders | **NULL** |
| AI3 the card's world is still the outlier | **cue14** reads above it after two updates | **FALSIFIER FIRED** |
| AI4 the initial reading does not move | **0.6875** six times, spread **0.0000** | **MET** |
| AI5 the separation is still growing | **0.0677** between the one-update **0.0604** and the five-hundred **0.3104** | **MET** |

## 2. What the three budgets say together

**The first step's ordering was partly luck.** The rank correlation between the one- and two-update orders is
**+0.600**, in the unit's null band and not above the 0.8 the claim asked for, and the card's world drops three
places: it reads **0.6792** after one update (the maximum of the six) and **0.6281** after two, below cue seeds 14, 6
and 3. Its agreement with the far end falls with it -- the correlation between the one-update order and the
five-hundred-update order is **+0.69** and between the two-update order and the far one **+0.43**. So `e405`'s
finding, that the draw's ordering is already there after a single step, holds **for that step** and does not carry
into the next: the far-end ordering is not established at the beginning and re-established; it is broken and made
again.

**And the spread grows where the order does not.** The six worlds span **0.0604** at one update, **0.0677** at two and
**0.3104** at five hundred -- a monotone widening -- while their **order** goes from agreeing with the far end at 0.69
to 0.43. So the two things a redraw series measures are not the same thing: the separation is a smooth widening and
the ranking inside it is not.

**And the card's own trajectory has a valley in it, which is why.** `e385` measured the card's world at 0.6792,
0.5917, 0.5750, 0.5625 and 0.5500 for one to five updates before it climbs back to 0.7729 by five hundred: the world
the line is about **falls for five steps** and recovers only over hundreds. A ranking taken at one update is a
ranking taken on the way down, and one taken at two is taken further down, so neither can be the far end's.

**Reported and not claimed**: this unit's card run at two updates reads **0.6281** where `e385`'s five-replicate roll
of the same budget read **0.5917**, a difference of **0.0364**. `e385`'s series was at five replicates and `e389`
showed that stream to be biased low by about that much at the near point, so the two readings are consistent and
this unit's twenty-replicate roll is the one to use.

## 3. What it cannot settle, and what it registers

- **Two updates are two updates**: three, five and twenty are not measured here, and `e385`'s card-only series has
  the world still falling at five. Whether the ordering is re-established by twenty, by a hundred, or only at the
  end is the stretch that remains.
- **And the ordering is against six worlds**: the four engine redraws are not run at either of these budgets.
- **One arm and one rate**: the 3e-3 `naive` bodies only.
- *And a probe is not a mechanism.*
