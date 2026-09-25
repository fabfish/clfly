# The two lines' distant-pair components agree in SIGN and not in TIMING — and the analytic side is a three-seed point with no stored spread

**Date:** 2026-09-25
**A cheap unit done while `e193`'s last level runs.** C4's box says the analytic and network lines differ on the
adjacent pairs while the **distant** pairs "point the same way in both"
(`docs/findings/2026-09-25-the-composition-survives-the-quantity-the-proxy-could-not-see.md`). Neither line's
distant-pair **timing** had been expressed as a fraction of its own 0 → 1 change, which is the form the shape
question needs and the form `analytic_progress` has computed for the near component since it was written. It now
computes both components, and the comparison is a read rather than a hand computation. Every number here is from
artifacts that already existed — `e7` (the analytic line, 3 seeds) and the `e193` levels (the network line, 40
seeds).

---

## 1. The instrument had a defect the second component exposed

`analytic_progress` divided by **the fall**, `block[0][comp] - block[-1][comp]`. That is defined for `e7`'s near
component, which falls (+0.025751 → −0.001327), and for nothing else: the **far** component *rises* (+0.008411 →
+0.011069), so the same expression returns a fraction of a fall that is not happening, with the sign inverted.

Rewritten as `(value - first) / (last - first)` — algebraically identical for a falling component, so the near
fractions are unchanged to the last digit (0.4014 / 0.7645 / 0.8648, which the existing tests already pin) — and
given a `comp` argument. The result **may be negative**, which is not a defect: it means the component is on the
other side of its own starting value.

## 2. The two far components, as fractions of their own 0 → 1 change

| achieved overlap | analytic far (`e7`, 3 seeds) | network far (`e193`/`e116`/`e144`, 40 seeds) |
|---|---|---|
| 0.0000 | 0% (by construction) | 0% (by construction) |
| 0.0526 | **−50.4%** | — |
| 0.1429 | **−20.0%** | +7.5% (0.30σ) |
| **0.3333** | **+16.5%** | **+82.1%** (3.31σ) |
| 0.6000 | +52.2% | *pending* |
| 1.0000 | 100% | 100% (3.12σ on the rise) |

Three things, in order of how well they are supported:

1. **The sign agrees.** Both far components end above where they started: `e7`'s by +0.002658, the network's by
   +0.08818. C4's "pointing the same way in both" is a statement about the **endpoints**, and it holds.
2. **The timing does not.** At the registered midpoint the network's far is **82.1%** of the way through its own
   change while the analytic far is at **16.5%** — a gap of **65.6 points**, and the network side is resolved at
   3.31σ while the analytic side is a point estimate. So the two lines agree on the destination and disagree on
   when they get there.
3. **The analytic far is not merely slow, it is non-monotone.** At achieved 0.0526 it sits **below** its overlap-0
   value, and at 0.1429 it is still below it (−20.0%). It has to come back above before it can rise to 100%.

## 3. Where this claim is weak, stated rather than buried

**`e7`'s controlled sweep is three seeds and the artifact stores means only — no per-level sem, for either
component.** Its config says `seeds: 3`, and each row carries `mean_interference`, `mean_interference_near` and
`mean_interference_far`. So:

- the far's whole 0 → 1 change is **+0.002658**, an order of magnitude smaller than the near's **0.027078**;
- the −50.4% reading at achieved 0.0526 is an absolute move of **0.0013** on a three-seed mean;
- **the dip and the 16.5% cannot be called resolved, and nothing here attaches a σ to them.**

What survives that caveat is the comparison's *direction and size*: the network's far is 82.1% of the way through a
change that is **+0.08818 over forty seeds** — 33× the analytic far's total — while the analytic far is at 16.5%.
The disagreement is large relative to the smaller of the two quantities, which is why it is worth recording; it is
not a precise number.

## 4. The read, and a fourth registered claim for the pending level

`e191 --dose` now prints the analytic far beside the network far on the `naive` row, so §2's table is a read:

```
P2: 20% of its own 0->1 rise (bar 60%) -- NOT met   [the analytic line is 76% there, i.e. this line is at 26%
of the analytic's progress; the distant-pair term is at 82% of its own (the analytic line's far is at 17% there)]
```

**Registered now, before level 0.75 lands** — alongside S1 and S2, which the same artifact decides:

- **S3 — the timing disagreement persists, and the sign agreement is not all there is to it.** At achieved 0.6000
  the network's far progress exceeds `e7`'s far progress at the same achieved overlap by **at least 15 points**
  (measured at the midpoint: 82.1% against 16.5%, a gap of 65.6; `e7`'s own far progress at 0.6000 is **52.16%**,
  so the bar asks for the network's far to be at **≥ 67.2%**). **Falsifier**: the network's far progress does **not**
  exceed the analytic's (gap ≤ 0), which would remove the timing difference entirely and leave C4's "same way" as a
  statement about sign alone. **Null worth keeping**: a gap between 0 and 15 points, which would leave the two lines'
  far components agreeing in sign and coming into agreement in timing by the far end of the axis.
- **Its asymmetry is part of the registration**: the network side is a forty-seed measurement with a sem, the
  analytic side is a three-seed point with none, so the falsifier's decisive half is the network's.

## 5. What this does not license

- **A σ on the analytic far's dip or on its 16.5%.** There is none in the artifact (§3), and this finding does not
  manufacture one.
- **That the two far components share a mechanism.** Agreeing in sign at the endpoints is compatible with the
  temporal disagreement being the whole story, which is what S3 is written to test.
- **Reading across the two lines' magnitudes.** The network's far change is +0.08818 and the analytic's +0.002658,
  on different constructions, different scales and different seed counts; only the *fraction of its own change* is
  comparable here, which is why that is the form §2 uses and the only form the instrument computes.
- **That the near/far split is the same split as the forgetting/accuracy one.** §2 is about the interference
  account's two pair classes; `docs/findings/2026-09-25-at-the-midpoint-p1-and-p2-fail-and-the-far-term-is-82-percent-done.md`
  §3's second half is about the two accounts. Nothing here measures whether those decompositions coincide.
