# The budget curve at thirty-two columns: the width does not move the crossing, and it does move the approach

*2026-10-08. `experiments/e468_the_budget_curve_at_thirty_two_columns.py` walks the same four budgets at **thirty-two
columns** that `e467` walked at eight -- four new rolls at **200** and **350** updates, both anchors, twenty replicates
each, read beside `e466`'s **100** and `e455`'s and `e456`'s **500** -- so the crossing can be compared across a
fourfold width. Four claims, all four **MET**.*

## 1. The two rungs

| thirty-two columns | | | | | | |
|---|---|---|---|---|---|---|
| the anchor | updates | its standing | sigma | its newest-task cost | sigma | the buffer over it | sigma |
| `ewc-block` | 100 | **-0.0243** | 1.74 | **-0.0479** | **2.65** | +0.1309 | 7.00 |
| `ewc-block-rand` | 100 | -0.0424 | **2.00** | -0.0729 | 4.18 | +0.1490 | 7.51 |
| `ewc-block` | 200 | **-0.0556** | **3.28** | **-0.0885** | **7.16** | +0.1542 | 8.48 |
| `ewc-block-rand` | 200 | -0.0437 | 2.08 | -0.0781 | 5.90 | +0.1424 | 6.36 |
| `ewc-block` | 350 | **-0.0017** | **0.10** | -0.0312 | 2.08 | +0.1132 | 6.28 |
| `ewc-block-rand` | 350 | **+0.0003** | **0.02** | -0.0385 | 2.71 | +0.1111 | 6.42 |
| `ewc-block` | 500 | **+0.0187** | 1.03 | -0.0115 | 0.78 | +0.1090 | 7.66 |
| `ewc-block-rand` | 500 | +0.0104 | 0.59 | -0.0323 | 2.77 | +0.1174 | 7.50 |

| the biological anchor's standing | 100 | 200 | 350 | 500 |
|---|---|---|---|---|
| at 8 columns, `e467` | -0.0483 | -0.0378 | -0.0243 | +0.0017 |
| at 32 columns, this unit | **-0.0243** | **-0.0556** | **-0.0017** | **+0.0187** |
| the signs, both rungs | -1 | -1 | -1 | **+1** |

| the pair apart at thirty-two columns | 100 | 200 | 350 | 500 |
|---|---|---|---|---|
| their newest-task costs | **0.0250** | 0.0104 | 0.0073 | 0.0208 |
| their standings | 0.0181 | 0.0119 | 0.0020 | 0.0083 |

| claim | measured | verdict |
|---|---|---|
| UA1 the new rolls are one configuration with the budget moved | **102** fields compared, **4** cells at **20** replicates, read-out **32** held | **MET** |
| UA2 and the sign changes once at thirty-two columns too | **-0.0243**, **-0.0556**, **-0.0017**, **+0.0187**; signs **-1, -1, -1, +1**, one change | **MET** |
| UA3 and the width does not move the crossing | **-1, -1, -1, +1** at both **32** and **8** columns | **MET** |
| UA4 and the pair's prices are alike at thirty-two columns | **0.0250**, **0.0104**, **0.0073**, **0.0208**, every one within **0.05** | **MET** |

## 2. What the second rung says

**The crossing is between the same two budgets at both widths.** The biological anchor's sign sequence is **-1, -1,
-1, +1** at thirty-two columns exactly as it is at eight, so a fourfold wider head crosses between **350** and **500**
updates as the narrow one does, and `e467`'s *one width* is closed: the place is the head's and not the rung's.

**And the approach is not.** At eight columns the standing **decays monotonically** (**-0.0483**, **-0.0378**,
**-0.0243**, **+0.0017**); at thirty-two it **deepens first and then collapses** (**-0.0243**, **-0.0556**,
**-0.0017**, **+0.0187**). So the sentence the two rungs agree on is about **which** two budgets the sign changes
between, and the sentence they disagree on is about the shape of the walk to it -- and **the deepest point of the whole
line is the thirty-two column, two-hundred-update cell**: **-0.0556** at **3.28** sigma, the largest standing and the
most resolved one any unit of this corpus has measured on this world.

**And at three hundred and fifty updates neither partition is distinguishable from `naive` on the diagonal.** The
biological anchor reads **-0.0017** at **0.10** sigma and the matched-random one **+0.0003** at **0.02**, so the two
anchors agree with each other and with the baseline, and the pair's standing gap is **0.0020**, the smallest of the
four budgets. **So the null `e462` and `e463` read at the far point is reached earlier at the wider rung**, and the far
point's own **+0.0187** is a partial return rather than the end of the decay.

**And the price's magnitude is not monotone at thirty-two columns either.** It runs **0.0479**, **0.0885**, **0.0312**
then **0.0115** for the biological anchor, deepest at two hundred updates as the standing is, and **0.0729**,
**0.0781**, **0.0385** then **0.0323** for the matched-random one. So both columns of this rung share the shape the
eight-column rung gives to neither: a maximum at two hundred updates.

**And the pair's prices are alike at every budget on both rungs, but the gaps are not the same.** At thirty-two columns
the four gaps are **0.0250**, **0.0104**, **0.0073** and **0.0208** and at eight they are **0.0448**, **0.0021**,
**0.0146** and **0.0021**; the widest is at the **first** budget on the narrow rung and at the first budget on the wide
one too, but the wide rung's is half the narrow one's and its second budget is five times the narrow one's. So *the pair
is alike everywhere* holds on both and *to the same degree* does not.

**And the buffer is ahead on both rungs at every budget, and its advantage is smaller at the wider head.** It reads
**+0.1090** to **+0.1542** at thirty-two columns against **+0.1326** to **+0.2111** at eight, at **6.28** to **8.48**
sigma against **7.60** to **15.00**: the wide rung's buffer advantage is between a fifth and a half smaller and its
resolution is between a third and a half lower, which is the same direction `e458` and `e462` found for a single budget.

## 3. What it cannot do

- **Two rungs are not the ladder**: **8** and **32** are fourfold apart and **16** and **24** are not measured at the
  intermediate budgets, so *the width does not move the crossing* is two points of a curve and not a constant.
- **And four budgets are still not a mechanism**: the corpus carries no run that separates the update count from the
  training it buys, so a crossing and a maximum are places on a dial and not causes.
- **And one cell each**: the card's world at twenty replicates, so the deepest cell's **3.28** sigma and the flat cell's
  **0.10** are what a redraw could move.
- **And one partition draw**: the matched-random cells are one draw of the same group sizes, so the random anchor's
  curve is one sample of its family.
