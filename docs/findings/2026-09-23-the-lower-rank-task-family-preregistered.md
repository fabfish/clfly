# E100 — the reversed-ordering question with a lower-rank task family, pre-registered

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, `e8_hardened_basis`'s configuration with `--classes 2` as the ONLY
change; artifact `runs/e100_rate_cs800_classes2.json` (in flight).
**Context:** `docs/findings/2026-09-23-the-reversed-ordering-question-at-a-smaller-circuit.md` (`e99`, the
smaller-circuit route, which moved the gap **58%** in the predicted direction and resolved nothing); the plan's
§8 item 2, which names **two** routes — *"a smaller circuit, or a lower-rank task family"* — and this is the
second.

---

## 1. Why the second route is a different mechanism, not a repeat

`e99` changed the **circuit**, so the block Fisher had **fewer entries to estimate** from the same 32 batches
(d = 952 against d = 1307). `e100` changes the **task family**: `--classes 2` makes each task a 2-way
discrimination where the configuration has been 4-way, so the readout's discriminating rank per task falls
from 3 to 1 and the family's covariances concentrate into fewer directions.

**The circuit, the partition, the number of block entries and the number of Fisher batches are all unchanged.**
So this route tests the account by making the *target* lower-rank rather than by making the *estimate* cheaper,
and the two mechanisms can come apart — which is the reason to run both rather than one.

**Why the same prediction nonetheless.** The biological block is **worse** than the diagonal by +0.0396 at
cs = 800 (five replicates, 32 Fisher batches). The account says the block's penalty is the *estimation noise in
its off-diagonal blocks*: it has `Σ s_g²` entries to fill from the same 256 observations the diagonal fills
26,568 from. A lower-rank task family puts less of the penalty's own mass in those off-diagonals, so the noise
that hurts should hurt less, and the block should move **toward** the diagonal it refines.

## 2. Predictions, written before the run

- **P1 — the negative replicates.** The biological block does not beat its matched random control, in the same
  direction as at 4 classes (+0.0167 there).
- **P2 — the gap shrinks again.** Block-minus-diagonal forgetting is **smaller in magnitude** than cs = 800's
  **+0.0396**.
- **P3 — and it is still unresolved**, for the reason `e99`'s P3 gave: the `naive` per-repeat sd is 0.048, so a
  0.04 gap is within one replicate's spread however many are averaged, and five replicates give a sem near
  0.02.
- **P4 — the discriminator, and the reason to run this at all.** If the estimation-noise account is right,
  **both** routes shrink the gap (two mechanisms, one prediction). If instead **one shrinks and one grows**,
  the account is incomplete and the gap is driven by something the two routes do not share — which is a
  *negative* result about the account that a single route could not have produced.

**Falsifier.** The block-minus-diagonal gap is **larger** in magnitude than +0.0396 at 2 classes. That reading
would say a lower-rank task family makes the block *worse*, which with `e99`'s result would be the
"one shrinks and one grows" case of P4 — and would mean the estimation-noise account explains the circuit-size
dependence without explaining the task-rank one.

## 3. What this cannot settle, and one asymmetry to expect

**One change is one point.** `--classes 2` also changes the *task difficulty* — a 2-way problem is easier, so
every arm's accuracy rises and its forgetting may fall — which is a confound this run does not remove. The
comparison that survives it is the **contrast** between arms, because all five arms see the same suite; but an
"easier benchmark" reading of any gap change cannot be excluded from one configuration.

**And a second asymmetry**: the matched-random control is a relabelling of the same partition, so it changes
with the block and not with the classes. So the block-minus-random contrast is the one this design protects
best, and the block-minus-diagonal contrast is the one carrying the mechanism. **Both are reported, and P2 is
gated on the latter while P1 is gated on the former**, which is why they are separate clauses rather than one.
