# Five budgets on all six worlds: the card's world leads at four of them, and the reshuffle was one budget's

*2026-10-04. `experiments/e407_five_budgets_on_all_six_worlds.py` adds **five** and **twenty** updates to the six
measured worlds, so each carries five budgets -- 1, 2, 5, 20 and 500 -- and the ordering can be read as a series
rather than as two ends. `e405` found the draw's ordering already there after one update and `e406` found the card's
world fourth after two with its agreement with the far end falling from 0.69 to 0.43; both registered the budgets
between as unmeasured. Five claims, registered before any of the new runs' readings was opened.*

## 1. Six worlds, five budgets

| world | cue seed | 1 update | 2 updates | 5 updates | 20 updates | 500 updates |
|---|---|---|---|---|---|---|
| **the card's** | -- | **0.6792** | 0.6281 | **0.5979** | **0.5740** | **0.7729** |
| **14** | 14 | 0.6677 | **0.6438** | 0.5396 | 0.5490 | 0.5396 |
| **3** | 3 | 0.6521 | 0.6375 | 0.5510 | 0.5219 | 0.5240 |
| **1** | 1 | 0.6469 | 0.5854 | 0.5615 | 0.4990 | 0.5062 |
| **6** | 6 | 0.6729 | 0.6427 | 0.5458 | 0.5177 | 0.4792 |
| **9** | 9 | 0.6188 | 0.5760 | 0.4802 | 0.5115 | 0.4625 |

The worlds are ordered by their 500-update readings. The span at each budget is **0.0604, 0.0677, 0.1177, 0.0750**
and **0.3104**, and the rank correlation of each budget's ordering with the far end's is **0.657, 0.429, 0.600,
0.829** and 1.000.

| claim | measured | verdict |
|---|---|---|
| AJ1 only the cue population moved, at both new budgets | 3 of 51 fields vary at each, the cue seed's and the plumbing's | **MET** |
| AJ2 the card's world is back on top by twenty | **0.5740**, the largest of the six | **MET** |
| AJ3 the ordering at twenty agrees with the far end | **+0.829** | **MET** |
| AJ4 at five the card's world is still not first | **0.5979**, the largest of the six | **FALSIFIER FIRED** |
| AJ5 the initial reading does not move | **0.6875** at both budgets, spread **0.0000** | **MET** |

## 2. What the five budgets say

**The card's world leads at four of the five prices.** It is first at one update, at five, at twenty and at five
hundred, and fourth at exactly **one** budget -- two updates. So `e406`'s reshuffle was not a descent but a
**single-budget event**: the world that recovers is the best of the six at every price the series samples except one,
and its own trajectory is the falling-then-rising valley `e385` measured.

**And the agreement with the far end comes back by twenty.** The series runs **0.657** at one update, **0.429** at
two, **0.600** at five, **0.829** at twenty and 1.000 at five hundred: it dips at two, is more than half restored by
five, and is above the unit's 0.8 bar by twenty. So the far-end ordering is not established at the start and
re-established over hundreds of updates; it is **re-established within twenty**, and the long stretch from twenty to
five hundred only sharpens it.

**And the separation is not monotone either.** The six worlds span 0.0604, 0.0677, 0.1177, 0.0750 and 0.3104 -- up,
up, **down**, then up by four times. The widest budget before the end is five updates, when every world is at or
near its own floor, and by twenty they have partly converged again before the long climb separates them. So the six
worlds are **most alike at twenty updates** of any budget sampled after the first.

**Reported and not claimed**: `e385`'s five-replicate series read the card's world at **0.5500** for five updates
where this unit's twenty-replicate roll reads **0.5979**, a difference of **0.0479** -- the same small-sample bias
`e389` measured at the near point, and another reason this unit's five-budget series is the one to read.

## 3. What it cannot settle, and what it registers

- **The long stretch is still unsampled**: twenty to five hundred is four hundred and eighty updates and holds the
  whole jump from a span of 0.0750 to 0.3104. Whether that widening is gradual or in steps is not measured.
- **And the series is six worlds wide**: the four engine redraws are not run at any of these budgets, so the anomaly
  at two updates is a six-world statement.
- **One arm and one rate**: the 3e-3 `naive` bodies only.
- *And a probe is not a mechanism.*
