# The cross-family contrasts on the corpus's own drawings: the two-side advantage is above 3× at ONE cell of six, and the drawings dominate everywhere else

*2026-09-26 13:50, `runs/e240_cross_family_drawings.json` through `e240_cross_family_drawings.py` — no new runs: every
number is read from artifacts already on the plan's rows. A **drawing** is a distinct `rewire_seed` (12 `alloy1`
artifacts at cs 800/support 80 are 5 drawings). **C1's falsifier fires at one cell, C2's at five of six, C3 is MET.***

## 1. What the corpus already carries

| cell (`rho` 0.9) | `alloy1` | `inalloy1` | `erdos_renyi` | median rank ratio | median ER ÷ `alloy1` |
|---|---|---|---|---|---|
| cs 300, support 30 | 3 | 3 | 3 | 0.65× | **1.28×** |
| cs 400, support 40 | 3 | 3 | 3 | 1.10× | **1.12×** |
| cs 400, support 80 | 2 | 2 | 2 | 0.82× | **1.22×** |
| cs 800, support 20 | 2 | 2 | 2 | 2.31× | **2.17×** |
| cs 800, support 160 | 2 | 2 | 2 | **5.81×** | **2.22×** |
| cs 800, support 80 | 5 | 3 | 6 | 0.85× | **3.45×** |

The two medians are the pairwise values over every cross-drawing pair — the distribution a single-drawing claim is
one draw of.

## 2. C1: the rank contrast has no systematic direction — except at one cell

Five of the six medians lie between 0.5 and 2, so the `alloy1`/`inalloy1` *rank* contrast is a draw at those cells, as
`e232` and `e239` found. **The falsifier fires at cs 800/support 160, whose median is 5.81×** — a direction the
drawings do not wash out. It is not a support-share story either: at cs 800 the median runs **2.31× at support 20,
0.85× at support 80 and 5.81× at support 160**, so the *direction of the in/out asymmetry at cs 800 is specific to the
support setting* rather than monotone in the share. That is a lead for the next design rather than a settled fact.

## 3. C2: the two-side advantage is above 3× at exactly one cell — and it is the convention cell

**Falsifier fired at five of six cells.** The median `erdos_renyi` ÷ `alloy1` *excess* ratio is **1.12×–2.22×** at cs
300/support 30, cs 400/support 40, cs 400/support 80, cs 800/support 20 and cs 800/support 160 — and **3.45×** only at
**cs 800/support 80**, the cell whose 2.76×/3.02× figures the record quotes for *"Erdős–Rényi is a separate regime"*.
So that reading is not a property of the substrate: it is a property of one cell, and the corpus's other cells — which
have drawings and therefore *can* be read this way — put the advantage at roughly the one-side level's own spread.

This is a qualification of the register rather than of a measurement: the ladder's "top step" is real at cs 800, and
its magnitude is cell-specific. Together with `e228`'s result (the same figure is a `rho` = 0.9 statement) the
honest form of the headline is **"the two-side null costs about 1.1–2.2× the one-side level in general, and 2.8–3.0×
at cs 800 with support 80 and `rho` 0.9"**.

## 4. C3 is MET: at 15 of 18 cells the drawings dominate the contrasts

The within-family excess spread across drawings (the larger of `alloy1`'s and `inalloy1`'s) exceeds the
between-family difference of their means at **15 of 18 cells**. The three exceptions are cs 800/support 80 at `rho`
0.95, 0.98 and 0.99 — where both one-side families have collapsed to ~1 effective dimension and their excesses are
both tiny, so the "spread" is near zero and the small difference is a real separation. **So on this corpus, a
cross-family contrast with one drawing per side is not a measurement; it is a draw whose spread usually exceeds the
thing being measured** — the same conclusion `e232`, `e236` and `e239` reached one claim at a time, now with 18 cells.

## 5. What this cannot do

- **These are re-tests on accidental drawings**, not a designed drawing axis: the cells with drawings are the ones some
  experiment happened to re-run, and the six cells above are not a random sample of the design.
- **The drawings within a cell are not independent of time** (`e227`'s code-epoch drift), so part of a "drawing
  spread" can be a run's arithmetic rather than the null.
- **`erdos_renyi` has two or more drawings at six cells and `real` never has two different ones** (it is not rewired),
  so no contrast against `real` can be re-tested this way.
- **Nothing here is new measurement**: if a cell's artifacts share a config error, this re-test shares it.
