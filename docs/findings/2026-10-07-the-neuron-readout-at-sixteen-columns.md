# The neuron read-out at sixteen columns: the middle rung, and the two ladders the width runs

*2026-10-07. `experiments/e462_the_neuron_readout_at_sixteen_columns.py` drives the **middle rung** of the card's world's
neuron width: two rolls of `e458`'s configuration at **sixteen** columns, the biological arm and the matched-random one,
twenty replicates each, so each arm's price is read at three widths and the pair at four heads. The reader recomputes the
four outer cells from `e458`, `e460`, `e455` and `e456` rather than quoting them, and compares the two new rolls field
for field and record for record. Five claims, registered before either new roll's reading was opened, all five **MET**.*

## 1. The rungs

| columns | the anchor | its standing over `naive` | sigma | its newest-task cost | sigma | the buffer over it | sigma |
|---|---|---|---|---|---|---|---|
| 8 | `ewc-block` | +0.0017 | 0.12 | **-0.0615** | **4.48** | +0.1785 | 10.48 |
| 8 | `ewc-block-rand` | -0.0271 | 1.80 | **-0.0594** | **4.18** | +0.2073 | 12.00 |
| 16 | `ewc-block` | +0.0215 | **1.48** | **-0.0406** | **3.71** | +0.1628 | 9.95 |
| 16 | `ewc-block-rand` | +0.0042 | **0.27** | **-0.0396** | **2.46** | +0.1802 | 10.37 |
| 32 | `ewc-block` | +0.0187 | 1.03 | **-0.0115** | **0.78** | +0.1090 | 7.66 |
| 32 | `ewc-block-rand` | +0.0104 | 0.59 | **-0.0323** | **2.77** | +0.1174 | 7.50 |

| the pair apart by rung | the eight columns | the sixteen | the thirty-two |
|---|---|---|---|
| their newest-task costs | 0.0021 | **0.0010** | **0.0208** |
| their standings | **0.0288** | **0.0173** | **0.0083** |

| claim | measured | verdict |
|---|---|---|
| DI1 the two rolls are one configuration with the arm list moved | **50** fields compared, **3** arms each at **20** replicates, read-out **16**, `naive` and `replay` bit-identical **2 of 2** | **MET** |
| DI2 and both anchors' prices resolve at the middle rung | **-0.0406** at **3.71** sigma and **-0.0396** at **2.46** | **MET** |
| DI3 and the pair's prices agree at the middle rung | **0.0010** apart | **MET** |
| DI4 and the width's grip on each arm's price is a ladder | **0.0615 / 0.0406 / 0.0115** and **0.0594 / 0.0396 / 0.0323** | **MET** |
| DI5 and the buffer is ahead of both anchors at the middle rung | **+0.1628** at **9.95** sigma and **+0.1802** at **10.37** | **MET** |

## 2. What the middle rung says

**The pair's prices agree at the middle rung as they do at both eight-column heads, so the separation is the wide
rung's and not the width's.** The gaps run **0.0021**, **0.0010** and **0.0208**: a factor of twenty between the middle
and the wide reading, and the middle one is the **smallest** of the three. `e460` found the pair alike at both
eight-column heads and apart at thirty-two and left open whether the agreement was the eight columns' or the pair's; the
middle rung says at sixteen it is still the pair's, so what the wide head does is a property of that head and not of
*being wider than eight*.

**And the two arms' prices move together up to the middle rung and part company after it.** From eight columns to sixteen
the biological arm's price falls by **0.0209** and the matched-random arm's by **0.0198**, **0.0011** apart; from sixteen
to thirty-two the biological arm falls a further **0.0291** and the matched-random one only **0.0073**, **0.0218** apart.
So the width's first step takes both anchors down by the same amount and its second takes one of them most of the way and
leaves the other where it was, which is where `e461`'s price gap of **0.0208** comes from and not from a steady drift.

