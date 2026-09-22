# E56 — the mechanism's direction is **null** at 12 seeds where it is testable, the banned metric's signal there is the oracle, and my own sign test on `e42` was wrong

**Date:** 2026-09-22
**Script:** `experiments/e56_metric_pathology_both_ways.py`
**Artifacts:** `runs/e56_metric_pathology.json`, `runs/e52_swap2_cs300_12seeds.json`, `runs/e42_e5_reseed.json`
**Context:** `2026-09-22-twelve-seeds-reverse-the-e5-direction.md` (`e42`), `2026-09-22-the-smoke-test-was-one-seed.md` (`e51`), plan rule 3

---

## 1. First, a correction to `e42`'s own headline number

The previous fire reported the `e42` sign test as **p = 0.0386**. That was wrong.

`e42`'s twelve per-seed ρ on the prescribed metric include **one value of exactly 0.000**, so the
counts are **9 positive, 2 negative, 1 tie**. I computed `binomtest(2, 12)` — which treats the tie as
a positive and asks about the two negatives — and that gives 0.039. **The tie is not a sign**, and the
standard treatment drops it:

| convention | p |
|---|---|
| `binomtest(2, 12)` — tie counted *as* positive (what I quoted) | 0.0386 |
| `binomtest(3, 12)` — tie counted *against* (also wrong) | 0.146 |
| **`binomtest(9, 11)` — tie dropped** | **0.0654** |

So `e42`'s reversal is **less significant than reported**: sign p = **0.065**, not 0.039. It remains a
reversal in direction (mean +0.265, 9 of 11 untied seeds positive, pooled ρ = +0.228 at p = 0.037) but
the sign test alone does not reach 0.05, and the corrected summary is *reversed, marginally, on two of
four tests*. The other three statistics are unaffected — the pooled ρ is computed over all 84 points
and no convention applies to it.

`e56`'s `sign_test` helper now returns the positive, negative and tied counts separately and applies
the tie-dropping convention in one place, so no caller can pick a convention by accident. That is the
bug's real lesson: **the convention was implicit, and an implicit convention is one a later reader
cannot audit.**

## 2. `e52`: where the mechanism is testable, at 12 seeds, the direction is **exactly null**

`swap2`/cs = 300 is the one configuration where the concentration knob has leverage for `e36`'s
mechanism — `e49` measured 30× the seed noise, driving `effective_rank` from 16.6 to 2.35 — and `e52`
ran it with twelve seeds. On the metric rule 3 prescribes:

| statistic | value |
|---|---|
| per-seed ρ, counts | **6 positive, 4 negative, 2 tied** |
| sign test (ties dropped) | **p = 0.754** |
| mean ρ | **−0.009** |
| median ρ | +0.071 |
| Wilcoxon | p = 1.00 |
| pooled over 84 points | ρ = **+0.076**, p = 0.49 |

**Six of twelve, a mean of −0.009, and a Wilcoxon p of exactly 1.00.** The mechanism's ordinal
direction is not confirmed, not reversed — it is **absent**.

And this retires `e51`'s reading. At three seeds the same configuration gave **+0.143, +0.214, +0.357
— 3 of 3 positive**, which I reported as "the mechanism's direction, unanimously and none
significant". At twelve seeds those three are simply three of the six positives, and the distribution
has no direction at all. **The 3-seed "unanimous" reading was a subset, not a signal** — the fourth
instance in this sequence of a shape read off the smallest sample that could produce one.

## 3. And the banned metric's strong signal there is the **oracle**

On the relative gap the same twelve seeds give a **strong negative** association: 3 positive, 9
negative, Wilcoxon **p = 0.0068**, pooled ρ = **−0.481 (p = 3.7e-06)**. That is the `e5` direction,
resolved — the opposite of the prescribed metric's exact null on the same 84 points.

`gap_EWC = excess_EWC / oracle_final`, so this can be the denominator. It is:

| quantity | cs = 300, `swap2` | cs = 800, `real` |
|---|---|---|
| ρ(oracle, flattening) | **+0.791** (p = 3.5e-19) | **+0.829** (p = 2.1e-22) |
| ρ(excess, flattening) | +0.076 (p = 0.49) | +0.228 (p = 0.037) |
| ρ(gap, flattening) | **−0.481** (p = 3.7e-06) | −0.071 (p = 0.52) |
| rank(gap) = a + b·rank(oracle) + c·rank(excess) | **a = 32.03, b = −0.66, c = +0.89, R² = 0.852** | a = 12.51, b = −0.34, c = +1.04, R² = 0.949 |

**The oracle's error falls with the drive's concentration at ρ = +0.79, and the relative gap inherits
that with a negative coefficient.** So the banned metric's "strong association" at cs = 300/`swap2` is
a statement about the oracle — a property of the task construction — rather than about the filter.
That is the pathway rule 3 exists to block, and this is the first configuration in the project where
it is resolved enough to demonstrate.

## 4. The two metrics fail in opposite directions, and both are now measured

| configuration (12 seeds) | prescribed `excess_ewc` | banned `gap_EWC` |
|---|---|---|
| cs = 800, `real` | **+0.265, 9/2/1, sign p = 0.065**, pooled p = 0.037 → *reversed* | +0.009, 7/5/0, p = 0.77 → null — **hid a result** |
| cs = 300, `swap2` | −0.009, **6/4/2, p = 0.754**, pooled p = 0.49 → **null** | −0.530, 3/9/0, Wilcoxon p = 0.0068, pooled p = 4e-6 → **manufactured** one, from the oracle |

**So "prefer the absolute excess" is not a claim that the absolute metric is more sensitive** — it is
a claim that the relative one can be a statement about the oracle rather than about the filter under
test. Rule 3 now carries both directions of failure, which is what a measurement rule needs to be
auditable rather than merely asserted.

## 5. Where the C1 mechanism question ends

On the metric the project prescribes, at the only configurations with twelve seeds:

| configuration | result |
|---|---|
| `real`/cs = 800 — where `e5` was published | **reversed, marginally** (+0.265, sign p = 0.065, pooled p = 0.037) |
| `swap2`/cs = 300 — where the mechanism is testable | **null** (−0.009, 6/12, p = 0.754) |
| `swap2`/cs = 800 — where the mechanism was proposed | **untested** — the knob is inert there (`e49`, rule 18) |

So the mechanism is **reversed in one place, absent in the other, and untestable in the third**. And
`e36`'s quantitative form is separately refuted (cross-family slopes, the missed pre-registered band),
while the coordinate's *ordinal* relation across a circuit's realizations survives statistical
correction (`e53`, p = 0.033). The honest summary of four fires of work: **the effective rank orders
the excess within a circuit's task draws, and nothing about it predicts or explains the excess across
circuits.**

## 6. Limits

- **The tie-dropping convention still has an alternative** — some texts use the mid-p correction, which
  for one tie gives a p between 0.065 and 0.146. The convention is now explicit and printed with the
  counts, so a reader who prefers another can recompute; that is the point.
- **Two configurations have twelve seeds**, both on the `real`-and-`swap2` axis of one task family.
  Nothing here constrains `swap0.5`, Erdős–Rényi, or another circuit size.
- **The rank decomposition is descriptive.** R² = 0.85 says the gap's rank is mostly the oracle's and
  the excess's ranks; it does not by itself establish that the oracle *causes* the association, though
  the negative coefficient and the +0.79 oracle–flattening correlation leave little else.
- **`e36`'s "untestable" configuration is not evidence of anything**, and it must not be counted as
  one of two nulls (`e49`, rule 18): that would be reading an inert knob as a failed test.
