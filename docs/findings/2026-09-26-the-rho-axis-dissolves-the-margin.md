# The `rho` axis dissolves the margin — and the register's own 14.77× with it

*2026-09-26 17:30. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30 --rho 0.99 --seeds 3 --seed0 0 -q 0.02
--topologies swap0.5,swap2,signshuffle,alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed {3,4}` — **two runs, one
cell each, ~13 min apiece, both exit 0**, written as `runs/e251_cs300_rho099_rs{3,4}.json` and read by
`experiments/e251_rho_axis_margin.py` (`runs/e251_rho_axis_margin.json`).*

## 1. The verdicts, and the two registrations disagreeing

| claim | what it said | verdict |
|---|---|---|
| **V1** | the count-two margin at `rho` 0.99 is above 0.851 (the `rho` 0.9 value at the same cell) | **FALSIFIER FIRED** — margin **0.529** |
| **V1b** | the same claim on the equally-drawn pair, each family's two newest drawings | **MET** — margin **4.298** |
| **V2** | the cell's kind-1 rank spreads are above 2.73× and 2.08× | **MET** — 4.76× and 2.72× |
| **V3** | `erdos_renyi` is the tightest of the six | **MET** — 1.168× against 1.910× to 8.386× |

**The two margins are the same cell, the same statistic and different pairs of drawings, and they differ by a factor of
8.1.** V1b was registered while the runs were in flight precisely because this cell can be read equally drawn; it is
not a correction of V1, it is the second reading that shows the quantity is not there.

## 2. Why: at `rho` 0.99 the one-side families' own scatter explodes

Each family's excesses at the cell, against the same cell at `rho` 0.9:

| family | kind | `rho` 0.99 excesses | span | `rho` 0.9 span |
|---|---|---|---|---|
| `swap0.5` | 0 | 0.00166, 0.00443 | 2.66× | 2.81× |
| `swap2` | 0 | 0.00205, 0.01720 | **8.39×** | 1.41× |
| `signshuffle` | 0 | 0.01004, 0.04165 | 4.15× | 1.39× |
| **`alloy1`** | 1 | 0.00547, 0.00286, **0.09178** | **32.04×** | 1.49× |
| **`inalloy1`** | 1 | 0.00825, 0.02046, 0.07412 | **8.98×** | 1.35× |
| `erdos_renyi` | 2 | 0.08078, 0.09434, 0.11575 | **1.43×** | 1.03× |

The one-side level collapses by roughly **20×** (alloy1's three-drawing mean 0.11919 → 0.03337) and its drawing scatter
grows from 1.35–1.49× to **9–32×**, while the two-side family's scatter barely moves (1.03× → 1.43×) and its level only
halves (0.157 → 0.097). So the (1,0) margin at this cell is a ratio of two quantities whose own noise is larger than
the thing being compared — which is exactly what `e247` showed a two-drawing spread to be.

## 3. And it takes the register's own headline with it

This cell at this `rho` is where the record's largest quoted top step comes from: `e233`'s "Erdős–Rényi over `alloy1`
is 1.91× at `rho` 0.95, 5.53× at 0.98 and **14.77×** at 0.99". Decomposed by drawing:

    the corpus's own rho-0.99 drawing (seed 0)   0.08078 / 0.00547 = 14.77x   <- the quoted figure
    the two new drawings  (seeds 3 and 4)        0.09434, 0.11575 / 0.00286, 0.09178 = 2.22x
    all three drawings pooled                                                 2.91x

**The largest top step in this record is one drawing's arithmetic.** Two more drawings at the same cell and the same
`rho` read **2.22×**, a factor of **6.7** away, and the three pooled read 2.91×. Since `e233`'s rho-0.95 and rho-0.98
points (1.91×, 5.53×) rest on single drawings too, the whole "the two-side advantage is *late*, not high-`rho`" reading
is a statement about one drawing per cell — and the same lottery that made the margin 0.529 against 4.298.

This is a **withdrawal** in the same spirit as the earlier ones in this line, and it is the sharper half of this fire's
result: the rho axis did not extend the four-cell relation, it identified the regime in which the record's own
headline quantity stops being a property of the cell.

## 4. What survives, and the relation's domain

**V3 is the survivor again, and it is the sharpest statement of it yet.** `erdos_renyi` is the tightest family at
`rho` 0.99 by a wide margin (1.168× against 1.910× to 8.386×) and it is the only family whose own drawing scatter
stays small there (1.43× where the one-side families are 9× and 32×). The two-side family's *level* also collapses far
less than the one-side ones (0.157 → 0.097 against 0.119 → 0.033), which is `e231`'s "`erdos_renyi` does not collapse"
seen on three drawings rather than one.

**And the four-cell relation now has a stated domain**: the margin was measurable at cs 400/support 40, cs 300/support
30, cs 800/support 20 and cs 800/support 80 because at each of them the one-side families' own drawing scatter was
**1.06× to 3.34×**; at `rho` 0.99 it is **8.98× and 32.04×** and the margin reads 0.529 or 4.298 depending on which
two drawings are picked. So the honest form of `e250`'s monotone relation is: **it holds where the one-side scatter is
a few tens of percent, and it is undefined where it is a factor of ten** — which is a claim about where to measure
rather than about what drives it.

## 4b. And it demotes three earlier verdicts, which is this fire's thesis as a consequence

Adding this cell to the censuses moves **three pooled claims that earlier fires recorded as MET**:

| claim | before this fire | with the `rho`-0.99 cell in |
|---|---|---|
| `e244`'s **K1** — kind 0 loosest, kind-2 and kind-0 ranges disjoint | MET | **null band**: kind 2's range [1.021, 1.433] now overlaps kind 0's [1.072, 8.386] |
| `e247`'s **R1** — count-matching halves the one-side spans (bars 2.5× and 2.0×) | MET (3.04× → 2.36×, 2.43× → 1.83×) | **FALSIFIER FIRED** (29.17× → 15.33×, 8.46× → 3.47×) |
| `e247`'s **R2** — count-matching dissolves `e246`'s N1 (separation 1.004×) | MET | **FALSIFIER FIRED** (separation 1.879×) |

And `e246`'s **N1**, whose dissolution R2 had asserted, now reads **MET with a wider gap than ever** — the one-side
families span 8.46× to 29.17× across cells where the other four span 1.40× to 6.11×.

So the honest form of `e247`'s and `e244`'s conclusions is that **they were corpus-dependent**: one near-critical cell
with a ten-to-thirty-fold drawing scatter moves three of them. A pooled verdict that flips with the next run is better
reported as a **domain** — "this holds for cells whose families scatter by a few tens of percent" — than as a verdict,
and declaring that domain is the natural next unit rather than another cell.

## 5. What it cannot do

It cannot say the relation is *wrong* along `rho`, only that this design cannot read it there: one `rho` point above
the regime, two drawings per family, and no measurement of how many drawings would be needed to stabilise the cell (a
six- or ten-drawing base at `rho` 0.99 is the obvious next design, and `e243`'s three-drawing addition already showed
how much a few drawings can move a two-drawing statistic). The driver and the margin are still computed from the same
drawings, so V2's "the rank contrast rose too" is consistency and not mechanism. And the decomposition of the 14.77×
is on **three** drawings — enough to show the figure is a drawing's, not enough to say what the cell's value is.
