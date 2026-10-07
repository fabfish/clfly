# The game card at revision 12: the head clause, the three heads of one world, and the correction revision 11 needed

*2026-10-07. `experiments/e459_the_game_card_revision_twelve.py` adds one clause to the card and checks every other field
rather than quoting it. `e458` held the card's world's **width** and moved its **source** -- the circuit's own neurons at
the card's own **eight** columns -- and the biological anchor's newest-task price came back at **-0.0615** and **4.48**
sigma, against **-0.0115** at **0.78** at thirty-two. **So the card's eleventh revision carries a reading its own numbers
do not support**, and the card has no clause with three heads of one world in it. Five claims, registered before this
unit's pass over the three rolls, with every number recomputed from the runs.*

## 1. The clause

| the head reads | width | the anchor's standing over `naive` | sigma | its newest-task cost | sigma |
|---|---|---|---|---|---|
| the world's own state | **8** | -0.0302 | 1.77 | **-0.1177** | **3.71** |
| the circuit's own neurons | **32** | +0.0187 | 1.03 | -0.0115 | **0.78** |
| the circuit's own neurons | **8** | **+0.0017** | **0.12** | **-0.0615** | **4.48** |

| the buffer over `naive` by position | first | middle | last | over the anchor |
|---|---|---|---|---|
| the world's state, 8 | +0.2896 | +0.2490 | -0.0604 | +0.1896 (10.89σ) |
| the neurons, 32 | +0.2323 | +0.1812 | -0.0302 | +0.1090 (7.66σ) |
| **the neurons, 8** | **+0.3281** | **+0.2958** | **-0.0833** | **+0.1785** (10.48σ) |

| claim | measured | verdict |
|---|---|---|
| DF1 the eleventh revision is carried where it is not rewritten | **25** fields equal, the revision now **12** | **MET** |
| DF2 and the clause's numbers come out of the three rolls | every head, standing, price, gain and sigma agrees to a thousandth | **MET** |
| DF3 and the price's presence is the width's | **3.71** and **4.48** at the two eight-column heads, **0.78** at the wide one | **MET** |
| DF4 and the anchor's standing is unresolved at all three heads | **1.77**, **1.03** and **0.12** sigma | **MET** |
| DF5 and the buffer's advantage holds at all three heads | first gains **+0.2896**, **+0.2323**, **+0.3281**; over the anchor **10.89**, **7.66**, **10.48** sigma | **MET** |

## 2. What the clause says, and what it corrects

**The clause corrects the reading its own predecessor carries, which is the first time a revision has had to.** Revision
11's `readout` clause carries four cells and the correct numbers, and its finding read them as *the read-out separates
the two anchors' prices*; `e458` then separated the read-out into its two dials and found the **width** doing the
separating and the **source** not. Revision 12 says so in the card: the price resolves at **both** eight-column heads --
one reading the world's state (**3.71** sigma) and one the circuit's neurons (**4.48**) -- and not at the thirty-two
column one (**0.78**). A reader of revision 11 alone would attribute the presence of that price to the head's **source**,
and the two clauses together attribute it to the head's **width**, which is `e286`'s axis and `e448`'s and `e449`'s, read
now under a second source.

**And the anchor's whole-diagonal standing is the one thing about that arm that no head moves.** It reads **-0.0302**,
**+0.0187** and **+0.0017** at **1.77**, **1.03** and **0.12** sigma -- a span of **0.0319** across a fourfold width and
two sources, and the smallest number this line has recorded for either anchor on any head. So the clause carries both
numbers for all three heads because they behave differently: the price is a function of the width and the standing is a
function of nothing this line has moved.

**And the buffer's advantage is largest at the narrow neuron head on two of its three positions.** Its first and middle
gains are **+0.3281** and **+0.2958** against **+0.2896**/**+0.2490** and **+0.2323**/**+0.1812**, its newest-task cost is
the largest at **-0.0833**, and its advantage over the anchor is **+0.1785** at **10.48** sigma against **+0.1896** at
**10.89** and **+0.1090** at **7.66**. So the two arms' standings move in opposite directions as the head narrows: the
anchor's goes to **0.12** sigma and the buffer's to its largest three positions, which is the stability-plasticity trade
read at its two ends on one world.

**And every number in the clause is recomputed rather than quoted, and the chain is twelve revisions long.** DF2 takes
the three runs' replicate lists and recomputes each head, standing, price, gain and sigma to a thousandth of a point;
DF1 checks that revision 11 survives into revision 12 in all **25** of its fields. So a revision now carries a correction
of a reading and a verification of the numbers it corrects, which is what the card's own form demands once its clauses
begin to be read against each other rather than one at a time.

## 3. What it cannot settle

- **Three heads of one world**: the card's own, so other worlds and the corpus's other suites are not in the clause.
- **And one corner is missing**: the world's state at thirty-two columns is not constructible, because
  `--readout-from-world` makes the head's input the world's state, so the **width** is measured at two widths under one
  source and the **source** at one width under two -- and the two dials are therefore not crossed in the clause.
- **And one cell each**: the card's world at twenty replicates, so a price at **0.78** sigma against one at **4.48** is a
  pair two redraws could narrow, and the fourth head that would bound the threshold between eight and thirty-two columns
  is not here.
- **And a clause is not a result**: DF1 shows revision 11 survives into revision 12 and not that revision 11 was right --
  and this revision is the first whose content is that a clause of its own was **read** the wrong way rather than that a
  number in it was wrong.
