# The spread is half sample size: count-matching the drift that the last three fires read

*2026-09-26 16:15. Runs: **none new** — `experiments/e247_count_matched_spread.py` re-reads the corpus's per-drawing
excesses and ranks, written as `runs/e247_count_matched_spread.json`. JSON-only, seconds.*

## 1. The thing all three fires shared

`e244` measured each family's spread over however many drawings the corpus had at a cell; `e245` read the (1, 0)
reversal at 2 of 2 comparable cells; `e246` found the cross-cell volatility concentrated in `alloy1` and `inalloy1`.
**A spread is a max-over-min, so a cell with nine drawings has more room to move than a cell with two**, and this
corpus's cells are unevenly drawn — `alloy1` has 2, 3, 3, 4, 4 and 8 drawings, `erdos_renyi` 3, 3, 3, 4, 4 and 9,
`swap0.5` and `swap2` 2 and 6, `signshuffle` 2 and 3. This module re-measures every spread **at a fixed number of
drawings** and asks what is left.

Two count-matched statistics, deliberately, because they disagree:

- **median-of-pairs** — the median spread over all C(n, 2) pairs at the cell: uses every drawing, and a two-drawing
  cell contributes its single pair;
- **two-lowest-seed** — the one pair formed by the two lowest `rewire_seed` drawings: maximally count-matched,
  deterministically chosen, and it discards everything else.

**Disclosure.** Four of the five claims were computed in an exploratory heredoc before the module was written and are
recorded as **confirmatory**; the fifth (**R5**, on the rank observable) was **blind**. The module exists so the
numbers are reproducible and regression-tested rather than living in a transcript.

## 2. Verdicts

**R1 MET — count-matching dissolves part of the one-side drift.** Under the median-of-pairs statistic `alloy1`'s
cross-cell span falls **3.04× → 2.36×** and `inalloy1`'s **2.43× → 1.83×**.

**R2 MET — and it takes `e246`'s N1 with it.** That claim was that the kind-1 range and the others are **disjoint**.
Count-matched, the median-of-pairs separation is **1.004×** (kind 1 spans 1.83× to 2.36×, the others 1.00× to 1.82×)
and the two-lowest-seed ranges **overlap**. The mechanism is that count-matching moves a kind-0 family *up*: `swap0.5`'s
span rises from 1.32× to **1.82×** precisely because its six-drawing cell is tight in the middle (`all` 1.45× against
`pair median` **1.05×**), so its cross-cell span becomes the ratio of two single pairs.

**R3 MET — the cell's own shape does not order the spread.** Over 26 count-matched groups,
Spearman(spread, **support share**) is **−0.074** and Spearman(spread, **circuit size**) **+0.033**. The hypothesis
that the drift tracks a cell-level property — the obvious next step queued after `e246` — is dead at this corpus size.

**R4 MET — and the (1, 0) reversal stops replicating.**

    cs 800/support 80   kind 0 1.12x  against kind 1 1.24x   -> the reversal
    cs 300/support 30   kind 0 1.39x  against kind 1 1.26x   -> the pooled direction

`e245` read that pair as **2 of 2 in the reversal's direction** on all drawings. At exactly two drawings per family
the two cells **disagree**, so "the reversal replicates in direction" is a statement about the larger samples at those
cells rather than about the pair.

**R5 MET (blind) — a drawing's noisiness is shared between the two observables.** Spearman between the
count-matched excess spread and the count-matched rank spread is **+0.724** over 26 groups. A drawing that is noisy
for the penalty is noisy for the task geometry too, which is the first thing in this line that says the drawing's
noise is a property of **the drawing** rather than of the statistic being read off it — and it agrees with `e230`'s
"volatility belongs to the family, not to the statistic" from the other direction.

## 3. What the corpus's quoted spreads become

Per cell, all drawings against the two count-matched statistics (excess):

| family | cell | n | all | pair median | lowest two |
|---|---|---|---|---|---|
| `alloy1` | cs 800/sup 80 | 8 | **3.34×** | **1.64×** | 1.25× |
| `alloy1` | cs 800/sup 160 | 2 | 2.58× | 2.58× | 2.58× |
| `alloy0.9` | cs 800/sup 80 | 5 | **3.34×** | **1.69×** | 1.81× |
| `inalloy1` | cs 800/sup 80 | 6 | **2.58×** | **1.90×** | 1.09× |
| `swap2` | cs 800/sup 80 | 6 | **1.84×** | **1.35×** | 1.12× |
| `swap0.5` | cs 800/sup 80 | 6 | 1.45× | **1.05×** | 1.35× |
| `erdos_renyi` | cs 800/sup 80 | 9 | 1.06× | 1.02× | 1.01× |

**Every one of the corpus's most-quoted spread figures is roughly halved by count-matching**: `alloy1`'s 3.34× (the
number `e215` called the wild one and `e230` called the family's fingerprint) is 1.64× at a two-drawing budget;
`alloy0.9`'s 3.34× is 1.69×; `inalloy1`'s 2.58× is 1.09× to 1.90×; `swap2`'s 1.84× is 1.35×. Since the convention
cell's `alloy1` spread is what several readings in this record rest on, that is the unit's practical result.

**But count-matching does not remove the sampling problem — it relocates it.** The two-drawing cells are the noisiest
in the corpus, and a family whose cells are mostly at two drawings has a count-matched span decided by single pairs:
`alloy1`'s count-matched 2.36× is exactly 2.58 ÷ 1.09, i.e. **one pair at cs 800/support 160 against one pair at
cs 400/support 40**. So the honest form is a **band**, not a number:

    alloy1's cross-cell drift     between 1.6x (two-drawing budget, median-of-pairs) and 3.0x (all drawings)
    inalloy1's                    between 1.2x and 2.4x
    the kind-0 families'          between 1.0x and 1.8x
    erdos_renyi's                 1.02x to 1.04x, unchanged by the budget

Only `erdos_renyi` is unaffected, because its per-cell spreads are 1.01×–1.06× at every budget — its tightness is not
a sample-size effect at all.

## 4. What it cannot do

The two statistics disagree and are reported as disagreeing rather than averaged; a two-drawing spread is a very
noisy estimator, so count-matching buys comparability at the price of precision and the price is visible in `alloy1`'s
2.36×; the drawings' identities still differ between cells (a `rewire_seed` is a fresh draw), so nothing here is a
paired comparison and no cell-to-cell difference is a difference of the same drawings; the rank observable is
count-matched only in R5; `rho` is the builder's default (`config.rho: None` everywhere); and nothing here is a new
measurement — all of it comes from artifacts already on the plan's rows. The strongest counter-consideration is stated
rather than hidden: **the effect `e243` created on purpose was created by the drawings that count-matching discards**
(`inalloy1` at cs 800/support 80 is 2.58× over six drawings and 1.09× over the two lowest-seeded ones), so
count-matching is a correction to the *comparison between families*, not a claim that the extra drawings were noise.
