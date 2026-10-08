# The held-out task at a fifth of the budget: the reading is bought early, and the rest of the budget adds nothing it can resolve

*2026-10-08. `experiments/e471_the_held_out_task_at_a_fifth_of_the_budget.py` moves the budget and holds the task: two
rolls of `e469`'s configuration at **100 updates** -- the flag's world does not depend on the update count, so the
held-out cue set is the **same** cue set -- read beside `e469`'s two at 500. Four claims: **XA1, XA2 and XA4 MET** and
**XA3's falsifier FIRED**.*

## 1. The two budgets

| the budget | the arm | the initial body | the trained body | the change | sigma | against the baseline | sigma |
|---|---|---|---|---|---|---|---|
| 100 | `naive` | 0.6875 | **0.7594** | **+0.0719** | **4.89** | -- | -- |
| 100 | `ewc-block` | 0.6875 | **0.7198** | +0.0323 | 1.51 | -0.0396 | -1.76 |
| 100 | `ewc-block-rand` | 0.6875 | **0.7448** | +0.0573 | 4.38 | -0.0146 | -0.73 |
| 100 | `replay` | 0.6875 | **0.7438** | +0.0563 | 3.76 | -0.0156 | -0.90 |
| 500 | `naive` | 0.6875 | **0.7719** | **+0.0844** | **10.11** | -- | -- |
| 500 | `ewc-block` | 0.6875 | **0.7625** | +0.0750 | 9.00 | -0.0094 | -0.86 |
| 500 | `ewc-block-rand` | 0.6875 | **0.7667** | +0.0792 | 8.54 | -0.0052 | -0.40 |
| 500 | `replay` | 0.6875 | **0.7677** | +0.0802 | 6.84 | -0.0042 | -0.29 |

| the baseline's trained reading, 100 against 500 | paired difference | sigma |
|---|---|---|
| both rolls | **+0.0125** | **0.89** |

| claim | measured | verdict |
|---|---|---|
| XA1 the two budgets are one configuration with the update count moved | **102** fields compared, **4** rolls at **20** replicates, the same held-out cue set with the same counts | **MET** |
| XA2 and the sequence raises the decodability at a fifth of the budget too | **+0.0719** at **4.89** sigma on both rolls | **MET** |
| XA3 and the trained reading grows with the budget | **+0.0125** at **0.89** sigma | **FALSIFIER FIRED** |
| XA4 and the anchoring does not move it at either budget | **-0.73** to **-1.76** sigma | **MET** |

## 2. What the second budget says

**Five sixths of the held-out reading is bought in the first fifth of the sequence.** The baseline's probe goes
**0.6875** to **0.7594** at a hundred updates -- a paired **+0.0719** at **4.89** sigma -- and from there to five
hundred it adds **+0.0125**, which at **0.89** sigma is not resolved. **So the card's `holdout` clause carries a number
the budget barely moves after its first fifth**, and what the remaining four hundred updates buy is a change this unit
cannot separate from a redraw.

**And the reading is bought *earlier than the sequence's own ledger* is finished.** `e467` put the biological anchor's
diagonal penalty crossing zero between **350** and **500** updates, and `e468` found the same at thirty-two columns --
so at a hundred updates, where the held-out reading is already at **0.7594**, the sequence's own diagonal is still
**-0.0483** at **2.21** sigma. The two axes are therefore not the same axis: what makes the unseen cue set readable
arrives in the first fifth and the penalty's decay takes the whole budget.

**And the anchors cost more at the small budget than at the far one, without either resolving.** The biological
anchor's trained reading is **0.0396** below the baseline's at **-1.76** sigma at a hundred updates and **0.0094** below
at **-0.86** at five hundred, and the matched-random one **0.0146** then **0.0052**: the direction is the same at both
budgets and the size is fourfold larger at the small one, so the `basis` clause's null is not a null at every budget
either -- it is a null this unit's twenty replicates cannot resolve, and the widest of these is **-1.76** sigma.

**And the buffer's own change is smaller at the small budget too.** `replay`'s probe goes **+0.0563** at **3.76** sigma
at a hundred updates against **+0.0802** at **6.84** at five hundred, and the anchor's **+0.0323** at **1.51** does not
resolve at all -- so at a fifth of the budget the two arms that add a penalty or a buffer are *less* readable on the
unseen cue set than the baseline, in the same direction as they are at the far point but further.

**And the two budgets are one configuration with one field moved.** All **102** compared fields agree except the update
count, the output path and the saved weights, the held-out cue set's name is `loop_holdout` on all four rolls and its
counts are **96** and **48** on every arm of every one of them -- so the difference between the two columns above is
the budget and nothing else, and the same cue set is being read at both.

## 3. What it cannot do

- **Two budgets are not a curve**: **100** and **500** are one pair, and the budgets between them -- where the
  **+0.0125** must actually arrive -- are not measured.
- **And a probe is not a task**: both readings are of **linear readability** from the body and not of what the
  sequence's method would learn if the held-out task were trained.
- **And one held-out draw**: the fourth cue set is the flag's own draw, so a redraw of it is not measured.
- **And one ridge**: **1e-2** is `e469`'s and not the benchmark's, and a different one would move both columns.
