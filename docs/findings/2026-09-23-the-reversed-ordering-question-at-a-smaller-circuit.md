# E99 — the reversed-ordering question at a smaller circuit: the account predicts the right direction and neither size resolves the size

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py` at `--circuit-size 300`, `e8_hardened_basis`'s configuration
otherwise field for field; artifact `runs/e99_rate_cs300_cell_class.json`.
**Pre-registration:** `docs/findings/2026-09-23-the-reversed-ordering-question-at-a-smaller-circuit-preregistered.md`
**Context:** the plan's §8 item 2 and C2b, which have asked this since the first network run;
`docs/findings/2026-09-23-the-last-two-unaudited-sections-were-clean.md`, which established that **all 25**
rate-network artifacts in this repository are at cs = 800.

---

## 1. The two sizes, side by side

Five replicates each, λ = 0.003, 32 Fisher batches, `cell_class`, `readout_size` 32, `shared_head`:

| arm | cs = 800 acc | cs = 800 forgetting | cs = 300 acc | cs = 300 forgetting |
|---|---|---|---|---|
| `naive` | 0.9139 | +0.0729 | 0.9028 | +0.0875 |
| `ewc` (diagonal) | 0.9222 | **+0.0208** | 0.8958 | +0.0771 |
| `ewc-block` (biological) | 0.9153 | +0.0604 | 0.9042 | +0.0938 |
| `ewc-block-rand` (matched) | 0.9278 | +0.0438 | 0.9056 | +0.0833 |
| `replay` | 0.9319 | +0.0500 | **0.9389** | **+0.0458** |

| contrast, mean forgetting | cs = 800 | cs = 300 |
|---|---|---|
| block − matched random | +0.0167 ± 0.0255 = 0.65σ | +0.0104 ± 0.0362 = **0.29σ** |
| **block − diagonal** | **+0.0396 ± 0.0250 = 1.59σ** | **+0.0167 ± 0.0432 = 0.39σ** |
| `naive` − diagonal | +0.0521 ± 0.0211 = **2.47σ** | +0.0104 ± 0.0421 = 0.25σ |

## 2. All three predictions hold and the falsifier did not fire

- **P1 — the negative replicates.** The biological block is worse than its matched random control at **both**
  sizes (+0.0167 and +0.0104), in the same direction, and resolved at neither.
- **P2 — the gap shrinks, because the mechanism says it should.** The block-minus-diagonal gap falls from
  **+0.0396 to +0.0167**, a **58% reduction**, which is the direction the estimation-quality account
  predicts: at d = 952 the block Fisher has far fewer entries to estimate from the same 32 batches, so a
  refinement of the diagonal should behave more like the diagonal.
- **P3 — and it stays unresolved.** 0.39σ at cs = 300 against 1.59σ at cs = 800. The question is not settled
  at either size.
- **The falsifier did not fire.** It was *the gap is larger at cs = 300*, which would have said a
  better-estimated block Fisher is worse and put the reverse-ordering reading on firmer ground. So this run
  is **the first evidence the project has *for* the estimation-quality account rather than against it** — and
  it is weak evidence, because the gap it explains is not resolved at either size.

## 3. Why the σ fell without the question being settled

Both σ fell, and it would be easy to read that as progress. It is not: **the arms are individually noisier at
the smaller circuit.** The forgetting sems are 0.0255 and 0.0250 at cs = 800 against **0.0362 and 0.0432** at
cs = 300, so the gap shrank *and* the error bar grew, and the σ fell because the numerator fell faster than
the denominator rose. **A smaller circuit bought a smaller gap and a wider interval**, which is the trade the
plan's §7 arithmetic already described and the reason P3 was written as a prediction rather than a fallback.

## 4. Two results that were not being looked for

- **The diagonal's advantage over `naive` disappears at the smaller circuit.** `naive` − diagonal is
  **+0.0521 at 2.47σ** at cs = 800 and **+0.0104 at 0.25σ** at cs = 300. So the one Fisher variant that
  *does* help at cs = 800 — the neuron diagonal — **stops helping at d = 952**, which is a size dependence in
  the network line's *baseline* result rather than in the basis question. The paper does not say this, and it
  is the kind of thing a second circuit size exists to find: the diagonal's benefit is not a property of the
  benchmark but of the benchmark **at that size**.
- **`replay` is best on both metrics at cs = 300** — 0.9389 accuracy and +0.0458 forgetting, against `naive`'s
  0.9028 / +0.0875 — so the network line's **only resolved positive result replicates at a second circuit
  size**, which it had not been asked to do. At cs = 800 it was 0.9319 / +0.0500, so the ordering
  (replay ≻ all) is stable across the two sizes while the basis ordering is not.

## 5. What this changes, and what it does not

**It does not answer the reversed-ordering question**, because the contrast that would answer it is 0.39σ.
**It does move the account that predicts it into positive territory for the first time**, and it does so with
a *direction* rather than a magnitude: the gap shrank by 58% when the estimation budget per block entry
improved, which is what the account says should happen.

**And it answers §8's item 2 in the negative in a useful way**: at the one other affordable circuit size, the
configuration §8 asked for exists *and* the question is still not resolvable there. So the item should be
restated as **resolved-in-direction, unresolved-in-size**, and its remaining route is the one §8 also names —
the lower-rank task family — which changes the suite rather than the substrate and is therefore cheaper than
a third circuit size.

**One size is one point.** P2's 58% is a difference between two points, and the direction it moves is the one
a mechanism predicts; but with two sizes and error bars that overlap, calling it a *trend* would be the same
error this project has spent the week correcting.
