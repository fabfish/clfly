# The pooled −0.70 decomposes into nothing: the spread is neither level-ordered between families nor inside them

*2026-09-26 15:12. Runs: **none new** — this reads the corpus through `experiments/e246_spread_volatility_by_family.py`,
which builds its groups from `e244`'s reader, written as `runs/e246_spread_volatility_by_family.json`. JSON-only,
seconds.*

## 1. What it asks

`e245` located the cross-cell movement of the drawing spread in the one-side rung — the reversal "kind 1 looser than
kind 0" holds in **direction** at 2 of 2 comparable cells and not in **size** (+2.2% and +104.4%). Two questions were
left: is that movement a property of the **family** or of the **kind**, and is the whole spread story the **level's**
story in disguise? `e244`'s own caveat said the second was open: *"kind and level are collinear across this corpus,
since `erdos_renyi` has both the highest excess and the tightest spread, so nothing here separates 'destroys more
degree structure' from 'sits at a higher penalty'."*

## 2. The claims, and what was already on screen

Two facts were visible when the module was written, from an exploratory heredoc and from `e244`'s tables: the
per-family cross-cell spans on the excess, and the aggregate Spearman between a group's level and its spread,
**−0.696** over 26 groups. **N1 and N2 therefore test what was seen** and are recorded as confirmatory. **N3's split
was registered blind**, and it is the one that moved.

- **N1 — the volatility is the one-side families' (excess).** Falsifier: a no-destruction or two-side family that
  moves as much across cells as a one-side one.
- **N2 — the same on the rank observable.**
- **N3 — the level orders the spread BETWEEN families and not within them.** (a) across families |Spearman| ≥ **0.7**;
  (b) inside families with four or more cells, the share of level-adjacent pairs whose spread falls as the level rises
  is at most **60%**. Falsifier: (b) ≥ **80%** or (a) < **0.5**; null: exactly one clause met.

## 3. Verdicts

**N1 MET — the volatility is the one-side families', and the ranges are disjoint.**

| family | kind | cells | excess spread per cell | span | rank span |
|---|---|---|---|---|---|
| `signshuffle` | 0 | 2 | 1.07, 1.39 | 1.30× | 1.14× |
| `swap0.5` | 0 | 2 | 1.45, 1.91 | 1.32× | 1.05× |
| `swap2` | 0 | 2 | 1.36, 1.84 | 1.36× | 4.40× |
| **`alloy1`** | 1 | 6 | 1.10, 1.12, 1.49, 1.55, 2.58, **3.34** | **3.04×** | **9.27×** |
| **`inalloy1`** | 1 | 6 | 1.06, 1.07, 1.08, 1.19, 1.35, 2.58 | **2.43×** | **7.34×** |
| `erdos_renyi` | 2 | 6 | 1.02, 1.03, 1.03, 1.03, 1.05, 1.06 | **1.04×** | 1.23× |

The two one-side families span 2.43×–3.04× across cells; the four measured elsewhere span 1.04×–1.36×. **N2 MET**: on
the rank observable the same split is wider — 7.34× and 9.27× against 1.05×–4.40× — and the narrow margin is `swap2`,
whose rank spread runs 1.34× to 5.87× between its two cells (its excess spread moves only 1.36× there, so the two
observables disagree about that family specifically).

So the movement `e245` attributed to kind 1 is carried by **two named families**, and it is worth stating that
`alloy0.75` and `alloy0.9` are kind 1 too and are measured at **one cell each**, so nothing here says the kind-1 rung
moves — it says `alloy1` and `inalloy1` do.

**N3 FALSIFIER FIRED, and on the clause that was expected to hold.**

    every group at once:               Spearman(level, spread)  -0.696  over 26 groups
    between families (one point each): Spearman(level, spread)  -0.371  over  6 families
    within families (4+ cells):        11 of 15 level-adjacent pairs fall as the level rises (73%)
                                       alloy1 4/5   erdos_renyi 4/5   inalloy1 3/5

The one point per family is where it breaks:

    swap0.5       mean level 0.02198   mean spread 1.68x   over 2 cells
    swap2         mean level 0.02540   mean spread 1.60x   over 2 cells
    signshuffle   mean level 0.04511   mean spread 1.23x   over 2 cells
    inalloy1      mean level 0.09060   mean spread 1.39x   over 6 cells
    alloy1        mean level 0.09521   mean spread 1.87x   over 6 cells
    erdos_renyi   mean level 0.14572   mean spread 1.04x   over 6 cells

**The widest-spread family sits at a middle level.** `alloy1` is at 0.095 — between `signshuffle`'s 0.045 and
`erdos_renyi`'s 0.146 — and it is the loosest family in the corpus (1.87× mean). Ordering these six points gives
**−0.371**, below the 0.5 floor the registration set for "the level does not order the spread at all", so the
falsifier fired on clause (a), not on the within-family clause (b) that it was aimed at (73% is between the 60%
ceiling and the 80% bar).

## 4. What this says about `e244`'s caveat

`e244` recorded that the level and the kind cannot be separated, and quoted the corpus's shape as the reason:
`erdos_renyi` highest and tightest. `e246` shows that reading is **too strong in one direction and too weak in
another**:

- The **pooled** −0.696 is **a pooling artifact**. It is not a between-family statement (−0.371 over six points) and
  not a clean within-family one (73% of fifteen adjacent pairs, binomial p ≈ 0.059 — suggestive, not resolved at this
  corpus size). It arises because pooling mixes each family's drift across cells with the ordering between families,
  and the two do not agree.
- The **structural fact survives**: `erdos_renyi` is extreme in both directions at once. What does not survive is the
  implication that the level orders the spread along the axis: with `alloy1` at a middle level and the widest spread,
  and `signshuffle` at a low level and the *tightest* of the kind-0 families, the six family means are not ordered.

So the honest form of `e244`'s caveat is **"the two extreme families are extreme in both directions, and the middle of
the axis is not ordered by level"** — not "kind and level are collinear".

## 5. What it cannot do

The families are measured over **different cell sets** (six cells for three families, two for three, one for two), so
a six-cell family has more room to move than a two-cell one — stated in the module and the reason N1 asks for disjoint
ranges rather than a threshold; the within-family instrument is **weak by construction**, counting sign changes in
spreads that sometimes differ by 1% (inside `erdos_renyi` the four "falls" happen in a window of 1.02× to 1.06×, so
that 4/5 is close to noise); a family's spread at a cell is a ratio of two to eight drawings; the level is a mean over
the drawings whose scatter the spread measures, so the two quantities are not independent; `rho` is the builder's
default throughout; and nothing here is a new measurement — every number comes from artifacts already on the plan's
rows.
