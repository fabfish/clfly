# Registered: the census's own work list — a second drawing at cs 300 with `rho` 0.5, 0.7 and 0.8

*2026-09-26 18:55, registered before its runs. Runs: `e2_topology_gap` at `--circuit-size 300 --support 30 --seeds 3
--seed0 0 -q 0.02 --topologies alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed 1` — **three runs, one per
`rho`: 0.5, 0.7 and 0.8**, to be written as `e255_cs300_rho050_rs1.json`, `_rho070_rs1.json` and `_rho080_rs1.json`.
The ladder families only, because the two figures the census flags are rank-curve figures.*

## 1. Why these three cells, and what the census said

`e254` classified the record's twelve quoted figures by how many drawings their inputs have and found **two still
exposed, both through the same three cells**: cs 300/support 30 at `rho` **0.5, 0.7 and 0.8**, each carrying **one
drawing per family**. The exposed figures are

    the rank curve falls monotonically in rho          (its low end rests on those three cells)
    the cs-300 rank contrasts resolve 7.68x to 25.25x  (withdrawn by e253 for rho >= 0.95, and the low end unchecked)

and the census's work list is one run per cell. Three runs of three topologies at cs 300 are **≈15 min**.

The corpus's single drawings there, so the prediction is checkable both ways:

| `rho` | `alloy1` rank | `inalloy1` rank | `erdos_renyi` rank | `alloy1` excess | `erdos_renyi` excess |
|---|---|---|---|---|---|
| 0.5 | 26.52 | 25.82 | 26.75 | 0.02940 | 0.02452 |
| 0.7 | 22.96 | 22.86 | 25.23 | 0.08417 | 0.07702 |
| 0.8 | 17.54 | 19.77 | 23.08 | 0.11987 | 0.12259 |

**Note the ceiling**: the support is 30 neurons, so at `rho` 0.5 a rank of 26.52 has little room above it — the drawing
noise there can only go down. That asymmetry is why R1 asks for a difference in either direction rather than a rise.

## 2. The registered claims

- **R1 — the low-`rho` end has drawing noise too, or it does not.** At **at least one** of the three cells, the new
  drawing's `alloy1` effective rank differs from the corpus's single-drawing value by a factor of **1.5 or more**, in
  either direction. **Falsifier**: all three within **±10%** — the low-`rho` rank levels are stable, so the rank curve's
  low end was safe all along and the census's flag was a count rather than a risk; **null**: every cell between 1.1
  and 1.5, so the noise is real but small.
- **R2 — the monotone fall survives one more drawing.** On the new drawings, `alloy1`'s rank still falls from `rho` 0.5
  to 0.8 to 0.9 — i.e. rank(0.5) > rank(0.8) > rank(0.9), where the last of those is the three-drawing `rho`-0.9 cell.
  **Falsifier**: a reversal, which would put the curve's monotonicity at the mercy of the drawing rather than the
  scalar.
- **R3 — reported, not claimed.** Both drawings' ranks and excesses at all three cells, the low end's decomposition,
  and the spreads the second drawing buys.
- **R4 — reported.** `e254` re-run: whether the two exposed figures become DECOMPOSED, and what the census's counts
  look like afterwards.

## 3. Cost, and what it cannot do

**Cost**: cs 300's cells have run at ≈93 s for the four-cell ladder and 120 s for four at one `rho`, so three
topologies are **≈5 min per run, ≈15 min for three**.

It cannot: give a distribution — two drawings per cell is one difference, and `e247` measured a two-drawing spread to
be the corpus's noisiest statistic; test the *kind-0* families at those `rho` values, which are not drawn there at all,
so the (1, 0) margin's low-`rho` behaviour stays unmeasured; separate `rho` from the task geometry it sets; or speak
for cs 800's low-`rho` cells, which the same census leaves thin (three families at one drawing each at `rho` 0.5, 0.7
and 0.8) and which this unit does not touch — so closing these three closes *one* of the corpus's two thin regions.
