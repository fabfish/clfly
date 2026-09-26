# The spread does not follow the destruction count

*2026-09-26 14:10. Runs: **none new** — this reads `runs/*.json` (`e208`, `e209_screen_rs0-4`, `e223`, `e226`…`e243`)
through `experiments/e244_drawing_spread_by_kind.py`, written as `runs/e244_drawing_spread_by_kind.json`. JSON-only,
seconds.*

## 1. The question

The ladder says the **level** of the penalty follows how many degree sequences a construction destroys — none for
`swap*` and `signshuffle`, one for `alloy*`/`inalloy*`, two for `erdos_renyi` — and that `erdos_renyi` sits highest.
`e240`/`e241`/`e242` established the complementary fact: a **cross-family comparison** in this corpus is a drawing,
while a **level over a few drawings** is a number. Together those raise a question the corpus can answer without new
runs:

    is the SPREAD of the penalty across drawings itself ordered by the same axis as its level?

The convention cell alone carries drawings of six `swap` strengths, `signshuffle`, `alloy0.25`…`alloy1`, `inalloy1`
and `erdos_renyi`. Six cells carry a group with two or more drawings; the whole census is **27 groups**.

## 2. The claims, and what was fixed after the first run

- **K1 — the pooled spread orders with the destruction count.** Over the (cell, family) groups with two or more
  drawings, the median excess spread is smallest for kind 2 and largest for kind 0 with kind 1 between, and the
  kind-2 and kind-0 ranges are disjoint. **Falsifier**: kind 2's median at or above kind 0's; **null**: ordered but
  the ranges overlapping.
- **K2 — it is not only the level.** The same ordering for the **scale-free** relative spread `(max - min)/mean`.
  **Falsifier**: unordered.
- **K3 — the ordering is not an artifact of pooling cells.** Inside **every** cell where two kinds both have two
  drawings, the kind that destroys more degree sequences has the smaller median spread. **Falsifier**: any reversal.

Three things were changed after this module's first run, and each is recorded rather than repaired silently:

