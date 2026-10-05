# What the buffer buys and what it costs: a gain on the two older tasks and a loss on the newest, on every world

*2026-10-05. `experiments/e419_what_the_buffer_buys.py` reads the two arms' **per-task** final accuracy off the six
worlds' five-hundred-update runs -- the card's world and five cue redraws, twenty replicates each. `e410` read the
`naive` arm's decomposition and `e411` the two arms' means; this reads the buffer's own per-task ledger, which is where
the net is taken. No training, no probe. Five claims, registered before this unit's pass over the runs.*

## 1. The per-task ledger

| world | naive 0/1/2 | replay 0/1/2 | gain 0 | gain 1 | gain 2 | coverage |
|---|---|---|---|---|---|---|
| **cue6** | 0.2750 0.4167 0.8729 | 0.5906 0.6667 0.7698 | **+0.3156** | +0.2500 | **-0.1031** | 5.48 |
| **cue9** | 0.3500 0.4354 0.8115 | 0.6542 0.6812 0.7333 | +0.3042 | +0.2458 | -0.0781 | 7.04 |
| **cue3** | 0.3542 0.4719 0.8240 | 0.6563 0.6906 0.7500 | +0.3021 | +0.2188 | -0.0740 | 7.04 |
| **card** | 0.3240 0.4292 0.8042 | 0.6135 0.6781 0.7438 | +0.2896 | +0.2490 | -0.0604 | 8.91 |
| **cue14** | 0.3396 0.4635 0.8271 | 0.6208 0.6854 0.7844 | +0.2813 | +0.2219 | -0.0427 | 11.78 |
| **cue1** | 0.3250 0.4646 0.8542 | 0.5885 0.6646 0.7896 | +0.2635 | +0.2000 | -0.0646 | 7.18 |

The worlds are ordered by their task-0 gain. *Coverage* is the two older gains over the newest loss.

| claim | measured | verdict |
|---|---|---|
| AT1 the ledger is carried | six worlds, both arms at **20** replicates, three per-task entries each | **MET** |
| AT2 and the buffer gains on the oldest task | **+0.2635** to **+0.3156** | **MET** |
| AT3 and on the middle one | **+0.2000** to **+0.2500** | **MET** |
| AT4 and it costs the newest one | **-0.0427** to **-0.1031** on all six | **MET** |
| AT5 and the two older gains cover the newest loss | **5.48** to **11.78** times | **MET** |

## 2. What the ledger says

**The corpus's headline arm is a net, and the term it is net of is the newest task.** On every one of the six worlds
`replay` recovers the oldest task by a quarter to a third of accuracy and the middle one by a fifth to a quarter, and
it finishes the task it was taught last **0.04 to 0.10 lower** than the arm that stores nothing. The mean gain over
the eighteen task-world pairs is **+0.1510**, which is `e411`'s +0.1330 to +0.1594 read a second way -- as a sum of
eighteen numbers of which six are negative.

**And the loss is small only next to what pays for it.** The two older gains cover the newest loss by **5.48** to
**11.78** times, so the benchmark's aggregate metric reads as improvement a change that has a systematic loser. A user
of the card who reports only the mean final accuracy cannot see it; a user who reads the retention row can.

**And the gain is ordered by position, not by task.** The oldest task gains most on every world, the middle one next,
and the newest loses: the buffer is worth what memory is worth, and the corpus's protocol teaches the tasks in one
order so the loss lands on the last one every time.

## 3. What it cannot settle

- **One setting and one pair**: the corpus's buffer (`--replay-per-task 16 --replay-batch 16`) and the
  `naive`/`replay` arms at five hundred updates on six worlds, so nothing here is about the penalty arms `e415` and
  `e416` read elsewhere.
- **And the loss is on the arm's own last task**: the order is fixed by convention, and `e317` showed that reversing
  it moves the arms that read a penalty and leaves the arms that read none alone, so where the loss falls is a
  property of this order.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned -- the task-2 loss here is a `learned` loss as much as a
  forgetting one, since the last task is never forgotten after it is taught.
- *And a decomposition is not a mechanism.*
