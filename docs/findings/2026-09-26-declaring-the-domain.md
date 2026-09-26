# Declaring the domain: three of eleven pooled spread verdicts are domain-sensitive, and my own bar was drawn from rounded prints

*2026-09-26 17:50. Runs: **none new** — `experiments/e252_spread_domain.py` re-reads every pooled claim of `e244`,
`e246` and `e247` inside a declared domain, written as `runs/e252_spread_domain.json`. JSON-only, seconds.*

## 1. The rule, and why it is not taste

`e251` found the (1, 0) margin undefined at `rho` 0.99 (0.529 on one pair of drawings, 4.298 on another) and recorded
that adding that one cell **demoted three pooled verdicts** earlier fires had called MET. A verdict that flips when the
next run lands is a statement about which cells happen to be in the corpus, so this module declares the domain openly:

    a cell is IN the domain when every family measured there scatters by at most T across its own drawings

At `T = 4` the corpus splits **6 cells in, 1 out**, and the cell that is out is cs 300/support 30/`rho` 0.99 — the one
`e251` bought:

| cell | groups | max scatter | in? |
|---|---|---|---|
| cs 300/support 30/`rho` 0.9 | 6 | 2.81× | yes |
| cs 300/support 30/`rho` 0.99 | 6 | **32.04×** | **NO** — `alloy1` 32.04×, `inalloy1` 8.98×, `swap2` 8.39×, `signshuffle` 4.15× |
| cs 400/support 40/`rho` 0.9 | 6 | 2.07× | yes |
| cs 400/support 80/`rho` 0.9 | 3 | 1.12× | yes |
| cs 800/support 20/`rho` 0.9 | 6 | 2.00× | yes |
| cs 800/support 80/`rho` 0.9 | 8 | **3.3444×** | yes |
| cs 800/support 160/`rho` 0.9 | 3 | 2.58× | yes |

## 2. Verdicts

**D1 FALSIFIER FIRED — and it fired on my own arithmetic, not on the corpus.** The registration drew the interval of
thresholds that "give the same domain" as **[3.34, 4.15]**, taken from the printed table above. Both ends were wrong:

- the **lower** edge is **3.344431**, not 3.34 — the print rounded the largest in-domain scatter, and at `T = 3.34`
  exactly, cs 800/support 80's `alloy0.9` (3.3444) and `alloy1` (3.3433) fall outside the domain, so that cell is
  excluded too and the domain becomes two cells rather than one;
- the **upper** edge is not 4.15 but **32.04**: 4.15 is the smallest *family* scatter above the bar at the excluded
  cell, while the rule compares the cell's **maximum**, which there is 32.04.

So the corrected statement is: **every `T` in [3.344431, 32.04] gives the same one-cell domain** — a span of 9.6×.
The lesson is one this line will need again: *a threshold must be taken from the value, not from the display, and from
the quantity the rule actually compares.*

**D2 MET.** Inside the domain, **K1, R1 and R2 all return to MET** — exactly what the near-critical cell had demoted.

**D3 MET.** The exclusion removes **6 of the corpus's 38 groups with a spread — 16%** — and leaves 6 of 7 cells.

**D4 MET (blind).** Comparing all **eleven** pooled claims inside and outside the domain, **exactly the three `e251`
recorded move** and no fourth:

    K1  null band    -> MET    <- moved        N1  MET -> MET        R3  MET -> MET
    K2  MET          -> MET                   N2  MET -> MET        R4  MET -> MET
    K3  FALSIFIER    -> FALSIFIER             N3  FALSIFIER -> FALSIFIER   R5  MET -> MET
    R1  FALSIFIER    -> MET    <- moved
    R2  FALSIFIER    -> MET    <- moved

**Three of eleven are domain-sensitive and eight are not.** That is the deliverable: the three should be reported with
their domain attached ("MET for cells whose families scatter by a few tens of percent"), and the other eight can be
reported without one — which is a stronger statement about them than any of the fires that produced them could make.

**The threshold grid says the exclusion is not tuned**: `T` ≤ 2 excludes five cells (and would gut the analysis), every
`T` from 3.344431 to 32.04 excludes the same single cell, and `T` ≥ 32.04 excludes none. So over nine-fold range of `T`
the domain is stable, and it changes only at the two ends where it must.

## 3. What it cannot do

The rule is about **scatter**, not about `rho`, so it would exclude a cell that scatters for any other reason — intended,
and empirical; and the justification for the rule is `e251`'s, measured at one cell. The three readers have different
natural units (groups of two or more drawings for `e244`/`e246`, families per cell for `e247`) and the filter is applied
to each group's cell, so a cell can be in the domain for one reviewer and contribute nothing to another. `T = 4` sits
inside a 9.6× window rather than at a tested boundary, so the domain's *edge* is not itself measured — only its
stability is. The "16% of groups" cost is a count and not a statement about how much information those groups carried.
And the domain makes no claim **stronger** than it was before the near-critical cell arrived: it restores the earlier
readings, and it says so, which is the honest form of an exclusion.
