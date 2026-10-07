# The game card at revision 13: the pair clause, and the six cells of one world's head table

*2026-10-07. `experiments/e461_the_game_card_revision_thirteen.py` adds one clause to the card and checks every other
field rather than quoting it. `e458` and `e460` completed the fifth cell of the card's world's head table, so the pair is
now measured at **all three heads** -- `ewc-block` and `ewc-block-rand` at the world's own state in eight columns, at the
circuit's neurons in thirty-two, and at the neurons in eight -- and revision 12's `head` clause carries **one** arm's
numbers there while the headline question is the **pair**'s. Five claims, registered before this unit's pass over the
six rolls, with every number recomputed from the runs.*

## 1. The clause

| the head reads | width | the anchor | its standing over `naive` | sigma | its newest-task cost | sigma |
|---|---|---|---|---|---|---|
| the world's own state | 8 | `ewc-block` | -0.0302 | 1.77 | **-0.1177** | **3.71** |
| the world's own state | 8 | `ewc-block-rand` | -0.0365 | **2.16** | **-0.1135** | **4.49** |
| the circuit's own neurons | 32 | `ewc-block` | +0.0187 | 1.03 | **-0.0115** | **0.78** |
| the circuit's own neurons | 32 | `ewc-block-rand` | +0.0104 | 0.59 | **-0.0323** | **2.77** |
| the circuit's own neurons | 8 | `ewc-block` | +0.0017 | 0.12 | **-0.0615** | **4.48** |
| the circuit's own neurons | 8 | `ewc-block-rand` | -0.0271 | 1.80 | **-0.0594** | **4.18** |

| the pair apart by head | the world's 8 | the neurons' 32 | the neurons' 8 |
|---|---|---|---|
| their newest-task costs | **0.0042** | **0.0208** | **0.0021** |
| their standings | **0.0063** | **0.0083** | **0.0288** |
| the basis contrast on the diagonal | +0.0063 (0.36σ) | +0.0083 (0.49σ) | +0.0288 (**1.70**σ) |

| claim | measured | verdict |
|---|---|---|
| DH1 the twelfth revision is carried where it is not rewritten | **26** fields equal, the revision now **13** | **MET** |
| DH2 and the clause's numbers come out of the six rolls | every head, standing, price and basis contrast agrees to a thousandth | **MET** |
| DH3 and the pair's prices agree at the eight-column heads and not at the wide one | **0.0042** and **0.0021** against **0.0208** | **MET** |
| DH4 and the pair's standings separate at the narrow neuron head and not at the wide one | **0.0288** against **0.0083** | **MET** |
| DH5 and the basis contrast is a null on the diagonal at all three heads | **0.36**, **0.49** and **1.70** sigma | **MET** |

## 2. What the clause says

**The pair is separated by the head only where the number read is the price, and the head that separates it is the wide
one.** The two anchors' newest-task costs agree to **0.0042** on the world's own state and to **0.0021** at the neurons'
eight, and separate to **0.0208** at the neurons' thirty-two -- so **the wide head is where the two arms look least like
one another and where both look least like buffers**, which is `e448`'s and `e449`'s width axis read on the pair. Their
**standings** do the opposite: **0.0063**, **0.0083** and **0.0288**, the widest at the **narrow neuron** head, so a
reader who asks *does the basis matter on this world* gets a different answer depending on which of the two numbers they
take and at which head.

**And the clause carries the basis contrast and the pair's standing gap as one number, which is worth saying plainly.**
The contrast on the diagonal is by construction the difference of the two standings, so DH5 and DH4 are **the same
quantity read twice** and this unit's fourth and fifth claims are not independent -- they are the clause's two names for
one fact. The card carries it once, as `basis_accuracy`, beside the six standings it is the difference of; the pair clause
should be read as five claims about four quantities and not as five about five.

**And the clause's own table is the answer to the question the corpus was built on, at six cells.** The basis contrast --
the biological cell-class partition against its size-matched random one -- is **+0.0063**, **+0.0083** and **+0.0288** at
**0.36**, **0.49** and **1.70** sigma, so it is a null at every head this line has put the pair on, and the largest of the
three is the one at the narrow neuron head where the pair's standings are the widest apart. Eleven corpus-wide audits and
now six cells of this world say the same thing: **which basis anchors does not move the diagonal, at any head.**

**And the chain is thirteen revisions long with every one verified against the roll it was read from.** DH2 takes the six
runs' replicate lists and recomputes each standing, each price and each basis contrast to a thousandth of a point; DH1
checks that revision 12 survives into revision 13 in all **26** of its fields. So the card's account of its own world is
now six cells over three heads for two arms, with the two corrections revisions 11 and 12 had to make already in it.

## 3. What it cannot settle

- **Six cells of one world**: the card's own, so other worlds and the corpus's other suites are not in the clause.
- **And two widths are not a ladder**: the eight-column heads differ from the thirty-two column one by a factor of four,
  and the widths between them are not measured, so *the wide head separates the pair's prices* is one step and not a
  trend.
- **And one cell each**: the card's world at twenty replicates, so a gap at **0.0021** against one at **0.0208** is a
  pair two redraws could narrow.
- **And one partition draw**: the matched-random cells are one draw of the same group sizes, so the three basis contrasts
  are three readings of one draw and not of the population.
