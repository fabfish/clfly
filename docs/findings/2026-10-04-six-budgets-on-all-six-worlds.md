# Six budgets on all six worlds: the widening is front-loaded, and the ordering dips again

*2026-10-04. `experiments/e408_six_budgets_on_all_six_worlds.py` puts a budget inside the stretch `e407` left open:
**one hundred** updates on all six measured worlds, so the series is 1, 2, 5, 20, 100 and 500. Five claims,
registered before any of the new runs' readings was opened.*

## 1. Six worlds, six budgets

| world | cue seed | 1 | 2 | 5 | 20 | 100 | 500 |
|---|---|---|---|---|---|---|---|
| **the card's** | -- | **0.6792** | 0.6281 | **0.5979** | **0.5740** | **0.6385** | **0.7729** |
| **14** | 14 | 0.6677 | **0.6438** | 0.5396 | 0.5490 | 0.5125 | 0.5396 |
| **6** | 6 | 0.6729 | 0.6427 | 0.5458 | 0.5177 | 0.5104 | 0.4792 |
| **3** | 3 | 0.6521 | 0.6375 | 0.5510 | 0.5219 | 0.5042 | 0.5240 |
| **9** | 9 | 0.6188 | 0.5760 | 0.4802 | 0.5115 | 0.4635 | 0.4625 |
| **1** | 1 | 0.6469 | 0.5854 | 0.5615 | 0.4990 | 0.4375 | 0.5062 |

The worlds are ordered by their 500-update readings. The **span** at each budget is 0.0604, 0.0677, 0.1177, 0.0750,
**0.2010** and 0.3104, and the **rank correlation with the far end** of each budget's ordering is 0.657, 0.429,
0.600, 0.829, **0.714** and 1.000.

| claim | measured | verdict |
|---|---|---|
| AK1 only the cue population moved, at a hundred | 3 of 51 fields vary, the cue seed's and the plumbing's | **MET** |
| AK2 the card's world is still on top there | **0.6385**, the largest of the six | **MET** |
| AK3 the ordering there still agrees with the far end | **+0.714** | **NULL** |
| AK4 the widening has begun by a hundred | **0.2010** against **0.0750** at twenty | **MET** |
| AK5 the initial reading does not move | **0.6875**, spread **0.0000** | **MET** |

## 2. What the sixth budget says

**The card's world leads at five of the six prices.** It is first at 1, 5, 20, 100 and 500 updates and fourth at
exactly **one** -- two updates -- with a gap at a hundred that is the widest of any budget in the series: **0.6385**
against 0.4375 to 0.5125 for the five that lose the cue.

**And the widening is front-loaded.** The stretch from twenty to five hundred widens the band from **0.0750** to
**0.3104**, and at a hundred it is already **0.2010** -- **54%** of the total widening in the first **17%** of the
stretch. The four hundred updates from a hundred to five hundred add the remaining 0.1094. So the answer to `e407`'s
question is that the widening is not gradual: most of it happens within the first eighty updates after twenty.

**And the ordering dips again on the way.** Its agreement with the far end is **0.829** at twenty, **0.714** at a
hundred and 1.000 at five hundred -- so the hundred-update ordering is *less* like the far end than the
twenty-update one, by four places' worth of rearranging (cue seeds 6, 3, 1 and 9 all change places between the two).
The convergence of the ranking is therefore not monotone either, and the third budget in a row where the ranking
moves the wrong way on the way to the end.

## 3. What it cannot settle, and what it registers

- **One budget inside four hundred and eighty updates.** The stretch from a hundred to five hundred is still the
  widest gap in the series, and whether *its* widening is gradual is not measured -- what is measured is that half of
  the whole stretch's widening is done by a hundred.
- **And the series is six worlds wide**: the four engine redraws are not run at any budget.
- **One arm and one rate**: the 3e-3 `naive` bodies only.
- *And a probe is not a mechanism.*
