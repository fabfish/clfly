# One size of the grid is whole, and it answers the question `e86` could not

**Date:** 2026-09-23
**Script:** `experiments/e92_grid_report.py`; artifact `runs/e92_grid_report.json`
**Data:** cs = 300 is **complete at 20 of 20 cells**; cs = 800 has 9 and cs = 1500 has 3, both `flat` only.
**Context:** `docs/findings/2026-09-23-the-cross-size-test-is-not-well-posed.md`,
`docs/findings/2026-09-23-the-concentration-matched-grid-preregistered.md`

---

## 1. The result at d = 952, where the design is whole

Twenty group-size profiles whose concentrations are **set by construction** rather than found, spanning
0.0063 to 0.5558, at `e14`/`e74`'s protocol (3 task seeds, 5 relabellings each):

| statistic at d = 952, n = 20 | value |
|---|---|
| raw Spearman, **absolute** pressure spread vs measured draw sd | **+0.908** |
| raw Spearman, **concentration** vs measured draw sd | +0.677 |
| **partial, absolute form given concentration** | **+0.919** (p = 2.7e-08) |
| partial, relative form given concentration | **+0.955** (p = 2.0e-10) |
| per-seed partials, absolute form | +0.829 / +0.937 / +0.900 (**3 of 3 positive**) |
| leave-one-cell-out, absolute form | **+0.896 to +0.951**, no sign flip |
| bootstrap over profiles, 4000 resamples | **+0.892 [+0.718, +0.977]**, **0.00% at or below zero** |

**This is the size at which `e86`'s raw test failed** — +0.412 against concentration's +0.832 on the nine
biological rungs, its one loss in three. On twenty profiles whose concentrations are set, the same statistic
gives **+0.908 raw** (above concentration's +0.677) and **+0.919 with the confound partialled out**, and
every robustness check the project uses passes: three of three seeds positive, no leave-one-out sign flip,
and a bootstrap interval that never touches zero.

So the d = 952 failure was a property of **the nine's bimodal design** — four near-duplicate coarse rows,
two of them the same run byte-for-byte, occupying four of nine ranks in both orderings — and not of the
spread statistic. That is the conclusion `e86` could state only as a suspicion, and it is now measured.

## 2. The second shape is not decoration: it is what makes the statistic readable

The grid's two shapes were introduced to give two points at one group count. They turn out to do something
the design needed and did not name:

| subset at d = 952 | n | ρ(concentration, target) | raw pressure | **partial** |
|---|---|---|---|---|
| `flat` only (concentration exactly `1/k`) | 10 | **+0.891** | +0.782 | **+0.590** |
| `harmonic` only | 10 | +0.782 | +0.479 | **+0.715** |
| **both** | 20 | **+0.677** | **+0.908** | **+0.919** |

Each shape alone leaves the confound coupled and yields a weaker partial, *and the two partials are each
below the joint one*. So the shapes are **complementary**, not redundant: jointly they break the
concentration–target coupling from +0.891 to +0.677 and lift the partial from 0.59 to 0.92. A grid built of
`flat` profiles alone — the obvious way to "set concentration" — would have been a concentration ladder with
the confound at +0.891 and partials around 0.6, i.e. it would have been much weaker evidence than the grid
that was actually run.

**And this is why P6 is worth pre-registering** (`...-preregistered.md` §8): at d = 1307 the nine cells on
disk are all `flat`, their concentration–target coupling is **+0.983**, and their partial is +0.654 with
**25% of profile-bootstrap resamples at or below zero**. That is not a result, it is the thin-residual
situation rule 24 warns about, and it is the *predicted* consequence of missing the second shape.

## 3. Shape carries information concentration does not — the direct measurement

Ten same-`k` pairs at d = 952, `harmonic` against `flat`, on the measured draw sd:

| k | conc harmonic | conc flat | measured harmonic | measured flat | ratio |
|---|---|---|---|---|---|
| 2 | 0.5558 | 0.5000 | 1.693e-3 | 5.053e-4 | 3.35× |
| 3 | 0.4048 | 0.3333 | 1.258e-3 | 6.438e-4 | 1.95× |
| 5 | 0.2809 | 0.2000 | 1.431e-3 | 2.799e-4 | 5.11× |
| 8 | 0.2066 | 0.1250 | 1.379e-3 | 4.997e-4 | 2.76× |
| 13 | 0.1553 | 0.0769 | 1.653e-3 | 2.288e-4 | 7.22× |
| 21 | 0.1203 | 0.0476 | 1.623e-3 | 2.896e-4 | 5.60× |
| 34 | 0.0953 | 0.0294 | 1.137e-3 | 2.616e-4 | 4.35× |
| 55 | 0.0771 | 0.0182 | 1.037e-3 | 1.469e-4 | 7.06× |
| 96 | 0.0619 | 0.0104 | 9.105e-4 | 1.955e-4 | 4.66× |
| 160 | 0.0511 | 0.0063 | 7.802e-4 | 1.298e-4 | 6.01× |

**Ten of ten in the same direction, by 1.95× to 7.22×.** But the harmonic profile also has higher
concentration in *every* pair, so the ratio is confounded and the table on its own says nothing about which
coordinate does the work. A joint fit on logs does separate them:

| dependent variable, d = 952, n = 20 | concentration alone | shape alone | both | shape beyond concentration |
|---|---|---|---|---|
| log measured draw sd | R² **0.497** (slope +0.490) | R² **0.779** | R² **0.938** | F = 121.4, **p < 1e-4** |
| log pressure spread | R² 0.309 (+0.392) | R² 0.829 | R² 0.881 | F = 81.6, **p < 1e-4** |
| log relative spread | R² 0.646 (+0.688) | R² 0.685 | R² 0.965 | F = 153.3, **p < 1e-4** |

**Shape adds information beyond concentration on all three, decisively** — and on the target it does more
than that: **shape alone explains 78% against concentration's 50%.** So at this size the "concentration is
the scalar that decides" view is refuted a second way: `side-draw-sd` refuted it from the measured side
(four points rising then falling as concentration rises), and this refutes it from the design side, on
twenty points, at p < 1e-4.

## 4. What is *not* yet true

- **P1, P2 and P4 are PENDING, not failed.** They are scoped to "every size" and one size has three cells.
  The report printed `FAIL` for them until this fire, which reads as a refutation when the data is simply
  absent; it now distinguishes the two, and prints `PENDING (n of 3 sizes scored)`.
- **d = 1307's grid result is not readable.** Nine cells, all `flat`, coupling +0.983, bootstrap 25% at or
  below zero. P6 predicts this changes; until it does, nothing here should be quoted from that size.
- **The twenty cells at one size share three task seeds and one circuit.** The bootstrap resamples
  *profiles*, which does not remove the shared seed or circuit variation, so the interval is a lower bound
  on the uncertainty in the way rule 23 describes. The companion is the per-seed column, which is 3 of 3
  positive with no leave-one-out flip — a count, not a calibrated test.
- **Nothing here speaks to the cross-size claim.** The two that matter for §4.3 are still partial: a
  second size in the statistic's favour would be needed to upgrade the paper from *passes at two of three
  sizes on the nine* to *passes on concentration-matched grids*, and that is what the remaining 28 cells
  are for.
