# The game card at revision 9: the width clause, and the ledger that peaks where the difficulty does not

*2026-10-07. `experiments/e450_the_game_card_revision_nine.py` adds one clause to the card and checks every other field
rather than quoting it. Revision 8 carried the **ledger** clause -- the buffer's three-position gain over the baseline
and the anchor's newest-task price, over the four rolls of the card's own world that `e437` to `e444` drove -- and every
one of those rolls, with `e446`'s and `e447`'s, was taken at **eight columns**. `e448` doubled the width and found the
two arms separating; `e449` halved it and found the ledger peaks at eight. Both named the same gap, that the card's
clause is a statement about the width the card is played at. Five claims, registered before this unit's pass over the
three rolls -- and as `e440` stated his, **CW2 and CW3 are confirmatory**, the rolls' numbers being published in `e448`'s
and `e449`'s findings already.*

## 1. The clause

| the world's width | the baseline `naive` | the buffer's first | its margin | its mean diagonal | the anchor's mean diagonal | its newest task |
|---|---|---|---|---|---|---|
| **4** | 0.4493 | +0.2115 | +0.2865 | +0.1212 (8.60σ) | **-0.0271** (**2.29**σ) | **-0.0937** (2.81σ) |
| **8** (the card's own) | 0.5191 | **+0.2896** | **+0.3500** | **+0.1594** (**11.97**σ) | -0.0302 (1.77σ) | **-0.1177** (**3.71**σ) |
| **16** | **0.5705** | +0.2500 | +0.3167 | +0.1323 (9.29σ) | +0.0073 (0.44σ) | -0.0292 (1.68σ) |

**`width`, the clause revision 9 writes**: the three widths **4**, **8** and **16** with **8** the card's own; the three
rolls' artifacts; each width's baseline diagonal; the buffer's first-position gain, first-over-last margin, mean-diagonal
contrast and its sigma; and the anchor's mean-diagonal contrast and newest-task cost with their sigmas.

| claim | measured | verdict |
|---|---|---|
| CW1 the eighth revision is carried where it is not rewritten | **22** fields equal, the revision now **9** | **MET** |
| CW2 and the clause's numbers come out of the three rolls | every number recomputed agrees to a thousandth of a point | **MET** |
| CW3 and five of the six numbers peak at the card's own width | first-position gain, margin, buffer diagonal, anchor's newest-task magnitude and its sigma all peak at **8** | **MET** |
| CW4 and the sigmas separate the two ends | the price clears 2σ at 4 and 8 and not at 16; the standing only at 4 | **MET** |
| CW5 and the clause names the widths and the rolls | **4**, **8**, **16** with 8 the card's own, three artifacts, the rolls' own baselines | **MET** |

## 2. What the clause says

**The card now carries how much of its own headline is a width's, and the answer is that the headline was taken at the
width where it is largest.** The buffer's first-position gain (**0.2896** against **0.2500** and **0.2115**), its margin
(**0.3500** against **0.3167** and **0.2865**), its mean-diagonal contrast (**0.1594** against **0.1323** and
**0.1212**), the anchor's newest-task cost (**-0.1177** against **-0.0937** and **-0.0292**) and that cost's sigma
(**3.71** against **2.81** and **1.68**) all peak at the card's own eight columns. Read with the `ledger` clause, the
card says that its ledger was measured where the ledger is largest -- which is a fact a reader of a benchmark's headline
needs and which no clause carried before this one.

**And the peak is not the difficulty's, which the clause's own table shows and neither `e448` nor `e449` printed.** The
baseline's diagonal rises monotonically with the width -- **0.4493**, **0.5191**, **0.5705** -- so the wider world is
**easier** for the arm that does nothing and the narrower one is harder, while the ledger's size peaks in the middle. The
arm differences are therefore not a monotone function of the task's difficulty: a world at sixteen columns is the easiest
of the three to read and the one where the anchor has no resolved effect at all (**0.44** sigma on the diagonal and
**1.68** on the price), and a world at four is the hardest and the one where the anchor's accuracy deficit resolves
(**2.29**). What the width moves is not how hard the task is but how much of it the world's own state carries.

**And the two ends are the two halves of the anchor.** At sixteen columns it is absent: **0.44** and **1.68** sigma, no
resolved effect in any of the three currencies this line reads it in. At four it is present as a **deficit**:
**-0.0271** at **2.29** sigma on the whole diagonal, the only roll in eight where that number clears the bar. And at
eight it is present as a **price**: **-0.1177** at **3.71**, its largest. So the card's clauses about that arm are three
statements about three widths, and a reader who takes the `ledger` clause alone would read the price as the arm's
property rather than as the width's.

**And every number in the clause is recomputed rather than quoted.** CW2 takes the three runs' replicate lists, recomputes
the paired contrasts and compares to a thousandth of a point; CW3 reads the peak off the clause's own numbers and CW4
reads its own sigmas against the two-sigma bar. So a revision that moves the clause without moving the rolls fails, which
is the property `e434` established for the parameters clause and `e445` for the ledger's.

## 3. What it cannot settle

- **Three widths**: four, eight and sixteen are three points and not a curve, so the clause carries a peak at eight and
  not the shape of one, and the integers between them are not measured.
- **And a width is not a decoder**: narrowing or widening the world changes what the three tasks are as well as how many
  columns the decoder has, so part of the clause's spread is the task's and CW2's own numbers cannot separate it.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  clause, and the anchor's **2.29** sigma at four columns is the kind of number a redraw could put under the bar.
- **And one arm pair**: no matched-random arm at four or sixteen columns, so whether the corpus's headline **basis**
  contrast survives a widening or a narrowing is not in this clause, which both `e448` and `e449` also closed on.
