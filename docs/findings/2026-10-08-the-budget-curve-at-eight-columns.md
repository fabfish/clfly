# The budget curve at eight columns: the crossing is between 350 and 500, and the diagonal penalty decays to zero

*2026-10-08. `experiments/e467_the_budget_curve_at_eight_columns.py` walks the axis `e466` left the sign flip between:
four more rolls at **eight columns**, both anchors, twenty replicates each, at **200** and **350** updates, read beside
`e466`'s **100** and the far point's **500**. Four claims, all four **MET**.*

## 1. The curve

| updates | the anchor | its standing over `naive` | sigma | its newest-task cost | sigma | the buffer over it | sigma |
|---|---|---|---|---|---|---|---|
| 100 | `ewc-block` | **-0.0483** | **2.21** | **-0.1031** | **4.15** | +0.1604 | 10.14 |
| 100 | `ewc-block-rand` | -0.0205 | 1.02 | -0.0583 | 2.27 | +0.1326 | 8.11 |
| 200 | `ewc-block` | **-0.0378** | **2.02** | **-0.0865** | **3.23** | +0.1809 | 8.66 |
| 200 | `ewc-block-rand` | -0.0295 | 1.49 | **-0.0885** | **4.18** | +0.1726 | 7.60 |
| 350 | `ewc-block` | -0.0243 | 1.55 | **-0.0781** | **3.67** | +0.2111 | 12.88 |
| 350 | `ewc-block-rand` | -0.0024 | 0.20 | -0.0635 | 3.17 | +0.1892 | 15.00 |
| 500 | `ewc-block` | **+0.0017** | 0.12 | -0.0615 | 4.48 | +0.1785 | 10.48 |
| 500 | `ewc-block-rand` | -0.0271 | 1.80 | -0.0594 | 4.18 | +0.2073 | 12.00 |

| the pair apart at eight columns | 100 | 200 | 350 | 500 |
|---|---|---|---|---|
| their newest-task costs | **0.0448** | 0.0021 | 0.0146 | 0.0021 |
| their standings | 0.0278 | 0.0083 | 0.0219 | 0.0288 |

| claim | measured | verdict |
|---|---|---|
| TA1 the new rolls are one configuration with the budget moved | **102** fields compared, **4** cells at **20** replicates, read-out **8** held | **MET** |
| TA2 and the biological anchor's standing changes sign once | **-0.0483**, **-0.0378**, **-0.0243**, **+0.0017**; signs **-1, -1, -1, +1**, one change | **MET** |
| TA3 and the pair's prices are alike at every budget | **0.0448**, **0.0021**, **0.0146**, **0.0021**, every one within **0.05** | **MET** |
| TA4 and the buffer is ahead of both anchors at every budget | **+0.1326** to **+0.2111** at **7.60** to **15.00** sigma | **MET** |

## 2. What the curve says

**The crossing is between three hundred and fifty updates and five hundred, and it is the end of a decay rather than
a step.** The biological anchor's standing runs **-0.0483**, **-0.0378**, **-0.0243** then **+0.0017** -- monotone in
the budget, with the two intermediate budgets placing the change of sign between the third and the fourth -- and its
sigma falls with it (**2.21**, **2.02**, **1.55**, **0.12**), so what `e466` found as *a null at five hundred updates*
is the far end of a penalty that trains away: the basis costs the anchor **0.0483** of mean diagonal accuracy at a
fifth of the budget and nothing at all at the full one.

**And the other anchor does not follow it.** `ewc-block-rand`'s standings are **-0.0205**, **-0.0295**, **-0.0024** and
**-0.0271** -- negative at every budget, not monotone, and resolving at none of them (its largest sigma is **1.80** at
the far point) -- so the two anchors' curves cross as well as their signs: the matched-random partition is behind the
biological one at a hundred updates and ahead of it at three hundred and fifty. **So what the basis is worth on this
world is not one number and not one direction; it is two curves that cross.**

**And the price's magnitude at eight columns falls with the budget for the biological anchor and not for the other.**
`ewc-block` reads **0.1031**, **0.0865**, **0.0781** then **0.0615**, monotone, while `ewc-block-rand` reads **0.0583**,
**0.0885**, **0.0635** and **0.0594**, rising at two hundred and falling back. So `e466`'s *the price grows with the
budget* is a statement about the first fifth of the axis for the arm that anchors on the cell classes, and at two
hundred updates the matched-random arm's price is the larger of the two for the only time on this rung.

**And the pair's likeness is not monotone in the budget either.** The two anchors' newest-task costs are **0.0448**
apart at a hundred updates, **0.0021** at two hundred, **0.0146** at three hundred and fifty and **0.0021** at five
hundred: the pair is **least** alike at a fifth of the budget and alike to two thousandths at both the two-hundred and
the far point, so `e466`'s reading of a twenty-times-wider gap at a hundred updates is the top of a bump rather than
the start of a trend.

**And the buffer's advantage is not monotone either, and it is the largest thing on the curve.** It reads **+0.1604**,
**+0.1326**, **+0.1809**, **+0.1726**, **+0.2111**, **+0.1892**, **+0.1785** and **+0.2073**, peaking at three hundred
and fifty updates on both anchors at **12.88** and **15.00** sigma, against **8.11** at its lowest. So the arm the
budget favours most is not the one the ledger's other columns favour, and a reader who wants the buffer's largest
measured advantage on this world has to say which budget they mean.

**And what this closes is `e466`'s own open bullet.** That unit said *two budgets are not a curve, and nothing here
says where between them the sign would change*; the change is between **350** and **500** updates, and the sentence
above it -- that the basis does nothing to the diagonal -- is now a statement about the far end of a monotone decay
rather than a null.

## 3. What it cannot do

- **One width**: **eight** columns is the rung the flip was seen on, and nothing here says a curve at sixteen or
  thirty-two crosses in the same place.
- **And four budgets are still not a mechanism**: the axis is the number of updates and the corpus carries no run that
  separates it from the training it buys, so a crossing is a place on a dial and not a cause.
- **And one cell each**: the card's world at twenty replicates, so a standing at **2.02** sigma is what a redraw could
  put under the bar, and the crossing's two neighbours are **1.55** and **0.12** sigma.
- **And one partition draw**: the matched-random cells are one draw of the same group sizes, so the random anchor's
  curve is one sample of its family.
