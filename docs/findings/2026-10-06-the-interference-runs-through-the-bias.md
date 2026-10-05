# The interference runs through the bias for the arms that are penalised and through the weights for the arm that is not

*2026-10-06. `experiments/e432_the_interference_runs_through_the_bias.py` reads the corpus's own one-line interference
account -- the gradient of a task's loss at the final body against the displacement that task experienced, split into
the half taken over the recurrent weights and the half taken over the bias -- on three rolls: the card's world with
`naive`, `ewc-block` and `replay` in one run at twenty replicates, and the plastic/frozen-bias pair at forty, whose
frozen side makes every bias displacement zero. `e427`, `e430` and `e431` found the bias carrying three quarters of the
buffer's worth and the penalties displacing it furthest; this reads the corpus's instrument on that split. No training,
no probe. Five claims, registered before this unit's pass over the runs.*

## 1. The account, split

| roll | arm | weight half 0/1 | bias half 0/1 | whole-body 0/1 | bias share |
|---|---|---|---|---|---|
| **card's world, 20 reps** | `ewc-block` | +0.1410 +0.0792 | **+0.4352 +0.7086** | +0.5762 +0.7878 | **0.76 0.90** |
| | `naive` | **+0.7185 +0.6277** | +0.4713 +0.6037 | +1.1898 +1.2314 | 0.40 0.49 |
| | `replay` | +0.3960 +0.2945 | +0.2971 +0.2045 | +0.6931 +0.4990 | 0.43 0.41 |
| **pair, frozen bias, 40 reps** | `ewc` | +0.0108 +0.0326 | **0.0000 0.0000** | +0.0108 +0.0326 | 0.00 0.00 |
| | `ewc-block` | +0.0914 +0.0435 | **0.0000 0.0000** | +0.0914 +0.0435 | 0.00 0.00 |
| | `ewc-block-rand` | +0.1261 +0.0646 | **0.0000 0.0000** | +0.1261 +0.0646 | 0.00 0.00 |
| | `naive` | +0.2142 +0.1087 | **0.0000 0.0000** | +0.2142 +0.1087 | 0.00 0.00 |
| | `replay` | +0.0004 +0.0007 | **0.0000 0.0000** | +0.0004 +0.0007 | 0.00 0.00 |
| **pair, plastic bias, 40 reps** | `ewc` | +0.0052 +0.0280 | **+0.3204 +0.3195** | +0.3257 +0.3474 | **0.98 0.92** |
| | `ewc-block` | +0.1594 +0.0920 | +0.2987 +0.1534 | +0.4581 +0.2453 | 0.65 0.63 |
| | `ewc-block-rand` | +0.1605 +0.1204 | +0.2517 +0.2549 | +0.4122 +0.3753 | 0.61 0.68 |
| | `naive` | +0.2336 +0.1474 | +0.1930 +0.1139 | +0.4266 +0.2614 | 0.45 0.44 |
| | `replay` | +0.0004 +0.0004 | +0.0005 +0.0012 | +0.0009 +0.0017 | 0.59 0.74 |

| claim | measured | verdict |
|---|---|---|
| BH1 the ledger is carried | **3** rolls at **20** and **40** replicates, both halves per task per arm | **MET** |
| BH2 and the control's own reading is zero | the frozen side's bias half at most **0.00e+00**, its weight half at most **2.14e-01** | **MET** |
| BH3 and every penalty's interference runs mostly through the bias | every penalty above the baseline on both tasks of both live runs, **10** comparisons | **MET** |
| BH4 and the diagonal penalty's is above 0.9 | **0.9839** and **0.9195** | **MET** |
| BH5 and the buffer's whole term is below the baseline's | **6 of 6** task comparisons | **MET** |

## 2. What the split says

**Which channel the forgetting runs through is the arm's.** On the card's world the penalty's bias share is **0.76** and
**0.90** where the arm that does nothing is at **0.40** and **0.49**; on the plastic pair the diagonal penalty's is
**0.98** and **0.92**, the block penalty's **0.65** and **0.63**, and the matched random control's **0.61** and
**0.68**, against the baseline's **0.45** and **0.44**. So the corpus's own instrument reads the unpenalised arm mostly
through the weights and every penalised arm mostly through the bias -- the same arms `e431` found displacing the bias
furthest, and on the parameter `e427` found three quarters of the aid in.

**And the control validates the split by construction.** With the bias frozen, the bias half is **exactly 0.0000** on
every arm and every task at forty replicates while the weight half is not, which is what `e139` built the split to
show: a share of zero on the control's side rules out the possibility that the bias term is an artefact of the
arithmetic.

**And the buffer's whole term is the smallest of the three families on every task.** It is below the baseline's on
**six of six** task comparisons across the three rolls -- **0.6931** and **0.4990** against **1.1898** and **1.2314** on
the card's world, and **0.0009** and **0.0017** against **0.4266** and **0.2614** on the plastic pair. Its own share is
not a reading: its two halves are of comparable size but three orders of magnitude below the baseline's on the pair, so
the unit makes no claim about which channel the buffer's interference runs through.

## 3. What it cannot settle

- **Three rolls and one instrument**: the account is the corpus's own first-order form, and `e109` found its
  second-order term non-monotone while `e336` found the update direction not reproducible at five replicates, so a
  share here is a share of that one-line reading and not of the forgetting itself.
- **And a frozen bias zeroes one channel by construction**: BH2 is the control validating the split and not a
  measurement.
- **And the buffer's own share is noise**: its two halves are comparable (0.43 and 0.41 on the card's world, 0.59 and
  0.74 on the plastic pair) but far below the baseline's in magnitude, so the unit claims nothing about it.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned.
- *And a decomposition is not a mechanism.*
