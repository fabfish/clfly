# Registered: an alloy between the two null families, so alignment can be placed inside the hole

**Date:** 2026-09-26. **Registered before stage 2**, whose claims are the ones stated below. Stage 1 (the screen) was
launched at 02:07 and this document was written at 02:08 with **no result read** — a screen is a design step, and the
registration's claims are about the *penalty* measurements of stage 2, which have not been launched.

---

## 1. Why a second null family is needed at all

`e209` (twenty cells) and `e211` (two cells, strengths 256 and 1024) between them measured **twenty-two cells of the
degree-preserving swap walk at cs 800** and found that its alignment never leaves **0.65–1.72× chance** — the highest
value in the whole family is `swap256`'s 0.09560 — while the **edge-count-matched Erdős–Rényi** ensemble sits at
**4.89–5.23× chance** (nine cells). The two ranges are disjoint by a factor of 3.0, and the mean does not trend upward
with strength across a 128× range. So **the interval `[0.09101, 0.27135]`, where C3's transition lives, cannot be
reached by rewiring harder**, and the transition is a difference between two *constructions* rather than a value on a
rewiring axis.

## 2. The new operation, and why it is not the failure this module already records

`random_targets(W, fraction)` — reachable as the topology name `alloy<fraction>` — replaces the target of a fraction of
the edges with a **guarded** uniformly random neuron. It keeps every neuron's **out-degree exactly** and the **edge
count exactly**, and it destroys the pairing structure much faster than a swap because the in-degree is free to move:
a swap preserves in-degree *and* out-degree, which is precisely why twenty-two swap cells could not move the tasks'
alignment.

**The guard is the whole difference from the construction this project already rejected.** `clfly/connectome/rewiring.py`
records an earlier version that randomised the target column globally and lost **70% of the edges** (86,443 → 25,594)
to summed collisions, making the "rewired" condition also the "sparser" one. Here a candidate target that already
exists is rejected and redrawn, so the edge count is preserved — checked in a test on a **complete** graph, where
nothing can move and the count still holds.

**Stage 1 (launched): the geometry-only screen.** `alloy0.25`, `alloy0.5`, `alloy0.75`, `alloy1` at cs 800, 3 seeds,
`--rewire-seed 0`, `--geometry-only` — 4 cells, ~8–10 min at 112–126 s per cell. Its job is to answer one question:
**which alloy fractions put `all_pairs_alignment` inside `[0.09101, 0.27135]`?**

**Stage 2 (priced, not launched): the payment.** A full analytic cell (225–240 s each) for **up to four** alloy
fractions that land in the band, which is what actually reads the penalty across the transition.

## 3. The claims

**P1 — the alloy axis spans the hole.** Stage 1 finds at least one of the four fractions with alignment inside
`[0.09101, 0.27135]`, **and** at least one with alignment **above 0.20** (i.e. within 1.36× of the ER family's lowest
cell). **Falsifier**: no fraction inside the band, which would say that even freeing the in-degree cannot place
alignment in the hole at these fractions and the design needs a different interpolation (or densification); **null**:
a fraction inside the band but none above 0.20, which would still allow the *lower* half of the transition to be read.

**P2 — the transition is graded (the question C3 asks).** Taking stage 2's cells in alignment order, the analytic
penalty is **non-decreasing in alignment**, and the cell nearest the ER end is at or above **0.06** — the same bar
`e208`'s T2 registered, so the two designs' answers are comparable. **Falsifier**: the highest-alignment alloy cell's
penalty is at or below **0.035**, i.e. the hole behaves like the in-axis regime and the jump happens only at the ER
construction itself, which would make **alignment a correlate rather than the driver** and leave C3 needing the
construction's other properties (degree distribution, densification, the absence of any structure at all).
**Null**: penalties that rise but not monotonically, unresolved at ≤4 cells.

**P3 — the alloy is not just a sparser graph in disguise.** Every stage-2 cell's `n_edges` and out-degree multiset are
identical to the connectome's (the construction guarantees it, and the claim is that the artifacts confirm it), and
`swap_fraction` is reported per cell. **Falsifier**: a cell whose edge count differs from the connectome's, which would
reintroduce the density confound this module's docstring records and invalidate the comparison.

## 4. What this cannot do

- **Locate the transition** even if P2 is MET: four fractions are four points, and the alloy's own realization spread is
  unmeasured (the swap family's was 1.60–2.05× at every strength, so a single drawing per fraction would not be a
  measurement of that fraction — the honest stage 2 draws at least two realizations per band fraction if the budget
  allows).
- **Separate alignment from `top_eig_share` and `effective_rank`**: the alloy moves all three, and nothing here holds
  two fixed.
- **Speak for the task draw** (`seed0` 0 throughout) or for other circuit sizes.
- **Reach the ER regime itself**: `alloy1` randomises targets but keeps out-degrees, so it is *not* the ER ensemble and
  may not reach 0.271 — P1's falsifier is written to catch exactly that, and if it lands, the two families are more
  than two points apart and the transition is between three constructions rather than two.
