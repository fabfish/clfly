# The aid turns on in every world: nothing at twenty updates and a sixth at five hundred, on all six draws

*2026-10-05. `experiments/e413_the_aid_turns_on_in_every_world.py` reads **six** worlds -- the card's and five cue
redraws -- at budgets **1**, **20** and **500**, each at twenty replicates with both arms, off the runs `e405`,
`e407`, `e398`, `e399`, `e401` and `e380` wrote. `e412` read the card's world's twenty-rung ladder and named one world
as what it could not settle; this reads the other five at the ladder's two ends. No training, no probe. Five claims,
registered before this unit's pass over the eighteen runs.*

## 1. The six worlds at the three budgets

| world | naive acc 1 | naive acc 20 | naive acc 500 | gain 1 | gain 20 | gain 500 | rise | cut 1/20/500 |
|---|---|---|---|---|---|---|---|---|
| **card** | 0.2438 | 0.2969 | 0.5191 | +0.0000 | **-0.0045** | +0.1594 | **+0.1639** | +0.009/+0.031/+0.284 |
| **14** | 0.2674 | 0.3014 | 0.5434 | +0.0003 | +0.0017 | +0.1535 | +0.1517 | +0.008/+0.036/+0.276 |
| **1** | 0.2708 | 0.2969 | 0.5479 | +0.0073 | +0.0021 | +0.1330 | +0.1309 | +0.012/+0.014/+0.234 |
| **9** | 0.2691 | 0.2799 | 0.5323 | **-0.0174** | +0.0288 | +0.1573 | +0.1285 | -0.002/+0.062/+0.307 |
| **6** | 0.2497 | 0.2844 | 0.5215 | +0.0062 | **+0.0365** | +0.1542 | +0.1177 | +0.007/+0.064/+0.315 |
| **3** | 0.2653 | 0.2941 | 0.5500 | +0.0045 | +0.0347 | +0.1490 | **+0.1142** | +0.003/+0.061/+0.268 |

The worlds are ordered by their rise from budget 20 to 500, best first.

| claim | measured | verdict |
|---|---|---|
| AY1 the eighteen runs are carried | **6** worlds x **3** budgets, **20** replicates on both arms, one configuration each | **MET** |
| AY2 and no world gains a twentieth at the small budgets | the most is **+0.0365** at 20, the least **-0.0174** at 1 | **MET** |
| AY3 and every world gains a tenth at five hundred | **+0.1330** to **+0.1594** | **MET** |
| AY4 and every world's rise clears a tenth | **+0.1142** to **+0.1639** | **MET** |
| AY5 and the aid's term beats the draw's | **2.79** times the six worlds' own span at twenty, **0.0410** | **MET** |

## 2. What the six draws say

**The turn-on is the setting's and not the card's world's.** At budget 1 every world's gain is within two hundredths
of zero, from -0.0174 on cue 9 to +0.0073 on cue 1; at budget 20 it is within four hundredths, from -0.0045 on the
card's world to +0.0365 on cue 6. At budget 500 every one of the six gains at least a tenth, and the six sit inside
a band of 0.0264. Between the two ends the naive arm's own accuracy rises too -- 0.2438 to 0.2691 at budget 1,
0.2799 to 0.3014 at 20, 0.5191 to 0.5500 at 500 -- so what the aid is worth goes with what the body has learned,
on every draw.

**And the arm's rise beats the draw's spread at the same budget.** At twenty updates the six draws' gains span
**0.0410**; every one of those worlds rises by at least **+0.1142** to five hundred. So the least rise is **2.79**
times the whole spread of the aid's gain across six different worlds at the small budget: the term the benchmark's
protocol moves is again larger than the term the world moves, as `e410` and `e411` found at five hundred.

**And the card's world is the extreme on both ends.** It is the only world whose budget-20 gain is negative
(**-0.0045**), and it has both the largest rise (**+0.1639**) and the largest five-hundred gain (+0.1594). It is also
the world with the smallest cut at twenty updates (+0.031) and the one whose naive accuracy starts lowest (0.2438 at
budget 1).

## 3. What it cannot settle

- **Three budgets are three points**: between 20 and 500 the corpus's budget axis has ten rungs on the card's world
  alone, so the other five worlds' turn-on is located only between those two rungs, not dated.
- **And the arms are the `naive`/`replay` pair**: the penalty arms are absent from all eighteen runs, so `e276`'s
  replay-over-penalty contrast is not available on the six worlds at any budget.
- **And the budget is not the level**: the naive arm rises from about 0.25 to about 0.53 along the same axis, so
  "the aid goes with what was learned" is a reading over a joint ramp and not an intervention.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned.
- *And a probe is not a mechanism.*
