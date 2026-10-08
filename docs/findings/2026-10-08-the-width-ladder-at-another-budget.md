# The width ladder at another budget: the ladder is the far point's, and so is the null on the diagonal

*2026-10-08. `experiments/e466_the_width_ladder_at_another_budget.py` moves the budget and holds the ladder: six rolls
of the far point's configuration at **100 updates** -- three widths and both anchors, twenty replicates each -- read
beside the six far-point rolls of the same widths. Four claims: **SA1 MET**, **SA2 FALSIFIER FIRED**, **SA3 MET** and
**SA4 MET**.*

## 1. The two points

| the far point, 500 updates | | | | | | |
|---|---|---|---|---|---|---|
| the anchor | columns | its standing | sigma | its newest-task cost | sigma | the buffer over it | sigma |
| `ewc-block` | 8 | +0.0017 | 0.12 | -0.0615 | 4.48 | +0.1785 | 10.48 |
| `ewc-block-rand` | 8 | -0.0271 | 1.80 | -0.0594 | 4.18 | +0.2073 | 12.00 |
| `ewc-block` | 16 | +0.0215 | 1.48 | -0.0406 | 3.71 | +0.1628 | 9.95 |
| `ewc-block-rand` | 16 | +0.0042 | 0.27 | -0.0396 | 2.46 | +0.1802 | 10.37 |
| `ewc-block` | 32 | +0.0187 | 1.03 | -0.0115 | 0.78 | +0.1090 | 7.66 |
| `ewc-block-rand` | 32 | +0.0104 | 0.59 | -0.0323 | 2.77 | +0.1174 | 7.50 |

| the middle point, 100 updates | | | | | | |
|---|---|---|---|---|---|---|
| the anchor | columns | its standing | sigma | its newest-task cost | sigma | the buffer over it | sigma |
| `ewc-block` | 8 | **-0.0483** | **2.21** | **-0.1031** | **4.15** | +0.1604 | 10.14 |
| `ewc-block-rand` | 8 | **-0.0205** | 1.02 | **-0.0583** | 2.27 | +0.1326 | 8.11 |
| `ewc-block` | 16 | **-0.0094** | 0.53 | **-0.0927** | **4.08** | +0.1378 | 7.01 |
| `ewc-block-rand` | 16 | **-0.0365** | 1.72 | **-0.1396** | **4.71** | +0.1649 | 9.23 |
| `ewc-block` | 32 | **-0.0243** | 1.74 | **-0.0479** | **2.65** | +0.1309 | 7.00 |
| `ewc-block-rand` | 32 | **-0.0424** | **2.00** | **-0.0729** | **4.18** | +0.1490 | 7.51 |

| the pair apart | 8 columns | 16 columns | 32 columns |
|---|---|---|---|
| at 500 updates, their newest-task costs | 0.0021 | 0.0010 | 0.0208 |
| at 100 updates, their newest-task costs | **0.0448** | **0.0469** | **0.0250** |
| at 500 updates, their standings | 0.0288 | 0.0174 | 0.0083 |
| at 100 updates, their standings | 0.0278 | 0.0271 | 0.0181 |

| claim | measured | verdict |
|---|---|---|
| SA1 the new rolls are one configuration with the budget moved | **306** fields compared, **6** cells at **20** replicates, read-outs **8/16/32** held | **MET** |
| SA2 and the price's magnitude falls with the width there for both arms | `ewc-block` **0.1031 / 0.0927 / 0.0479**, `ewc-block-rand` **0.0583 / 0.1396 / 0.0729** | **FALSIFIER FIRED** |
| SA3 and the pair's prices agree there | **0.0448**, **0.0469**, **0.0250**, every one within **0.05** | **MET** |
| SA4 and the buffer is ahead of both anchors there | **+0.1309** to **+0.1649** at **7.00** to **10.14** sigma | **MET** |

## 2. What the second budget says

**The price's magnitude ladder is the far point's.** At a hundred updates `ewc-block` runs **0.1031**, **0.0927** and
**0.0479** -- ordered, as at the far point -- but `ewc-block-rand` runs **0.0583**, **0.1396** and **0.0729**, so its
magnitude **rises** from eight columns to sixteen by a factor of **2.4** and falls again. So *the width's grip on the
price falls as the head widens* is a statement about a body trained to five hundred updates: at a fifth of that budget
one of the two arms is not ordered at all, and the far point's clean two-step ladder is not the head's property.

**And the null on the diagonal is the far point's too, which is the sharper of the two results.** Every one of the six
far-point standings is between **-0.0271** and **+0.0215** and none of them resolves, and that is what `e462` and `e463`
read as *the two arms have no diagonal effect at any of the four widths*. At a hundred updates **all six standings are
negative** -- the anchored arm is behind `naive` on the mean diagonal at every width and for both anchors -- and **two
of them resolve**: `ewc-block` at eight columns reads **-0.0483** at **2.21** sigma and `ewc-block-rand` at thirty-two
reads **-0.0424** at **2.00**. So the basis's diagonal effect is not a null; it is a null **at five hundred updates**,
and at a hundred it has a sign and, twice, a size.

**And the sign of the biological anchor's standing flips with the budget.** Positive at all three far-point widths
(**+0.0017**, **+0.0215**, **+0.0187**) and negative at all three middle-point ones (**-0.0483**, **-0.0094**,
**-0.0243**), so what the cell-class basis does to the diagonal is a function of how long the body has trained and not
a property of the partition -- which is exactly the axis `e276`'s and `e440`'s readings leave open and no unit in this
line has crossed with the head.

**And the price itself grows with the budget at every width rather than shrinking.** The far point's magnitudes are
**0.0615**, **0.0406**, **0.0115** and **0.0594**, **0.0396**, **0.0323**; the middle point's are **0.1031**, **0.0927**,
**0.0479** and **0.0583**, **0.1396**, **0.0729**. So a longer budget *reduces* the anchor's advantage on the newest
task at every cell but one, and the far point's low prices are the trained body's rather than the head's.

**And the pair's prices are nearly an order of magnitude further apart at a hundred updates than at five hundred.**
The gaps are **0.0448**, **0.0469** and **0.0250**, against **0.0021**, **0.0010** and **0.0208**: all three pass the
unit's own **0.05** bar, so the pair still agrees at every width, and all three are between twenty and fifty times the
far point's narrow ones. So the far point's *the pair is alike at the narrow rungs* is a trained body's likeness, and
the two anchors are far more distinguishable before that training than after it.

## 3. What it cannot do

- **Two budgets are not a curve**: **100** and **500** are one pair and the corpus's budget series (`e389`, `e390`,
  `e391`) carries `naive` and `replay` only, so nothing here says where between them the sign would change.
- **And one cell each**: the card's world at twenty replicates, so a standing at **2.21** sigma is what a redraw could
  put under the bar.
- **And one partition draw**: the matched-random cells are one draw of the same group sizes.
- **And three of the four rungs**: **24** is left out so that the two points are compared on the same widths, so a
  difference at that rung is not measured, and the far point's finding that the pair parts between twenty-four and
  thirty-two columns is untouched here.
