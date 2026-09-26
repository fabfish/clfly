# The "late advantage" is a drawing's at all three points — and growing the corpus flipped two of `e252`'s own claims

*2026-09-26 18:20. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30 --seeds 3 --seed0 0 -q 0.02
--topologies swap0.5,swap2,signshuffle,alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed 1`, one per `rho`
(`--rho 0.95`, `--rho 0.98`), ~11 min apiece, both exit 0 — `runs/e253_cs300_rho095_rs1.json` and `_rho098_rs1.json`,
read by `experiments/e253_two_drawings_at_high_rho.py` (`runs/e253_two_drawings_at_high_rho.json`).*

## 1. The unit: the two remaining points decomposed

This record's headline reading of the ladder's mechanism is that the two-side advantage is **late rather than
high-`rho`** — "1.91× at 0.95, 5.53× at 0.98 and 14.77× at 0.99" — and `e251` had already shown the third point is one
drawing's. A second drawing at each of the first two finishes the decomposition:

| `rho` | drawings | `alloy1` | `erdos_renyi` | single-drawing top step |
|---|---|---|---|---|
| 0.95 | 2 | 0.06927, 0.11206 | 0.13223, 0.13907 | **1.91× → 1.24×** (factor 1.54) |
| 0.98 | 2 | 0.01674, 0.07647 | 0.09253, 0.09448 | **5.53× → 1.24×** (factor **4.47**) |
| 0.99 | 3 | 0.00547, 0.00286, 0.09178 | 0.08078, 0.09434, 0.11575 | 14.77× → 2.22× (factor 6.7, `e251`) |

**W1 MET**: the quoted 5.53× at `rho` 0.98 is one drawing's, by a factor of 4.47 — the same lottery `e251` found at
0.99 (6.7×) and, less violently, at 0.95 (1.54×).

**W2 FALSIFIER FIRED, and on a coincidence that settles the point**: on the new drawings `rho` 0.98 reads **1.24×** and
`rho` 0.95 reads **1.24×** — identical to two decimals — where the corpus's own pair reads 5.53× against 1.91×, a 2.9×
rise. So on that drawing set there is **no `rho` trend at all**, and `e245`'s "the reversal replicates in direction"
has a sibling: the *rise* replicates only across the corpus's particular drawings.

## 2. What the "late advantage" becomes: a direction with a pooling-dependent size

Three ways to pool the same cells, all monotone in `rho`:

| pooling | `rho` 0.95 | `rho` 0.98 | `rho` 0.99 | rise |
|---|---|---|---|---|
| the corpus's own single drawing | 1.91× | 5.53× | 14.77× | **7.7×** |
| mean of the per-drawing ratios | 1.57× | 3.38× | 16.32× | **10.4×** |
| ratio of the pooled means | 1.50× | 2.01× | 2.91× | **1.94×** |

**The direction survives every pooling and the size does not**: the "late advantage" is somewhere between a doubling
and a ten-fold rise depending on which drawing or which average you look at, and the ten-fold form is inflated by one
drawing at `rho` 0.99 whose `alloy1` is 0.00286 — 28× below the other two there. The robust form, the ratio of the
pooled means, gives **1.94×** across the whole `rho` range, against the 7.7× the record quotes. So the honest sentence
is: **destroying both degree sequences buys more than destroying one, increasingly so as `rho` rises, and how much
more is 1.9× to 10× depending on the drawing.**

One more measured fact: the one-side **level** moves with the drawing as much as the ratio does at high `rho` —
`alloy1` at `rho` 0.98 reads 0.01674 on the corpus's drawing and **0.07647** on the new one, a factor of 4.6 — so the
collapse `e233` measured is a drawing-level fact there, not only a `rho`-level one.

**W4 reported**: `rho` 0.98 is now **outside** `e252`'s declared domain (max family scatter 4.57×) while `rho` 0.95 is
inside it (1.62×), so the domain's excluded set is now two cells.

## 3. The surprise: growing the corpus flipped two of `e252`'s own claims

`e252` registered, one fire ago, that the domain removes **6 of 38** groups and that **exactly three** verdicts move.
With this fire's two cells in the corpus — 44 groups now, and two more cells outside the domain — both of those
**fired**:

    e252 D3  9 of 44 groups removed (20%)          FALSIFIER FIRED -- the bar was 6
    e252 D4  claims that change: K1, K2, R1, R2    FALSIFIER FIRED -- K2 also moved
    e252 D2  K1, R1 and R2 all return to MET       MET
    e252 D1  unchanged: the registered [3.34, 4.15] still moves inside itself

and `e244`'s **K1 went from its null band to FALSIFIER FIRED outside the domain** (kind 1's median 1.461× now exceeds
kind 0's 1.449×), which is why four claims move inside it rather than three.

That is the domain unit's subject matter happening to the domain unit: **the rule is stable and the numbers it reports
are not**, because a claim whose support is a *count* ("6 groups", "three verdicts") is corpus-dependent by
construction. The lesson is the same one `e252` drew about thresholds, one level up: *report the membership and the
share, not the count* — the excluded cells are `rho` 0.98 and 0.99 and the moved claims are those the near-critical
regime demotes, whichever ones they turn out to be.

## 3b. And it collapses `e230`'s cs-300 half, which was quoted in the paper

`e230`'s audit — quoted in the plan and in the paper as *"at cs 300 all four families' rank contrasts resolve their own
drawing scatter (7.68× to 25.25× against 1.06× to 2.73×)"* — reads very differently with a second drawing at `rho` 0.95
and 0.98, because **those contrasts were read off one drawing per `rho` value too**:

| cs 300 family | rho contrast, as read | its own scatter at `rho` 0.9 | verdict |
|---|---|---|---|
| `alloy1` | **1.51×** (was 25.25×) | 2.73× | **NOT RESOLVABLE** |
| `inalloy1` | **1.31×** | 2.08× | **NOT RESOLVABLE** |
| `swap0.5` | **4.05×** | 8.77× | **NOT RESOLVABLE** |
| `swap2` | **1.18×** | 7.77× | **NOT RESOLVABLE** |
| `signshuffle` | 1.21× | 1.19× | resolvable, by 2% |
| `erdos_renyi` | 1.16× | 1.06× | resolvable, by 9% |
| cs 800 `inalloy1` | 45.14× | 8.02× | resolvable (unchanged) |
| cs 800 `erdos_renyi` | 15.34× | 3.21× | resolvable (unchanged) |

**Five of the six cs-300 families are now unresolvable and `e230` declares them** (its `DECLARED_UNRESOLVABLE` grew
from one entry to five, with the cause recorded on each). So the cs-300 half of that sentence is withdrawn and the
cs-800 half is untouched — which is `e247`'s "the spread is half sample size" arriving a second time, now for the
*rank* contrast and at the very cell where the mechanism reading was strongest.

That is the fourth headline withdrawal of this session's spread line (the rank contrast, the size effect, the late
advantage, and now the cs-300 rank contrasts), and it came from two runs that were not looking for it.

## 4. What it cannot do

Two drawings per cell is **one difference and not a distribution**, and `e247` measured a two-drawing spread to be the
corpus's noisiest statistic — so a factor of 4.47 here is evidence about that pair, and the 1.24-against-1.24
coincidence is one pair's agreement rather than a proven absence of trend. `rho` 0.95 and 0.98 are different task
**geometries** as well as different scalars, so the two runs are not a controlled contrast. One run per `rho` leaves the
kind-0 families with one drawing each, so no (1, 0) margin is computable at either cell and this unit says nothing about
it. The corpus's drawings are `rewire_seed` 0 and the new ones seed 1. And the pooling table's three forms are three
arithmetic choices over the same few numbers, so it bounds the claim rather than measuring a quantity.
