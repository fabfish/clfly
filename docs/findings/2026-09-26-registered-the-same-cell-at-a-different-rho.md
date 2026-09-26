# Registered: the same cell at a different `rho` — the relation's second axis

*2026-09-26 17:20, registered before its runs. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30 --rho 0.99
--seeds 3 --seed0 0 -q 0.02 --topologies swap0.5,swap2,signshuffle,alloy1,inalloy1,erdos_renyi --no-realized
--rewire-seed {3,4}` — **two runs, one cell each**, to be written as `e251_cs300_rho099_rs{3,4}.json`. Two runs because
the base being read is the **count-two** one, whose margin already has four readings to be compared against.*

## 1. The gap this fills

The (1, 0) margin has been read at four cells and is **monotone in the cell's kind-1 rank contrast on both footings**
(`e250`: margins 0.787, 1.008, 1.714 at three drawings and 0.771, 0.851, 0.935, 1.660 at two, against rank contrasts
1.56, 2.38, 3.72 and 10.63). Every one of those cells varies **size, support and the cell's identity at once**, and the
driver is computed from **the same drawings** as the quantity it would explain — so the relation has never been
separated from "which cell is it".

The one axis that holds the size and the support fixed and moves the task geometry is `rho`, the assembly geometry's
target spectral radius, and the corpus already has **eight cells** of it at cs 300/support 30 (0.5, 0.7, 0.8, 0.9,
0.95, 0.98, 0.99) — but the ladder families have **exactly one drawing at every `rho` except 0.9**, so no spread can
be computed there and **the kind-0 rung has never been drawn off `rho` 0.9 at all**. Two runs of all six families at
`rho` 0.99 give two drawings each at the same size and support as `e248`'s base, and therefore a margin on the same
**count-two** footing as four existing readings.

## 2. The registered claims

- **V1 — the margin moves with `rho` the way the relation says.** The count-two (1, 0) margin at cs 300/support 30
  with `rho` 0.99 is **above 0.851**, the value the same statistic takes at the same cell with `rho` 0.9. **Falsifier**:
  at or below 0.851 — no rise at all, so the margin does not move with the one axis that holds everything else fixed,
  and the four-cell relation is about which cell it is rather than about the geometry. **Null**: above 0.851 but below
  0.90, i.e. a rise inside the noise this corpus has already measured for two-drawing spreads.
- **V2 — the driver moves too.** At `rho` 0.99 the cell's kind-1 rank spreads are **above** the 2.73× and 2.08× it
  reads at `rho` 0.9 — the near-collapsed geometry scattering more across drawings than the rho-0.9 one. **Falsifier**:
  below either, in which case the driver and the margin move in opposite directions along this axis and the four-cell
  ordering was a coincidence of the cells.
- **V3 — the survivor.** `erdos_renyi` is the tightest of the six families at `rho` 0.99.
- **V4 — reported, not claimed.** Every family's two excesses and ranks at `rho` 0.99, the same six at `rho` 0.9, and
  both margins, so the axis can be read directly.

## 3. Cost, and what it cannot do

**Cost**: cs 300's cells measured 372 s for four cells (≈93 s each) and 120 s for four at one `rho`, so six topologies
are ≈9 min per run and **two runs ≈20 min** — one fire's wait.

It cannot: make the driver independent of the margin, since both are computed from **the same two drawings** at
`rho` 0.99 — the same-drawings objection survives this design and only a second *instrument* (an independent way to
measure the geometry's drawing noise, e.g. from the connectome side rather than the task side) would remove it;
separate `rho` from the task's near-critical regime, since `rho` 0.99 is also where the one-side level collapses
18× past its peak (`e233`); speak for the three- or four-drawing footings, since two drawings is the corpus's noisiest
count and `e247` measured how unstable a two-drawing spread is; give more than **one** new `rho` point, so a
monotone-in-rho claim would still rest on a single axis step; or make the base equally **drawn**, the two runs being
new drawings against `e248`'s at another `rho`.
