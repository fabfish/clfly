# The front page's second region: the parameters clause, checked against the card

*2026-10-06. `experiments/e435_the_front_pages_second_region.py` adds a second marked region to `README.md` -- the
numbers of the card's **parameters** clause at revision 7, which `e431` to `e434` measured -- and reads it back against
`runs/e434_the_game_card_revision_seven.json`, the way `e429` does for the first region. It re-runs `e429`'s own check
on that first region rather than quoting it. No training and no probe. Five claims, registered before this unit's pass
over the README and the card.*

## 1. What the second region carries

| clause | number on the page | the card's own |
|---|---|---|
| the cells the parameters are pooled over | 207 | 207 |
| the buffer's bias ratio | 0.9461 | 0.9461 |
| the diagonal penalty's bias ratio | 1.5076 | 1.5076 |
| the buffer's drift ratio | 0.9838 | 0.9838 |
| the diagonal penalty's drift ratio | 0.7184 | 0.7184 |
| the buffer's cells with the weights held and the bias pushed | 0.0534 | 0.0534 |
| the diagonal penalty's cells with the weights held and the bias pushed | 0.9091 | 0.9091 |
| the diagonal penalty's bias share of the interference account | 0.9839 | 0.9839 |
| the unpenalised arm's bias share of the interference account | 0.4524 | 0.4524 |
| the frozen side's bias half | 0.0 | 0.0 |

| claim | measured | verdict |
|---|---|---|
| BK1 the region is carried and names its source | **10** rows of a **10**-label vocabulary, the artifact and revision **7** named | **MET** |
| BK2 and its bias and drift rows are the card's | the cells row and the four ratios equal the card's | **MET** |
| BK3 and its joint rows are the card's | the two joint shares equal the card's | **MET** |
| BK4 and its channel rows are the card's | the two interference shares and the frozen half equal the card's | **MET** |
| BK5 and the first region is still the card's | `e429`'s **21** rows and all **5** of its claims still hold | **MET** |

## 2. What the two regions do together

**The front page now says where each arm's movement goes, beside what the benchmark is worth.** The first region
carries the benchmark's own numbers -- the trade, the order, the controls -- and the second the parameter ledger behind
them: the buffer's bias ratio **0.9461** against the diagonal penalty's **1.5076**, the buffer's drift ratio
**0.9838** against the penalty's **0.7184**, and the joint share **0.0534** against **0.9091**. A reader can see from
the page alone that an arm which regularises toward a basis holds the recurrent weights where they are and leaves the
bias to make the movement.

**And the two regions are checked against the same card.** Every row of both is compared with the artifact that
carries it, so a revision that moves a number cannot leave the page behind: the second region points at `e434`'s card
and the first at `e428`'s, and this unit re-runs the first region's own five claims rather than taking them on trust --
they come back **MET** with **21** rows.

**And the front page's existing text is untouched.** The scope blockquote at the top, which `e307` reads, is
byte-identical, and the unit's live test asserts that both regions' markers and that blockquote are all still there.

## 3. What it cannot settle

- **A front page is not a result**: the region summarises the clause and the clause summarises its artifacts.
- **And the region is one table**: it carries the ten numbers this unit's vocabulary holds, not every number of the
  clause, so a new number arrives on the page only when the vocabulary grows with it.
- **And the check is the unit's own**: the vocabulary, the tolerances and the marker syntax are this unit's choices, so
  a reader should take the region as a checked summary rather than as the clause.
- **And BK5 re-runs a sibling's check**: it shows `e429`'s reader still passes, not that its reading was ever the right
  one.
- *And a summary is not a benchmark.*
