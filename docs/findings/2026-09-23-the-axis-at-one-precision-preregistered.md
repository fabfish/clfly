# `e116`, pre-registered: the whole axis at one precision, and the direction of the noise predicted

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, five runs; artifacts `runs/e116_r{1307,900,700,128,32}_40reps.json`
(in flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, `--seed0 0`, `--repeats 40`, at the five read-outs that have
only five replicates.
**Context:** `docs/findings/2026-09-23-forty-replicates-refute-the-minimum.md`, which gave read-out 300 and 512
forty replicates each and left the axis **measured with unequal precision** — so that every comparison involving
one of those two is dominated by the *other* side's five-replicate noise (read-out 900's sem is 0.0090 against
300's 0.0040).

---

## 1. What one unit of work buys, and why it is not another point

The axis's only surviving claim — read-out 32 forgets more than 900, 512, 300 and 128 — does not need this fire.
**What needs it is every other comparison on the axis**: the trough (300–512 at +0.0232 and +0.0250) is measured
to ±0.004 while its neighbours are measured to ±0.009–0.015, so the trough's *extent* is not a measured quantity
at all. **Putting the five remaining read-outs on forty replicates is the only change that makes the axis
readable**, and it is priced at **5 × ≈ 15 min ≈ 75 minutes** from the same arithmetic that priced the last
step — with the correction that the per-repeat sds are larger than their five-replicate estimates, so the true
price may be higher.

**The deliverable is a shape with one error bar, not a new extreme.** Four fires have now produced a shape claim
that the next measurement retracted, and every one of those retractions came from measuring a *point* better
rather than from measuring the *curve* evenly. This fire measures the curve evenly.

## 2. The control, at five read-outs

The training seed is `seed0 + 100·r`, so each new run's **first five replicates must be bit-identical** to the
stored five-replicate run at the same read-out:

| read-out | stored artifact |
|---|---|
| 1307 | `runs/e109_second_order_r0.json` |
| 900 | `runs/e111_readout900_plastic.json` |
| 700 | `runs/e112_readout700_plastic.json` |
| 128 | `runs/e109_second_order_r128.json` |
| 32 | `runs/e109_second_order_r32.json` |

**A failure at any read-out voids that run rather than being reported as a difference** — the `e61`/`e68` rule,
applied in advance for the second fire running. And a failure at *one* read-out while the others pass would say
the configuration changed between the five-replicate and forty-replicate runs at that point, which is a
different and more interesting finding than any shape.

## 3. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **C0** | the first five replicates are bit-identical at all five read-outs |
| **P1, directed** | the forty-replicate per-repeat sds are **larger** than the five-replicate ones. This is stated as a **direction** rather than as a tolerance, which is last fire's own rule applied: a two-sided factor-of-two tolerance on an sd is a factor-of-four tolerance on the count it feeds, and it let a 1.69× underestimate through. The direction here has two pieces of evidence — 300 went up 1.12× and 512 up 1.69× — and a five-point sd of a heavy-tailed quantity should be an underestimate |
| **P2** | read-out 32 remains the axis maximum and its excess over the trough resolves at **≥ 3σ** against the new forty-replicate trough points |
| **P3, the interesting one** | **the flat region extends from 300 to 900**: none of the four neighbour steps 900 → 700, 700 → 512, 512 → 300, 300 → 128 resolves at 2σ |
| **Falsifier** | any of those four steps resolves at 2σ — in which case the trough has internal structure, the axis is a curve rather than a plateau, and the previous fire's "flat trough" is itself a two-point reading that needs replacing |

**P3 is the prediction this fire is about**, and it is falsifiable in the direction that would be *good news*:
structure in the trough would be the first non-trivial shape on this axis to survive a measurement made to detect
it. A null result means the axis really is "a high end and a plateau", which is a smaller claim than any of the
five that preceded it and the first one that will have been measured at the resolution it is stated at.

## 4. What this cannot settle

- **The draw is still one per read-out.** Even with equal precision the axis is one sample per size, so a
  resolved step would be a statement about these draws; the draw span (0.0125 at read-out 300) sits **at** the
  2σ threshold this design achieves (≈0.0125), so this fire cannot separate draw from size even where it
  resolves. That is a *different* experiment — replicate draws, not replicates — and its cost is 40× higher.
- **Five points with forty replicates.** Read-out 32's point is at the axis's end and its excess is not in doubt;
  whether 32 is special or simply the far end of a trend remains unanswerable without read-outs between 32 and
  128, which is a new point rather than more precision.
- **The sds it produces are themselves estimates** — from forty points rather than five, which is the whole point,
  but a third round would move them again.
