# Registered: a third cell that should interpolate the (1, 0) margin

*2026-09-26 17:10, registered before its runs. Runs: `e2_topology_gap` at `--circuit-size 800 --support 20 --seeds 3
--seed0 0 -q 0.02 --topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed {4,5}` — **two runs, one cell
each**, to be written as `e249_cs800_sup20_kind0_rs4.json` and `_rs5.json`. Two runs because the base being matched has
kind 1 and kind 2 at **exactly two excess drawings** at this cell, so two is the count to match and no post-hoc
subsetting is needed.*

## 1. The question the last three fires left

The (1, 0) comparison — the no-destruction constructions against the one-side ones — has been read five ways and the
margins run from a tie to a doubling:

| cell | reading | margin (kind 1 ÷ kind 0) |
|---|---|---|
| cs 300/support 30 | equal count 3 (`e248`) | **1.008** |
| cs 300/support 30 | `e245`'s unequal form | 1.022 |
| cs 300/support 30 | `e247`'s two-lowest-seed | 0.94 (the other way) |
| cs 800/support 80 | all drawings | **2.044** |
| cs 800/support 80 | two-lowest-seed | 1.107 |

`e247`'s R3 killed the two obvious cell-level explanations — the support share and the circuit size order **nothing**
(−0.074 and +0.033) — and `e248`'s equal-count base left the driver unnamed while showing the margin is a **tie** at
cs 300/support 30 at matched counts. What is left is the one thing that does differ between those two cells and that
is measured for every cell's families already: **the cell's own rank contrast**.

    cs 300/support 30   alloy1 rank spread 2.73x   inalloy1 2.08x   ->  (1, 0) margin 1.008
    cs 800/support 80   alloy1 rank spread 14.08x  inalloy1 8.02x   ->  (1, 0) margin 2.044

If the margin follows that, a cell whose kind-1 rank spreads sit **between** those two should give a margin that sits
between those two. **cs 800/support 20 is exactly such a cell and is one run away from being measured**: its kind-1
rank spreads are **6.28×** and **2.21×**, between 2.73/2.08 and 14.08/8.02, and its kind-1 and kind-2 families carry
**exactly two excess drawings each**, so two runs of the three kind-0 families give a base that is equal-count at two
with no subsetting at all.

## 2. The registered claims

- **T1 — the margin interpolates, which is the prediction.** At cs 800/support 20, with every family at **two**
  drawings, the (1, 0) margin — median kind-1 spread ÷ median kind-0 spread over the three kind-0 families — is
  **above 1.10 and below 2.00**. **Falsifier**: **below 1.05**, in which case the margin is not ordered by the rank
  contrast and cs 800/support 80's doubling is a cell idiosyncrasy rather than an interpolation point, or **above
  2.50**, in which case the margin does not interpolate either. **Null**: 1.05 to 1.10, or 2.00 to 2.50.
- **T2 — the survivor travels.** With every family at two drawings, `erdos_renyi` is the tightest of the five families
  at this cell, as it is at every cell, every count and every leave-one-out subset measured so far.
- **T3 — reported, not claimed.** Each of the five families' two excesses, their spreads, the cell's rank spreads
  beside them, and the margin computed both on the equal-count base and on the corpus's larger drawings where they
  exist (the kind-1 families have two here, so the two forms coincide for kind 1 and differ only for kind 0).

## 2b. A correction registered while the runs were in flight, before any of their data existed

Writing this module's own table exposed a mismatch in T1 above, and it is worth stating in the registration rather
than after the result. **T1's bars come from the *all-drawings* margins at the two reference cells** (1.008 at cs
300/support 30 and 2.044 at cs 800/support 80) while the new cell is read at **two** drawings. On a consistent
two-drawing footing the same two reference cells read

    cs 300/support 30   equal-count-two margin 0.851   (kind-1 rank spreads 2.73x, 2.08x)
    cs 800/support 80   equal-count-two margin 1.660   (kind-1 rank spreads 14.08x, 8.02x)

so T1's interval is drawn on a different scale from the quantity it judges. **T1b, added to the module at 17:20 while
both runs were still running and no artifact of theirs existed**, restates the prediction on one footing: the new
cell's equal-count-two margin lies **strictly inside (0.851, 1.660)**. **Falsifier**: outside that interval, which
would mean the margin is not monotone in the rank contrast over these three cells. The reference values are computed
from data already on disk; the new cell's value is not, so this is a blind prediction, and T1 stays registered as
written — if the two disagree, both verdicts are reported.

## 3. Cost, and what it cannot do

**Cost**: cs 800's cells have run at 228–240 s for three seeds without the realized arm (`e213`'s ten cells), so two
runs of three topologies are **≈23 min** — longer than one fire, so the read lands in the next.

It cannot: **prove** the rank contrast is the driver, because two cells becoming three is a trend and not a relation
(and the rank spreads and the excess spreads are read off the same drawings, so they are not independent variables);
it is one support at one size, so the rank contrast is confounded with whatever else cs 800/support 20 is; two drawings
per family is the noisiest count in the corpus and `e247` measured that a two-drawing spread is unstable; the three
kind-0 families share each run's single `rewire_seed`; `rho` is the builder's default; and the comparison remains one
of spreads, not levels.
