# `e118`: the metric is thirty times noisier than the quantities compared against it

**Date:** 2026-09-24
**Method:** the forty-replicate per-repeat sds of `theta_drift` and of `mean_forgetting` at all seven read-outs,
plus the four independent draws at read-out 128, all from artifacts already on disk.
**Artifacts:** `runs/e115_r{300,512}_40reps.json`, `runs/e116_r{1307,900,700,128,32}_40reps.json`,
`runs/e117_r128_draw{1,2,3}_20reps.json`.
**Context:** `docs/findings/2026-09-24-the-axis-is-a-plateau.md`, which gave the axis one error bar, and
`docs/findings/2026-09-23-the-bodys-drift-is-monotone-and-forgetting-is-not.md`, which measured the drift as
monotone in the read-out and unable to order the forgetting.

---

## 1. The two quantities, at forty replicates each

| read-out | forgetting | **drift** | forgetting sd (per repeat) | **drift sd** |
|---|---|---|---|---|
| 1307 | +0.0357 | 0.0191 | 0.0423 — **119% of its value** | 0.00060 — **3.1%** |
| 900 | +0.0219 | 0.0216 | 0.0244 — **111%** | 0.00071 — **3.3%** |
| 700 | +0.0221 | 0.0236 | 0.0297 — **134%** | 0.00083 — **3.5%** |
| 512 | +0.0250 | 0.0260 | 0.0305 — **122%** | 0.00085 — **3.3%** |
| 300 | +0.0232 | 0.0309 | 0.0252 — **109%** | 0.00080 — **2.6%** |
| 128 | +0.0370 | 0.0395 | 0.0325 — **88%** | 0.00116 — **2.9%** |
| 32 | +0.0750 | 0.0497 | 0.0556 — **74%** | 0.00130 — **2.6%** |

**The drift is monotone in the read-out to three decimals** — 0.0191, 0.0216, 0.0236, 0.0260, 0.0309, 0.0395,
0.0497 — and every one of those seven values is measured to **2.6–3.5% of itself**. **The forgetting is a
plateau and every value is measured to 74–134% of itself.**

**So the two quantities differ in relative precision by a factor of about thirty**, on seven read-outs and forty
replicates each. That is not a difference in effect size; it is a difference in the estimator.

## 2. And it is a property of the estimators, not of the physics

**The drift is a Euclidean norm over 26,568 numbers**, so its per-repeat variation averages out a 26-millifold
of independent contributions and lands at 3%. **The forgetting is a difference of accuracies over 48 held-out
decisions, twice** — `max_k R[k,j] − R[T−1,j]` for `j = 0, 1` — so it is a coarse integer-valued quantity whose
own granularity is `1/240` and whose replicate-to-replicate swing is the same order as the differences the whole
line has been arguing about. `§4.7` already says the binding limit is the benchmark's own per-repeat spread;
**this measures the ratio that makes it binding**, and the ratio is thirty.

**Which reframes five fires of mechanism search.** The sequence tested four monotone mechanical quantities
(drift, the load-bearing gap, the first-order interference term, the second-order quadratic form) against the
forgetting, and the reason each failed was diagnosed as *shape* — the metric is a plateau, and monotone
quantities cannot order a plateau. **That diagnosis is right and incomplete**: the metric is also, in relative
terms, **thirty times noisier than every quantity it was being compared against**, so a comparison at this
replicate count could not resolve the ordering even if one existed. The two facts are the same fact seen from
two sides — a plateau *is* what a signal looks like when the noise is thirty times the effect.

## 3. The decoupling that the axis cannot provide, and it is a clean negative

Across the seven read-outs the drift is monotone and the forgetting is not, but those two series are perfectly
confounded — the drift *is* a function of the read-out size, so no contrast between them can say which variable
the forgetting follows. **The four independent draws at read-out 128 break that confound**: the size is fixed and
the draw varies, and the drift is recorded too.

| draw at read-out 128 | forgetting | drift |
|---|---|---|
| seed 0 | +0.0370 | 0.0395 |
| seed 1 | +0.0469 | 0.0382 |
| seed 2 | +0.0411 | 0.0376 |
| seed 3 | +0.0349 | 0.0396 |
| **spread** | **sd 0.0053 (14%)** | **sd 0.00095 (2.4%)** |

**At a fixed read-out size the drift is nearly constant while the forgetting varies more than six times as much
in relative terms.** So forgetting is **not** a function of how far the body moved — the same drift (0.0376 to
0.0396, a range of 0.0020) sits beside forgettings from 0.0349 to 0.0469. **This is the strongest form of that
negative available**, because it holds the variable that the axis confounds fixed, and it also kills a reading
that was tempting from the axis alone: *"forgetting is flat until the body has moved more than ≈ 0.031 and rises
after"* is an artefact of the drift being a re-parameterisation of the read-out, not a threshold anyone can
locate independently.

## 4. What follows, and what it costs

- **The line's binding limit is now a number rather than a sentence.** To resolve a forgetting difference whose
  size is one per-repeat sd, a contrast needs tens of replicates per side; to resolve one of the size the axis's
  steps actually have (0.0138) needs the counts `e114` computed, corrected by `e116`'s finding that a replicate
  count from an sd is uncertain by a factor of three either way.
- **No further mechanical quantity will fix it.** Four have been measured, all monotone, all precise to a few
  per cent — and the failure is on the other side of the comparison. **The productive directions are a metric
  with a better SNR (more held-out decisions, more tasks) or a statement that does not need the metric to be
  ordered** — which is what the plateau is.
- **And `theta_drift` turns out to be the line's best instrument and its least useful predictor**: it
  reproduces to 3% across forty replicates and 2.4% across four draws, it is monotone in the read-out to three
  decimals, and it carries no information about the forgetting. **A quantity can be precise, monotone and
  irrelevant at once**, and the way that was found out was to measure it.

## 5. What this cannot settle

- **The 3% drift figure is conditional on the configuration**: it is measured at seven read-outs, all cs = 800,
  three tasks, five hundred iterations; a longer or harder run would drift further and might drift less
  repeatably.
- **It does not say the metric cannot be ordered by anything** — only that the four mechanical quantities tried
  are thirty times more precise than it is, and that a comparison needs the counts this fire's predecessors
  computed.
- **The relative-precision ratio is computed from two different estimators with different distributions**, so
  "thirty times" is a ratio of coefficients of variation rather than a variance ratio; it is a description of the
  comparison's difficulty, not of any underlying randomness.
