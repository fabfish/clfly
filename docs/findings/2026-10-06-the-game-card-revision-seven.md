# The game card at revision 7: the parameters clause, where each arm spends its movement

*2026-10-06. `experiments/e434_the_game_card_revision_seven.py` writes the closed-loop benchmark's card at **revision
7**. One clause is added -- the **parameters** each arm moves, and the channel the corpus's own interference account
reads it through -- read from the three artifacts that measured them, and every other field is checked equal to
`e428`'s revision 6 rather than restated. No training and no roll. Five claims, registered before this unit read any of
them.*

## 1. What revision 7 adds

| the clause | over **207** cells, read from | |
|---|---|---|
| **bias ratio** | **0.9461** `replay`, **1.4556** `ewc-block-rand`, **1.4734** `ewc-block`, **1.5076** `ewc` | `e431` |
| **bias below share** | **78.6%** `replay`, **5.3%** `ewc-block-rand`, **0.0%** `ewc-block`, **0.0%** `ewc` | `e431` |
| **drift ratio** | **0.9838** `replay`, **0.7184** `ewc`, **0.7507** `ewc-block`, **0.7520** `ewc-block-rand` | `e433` |
| **joint share** | **5.3%** `replay`, **78.9%** `ewc-block-rand`, **83.3%** `ewc-block`, **90.9%** `ewc` | `e433` |
| **channel bias share** | `cell`: `naive` **0.40 0.49**, `replay` **0.43 0.41**, `ewc-block` **0.76 0.90**; `pair/plastic`: `naive` **0.45 0.44**, `ewc` **0.98 0.92**, `ewc-block` **0.65 0.63**, `ewc-block-rand` **0.61 0.68**, `replay` **0.59 0.74** | `e432` |
| **the frozen side** | **0.0** | `e432` |

The other twenty fields -- the substrate, loop, protocol, metrics, arms, absence list, the world, stream, recovery and
invariance clauses, the buffer clause and draw terms, the penalty clause, and the trade, terms, arm-terms, order and
controls clauses -- are carried equal.

| claim | measured | verdict |
|---|---|---|
| BJ1 the sixth revision is carried unchanged where it is not rewritten | **20** fields equal, revision now **7** | **MET** |
| BJ2 and the clause's bias half is `e431`'s | the four ratios and four below-shares equal the ledger's | **MET** |
| BJ3 and its weights half is `e433`'s | the four drift ratios equal that ledger's | **MET** |
| BJ4 and its joint half is `e433`'s | the four joint shares equal it | **MET** |
| BJ5 and its channel half is `e432`'s | both rolls' shares and the control's **0.0** equal it | **MET** |

## 2. What the seventh revision says

**The card now says where each arm spends its movement.** The bias ratio orders the arms one way (**0.9461** for the
buffer, **1.4556** to **1.5076** for the penalties) and the drift ratio orders them the other (**0.9838** against
**0.7184** to **0.7520**), so a reader can see from the card alone that the penalties hold the recurrent weights and
leave the bias to make the movement while the buffer moves both less than the arm that does nothing.

**And it says how tightly the two movements are one event.** Weights held and bias pushed together holds in **90.9%**,
**83.3%** and **78.9%** of the three penalties' cells against **5.3%** of the buffer's, so the joint share is not a
coincidence of two marginals.

**And it says which channel the corpus's own instrument reads.** The interference account's bias share is **0.76** and
**0.90** for the penalty on the card's world and **0.98**, **0.92** for the diagonal penalty on the plastic pair,
against **0.40**, **0.49** and **0.45**, **0.44** for the arms that are not penalised, with the frozen side at its own
**0.0**. The clause carries the two ledgers side by side and they agree cell for cell on the bias ratio, so a revision
that moves either number turns the unit red.

## 3. What it cannot settle

- **A card is a definition and not a result**: it states what the benchmark is and points at the artifacts for every
  number.
- **And the clause is the corpus's own aggregates**: the ratios are per cell over cells that are not independent
  samples, and the drift is the runner's per-task reading rather than the displacement itself.
- **And the clauses are only checked against each other**: BJ1 shows revision 6 survives into revision 7 and not that
  revision 6 was right.
- **And the clause says where the parameters go and not why**: the ordering is a co-movement, and no unit here
  intervenes on either parameter.
- *And a clause is not an experiment.*
