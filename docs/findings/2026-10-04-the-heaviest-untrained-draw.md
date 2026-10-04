# The heaviest untrained draw: the path weight's lead is retired, and the card's world is the only one of ten that keeps the cue

*2026-10-04. `experiments/e401_the_heaviest_untrained_draw.py` runs the test `e400` asked for. A search over **32**
cue draws measures each one's path weight and its cue-to-action distance without rolling anything, and the criterion
-- registered before any training -- is the **heaviest draw that `e398` and `e399` did not train**. That draw is run at
the card's two ends. Five claims, registered before any of the new runs' readings was opened.*

## 1. The heaviest draw, and the five before it

| world | cue seed | cue to action | gain | path weight | trained head |
|---|---|---|---|---|---|
| **9** | 9 | 2 | −0.2250 | 28.80 | 0.8125 |
| **6** | **6** | **1** | **−0.2083** | **104.95** | 0.5208 |
| **1** | 1 | 1 | −0.1813 | 42.22 | 0.7500 |
| **3** | 3 | 2 | −0.1635 | 48.78 | 0.8333 |
| **14** | 14 | 2 | −0.1479 | 42.80 | 0.8333 |
| **the card's** | -- | 2 | **+0.0854** | 77.34 | 0.7500 |

The search's five heaviest draws are **seed 6 at 104.95**, seed 28 at 88.32, seed 11 at 85.59, seed 26 at 81.44 and
seed 8 at 79.80 -- and the card's world, at 77.34, is **sixth**. Every one of the five heaviest is at distance 1.

| claim | measured | verdict |
|---|---|---|
| Y1 the selection is the heaviest untrained draw | seed **6** at **104.95** over 32 draws | **MET** |
| Y2 it is heavier than the card's world | **104.95** against **77.34** | **MET** |
| Y3 the lead's prediction is that it recovers | **−0.2083** | **FALSIFIER FIRED** |
| Y4 the initial reading does not move | **0.6875** six times, spread **0.0000** | **MET** |
| Y5 the weight still tracks the outcomes | **+0.371**, against 0.9 over five | **FALSIFIER FIRED** |

## 2. What fired, and what it retires

**The heaviest cue population measured fails by as much as the rest.** Seed 6's path weight is **1.36 times** the
card's -- the largest of thirty-two draws, chosen by the property alone -- and its body ends **0.2083 below** an
untrained one, inside the band the other four failures occupy (0.1479 to 0.2250). So the path weight is **not
sufficient**, and `e400`'s lead is retired by the test it asked for: the property was outside the losers' range on
the five it was screened on and the sixth draw puts it back inside.

**And the correlation collapses.** Over the five worlds the weight's rank correlation with the gain was **0.9**; with
the sixth measured it is **+0.371**, under the 0.5 the unit registered as the point at which the ordering breaks.
The correlation was a five-point artifact, and the unit's own falsifier caught it.

**And the card's world is now one of ten.** Four engine redraws (`e395`, `e396`), five other cue populations at
distance 2, 2, 2, 1 and 1 (`e398`, `e399`, this), and the card's own world: **nine of the ten lose the cue** by
0.1479 to 0.2490, and the card's is the only one that keeps it. Its cue population is not even the heaviest -- it is
the **sixth** of thirty-two -- so the one property `e400` found it extreme on is one it is not extreme on outside the
five-world screen.

## 3. What it cannot settle, and what it registers

- **The screen is empty.** Among the near geometries measured -- the hop count (`e397`, `e398`), the five properties
  of `e400`, and now the weight's own test -- nothing separates the card's world from the other nine. What remains
  unmeasured is the cue's **weighted spectrum**, its overlap with the read-out draw, the action population's own
  tree, and anything about the **trained body**, which is where the difference actually appears (`e396`: the draw is
  invisible before the weights move).
- **One fresh draw is one fresh draw**, and the criterion picked the *extreme* of the weight's range, so what is
  retired is the weight at its heaviest and not the property in general. A draw in the middle of the range would test
  the rest of it.
- **And `e400`'s other four properties are untested**: the two-hop frontier, the fan-out, the action overlap and the
  cue out-degree were screened and not run.
- *And a probe is not a mechanism.*
