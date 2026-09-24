# The diagonal's advantage tracks the share of the forgetting it does not cover

**Date:** 2026-09-24
**Artifacts, all at forty replicates on the same seeds:**
`runs/e133_r32_naive_ewc_40reps.json` (base family, `naive` and `ewc`),
`runs/e125_r32_frozenbias.json` (base family, offsets frozen),
`runs/e141_r32_ewc_lam3e-4.json` (base family, λ = 3e-4),
`runs/e142_r32_overlap1.json` and `runs/e143_r32_overlap1_frozenbias.json` (the wiring family),
`runs/e144_r32_overlap1_methods_40reps.json` (the wiring family's four-method table).
**The claim:** *the diagonal penalty's advantage over `naive` is ordered by how much of that baseline's
forgetting lives in the 800 offsets — the one channel the diagonal does not cover.*

---

## 1. Two measured points, and they order

| family and arm | share of the baseline's forgetting **removed by freezing the offsets** (the *uncovered* share) | **diagonal − naive** |
|---|---|---|
| base family (`overlap 0.0`), λ = 3e-3 | **70%** (+0.0750 → +0.0227) | **−0.0096 ± 0.0080 = 1.21σ** |
| wiring family (`overlap 1.0`), λ = 3e-3 | **44%** (+0.1068 → +0.0599) | **−0.0437 ± 0.0093 = 4.73σ** |

**The family where less of the forgetting lives in the uncovered channel is the family where the diagonal does
four times better**, and the two numbers come from measurements rather than from a model: the freeze is a *free*
intervention on the same seeds, and it measures the share directly.

**And the mechanism is not a coincidence of two families**: `e143` measured that the wiring family's extra
forgetting **survives** the freeze at 5.04σ, i.e. the difficulty there is in the **26,568 connectome-masked
weights** — which the diagonal's Fisher *does* cover — while the base family's forgetting is **70%** in the 800
offsets, which it does not. **A penalty that covers 97.1% of the parameters should help more where the forgetting
is in those 97.1%, and the measurement says it does.**

## 2. And the third point is the λ floor, qualitatively

`e141`'s λ = 3e-4 arm is the base family with a weaker penalty, and it is **4.27σ** from `naive` (against λ =
3e-3's 1.21σ) — near the wiring family's 4.73σ. **Its bias path is lower than the 3e-3 arm's** (3.6835 against
4.2819), i.e. the weaker penalty displaces *less* movement into the offsets, **which is the same direction**:
less displacement into the uncovered channel, a larger advantage. **But its own uncovered share has not been
measured**, so this point is qualitative and the relation is two points and an expectation.

## 3. The registered third point

**`--frozen-bias` at λ = 3e-4 on the base family, forty replicates** — one arm, the identical command with
`--frozen-bias`, writing `runs/e146_r32_lam3e-4_frozenbias.json`.

- **P1.** Its uncovered share is **below the base family's 70%** — the weaker penalty displaces less into the
  offsets (its bias path is 3.6835 against the 4.2819 of the 3e-3 arm, a 12.93σ difference), so the frozen arm
  should be **closer to its own naive** than `e125`'s freeze is to `e133`'s naive.
- **Falsifier.** The share is **at or above 70%**. Then the λ floor's 4.27σ is *not* explained by a smaller
  displacement into the uncovered channel — the displacement is larger there and the penalty still helps more —
  and §1's ordering across families is a two-family coincidence rather than a mechanism.
- **And it costs one arm**, because the `naive` arm it is compared against is `e133`'s own: `--frozen-bias` at
  λ = 3e-4 differs from `e125` only in `--lam`, which `naive` never reads, so **its forty replicates should be
  per-replicate identical to `e125`'s** — which is a second, internal control of the same shape as `e140`'s C0b.

## 4. What this cannot settle

- **Two points plus an expectation is not a relation.** The ordering could be read the other way — *the wiring
  family's forgetting is simply larger and easier to reduce* (0.1068 against 0.0750) — and that reading is not
  excluded by anything here: **both candidate orderings fit the two points.** The registered third point does not
  separate them either, since it varies λ on one family; **what would is a family whose baseline forgetting is as
  large as the wiring family's while its uncovered share is 70%**, and none exists in the record.
- **The share is a property of the *baseline*, and the advantage is a property of the penalty.** §1 compares a
  diagonal arm with a freeze performed on the naive arm, so the two quantities are measured on different arms of
  the same family; the honest form is *"the family whose baseline is more exposed to the uncovered channel is the
  family where the diagonal does worse"*.
- **And both families are one read-out (32), one partition (`cell_class`), three tasks, and the same forty seeds**
  — so §1's two points are two configurations of one benchmark, not two benchmarks.
