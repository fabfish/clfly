# The trade follows the position, not the task: the same task is recovered first and cost last

*2026-10-05. `experiments/e425_the_trade_follows_the_position.py` reads the corpus's own **order axis**: three
configurations rolled twice with `config.task_order` the only differing field and the same tasks in the reverse order
-- `e315` (`ov1_t0..t2`), `e316` and `e317` (the assembly suite) -- each roll carrying both arms. `e419` to `e422` read
the trade on one order and all four registered that limit. No training, no probe. Five claims, registered before this
unit's pass over the runs.*

## 1. The same three tasks, both ways

| configuration | order | tasks | gain by position | mean |
|---|---|---|---|---|
| **overlap** | as-built | `ov1_t0>ov1_t1>ov1_t2` | **+0.0542** +0.0542 -0.0000 | +0.0361 |
| **overlap** | reverse | `ov1_t2>ov1_t1>ov1_t0` | **+0.1042** -0.0000 -0.0042 | +0.0333 |
| **assembly** | as-built | `odour_identity>heading>odour_input` | **+0.2333** +0.0937 **+0.0021** | +0.1097 |
| **assembly** | reverse | `odour_input>heading>odour_identity` | **+0.0875** +0.0667 -0.0104 | +0.0479 |
| **assembly-five** | as-built | `odour_identity>heading>odour_input` | **+0.2792** +0.0667 -0.0042 | +0.1139 |
| **assembly-five** | reverse | `odour_input>heading>odour_identity` | **+0.0667** +0.0875 -0.0208 | +0.0444 |

| the same task, taught first against taught last | at first | at last | margin |
|---|---|---|---|
| `ov1_t0` | +0.0542 | -0.0042 | **+0.0583** |
| `ov1_t2` | +0.1042 | -0.0000 | **+0.1042** |
| `odour_identity` (assembly) | +0.2333 | -0.0104 | **+0.2437** |
| `odour_input` (assembly) | +0.0875 | +0.0021 | **+0.0854** |
| `odour_identity` (assembly-five) | +0.2792 | -0.0208 | **+0.3000** |
| `odour_input` (assembly-five) | +0.0667 | -0.0042 | **+0.0708** |

| claim | measured | verdict |
|---|---|---|
| BA1 the paired ledger is carried | **3** configurations, **6** rolls, `task_order` the only differing field | **MET** |
| BA2 and the first-taught gains more than the last-taught | **+0.0542** to **+0.2834** over all six rolls | **MET** |
| BA3 and the last position is worth nothing | **-0.0208** to **+0.0021** | **MET** |
| BA4 and the same task moves with its position | all six margins **+0.0583** to **+0.3000** | **MET** |
| BA5 and reversing the order costs the buffer | **-0.0028**, **-0.0618** and **-0.0694** of mean gain | **MET** |

## 2. What the order axis says

**The trade is the sequence's, not the task's.** The same pathway is worth **+0.2333** to the buffer when it is taught
first and **-0.0104** when it is taught last (`e316`), **+0.2792** and **-0.0208** (`e317`), and the overlap suite's
`ov1_t2` is worth **-0.0000** last and **+0.1042** first (`e315`). Every one of the six such contrasts is at least
**+0.0583**. So what a task gains is where it sits in the order, which is what the four per-task units before this one
could not say because they read one order.

**And the last position is worth nothing in every roll.** The task taught third gains between **-0.0208** and
**+0.0021**, never a tenth of what the first position gains -- so the price the buffer pays is a price paid for being
last, and the loss `e422` found to be entirely a learning term is a learning cost the sequence imposes on whatever
comes last.

**And reversing the order costs the buffer.** On the same configurations the mean gain over the three tasks falls by
**-0.0028** (the overlap suite, five replicates), **-0.0618** and **-0.0694** (the assembly suite, ten and five). The
assembly pair is the sharpest: the same three pathways, the same circuit, the same draws and the same arms, and the
buffer's worth is **0.0479** against **0.1097** -- less than half, on the order alone.

## 3. What it cannot settle

- **Three configurations and one protocol**: the `naive`/`replay` pair, the corpus's buffer and three tasks with the
  middle one left in place, so a full permutation and the penalty arms are not in this reading.
- **And the replicate counts are five, ten and five**: the assembly pair carries ten and the other two five, so the
  mean gains carry the draws' own spread.
- **And the task sets are two**: the overlap suite's `ov1_t*` twice and the assembly suite's three pathways four
  times, so the position effect is measured in two families rather than across many.
- **And the metric is the corpus's**: the last task is never forgotten after it is taught, so its gain is a `learned`
  difference.
- *And a ledger is not a mechanism.*
