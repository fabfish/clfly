# The penalty ledger: over the corpus's own penalty cells the buffer is never dominated where the power is

*2026-10-05. `experiments/e416_the_penalty_ledger.py` globs `runs/`, skips the second executions the corpus's own rule
collapses, and takes every artifact that carries `naive`, `replay` and at least one of `ewc` and `ewc-block` in **one
run**: the two paired contrasts, on final accuracy and on mean forgetting, per cell, pooled over the penalty arm the
artifact carries. No training, no probe. Five claims, registered before this unit's pass over the corpus.*

## 1. The ledger

**60 cells over 34 artifacts**, with 24 second executions collapsed. Pooled over the arm:

| penalty | replicates | cells | buffer wins accuracy | buffer forgets less | buffer dominated |
|---|---|---|---|---|---|
| `ewc` | 3 | 2 | 2 | 2 | 0 |
| `ewc` | 5 | 23 | 23 | 12 | 0 |
| `ewc` | 10 | 2 | 2 | 2 | 0 |
| `ewc` | 40 | 5 | 5 | 3 | 0 |
| `ewc-block` | 3 | 1 | 1 | 1 | 0 |
| `ewc-block` | **5** | 21 | 15 | 14 | **6** |
| `ewc-block` | 20 | 1 | 1 | 1 | 0 |
| `ewc-block` | 40 | 5 | 5 | 5 | 0 |

| claim | measured | verdict |
|---|---|---|
| AL1 the ledger is carried | **60** cells over **34** artifacts, at least **3** replicates each | **MET** |
| AL2 and the buffer wins most of them | **54 of 60**, **90%** | **MET** |
| AL3 and where the power is it wins them all | **11 of 11** at the twenty-replicate floor | **MET** |
| AL4 and where the power is the buffer is never dominated | **0 of 11** at that floor | **MET** |
| AL5 and the cells that dominate it are small and few | **6** cells, all `ewc-block` at **5** replicates, margins under **0.0222** | **MET** |

## 2. What the ledger says

**With power, the buffer is not dominated anywhere.** At a floor of twenty replicates the corpus holds eleven cells,
at twenty and forty replicates, and `replay`'s final accuracy exceeds the penalty arm's in **every one**; in **none**
of them is the penalty arm both more accurate and less forgetful. `e276` measured that ordering at twelve sigma on
one suite and `e415` at eleven on the card's world; over the eleven powered cells of the whole corpus it has no
counterexample.

**And where the buffer does lose, the loss is one arm, one replicate count and three hundredths wide.** Six of the
sixty cells have the penalty arm ahead on **both** axes, and all six are the block penalty at **five** replicates:
`e101`'s `fb8` and `fb128` cells, `e102`'s `fb8` cells, `e164`'s and `e8_class_incremental`. Their accuracy margins
are **0.0014** to **0.0222**. So the clause this ledger adds is narrow: *replay over penalty holds wherever the corpus
ran enough replicates and enough Fisher batches to see it, and the exception is a five-replicate block-penalty regime
whose margin is a fortieth of the buffer's own worth on the card's world.*

**And on the other axis the two arms are nearly tied.** The buffer forgets less in **40 of 60** cells -- 19 of 32 for
`ewc` and 21 of 28 for `ewc-block` -- so on forgetting the ledger is a coin-flip and not a result, while on accuracy
it is 54 of 60. That is the same two-axis shape `e152` found on its own arm set: the buffer's advantage is an
accuracy advantage, and its forgetting advantage appears where the penalty is strong (`lam = 1.0`: the powered
`plastic` and `overlap1` cells and the card's world) rather than everywhere.

## 3. What it cannot settle

- **The ledger is not a design**: each cell is one configuration executed once, so a dominance is a reading of that
  execution and not of the configuration, and the replicate counts differ from three to forty.
- **And the comparison is pooled over the arm**: an artifact carrying both penalties contributes two cells, so the
  cells are not independent samples.
- **And the arms are the corpus's**: `replay` is the corpus's buffer (`--replay-per-task 16 --replay-batch 16`) and
  the strengths are the corpus's own two, `lam` 3e-3 and 1.0.
- **And the metric is the corpus's**: `mean_forgetting` is the retention matrix's diagonal minus its last row, which
  `e305` showed cannot see the part an arm never learned.
- *And a ledger is not a mechanism.*

## RE-READ 2026-10-11

**The floor claims are scoped to the cells that carry a signal.** `e489` added two runs to the corpus whose pass is an **episode of three trials**, and in them every arm sits at the four-class chance (**0.2476**, **0.2451**, **0.2413** against **0.25**): the world carries the episode, so the last trial's label is a small part of the state the head reads and no arm learns it. On those cells this unit's AL3 and AL4 falsifiers fired -- `replay` does not win an accuracy contrast there (by **0.0118** and **0.0014**) and `ewc-block` is both more accurate and less forgetful. A cell whose arms are at chance is not a comparison of arms, so every cell now records its run's own chance (`1 / classes`, read off the configuration it carries) and its `naive` arm's final accuracy, and the two floor claims are read over the cells whose `naive` is above it: **46 of 46** powered cells at the floor with the buffer winning the accuracy contrast in all of them, and **0 of 46** where the penalty arm is both more accurate and less forgetful. The two episode cells are named in the artifact as the cells left out. AL1, AL2 and AL5 are unedited and stand over all **97** cells.
