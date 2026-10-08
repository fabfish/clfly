# The neuron read-out at twenty-four columns: the fourth rung breaks the standing ladder and holds the price one

*2026-10-07. `experiments/e463_the_neuron_readout_at_twenty_four_columns.py` drives the rung between the two `e462` left
the parting in: two rolls of the card's world's neuron head at **twenty-four** columns, the biological arm and the
matched-random one, twenty replicates each, with the six outer rolls recomputed rather than quoted. Five claims,
registered before either new roll's reading was opened, four **MET** and the fifth's **falsifier FIRED**.*

## 1. The four rungs

| columns | the anchor | its standing over `naive` | sigma | its newest-task cost | sigma | the buffer over it | sigma |
|---|---|---|---|---|---|---|---|
| 8 | `ewc-block` | +0.0017 | 0.12 | **-0.0615** | **4.48** | +0.1785 | 10.48 |
| 8 | `ewc-block-rand` | -0.0271 | 1.80 | **-0.0594** | **4.18** | +0.2073 | 12.00 |
| 16 | `ewc-block` | +0.0215 | 1.48 | **-0.0406** | **3.71** | +0.1628 | 9.95 |
| 16 | `ewc-block-rand` | +0.0042 | 0.27 | **-0.0396** | **2.46** | +0.1802 | 10.37 |
| 24 | `ewc-block` | **-0.0007** | **0.05** | **-0.0354** | **3.13** | +0.1163 | 6.74 |
| 24 | `ewc-block-rand` | **-0.0014** | **0.10** | **-0.0375** | **2.61** | +0.1170 | 9.93 |
| 32 | `ewc-block` | +0.0187 | 1.03 | **-0.0115** | **0.78** | +0.1090 | 7.66 |
| 32 | `ewc-block-rand` | +0.0104 | 0.59 | **-0.0323** | **2.77** | +0.1174 | 7.50 |

| the pair apart by rung | 8 | 16 | 24 | 32 |
|---|---|---|---|---|
| their newest-task costs | 0.0021 | 0.0010 | 0.0021 | **0.0208** |
| their standings | 0.0288 | 0.0174 | **0.0007** | 0.0083 |

| claim | measured | verdict |
|---|---|---|
| DJ1 the two rolls are one configuration with the arm list moved | **50** fields compared, **3** arms each at **20** replicates, read-out **24**, `naive` and `replay` bit-identical **2 of 2** | **MET** |
| DJ2 and both anchors' prices resolve at the new rung | **-0.0354** at **3.13** sigma and **-0.0375** at **2.61** | **MET** |
| DJ3 and the pair's prices still agree there | **0.0021** apart | **MET** |
| DJ4 and the price magnitude ladder holds for both arms | **0.0406 / 0.0354 / 0.0115** and **0.0396 / 0.0375 / 0.0323** | **MET** |
| DJ5 and the pair's standing gap is ordered there | **0.0007**, the **smallest** of the four, against **0.0174** below and **0.0083** above | **FALSIFIER FIRED** |

## 2. What the fourth rung says

**The standing gap is not monotone in the width, and `e462`'s monotone run of three was an accident of which three
widths were drawn.** The gaps run **0.0288**, **0.0174**, **0.0007** then **0.0083**: the fourth rung puts the pair
**closer together on the diagonal than any other rung this line has read**, and the three-rung fall `e462` reported was
a fragment of a curve with a minimum in the middle of it. **And the right statement is the one the sigmas always
supported**: every one of the eight standings is under two sigma (**0.12**, **1.80**, **1.48**, **0.27**, **0.05**,
**0.10**, **1.03**, **0.59**), so the two arms have no diagonal effect at any of the four widths and any ordering of
their gaps orders noise. At twenty-four columns both anchors land on zero together (**-0.0007** at **0.05** sigma and
**-0.0014** at **0.10**), which is the null reading of the whole ladder rather than one of its rungs.

**And the price's magnitude ladder does survive the fourth point for both arms, which is the difference between the two
numbers.** `ewc-block` reads **0.0615**, **0.0406**, **0.0354** then **0.0115** and `ewc-block-rand` **0.0594**,
**0.0396**, **0.0375** then **0.0323**, so the width's grip on the price falls monotonically for both arms at four
points while its grip on the standing is a null at four. **So the card's `pair` clause has one quantity that is a
function of the width and one that is not**, and that is a sharper statement than either three-point run could make.

**And the pair's prices part between twenty-four and thirty-two columns, not between sixteen and twenty-four.** The gaps
run **0.0021**, **0.0010**, **0.0021** and **0.0208**, so the three narrow rungs agree to a thousandth or two and the
wide one is twenty times the smallest of them. **And the two arms get there differently**: `ewc-block` falls **0.0209**,
**0.0052** then **0.0239** across the three steps, with a plateau at twenty-four, while `ewc-block-rand` falls
**0.0198**, **0.0021** then **0.0052** and loses most of its price in the first step. So the biological arm's price
is not a smooth function of the width either, and the two arms' price curves cross in their shape between sixteen and
thirty-two.

**And the buffer's advantage is a four-point ladder for the biological anchor and flat at the top for the other.** It
reads **+0.1785**, **+0.1628**, **+0.1163** then **+0.1090** over `ewc-block` -- falling at every step -- and
**+0.2073**, **+0.1802**, **+0.1170** then **+0.1174** over `ewc-block-rand`, whose last step rises by **0.0004** and
leaves it flat within a thousandth between twenty-four and thirty-two columns. **So of the three quantities the ladder
carries, one is monotone at four points for both arms, one is monotone for one arm, and one is a null for both.**

## 3. What it cannot settle

- **Four widths are not a mechanism**: **8**, **16**, **24** and **32** are one ladder of a dial whose setting also
  moves the head's parameter count, so four points are a shape and not a cause, and `e440`'s parameters are read on the
  earned label and not on this head.
- **And the new rung is one cell each**: the card's world at twenty replicates, so the **0.0007** gap and the
  **0.0021** price gap are differences a redraw could move, and they are read at **0.05** and **0.10** sigma.
- **And one partition draw**: the matched-random cells are one draw of the same group sizes, so the four rungs' random
  arms are four readings of one draw and not of the population.
- **And the source's axis stays one rung**: the world's own state is only constructible at eight columns, so the whole
  ladder is the circuit's own neurons and the width is not crossed with the source.

## RE-READ 2026-10-08: the null this unit found is the far point's

This finding's sharpest sentence -- *all eight standings are under two sigma, so the two arms have no diagonal effect at
any of the four widths and any ordering of their gaps orders noise* -- has a condition it does not name, and `e466`
supplied it: the ladder is measured at **500 updates**, which is `e438`'s `--iters` and what every rung of this line
inherits. At **100 updates** the same three widths give **six negative standings**, the anchored arm behind `naive` on
the mean diagonal at every width and for both anchors, and **two of them resolve** -- `ewc-block` at eight columns at
**-0.0483**, **2.21** sigma, and `ewc-block-rand` at thirty-two at **-0.0424**, **2.00**. The price's magnitude ladder
goes the same way: `ewc-block-rand`'s magnitudes there are **0.0583**, **0.1396** and **0.0729**, rising at the middle
rung. So *the basis does nothing to the diagonal* is a fact about a body trained to five hundred updates, and the sign
of the biological anchor's standing flips between the two budgets (**+0.0017**, **+0.0215**, **+0.0187** against
**-0.0483**, **-0.0094**, **-0.0243**). Every number below stands as what this unit measured at 500 updates; what is
withdrawn is the sentence's scope
(`docs/findings/2026-10-08-the-width-ladder-at-another-budget.md`).
