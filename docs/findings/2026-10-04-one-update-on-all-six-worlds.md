# One update on all six worlds: the draw's ordering is already there after a single gradient step

*2026-10-04. `experiments/e405_one_update_on_all_six_worlds.py` runs all six measured worlds for exactly **one**
update and puts their one-update readings against their five-hundred-update ones. `e404` closed the third screen and
registered the direction that was left -- *"the **training** itself, since `e396` measured that the draw is invisible
before the weights move and worth a third of the reading after"* -- and the cheapest place in the training is its
first step, which `e384` measured as costing the card's world only **0.0083**. Five claims, registered before any of
the new runs' readings was opened, and **two of them fired against the unit's own prediction.***

## 1. Six worlds, two budgets

| world | cue seed | connectome's own reading | body after 1 update | gain at 1 | body after 500 updates | gain at 500 |
|---|---|---|---|---|---|---|
| **9** | 9 | 0.6875 | 0.6188 | **−0.0687** | 0.4625 | −0.2250 |
| **6** | 6 | 0.6875 | 0.6729 | −0.0146 | 0.4792 | −0.2083 |
| **1** | 1 | 0.6875 | 0.6469 | −0.0406 | 0.5062 | −0.1813 |
| **3** | 3 | 0.6875 | 0.6521 | −0.0354 | 0.5240 | −0.1635 |
| **14** | 14 | 0.6875 | 0.6677 | −0.0198 | 0.5396 | −0.1479 |
| **the card's** | -- | 0.6875 | **0.6792** | **−0.0083** | **0.7729** | **+0.0854** |

The worlds are in the 500-update readings' order, best first.

| claim | measured | verdict |
|---|---|---|
| AH1 only the cue population moved, at a budget of one | 3 of 51 configuration fields vary, all of them the cue seed's or the plumbing's | **MET** |
| AH2 the first update is mild on every world | the largest cost is **0.0687** | **NULL** |
| AH3 the worlds separate later | **0.0604** at one update against **0.3104** at five hundred | **FALSIFIER FIRED** |
| AH4 the initial reading does not move | **0.6875** six times, spread **0.0000** | **MET** |
| AH5 the one that recovers is not distinguished at one update | **0.6792**, the highest of the six | **FALSIFIER FIRED** |

## 2. What fired, and what it takes back

**The draw is visible after one gradient step.** The unit registered the prediction that the six worlds would be one
band at one update and two groups at five hundred -- the natural extension of `e396`'s 0.0000 *before* any update --
and it is false: the card's world's one-update reading, **0.6792**, is the **largest of the six**, the five failing
worlds span 0.6188 to 0.6729, and the six already span **0.0604**. Every world loses something in the first step, by
0.0083 on the card's world and by 0.0146 to 0.0687 on the others, so the first update is not uniformly mild either
(AH2's **NULL**).

**And the separation grows rather than appearing.** The six worlds span **0.0604** after one update and **0.3104**
after five hundred -- **5.1 times** as wide -- and their two orderings largely agree: four of the six keep their
rank, with cue seed 6 falling from second to fifth and cue seed 14 rising from third to second, a rank correlation
of **0.69**. So the draw's ordering is established by the first gradient step and *amplified* by the rest of the
training, which is a different account from the one the unit registered.

**And that accounts for the six empty screens.** `e397` to `e404` screened the draw's distance, five geometric
properties, the trained bodies' movement and alignment, and the annotation table -- all of them properties of the
**draw alone** or of the **body alone** -- and found nothing. What this unit shows is that the difference is not in
either: it is in what the draw does to the **first gradient step**, which is why a screen of static properties has
nothing to separate on. The one update is a measurement of the pair and not of the draw.

## 3. What it cannot settle, and what it registers

- **One update is one update**: the separation could be arranged in the second step or the hundredth, and only the
  two ends are measured. `e384`'s series put the card's world at 0.6792, 0.5917, 0.5750 for one, two and three
  updates, so the second step costs it twenty times the first -- whether the six worlds' order survives **that** is
  the next measurement.
- **And the worlds are six of ten**: the four engine redraws are not run here, so the band is six wide and not ten.
- **One arm and one rate**: the 3e-3 `naive` bodies only, where `e383` showed the tight end's collapse at two rates.
- *And a probe is not a mechanism.*
