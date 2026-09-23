# `e111`, pre-registered: a fifth read-out, inside the interval the reframed question is about

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, three runs; artifacts `runs/e111_readout900_plastic.json`,
`runs/e111_readout900_plateau.json`, `runs/e111_readout900_frozen.json` (in flight at registration).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 900** — between 512 and the 1307 whole state.
**Context:** `docs/findings/2026-09-23-the-anomaly-is-the-whole-state-not-the-middle.md`, whose fourth read-out
refuted the curvature hypothesis and **relocated** the anomaly: forgetting is monotone over the three narrow
read-outs (512, 128, 32) and the **whole state is the one point above them**, despite being the widest read-out
and the one where the body is least needed.

---

## 1. The four points, and the two pictures that fit them

| read-out | forgetting | load-bearing gap | body drift |
|---|---|---|---|
| **1307** (whole) | +0.0479 | −0.0111 | 0.0195 |
| **512** | **+0.0208** | +0.0014 | 0.0258 |
| **128** | +0.0333 | +0.0167 | 0.0391 |
| **32** | +0.0729 | +0.1000 | 0.0493 |

Four points admit two readings and this fire's read-out separates them:

- **(A) A smooth interior minimum.** Forgetting falls from 1307 to 512 and rises from 512 to 32, so the
  read-out axis has an **interior optimum at 512** and nothing is anomalous — the curve is simply not monotone,
  and the whole state is no more special than 32.
- **(B) The whole state is a single outlier.** Forgetting at 900 sits at the narrow read-outs' level
  (≈ 0.021–0.033) rather than between it and 1307, so 1307 alone is above a plateau and the excess is a
  property of *that* configuration.

**Everything mechanical is monotone in the read-out**, so (A) is the reading the existing measurements support:
the gap runs −0.0111 → +0.0014 → +0.0167 → +0.1000 and the drift 0.0195 → 0.0258 → 0.0391 → 0.0493, both
without a break, and 900 lies between 512 and 1307 on every one of those series.

## 2. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **P1** | forgetting at read-out 900 is **strictly between** 512's **+0.0208** and 1307's **+0.0479** — the decline from the whole state to 512 is monotone and the minimum stays at 512 |
| **P2** | the load-bearing gap at 900 is **strictly between** 1307's **−0.0111** and 512's **+0.0014**, continuing that series rather than breaking it |
| **Falsifier** | forgetting at 900 is **below 512's** (the minimum moves to 900 or beyond, and picture (A)'s left arm is not monotone) **or above 1307's** (the decline runs the other way) |

**P1 is the one that matters and P2 is the instrument's own control**: P2 is a prediction about a series that
has been monotone at four points, so if *it* fails the natural inference is that this run is in a different
environment rather than that the read-out axis is stranger than measured. The environment is recorded, and will
be reported beside the result for exactly that reason.

**This is the second prediction in the sequence tested on a value not already in hand**, and the first whose
subject is a *shape* rather than a candidate quantity: the question is not "does quantity X order the
forgetting" but "is the axis's left arm monotone", which is a question about the benchmark rather than about one
of my hypotheses.

**A second execution at 900** is included for the reason every read-out since `e106` has one: at a fixed
read-out this configuration's `naive` arm has reproduced bit-identically at **seven** executions (the number
`e103` now prints), and a repeat either continues that or breaks it.

## 3. What this cannot settle

- **Five points is still a curve on five points**, and "strictly between" is a claim about one interpolation.
  If P1 holds the honest statement is a four-point monotone decline plus an interior minimum, not a fitted
  optimum — the minimum's *location* would still be known only to within the interval (512, 900).
- **`H_j` and the curvature instrument are not re-run here.** This fire is about the forgetting and the gap, and
  the curvature's role was refuted at the fourth point; adding its value at 900 would be another series to
  aggregate, not another test.
- **It does not say why** an interior minimum would exist. That is a mechanism question and this is a
  measurement of shape.