1. **`real` was removed from the kinds.** `real` is the observed network and is never redrawn, so its "spread across
   drawings" is exactly 1.00 by construction. Including it moved the pooled kind-0 median from **1.45× to 1.26×**
   (the whole of K1's top rung). It is now reported as a **control**: `e223_cs400_support80_rs0/rs1` both carry
   excess **1.0** and rank **1.0**, i.e. the two artifacts hold the same number to the last printed digit.
2. **K2's statistic was rewritten.** The first version divided the ratio spread by the mean, which is dominated by the
   mean and is not scale-free: it gave 61.5 / 17.2 / 7.1 across kinds 0 / 1 / 2, an ordering that is really the level
   ordering. It is now `(max - min) / mean`, invariant under rescaling the level (pinned by a test).
3. **K3 was written after seeing the pooled K1 output** — the discriminator between "kinds are ordered" and "cells are
   ordered" could be written either way, and writing it after the pooled run is disclosed here.

## 3. Results

Pooled over all cells:

| kind | destroy | groups | families | median excess spread | range | median rel range |
|---|---|---|---|---|---|---|
| 0 | 0 sequences | 3 | 3 | **1.449×** | [1.072, 1.844] | 0.337 |
| 1 | 1 sequence | 14 | 6 | **1.234×** | [1.062, 3.344] | 0.210 |
| 2 | 2 sequences | 6 | 6 | **1.029×** | [1.021, 1.054] | 0.029 |

**K1 MET** (ordered, and [1.021, 1.054] is disjoint from [1.072, 1.844]). **K2 MET** — the relative spreads order the
same way, 0.029 < 0.210 < 0.337. **K3 FALSIFIER FIRED: 6 of 7 cell-pairs support the ordering**, and the reversal is
at the one cell that carries a kind-0 construction at all.

The per-cell collapse is the whole finding:

    cs 300/sup  30   kind 1: 1.42x (2 fam)   kind 2: 1.03x
    cs 400/sup  40   kind 1: 1.08x (2 fam)   kind 2: 1.05x
    cs 400/sup  80   kind 1: 1.09x (2 fam)   kind 2: 1.02x
    cs 800/sup  20   kind 1: 1.32x (2 fam)   kind 2: 1.03x
    cs 800/sup 160   kind 1: 1.89x (2 fam)   kind 2: 1.03x
    cs 800/sup  80   kind 0: 1.45x (3 fam)   kind 1: 2.29x (4 fam)   kind 2: 1.05x

`erdos_renyi` is the tightest in **6 of 6** cells — the six cell-pairs that support K3 are exactly the (2, 1) pairs.
The single (1, 0) pair, at the one cell where both exist, **reverses**: `alloy1`/`inalloy1` spread **1.58× wider**
than `swap*`/`signshuffle`, even though the no-destruction constructions are the lower-level ones.

## 4. What survives

- **The two-side kind is the tightest one, in every cell it appears in (6 of 6).** `erdos_renyi`'s spread is
  1.02× to 1.05× pooled and 1.02× to 1.05× per cell; the one-side families run 1.06× to 3.34×.
- **The two-side kind is the tightest and the highest — the two are the same fact here.** Its excess is 0.12 to 0.16
  against the one-side families' 0.027 to 0.134, so "destroys two degree sequences" and "sits at the top of the
  ladder" cannot be separated by this corpus. Every supporting cell-pair is collinear with the level.

## 5. What does not survive, and the negatives

- **K1's ordering is cell composition.** Its top rung, kind 0, is **one cell** (cs 800/support 80): the three
  families `swap0.5`, `swap2`, `signshuffle`, at one size, one support, one `rho`. Kind 1's median sits on 14 groups
  across 6 cells. Inside the one cell that carries both, the order is **2 < 0 < 1** — `alloy1` is the loosest thing
  in the table, and the pooled K1 only survives because five other cells vote for kind 1 while carrying no kind 0.
  Dilution is pinned by a test: with the four kind-1-and-2-only cells removed, **the same reversal breaks K1 too**.
- **The cell moves the spread more than the kind does — for one of the two spellings.** `alloy1`'s spread runs
  1.10×, 1.12×, 1.49×, 1.55×, 2.58×, **3.34×** across the six cells (a 3.0× span), while `inalloy1`'s runs 1.06× to
  1.35× (1.3×). The 3.34× is **one run's** excess (0.1007 in `e208`, against its own other four drawings' 0.0301 to
  0.0470), so the kind-1 rung's looseness at the convention cell is one outlier. Pooled between-kind span is 1.03× to
  1.45× (1.4×), within-kind across-cell span 1.08× to 2.29× (2.1×).
- **The excess rung stops where the rank rung does not.** `e209_screen_rs0-4` are `--geometry-only` runs, so the
  excess is absent for `swap8`/`swap16`/`swap32`/`swap64` (only their ranks exist) and kind 0's excess census is
  three families against seven usable rank families. On the **rank** spread the same cell orders **0 > 1 > 2**
  (5.87×, 3.26×, 1.23×, and 6 of 6 cells again for the two-side kind) — so the reversal in §5 is a property of the
  **penalty's** spread, not of the geometry's, and the two observables disagree about which construction is loosest.
- **Nothing here separates the destruction count from the level.** The one axis that would (matching the level and
  varying only the destroyed structure) is not in the corpus.

## 6. What it cannot do

The drawings are the corpus's accidental ones and are unevenly distributed (kind 0 exists at **one** cell, kind 2 is
always the single family `erdos_renyi`); a kind's per-cell value is a median over one or two families; a construction
whose level is near zero cannot spread far in absolute terms, though the relative range is meant to blunt that; the
`rho` above 0.9 cells carry one drawing per family and are absent from the census entirely; and nothing here is a new
measurement — every number comes from artifacts already on the plan's rows. The K1/K2 "MET" verdicts are recorded as
pooled statements that the only within-cell test available contradicts, not as support for the ladder.
