# Registered: screen by alignment, then pay only for the cells in the band

**Date:** 2026-09-26. **Registered before its run.** Artifacts to be written: `runs/e209_screen_rs0.json` … 
`runs/e209_screen_rs4.json` (one per swap realization).

---

## 1. What the last run established, and what it left open

`e208` put one cell inside the hole — `swap8` at alignment **0.09101** (1.64× chance) with excess **0.00598**, the
lowest value in the record — so the penalty is **flat across a factor of 20 in alignment** (0.006–0.023 from 0.00444 to
0.09101) while the jump to 0.141–0.149 sits in the Erdős–Rényi regime at 4.89–5.23× chance. **The transition is in
[0.09101, 0.27135] and the record has nothing inside it.**

And `e208` also showed *why* the obvious next step is wrong: its three new levels are **not ordered in alignment**
(`swap4` 0.03944, `swap8` 0.09101, `swap16` 0.04146), because alignment at a *fixed* strength spreads widely across
realizations — measured at cs 800: `swap2` **2.60×** (0.03257–0.08475 over six `rewire_seed`s), `swap0.5` 1.68×,
`erdos_renyi` 1.07×. So **adding strengths buys cells whose alignment nobody can predict**, and the hole is a gap in
the record's sampling rather than in the design space.

## 2. The design: two stages, and the second one is paid for only where it is needed

**Stage 1 — the screen (this registration).** Run the topology-gap sweep in its new **`--geometry-only`** mode, which
writes the `geometry` block and **skips all three arms**. A screen cell costs **112 s** against the 225 s of a full
analytic cell (both measured on `swap8`/cs 800/3 seeds this evening), and a screening artifact carries no `analytic`
arm at all — which is also what keeps it out of `e207`'s join, where a cell without a penalty is not a cell.

**The grid is (strength × realization)**: `swap8`, `swap16`, `swap32`, `swap64` at `--rewire-seed` 0, 1, 2, 3, 4 — 20
cells ≈ **37 min**, one run per realization so the swaps are drawn independently (`rewire_seed` is per-run, and the
corpus's whole sampling lesson is that one drawing per setting is not a measurement of the setting).

**Stage 2 — the payment (registered, not launched here).** Run the *full* analytic cell (225 s each) for every screen
cell whose alignment falls inside `[0.09101, 0.27135]`, at most a handful of cells, so the band is filled by cells
**chosen by alignment** rather than by strength. If the screen finds no cell in the band, stage 2 does not run and the
answer is that the swap operation at cs 800 cannot reach the band at these strengths — which is itself the
registration's falsifier for stage 2 and not a failure of the screen.

## 3. The claims

**S1 — the screen is affordable and lands where it says.** Every screen cell has `geometry.all_pairs_alignment`
written and no `analytic` arm; the 20 cells together cost **under 45 min** (registered from the 112 s measurement,
with 15% headroom for the connectome build's variation).

**S2 — the band is reachable by the swap operation at cs 800.** At least one of the 20 cells has alignment in
**`[0.09101, 0.27135]`**. **Falsifier**: none does — which would say the swap family's alignment distribution at high
strength sits *below* the Erdős–Rényi family's (0.27135–0.29039) and the band cannot be sampled this way at all, so
the transition would have to be approached by mixing topologies rather than by rewiring further.

**S3 — the alignment spread at high strength is of the same order as at `swap2`.** Across the five realizations at a
fixed strength, the alignment span is **at least 1.5×** in ratio for at least two of the four strengths (the `swap2`
ratio is 2.60×, `swap0.5` 1.68×). **Falsifier**: no strength has a ratio above 1.5×, which would say the spread is a
property of the *low* end of the family and that one realization per strength is adequate at the high end — a result
that would rehabilitate the strength axis as an x-axis.

**Reported, not claimed**: the full 20-cell table (alignment, × chance, `top_eig_share`, `effective_rank`) and the
list of cells in the band.

## 4. What this cannot do

- **Measure a penalty.** The screen has no arms by construction; every penalty in the band comes from stage 2, which
  this registration only prices.
- **Separate alignment from the other geometry statistics.** `top_eig_share` and `effective_rank` are written
  alongside and move with the swap operation by construction; the screen can say which cells to pay for, not what
  the penalty responds to.
- **Sample different task draws.** `seed0` is 0 everywhere here, so the screen varies the *wiring* realization only —
  the task draw is the other axis and `e3`'s ladder work owns it.
- **Speak for other circuit sizes**, whose alignment distributions are their own (cs 400–700 have the same three
  levels and no ER-mixing results yet).
