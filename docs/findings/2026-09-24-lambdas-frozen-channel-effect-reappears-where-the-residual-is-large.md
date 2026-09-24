# λ's frozen-channel effect is not flat: it is flat where the freeze left little to remove

**Date:** 2026-09-24
**Artifacts:** `runs/e150_r32_overlap1_frozenbias_ewc_lam3e-3.json` (the second arm of `e150`, landed) against its
λ = 3e-4 sibling and `runs/e143_r32_overlap1_frozenbias.json`; and, on the base family,
`runs/e147_r32_frozenbias_ewc_lam3e-{3,4}.json` against `runs/e125_r32_frozenbias.json`.
**The registration** is `docs/findings/2026-09-24-the-pair-under-the-freeze-registered.md` §2, which asked with the
second arm **whether the pair is a λ-invariant unit**. **It is not**, and the way it is not bounds a claim of
yesterday's.

---

## 1. The λ-against-λ contrast, under the freeze, on both families

| family | λ = 3e-4 | λ = 3e-3 | **the λ step (3e-3 − 3e-4)** |
|---|---|---|---|
| **base** (freeze residual +0.0227) | +0.0026 | −0.0021 | **−0.0047 ± 0.0032 = 1.46σ** |
| **shared-input** (freeze residual +0.0599) | +0.0190 | **+0.0008** | **−0.0182 ± 0.0042 = 4.34σ** |
| **the two steps against each other** | | | **−0.0135 ± 0.0052 = 2.61σ** |

**So the λ effect does not vanish under the freeze — it vanishes on the family whose freeze left little to
remove.** The residual fractions make it visible: on the shared-input family λ = 3e-3 removes **98.7%** of the
freeze's residual against λ = 3e-4's **68.3%** (0.013 against 0.317), and on the base family the same two λ give
**0.115** and **−0.092** — the second being below the freeze's own level, which is why its comparison to the
first is 1.46σ.

**And the difference between the families' λ steps is itself resolved at 2.61σ**, so this is a bounded
refinement rather than a re-reading: `e147`'s finding said *"with the channel held still λ's only resolvable
effect is on the other axis"*, and that sentence is **a statement about a freeze that left 0.0227 of forgetting
behind**. Where the freeze leaves **0.0599** — the family whose difficulty is in the wiring — λ's stability
effect is back at **4.34σ**.

## 2. What that makes of the "λ is about the channel" reading

Three measured configurations order themselves by **how much forgetting is still available to remove**, not by
whether the channel is frozen:

| configuration | forgetting available to the knob | the λ step's resolution, on forgetting |
|---|---|---|
| base family, channel **free** | +0.0750 at λ = 0 | **3.74σ**, in the *opposite* direction (raising λ hurts) |
| shared-input family, channel **frozen** | +0.0599 | **4.34σ**, λ = 3e-3 better |
| base family, channel **frozen** | +0.0227 | **1.46σ**, unresolved |

**So λ's leverage tracks the residual — with one exception that is the whole point of the free channel**: when
the channel is free, raising λ *hurts*, because the adaptation is displaced into an offsets channel that carries
most of the forgetting. Freeze that channel and the same step *helps*; freeze it and leave little behind, and it
neither helps nor hurts resolvably. **The knob's effect is therefore not "masked by the channel" or "owned by the
channel" in the categorical sense of yesterday's reading — it is proportional to the residual the channel
leaves**, and the free-channel case is the one where the channel's *own* forgetting is the thing being moved.

## 3. And the price stays put, which is now a third replication

| contrast | change | resolution |
|---|---|---|
| the pair's newest-task cost, shared-input, λ = 3e-3 | −0.0531 ± 0.0073 | 7.27σ |
| the pair's newest-task cost, base, λ = 3e-3 | −0.0651 ± 0.0073 | 8.95σ |
| **the two families' λ steps on the newest task** | **+0.0130 ± 0.0090** | **1.44σ** |

The λ step's *cost* on the newest task is **−0.0193 ± 0.0063 (3.04σ)** on the shared-input family and
**−0.0323 ± 0.0056 (5.74σ)** on the base family, and the difference between those steps is **1.44σ** — unresolved,
i.e. **the price of λ is again the same on both families** while its benefit is not. That is the third time this
separation has appeared in the same week (the channel × λ interaction at 1.23σ, the pair's price at 0.13σ, this at
1.44σ) while the corresponding benefits are 4.10σ, 2.99σ and 4.34σ.

**And the arm is a new record**: against its own family's `naive` the pair at λ = 3e-3 is **−0.1060 ± 0.0092 =
11.57σ** on forgetting — the largest stability effect measured anywhere in this project — with a newest-task cost
of **−0.0776 (9.62σ)**, and its per-task forgetting is `[-0.0005, +0.0021, 0.0]`, i.e. **zero on both forgettable
tasks**. The whole 11.57σ is bought for 0.0776 of newest-task accuracy.

## 4. What this cannot settle

- **Two λ per family and two families**, both siblings (same circuit, read-out, tasks; differing in
  `--input-overlap`). The "residual" that orders the three configurations is a *level* measured in each, so
  "leverage tracks the residual" is a two-point-per-family regularity and not a fitted law; a third residual
  (e.g. a free channel with a different task family, or a partial freeze) is the natural test.
- **The freeze is a diagnostic, not a method** — as everywhere in this project — so none of this is advice about
  which λ to deploy; it is a statement about where the penalty's leverage lives.
- One read-out (32), three tasks, one seed stream; and the base family's 1.46σ step is the *same arms* whose
  channel × λ interaction was measured last fire, so the two findings are two readings of one design and not two
  independent confirmations.
- The λ step is quoted **per seed**; the two families' step difference (2.61σ) uses the same forty seeds on both
  sides, so it is a paired contrast and not a difference of two independent estimates.
