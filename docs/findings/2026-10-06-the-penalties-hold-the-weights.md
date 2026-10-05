# The penalties hold the weights and spend the drift on the bias: the two parameters separate the arms

*2026-10-06. `experiments/e433_the_penalties_hold_the_weights.py` globs `runs/`, skips the second executions the
corpus's own rule collapses, and for every artifact carrying `naive` beside another arm with a drift of the recurrent
weights and a final distance of the bias from zero on both, takes the arm's drift over the baseline's and its bias over
the baseline's -- pooled by arm, with the cell-by-cell joint pattern: weights held and bias pushed. `e431` read the
bias side of these cells and `e432` the corpus's interference account; this reads the weights beside the bias. No
training, no probe. Five claims, registered before this unit's pass over the corpus.*

## 1. The two parameters, arm by arm

**207 cells over 159 artifacts and 4 arms**, with 24 second executions collapsed.

| arm | cells | mean drift ratio | cells holding the weights | mean bias ratio | cells pushing the bias | both |
|---|---|---|---|---|---|---|
| **`ewc`** | 33 | **0.718** | **90.9%** | **1.508** | 93.9% | **90.9%** |
| **`ewc-block`** | 24 | **0.751** | **83.3%** | **1.473** | 100.0% | **83.3%** |
| **`ewc-block-rand`** | 19 | **0.752** | **78.9%** | **1.456** | 94.7% | **78.9%** |
| **`replay`** | 131 | 0.984 | 73.3% | **0.946** | 21.4% | **5.3%** |

*Both* is the share of cells in which the arm's drift is below the baseline's **and** its bias above it.

| claim | measured | verdict |
|---|---|---|
| BI1 the ledger is carried | **207** cells over **159** artifacts and **4** arms, **131** the buffer's | **MET** |
| BI2 and every penalty holds the weights | **78.9%** to **90.9%** of their cells | **MET** |
| BI3 and by a wide margin | mean drift ratios **0.718**, **0.751**, **0.752** | **MET** |
| BI4 and the two parameters move opposite ways in a penalty's cells | **78.9%** to **90.9%** | **MET** |
| BI5 and that is not the buffer's pattern | **5.3%** of its cells | **MET** |

## 2. What the two parameters say

**The two parameters order the arms oppositely.** Pooled over the corpus's cells the penalty arms' drift ratios are
**0.718**, **0.751** and **0.752**, and their bias ratios are **1.508**, **1.473** and **1.456**: an arm that
regularises toward a basis holds the recurrent weights where they are and leaves the bias to make the movement. The
buffer moves both less than the arm that does nothing (**0.984** and **0.946**), which is the same statement from the
other side -- the arm that stores is the arm that disturbs the parameters least.

**And the cell-by-cell pattern is the penalties' and not the buffer's.** Weights held and bias pushed together holds in
**90.9%**, **83.3%** and **78.9%** of the three penalties' cells against **5.3%** of the buffer's, so the joint pattern
is not a coincidence of the two marginals: on a penalised arm the two movements are the same event.

**And it is the parameter signature of the channel `e432` read.** `e432` found the corpus's own interference account
reading the penalised arms mostly through the bias (**0.76** to **0.98** of the first-order term) against the
unpenalised arm's **0.40** to **0.49**; this says why the account sees that -- the penalty's displacement *is* the
bias's movement, because the weights are held -- and `e431`'s ordering on the bias distance is the same ordering seen
from the other end.

## 3. What it cannot settle

- **A ratio is not a mechanism**: where the parameters end is two readings of one trajectory, and this unit intervenes
  on neither, so the ordering is a co-movement.
- **And the cells are not independent**: the corpus's artifacts include several executions of one configuration, so the
  shares are over the corpus as it stands rather than over independent samples.
- **And the drift is the corpus's own aggregate**: the recorded `theta_drift` is per task and its definition is the
  runner's, so a ratio here is of that reading and not of the displacement itself.
- **And the baseline is the same arm in each cell**: the ratios are per cell, so a cell whose baseline is small
  contributes a large ratio and the mean is over ratios rather than over distances.
- *And a ledger is not a mechanism.*
