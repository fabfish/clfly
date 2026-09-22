# E39 — the realization axis refutes the geometry mechanism, and the pre-registered sd prediction was right

**Date:** 2026-09-22
**Script:** `experiments/e36_geometry_carrier.py` (extended; read-only over `runs/`)
**Artifacts:** `runs/e36_geometry_carrier.json`, `runs/e32_rewire{0,1,2,3}.json`, `runs/e33_er_rewire{0,1,2,3}.json`
**Context:** `2026-09-22-realization-attribution-refuted.md` (§6, §7, §9)

---

## 1. The pre-registered prediction, and it held

The previous fire measured the realization-to-realization sd of `excess(swap2)` at **0.00125 from
three realizations** and pre-registered: *"`e32`'s remaining three realizations will turn the 3-point
sd of 0.00125 into a 6-point one; if it moves above ~0.004 the 16× ratio shrinks to 5×, and the
withdrawal stands either way but the margin changes."* Four realizations have landed:

| topology | realizations (excess) | sample sd | df | attributed sd | ratio | χ², P(sd this small │ 0.0205) |
|---|---|---|---|---|---|---|
| `swap2` | 0.01255, 0.01350, 0.01503, 0.01940 | **0.00303** | 3 | 0.0205 | **6.8×** | 0.0657, **p = 0.0044** |
| `erdos_renyi` | 0.14176, 0.14223, 0.14897, 0.14688 | **0.00353** | 3 | 0.0205 | **5.8×** | 0.0891, **p = 0.0069** |

The sd moved 0.00125 → 0.00303, i.e. it stayed **below 0.004**, so the ratio went 16.3× → **6.8×**,
in the direction and to the margin the previous fire wrote down in advance. The withdrawal of the
0.0205 attribution stands on an independent draw: neither topology's realization sd is within a
factor of six of the number that was used to turn the 152σ ER separation into 4.5σ. And ER's four
realizations span 0.00721, **2.5% of their own mean**, against a claimed sd of 67% of the mean that
would have been needed.

## 2. The 5-point geometry curve has no out-of-sample predictive power

The previous fire fitted `excess(swap2) ≈ 0.00280 + 0.02016·ln(effrank)` on the five circuit-size
points, with a **maximum in-sample residual of 0.00296 over a range of 0.04545**, and pre-registered
a `±0.0034` band (the wider of that residual and one out-of-sample point). Three further `swap2`
points are now in hand — same circuit size, same task seeds, different rewiring, all with effective
ranks *inside* the fitted range:

| point | effrank | excess | curve predicts | **residual** |
|---|---|---|---|---|
| rewire-seed 1 | 1.436 | 0.01350 | 0.01009 | +0.00341 |
| rewire-seed 2 | 2.692 | 0.01503 | 0.02276 | −0.00773 |
| **rewire-seed 3** | **5.853** | **0.01940** | **0.03842** | **−0.01902** |

The third is **6.4× the in-sample maximum residual and 42% of the whole fitted range**. Its
effective rank (5.853) sits between the cs500 point (5.040) and the cs300 point (15.407) that
defined the curve, so this is interpolation, not extrapolation. A one-parameter curve that fits five
points to 0.003 and misses the next one by 0.019 is not a predictor; the 8-point rank correlation
drops from 1.000 to **+0.810**.

## 3. The log-slope is not a shared constant either, at 13.6σ

§6 of the previous fire read the five-point rank correlation as the *carrier*: swap2's task precision
rank-collapses, and a collapsed precision is cheap to protect, so its excess tracks the collapse. If
the effective rank were the carrier, then varying it *some other way* should reproduce the same
slope. It is varied by re-drawing the rewiring, at fixed circuit size and fixed tasks — and it does
not:

| family | n | ln-leverage | **log slope** | ± se | ρ | exact p | linear slope | effrank leverage |
|---|---|---|---|---|---|---|---|---|
| `swap2` realizations | 4 | 1.405 | **0.0047** | 0.0009 | +0.800 | 0.167 | 0.00147 | 4.42 |
| `erdos_renyi` realizations | 4 | 0.213 | **0.0340** | 0.0020 | **+1.000** | **0.042** | 0.00110 | 6.61 |
| circuit-size sweep | 5 | 2.203 | **0.0202** | — | +1.000 | 0.042 | 0.00300 | 13.70 |

`swap2` versus ER: **−0.0293 ± 0.0022, i.e. 13.6σ apart** — and the circuit sweep's own slope
matches neither (it is 4.3× the first and 0.6× the second). The two families sit at levels 0.013 and
0.142, ten apart, so a shared log slope would have been the natural signature of a coordinate acting
multiplicatively. It is not there.

Nor does a different functional form rescue it. The **linear**-in-effrank slope is the one the two
realization families agree on (0.00147 against 0.00110, 34% apart), but it does *not* describe the
circuit sweep, whose linear slope is 0.00300 — 2–2.7× the other two. So **no single monotone form
fits all three families**: the implied slope depends on which interval of effective rank you probe.
That is what a shared confound looks like, and it is what a carrier does not look like.

## 4. What survives, and what is withdrawn

**Withdrawn: §6 of `2026-09-22-realization-attribution-refuted.md`** — the mechanism reading, that
`swap2`'s excess tracks the rank collapse of its task precision and that this is why the C1
contrast's sign flips with circuit size. Two independent intervention axes now contradict it: this
fire's realization sweep (slopes 13.6σ apart; a 0.019 out-of-sample miss inside the fitted range) and
the previous fire's `kappa` smoke test (more concentration gave a *larger* gap at `swap2`, which is
`e5`'s direction at `real`, not the required one).

**What survives, because it is only descriptive:** across those five circuit sizes, the sign of the
C1 contrast is a monotone function of `swap2`'s effective rank — `−, −, −, +, +`, every negative at
≤ 2.476 and every positive at ≥ 5.040, ρ = +1.000 with exact p = 0.0083, and neither quantity
monotone in d. That is a true statement about five points and it is *useful as a coordinate*, because
it needs no learning run to compute. It is **not** a statement that the effective rank causes the
excess, and the previous fire's own §6b had already flagged the tension. The honest summary is that
the C1 refutation's sign is *predictable from a diagnostic* and *not explained by it*.

**One place the relation does hold, reported because it cuts the other way:** within ER's four
realizations the ordering is perfect (ρ = +1.000, exact p = 0.042) with a slope of 0.0340. ER is a
different regime — it destroys the degree sequence and makes `(I − W)` near-singular — and its level
is 10× swap2's, so this is not evidence for the mechanism; it is evidence that the effective rank
carries *some* information inside a family, which is exactly why the cross-family slope mismatch is
the thing that matters.

## 5. Limits

- Both realization families have **four** points, so each slope has 2 df and the σ on the difference
  (13.6σ) is the one number here that is properly resolved; the individual slopes are not.
- `swap2`'s within-family rank correlation is +0.800 with exact p = 0.167 — a null at four points,
  so "the coordinate does not order swap2's own realizations" is as much as can be said.
- The slope comparison has the shape of a functional-form search, and the previous fire's §7 warned
  about that. The guard is that the *prediction* was registered before the points landed (the ±0.0034
  band, and the sd-vs-0.004 threshold) and both failed in the pre-registered direction. The
  linear-versus-log comparison in §3 is post hoc and is labelled as such.
- `cs700` is still running. It is now a test of a curve that has already failed out of sample, so a
  miss there would be a third confirmation rather than a new finding — the decisive result is
  already in.
