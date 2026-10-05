# The trade is a constant of the protocol: the newest task is cost on all twelve draws

*2026-10-05. `experiments/e420_the_trade_is_a_constant.py` reads the per-task gains of **twelve** earned-label
far-point cells -- the card's world, four engine world redraws, two clean training streams and five cue-population
redraws, all at five hundred updates and twenty replicates, all carrying both arms. `e419` read the trade on six
worlds and registered that it was six; this reads every draw the corpus varies. No training, no probe. Five claims,
registered before this unit's pass over the runs.*

## 1. The twelve cells

| cell | kind | gain 0 | gain 1 | gain 2 | coverage | loss / gain 0 |
|---|---|---|---|---|---|---|
| **cue6** | cue | +0.3156 | +0.2500 | **-0.1031** | 5.48 | 0.327 |
| **stream1** | stream | +0.3219 | +0.2323 | -0.0927 | 5.98 | 0.288 |
| **stream2** | stream | +0.2333 | +0.2240 | -0.0802 | 5.70 | 0.344 |
| **cue9** | cue | +0.3042 | +0.2458 | -0.0781 | 7.04 | 0.257 |
| **cue3** | cue | +0.3021 | +0.2188 | -0.0740 | 7.04 | 0.245 |
| **world4** | world | +0.2615 | +0.2604 | -0.0656 | 7.95 | 0.251 |
| **cue1** | cue | +0.2635 | +0.2000 | -0.0646 | 7.18 | 0.245 |
| **card** | card | +0.2896 | +0.2490 | -0.0604 | 8.91 | 0.209 |
| **world2** | world | +0.2615 | +0.1479 | -0.0563 | 7.28 | 0.215 |
| **world1** | world | +0.3198 | +0.2552 | -0.0479 | 12.00 | 0.150 |
| **cue14** | cue | +0.2813 | +0.2219 | -0.0427 | 11.78 | 0.152 |
| **world3** | world | +0.3021 | +0.2385 | **-0.0115** | 47.18 | 0.038 |

*Coverage* is the two older gains over the newest loss; *loss / gain 0* is the newest loss against the oldest gain that
pays for it. The cells are ordered by their task-2 gain, most cost first.

| claim | measured | verdict |
|---|---|---|
| AU1 the twelve cells are carried over three kinds of redraw | **12** cells at **20** replicates over **4** kinds | **MET** |
| AU2 and the newest task is cost in every cell | **-0.0115** to **-0.1031**, all twelve negative | **MET** |
| AU3 and the oldest task is recovered in every cell | **+0.2333** to **+0.3219**, weakest at **6.05 sigma** | **MET** |
| AU4 and the two older gains cover the newest loss | **5.48** to **47.18** times | **MET** |
| AU5 and the loss is small against the gain that pays for it | **0.038** to **0.344** of it | **MET** |

## 2. What the twelve say

**The trade's direction does not move with the draw.** Across four kinds of redraw -- the card's world, four engine
world redraws, two clean streams and five cue populations -- the newest task is cost in **every** cell, by **0.0115**
to **0.1031** of final accuracy, while the oldest is recovered by **0.2333** to **0.3219** at six sigma and better.
The corpus's own record is that the *reading* varies threefold across these draws (0.3104 at the far point) and that
the final accuracy spans 0.0309; the trade is the one quantity in this line whose sign no draw reverses.

**And its size is between a twenty-seventh and a third.** The newest loss is **0.038** to **0.344** of the oldest
gain, and the two older gains cover it by **5.48** to **47.18** times. The extremes are both world redraws: `world3`
pays **0.0115** for a **+0.3021** recovery, and `cue6` pays **0.1031**. So the protocol's price is bounded and small,
but it is paid every time.

**And it is not the aid's size that is invariant, only its sign.** The task-0 gains span 0.0886 across the twelve
cells and the task-1 gains 0.1125, while `e419`'s six worlds span 0.0521 and 0.0500; so the trade is constant in
direction and variable in size, which is what a protocol constant should look like when the draw is what varies.

## 3. What it cannot settle

- **One order and one arm pair**: the corpus's three tasks in the as-built order, `naive` and `replay`, at five
  hundred updates. Whether the direction survives a reversed order is `e317`'s axis, and the penalty arms are not in
  this reading.
- **And one cell is thin**: `world3`'s loss of 0.0115 is the smallest and the claim's bar for it is its sign rather
  than a resolved difference; the next smallest is 0.0427.
- **And the cells overlap**: the card's world is also the cue-0 draw, so the twelve are not twelve independent samples
  of the protocol.
- **And the metric is the corpus's**: the task-2 loss is a `learned` loss as much as a forgetting one, since the last
  task is never forgotten after it is taught.
- *And a ledger is not a mechanism.*
