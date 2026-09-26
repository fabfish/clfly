# The rank contrast meets its own drawing scatter: cs 800's `alloy1` cannot resolve it, and volatility is a property of the family

*2026-09-26 09:25, `runs/e230_rank_draw_census.json` through `e230_rank_draw_census.py`, over the **65 artifacts** that
carry a `geometry` block (40 (circuit size, topology) families). The audit asks one question of the claim the last
two fires built: **is the task geometry's `effective_rank` contrast between `rho` values larger than the family's own
scatter across drawings?** Every point of that claim was one drawing.*

## 1. The families that have drawings, and what their scatter is

`within` is the spread of `effective_rank` across the drawings on disk at `rho = 0.9`; `between (as read)` is the
largest-to-smallest ratio over the `rho` values that carry a **single** drawing, which is exactly what a
one-drawing-per-`rho` grid quotes.

| size | topology | drawings at 0.9 | within | between (as read) | between (means) | verdict |
|---|---|---|---|---|---|---|
| 300 | `alloy1` | 4 | 2.73× | 25.25× | 25.25× | RESOLVABLE |
| 300 | `inalloy1` | 4 | 2.08× | 23.53× | 23.53× | RESOLVABLE |
| 300 | `erdos_renyi` | 4 | 1.06× | 7.68× | 7.68× | RESOLVABLE |
| 300 | `real` | 2 | 1.98× | 3.76× | 4.55× | RESOLVABLE |
| 800 | `alloy1` | **12** | **16.44×** | **3.01×** | 5.83× | **NOT RESOLVABLE** |
| 800 | `inalloy1` | 7 | 4.14× | 44.79× | 44.79× | RESOLVABLE |
| 800 | `erdos_renyi` | 14 | 2.64× | 15.34× | 15.34× | RESOLVABLE |
| 800 | `real` | 4 | 1.01× | 5.64× | 5.64× | RESOLVABLE |

## 2. What survives, and what does not

- **The cs-300 half of the mechanism reading stands, comfortably.** All four families there resolve their `rho`
  contrast: `alloy1` 25.25× against a 2.73× scatter, `inalloy1` 23.53× against 2.08×, `erdos_renyi` 7.68× against
  1.06× (the tightest family in the corpus), `real` 3.76× against 1.98×.
- **The cs-800 half is half-supported.** The family that *collapses* — `inalloy1`, whose out-structure is destroyed —
  resolves its contrast by a factor of ten (44.79× against 4.14×), so **the collapse is real**. The family it was
  compared *against*, `alloy1`, does not: its twelve drawings span **16.44×** while the single-drawing contrast the
  record read is **3.01×** — so *"the two families come apart by 16.4× at cs 800"* is a statement about **which
  drawing of twelve** was taken.

So the last fire's sentence has to be split, and it is: **the out-side collapse at high `rho` is measured; the
comparison that made it "directional" is not.**

## 3. The pattern worth carrying: volatility belongs to the family, not to the statistic

| family at cs 800 | rank spread over its drawings | penalty spread over its drawings |
|---|---|---|
| `alloy1` | **16.44×** (12 drawings) | 3.34× (5) |
| `inalloy1` | 4.14× (7) | 1.24× (3) |
| `erdos_renyi` | 2.64× (14) | **1.05×** (3) |
| `real` | **1.01×** (4) | — (identical by construction) |

The same ordering appears on **both** statistics: the family whose *task geometry* is drawing-volatile is the family
whose *penalty* is drawing-volatile, and the two that are tight are tight on both. That is the useful generalisation —
**a family's volatility is a property of the construction, not of what you measure about it** — and it is what makes
the corpus's per-family scatter a precondition for the next claim rather than a surprise.

## 4. Correction to the previous fire's mechanism finding

`docs/findings/2026-09-26-the-top-steps-rho-dependence-is-not-the-alignment-contrast.md` read the rank contrast as
"monotone together" with the penalty and left it as the mechanism lead. That reading is **resolvable at cs 300 and
not at cs 800 for `alloy1`**, as measured here. The alignment part of that finding is untouched (the alignment
contrast spans 1.13–1.56× across cells, and no drawing scatter would make it 11–15×). The rank part is now:
*resolvable at cs 300, resolvable for the collapsing family at cs 800, and a drawing for the other one.*

## 5. What this cannot do

- **One statistic.** Nothing here says a *penalty* contrast at cs 800/`alloy1` is unresolvable; the penalty's own
  scatter (3.34×) is smaller than its own rho contrast.
- **The within-scatter is measured at `rho` 0.9 only** — that is where the corpus has drawings — so a family could be
  tighter at another `rho`, and a design that wants to know must draw more there.
- **The drawings are not independent of write time**, so a family whose drawings straddle a code epoch inherits that
  (`e227`'s drift); this audit attributes no scatter to a cause.
- **RESOLVABLE is not CORRECT**: it says the design could have seen an effect that large, not that the effect is one.