**And the magnitude ladder is ordered at both rungs for both arms, which is the claim.** `ewc-block` reads **0.0615**,
**0.0406** then **0.0115** and `ewc-block-rand` **0.0594**, **0.0396** then **0.0323**, so the width's grip falls
monotonically in the width for each arm and the pair's prices are not two independent dials. **And the resolution is not
monotone in the width even where the magnitude is**: the matched-random arm's price is **4.18** sigma at eight, **2.46**
at sixteen and **2.77** at thirty-two, so the middle rung is where that arm's price is *least* resolved while still
resolving -- the sigma is the spread's and the magnitude's together, and only the magnitude is ordered.

**And the pair's *standings* run a clean monotone ladder across the three rungs, which is the first three-point trend
this line has.** Their gap falls **0.0288**, **0.0173**, **0.0083**, so the two anchors' mean diagonals converge as the
head widens while their prices diverge, and neither arm's standing resolves anywhere on the ladder (**0.12**, **1.48**,
**1.03** sigma for the biological arm and **1.80**, **0.27**, **0.59** for the matched-random one, every one under two).
Read with `e461`, the card's pair clause now has a direction as well as two points: **the narrow neuron head is where the
two anchors are least alike on the diagonal and most alike on the last task.**

**And the buffer's advantage is a third ladder, falling for both anchors as the head widens.** It reads **+0.1785**,
**+0.1628** then **+0.1090** over `ewc-block` and **+0.2073**, **+0.1802** then **+0.1174** over `ewc-block-rand`, at
**9.95** to **12.00** sigma throughout, so the narrow neuron head is where the buffer is furthest ahead and the wide one
is where it is least ahead -- the same direction `e458` found at two points, now measured at three.

## 3. What it cannot settle

- **Three widths are not a mechanism**: **8**, **16** and **32** are one ladder of a dial whose setting also moves the
  head's parameter count, so a ladder is a shape and not a cause, and `e440`'s two parameters are read on the earned
  label and not on this head.
- **And the middle rung is one cell each**: the card's world at twenty replicates, so a price at **2.46** sigma is what a
  redraw could put under the bar and the **0.0010** gap is a difference two redraws could reverse.
- **And the source's axis stays one rung**: the world's own state is only constructible at eight columns, so this whole
  ladder is the circuit's neurons and the width is not crossed with the source.
- **And one partition draw**: the matched-random cells are one draw of the same group sizes, so the three basis contrasts
  are three readings of one draw and not of the population.

## RE-READ 2026-10-07

**The pair's standings are not a ladder, and the run of three this unit reported was a fragment.** `e463` drove a
fourth rung at **twenty-four** columns and the gaps came out **0.0288**, **0.0174**, **0.0007** and **0.0083**: the new
rung puts the pair **closer together on the diagonal than any other**, so the fall this finding describes has a minimum
inside it and the word *ladder* in it does not survive. What survives is the sentence the sigmas always supported --
**every one of the eight standings is under two sigma** (**0.12**, **1.80**, **1.48**, **0.27**, **0.05**, **0.10**,
**1.03**, **0.59**) -- so the two anchors have no diagonal effect at any of the four widths and **any ordering of their
gaps orders noise**. The rest of this finding is unaffected: the price's magnitude still falls monotonically for both
arms with the fourth point in (**DJ4** of `e463`), the pair's prices still part between **24** and **32** columns, and
the conclusions this unit drew about the wide head are the fourth rung's as well. The three-rung numbers below stand as
what this unit measured; what is withdrawn is the trend read out of them
(`docs/findings/2026-10-07-the-neuron-readout-at-twenty-four-columns.md`).

## RE-READ 2026-10-08, second: the ladder has a budget

`e466` drove the same three widths at **100 updates** and the far point's two ladders turned out to be the far point's:
`ewc-block-rand`'s price magnitude **rises** from eight columns to sixteen there (**0.0583** to **0.1396**), so **DI4**'s
ordering is a statement about a body trained to five hundred updates; and all six standings are **negative** at that
budget with **two** of them resolving, so *the two arms have no diagonal effect at any of the four widths* is a null at
five hundred updates rather than a property of the partition. Nothing in this unit's own numbers moves -- the six rolls
it read are the far point's and its five claims stand on them -- and what this RE-READ adds is the condition its first
table does not name: **500 updates**, which is `e438`'s `--iters` and what every rung of this line inherits
(`docs/findings/2026-10-08-the-width-ladder-at-another-budget.md`).
