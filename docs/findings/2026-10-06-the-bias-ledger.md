# The bias ledger: across the corpus the buffer leaves the bias nearer zero and every penalty leaves it further

*2026-10-06. `experiments/e431_the_bias_ledger.py` globs `runs/`, skips the second executions the corpus's own rule
collapses, and takes every artifact carrying `naive` beside another arm with a final distance of the bias from zero on
both: the second arm's distance over the baseline's, pooled by arm, with the corpus's frozen-bias cells set aside
because there both sides read zero. `e430` read that ratio on two cells; this reads every paired cell the corpus holds.
No training, no probe. Five claims, registered before this unit's pass over the corpus.*

## 1. The ledger

**207 paired cells over 159 artifacts and 4 arms**, with 16 frozen-bias cells set aside and 24 second executions
collapsed.

| arm | cells | below the baseline | above | equal | mean ratio |
|---|---|---|---|---|---|
| **`replay`** | 131 | **103** | 28 | 0 | **0.946** |
| `ewc-block-rand` | 19 | 1 | 18 | 0 | **1.456** |
| `ewc-block` | 24 | 0 | 24 | 0 | **1.473** |
| `ewc` | 33 | 0 | 31 | 2 | **1.508** |

| claim | measured | verdict |
|---|---|---|
| BG1 the ledger is carried | **207** cells over **159** artifacts and **4** arms, **131** of them the buffer's | **MET** |
| BG2 and every penalty leaves the bias at or above the baseline's | `ewc` **100%**, `ewc-block` **100%**, `ewc-block-rand` **94.74%** | **NULL** |
| BG3 and by a wide margin | mean ratios **1.456**, **1.473**, **1.508** | **MET** |
| BG4 and the buffer leaves it nearer | **103 of 131**, **78.6%** | **MET** |
| BG5 and its mean ratio is below one | **0.946** | **MET** |

## 2. What the ledger says

**The buffer leaves the head nearer where the sequence started, and the penalties leave it further.** Pooled over the
corpus's plastic cells, `replay`'s final bias distance is **0.946** of the same run's `naive` arm and below it in
**103 of 131** cells; `ewc`, `ewc-block` and `ewc-block-rand` sit at **1.508**, **1.473** and **1.456** of it. So the
ordering `e415` and `e423` measured on accuracy and retention, and `e430` on two cells, is a property of the parameter
`e427` found three quarters of the aid living in, over the whole corpus.

**And the second claim's own bar is where the matched control lands, one cell short.** The two basis arms are at or
above the baseline in **every** one of their cells (33 of 33, 24 of 24, two of the diagonal penalty's by exact
equality); the group-size-matched random control is at or above in **18 of 19**, and the nineteenth is the cell that
puts it under the registered 95% bar. So the displacement is universal to the two basis partitions and one cell short
of universal on the control that shares their group sizes -- which is the shape a null should have here, and it is
reported as the null it is rather than as a near miss.

**And the buffer's own side is a majority, not a law.** It leaves the bias nearer in a little under four cells in five,
so an arm that replays is *usually* nearer to the sequence's start than the arm that does nothing, where the two basis
penalties are *always* further. The asymmetry is the finding: the penalties' displacement is a property of the arm, the
buffer's is a tendency of it.

## 3. What it cannot settle

- **A ratio is not a mechanism**: where the bias ends and what an arm forgets are two readings of one trajectory, and
  this unit intervenes on neither, so the association is a co-movement.
- **And the cells are not independent**: the corpus's artifacts include several executions of one configuration, so the
  shares are over the corpus as it stands rather than over independent samples.
- **And the baseline is the same arm in each cell**: the ratio is per cell, so a cell whose baseline bias is small
  contributes a large ratio and the mean is over ratios rather than over distances.
- **And the distance is from the initialisation**: the corpus records the distance from zero, which for a
  zero-initialised bias is the same thing and for any other is not.
- *And a ledger is not a mechanism.*
