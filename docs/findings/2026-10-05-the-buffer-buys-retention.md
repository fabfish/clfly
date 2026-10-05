# The buffer buys retention and pays in learning: the trade decomposed on all twelve draws

*2026-10-05. `experiments/e422_the_buffer_buys_retention.py` splits the paired per-task gain of the twelve far-point
cells into the **learning term** -- what the buffer changes about the level a task is taught to -- and the
**retention term** -- what it changes about how much is lost afterwards. `e419`, `e420` and `e421` measured the trade
and registered that the newest task's loss is a `learned` one; `e304` established the decomposition this reads it with.
No training, no probe. Five claims, registered before this unit's pass over the runs.*

## 1. The gain, split

| cell | learned 0/1/2 | retention 0/1/2 | gain 0/1/2 | T1 ratio |
|---|---|---|---|---|
| **card** | +0.0000 -0.0302 -0.0604 | +0.2896 +0.2792 +0.0000 | +0.2896 +0.2490 -0.0604 | 9.24 |
| **world1** | +0.0000 -0.0177 -0.0479 | +0.3198 +0.2729 +0.0000 | +0.3198 +0.2552 -0.0479 | 15.41 |
| **world2** | +0.0000 -0.0115 -0.0563 | +0.2615 +0.1594 +0.0000 | +0.2615 +0.1479 -0.0563 | 13.91 |
| **world3** | +0.0000 **+0.0208** -0.0115 | +0.3021 +0.2177 +0.0000 | +0.3021 +0.2385 -0.0115 | 10.45 |
| **world4** | +0.0000 -0.0667 -0.0656 | +0.2615 +0.3271 +0.0000 | +0.2615 +0.2604 -0.0656 | 4.91 |
| **stream1** | +0.0000 -0.0531 -0.0927 | +0.3219 +0.2854 +0.0000 | +0.3219 +0.2323 -0.0927 | 5.37 |
| **stream2** | +0.0000 -0.0750 -0.0802 | +0.2333 +0.2990 +0.0000 | +0.2333 +0.2240 -0.0802 | 3.99 |
| **cue1** | +0.0000 -0.0042 -0.0646 | +0.2635 +0.2042 +0.0000 | +0.2635 +0.2000 -0.0646 | 49.00 |
| **cue3** | +0.0000 -0.0146 -0.0740 | +0.3021 +0.2333 +0.0000 | +0.3021 +0.2188 -0.0740 | 16.00 |
| **cue6** | +0.0000 -0.0635 -0.1031 | +0.3156 +0.3135 +0.0000 | +0.3156 +0.2500 -0.1031 | 4.93 |
| **cue9** | +0.0000 -0.0646 -0.0781 | +0.3042 +0.3104 +0.0000 | +0.3042 +0.2458 -0.0781 | 4.81 |
| **cue14** | +0.0000 -0.0479 -0.0427 | +0.2813 +0.2698 +0.0000 | +0.2813 +0.2219 -0.0427 | 5.63 |

*Ratio* is the middle task's retention term over the magnitude of its learning term, where that term is a cost.

| claim | measured | verdict |
|---|---|---|
| AW1 the ledger is carried | **12** cells, both arms at **20** replicates, three per-task entries | **MET** |
| AW2 and the oldest task's whole gain is retention | learning **0.0e+00** exactly, retention **+0.2333** to **+0.3219** | **MET** |
| AW3 and the newest task's whole loss is a learning term | retention **0.0e+00** exactly, learning **-0.0115** to **-0.1031** | **MET** |
| AW4 and in the middle it pays a small learning price | retention **+0.1594** to **+0.3271**, ratio at least **3.99** | **MET** |
| AW5 and the two terms are the gain | largest gap **0.0e+00** over 12 cells and 3 tasks | **MET** |

## 2. What the split says

**The recovery is entirely retention.** At the first task the two arms are the same arm -- the buffer has nothing
stored when task 0 is taught -- so the learning term is **exactly zero** in every cell, and the whole gain of
**+0.2333** to **+0.3219** is the buffer keeping more of what it learned. At the last task nothing is taught after it,
so the retention term is **exactly zero** in every cell: the buffer never forgets the last task, it simply reaches a
**lower level** on it, **0.0115** to **0.1031** lower, and that is the entire price.

**And in the middle both terms are real, and the retention one is much the larger.** At task 1 the buffer keeps
**+0.1594** to **+0.3271** more, at a learning price of **0.0042** to **0.0750** -- a cost in **11 of the 12** cells,
the exception being `world3` where the buffer learns the middle task slightly better as well -- and the retention term
is at least **3.99** times the price. So the trade `e419`, `e420` and `e421` measured is one mechanism with two
signs: the buffer shifts accuracy from learning to keeping.

**And the two structural zeros are the protocol's, not the buffer's.** The learning term at task 0 is zero because
the arms are identical until it is taught; the retention term at task 2 because nothing is taught after it. Both are
identities of a three-task sequence in a fixed order, so a reader should take them as the decomposition's frame and
not as two more measurements -- which is also why the third one, the middle, is the only task where the split carries
information.

## 3. What it cannot settle

- **One order and one arm pair**: the as-built three tasks, `naive` and `replay`, at five hundred updates, so
  `e317`'s order axis and the penalty arms are not here.
- **And the decomposition is the corpus's**: `e305` showed that `mean_forgetting` cannot see the part an arm never
  learned, so the retention term here is the corpus's own diagonal-minus-last-row reading of what was lost.
- **And the two zeros are structural**: the learning term at task 0 and the retention term at task 2 are identities of
  the protocol, so only the middle task's split is a measurement.
- *And a decomposition is not a mechanism.*
