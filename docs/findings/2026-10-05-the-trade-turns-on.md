# The trade turns on: at twenty updates the newest task is cost in eight cells of thirteen, at five hundred in all twelve

*2026-10-05. `experiments/e421_the_trade_turns_on.py` reads the per-task ledger of the **same twelve cells** at
**twenty** updates and at **five hundred** -- the card's world and five cue redraws, four engine world redraws and two
clean streams, each with both arms at twenty replicates at both ends. `e420` found the trade's direction constant
across these cells at the far point and `e412` found the aid itself turning on between twenty and forty-five updates.
No training, no probe. Five claims, registered before this unit's pass over the runs.*

## 1. The same twelve cells at both ends

| cell | kind | gain 0/1/2 at 20 | coverage | gain 0/1/2 at 500 | coverage |
|---|---|---|---|---|---|
| **cue6** | cue | +0.0354 +0.0406 **+0.0333** | none | +0.3156 +0.2500 **-0.1031** | 5.48 |
| **stream1** | stream | +0.0229 +0.0135 **-0.0260** | 1.40 | +0.3219 +0.2323 **-0.0927** | 5.98 |
| **stream2** | stream | +0.0219 +0.0271 **-0.0052** | 9.40 | +0.2333 +0.2240 **-0.0802** | 5.70 |
| **cue9** | cue | +0.0354 +0.0469 **+0.0042** | none | +0.3042 +0.2458 **-0.0781** | 7.04 |
| **cue3** | cue | +0.0604 +0.0354 **+0.0083** | none | +0.3021 +0.2188 **-0.0740** | 7.04 |
| **world4** | world | +0.0750 +0.0021 **+0.0250** | none | +0.2615 +0.2604 **-0.0656** | 7.95 |
| **cue1** | cue | +0.0115 +0.0104 **-0.0156** | 1.40 | +0.2635 +0.2000 **-0.0646** | 7.18 |
| **card** | card | +0.0198 -0.0073 **-0.0260** | 0.48 | +0.2896 +0.2490 **-0.0604** | 8.91 |
| **world2** | world | +0.0250 +0.0135 **-0.0115** | 3.36 | +0.2615 +0.1479 **-0.0563** | 7.28 |
| **world1** | world | +0.0552 +0.0354 **-0.0302** | 3.00 | +0.3198 +0.2552 **-0.0479** | 12.00 |
| **cue14** | cue | +0.0354 +0.0125 **-0.0427** | 1.12 | +0.2813 +0.2219 **-0.0427** | 11.78 |
| **world3** | world | +0.0125 +0.0667 **-0.0010** | 76.00 | +0.3021 +0.2385 **-0.0115** | 47.18 |

*Coverage* is the two older gains over the newest loss, absent where the newest task is not cost. The unpaired third
stream, rolled at twenty updates only, gains **+0.0708, -0.0208, +0.0396**.

| claim | measured | verdict |
|---|---|---|
| AV1 the paired ledger is carried | **12** cells at both budgets, **20** replicates, over **4** kinds | **MET** |
| AV2 and at twenty updates the newest task is not systematically cost | **8** negative and **4** positive | **MET** |
| AV3 and at five hundred it is cost in every one | **12 of 12** | **MET** |
| AV4 and the recovery is a tenth of it at twenty and a fifth at five hundred | at most **+0.0750** at twenty, at least **+0.2333** at five hundred | **MET** |
| AV5 and the coverage is under one at twenty and over five at five hundred | **0.48** then **5.48**, with four cells losing nothing at twenty | **MET** |

## 2. What the two ends say

**The trade is not a property of the three tasks; it is a product of the training.** At twenty updates the newest task
is cost in **eight** of the thirteen cells the corpus rolled that far and **gains** in five, four of which are in the
paired twelve; the oldest task is recovered by at most **0.0750**; and four cells lose nothing at all, so their
coverage has no denominator. At five hundred updates the newest task is cost in **all twelve**, the oldest is
recovered by at least **0.2333**, and the least coverage is **5.48**. Between the two ends the oldest task's recovery
grows threefold and the newest task's loss goes from mixed to universal.

**And that is `e412`'s turn-on read on the second axis.** `e412` found the aid's accuracy gain at zero at twenty
updates and ramping to +0.1594 at five hundred on the card's world, and `e413` found the same on the other five. The
per-task ledger says what the aid buys when it arrives: at twenty updates the buffer is nearly free because there is
little to protect, and by five hundred it has both a recovery and a price. So what `e412` and `e413` measured as one
number is a trade whose two sides turn on together.

**And the price is paid where the order trains last.** The four cells that lose nothing at twenty updates are spread
across kinds (two cue draws, one world, one stream), so the near-end sign is the draw's; at the far end the sign is
the protocol's.

## 3. What it cannot settle

- **One order and one arm pair**: the as-built three tasks, `naive` and `replay`, so `e317`'s order axis is not in
  this reading, and the penalty arms are not either.
- **And the two ends are twenty-five times apart**: nothing here locates the turn-on between twenty and five hundred,
  which is `e412`'s twenty-rung ladder on the card's world alone.
- **And one cell is unpaired**: the third stream has no five-hundred-update run, so it is read in the near band and
  not in the pairing.
- **And the metric is the corpus's**: the newest task is never forgotten after it is taught, so its loss is a
  `learned` loss as much as a forgetting one.
- *And a ledger is not a mechanism.*
