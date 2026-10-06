# The ledger at a narrower world: eight columns is a peak, and at four the anchor's standing resolves for the first time

*2026-10-07. `experiments/e449_the_ledger_at_a_narrower_world.py` reads the card's world at **half its width**. `e448`
doubled it and found the two arms separating -- the buffer's ledger held while the anchor's newest-task cost fell from
**-0.1177** at **3.71** sigma to **-0.0292** at **1.68** -- and named its own first gap, that a width of sixteen is one
point on an axis. The corpus has a direction for the other end: `e292` found the share of the variance the read-out
explains rising from a median of **0.637** to **1.160** between the narrow and wide ends of its ladder. This unit drives
`e438`'s configuration with `--loop-world-dims 4` alone differing, at the same three arms and twenty replicates. Five
claims, registered before the new run's reading was opened.*

## 1. Three widths of the card's world

| the world's width | the buffer's first | its middle | its last | its mean diagonal | the anchor's mean diagonal | its newest task |
|---|---|---|---|---|---|---|
| **4** | +0.2115 | +0.2271 | **-0.0750** | **+0.1212** (8.60σ) | **-0.0271** (**2.29**σ) | **-0.0937** (2.81σ) |
| **8** (the card) | **+0.2896** | +0.2490 | -0.0604 | **+0.1594** (**11.97**σ) | -0.0302 (1.77σ) | **-0.1177** (**3.71**σ) |
| **16** | +0.2500 | +0.2135 | -0.0667 | +0.1323 (9.29σ) | +0.0073 (0.44σ) | -0.0292 (1.68σ) |

| the baseline `naive` | its mean diagonal | over the 0.25 chance |
|---|---|---|
| 4 columns | **0.4493** | **+0.1993** |
| 8 columns | 0.5191 | +0.2691 |
| 16 columns | 0.5191 | +0.2691 |

| claim | measured | verdict |
|---|---|---|
| CA1 the run is one configuration with the world narrowed | `loop_world_dims` moved 8 to 4, **50** fields, the task names held, each read-out the world's own | **MET** |
| CA2 and the world is still learnable | the baseline is **+0.1993** over chance | **MET** |
| CA3 and the buffer's ledger holds at the first position | **+0.2115** | **MET** |
| CA4 and the anchor's price is larger at four columns than at eight | **-0.0937** against the card's **0.1177** | **NULL** |
| CA5 and the anchor's whole-diagonal standing still does not resolve | **-0.0271** at **2.29** sigma | **FALSIFIER FIRED** |

## 2. What the third width says

**Eight columns is a peak, and it is the peak the card is played at.** Of the six numbers above, five are largest at
eight: the buffer's first-position gain (**0.2896** against **0.2500** and **0.2115**), its margin (**0.3500** against
**0.3167** and **0.2865**), its mean-diagonal contrast (**0.1594** against **0.1323** and **0.1212**), the anchor's
newest-task cost (**-0.1177** against **-0.0937** and **-0.0292**) and that cost's sigma (**3.71** against **2.81** and
**1.68**). CA4 registered the corpus's prediction that the narrow end amplifies and it came back a **null**: the price at
four columns is **-0.0937**, between the unit's floor of **0.06** and the card's **0.1177**, so the narrow end does not
amplify either and `e292`'s monotone does not appear on this world. **The card's clause is therefore a statement about
the width the card is played at and not about a range of them**, and a reader who wants to know how much of the ledger
is a width's now has three points rather than one.

**And at four columns the anchor's standing resolves for the first time in seven rolls.** Its mean diagonal over the
baseline is **-0.0271** at **2.29** sigma -- under the bar's magnitude at eight columns (**-0.0302**) but over the
bar -- so CA5's falsifier fired on a claim whose whole content was that this number has never resolved. Read beside
`e448`, the two ends say different things about the same arm: at sixteen columns it has **no** resolved effect at all
(**0.44** sigma on the diagonal and **1.68** on the price), and at four it has a resolved **deficit** of **-0.0271**.
So the arm is not switched off by width in one direction and on in the other; **eight columns is where its price is
largest and four is where its accuracy deficit is the only one of the three that clears two sigma**, and neither of
the two ends is a monotone continuation of the middle.

**And the narrower world is still a game.** The baseline reads **0.4493**, **+0.1993** over chance and **0.0698** below
the card's, so the task survives being read off four numbers; the buffer's ledger holds on all three positions and
resolves at **8.60** sigma on the diagonal, and the arms' forgetting ordering is unchanged (**naive** 0.3276,
`ewc-block` 0.2958, `replay` 0.0901 against the card's 0.3750, 0.3276, 0.0906). A world that could not hold the task
would have made CA2 the unit's subject; it is the unit's **floor**, registered before the others, and it passed.

**And the width moves the environment the way `e448` found it does at the other end.** The three **world** fingerprints
changed and the **cue, action and feedback** populations were held, which is `e448`'s partition and the mirror of
`e444`'s: the pool the populations are drawn from is the decoder's and the maps are the world's, and a change of width is
a change of the maps at either end of the axis.

## 3. What it cannot settle

- **Three widths** -- four, eight and sixteen -- so a peak at eight is three points and not a curve, and the two inner
  widths that would bracket it are not here.
- **And a width is not a decoder**: narrowing the world changes what the three tasks are as well as how many columns the
  decoder has, so the baseline's own **0.0698** of lost accuracy is part of what the three columns cost.
- **And one cell**: the card's world at twenty replicates, so the other five draws and the three streams are not in the
  reading, and a standing at **2.29** sigma is the kind of number a redraw could put under the bar.
- **And one run**: no second order, no redraw and no matched-random arm at four columns, so whether the **basis**
  contrast survives a narrowing -- the corpus's headline -- is not measured, and `e448`'s "cannot settle" says the same
  of a widening.
