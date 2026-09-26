# The fourth cell: the (1, 0) margin is monotone in the cell's rank contrast on both footings

*2026-09-26 17:00. Runs: `e2_topology_gap` at `--circuit-size 400 --support 40 --seeds 3 --seed0 0 -q 0.02
--topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed {3,4,5}` — **three runs, one cell each, ~9 min
apiece, all exit 0**, written as `runs/e250_cs400_sup40_kind0_rs{3,4,5}.json` and read by
`experiments/e250_second_count_three_base.py` (`runs/e250_second_count_three_base.json`).*

## 1. The base

cs 400/support 40's kind-1 and kind-2 families already carried three excess drawings each and it had **no kind-0
family at all**, so three runs gave a base on the **same footing as `e248`'s** — six families, three drawings each:

| family | kind | excesses | spread | level |
|---|---|---|---|---|
| `swap0.5` | 0 | 0.03217, 0.03001, 0.03503 | 1.167× | 0.03240 |
| `swap2` | 0 | 0.03062, 0.02231, 0.02866 | 1.373× | 0.02720 |
| `signshuffle` | 0 | 0.04205, 0.08707, 0.06999 | **2.071×** | 0.06637 |
| `alloy1` | 1 | 0.13859, 0.12618, 0.13808 | **1.098×** | 0.13428 |
| `inalloy1` | 1 | 0.13249, 0.13014, 0.12480 | **1.062×** | 0.12914 |
| `erdos_renyi` | 2 | 0.15015, 0.15497, 0.14779 | **1.049×** | 0.15097 |

## 2. Verdicts

**U1 MET.** The (1, 0) margin is **0.787** against the cs 300/support 30 base's **1.008** *read on the same footing* —
below the reference and below 1, so the flatter geometry gives the smaller margin and the **no-destruction rung is the
looser one**. At this cell kind 0's median (1.373×) is above *both* kind-1 families (1.098×, 1.062×), which is the
clearest the pooled K1 direction has been anywhere in this line.

**U2 MET by 1.2%.** `erdos_renyi` at 1.049× is the tightest family, and `inalloy1` at **1.062×** is the closest any
one-side family has yet come to it — closer than at cs 800/support 20 (1.077×) one fire ago, and further down the
ladder of margins than anywhere else in the corpus.

## 3. The relation, now four cells and two footings

Because `e243`'s drawings had also pushed `signshuffle` to three drawings at cs 800/support 80, that cell now carries a
count-three base too, so the margin can be read on **two footings** at up to four cells. The candidate driver is the
cell's kind-1 rank contrast (the geometric mean of the two kind-1 rank spreads), which is measured for every cell:

| cell | kind-1 rank spreads | rank contrast | margin at 3 drawings | margin at 2 drawings |
|---|---|---|---|---|
| cs 400/support 40 | 1.53×, 1.59× | **1.56** | **0.787** | 0.771 |
| cs 300/support 30 | 2.73×, 2.08× | **2.38** | **1.008** | 0.851 |
| cs 800/support 20 | 6.28×, 2.21× | **3.72** | — (kind 0 has two) | 0.935 |
| cs 800/support 80 | 14.08×, 8.02× | **10.63** | **1.714** | 1.660 |

**Both footings are monotone**: at three drawings 0.787 < 1.008 < 1.714 in rank order, and at two drawings
0.771 < 0.851 < 0.935 < 1.660 across all four cells. That is the strongest form this relation has taken — four cells,
two independent footings, no inversion — and it is the low end `e249` was missing.

**But the two qualifications `e249` recorded both survive, and one is now sharper.** The margin spans
**0.771 to 1.714 (2.2×)** while the rank contrast spans **1.56 to 10.63 (6.8×)**, so the excess margin remains a weak
correlate of the geometry rather than a rescaled copy of it (1.660 ÷ 0.851 = 1.95× against 5.16× before this fire).
And the direction count barely moves: **three of the four cells put the no-destruction rung looser** — the pooled K1
direction — with only cs 800/support 80, whose geometry is the most collapsed, reversing it. `e245`'s "the reversal
replicates in direction at 2 of 2 cells" is now **1 of 4**.

## 4. The two-side family's spread advantage nearly vanishes where its level advantage is largest

The one statement that has survived every audit in this line — `erdos_renyi` is the tightest family — is also the one
whose *margin* the flat cells erode:

| cell | `erdos_renyi` | tightest one-side family | ratio |
|---|---|---|---|
| cs 400/support 40 | 1.049× | `inalloy1` 1.062× | **1.012×** |
| cs 800/support 20 | 1.027× | `inalloy1` 1.077× | 1.048× |
| cs 800/support 80 | 1.050× | `inalloy1` 1.236× | 1.178× |
| cs 300/support 30 | 1.032× | `inalloy1` 1.353× | 1.311× |

The two flattest-geometry cells are the two where the two-side family's **spread** advantage is nearly gone (1.012× and
1.048×), and its **level** advantage is largest there (0.151 against 0.129, a factor of 1.17, where cs 800/support 80
has 0.144 against 0.066). So "the two-side family is the tightest" is true everywhere and is *nearly nothing* at the
cells where the ladder's level story is strongest — the same decoupling between level and spread that every fire since
`e244` has had to state, now measured from the survivor's side rather than the casualty's.

## 5. What it cannot do

Four cells with a driver read off **the same drawings** as the quantity it would explain is still not a mechanism —
the rank contrast and the excess spread are two readings of one set of drawings, and nothing here rules out that both
follow a third, unmeasured cell property. The level confound survives (kind 0 near the floor at 0.031 to 0.066 against
kind 1's 0.124 to 0.139 here). The base is equal-**count** and not equally **drawn**. Each cell is one `rho` (the
builder's default, `config.rho: None`), and the two footings are two points in the corpus's support-and-size grid, not
a designed sweep of either. And the margin's own range is small enough that a single drawing moving by 20% could
reorder two adjacent cells — which is exactly what `e247` measured about two-drawing spreads.
