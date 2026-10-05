# The game card at revision 5: the trade written in, and what it is made of

*2026-10-05. `experiments/e424_the_game_card_revision_five.py` writes the closed-loop benchmark's card at **revision
5**. Three clauses are added -- the **trade** at both ends of the budget, the **terms** it is made of, and the **arm
terms** -- each read from the artifact that measured it, and every other field is checked equal to `e418`'s revision 4
rather than restated. No training and no roll. Five claims, registered before this unit read any of them.*

## 1. What revision 5 adds

| clause | carried | read from |
|---|---|---|
| **trade** | **12** far-point cells with the newest task cost in **12**, the oldest recovered by **+0.2333** to **+0.3219**, the loss **0.0115** to **0.1031**, the coverage at least **5.48**; at twenty updates **13** cells with the newest cost in **8** and the oldest recovered by at most **+0.0750** | **`e420`, `e421`** |
| **terms** | the oldest task's learning term exactly **0.0** and the newest task's retention term exactly **0.0** over **12** cells, the middle retention at least **3.99** times its learning price | **`e422`** |
| **arm terms** | the buffer's retention over the penalty's is **7.13** to **9.75** times, with the two learning prices **0.0344** apart | **`e423`** |

The other fifteen fields -- the substrate, loop, protocol, metrics, arms, absence list, the world, stream, recovery and
invariance clauses, the buffer's own clause and draw terms, and the penalty clause -- are carried equal.

| claim | measured | verdict |
|---|---|---|
| AZ1 the fourth revision is carried unchanged where it is not rewritten | **15** fields equal, revision now **5** | **MET** |
| AZ2 and the trade clause is `e420`'s far point | 12 cells, 12 cost, **+0.2333**, **5.48** | **MET** |
| AZ3 and its near point is `e421`'s | 13 cells, **8** cost, at most **+0.0750** | **MET** |
| AZ4 and the terms clause is `e422`'s | both structural zeros, ratio at least **3.99** | **MET** |
| AZ5 and the arm terms clause is `e423`'s | **7.13** times the retention, **0.0344** the price gap | **MET** |

## 2. What the fifth revision says

**The card now says what an arm does, not only what it is worth.** Revisions 2 to 4 published the draw's clauses, the
buffer's ordering and the penalty's, each as a number per arm. Revision 5 publishes the ledger underneath: on twelve
draws the buffer's mean gain of **+0.1330** to **+0.1594** is a recovery of **+0.2333** to **+0.3219** on the oldest
task against a loss of **0.0115** to **0.1031** on the newest, every time; at twenty updates the newest task is cost
in only **8** of **13**; and the recovery is **entirely** retention while the loss is **entirely** a learning term.

**And it says what happens to the same trade under a different arm.** The penalty regularises toward the past too, but
buys **7.13** to **9.75** times less retention for the same learning price, so the ordering the card's penalty clause
carries at eleven and a half sigma is a difference in what the arms buy, not in what they spend.

**And the two ends of the budget are in one clause.** A reader can see that the aid at twenty updates is nearly free
because there is little to protect, and that at five hundred it has both a threefold recovery and a universal price.
The card no longer reports a single number per arm at a single budget.

## 3. What it cannot settle

- **A card is a definition and not a result**: it states what the benchmark is and points at the artifacts for every
  number.
- **And the trade is one arm pair on one order**: the `naive`/`replay` pair at five hundred and twenty updates in the
  as-built order, with the penalty measured on one cell only.
- **And the clauses are only checked against each other**: AZ1 shows revision 4 survives into revision 5 and not that
  revision 4 was right.
- *And a clause is not an experiment.*
