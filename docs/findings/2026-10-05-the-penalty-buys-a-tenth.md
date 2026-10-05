# The penalty buys a tenth of the retention: both arms' trade split on one run

*2026-10-05. `experiments/e423_the_penalty_buys_a_tenth.py` splits **both** arms of the one cell that carries all three
-- the card's world at five hundred updates, `naive`, `ewc-block` and `replay` in a single run at twenty replicates,
the cell `e415` read -- into a **learning** term and a **retention** term against the same baseline, on the same seeds.
`e422` split the buffer's gain on the twelve draws; this asks what the penalty buys and what it pays on that cell's own
run. No training, no probe. Five claims, registered before this unit's pass over the run.*

## 1. The two arms' terms

| arm | learned 0/1/2 | retention 0/1/2 | gain 0/1/2 |
|---|---|---|---|
| `naive` | 0.7917 0.8292 0.8469 | 0.4542 0.3656 0.0000 | 0.3375 0.4635 0.8469 |
| **`ewc-block`** | +0.0000 **-0.0750** -0.0771 | **+0.0292** **+0.0406** +0.0000 | **+0.0292** **-0.0344** -0.0771 |
| **`replay`** | +0.0000 **-0.0406** -0.0865 | **+0.2844** **+0.2896** +0.0000 | **+0.2844** **+0.2490** -0.0865 |

The `naive` row is the arm's own per-task readings; the other two rows are each arm's terms against it.

| claim | measured | verdict |
|---|---|---|
| AX1 the ledger is carried | one artifact, **three** arms, **20** replicates, three per-task readings each | **MET** |
| AX2 and the penalty buys retention too | **+0.0292** and **+0.0406** at the two older tasks | **MET** |
| AX3 and the two arms pay about the same price | the widest learning gap is **0.0344** | **MET** |
| AX4 and the buffer buys at least five times the retention | **9.75** and **7.13** times | **MET** |
| AX5 and only the buffer's trade pays | the penalty's middle gain is **-0.0344** against the buffer's **+0.2490** | **MET** |

## 2. What the two arms say

**Both arms regularise toward the past; the buffer regularises ten times harder.** The penalty's retention terms are
**+0.0292** on the oldest task and **+0.0406** on the middle; the buffer's are **+0.2844** and **+0.2896**. So the
ordering `e415` measured at eleven and a half sigma on accuracy is here in its own terms: the same mechanism at
**9.75** and **7.13** times the size.

**And the two arms pay about the same price for it.** Their learning terms differ by **0.0344** at the middle task and
**0.0094** at the newest, so the difference in what they achieve -- **+0.0292** against **+0.2844** on the oldest,
**-0.0344** against **+0.2490** on the middle -- is a difference in what they buy and not in what they spend. The
penalty's middle trade is a net **loss**: it keeps **+0.0406** more of an older task and learns the next one **-0.0750**
worse, so it does not pay.

**And the buffer's own price is the newest task, as `e422` found on the twelve draws.** Both arms pay there
(**-0.0865** and **-0.0771**) and neither forgets it (**0.0000** retention on both), so the last task's level is the
thing an arm spends, whichever arm it is.

## 3. What it cannot settle

- **One cell, one strength and one penalty**: the card's world at `lam = 1.0` with `ewc-block`, so the `lam` ladder,
  the diagonal penalty and the other draws are not in this reading, and `e416`'s corpus-wide ledger is not either.
- **And the cell's world predates the coupling**: `e415` reported that the card's world's run records the coupling and
  this artifact carries no such field.
- **And the two arms share a run but not a mechanism**: the split says what each arm changed, not how.
- **And the decomposition is the corpus's**: the retention term is the diagonal-minus-last-row reading, which `e305`
  showed cannot see the part an arm never learned.
- *And a decomposition is not a mechanism.*
