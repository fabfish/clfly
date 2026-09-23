# `e112`, pre-registered: bracketing the minimum from both sides

**Date:** 2026-09-23
**Script:** `experiments/e8_rate_network.py`, five runs; artifacts `runs/e112_readout300_{plastic,frozen}.json`,
`runs/e112_readout700_{plastic,frozen}.json`, `runs/e112_readout300_plateau.json` (in flight).
**Setup:** circuit `mb+cx+al@n1307` (cs = 800), 3 tasks, 5 replicates, chance 0.25, `--methods naive`,
`--input-overlap 0.0 --noise 1.0 --shared-head`, **read-out 300 and 700** — one on each side of the minimum.
**Context:** `docs/findings/2026-09-23-the-read-out-axis-has-an-interior-minimum.md`, where five points gave a
two-sided minimum at read-out 512 with both arms monotone (0.0479 > 0.0292 > **0.0208** < 0.0333 < 0.0729), which
locates the minimum only within the interval **(128, 900)** — a factor of seven in width.

---

## 1. The state of the curve, and what one point on each side buys

| read-out | forgetting | task 0 | load-bearing gap | body drift |
|---|---|---|---|---|
| **1307** (whole) | +0.0479 | +0.0833 | −0.0111 | 0.0195 |
| **900** | +0.0292 | +0.0375 | −0.0014 | 0.0213 |
| **512** | **+0.0208** | +0.0333 | +0.0014 | 0.0258 |
| **128** | +0.0333 | +0.0583 | +0.0167 | 0.0391 |
| **32** | +0.0729 | +0.0833 | +0.1000 | 0.0493 |

**Two points, one on each side, halve the bracket on each side**: 300 lies between 128 and 512, 700 between 512
and 900. If both land where a smooth bowl predicts, the minimum is confined to **(300, 700)** — 2.3× narrower
than the interval the five points leave, and the first statement in this sequence whose *value* is a location
rather than a candidate quantity or a shape.

**A single point would have been cheaper and would have left the bracket lopsided**, which is why both are run:
with only 300 the wide side still spans 512 → 1307, and a bowl whose minimum sits at 700 would be
indistinguishable from a corner at 512.

## 2. The predictions, and the falsifier, written before the runs finish

| | prediction |
|---|---|
| **P1, the wide side** | forgetting at **700** is **strictly between** 512's **+0.0208** and 900's **+0.0292** |
| **P2, the narrow side** | forgetting at **300** is **strictly between** 512's **+0.0208** and 128's **+0.0333** |
| **P3, the deliverable** | if P1 and P2 hold, **the minimum is confined to (300, 700)** |
| **Secondary** | task 0 follows the same ordering at both new points (its own minimum is also at 512, at +0.0333) and the load-bearing gap continues its monotone series at both |
| **Falsifier** | either value falls **below +0.0208** (the minimum has moved out of the new bracket, and the arm containing it is not monotone) or above **its own upper bound** (an arm is non-monotone there) |

**The falsifier is one-sided in an informative way**: a value *below* 512's means the bowl is deeper and shifted,
which is a *better* result for the benchmark statement and a worse one for the location claim — and those are
different findings, so they are separated here rather than pooled.

**A repeat at 300** is included, and the frozen controls at both new read-outs, for the reasons every read-out
since `e106` has them: the `naive` arm at a fixed read-out has reproduced bit-identically at **seven**
executions per configuration (what `e103` now prints), and the gap series is one of the two mechanical series
that has stayed monotone, so a point is either a continuation of both or a break in one of them.

## 3. What this cannot settle

- **Two points is still two points.** Even with both predictions holding, the minimum is known only to within
  (300, 700), and the *depth* remains 0.0125 — measured against a wide-half residual in task 1 of 0.0083, so the
  depth is barely larger than a quantity this project has already declined to interpret.
- **The bowl's shape is still not fitted.** Monotone arms over three and then four points do not distinguish a
  parabola from a corner, and nothing here estimates where a minimum of a *smooth* function would be beyond
  saying the observed values are lowest at 512.
- **It says nothing about why.** Five fires have measured mechanical quantities and found them all monotone in
  the read-out; this fire narrows *where* the forgetting's minimum is and not what produces it.
