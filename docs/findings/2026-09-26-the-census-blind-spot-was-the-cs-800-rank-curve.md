# The census's blind spot: the same rank curve, checked at cs 300 and one-drawing at cs 800

*2026-09-26 19:25. Runs: **none new** — `experiments/e254_quoted_figure_census.py`'s registry was extended with the three
cs-800 figures it had not named, and the census re-run (`runs/e254_quoted_figure_census.json`). JSON-only, seconds.*

## 1. Why the registry needed extending

`e255` closed the low-`rho` thinness at cs 300 and recorded, as a limitation, that **cs 800's `rho` 0.5, 0.7 and 0.8
cells also carry one drawing per family** — and that the census's registry named **no figure** resting on them, so the
census could not say whether that thinness mattered. That is the instrument's own blind spot: a thin cell is invisible
to it unless a quoted figure draws on it.

## 2. What the extension found

Three figures the registry had not named, re-run through the census:

| figure | inputs | verdict |
|---|---|---|
| **the rank curve at cs 800** | 14 | **STILL EXPOSED at 6 of its 7 `rho` values** (0.5, 0.7, 0.8, 0.95, 0.98, 0.99) |
| **the size effect changes sign with `rho`** | 12 | **STILL EXPOSED** (through cs 800/`rho` 0.5) |
| the two-side level is flat across sizes | 2 | SAFE |

**E1 MET** (two of the three are exposed), **E2 MET** (every new exposure is a cs-800 `rho` cell), **E3 MET** (the
cs-800 rank curve is thin at **6 of 7** rho values — only `rho` 0.9 is drawn). All three are confirmatory, computed
with the extension, and recorded as **coverage regressions**: they pin the registry so a future edit that drops a
cs-800 figure fires.

So the census now stands at **15 figures: 8 SAFE, 5 DECOMPOSED, 2 EXPOSED** — where the two exposed ones are the
counterpart of the claim `e255` had just checked.

## 3. The asymmetry, which is the finding

The record's rank curve exists at two sizes, and its two halves are in opposite states:

    cs 300/support 30, rho 0.5 to 0.99   2 to 3 drawings per cell   checked by e255: the fall survives, 1.00x to 1.10x
    cs 800/support 80, rho 0.5 to 0.99   1 drawing at 6 of 7 values  NOT checked, and the census said nothing until now

    cs 800/support 80, single-drawing alloy1 ranks:  63.14 (0.5), 45.83 (0.7), 32.78 (0.8), 22.09 (0.95), 21.24 (0.98), 21.01 (0.99)

**At cs 300 the low-`rho` end turned out stable to within 10%, and that stability is exactly what makes the cs-800
half's 63.14 → 45.83 → 32.78 → 22.09 fall worth checking rather than assuming**: the same claim at the other size has
one drawing at each of those values, and `e251`/`e253` measured the high-`rho` end of the *excess* side to move by
factors of 1.54 and 4.47 between drawings. The cs-800 rank curve's design history is the same as the cs-300 one's — a
single pass over the grid — so the same lottery applies until it is drawn again.

## 4. What it cannot do

The extension is a **registry edit**, so it changes what the instrument looks at and not what the corpus contains; a
figure still missing from the registry remains invisible, and this episode shows how that happens — the registry was
written by hand from one session's fires, and a figure at a *different size* of the same claim is not obviously a
separate entry until the counts are asked for. The E-claims are confirmatory by construction. And "exposed" still means
only that an input has one drawing, not that the figure is wrong: of the six thin figures checked so far, three agreed
when drawn — so the base rate this exercise should be read against is **three moved, three held**, and the two cs-800
figures now join the unchecked side of that ledger.
