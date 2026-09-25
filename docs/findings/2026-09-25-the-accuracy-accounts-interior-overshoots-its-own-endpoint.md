# The accuracy account's shape is not its endpoint's: the midpoint's cost is 1.77× the whole 0 → 1 change, and that overshoot is 1.56σ

**Date:** 2026-09-25
**A cheap unit done while `e193`'s last level runs.** `e191` reads the shape of the overlap response on the
interference account — each term's change as a fraction of its own 0 → 1 change. `e188` had no equivalent: it
reported a level's forgetting and accuracy *changes* and the registered bars on them, so the same shape question on
the accuracy account had no instrument, and the fractions in §2 were being read by hand. They are now computed for
both quantities, together with the contrast an overshoot past 100% needs. Every number here is off artifacts that
already existed.

---

## 1. The fractions, and the one that passes 100%

`naive`, both quantities, against the disjoint baseline `e116` (overlap 0.0, λ = 3e-3) with `e144` as the
overlap-1.0 anchor — the pairing rule is `e191`'s, applied to this account:

| `naive` | 0 → 1 change (the denominator) | at achieved 0.1429 | at achieved **0.3333** |
|---|---|---|---|
| forgetting | +0.03177 ± 0.01063 = **2.99σ** | +0.01406 (1.16σ) → **44.3%** | +0.00833 (0.79σ) → **26.2%** |
| accuracy | −0.01858 ± 0.00691 = **2.69σ** | −0.00278 (0.34σ) → **15.0%** | **−0.03281 (4.45σ) → 176.6%** |

**The accuracy cost at the registered midpoint is 176.6% of its own 0 → 1 endpoint change**: the network's accuracy
one third of the way along the overlap axis is further below its overlap-0 value (0.03281) than it is at *full*
overlap (0.01858). So the accuracy account's interior **overshoots** its own endpoint, while the forgetting
account's interior does not even reach a third of its endpoint and its two means are ordered the wrong way (44.3%
then 26.2%).

## 2. The overshoot's own σ, which is the whole question

A fraction above 100% is a reading, not an error — but it is a **point estimate** unless the overshoot is tested, and
the test is not two sems in quadrature. Both fractions are deltas against the **same** baseline, so the thing to
measure is the level against the **anchor** directly:

| contrast | measurement | σ |
|---|---|---|
| the accuracy cost at the midpoint **against `e144`** | −0.01424 ± 0.00910 | **1.56σ** |
| the same computed by quadrature of the two deltas' sems (0.00737, 0.00691) | 0.01424 ± 0.01010 | 1.41σ |

Quadrature **overstates the sem by 11%**, i.e. it understates the overshoot's resolution, because the two arms are
positively correlated: solving `sem²_paired = sem²_level + sem²_anchor − 2r·sem_level·sem_anchor` gives **r ≈ +0.19**.
The difference is not decoration — a reader who took the quadrature figure would report 1.4σ and one who took the
paired figure reports 1.6σ, and **neither resolves the overshoot**: the non-monotonicity of the accuracy profile is a
point estimate at forty seeds.

Same contrast on the forgetting side: the midpoint's forgetting against `e144` is −0.02344 ± 0.01415 = **1.66σ**, so
that account's non-monotone ordering is unresolved too.

## 3. What IS resolved on this account, and it is not the endpoint story either

At achieved **0.1429** the accuracy against `e144` is **+0.01580 ± 0.00624 = 2.53σ better**. So low overlap costs
genuinely less accuracy than full overlap — a resolved statement, and the first resolved *interior* statement either
account has produced:

| | interior points, as σ against the overlap-1.0 anchor |
|---|---|
| forgetting | 1.71σ at 0.1429; 1.66σ at 0.3333 — neither resolved |
| **accuracy** | **2.53σ at 0.1429**; 1.56σ at 0.3333 |

So the accuracy account is **not** a flat interior with an endpoint: one of its interior points is resolved, in the
direction of *less* cost at lower overlap, while the other is unresolved in the direction of *more*. Both of those
are statements about a `naive` arm whose 0 → 1 endpoint change is itself only 2.69σ.

## 4. The sign convention, and the test that caught it

`overshoot_vs_anchor` is oriented **level − anchor** for both quantities, so a positive value means the level's
quantity is larger. The first version had the forgetting one the other way round, which no live read would have
shown — the printed sign would have been consistent with either convention — and a synthetic test with a known
answer caught it. It is the same class as the two defects
`docs/findings/2026-09-25-p2s-bar-is-60-percent-and-the-read-applied-46.md` records: a quantity read in the wrong
direction prints a plausible number.

## 5. Registered now, before level 0.75 lands

Neither account's interior **shape** was registered — the registration's P1 and P2 are about the interference
account's adjacent-pair term, and `e188`'s bar is about forgetting at the midpoint. So, alongside S1–S3:

- **S4 — the midpoint is a local maximum in the accuracy cost.** At achieved 0.6000 `naive`'s accuracy cost is
  **below 176.6%** of its own 0 → 1 change, i.e. the cost comes back down toward the endpoint (100%) rather than
  continuing to climb. **Falsifier**: at or above **176.6%**, which would say the cost still climbs and the endpoint's
  100% is a genuine turn rather than a peak — and would make the profile's only resolved feature the endpoint itself.
  **Null worth keeping**: the 0.6000 cost lands within 2σ of 100%, leaving the accuracy account's interior
  featureless apart from the 2.53σ low-overlap point of §3, with the endpoint as its shape.
- **Its resolution is part of the registration**: the bar is decidable on the network side (40 seeds, sems of
  0.007–0.009), and the overshoot's own σ at that level is to be computed the paired way (§2) rather than by
  quadrature.

## 6. What this does not license

- **That the accuracy cost is non-monotone in the overlap.** It is a point estimate: 176.6% against 100% is 1.56σ.
  What is resolved is that the midpoint's cost is 4.45σ from zero and the low-overlap cost is 2.53σ *below* the
  endpoint's.
- **Comparing the two accounts' fractions as if they were one axis.** They are two different quantities with
  different 0 → 1 denominators (+0.03177 against −0.01858) and different sems; the fractions are comparable within
  an account and not across them.
- **That a fraction above 100% means the endpoint is wrong.** The endpoint is a 40-seed paired contrast at 2.69σ; an
  interior point above it is a statement about the profile and not about the endpoint's measurement.
- **Any of this for the penalised arms.** Their admitted baseline is `e153`, which is itself at overlap 1.0, so the
  progress fractions are **refused** for them with the reason printed — the same guard `e191` applies and for the
  same reason.
