# The third cell: the margin sits inside the interval on a consistent footing and fires the falsifier on the scale it was first registered against

*2026-09-26 16:20. Runs: `e2_topology_gap` at `--circuit-size 800 --support 20 --seeds 3 --seed0 0 -q 0.02
--topologies swap0.5,swap2,signshuffle --no-realized --rewire-seed {4,5}` — **two runs, one cell each, ~12 min
apiece, both exit 0**, written as `runs/e249_cs800_sup20_kind0_rs4.json` and `_rs5.json` and read by
`experiments/e249_third_cell_margin.py` (`runs/e249_third_cell_margin.json`).*

## 1. The base, and the two registrations

cs 800/support 20's kind-1 and kind-2 families carry **exactly two excess drawings** each, so two runs of the three
kind-0 families make the cell **equal-count at two with no subsetting**:

| family | kind | keys | excesses | spread | rank spread |
|---|---|---|---|---|---|
| `swap0.5` | 0 | 4, 5 | 0.03848, 0.05415 | 1.407× | 3.21× |
| `swap2` | 0 | 4, 5 | 0.04653, 0.02329 | 1.998× | 4.34× |
| `signshuffle` | 0 | 4, 5 | 0.02798, 0.03354 | 1.199× | 1.06× |
| `alloy1` | 1 | 0, 1 | 0.09440, 0.06072 | 1.555× | 4.90× |
| `inalloy1` | 1 | 0, 1 | 0.07805, 0.07249 | **1.077×** | 1.18× |
| `erdos_renyi` | 2 | 0, 1 | 0.16335, 0.15903 | **1.027×** | 1.01× |

Two claims were registered for this cell, and they judge **the same cell's margin on two different scales** — T1
against the *all-drawings* margins of the reference cells (1.008 and 2.044), T1b against the same statistic computed
at **two** drawings everywhere (0.851 and 1.660). **They disagree, and both are reported.**

**T1 FALSIFIER FIRED.** The margin is **0.935** — below the 1.05 falsifier, i.e. at this cell the no-destruction
families are *looser* than the one-side ones, so the margin does not interpolate the all-drawings story at all.

**T1b MET.** On the consistent footing 0.935 lies **strictly inside (0.851, 1.660)**, the interval the same statistic
spans at cs 300/support 30 and cs 800/support 80.

That split is the whole reason T1b exists: writing the reader exposed that T1's bars were drawn on a different scale
from the quantity they judged, and T1b was registered at 15:52 **while both runs were still running and no artifact of
theirs existed**. The correction is vindicated in the sense that matters — the two readings of one number point
opposite ways, and the record carries both rather than the flattering one.

**T2 MET, by 5%.** `erdos_renyi` at **1.027×** is the tightest family, and `inalloy1` at **1.077×** is the closest any
one-side family has ever come to it in this corpus (the next closest is 1.19× at cs 800/support 160).

## 2. The three cells on one footing

    cs 300/support 30   margin 0.851   kind-1 rank spreads 2.73x, 2.08x
    cs 800/support 20   margin 0.935   kind-1 rank spreads 6.28x, 2.21x
    cs 800/support 80   margin 1.660   kind-1 rank spreads 14.08x, 8.02x

(the margins are all computed at **two** drawings per family; the rank spreads beside them are each cell's kind-1
rank spreads over **all** its rank drawings, the quantity the census already carries)

**The margin rises monotonically with the cell's rank contrast** — 0.851, 0.935, 1.660 against rank spreads that grow
from 2.4× to 3.4× to 11× — and that is the first three-point support for the reading `e247`'s R3 left as the only
survivor after the support share and the circuit size were ruled out. Three qualifications belong with it, and they
weigh more than the support does:

- **The margin moves less than the rank contrast does.** 1.660 ÷ 0.851 is **1.95×** while the alloy1 rank spread
  grows 14.08 ÷ 2.73 = **5.16×**, so the excess margin is a weak correlate of the geometry, not a rescaled version of it.
- **Two of the three cells put the NO-destruction rung looser**, which is the pooled ordering `e244`'s K1 asserts, and
  only the cell with the largest rank contrast reverses it. So among the five readings of this pair that are
  count-matched, the reversal is now **1 of 3 cells** rather than the "2 of 2 in direction" `e245` reported — the
  statement narrows again, to "the reversal is what happens at the cell whose geometry has collapsed", and cs
  800/support 80 is that cell (its kind-1 rank spreads are 14.08× and 8.02× against 2.73× and 2.08× at cs 300).
- **Three points is a trend and not a relation**, and the two quantities are read off the **same** drawings, so they
  are not independent variables; what this run bought is one more cell on a consistent footing, not a mechanism.

One more measured fact belongs here, because it bears on the confound every fire since `e244` has had to state:
**cs 800/support 20 has the smallest level gap in the corpus** — its kind-0 families sit at 0.023 to 0.047 and its
kind-1 families at 0.054 to 0.083, a factor of 1.8, against 2× to 5× at cs 300/support 30 and cs 800/support 80. The
cell where the levels are most nearly matched is one of the two that give the pooled direction, which is consistent
with the level and the kind pulling the same way rather than against each other.

## 3. What it cannot do

Three cells is not a relation; the rank contrast is confounded with whatever else each cell is (and with the support
and the size, which `e247` showed do not order the spread on their own); two drawings per family is the corpus's
noisiest count, and `e247` measured that a two-drawing spread is unstable; the three kind-0 families share each run's
single `rewire_seed`; the base is equal-**count** and not equally **drawn**, since the kind-1 and kind-2 drawings come
from `e241`; one `rho` (the builder's default); the 1.05/2.50 bars were fixed before the run and the 0.851/1.660
interval was fixed mid-flight — both are conventions, and a margin of 0.935 would read differently under a ±5% one;
and the comparison remains one of spreads, not levels.
