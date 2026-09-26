# Registered: the cs-800 rank curve's second drawing — does the profile in `rho` hold at the other size?

*2026-09-26 19:30, registered before its runs. Runs: `e2_topology_gap` at `--circuit-size 800 --support 80 --seeds 3
--seed0 0 -q 0.02 --topologies alloy1,inalloy1,erdos_renyi --no-realized --rewire-seed 1`, one per `rho` (0.5, 0.7,
0.8, 0.95, 0.98, 0.99) — **six runs**, to be written as `e256_cs800_rho{050,070,080,095,098,099}_rs1.json`. Six
because cs 800/support 80 carries **one drawing at six of its seven `rho` values**.*

## 1. What the census just found, and what this tests

The censuses of the last two fires measured a **profile of the drawing noise in `rho`** at cs 300/support 30:

    rho 0.5 to 0.8   alloy1's rank moves 0.4% to 9.8% between two drawings   STABLE   (e255)
    rho 0.95, 0.98   the top step moves by factors of 1.54 and 4.47          EXPLODES (e253)
    rho 0.99         alloy1's excess spans 32.04x over three drawings        EXPLODES (e251)

and then, extending its registry, found that **the same rank curve at cs 800 is one-drawing at six of its seven `rho`
values** — the counterpart claim, unchecked:

    cs 800/support 80 single-drawing alloy1 ranks: 63.14 (0.5), 45.83 (0.7), 32.78 (0.8), 22.09 (0.95), 21.24 (0.98), 21.01 (0.99)

Six runs of the ladder families add a second drawing at each, which is the first check of that half and a test of
whether the profile is a property of the **`rho` regime** or of the **size**.

## 2. The registered claims

- **F1 — the low-`rho` end is stable at cs 800 too, which is what the profile predicts.** At each of `rho` 0.5, 0.7 and
  0.8 the new `alloy1` rank is within **±20%** of the corpus's single-drawing value (63.14, 45.83, 32.78). **Falsifier**:
  any of the three moves by **1.5× or more**, which would say the low-`rho` stability `e255` measured at cs 300 is a
  property of that size rather than of the regime — and would put the profile in doubt. **Null**: a factor between 1.2
  and 1.5 at any of them.
- **F2 — the high-`rho` end moves, which is the other half of the profile.** At `rho` 0.95, 0.98 or 0.99 the new
  `alloy1` rank differs from the corpus's value (22.09, 21.24, 21.01) by a factor of **1.5 or more**. **Falsifier**: all
  three within ±10%, which would say the high-`rho` volatility is the *excess* side's alone and the geometry stays put.
  **Null**: every high-`rho` cell between 1.1 and 1.5.
- **F3 — the cs-800 rank curve's fall survives one more drawing.** On the new drawings, `alloy1`'s rank still falls
  from `rho` 0.5 to 0.8 to 0.99 — rank(0.5) > rank(0.8) > rank(0.99). **Falsifier**: a reversal.
- **F4 — reported.** Both drawings' ranks and excesses at all six cells, the cs-300 profile beside the cs-800 one, and
  `e254` re-run: whether the two newly exposed figures become DECOMPOSED.

## 3. Cost, and what it cannot do

**Cost**: cs 800's cells have run at 228–240 s for three seeds without the realized arm, so three topologies are ≈4 min
per run and **six runs ≈24 min** — longer than one fire, so the read lands in the next.

It cannot: give a distribution — two drawings per cell is one difference, and `e247` measured a two-drawing spread to
be the corpus's noisiest statistic; separate `rho` from the task geometry it sets, or from the **size**, since this is
one size and the profile's two halves come from two different sizes; give any kind-0 **spread** at those cells (one run
per rho means one drawing each), so the (1,0) margin is not computable there; test the *excess* side's high-`rho`
behaviour, which `e251`/`e253` did at cs 300; or fix the fact that the corpus's own drawings at these cells are
`rewire_seed` 0 while the new ones are seed 1.
